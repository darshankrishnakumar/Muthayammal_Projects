package com.academic.service;

import com.academic.dto.CatalogItemDto;
import com.academic.dto.CheckoutRequest;
import com.academic.model.*;
import com.academic.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
public class OrderService {

    private static final SecureRandom RANDOM = new SecureRandom();

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private AuditLogService auditLogService;

    public List<CatalogItemDto> getCatalog() {
        List<CatalogItemDto> items = new ArrayList<>();

        items.add(new CatalogItemDto(
                "CAT-REQ-101",
                "Automated Academic Evaluation Portal Package",
                "Academic Requirements",
                ItemType.REQUIREMENT,
                "Complete IEEE standard requirement specification, architecture diagrams, and test matrix for student grading platforms.",
                149.00,
                "Java, Spring Boot 3, React 18, MySQL",
                "Instant PDF Specs + Markdown + Data Schemas",
                "Best Seller",
                4.9,
                38
        ));

        items.add(new CatalogItemDto(
                "CAT-DS-202",
                "Multi-Tenant Research Dataset & Citation Index",
                "Datasets",
                ItemType.DATASET,
                "Curated 50,000+ academic citation graph with schema definitions, vector embeddings, and indexing scripts.",
                89.00,
                "Python, PostgreSQL, ElasticSearch",
                "JSONL Data Dump + SQL Schema + Python Loader",
                "Verified",
                4.8,
                24
        ));

        items.add(new CatalogItemDto(
                "CAT-MOD-303",
                "Zero-Delay DRM Watermark Security Module",
                "Premium Modules",
                ItemType.MODULE,
                "High-performance frontend DRM snapshot shutter with forensic diagonal canvas watermark curtain.",
                199.00,
                "React, HTML5 Canvas, Web Audio API",
                "NPM Drop-in Module + Integration Guide",
                "Security Standard",
                5.0,
                52
        ));

        items.add(new CatalogItemDto(
                "CAT-SRV-404",
                "Comprehensive Code Security Audit & Compliance Review",
                "Research Services",
                ItemType.SERVICE,
                "End-to-end automated penetration test, static code analysis (SAST), and OWASP Top 10 vulnerability remediation report.",
                299.00,
                "SonarQube, OWASP ZAP, JUnit 5",
                "Signed Audit Certificate + PDF Executive Summary",
                "Enterprise",
                4.9,
                19
        ));

        items.add(new CatalogItemDto(
                "CAT-REQ-505",
                "Campus Resource Scheduling Engine Blueprint",
                "Academic Requirements",
                ItemType.REQUIREMENT,
                "Microservice architectural design and scheduling algorithm blueprints for university lab & classroom allocation.",
                129.00,
                "Node.js, Redis, Docker, RabbitMQ",
                "Architecture Diagrams + API Specs",
                "Popular",
                4.7,
                29
        ));

        items.add(new CatalogItemDto(
                "CAT-DS-606",
                "IoT Weather Telemetry & Sensor Analytics Dataset",
                "Datasets",
                ItemType.DATASET,
                "Real-time sensor telemetry stream dataset covering 12 meteorological variables with time-series benchmarks.",
                79.00,
                "InfluxDB, MQTT, Python",
                "Parquet Timeseries + InfluxDB DDL",
                "New",
                4.8,
                14
        ));

        return items;
    }

