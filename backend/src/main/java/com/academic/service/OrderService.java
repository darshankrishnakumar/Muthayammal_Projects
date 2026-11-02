package com.academic.service;

import com.academic.model.*;
import com.academic.repository.CollegeProjectAllocationRepository;
import com.academic.repository.OrderRepository;
import com.academic.repository.PaymentTransactionRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import com.academic.service.payment.PaymentGateway;
import com.academic.service.payment.PaymentResult;
import com.academic.service.payment.PaymentUnavailableException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Orders and payments.
 *
 * Rules enforced here (never in the browser):
 * <ul>
 *   <li>The amount is always computed on the server from the allocation, requirement or project.</li>
 *   <li>The buyer must own the requirement / project, or belong to a college the library project is allocated to.</li>
 *   <li>The requirement or project must be in the state that expects the payment.</li>
 *   <li>Access is granted only after the payment gateway reports success; every attempt is
 *       stored as a {@link PaymentTransaction}.</li>
 *   <li>Idempotency keys are scoped to the paying user.</li>
 * </ul>
 */
@Service
public class OrderService {

    private static final SecureRandom RANDOM = new SecureRandom();

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PaymentTransactionRepository transactionRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntitlementService entitlementService;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private StatusHistoryService statusHistoryService;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private NotificationService notificationService;

    @Autowired
    private List<PaymentGateway> gateways;

    @Value("${academic.payments.provider:simulated}")
    private String providerName;

    @Value("${academic.payments.currency:INR}")
    private String currency;

    // ------------------------------------------------------------------
    // Queries
    // ------------------------------------------------------------------

    public List<Order> getUserOrders(User user) {
        if (user == null) {
            return Collections.emptyList();
        }
        return orderRepository.findByUserOrderByCreatedAtDesc(user);
    }

    /** Orders visible to the actor: own (USER), own college (ADMIN), all (SUPER_ADMIN). */
    public List<Order> getOrdersForActor(User actor) {
        switch (actor.getRole()) {
            case SUPER_ADMIN:
                return orderRepository.findAllByOrderByCreatedAtDesc();
            case ADMIN:
                return actor.getCollege() == null ? Collections.emptyList()
                        : orderRepository.findByCollegeIdOrderByCreatedAtDesc(actor.getCollege().getId());
            case USER:
                return getUserOrders(actor);
            default:
                return Collections.emptyList();
        }
    }

