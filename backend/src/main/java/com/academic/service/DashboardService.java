package com.academic.service;

import com.academic.model.*;
import com.academic.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

/** Role-specific dashboard metrics, computed from live data with college isolation applied. */
@Service
public class DashboardService {

    private static final Set<ProjectStatus> DELIVERED = EnumSet.of(ProjectStatus.ACCESS_GRANTED, ProjectStatus.COMPLETED);

    @Autowired private CollegeRepository collegeRepository;
    @Autowired private UserRepository userRepository;
    @Autowired private ProjectRepository projectRepository;
    @Autowired private RequirementRepository requirementRepository;
    @Autowired private OrderRepository orderRepository;
    @Autowired private CollegeProjectAllocationRepository allocationRepository;
    @Autowired private ProjectEntitlementRepository entitlementRepository;
    @Autowired private AuditLogRepository auditLogRepository;
    @Autowired private OrderService orderService;

    @Transactional(readOnly = true)
    public Map<String, Object> forActor(User actor) {
        return switch (actor.getRole()) {
            case SUPER_ADMIN -> superAdmin();
            case ADMIN -> collegeAdmin(actor);
            case PROJECT_DEVELOPER -> developer(actor);
            case USER -> student(actor);
        };
    }

    private Map<String, Object> superAdmin() {
        Map<String, Object> m = new LinkedHashMap<>();
        List<College> colleges = collegeRepository.findAll();
        List<Project> custom = projectRepository.findAllCustomProjects();
        m.put("role", "SUPER_ADMIN");
        m.put("colleges", colleges.size());
        m.put("activeColleges", colleges.stream().filter(College::isActive).count());
        m.put("admins", userRepository.countByRoleAndDeletedFalse(Role.ADMIN));
        m.put("students", userRepository.countByRoleAndDeletedFalse(Role.USER));
        m.put("developers", userRepository.findByRoleAndDeletedFalse(Role.PROJECT_DEVELOPER).stream()
                .filter(u -> u.getStatus() == UserStatus.ACTIVE).count());
        m.put("libraryProjects", projectRepository.countByProjectType(ProjectType.LIBRARY));
        m.put("publishedProjects", projectRepository.countByProjectTypeAndCatalogStatus(ProjectType.LIBRARY, CatalogStatus.PUBLISHED));
        m.put("allocatedProjects", allocationRepository.countDistinctAllocatedProjects());
        m.put("activeAllocations", allocationRepository.countByActiveTrue());
        m.put("customRequests", requirementRepository.count());
        m.put("pendingApprovals", requirementRepository.countByStatus(RequirementStatus.SUPER_ADMIN_REVIEW));
        m.put("awaitingAssignment", requirementRepository.countByStatus(RequirementStatus.ADVANCE_PAYMENT_COMPLETED));
        m.put("awaitingReview", custom.stream().filter(p -> p.getLifecycleStatus() == ProjectStatus.READY_FOR_REVIEW).count());
        m.put("activeDevelopment", custom.stream().filter(p -> !DELIVERED.contains(p.getLifecycleStatus())).count());
        m.put("orders", orderRepository.count());
        m.put("verifiedRevenue", orderRepository.sumCompletedRevenue(null, false));
        m.put("simulatedRevenue", orderRepository.sumCompletedRevenue(null, true));
        m.put("paymentSimulation", orderService.isSimulationMode());
        m.put("requirementPipeline", pipeline(requirementRepository.findAll()));
        m.put("recentActivity", auditLogRepository.findTop10ByOrderByTimestampDesc());
        m.put("collegeLeaderboard", colleges.stream()
                .map(c -> Map.<String, Object>of(
                        "id", c.getId(), "name", c.getName(), "code", c.getCode(),
                        "students", userRepository.countByCollegeAndRole(c.getId(), Role.USER),
                        "allocated", allocationRepository.countActiveByCollegeId(c.getId()),
                        "orders", orderRepository.countByCollegeId(c.getId())))
                .sorted(Comparator.comparing((Map<String, Object> r) -> (Long) r.get("orders")).reversed())
                .limit(6).collect(Collectors.toList()));
        return m;
    }

