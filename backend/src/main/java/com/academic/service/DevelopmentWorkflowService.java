package com.academic.service;

import com.academic.model.*;
import com.academic.repository.AssetRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.Year;
import java.util.*;

/**
 * Custom project development after a requirement's advance is settled.
 *
 * <pre>
 * DEVELOPER_ASSIGNED --developer accepts--> IN_PROGRESS --submit--> READY_FOR_REVIEW
 * READY_FOR_REVIEW --reviewer approves--> REVIEW_APPROVED (lifecycle READY_FOR_FINAL_PAYMENT)
 * READY_FOR_REVIEW --reviewer requests changes--> CHANGES_REQUESTED --resubmit--> READY_FOR_REVIEW
 * READY_FOR_FINAL_PAYMENT --student pays (OrderService)--> ACCESS_GRANTED
 * </pre>
 */
@Service
public class DevelopmentWorkflowService {

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private RequirementService requirementService;

    @Autowired
    private LibraryService libraryService;

    @Autowired
    private OrderService orderService;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private StatusHistoryService statusHistoryService;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private NotificationService notificationService;

    // ------------------------------------------------------------------
    // Super Admin: create project and assign people
    // ------------------------------------------------------------------

    /**
     * Creates the development project for a requirement whose advance is settled and assigns
     * the developer (and optionally a reviewer). Idempotent per requirement.
     */
    @Transactional
    public Project startDevelopment(Long requirementId, Long developerId, Long reviewerId, String deadlineNotes, User actor) {
        requireSuperAdmin(actor);
        Requirement req = requirementRepository.findById(requirementId)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found: " + requirementId));
        if (req.getStatus() != RequirementStatus.ADVANCE_PAYMENT_COMPLETED) {
            throw new IllegalStateException("Development can start only after the advance is settled (status: " + req.getStatus() + ").");
        }
        User developer = requireRole(developerId, Role.PROJECT_DEVELOPER, "developer");
        User reviewer = reviewerId != null ? requireReviewer(reviewerId) : null;

        Project project = projectRepository.findByLinkedRequirementId(req.getId()).orElseGet(Project::new);
        boolean isNew = project.getId() == null;
        if (isNew) {
            project.setProjectCode(nextDevelopmentCode());
            project.setProjectName(req.getTitle());
            project.setDescription(req.getProblemStatement() + (req.getDescription() != null ? "\n\n" + req.getDescription() : ""));
            project.setTechnologyStack(req.getTechnologyStack());
            project.setLinkedRequirementId(req.getId());
            project.setProjectType(ProjectType.CUSTOM);
            project.setCatalogStatus(CatalogStatus.DRAFT);
            project.setMarketplace(false);
            project.setCreatedBy(actor.getEmail());
        }
        project.setBudget(req.getBudget());
        project.setAdvanceAmount(req.getAdvanceAmount());
        project.setRemainingAmount(req.getRemainingAmount() != null ? req.getRemainingAmount() : BigDecimal.ZERO);
        project.setAdvancePaymentStatus(req.getAdvancePaymentStatus());
        project.setRemainingPaymentStatus(req.getRemainingAmount() != null && req.getRemainingAmount().signum() > 0 ? "PENDING" : "NOT_REQUIRED");
        project.setDeveloper(developer);
        project.setDeveloperAcceptedAt(null);
        if (reviewer != null) {
            project.setReviewerAdmin(reviewer);
        }
        ProjectStatus previous = isNew ? null : project.getLifecycleStatus();
        project.setStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        project.setLifecycleStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        project.setUpdatedBy(actor.getEmail());
        Project saved = projectRepository.save(project);
        if (isNew) {
            libraryService.ensureCategoryFolders(saved, actor.getEmail());
        }

        statusHistoryService.record(StatusHistoryService.PROJECT, saved.getId(), previous, ProjectStatus.DEVELOPER_ASSIGNED, actor.getEmail(),
                "Assigned to " + developer.getFullName() + (reviewer != null ? "; reviewer " + reviewer.getFullName() : "")
                        + (deadlineNotes != null && !deadlineNotes.isBlank() ? ". " + deadlineNotes : ""));
        requirementService.transition(req, RequirementStatus.IN_PROGRESS, actor, "Development project " + saved.getProjectCode() + " created");

        notificationService.sendNotification(developer.getEmail(), "PROJECT_DEVELOPER", "New development assignment",
                "You have been assigned '" + saved.getProjectName() + "' (" + saved.getProjectCode() + "). Please review and accept it.",
                "/projects/" + saved.getId());
        if (reviewer != null) {
            notificationService.sendNotification(reviewer.getEmail(), reviewer.getRole().name(), "Reviewer assignment",
                    "You will review '" + saved.getProjectName() + "' when the developer submits it.", "/projects/" + saved.getId());
        }
        notificationService.sendNotification(req.getUser().getEmail(), "USER", "Development started",
                "A developer has been assigned to '" + req.getTitle() + "'.", "/projects/" + saved.getId());
        return saved;
    }