    public List<PaymentTransaction> getTransactions(Long orderId, User actor) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new NoSuchElementException("Order not found with id: " + orderId));
        assertCanViewOrder(order, actor);
        return transactionRepository.findByOrderIdOrderByCreatedAtDesc(orderId);
    }

    public Map<String, Object> getInvoice(Long orderId, User actor) {
        if (orderId == null) {
            throw new IllegalArgumentException("Order ID is required.");
        }

        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new NoSuchElementException("Order not found with id: " + orderId));
        assertCanViewOrder(order, actor);

        List<PaymentTransaction> transactions = transactionRepository.findByOrderIdOrderByCreatedAtDesc(orderId);
        PaymentTransaction latest = transactions.isEmpty() ? null : transactions.get(0);

        Map<String, Object> invoice = new HashMap<>();
        invoice.put("invoiceNumber", order.getInvoiceNumber());
        invoice.put("orderNumber", order.getOrderNumber());
        invoice.put("createdAt", order.getCreatedAt());
        invoice.put("customerName", order.getUser().getFullName());
        invoice.put("customerEmail", order.getUser().getEmail());
        invoice.put("organization", order.getUser().getCollege() != null ? order.getUser().getCollege().getName()
                : (order.getUser().getOrganization() != null ? order.getUser().getOrganization() : "—"));
        invoice.put("mobileNumber", order.getUser().getMobileNumber() != null ? order.getUser().getMobileNumber() : "N/A");

        invoice.put("itemName", order.getItemName());
        invoice.put("itemType", order.getItemType().name());
        invoice.put("itemDescription", order.getItemDescription());
        invoice.put("paymentType", order.getPaymentType());
        invoice.put("paymentMethod", order.getPaymentMethod().name());
        invoice.put("paymentStatus", order.getPaymentStatus().name());
        invoice.put("orderStatus", order.getStatus().name());
        invoice.put("simulatedPayment", order.isSimulatedPayment());
        invoice.put("transactionReference", latest != null ? latest.getProviderReference() : null);
        invoice.put("paymentProvider", latest != null ? latest.getProvider() : null);
        invoice.put("verifiedAt", latest != null ? latest.getVerifiedAt() : null);

        double subtotal = order.getAmount();
        invoice.put("subtotal", subtotal);
        invoice.put("tax", 0.0);
        invoice.put("total", subtotal);
        invoice.put("currency", order.getCurrency() != null ? order.getCurrency() : currency);
        invoice.put("fulfillmentDetails", order.getFulfillmentDetails());
        return invoice;
    }

    // ------------------------------------------------------------------
    // Library purchases
    // ------------------------------------------------------------------

    @Transactional
    public Order purchaseLibraryProject(Long projectId, String idempotencyKey, User actor) {
        requireActor(actor);
        if (actor.getRole() != Role.USER) {
            throw new AccessDeniedException("Only student accounts can purchase projects.");
        }
        Optional<Order> replay = findReplay(idempotencyKey, actor);
        if (replay.isPresent()) {
            return replay.get();
        }

        College college = accessControlService.requireCollege(actor);
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found: " + projectId));
        if (!project.isLibrary() || project.getCatalogStatus() != CatalogStatus.PUBLISHED) {
            throw new IllegalStateException("This project is not available for purchase.");
        }
        CollegeProjectAllocation allocation = allocationRepository.findActive(college.getId(), projectId)
                .orElseThrow(() -> new AccessDeniedException("This project is not offered to your college."));
        if (entitlementService.hasAccess(actor.getId(), projectId)) {
            throw new IllegalStateException("You already have access to this project.");
        }

        if (allocation.getEffectivePrice() == null) {
            throw new IllegalStateException("This project has no price yet and cannot be purchased.");
        }
        BigDecimal amount = normalize(allocation.getEffectivePrice());
        Order order = newOrder(actor, "Library project: " + project.getProjectName(), ItemType.PROJECT,
                "Purchase of library project " + project.getProjectCode() + " for " + college.getName(),
                amount, "FULL", idempotencyKey);
        order.setProjectId(project.getId());
        order = orderRepository.save(order);

        settle(order, amount, actor);

        entitlementService.grant(actor, project, EntitlementSource.PURCHASE, order.getId(), actor.getEmail());
        order.setFulfillmentDetails("{\"accessGranted\":true,\"projectId\":" + project.getId() + "}");
        order = orderRepository.save(order);

        auditLogService.log(actor.getEmail(), "MARKETPLACE_PURCHASE_COMPLETED",
                String.format("Purchased library project %s for %s %s (order %s)", project.getProjectCode(),
                        order.getCurrency(), amount.toPlainString(), order.getOrderNumber()));
        notificationService.sendNotification(actor.getEmail(), "USER",
                "Purchase confirmed",
                "You now have full access to '" + project.getProjectName() + "'.",
                "/projects/" + project.getId());
        return order;
    }

    // ------------------------------------------------------------------
    // Custom development payments
    // ------------------------------------------------------------------

    @Transactional
    public Order processRequirementAdvancePayment(Long requirementId, String idempotencyKey, User actor) {
        requireActor(actor);
        Optional<Order> replay = findReplay(idempotencyKey, actor);
        if (replay.isPresent()) {
            return replay.get();
        }

        Requirement req = requirementRepository.findById(requirementId)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found: " + requirementId));
        if (req.getUser() == null || !req.getUser().getId().equals(actor.getId())) {
            throw new AccessDeniedException("You can only pay the advance for your own requirement.");
        }
        if (req.getStatus() != RequirementStatus.ADVANCE_PAYMENT_PENDING) {
            throw new IllegalStateException("This requirement is not awaiting an advance payment (status: " + req.getStatus() + ").");
        }
        BigDecimal amount = normalize(req.getAdvanceAmount());
        if (amount.signum() <= 0) {
            throw new IllegalStateException("No advance amount has been quoted for this requirement yet.");
        }

        Order order = newOrder(actor, "Advance payment: " + req.getTitle(), ItemType.REQUIREMENT,
                "Advance payment for custom development requirement #" + req.getId(), amount, "ADVANCE", idempotencyKey);
        order.setRequirementId(req.getId());
        order = orderRepository.save(order);

        settle(order, amount, actor);

        RequirementStatus previous = req.getStatus();
        req.setAdvancePaymentStatus("COMPLETED");
        req.setStatus(RequirementStatus.ADVANCE_PAYMENT_COMPLETED);
        requirementRepository.save(req);
        statusHistoryService.record(StatusHistoryService.REQUIREMENT, req.getId(), previous, req.getStatus(), actor.getEmail(),
                "Advance payment verified (order " + order.getOrderNumber() + ")");

        auditLogService.log(actor.getEmail(), "ADVANCE_PAYMENT_COMPLETED",
                String.format("Advance of %s %s verified for requirement #%d (%s)", order.getCurrency(), amount.toPlainString(), req.getId(), req.getTitle()));
        notifySuperAdmins("Advance payment received",
                "Advance paid for '" + req.getTitle() + "'. The requirement is ready for developer assignment.",
                "/requirements/" + req.getId());
        notificationService.sendNotification(actor.getEmail(), "USER", "Advance payment received",
                "Your advance payment for '" + req.getTitle() + "' was verified. A developer will be assigned shortly.",
                "/requirements/" + req.getId());
        return order;
    }

    @Transactional
    public Order processProjectRemainingPayment(Long projectId, String idempotencyKey, User actor) {
        requireActor(actor);
        Optional<Order> replay = findReplay(idempotencyKey, actor);
        if (replay.isPresent()) {
            return replay.get();
        }

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found: " + projectId));
        if (project.isLibrary()) {
            throw new IllegalStateException("Library projects are purchased from the marketplace.");
        }
        if (!accessControlService.isRequesterOf(project, actor)) {
            throw new AccessDeniedException("You can only pay for a project you requested.");
        }
        if (project.getLifecycleStatus() != ProjectStatus.READY_FOR_FINAL_PAYMENT) {
            throw new IllegalStateException("This project is not awaiting final payment (status: " + project.getLifecycleStatus() + ").");
        }
        BigDecimal amount = normalize(project.getRemainingAmount());
        if (amount.signum() <= 0) {
            throw new IllegalStateException("No balance is due for this project.");
        }

        Order order = newOrder(actor, "Final payment: " + project.getProjectName(), ItemType.PROJECT,
                "Final balance to unlock deliverables for project " + project.getProjectCode(), amount, "REMAINING", idempotencyKey);
        order.setProjectId(project.getId());
        order.setRequirementId(project.getLinkedRequirementId());
        order = orderRepository.save(order);

        settle(order, amount, actor);
        completeCustomDelivery(project, actor, order.getId(), "Final payment verified (order " + order.getOrderNumber() + ")");
        return order;
    }

    /**
     * Unlocks a delivered custom project for its requester. Called after verified final payment,
     * or directly when no balance is due.
     */
    @Transactional
    public void completeCustomDelivery(Project project, User requester, Long orderId, String note) {
        ProjectStatus previous = project.getLifecycleStatus();
        project.setRemainingPaymentStatus("COMPLETED");
        project.setStatus(ProjectStatus.ACCESS_GRANTED);
        project.setLifecycleStatus(ProjectStatus.ACCESS_GRANTED);
        project.setProgressPercent(100);
        projectRepository.save(project);
        statusHistoryService.record(StatusHistoryService.PROJECT, project.getId(), previous, ProjectStatus.ACCESS_GRANTED,
                requester.getEmail(), note);

        entitlementService.grant(requester, project, EntitlementSource.CUSTOM_DELIVERY, orderId, requester.getEmail());

        if (project.getLinkedRequirementId() != null) {
            requirementRepository.findById(project.getLinkedRequirementId()).ifPresent(req -> {
                RequirementStatus before = req.getStatus();
                req.setStatus(RequirementStatus.COMPLETED);
                req.setRemainingPaymentStatus("COMPLETED");
                requirementRepository.save(req);
                statusHistoryService.record(StatusHistoryService.REQUIREMENT, req.getId(), before, RequirementStatus.COMPLETED,
                        requester.getEmail(), "Deliverables unlocked");
            });
        }

        auditLogService.log(requester.getEmail(), "FINAL_PAYMENT_COMPLETED",
                String.format("Deliverables for %s (%s) unlocked for %s", project.getProjectCode(), project.getProjectName(), requester.getEmail()));
        notificationService.sendNotification(requester.getEmail(), "USER", "Deliverables unlocked",
                "Full access to '" + project.getProjectName() + "' is now available.", "/projects/" + project.getId());
        if (project.getDeveloper() != null) {
            notificationService.sendNotification(project.getDeveloper().getEmail(), "PROJECT_DEVELOPER", "Project delivered",
                    "'" + project.getProjectName() + "' has been delivered to the student.", "/projects/" + project.getId());
        }
    }

    // ------------------------------------------------------------------
    // Internals
    // ------------------------------------------------------------------

    /**
     * Charges the order through the configured gateway and records the transaction.
     * Throws if the gateway is unavailable or the charge fails; callers grant access only after this returns.
     */
    private void settle(Order order, BigDecimal amount, User actor) {
        if (amount.signum() == 0) {
            order.setPaymentStatus(PaymentStatus.COMPLETED);
            order.setStatus(OrderStatus.COMPLETED);
            order.setPaymentMethod(PaymentMethod.ACADEMIC_CREDIT);
            orderRepository.save(order);
            statusHistoryService.record(StatusHistoryService.ORDER, order.getId(), OrderStatus.PENDING, OrderStatus.COMPLETED,
                    actor.getEmail(), "No charge due");
            return;
        }

        PaymentGateway gateway = activeGateway();
        PaymentResult result = gateway.charge(order.getOrderNumber(), amount, currency, actor.getEmail());

        PaymentTransaction tx = new PaymentTransaction();
        tx.setOrder(order);
        tx.setProvider(gateway.name());
        tx.setProviderReference(result.getProviderReference());
        tx.setAmount(amount);
        tx.setCurrency(currency);
        tx.setSimulated(gateway.isSimulated());

        switch (result.getOutcome()) {
            case SUCCEEDED:
                tx.setStatus(PaymentTransactionStatus.SUCCEEDED);
                tx.setVerifiedAt(LocalDateTime.now());
                transactionRepository.save(tx);
                order.setPaymentStatus(PaymentStatus.COMPLETED);
                order.setStatus(OrderStatus.COMPLETED);
                order.setSimulatedPayment(gateway.isSimulated());
                orderRepository.save(order);
                statusHistoryService.record(StatusHistoryService.ORDER, order.getId(), OrderStatus.PENDING, OrderStatus.COMPLETED,
                        actor.getEmail(), (gateway.isSimulated() ? "SIMULATED payment " : "Payment ") + result.getProviderReference());
                return;
            case PENDING:
                tx.setStatus(PaymentTransactionStatus.INITIATED);
                transactionRepository.save(tx);
                throw new IllegalStateException("Payment is pending confirmation from the provider.");
            case FAILED:
            default:
                tx.setStatus(PaymentTransactionStatus.FAILED);
                tx.setFailureReason(result.getFailureReason());
                transactionRepository.save(tx);
                order.setPaymentStatus(PaymentStatus.FAILED);
                order.setStatus(OrderStatus.FAILED);
                orderRepository.save(order);
                throw new IllegalStateException("Payment failed: " + (result.getFailureReason() != null ? result.getFailureReason() : "declined"));
        }
    }

    public boolean isPaymentAvailable() {
        return gateways.stream().anyMatch(g -> g.name().equalsIgnoreCase(providerName) && g.isEnabled());
    }

    public boolean isSimulationMode() {
        return gateways.stream().anyMatch(g -> g.name().equalsIgnoreCase(providerName) && g.isEnabled() && g.isSimulated());
    }

    private PaymentGateway activeGateway() {
        return gateways.stream()
                .filter(g -> g.name().equalsIgnoreCase(providerName))
                .filter(PaymentGateway::isEnabled)
                .findFirst()
                .orElseThrow(() -> new PaymentUnavailableException(
                        "Online payments are not configured on this server. Please contact the platform administrator."));
    }

    private Order newOrder(User actor, String itemName, ItemType type, String description, BigDecimal amount,
                           String paymentType, String idempotencyKey) {
        Order order = new Order(
                generateUniqueOrderNumber(),
                generateUniqueInvoiceNumber(),
                actor,
                itemName,
                type,
                description,
                amount.doubleValue(),
                PaymentMethod.CARD,
                PaymentStatus.PENDING,
                OrderStatus.PENDING,
                null
        );
        order.setPaymentType(paymentType);
        order.setCurrency(currency);
        order.setCollegeId(actor.getCollege() != null ? actor.getCollege().getId() : null);
        String scoped = scopedKey(idempotencyKey, actor);
        if (scoped != null) {
            order.setIdempotencyKey(scoped);
        }
        return order;
    }

    private Optional<Order> findReplay(String idempotencyKey, User actor) {
        String scoped = scopedKey(idempotencyKey, actor);
        if (scoped == null) {
            return Optional.empty();
        }
        return orderRepository.findByIdempotencyKey(scoped)
                .filter(o -> o.getUser().getId().equals(actor.getId()))
                .filter(o -> o.getPaymentStatus() == PaymentStatus.COMPLETED);
    }

    private static String scopedKey(String key, User actor) {
        if (key == null || key.isBlank()) {
            return null;
        }
        String scoped = "u" + actor.getId() + ":" + key.trim();
        return scoped.length() > 100 ? scoped.substring(0, 100) : scoped;
    }

    private void assertCanViewOrder(Order order, User actor) {
        boolean allowed = switch (actor.getRole()) {
            case SUPER_ADMIN -> true;
            case ADMIN -> actor.getCollege() != null && Objects.equals(order.getCollegeId(), actor.getCollege().getId());
            case USER -> order.getUser().getId().equals(actor.getId());
            default -> false;
        };
        if (!allowed) {
            throw new AccessDeniedException("Access Denied: You cannot view this order.");
        }
    }

    private void notifySuperAdmins(String title, String message, String link) {
        userRepository.findByRoleAndDeletedFalse(Role.SUPER_ADMIN)
                .forEach(sa -> notificationService.sendNotification(sa.getEmail(), "SUPER_ADMIN", title, message, link));
    }

    private static void requireActor(User actor) {
        if (actor == null) {
            throw new IllegalArgumentException("Authenticated user required.");
        }
    }

    private static BigDecimal normalize(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value.setScale(2, RoundingMode.HALF_UP);
    }

    private String generateUniqueOrderNumber() {
        String num;
        do {
            num = "ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        } while (orderRepository.existsByOrderNumber(num));
        return num;
    }

    private String generateUniqueInvoiceNumber() {
        String num;
        do {
            num = "INV-" + (1000000 + RANDOM.nextInt(9000000));
        } while (orderRepository.existsByInvoiceNumber(num));
        return num;
    }
}
