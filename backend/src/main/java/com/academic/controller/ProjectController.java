package com.academic.controller;

import com.academic.dto.AssignmentRequest;
import com.academic.dto.ProjectCreateRequest;
import com.academic.dto.ProjectStatusUpdateRequest;
import com.academic.dto.ProjectUpdateRequest;
import com.academic.model.Project;
import com.academic.model.ProjectAssignment;
import com.academic.model.ProjectStatus;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.repository.ProjectAssignmentRepository;
import com.academic.service.ProjectAssignmentService;
import com.academic.service.ProjectService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/projects")
@CrossOrigin(origins = "*", allowedHeaders = "*")
public class ProjectController {

    @Autowired
    private ProjectService projectService;

    @Autowired
    private ProjectAssignmentService projectAssignmentService;

    @Autowired
    private ProjectAssignmentRepository projectAssignmentRepository;

    @Autowired
    private UserService userService;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user context not found."));
    }

    @GetMapping
    public ResponseEntity<?> getProjects(
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String techStack,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(required = false) Long assignedUserId) {
        
        User actor = getAuthenticatedUser();
        ProjectStatus projectStatus = null;
        if (status != null && !status.isBlank()) {
            try {
                projectStatus = ProjectStatus.valueOf(status.toUpperCase());
            } catch (IllegalArgumentException e) {
                return ResponseEntity.badRequest().body(Map.of("message", "Invalid project status filter: " + status));
            }
        }

        Long effectiveUserId = null;
        if (actor.getRole() == Role.SUPER_ADMIN || "superadmin@academic.com".equalsIgnoreCase(actor.getEmail())) {
            effectiveUserId = assignedUserId;
        } else if (actor.getRole() == Role.ADMIN) {
            effectiveUserId = assignedUserId;
        } else {
            // Regular USER or PROJECT_DEVELOPER sees scoped projects
            effectiveUserId = actor.getId();
        }

        List<Project> projects = projectService.searchProjects(search, projectStatus, techStack, startDate, endDate, effectiveUserId);
        return ResponseEntity.ok(projects);
    }

    @GetMapping("/user/projects")
    public ResponseEntity<?> getUserProjects() {
        User actor = getAuthenticatedUser();
        List<Project> projects = projectService.getAssignedProjectsForUser(actor.getId());
        return ResponseEntity.ok(projects);
    }

    @GetMapping("/dashboard")
    public ResponseEntity<?> getDashboardSummary() {
        User actor = getAuthenticatedUser();
        Map<String, Object> dashboard = projectService.getDashboardSummary(actor);
        return ResponseEntity.ok(dashboard);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getProjectById(@PathVariable Long id) {
        User actor = getAuthenticatedUser();
        try {
            // Authorization Check for non-superadmin roles (Admins and Users must be assigned)
            if (actor.getRole() != Role.SUPER_ADMIN) {
                boolean isAssigned = projectAssignmentRepository.findActiveAssignment(id, actor.getId()).isPresent();
                if (!isAssigned) {
                    return ResponseEntity.status(HttpStatus.FORBIDDEN)
                            .body(Map.of("message", "Access denied: You are not assigned to this project."));
                }
            }

            Project project = projectService.getProjectById(id);
            return ResponseEntity.ok(project);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", e.getMessage()));
        }
    }

    @GetMapping("/by-requirement/{reqId}")
    public ResponseEntity<?> getProjectByRequirementId(@PathVariable Long reqId) {
        getAuthenticatedUser();
        return projectService.getProjectByLinkedRequirementId(reqId)
                .<ResponseEntity<?>>map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", "No linked project found for requirement ID " + reqId)));
    }

    @PostMapping
    public ResponseEntity<?> createProject(@RequestBody ProjectCreateRequest request) {
        User actor = getAuthenticatedUser();

        // RBAC Check: Only Super Admin can create new projects
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to create new projects."));
        }

        try {
            Project project = projectService.createProject(request, actor.getEmail());
            return ResponseEntity.status(HttpStatus.CREATED).body(project);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateProject(@PathVariable Long id, @RequestBody ProjectUpdateRequest request) {
        User actor = getAuthenticatedUser();

        // RBAC Check: Only Super Admin can edit project parameters
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to edit project details."));
        }

        try {
            Project project = projectService.updateProject(id, request, actor.getEmail());
            return ResponseEntity.ok(project);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @RequestMapping(value = "/{id}/status", method = {RequestMethod.PATCH, RequestMethod.PUT})
    public ResponseEntity<?> updateProjectStatus(@PathVariable Long id, @RequestBody ProjectStatusUpdateRequest request) {
        User actor = getAuthenticatedUser();

        // RBAC Check: Regular users cannot transition project status
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Regular users are unauthorized to alter project status."));
        }

        try {
            Project project = projectService.changeStatus(id, request.getStatus(), actor.getEmail());
            return ResponseEntity.ok(project);
        } catch (IllegalStateException | IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", e.getMessage()));
        }
    }

    // ----------------------------------------------------
    // Project Assignments Endpoints
    // ----------------------------------------------------

    @GetMapping("/{id}/assignments")
    public ResponseEntity<?> getProjectAssignments(@PathVariable Long id) {
        getAuthenticatedUser();
        try {
            List<ProjectAssignment> assignments = projectAssignmentService.getActiveAssignmentsByProject(id);
            return ResponseEntity.ok(assignments);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping({"/{id}/assign", "/{id}/assignments"})
    public ResponseEntity<?> assignUserToProject(@PathVariable Long id, @RequestBody AssignmentRequest request) {
        User actor = getAuthenticatedUser();

        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Admins are authorized to assign users to projects."));
        }

        try {
            ProjectAssignment assignment = projectAssignmentService.assignUserToProject(
                    id,
                    request.getUserId(),
                    request.getExpiredAt(),
                    request.getNotes(),
                    actor.getEmail()
            );
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                    "success", true,
                    "message", "Project assigned successfully",
                    "assignment", assignment
            ));
        } catch (org.springframework.security.access.AccessDeniedException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping({"/{id}/assign/{userId}", "/{id}/assignments/user/{userId}"})
    public ResponseEntity<?> removeAssignmentByUser(@PathVariable Long id, @PathVariable Long userId) {
        User actor = getAuthenticatedUser();

        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Admins can revoke project assignments."));
        }

        try {
            projectAssignmentService.deactivateAssignmentByUser(id, userId, actor.getEmail());
            return ResponseEntity.ok(Map.of("success", true, "message", "Project assignment successfully revoked."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @Autowired
    private com.academic.service.OrderService orderService;

    @Autowired
    private com.academic.service.NotificationService notificationService;

    @PostMapping("/{id}/assign-developer")
    public ResponseEntity<?> assignDeveloper(
            @PathVariable Long id,
            @RequestBody Map<String, Long> payload) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN && actor.getRole() != Role.ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        Long devId = payload.get("developerId");
        if (devId == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "developerId is required."));
        }

        User dev = userService.findById(devId)
                .orElseThrow(() -> new IllegalArgumentException("Developer not found: " + devId));

        Project p = projectService.getProjectById(id);
        p.setDeveloper(dev);
        p.setStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        p.setLifecycleStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        Project saved = projectService.save(p);

        // Also assign developer in project_assignments
        projectAssignmentService.assignUserToProject(id, devId, null, "Assigned Developer", actor.getEmail());

        notificationService.sendNotification(dev.getEmail(), "PROJECT_DEVELOPER",
                "New Project Assigned",
                "You have been assigned to project '" + p.getProjectName() + "' (" + p.getProjectCode() + ").",
                "/developer/workspace");

        return ResponseEntity.ok(Map.of("success", true, "message", "Developer assigned successfully.", "project", saved));
    }

    @PostMapping("/{id}/assign-reviewer")
    public ResponseEntity<?> assignReviewer(
            @PathVariable Long id,
            @RequestBody Map<String, Long> payload) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied. Only Super Admin can assign Reviewer Admins."));
        }

        Long reviewerId = payload.get("reviewerId");
        if (reviewerId == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "reviewerId is required."));
        }

        User reviewer = userService.findById(reviewerId)
                .orElseThrow(() -> new IllegalArgumentException("Reviewer Admin not found: " + reviewerId));

        Project p = projectService.getProjectById(id);
        p.setReviewerAdmin(reviewer);
        Project saved = projectService.save(p);

        // Also assign reviewer in project_assignments
        projectAssignmentService.assignUserToProject(id, reviewerId, null, "Assigned Reviewer Admin", actor.getEmail());

        notificationService.sendNotification(reviewer.getEmail(), "ADMIN",
                "Assigned as Project Reviewer",
                "You have been assigned as Reviewer for project '" + p.getProjectName() + "' (" + p.getProjectCode() + ").",
                "/admin/project-review");

        return ResponseEntity.ok(Map.of("success", true, "message", "Reviewer Admin assigned successfully.", "project", saved));
    }

    @PostMapping("/{id}/developer-submit-review")
    public ResponseEntity<?> developerSubmitReview(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, String> payload) {
        User actor = getAuthenticatedUser();
        Project p = projectService.getProjectById(id);

        if (actor.getRole() != Role.PROJECT_DEVELOPER && actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Only assigned developer can submit deliverables for review."));
        }
        if (actor.getRole() == Role.PROJECT_DEVELOPER && (p.getDeveloper() == null || !p.getDeveloper().getId().equals(actor.getId()))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "You can only submit deliverables for projects assigned to you."));
        }

        String notes = payload != null ? payload.getOrDefault("notes", "Developer marked development complete and submitted for review.") : "";
        p.setStatus(ProjectStatus.READY_FOR_REVIEW);
        p.setLifecycleStatus(ProjectStatus.READY_FOR_REVIEW);
        p.setReviewNotes(notes);
        Project saved = projectService.save(p);

        if (p.getReviewerAdmin() != null) {
            notificationService.sendNotification(p.getReviewerAdmin().getEmail(), "ADMIN",
                    "Project Ready for Review",
                    "Developer has submitted deliverables for '" + p.getProjectName() + "' (" + p.getProjectCode() + ").",
                    "/admin/project-review");
        }

        return ResponseEntity.ok(Map.of("success", true, "message", "Project submitted for review successfully.", "project", saved));
    }

    @PostMapping("/{id}/admin-review")
    public ResponseEntity<?> adminReview(
            @PathVariable Long id,
            @RequestBody Map<String, String> payload) {
        User actor = getAuthenticatedUser();
        Project p = projectService.getProjectById(id);

        if (actor.getRole() != Role.SUPER_ADMIN && actor.getRole() != Role.ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied. Only Super Admin or assigned Reviewer Admin can review projects."));
        }
        if (actor.getRole() == Role.ADMIN && (p.getReviewerAdmin() == null || !p.getReviewerAdmin().getId().equals(actor.getId()))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "You can only review projects assigned to you."));
        }

        String action = payload.getOrDefault("action", "APPROVE");
        String notes = payload.getOrDefault("notes", "");

        if ("APPROVE".equalsIgnoreCase(action)) {
            p.setStatus(ProjectStatus.REVIEW_APPROVED);
            p.setLifecycleStatus(ProjectStatus.READY_FOR_FINAL_PAYMENT);
            p.setReviewNotes(notes);
            projectService.save(p);

            // Notify assigned users/customers that project is ready for final payment
            if (p.getDeveloper() != null) {
                notificationService.sendNotification(p.getDeveloper().getEmail(), "PROJECT_DEVELOPER",
                        "Project Review Approved",
                        "Deliverables for '" + p.getProjectName() + "' passed review with status APPROVED.",
                        "/developer/workspace");
            }
            return ResponseEntity.ok(Map.of("success", true, "message", "Project review approved. Ready for customer final payment.", "project", p));
        } else if ("REQUEST_CHANGES".equalsIgnoreCase(action)) {
            p.setStatus(ProjectStatus.CHANGES_REQUESTED);
            p.setLifecycleStatus(ProjectStatus.CHANGES_REQUESTED);
            p.setChangeRequestNotes(notes);
            projectService.save(p);

            if (p.getDeveloper() != null) {
                notificationService.sendNotification(p.getDeveloper().getEmail(), "PROJECT_DEVELOPER",
                        "Revisions Requested on Project",
                        "Reviewer requested changes for '" + p.getProjectName() + "': " + notes,
                        "/developer/workspace");
            }
            return ResponseEntity.ok(Map.of("success", true, "message", "Revisions requested from developer.", "project", p));
        }

        return ResponseEntity.badRequest().body(Map.of("message", "Invalid review action: " + action));
    }

    @PostMapping("/{id}/pay-remaining")
    public ResponseEntity<?> payRemaining(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, Object> body) {
        try {
            User actor = getAuthenticatedUser();
            Double amount = body != null && body.containsKey("amount") ? Double.valueOf(body.get("amount").toString()) : null;
            String idempotencyKey = body != null && body.containsKey("idempotencyKey") ? (String) body.get("idempotencyKey") : null;

            var order = orderService.processProjectRemainingPayment(id, amount, idempotencyKey, actor);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Final payment verified! Project deliverables and files are now unlocked.",
                    "order", order
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/{id}/purchase-marketplace")
    public ResponseEntity<?> purchaseMarketplace(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, Object> body) {
        try {
            User actor = getAuthenticatedUser();
            String idempotencyKey = body != null && body.containsKey("idempotencyKey") ? (String) body.get("idempotencyKey") : null;

            var order = orderService.processMarketplacePurchase(id, idempotencyKey, actor);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Marketplace project purchased successfully! Project access unlocked.",
                    "order", order
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @GetMapping("/my-developer-projects")
    public ResponseEntity<?> getMyDeveloperProjects() {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.PROJECT_DEVELOPER && actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }
        List<Project> list = actor.getRole() == Role.SUPER_ADMIN 
                ? projectService.getAllProjectsList() 
                : projectService.getProjectsByDeveloperId(actor.getId());
        return ResponseEntity.ok(list);
    }

    @GetMapping("/my-review-projects")
    public ResponseEntity<?> getMyReviewProjects() {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.ADMIN && actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }
        List<Project> list = actor.getRole() == Role.SUPER_ADMIN
                ? projectService.getAllProjectsList()
                : projectService.getProjectsByReviewerAdminId(actor.getId());
        return ResponseEntity.ok(list);
    }

    @GetMapping("/marketplace")
    public ResponseEntity<?> getMarketplaceProjects() {
        List<Project> list = projectService.getMarketplaceProjects();
        return ResponseEntity.ok(list);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteProjectById(@PathVariable Long id) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to delete projects."));
        }

        try {
            projectService.deleteProject(id, actor.getEmail());
            return ResponseEntity.ok(Map.of("success", true, "message", "Project successfully deleted."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping
    public ResponseEntity<?> deleteAllProjects() {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Access denied. Only Super Admin is authorized to delete all projects."));
        }

        try {
            projectService.deleteAllProjects(actor.getEmail());
            return ResponseEntity.ok(Map.of("success", true, "message", "All projects successfully deleted."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