    @Transactional
    public Project reassignDeveloper(Long projectId, Long developerId, User actor) {
        requireSuperAdmin(actor);
        Project project = getCustomProject(projectId);
        if (isDelivered(project)) {
            throw new IllegalStateException("A delivered project cannot be reassigned.");
        }
        User developer = requireRole(developerId, Role.PROJECT_DEVELOPER, "developer");
        User previousDev = project.getDeveloper();
        project.setDeveloper(developer);
        project.setDeveloperAcceptedAt(null);
        ProjectStatus previous = project.getLifecycleStatus();
        project.setStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        project.setLifecycleStatus(ProjectStatus.DEVELOPER_ASSIGNED);
        Project saved = projectRepository.save(project);
        statusHistoryService.record(StatusHistoryService.PROJECT, projectId, previous, ProjectStatus.DEVELOPER_ASSIGNED, actor.getEmail(),
                "Reassigned from " + (previousDev != null ? previousDev.getFullName() : "nobody") + " to " + developer.getFullName());
        notificationService.sendNotification(developer.getEmail(), "PROJECT_DEVELOPER", "New development assignment",
                "You have been assigned '" + saved.getProjectName() + "'.", "/projects/" + saved.getId());
        return saved;
    }

    @Transactional
    public Project assignReviewer(Long projectId, Long reviewerId, User actor) {
        requireSuperAdmin(actor);
        Project project = getCustomProject(projectId);
        User reviewer = requireReviewer(reviewerId);
        project.setReviewerAdmin(reviewer);
        Project saved = projectRepository.save(project);
        statusHistoryService.record(StatusHistoryService.PROJECT, projectId, project.getLifecycleStatus(), project.getLifecycleStatus(),
                actor.getEmail(), "Reviewer set to " + reviewer.getFullName());
        auditLogService.log(actor.getEmail(), "ASSIGN_REVIEWER", reviewer.getEmail() + " reviews " + project.getProjectCode());
        notificationService.sendNotification(reviewer.getEmail(), reviewer.getRole().name(), "Reviewer assignment",
                "You will review '" + saved.getProjectName() + "'.", "/projects/" + saved.getId());
        return saved;
    }

    // ------------------------------------------------------------------
    // Developer actions
    // ------------------------------------------------------------------

    @Transactional
    public Project accept(Long projectId, User actor) {
        Project project = getCustomProject(projectId);
        requireAssignedDeveloper(project, actor);
        if (project.getLifecycleStatus() != ProjectStatus.DEVELOPER_ASSIGNED) {
            throw new IllegalStateException("Only new assignments can be accepted (status: " + project.getLifecycleStatus() + ").");
        }
        project.setDeveloperAcceptedAt(LocalDateTime.now());
        move(project, ProjectStatus.IN_PROGRESS, actor, "Assignment accepted by developer");
        notifySuperAdmins("Assignment accepted", actor.getFullName() + " accepted '" + project.getProjectName() + "'.", "/projects/" + projectId);
        return project;
    }

