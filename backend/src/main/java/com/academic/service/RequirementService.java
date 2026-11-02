package com.academic.service;

import com.academic.dto.RequirementSummaryDto;
import com.academic.model.*;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Custom development requirements.
 *
 * <pre>
 * DRAFT --submit--> SUBMITTED --college admin forwards--> SUPER_ADMIN_REVIEW
 *   ^                   |  \--return--> CHANGES_REQUESTED --resubmit--> SUBMITTED
 *   |                   \--reject--> REJECTED
 * SUPER_ADMIN_REVIEW --approve with quote--> ADVANCE_PAYMENT_PENDING --paid--> ADVANCE_PAYMENT_COMPLETED
 * ADVANCE_PAYMENT_COMPLETED --developer assigned--> IN_PROGRESS --deliverables unlocked--> COMPLETED
 * </pre>
 * Payments are handled by {@link OrderService}; developer assignment by {@link DevelopmentWorkflowService}.
 */
@Service
public class RequirementService {

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private StatusHistoryService statusHistoryService;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private NotificationService notificationService;

    // ------------------------------------------------------------------
    // Queries (college-scoped)
    // ------------------------------------------------------------------

    public List<RequirementSummaryDto> listForActor(User actor, String query, String statusStr) {
        RequirementStatus status = parseStatus(statusStr);
        String q = query != null && !query.trim().isEmpty() ? query.trim() : null;
        List<Requirement> rows = switch (actor.getRole()) {
            case SUPER_ADMIN -> requirementRepository.searchAllRequirements(status, q);
            case ADMIN -> actor.getCollege() == null ? List.of()
                    : requirementRepository.searchCollegeRequirements(actor.getCollege().getId(), status, q);
            case USER -> requirementRepository.searchUserRequirements(actor, status, q);
            case PROJECT_DEVELOPER -> projectRepository.findByDeveloperId(actor.getId()).stream()
                    .map(Project::getLinkedRequirementId).filter(Objects::nonNull)
                    .map(requirementRepository::findById).flatMap(Optional::stream)
                    .filter(r -> status == null || r.getStatus() == status)
                    .toList();
        };
        return rows.stream().map(RequirementSummaryDto::fromEntity).collect(Collectors.toList());
    }

    public Requirement getRequirementById(Long id, User actor) {
        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found with id: " + id));
        if (!accessControlService.canViewRequirement(actor, req)) {
            throw new AccessDeniedException("Access denied: You cannot view this requirement.");
        }
        return req;
    }

    public Map<String, Object> getUserStats(User user) {
        Map<String, Object> stats = new HashMap<>();
        stats.put("myRequirements", requirementRepository.countByUser(user));
        stats.put("pendingSubmissions", requirementRepository.countByUserAndStatus(user, RequirementStatus.SUBMITTED)
                + requirementRepository.countByUserAndStatus(user, RequirementStatus.SUPER_ADMIN_REVIEW));
        stats.put("awaitingAdvance", requirementRepository.countByUserAndStatus(user, RequirementStatus.ADVANCE_PAYMENT_PENDING));
        stats.put("inProgress", requirementRepository.countByUserAndStatus(user, RequirementStatus.IN_PROGRESS));
        stats.put("completed", requirementRepository.countByUserAndStatus(user, RequirementStatus.COMPLETED));
        return stats;
    }

    public List<StatusHistory> timeline(Long id, User actor) {
        getRequirementById(id, actor);
        return statusHistoryService.timeline(StatusHistoryService.REQUIREMENT, id);
    }

    // ------------------------------------------------------------------
    // Student actions
    // ------------------------------------------------------------------

