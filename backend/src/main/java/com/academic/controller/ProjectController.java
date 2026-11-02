package com.academic.controller;

import com.academic.dto.AssignmentRequest;
import com.academic.dto.ProjectCreateRequest;
import com.academic.dto.ProjectStatusUpdateRequest;
import com.academic.dto.ProjectUpdateRequest;
import com.academic.model.*;
import com.academic.repository.ProjectEntitlementRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.service.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    @Autowired
    private ProjectService projectService;

    @Autowired
    private ProjectAssignmentService projectAssignmentService;

    @Autowired
    private DevelopmentWorkflowService workflowService;

    @Autowired
    private OrderService orderService;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private ProjectEntitlementRepository entitlementRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private User actor() {
        return accessControlService.getCurrentAuthenticatedUser();
    }

    // ------------------------------------------------------------------
    // Listing and detail (role and college scoped)
    // ------------------------------------------------------------------

    @GetMapping
    public List<Project> getProjects(
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String techStack,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(required = false) Long assignedUserId,
            @RequestParam(required = false) String type) {

        User actor = actor();
        ProjectStatus projectStatus = parseStatus(status);
        List<Project> projects;
        switch (actor.getRole()) {
            case SUPER_ADMIN -> projects = projectService.searchProjects(search, projectStatus, techStack, startDate, endDate, assignedUserId);
            case ADMIN -> {
                Long collegeId = actor.getCollege() != null ? actor.getCollege().getId() : null;
                Stream<Project> own = collegeId != null ? projectRepository.findCustomProjectsByCollegeId(collegeId).stream() : Stream.empty();
                projects = Stream.concat(own, projectRepository.findByReviewerAdminId(actor.getId()).stream())
                        .distinct().collect(Collectors.toList());
            }
            case PROJECT_DEVELOPER -> projects = projectRepository.findByDeveloperId(actor.getId());
            default -> {
                Stream<Project> requested = projectRepository.findCustomProjectsByRequesterId(actor.getId()).stream();
                Stream<Project> owned = entitlementRepository.findActiveByUserId(actor.getId()).stream().map(ProjectEntitlement::getProject);
                projects = Stream.concat(requested, owned).distinct().collect(Collectors.toList());
            }
        }
        if (actor.getRole() != Role.SUPER_ADMIN) {
            String q = search == null ? null : search.trim().toLowerCase();
            projects = projects.stream()
                    .filter(p -> q == null || q.isEmpty() || p.getProjectName().toLowerCase().contains(q) || p.getProjectCode().toLowerCase().contains(q))
                    .filter(p -> projectStatus == null || p.getStatus() == projectStatus || p.getLifecycleStatus() == projectStatus)
                    .collect(Collectors.toList());
        }
        if (type != null && !type.isBlank()) {
            ProjectType t = ProjectType.valueOf(type.trim().toUpperCase());
            projects = projects.stream().filter(p -> p.getProjectType() == t).collect(Collectors.toList());
        }
        return projects;
    }

    @GetMapping("/user/projects")
    public List<Project> getUserProjects() {
        return getProjects(null, null, null, null, null, null, null);
    }

    @GetMapping("/dashboard")
    public Map<String, Object> getDashboardSummary() {
        return projectService.getDashboardSummary(actor());
    }

    /**
     * Project detail with the caller's access level and, for custom projects, the requesting
     * student and college. Requires at least PREVIEW access.
     */
    @GetMapping("/{id}")
    public Map<String, Object> getProjectById(@PathVariable Long id) {
        User actor = actor();
        Project project = projectService.getProjectById(id);
        AccessControlService.ProjectAccessLevel level = accessControlService.getAccessLevel(project, actor);
        if (level == AccessControlService.ProjectAccessLevel.NONE) {
            throw new AccessDeniedException("Access denied: You are not assigned to this project.");
        }
        @SuppressWarnings("unchecked")
        Map<String, Object> body = objectMapper.convertValue(project, LinkedHashMap.class);
        body.put("accessLevel", level.name());
        if (level != AccessControlService.ProjectAccessLevel.FULL) {
            body.remove("installationInstructions");
        }
        if (project.getLinkedRequirementId() != null) {
            requirementRepository.findById(project.getLinkedRequirementId()).ifPresent(r -> {
                Map<String, Object> req = new LinkedHashMap<>();
                req.put("id", r.getId());
                req.put("title", r.getTitle());
                req.put("status", r.getStatus());
                req.put("studentName", r.getUser() != null ? r.getUser().getFullName() : null);
                req.put("studentId", r.getUser() != null ? r.getUser().getId() : null);
                req.put("collegeName", r.getCollege() != null ? r.getCollege().getName() : null);
                body.put("requirement", req);
            });
        }
        body.put("isRequester", accessControlService.isRequesterOf(project, actor));
        body.put("isDeveloper", accessControlService.isDeveloperOf(project, actor));
        body.put("isReviewer", project.getReviewerAdmin() != null && project.getReviewerAdmin().getId().equals(actor.getId()));
        return body;
    }

    @GetMapping("/{id}/timeline")
    public List<StatusHistory> timeline(@PathVariable Long id) {
        return workflowService.timeline(id, actor());
    }

    @GetMapping("/by-requirement/{reqId}")
    public ResponseEntity<?> getProjectByRequirementId(@PathVariable Long reqId) {
        User actor = actor();
        Requirement req = requirementRepository.findById(reqId)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found: " + reqId));
        if (!accessControlService.canViewRequirement(actor, req)) {
            throw new AccessDeniedException("Access denied.");
        }
        return projectService.getProjectByLinkedRequirementId(reqId)
                .<ResponseEntity<?>>map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", "No linked project found for requirement ID " + reqId)));
    }

    // ------------------------------------------------------------------
    // Super Admin project administration
    // ------------------------------------------------------------------

    @PostMapping
    public ResponseEntity<Project> createProject(@RequestBody ProjectCreateRequest request) {
        User actor = requireSuperAdmin();
        return ResponseEntity.status(HttpStatus.CREATED).body(projectService.createProject(request, actor.getEmail()));
    }

    @PutMapping("/{id}")
    public Project updateProject(@PathVariable Long id, @RequestBody ProjectUpdateRequest request) {
        User actor = requireSuperAdmin();
        return projectService.updateProject(id, request, actor.getEmail());
    }

    /** Manual status override (validated against allowed transitions). Super Admin only. */
    @RequestMapping(value = "/{id}/status", method = {RequestMethod.PATCH, RequestMethod.PUT})
    public Project updateProjectStatus(@PathVariable Long id, @RequestBody ProjectStatusUpdateRequest request) {
        User actor = requireSuperAdmin();
        return projectService.changeStatus(id, request.getStatus(), actor.getEmail());
    }

    @DeleteMapping("/{id}")
    public Map<String, Object> deleteProjectById(@PathVariable Long id) {
        User actor = requireSuperAdmin();
        projectService.deleteProject(id, actor.getEmail());
        return Map.of("success", true, "message", "Project successfully deleted.");
    }

    // ------------------------------------------------------------------
    // Manual access grants (project assignments)
    // ------------------------------------------------------------------

    @GetMapping("/{id}/assignments")
    public List<ProjectAssignment> getProjectAssignments(@PathVariable Long id) {
        User actor = actor();
        if (actor.getRole() != Role.SUPER_ADMIN && actor.getRole() != Role.ADMIN) {
            throw new AccessDeniedException("Access denied.");
        }
        accessControlService.validateProjectAccess(id);
        List<ProjectAssignment> all = projectAssignmentService.getActiveAssignmentsByProject(id);
        if (actor.getRole() == Role.ADMIN) {
            return all.stream().filter(a -> accessControlService.sameCollege(actor, a.getUser())).collect(Collectors.toList());
        }
        return all;
    }

    @PostMapping({"/{id}/assign", "/{id}/assignments"})
    public ResponseEntity<?> assignUserToProject(@PathVariable Long id, @RequestBody AssignmentRequest request) {
        User actor = requireSuperAdmin();
        ProjectAssignment assignment = projectAssignmentService.assignUserToProject(
                id, request.getUserId(), request.getExpiredAt(), request.getNotes(), actor.getEmail());
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "success", true,
                "message", "Project assigned successfully",
                "assignment", assignment));
    }

    @DeleteMapping({"/{id}/assign/{userId}", "/{id}/assignments/user/{userId}"})
    public Map<String, Object> removeAssignmentByUser(@PathVariable Long id, @PathVariable Long userId) {
        User actor = requireSuperAdmin();
        projectAssignmentService.deactivateAssignmentByUser(id, userId, actor.getEmail());
        return Map.of("success", true, "message", "Project assignment successfully revoked.");
    }

    // ------------------------------------------------------------------
    // Development workflow
    // ------------------------------------------------------------------

    @PostMapping("/{id}/assign-developer")
    public Project assignDeveloper(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        return workflowService.reassignDeveloper(id, toLong(body.get("developerId")), actor());
    }

    @PostMapping("/{id}/assign-reviewer")
    public Project assignReviewer(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        return workflowService.assignReviewer(id, toLong(body.get("reviewerId")), actor());
    }

    @PostMapping("/{id}/accept")
    public Project accept(@PathVariable Long id) {
        return workflowService.accept(id, actor());
    }

    @PostMapping("/{id}/progress")
    public Project progress(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Integer percent = body.get("percent") != null ? Integer.valueOf(body.get("percent").toString()) : null;
        return workflowService.updateProgress(id, percent, (String) body.get("note"), actor());
    }

    @PostMapping("/{id}/developer-submit-review")
    public Project developerSubmitReview(@PathVariable Long id, @RequestBody(required = false) Map<String, String> body) {
        return workflowService.submitForReview(id, body != null ? body.get("notes") : null, actor());
    }

    @PostMapping("/{id}/admin-review")
    public Project adminReview(@PathVariable Long id, @RequestBody Map<String, String> body) {
        return workflowService.review(id, body.getOrDefault("action", ""), body.get("notes"), actor());
    }

    /** Final balance for a reviewed custom project. Amount is computed server-side. */
    @PostMapping("/{id}/pay-remaining")
    public Map<String, Object> payRemaining(@PathVariable Long id, @RequestBody(required = false) Map<String, Object> body,
                                            @RequestHeader(value = "Idempotency-Key", required = false) String headerKey) {
        String key = headerKey != null ? headerKey : body != null && body.get("idempotencyKey") != null ? body.get("idempotencyKey").toString() : null;
        Order order = orderService.processProjectRemainingPayment(id, key, actor());
        return Map.of(
                "success", true,
                "message", order.isSimulatedPayment()
                        ? "Final payment recorded (SIMULATED — development mode). Deliverables unlocked."
                        : "Final payment verified. Deliverables unlocked.",
                "order", order);
    }

    /** Deprecated alias kept for older clients; use POST /api/marketplace/{id}/purchase. */
    @PostMapping("/{id}/purchase-marketplace")
    public Map<String, Object> purchaseMarketplace(@PathVariable Long id, @RequestBody(required = false) Map<String, Object> body) {
        String key = body != null && body.get("idempotencyKey") != null ? body.get("idempotencyKey").toString() : null;
        Order order = orderService.purchaseLibraryProject(id, key, actor());
        return Map.of("success", true, "message", "Purchase completed.", "order", order);
    }

    @GetMapping("/my-developer-projects")
    public List<Project> getMyDeveloperProjects() {
        return workflowService.developerProjects(actor());
    }

    @GetMapping("/my-review-projects")
    public List<Project> getMyReviewProjects() {
        return workflowService.reviewProjects(actor());
    }

    @GetMapping("/workflow/developers")
    public List<Map<String, Object>> developerOptions() {
        requireSuperAdmin();
        return workflowService.developerOptions();
    }

    @GetMapping("/workflow/reviewers")
    public List<Map<String, Object>> reviewerOptions() {
        requireSuperAdmin();
        return workflowService.reviewerOptions();
    }

    private User requireSuperAdmin() {
        User actor = actor();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Access denied. Only the Super Admin can perform this action.");
        }
        return actor;
    }

    private static ProjectStatus parseStatus(String status) {
        if (status == null || status.isBlank()) return null;
        try {
            return ProjectStatus.valueOf(status.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid project status filter: " + status);
        }
    }

    private static Long toLong(Object o) {
        if (o == null || o.toString().isBlank()) throw new IllegalArgumentException("A user must be selected.");
        return Long.valueOf(o.toString());
    }
}
