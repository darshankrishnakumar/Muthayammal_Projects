package com.academic.service;

import com.academic.dto.RequirementSummaryDto;
import com.academic.model.Requirement;
import com.academic.model.RequirementStatus;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.repository.RequirementRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@SuppressWarnings("null")
public class RequirementService {

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private ProjectService projectService;

    public List<RequirementSummaryDto> getUserRequirements(User user, String query, String statusStr) {
        RequirementStatus status = parseStatus(statusStr);
        String cleanQuery = (query != null && !query.trim().isEmpty()) ? query.trim() : null;
        return requirementRepository.searchUserRequirements(user, status, cleanQuery)
                .stream()
                .map(RequirementSummaryDto::fromEntity)
                .collect(Collectors.toList());
    }

    public List<RequirementSummaryDto> getAllRequirements(String query, String statusStr) {
        RequirementStatus status = parseStatus(statusStr);
        String cleanQuery = (query != null && !query.trim().isEmpty()) ? query.trim() : null;
        return requirementRepository.searchAllRequirements(status, cleanQuery)
                .stream()
                .map(RequirementSummaryDto::fromEntity)
                .collect(Collectors.toList());
    }

    public Requirement getRequirementById(Long id, User actor) {
        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Requirement not found with id: " + id));

        // Ownership or RBAC validation
        if (actor.getRole() == Role.USER && !req.getUser().getId().equals(actor.getId())) {
            throw new RuntimeException("Access denied: You do not own this requirement.");
        }
        return req;
    }

    public List<Requirement> getApprovedRequirements() {
        return requirementRepository.findByStatus(RequirementStatus.APPROVED);
    }

    @Transactional
    public Requirement createRequirement(Requirement req, User actor) {
        if (req.getTitle() == null || req.getTitle().trim().isEmpty()) {
            throw new RuntimeException("Requirement title is required.");
        }
        if (req.getProblemStatement() == null || req.getProblemStatement().trim().isEmpty()) {
            throw new RuntimeException("Problem statement is required.");
        }

        req.setUser(actor);
        req.setStatus(RequirementStatus.DRAFT);
        Requirement saved = requirementRepository.save(req);

        auditLogService.log(actor.getEmail(), "CREATE_REQUIREMENT",
                "Created requirement ID #" + saved.getId() + ": " + saved.getTitle());
        return saved;
    }

    @Transactional
    public Requirement updateRequirement(Long id, Requirement updateData, User actor) {
        Requirement req = getRequirementById(id, actor);

        // USER role can only update if requirement is still in DRAFT status
        if (actor.getRole() == Role.USER && req.getStatus() != RequirementStatus.DRAFT) {
            throw new RuntimeException("Cannot edit requirement after submission.");
        }

        if (updateData.getTitle() != null && !updateData.getTitle().trim().isEmpty()) {
            req.setTitle(updateData.getTitle().trim());
        }
        if (updateData.getProblemStatement() != null && !updateData.getProblemStatement().trim().isEmpty()) {
            req.setProblemStatement(updateData.getProblemStatement().trim());
        }
        if (updateData.getDescription() != null) {
            req.setDescription(updateData.getDescription());
        }
        if (updateData.getBudget() != null) {
            req.setBudget(updateData.getBudget());
        }
        if (updateData.getTechnologyStack() != null) {
            req.setTechnologyStack(updateData.getTechnologyStack());
        }
        if (updateData.getImageUrl() != null) {
            req.setImageUrl(updateData.getImageUrl());
        }
        if (updateData.getAudioUrl() != null) {
            req.setAudioUrl(updateData.getAudioUrl());
        }

        Requirement saved = requirementRepository.save(req);
        auditLogService.log(actor.getEmail(), "UPDATE_REQUIREMENT",
                "Updated requirement ID #" + saved.getId());
        return saved;
    }