    @Transactional
    public Requirement createRequirement(Requirement input, User actor) {
        if (actor.getRole() != Role.USER) {
            throw new AccessDeniedException("Only student accounts can submit project requirements.");
        }
        College college = accessControlService.requireCollege(actor);
        if (input.getTitle() == null || input.getTitle().trim().isEmpty()) {
            throw new IllegalArgumentException("Requirement title is required.");
        }
        if (input.getProblemStatement() == null || input.getProblemStatement().trim().isEmpty()) {
            throw new IllegalArgumentException("Problem statement is required.");
        }
        if (input.getBudget() != null && input.getBudget().signum() < 0) {
            throw new IllegalArgumentException("Budget cannot be negative.");
        }

        Requirement req = new Requirement();
        req.setTitle(input.getTitle().trim());
        req.setProblemStatement(input.getProblemStatement().trim());
        req.setDescription(input.getDescription());
        req.setBudget(input.getBudget());
        req.setTechnologyStack(input.getTechnologyStack());
        req.setImageUrl(input.getImageUrl());
        req.setAudioUrl(input.getAudioUrl());
        req.setUser(actor);
        req.setCollege(college);
        req.setStatus(RequirementStatus.DRAFT);
        req.setAdvancePaymentStatus("PENDING");
        req.setRemainingPaymentStatus("PENDING");

        Requirement saved = requirementRepository.save(req);
        statusHistoryService.record(StatusHistoryService.REQUIREMENT, saved.getId(), null, RequirementStatus.DRAFT, actor.getEmail(), "Requirement drafted");
        auditLogService.log(actor.getEmail(), "CREATE_REQUIREMENT", "Created requirement #" + saved.getId() + ": " + saved.getTitle());
        return saved;
    }

    @Transactional
    public Requirement updateRequirement(Long id, Requirement updateData, User actor) {
        Requirement req = getRequirementById(id, actor);
        boolean owner = req.getUser().getId().equals(actor.getId());
        if (actor.getRole() == Role.USER) {
            if (!owner) throw new AccessDeniedException("Access denied: You do not own this requirement.");
            if (req.getStatus() != RequirementStatus.DRAFT && req.getStatus() != RequirementStatus.CHANGES_REQUESTED) {
                throw new IllegalStateException("A requirement can only be edited while in draft or when changes were requested.");
            }
        } else if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Only the student or the Super Admin can edit a requirement.");
        }

        if (updateData.getTitle() != null && !updateData.getTitle().trim().isEmpty()) req.setTitle(updateData.getTitle().trim());
        if (updateData.getProblemStatement() != null && !updateData.getProblemStatement().trim().isEmpty()) req.setProblemStatement(updateData.getProblemStatement().trim());
        if (updateData.getDescription() != null) req.setDescription(updateData.getDescription());
        if (updateData.getBudget() != null) {
            if (updateData.getBudget().signum() < 0) throw new IllegalArgumentException("Budget cannot be negative.");
            req.setBudget(updateData.getBudget());
        }
        if (updateData.getTechnologyStack() != null) req.setTechnologyStack(updateData.getTechnologyStack());
        if (updateData.getImageUrl() != null) req.setImageUrl(updateData.getImageUrl());
        if (updateData.getAudioUrl() != null) req.setAudioUrl(updateData.getAudioUrl());