    @Transactional
    public Project updateProgress(Long projectId, Integer percent, String note, User actor) {
        Project project = getCustomProject(projectId);
        requireAssignedDeveloper(project, actor);
        ProjectStatus s = project.getLifecycleStatus();
        if (s != ProjectStatus.IN_PROGRESS && s != ProjectStatus.CHANGES_REQUESTED && s != ProjectStatus.TESTING) {
            throw new IllegalStateException("Progress can be updated only while development is active (status: " + s + ").");
        }
        if (percent != null) {
            if (percent < 0 || percent > 100) throw new IllegalArgumentException("Progress must be between 0 and 100.");
            project.setProgressPercent(percent);
        }
        projectRepository.save(project);
        statusHistoryService.record(StatusHistoryService.PROJECT, projectId, s, s, actor.getEmail(),
                "Progress " + project.getProgressPercent() + "%" + (note != null && !note.isBlank() ? ": " + note.trim() : ""));
        return project;
    }

    @Transactional
    public Project submitForReview(Long projectId, String notes, User actor) {
        Project project = getCustomProject(projectId);
        requireAssignedDeveloper(project, actor);
        ProjectStatus s = project.getLifecycleStatus();
        if (s != ProjectStatus.IN_PROGRESS && s != ProjectStatus.CHANGES_REQUESTED && s != ProjectStatus.TESTING) {
            throw new IllegalStateException("Only active development can be submitted for review (status: " + s + ").");
        }
        if (assetRepository.findCurrentAssetsByProjectId(projectId).isEmpty()) {
            throw new IllegalStateException("Upload the deliverables (source code, documentation, demo) before submitting for review.");
        }
        project.setReviewNotes(notes);
        project.setProgressPercent(Math.max(project.getProgressPercent(), 90));
        move(project, ProjectStatus.READY_FOR_REVIEW, actor, notes == null || notes.isBlank() ? "Submitted for review" : "Submitted for review: " + notes.trim());

        if (project.getReviewerAdmin() != null) {
            notificationService.sendNotification(project.getReviewerAdmin().getEmail(), project.getReviewerAdmin().getRole().name(),
                    "Review requested", "'" + project.getProjectName() + "' is ready for your review.", "/projects/" + projectId);
        } else {
            notifySuperAdmins("Review requested", "'" + project.getProjectName() + "' is ready for review (no reviewer assigned).", "/projects/" + projectId);
        }
        return project;
    }

    // ------------------------------------------------------------------
    // Reviewer actions
    // ------------------------------------------------------------------