    private Map<String, Object> collegeAdmin(User actor) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("role", "ADMIN");
        College college = actor.getCollege();
        if (college == null) {
            m.put("college", null);
            m.put("message", "Your account is not linked to a college yet.");
            return m;
        }
        Long cid = college.getId();
        List<Project> custom = projectRepository.findCustomProjectsByCollegeId(cid);
        List<Requirement> reqs = requirementRepository.searchCollegeRequirements(cid, null, null);
        m.put("college", Map.of("id", cid, "name", college.getName(), "code", college.getCode(), "active", college.isActive()));
        m.put("allocatedProjects", allocationRepository.countActiveByCollegeId(cid));
        m.put("students", userRepository.countByCollegeAndRole(cid, Role.USER));
        m.put("newRequirements", requirementRepository.countByCollegeAndStatus(cid, RequirementStatus.SUBMITTED));
        m.put("pendingRequests", requirementRepository.countByCollegeAndStatus(cid, RequirementStatus.SUPER_ADMIN_REVIEW)
                + requirementRepository.countByCollegeAndStatus(cid, RequirementStatus.ADVANCE_PAYMENT_PENDING));
        m.put("activeProjects", custom.stream().filter(p -> !DELIVERED.contains(p.getLifecycleStatus())).count());
        m.put("completedProjects", custom.stream().filter(p -> DELIVERED.contains(p.getLifecycleStatus())).count());
        m.put("orders", orderRepository.countByCollegeId(cid));
        m.put("revenue", orderRepository.sumCompletedRevenue(cid, null));
        m.put("reviewQueue", projectRepository.findByReviewerAdminId(actor.getId()).stream()
                .filter(p -> p.getLifecycleStatus() == ProjectStatus.READY_FOR_REVIEW).count());
        m.put("requirementPipeline", pipeline(reqs));
        m.put("recentRequirements", reqs.stream().limit(6).map(r -> Map.<String, Object>of(
                "id", r.getId(), "title", r.getTitle(), "status", r.getStatus(),
                "student", r.getUser() != null ? r.getUser().getFullName() : "",
                "createdAt", r.getCreatedAt())).collect(Collectors.toList()));
        return m;
    }

    private Map<String, Object> developer(User actor) {
        List<Project> mine = projectRepository.findByDeveloperId(actor.getId());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("role", "PROJECT_DEVELOPER");
        m.put("assigned", mine.size());
        m.put("pendingAcceptance", count(mine, ProjectStatus.DEVELOPER_ASSIGNED));
        m.put("inProgress", count(mine, ProjectStatus.IN_PROGRESS) + count(mine, ProjectStatus.TESTING));
        m.put("inReview", count(mine, ProjectStatus.READY_FOR_REVIEW));
        m.put("changesRequested", count(mine, ProjectStatus.CHANGES_REQUESTED));
        m.put("completed", mine.stream().filter(p -> DELIVERED.contains(p.getLifecycleStatus())
                || p.getLifecycleStatus() == ProjectStatus.READY_FOR_FINAL_PAYMENT || p.getLifecycleStatus() == ProjectStatus.REVIEW_APPROVED).count());
        m.put("projects", mine.stream().map(this::projectCard).collect(Collectors.toList()));
        return m;
    }

    private Map<String, Object> student(User actor) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("role", "USER");
        College college = actor.getCollege();
        m.put("college", college != null ? Map.of("id", college.getId(), "name", college.getName()) : null);
        long available = college == null ? 0 : allocationRepository.findActiveByCollegeId(college.getId()).stream()
                .filter(a -> a.getProject().getCatalogStatus() == CatalogStatus.PUBLISHED).count();
        List<Project> custom = projectRepository.findCustomProjectsByRequesterId(actor.getId());
        List<ProjectEntitlement> owned = entitlementRepository.findActiveByUserId(actor.getId());
        m.put("availableProjects", available);
        m.put("requested", requirementRepository.countByUser(actor));
        m.put("purchased", owned.stream().filter(e -> e.getProject().isLibrary()).count());
        m.put("activeDevelopment", custom.stream().filter(p -> !DELIVERED.contains(p.getLifecycleStatus())).count());
        long pendingPayments = requirementRepository.countByUserAndStatus(actor, RequirementStatus.ADVANCE_PAYMENT_PENDING)
                + custom.stream().filter(p -> p.getLifecycleStatus() == ProjectStatus.READY_FOR_FINAL_PAYMENT).count();
        m.put("pendingPayments", pendingPayments);
        m.put("customProjects", custom.stream().map(this::projectCard).collect(Collectors.toList()));
        m.put("library", owned.stream().filter(e -> e.getProject().isLibrary()).limit(6).map(e -> projectCard(e.getProject())).collect(Collectors.toList()));
        m.put("recentOrders", orderRepository.findByUserOrderByCreatedAtDesc(actor).stream().limit(5).map(o -> Map.<String, Object>of(
                "id", o.getId(), "orderNumber", o.getOrderNumber(), "itemName", o.getItemName(), "amount", o.getAmount(),
                "paymentStatus", o.getPaymentStatus(), "simulated", o.isSimulatedPayment(), "createdAt", o.getCreatedAt()))
                .collect(Collectors.toList()));
        return m;
    }

    private Map<String, Object> projectCard(Project p) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", p.getId());
        m.put("projectCode", p.getProjectCode());
        m.put("projectName", p.getProjectName());
        m.put("projectType", p.getProjectType());
        m.put("status", p.getLifecycleStatus() != null ? p.getLifecycleStatus() : p.getStatus());
        m.put("progressPercent", p.getProgressPercent());
        m.put("domain", p.getDomain());
        m.put("updatedAt", p.getUpdatedAt());
        return m;
    }

    private static long count(List<Project> projects, ProjectStatus status) {
        return projects.stream().filter(p -> p.getLifecycleStatus() == status).count();
    }

    private static Map<String, Long> pipeline(List<Requirement> reqs) {
        Map<String, Long> m = new LinkedHashMap<>();
        for (RequirementStatus s : RequirementStatus.values()) {
            long n = reqs.stream().filter(r -> r.getStatus() == s).count();
            if (n > 0) m.put(s.name(), n);
        }
        return m;
    }
}