        Requirement saved = requirementRepository.save(req);
        auditLogService.log(actor.getEmail(), "UPDATE_REQUIREMENT", "Updated requirement #" + saved.getId());
        return saved;
    }

    @Transactional
    public Requirement submitRequirement(Long id, User actor) {
        Requirement req = getRequirementById(id, actor);
        if (!req.getUser().getId().equals(actor.getId())) {
            throw new AccessDeniedException("Only the student who created the requirement can submit it.");
        }
        if (req.getStatus() != RequirementStatus.DRAFT && req.getStatus() != RequirementStatus.CHANGES_REQUESTED) {
            throw new IllegalStateException("Only draft requirements or those returned for changes can be submitted.");
        }
        transition(req, RequirementStatus.SUBMITTED, actor, "Submitted for college review");

        List<User> admins = req.getCollege() != null ? userRepository.findAdminsByCollegeId(req.getCollege().getId()) : List.of();
        if (admins.isEmpty()) {
            notifySuperAdmins("New requirement (no college admin)",
                    "'" + req.getTitle() + "' was submitted by " + actor.getFullName() + " and needs review.", "/requirements/" + req.getId());
        }
        admins.forEach(a -> notificationService.sendNotification(a.getEmail(), "ADMIN", "New project requirement",
                actor.getFullName() + " submitted '" + req.getTitle() + "'.", "/requirements/" + req.getId()));
        return req;
    }

    // ------------------------------------------------------------------
    // College admin review
    // ------------------------------------------------------------------

    /**
     * FORWARD to the Super Admin, RETURN to the student for changes, or REJECT.
     */
    @Transactional
    public Requirement collegeReview(Long id, String action, String notes, User actor) {
        Requirement req = getRequirementById(id, actor);
        if (actor.getRole() != Role.ADMIN && actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Only college administrators can review requirements.");
        }
        if (req.getStatus() != RequirementStatus.SUBMITTED) {
            throw new IllegalStateException("Only submitted requirements can be reviewed by the college (status: " + req.getStatus() + ").");
        }
        req.setCollegeAdminNotes(notes);
        String a = action == null ? "" : action.trim().toUpperCase();
        switch (a) {
            case "FORWARD" -> {
                req.setForwardedBy(actor.getEmail());
                req.setForwardedAt(LocalDateTime.now());
                transition(req, RequirementStatus.SUPER_ADMIN_REVIEW, actor, note("Forwarded for development approval", notes));
                notifySuperAdmins("Requirement forwarded for approval",
                        "'" + req.getTitle() + "' from " + collegeName(req) + " needs a quote.", "/requirements/" + req.getId());
                notifyStudent(req, "Requirement forwarded", "Your college forwarded '" + req.getTitle() + "' for development approval.");
            }
            case "RETURN" -> {
                transition(req, RequirementStatus.CHANGES_REQUESTED, actor, note("Returned to student", notes));
                notifyStudent(req, "Changes requested", "Your college asked for changes to '" + req.getTitle() + "'" + (notes != null && !notes.isBlank() ? ": " + notes : "."));
            }
            case "REJECT" -> {
                transition(req, RequirementStatus.REJECTED, actor, note("Rejected by college", notes));
                notifyStudent(req, "Requirement closed", "Your college closed '" + req.getTitle() + "'" + (notes != null && !notes.isBlank() ? ": " + notes : "."));
            }
            default -> throw new IllegalArgumentException("Action must be FORWARD, RETURN or REJECT.");
        }
        return req;
    }

    // ------------------------------------------------------------------
    // Super Admin review
    // ------------------------------------------------------------------

    /**
     * APPROVE with a quote (total budget and advance), REQUEST_CHANGES, or REJECT.
     * The Super Admin may also act on a SUBMITTED requirement directly.
     */
    @Transactional
    public Requirement superAdminReview(Long id, String action, String notes, BigDecimal budget, BigDecimal advance, User actor) {
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Only the Super Admin can approve development requests.");
        }
        Requirement req = getRequirementById(id, actor);
        if (req.getStatus() != RequirementStatus.SUPER_ADMIN_REVIEW && req.getStatus() != RequirementStatus.SUBMITTED) {
            throw new IllegalStateException("This requirement is not awaiting Super Admin review (status: " + req.getStatus() + ").");
        }
        req.setSuperAdminNotes(notes);
        String a = action == null ? "" : action.trim().toUpperCase();
        switch (a) {
            case "APPROVE" -> {
                BigDecimal total = budget != null ? budget : req.getBudget();
                if (total == null || total.signum() <= 0) {
                    throw new IllegalArgumentException("A total price greater than zero is required to approve.");
                }
                BigDecimal adv = advance != null ? advance : BigDecimal.ZERO;
                if (adv.signum() < 0 || adv.compareTo(total) > 0) {
                    throw new IllegalArgumentException("The advance must be between 0 and the total price.");
                }
                req.setBudget(total);
                req.setAdvanceAmount(adv);
                req.setRemainingAmount(total.subtract(adv));
                if (adv.signum() == 0) {
                    req.setAdvancePaymentStatus("NOT_REQUIRED");
                    transition(req, RequirementStatus.ADVANCE_PAYMENT_COMPLETED, actor, note("Approved; no advance required (total " + total + ")", notes));
                    notifyStudent(req, "Requirement approved", "'" + req.getTitle() + "' was approved. A developer will be assigned shortly.");
                } else {
                    transition(req, RequirementStatus.ADVANCE_PAYMENT_PENDING, actor, note("Approved with quote: total " + total + ", advance " + adv, notes));
                    notifyStudent(req, "Requirement approved — advance due",
                            "'" + req.getTitle() + "' was approved. Pay the advance of " + adv + " to start development.");
                }
            }
            case "REQUEST_CHANGES" -> {
                transition(req, RequirementStatus.CHANGES_REQUESTED, actor, note("Changes requested by Super Admin", notes));
                notifyStudent(req, "Changes requested", "Revisions were requested for '" + req.getTitle() + "'" + (notes != null && !notes.isBlank() ? ": " + notes : "."));
            }
            case "REJECT" -> {
                transition(req, RequirementStatus.REJECTED, actor, note("Rejected by Super Admin", notes));
                notifyStudent(req, "Requirement closed", "'" + req.getTitle() + "' was not approved" + (notes != null && !notes.isBlank() ? ": " + notes : "."));
            }
            default -> throw new IllegalArgumentException("Action must be APPROVE, REQUEST_CHANGES or REJECT.");
        }
        return req;
    }

    @Transactional
    public void deleteRequirement(Long id, User actor) {
        if (actor.getRole() != Role.SUPER_ADMIN) {
            throw new AccessDeniedException("Only the Super Admin can delete requirements.");
        }
        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found with id: " + id));
        if (projectRepository.findByLinkedRequirementId(id).isPresent()) {
            throw new IllegalStateException("This requirement already has a development project and cannot be deleted.");
        }
        requirementRepository.delete(req);
        auditLogService.log(actor.getEmail(), "DELETE_REQUIREMENT", "Deleted requirement #" + id + ": " + req.getTitle());
    }

    public Requirement getRequirementEntityById(Long id) {
        return requirementRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Requirement not found with id: " + id));
    }

    @Transactional
    public Requirement save(Requirement requirement) {
        return requirementRepository.save(requirement);
    }

    // ------------------------------------------------------------------
    // Internals
    // ------------------------------------------------------------------

    void transition(Requirement req, RequirementStatus next, User actor, String note) {
        RequirementStatus previous = req.getStatus();
        req.setStatus(next);
        requirementRepository.save(req);
        statusHistoryService.record(StatusHistoryService.REQUIREMENT, req.getId(), previous, next, actor.getEmail(), note);
        auditLogService.log(actor.getEmail(), "REQUIREMENT_" + next.name(),
                String.format("Requirement #%d '%s': %s -> %s", req.getId(), req.getTitle(), previous, next));
    }

    private void notifyStudent(Requirement req, String title, String message) {
        if (req.getUser() != null) {
            notificationService.sendNotification(req.getUser().getEmail(), "USER", title, message, "/requirements/" + req.getId());
        }
    }

    private void notifySuperAdmins(String title, String message, String link) {
        userRepository.findByRoleAndDeletedFalse(Role.SUPER_ADMIN)
                .forEach(sa -> notificationService.sendNotification(sa.getEmail(), "SUPER_ADMIN", title, message, link));
    }

    private static String collegeName(Requirement req) {
        return req.getCollege() != null ? req.getCollege().getName() : "an unassigned student";
    }

    private static String note(String base, String notes) {
        return notes == null || notes.isBlank() ? base : base + ": " + notes.trim();
    }

    private RequirementStatus parseStatus(String statusStr) {
        if (statusStr != null && !statusStr.trim().isEmpty() && !"ALL".equalsIgnoreCase(statusStr.trim())) {
            try {
                return RequirementStatus.valueOf(statusStr.trim().toUpperCase());
            } catch (IllegalArgumentException e) {
                throw new IllegalArgumentException("Unknown requirement status: " + statusStr);
            }
        }
        return null;
    }
}