    @Transactional
    public Order processCheckout(CheckoutRequest req, User actor) {
        if (actor == null) {
            throw new IllegalArgumentException("Authenticated user required for purchase.");
        }
        if (req.getItemName() == null || req.getItemName().isBlank()) {
            throw new IllegalArgumentException("Item name is required for purchase.");
        }
        if (req.getAmount() == null || req.getAmount() <= 0) {
            throw new IllegalArgumentException("Invalid order amount.");
        }
        if (req.getPaymentMethod() == null) {
            req.setPaymentMethod(PaymentMethod.CARD);
        }
        if (req.getItemType() == null) {
            req.setItemType(ItemType.REQUIREMENT);
        }

        String orderNumber = generateUniqueOrderNumber();
        String invoiceNumber = generateUniqueInvoiceNumber();

        // Simulate instant mock payment gateway clearance
        PaymentStatus paymentStatus = PaymentStatus.COMPLETED;
        OrderStatus orderStatus = OrderStatus.COMPLETED;

        String licenseKey = "LIC-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase() + "-" +
                            UUID.randomUUID().toString().substring(0, 4).toUpperCase();
        String fulfillment = "{"
                + "\"licenseKey\":\"" + licenseKey + "\","
                + "\"accessGrantedAt\":\"" + LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME) + "\","
                + "\"downloadPermitted\":true,"
                + "\"resourceToken\":\"tok_" + UUID.randomUUID().toString().replace("-", "") + "\""
                + "}";

        Order order = new Order(
                orderNumber,
                invoiceNumber,
                actor,
                req.getItemName().trim(),
                req.getItemType(),
                req.getItemDescription() != null ? req.getItemDescription().trim() : "Purchased from Academic Store Catalog",
                req.getAmount(),
                req.getPaymentMethod(),
                paymentStatus,
                orderStatus,
                fulfillment
        );

        Order saved = orderRepository.save(order);

        auditLogService.log(
                actor.getEmail(),
                "PURCHASE_CHECKOUT",
                String.format("User purchased '%s' (Order: %s, Invoice: %s, Amount: $%.2f via %s)",
                        saved.getItemName(), saved.getOrderNumber(), saved.getInvoiceNumber(), saved.getAmount(), saved.getPaymentMethod())
        );