    @Transactional
    public Project review(Long projectId, String action, String notes, User actor) {
        Project project = getCustomProject(projectId);
        boolean isReviewer = project.getReviewerAdmin() != null && project.getReviewerAdmin().getId().equals(actor.getId());
        if (actor.getRole() != Role.SUPER_ADMIN && !isReviewer) {
            throw new AccessDeniedException("Only the assigned reviewer or the Super Admin can review this project.");
        }
        if (project.getLifecycleStatus() != ProjectStatus.READY_FOR_REVIEW) {
            throw new IllegalStateException("This project is not awaiting review (status: " + project.getLifecycleStatus() + ").");
        }
        String a = action == null ? "" : action.trim().toUpperCase();
        User requester = requesterOf(project);
        switch (a) {
            case "APPROVE" -> {
                project.setReviewNotes(notes);
                project.setChangeRequestNotes(null);
                ProjectStatus previous = project.getLifecycleStatus();
                project.setStatus(ProjectStatus.REVIEW_APPROVED);
                boolean balanceDue = project.getRemainingAmount() != null && project.getRemainingAmount().signum() > 0;
                project.setLifecycleStatus(balanceDue ? ProjectStatus.READY_FOR_FINAL_PAYMENT : ProjectStatus.REVIEW_APPROVED);
                project.setProgressPercent(100);
                projectRepository.save(project);
                statusHistoryService.record(StatusHistoryService.PROJECT, projectId, previous, project.getLifecycleStatus(), actor.getEmail(),
                        notes == null || notes.isBlank() ? "Review approved" : "Review approved: " + notes.trim());
                notifyDeveloper(project, "Review approved", "'" + project.getProjectName() + "' passed review.");
                if (balanceDue) {
                    if (requester != null) {
                        notificationService.sendNotification(requester.getEmail(), "USER", "Your project is ready",
                                "'" + project.getProjectName() + "' passed review. Pay the remaining " + project.getRemainingAmount() + " to unlock the deliverables.",
                                "/projects/" + projectId);
                    }
                } else if (requester != null) {
                    orderService.completeCustomDelivery(project, requester, null, "Approved; no balance due");
                }
            }
            case "REQUEST_CHANGES" -> {
                if (notes == null || notes.isBlank()) {
                    throw new IllegalArgumentException("Describe the changes you need.");
                }
                project.setChangeRequestNotes(notes.trim());
                move(project, ProjectStatus.CHANGES_REQUESTED, actor, "Changes requested: " + notes.trim());
                notifyDeveloper(project, "Changes requested", "Reviewer feedback on '" + project.getProjectName() + "': " + notes.trim());
            }
            default -> throw new IllegalArgumentException("Action must be APPROVE or REQUEST_CHANGES.");
        }
        auditLogService.log(actor.getEmail(), "PROJECT_REVIEW_" + a, project.getProjectCode() + (notes != null ? ": " + notes : ""));
        return project;
    }

    // ------------------------------------------------------------------
    // Queries
    // ------------------------------------------------------------------