    @Transactional
    public Requirement submitRequirement(Long id, User actor) {
        Requirement req = getRequirementById(id, actor);

        if (req.getStatus() != RequirementStatus.DRAFT) {
            throw new RuntimeException("Only requirements in DRAFT status can be submitted.");
        }

        req.setStatus(RequirementStatus.SUBMITTED);
        Requirement saved = requirementRepository.save(req);

        auditLogService.log(actor.getEmail(), "SUBMIT_REQUIREMENT",
                "Submitted requirement ID #" + saved.getId() + " for admin review.");
        return saved;
    }

    @Transactional
    public Requirement approveRequirement(Long id, User actor) {
        if (actor.getRole() == Role.USER) {
            throw new RuntimeException("Access denied: Regular users cannot approve requirements.");
        }

        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Requirement not found."));

        if (req.getStatus() != RequirementStatus.SUBMITTED) {
            throw new RuntimeException("Only SUBMITTED requirements can be approved.");
        }

        req.setStatus(RequirementStatus.APPROVED);
        Requirement saved = requirementRepository.save(req);

        // Auto-create an UNASSIGNED project in `projects` table fetching data directly from the requirement!
        projectService.createProjectFromRequirement(saved, actor.getEmail());

        auditLogService.log(actor.getEmail(), "APPROVE_REQUIREMENT",
                "Approved requirement ID #" + saved.getId());
        return saved;
    }

    @Transactional
    public Requirement rejectRequirement(Long id, User actor) {
        if (actor.getRole() == Role.USER) {
            throw new RuntimeException("Access denied: Regular users cannot reject requirements.");
        }

        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Requirement not found."));

        if (req.getStatus() != RequirementStatus.SUBMITTED) {
            throw new RuntimeException("Only SUBMITTED requirements can be rejected.");
        }

        req.setStatus(RequirementStatus.REJECTED);
        Requirement saved = requirementRepository.save(req);

        auditLogService.log(actor.getEmail(), "REJECT_REQUIREMENT",
                "Rejected requirement ID #" + saved.getId());
        return saved;
    }

    public Map<String, Object> getUserStats(User user) {
        Map<String, Object> stats = new HashMap<>();
        long total = requirementRepository.countByUser(user);
        long pending = requirementRepository.countByUserAndStatus(user, RequirementStatus.SUBMITTED);
        long approved = requirementRepository.countByUserAndStatus(user, RequirementStatus.APPROVED);

        stats.put("myRequirements", total);
        stats.put("pendingSubmissions", pending);
        stats.put("approvedRequirements", approved);
        return stats;
    }

    @Autowired
    private org.springframework.jdbc.core.JdbcTemplate jdbcTemplate;

    @Transactional
    public void deleteRequirement(Long id, String actorEmail) {
        Requirement req = requirementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Requirement not found with id: " + id));
        jdbcTemplate.update("UPDATE projects SET linked_requirement_id = NULL WHERE linked_requirement_id = ?", id);
        requirementRepository.delete(req);
        auditLogService.log(actorEmail, "DELETE_REQUIREMENT", "Deleted requirement #" + id + ": " + req.getTitle());
    }

    @Transactional
    public void deleteAllRequirements(String actorEmail) {
        jdbcTemplate.execute("UPDATE projects SET linked_requirement_id = NULL");
        requirementRepository.deleteAll();
        auditLogService.log(actorEmail, "DELETE_ALL_REQUIREMENTS", "Super Admin deleted all requirements.");
    }

    public Requirement getRequirementEntityById(Long id) {
        return requirementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Requirement not found with id: " + id));
    }

    @Transactional
    public Requirement save(Requirement requirement) {
        return requirementRepository.save(requirement);
    }

    private RequirementStatus parseStatus(String statusStr) {
        if (statusStr != null && !statusStr.trim().isEmpty()) {
            try {
                return RequirementStatus.valueOf(statusStr.trim().toUpperCase());
            } catch (IllegalArgumentException e) {
                return null;
            }
        }
        return null;
    }
}