        return saved;
    }

    public List<Order> getUserOrders(User user) {
        if (user == null) {
            return Collections.emptyList();
        }
        return orderRepository.findByUserOrderByCreatedAtDesc(user);
    }

    public Map<String, Object> getInvoice(Long orderId, User actor) {
        if (orderId == null) {
            throw new IllegalArgumentException("Order ID is required.");
        }

        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found with id: " + orderId));

        // Strict RBAC & IDOR check: Users can only see their own invoices
        if (actor.getRole() == Role.USER && !order.getUser().getId().equals(actor.getId())) {
            throw new SecurityException("Access Denied: You cannot view invoices belonging to other users.");
        }

        Map<String, Object> invoice = new HashMap<>();
        invoice.put("invoiceNumber", order.getInvoiceNumber());
        invoice.put("orderNumber", order.getOrderNumber());
        invoice.put("createdAt", order.getCreatedAt());
        invoice.put("customerName", order.getUser().getFullName());
        invoice.put("customerEmail", order.getUser().getEmail());
        invoice.put("organization", order.getUser().getOrganization() != null ? order.getUser().getOrganization() : "Academic Independent");
        invoice.put("mobileNumber", order.getUser().getMobileNumber() != null ? order.getUser().getMobileNumber() : "N/A");

        invoice.put("itemName", order.getItemName());
        invoice.put("itemType", order.getItemType().name());
        invoice.put("itemDescription", order.getItemDescription());
        invoice.put("paymentMethod", order.getPaymentMethod().name());
        invoice.put("paymentStatus", order.getPaymentStatus().name());
        invoice.put("orderStatus", order.getStatus().name());

        double subtotal = order.getAmount();
        double tax = 0.00; // Academic tax exempt or transparent breakdown
        double total = subtotal + tax;

        invoice.put("subtotal", subtotal);
        invoice.put("tax", tax);
        invoice.put("total", total);
        invoice.put("currency", "USD");
        invoice.put("fulfillmentDetails", order.getFulfillmentDetails());
        invoice.put("qrVerificationPayload", String.format("VERIFY:INV=%s:ORD=%s:USER=%s:AMT=%.2f",
                order.getInvoiceNumber(), order.getOrderNumber(), order.getUser().getEmail(), total));

        return invoice;
    }

    @Autowired
    private com.academic.repository.RequirementRepository requirementRepository;

    @Autowired
    private com.academic.repository.ProjectRepository projectRepository;

    @Autowired
    private NotificationService notificationService;

    /**
     * Idempotent advance payment for custom requirements.
     */
    @Transactional
    public Order processRequirementAdvancePayment(Long requirementId, Double amount, String idempotencyKey, User actor) {
        if (actor == null) throw new IllegalArgumentException("Authenticated user required.");
        if (requirementId == null) throw new IllegalArgumentException("Requirement ID is required.");

        // Idempotency guard: Return existing completed order if already processed
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = orderRepository.findByIdempotencyKey(idempotencyKey.trim());
            if (existing.isPresent()) {
                return existing.get();
            }
        }

        Requirement req = requirementRepository.findById(requirementId)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found: " + requirementId));

        if (!req.getUser().getId().equals(actor.getId()) && actor.getRole() != Role.SUPER_ADMIN) {
            throw new SecurityException("Forbidden: You can only pay advance for your own requirement.");
        }

        double payAmount = amount != null && amount > 0 ? amount : 
                (req.getAdvanceAmount() != null ? req.getAdvanceAmount().doubleValue() : 200.00);

        String orderNumber = generateUniqueOrderNumber();
        String invoiceNumber = generateUniqueInvoiceNumber();

        Order order = new Order(
                orderNumber,
                invoiceNumber,
                actor,
                "Advance Payment: " + req.getTitle(),
                ItemType.REQUIREMENT,
                "Advance project initiation payment for Requirement #" + req.getId(),
                payAmount,
                PaymentMethod.CARD,
                PaymentStatus.COMPLETED,
                OrderStatus.COMPLETED,
                "{\"paymentType\":\"ADVANCE\",\"requirementId\":" + req.getId() + ",\"verified\":true}"
        );
        order.setRequirementId(req.getId());
        order.setPaymentType("ADVANCE");
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            order.setIdempotencyKey(idempotencyKey.trim());
        }

        Order saved = orderRepository.save(order);

        // Update requirement state
        req.setAdvancePaymentStatus("COMPLETED");
        req.setStatus(RequirementStatus.ADVANCE_PAYMENT_COMPLETED);
        req.setAdvanceAmount(java.math.BigDecimal.valueOf(payAmount));
        if (req.getBudget() != null && req.getBudget().doubleValue() > payAmount) {
            req.setRemainingAmount(req.getBudget().subtract(java.math.BigDecimal.valueOf(payAmount)));
        }
        requirementRepository.save(req);

        auditLogService.log(actor.getEmail(), "ADVANCE_PAYMENT_COMPLETED",
                String.format("Advance payment of $%.2f received for Requirement #%d (%s)", payAmount, req.getId(), req.getTitle()));

        notificationService.sendNotification(actor.getEmail(), "USER",
                "Advance Payment Received",
                "Your advance payment for '" + req.getTitle() + "' has been verified. Your requirement is now in Super Admin review.",
                "/requirements");

        return saved;
    }

    /**
     * Idempotent remaining payment for completing and unlocking projects.
     */
    @Transactional
    public Order processProjectRemainingPayment(Long projectId, Double amount, String idempotencyKey, User actor) {
        if (actor == null) throw new IllegalArgumentException("Authenticated user required.");
        if (projectId == null) throw new IllegalArgumentException("Project ID is required.");

        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = orderRepository.findByIdempotencyKey(idempotencyKey.trim());
            if (existing.isPresent()) {
                return existing.get();
            }
        }

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found: " + projectId));

        double payAmount = amount != null && amount > 0 ? amount : 
                (project.getRemainingAmount() != null ? project.getRemainingAmount().doubleValue() : 300.00);

        String orderNumber = generateUniqueOrderNumber();
        String invoiceNumber = generateUniqueInvoiceNumber();

        Order order = new Order(
                orderNumber,
                invoiceNumber,
                actor,
                "Final Balance: " + project.getProjectName(),
                ItemType.MODULE,
                "Remaining balance payment to unlock full deliverables for Project " + project.getProjectCode(),
                payAmount,
                PaymentMethod.CARD,
                PaymentStatus.COMPLETED,
                OrderStatus.COMPLETED,
                "{\"paymentType\":\"REMAINING\",\"projectId\":" + project.getId() + ",\"accessGranted\":true}"
        );
        order.setProjectId(project.getId());
        order.setPaymentType("REMAINING");
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            order.setIdempotencyKey(idempotencyKey.trim());
        }

        Order saved = orderRepository.save(order);

        // Unlock Project Access
        project.setRemainingPaymentStatus("COMPLETED");
        project.setStatus(ProjectStatus.ACCESS_GRANTED);
        project.setLifecycleStatus(ProjectStatus.ACCESS_GRANTED);
        project.setPurchasedByUserId(actor.getId());
        projectRepository.save(project);

        auditLogService.log(actor.getEmail(), "FINAL_PAYMENT_COMPLETED",
                String.format("Final payment of $%.2f received. Project %s (%s) access unlocked.", payAmount, project.getProjectCode(), project.getProjectName()));

        notificationService.sendNotification(actor.getEmail(), "USER",
                "Project Deliverables Unlocked",
                "Final payment confirmed! Full access and protected deliverables for '" + project.getProjectName() + "' are now unlocked.",
                "/projects/" + project.getId());

        return saved;
    }

    /**
     * Idempotent direct purchase of existing Marketplace project.
     */
    @Transactional
    public Order processMarketplacePurchase(Long projectId, String idempotencyKey, User actor) {
        if (actor == null) throw new IllegalArgumentException("Authenticated user required.");
        if (projectId == null) throw new IllegalArgumentException("Project ID is required.");

        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = orderRepository.findByIdempotencyKey(idempotencyKey.trim());
            if (existing.isPresent()) {
                return existing.get();
            }
        }

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Marketplace project not found: " + projectId));

        double payAmount = project.getBudget() != null ? project.getBudget().doubleValue() : 199.00;

        String orderNumber = generateUniqueOrderNumber();
        String invoiceNumber = generateUniqueInvoiceNumber();

        Order order = new Order(
                orderNumber,
                invoiceNumber,
                actor,
                "Marketplace: " + project.getProjectName(),
                ItemType.MODULE,
                "Instant purchase of marketplace project " + project.getProjectCode(),
                payAmount,
                PaymentMethod.CARD,
                PaymentStatus.COMPLETED,
                OrderStatus.COMPLETED,
                "{\"paymentType\":\"FULL\",\"marketplaceProjectId\":" + project.getId() + ",\"accessGranted\":true}"
        );
        order.setProjectId(project.getId());
        order.setPaymentType("FULL");
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            order.setIdempotencyKey(idempotencyKey.trim());
        }

        Order saved = orderRepository.save(order);

        // Grant access to this purchased project
        project.setPurchasedByUserId(actor.getId());
        project.setStatus(ProjectStatus.ACCESS_GRANTED);
        project.setLifecycleStatus(ProjectStatus.ACCESS_GRANTED);
        project.setAdvancePaymentStatus("COMPLETED");
        project.setRemainingPaymentStatus("COMPLETED");
        projectRepository.save(project);

        auditLogService.log(actor.getEmail(), "MARKETPLACE_PURCHASE_COMPLETED",
                String.format("User %s purchased Marketplace Project %s ($%.2f)", actor.getEmail(), project.getProjectCode(), payAmount));

        notificationService.sendNotification(actor.getEmail(), "USER",
                "Marketplace Purchase Confirmed",
                "You have successfully purchased '" + project.getProjectName() + "'. Full project access is now available.",
                "/projects/" + project.getId());

        return saved;
    }

    private String generateUniqueOrderNumber() {
        String num;
        do {
            num = "ORD-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
        } while (orderRepository.existsByOrderNumber(num));
        return num;
    }

    private String generateUniqueInvoiceNumber() {
        String num;
        do {
            num = "INV-" + (100000 + RANDOM.nextInt(900000));
        } while (orderRepository.existsByInvoiceNumber(num));
        return num;
    }
}