    public List<StatusHistory> timeline(Long projectId, User actor) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found: " + projectId));
        if (accessControlService.getAccessLevel(project, actor) == AccessControlService.ProjectAccessLevel.NONE) {
            throw new AccessDeniedException("Access denied.");
        }
        return statusHistoryService.timeline(StatusHistoryService.PROJECT, projectId);
    }

    public List<Project> developerProjects(User actor) {
        if (actor.getRole() == Role.SUPER_ADMIN) {
            return projectRepository.findAllCustomProjects();
        }
        if (actor.getRole() != Role.PROJECT_DEVELOPER) {
            throw new AccessDeniedException("Access denied.");
        }
        return projectRepository.findByDeveloperId(actor.getId());
    }

    public List<Project> reviewProjects(User actor) {
        if (actor.getRole() == Role.SUPER_ADMIN) {
            return projectRepository.findAllCustomProjects().stream()
                    .filter(p -> p.getLifecycleStatus() == ProjectStatus.READY_FOR_REVIEW || p.getReviewerAdmin() != null)
                    .toList();
        }
        if (actor.getRole() != Role.ADMIN) {
            throw new AccessDeniedException("Access denied.");
        }
        return projectRepository.findByReviewerAdminId(actor.getId());
    }

    /** Developers for assignment pickers, with their active workload. */
    public List<Map<String, Object>> developerOptions() {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (User dev : userRepository.findByRoleAndDeletedFalse(Role.PROJECT_DEVELOPER)) {
            if (dev.getStatus() != UserStatus.ACTIVE) continue;
            long active = projectRepository.findByDeveloperId(dev.getId()).stream().filter(p -> !isDelivered(p)).count();
            rows.add(Map.of("id", dev.getId(), "fullName", dev.getFullName(), "email", dev.getEmail(), "activeProjects", active));
        }
        return rows;
    }

    /** Reviewers: Super Admins and college administrators. */
    public List<Map<String, Object>> reviewerOptions() {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Role role : List.of(Role.SUPER_ADMIN, Role.ADMIN)) {
            for (User u : userRepository.findByRoleAndDeletedFalse(role)) {
                if (u.getStatus() != UserStatus.ACTIVE) continue;
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("id", u.getId());
                m.put("fullName", u.getFullName());
                m.put("email", u.getEmail());
                m.put("role", u.getRole());
                m.put("collegeName", u.getCollege() != null ? u.getCollege().getName() : null);
                rows.add(m);
            }
        }
        return rows;
    }

    // ------------------------------------------------------------------
    // Internals
    // ------------------------------------------------------------------

    private void move(Project project, ProjectStatus next, User actor, String note) {
        ProjectStatus previous = project.getLifecycleStatus();
        project.setStatus(next);
        project.setLifecycleStatus(next);
        project.setUpdatedBy(actor.getEmail());
        projectRepository.save(project);
        statusHistoryService.record(StatusHistoryService.PROJECT, project.getId(), previous, next, actor.getEmail(), note);
        auditLogService.log(actor.getEmail(), "PROJECT_" + next.name(), project.getProjectCode() + ": " + previous + " -> " + next);
    }

    private Project getCustomProject(Long projectId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found: " + projectId));
        if (project.isLibrary()) {
            throw new IllegalArgumentException("Library projects do not have a development workflow.");
        }
        return project;
    }

    private void requireAssignedDeveloper(Project project, User actor) {
        if (actor.getRole() != Role.PROJECT_DEVELOPER || !accessControlService.isDeveloperOf(project, actor)) {
            throw new AccessDeniedException("Only the assigned developer can do this.");
        }
    }

    private static void requireSuperAdmin(User actor) {
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Only the Super Admin can assign developers and reviewers.");
        }
    }

    private User requireRole(Long userId, Role role, String label) {
        if (userId == null) throw new IllegalArgumentException("Select a " + label + ".");
        User u = userRepository.findById(userId).filter(x -> !x.isDeleted())
                .orElseThrow(() -> new NoSuchElementException("User not found: " + userId));
        if (u.getRole() != role || u.getStatus() != UserStatus.ACTIVE) {
            throw new IllegalArgumentException(u.getFullName() + " is not an active " + label + ".");
        }
        return u;
    }

    private User requireReviewer(Long userId) {
        User u = userRepository.findById(userId).filter(x -> !x.isDeleted())
                .orElseThrow(() -> new NoSuchElementException("User not found: " + userId));
        if ((u.getRole() != Role.ADMIN && u.getRole() != Role.SUPER_ADMIN) || u.getStatus() != UserStatus.ACTIVE) {
            throw new IllegalArgumentException("Reviewers must be active administrators.");
        }
        return u;
    }

    private User requesterOf(Project project) {
        if (project.getLinkedRequirementId() == null) return null;
        return requirementRepository.findById(project.getLinkedRequirementId()).map(Requirement::getUser).orElse(null);
    }

    private static boolean isDelivered(Project p) {
        return p.getLifecycleStatus() == ProjectStatus.ACCESS_GRANTED || p.getLifecycleStatus() == ProjectStatus.COMPLETED;
    }

    private void notifyDeveloper(Project project, String title, String message) {
        if (project.getDeveloper() != null) {
            notificationService.sendNotification(project.getDeveloper().getEmail(), "PROJECT_DEVELOPER", title, message, "/projects/" + project.getId());
        }
    }

    private void notifySuperAdmins(String title, String message, String link) {
        userRepository.findByRoleAndDeletedFalse(Role.SUPER_ADMIN)
                .forEach(sa -> notificationService.sendNotification(sa.getEmail(), "SUPER_ADMIN", title, message, link));
    }

    private String nextDevelopmentCode() {
        String code;
        do {
            code = "DEV-" + Year.now().getValue() + "-" + String.format("%04d", new Random().nextInt(10000));
        } while (projectRepository.existsByProjectCode(code));
        return code;
    }
}
