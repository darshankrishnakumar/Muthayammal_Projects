package com.academic.service;

import com.academic.dto.ProjectCreateRequest;
import com.academic.dto.ProjectUpdateRequest;
import com.academic.model.Project;
import com.academic.model.ProjectStatus;
import com.academic.model.Requirement;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@SuppressWarnings("null")
public class ProjectService {

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @Autowired
    private AuditLogService auditLogService;

    @Transactional
    public Project createProject(ProjectCreateRequest dto, String actorEmail) {
        String projectName = dto.getProjectName();
        String description = dto.getDescription();
        Double budget = dto.getBudget();
        String techStack = dto.getTechnologyStack();
        Long linkedReqId = dto.getLinkedRequirementId();

        // Integrate with real database Requirement if linkedRequirementId is provided and fields are incomplete
        if (linkedReqId != null) {
            Optional<Requirement> reqOpt = requirementRepository.findById(linkedReqId);
            if (reqOpt.isPresent()) {
                Requirement req = reqOpt.get();
                if (projectName == null || projectName.isBlank()) {
                    projectName = req.getTitle();
                }
                if (description == null || description.isBlank()) {
                    description = req.getProblemStatement();
                }
                if (budget == null && req.getBudget() != null) {
                    budget = req.getBudget().doubleValue();
                }
                if (techStack == null || techStack.isBlank()) {
                    techStack = req.getTechnologyStack();
                }
            }
        }

        if (projectName == null || projectName.isBlank()) {
            throw new IllegalArgumentException("Project name is required.");
        }

        String projectCode = generateUniqueProjectCode();
        ProjectStatus initialStatus = (dto.getStatus() != null) ? dto.getStatus() : ProjectStatus.CREATED;

        Project project = new Project(
                projectName,
                projectCode,
                description,
                budget != null ? java.math.BigDecimal.valueOf(budget) : null,
                techStack,
                initialStatus,
                linkedReqId,
                actorEmail
        );

        Project savedProject = projectRepository.save(project);

        auditLogService.log(
                actorEmail,
                "CREATE_PROJECT",
                String.format("Created project %s (%s) with status %s", savedProject.getProjectCode(), savedProject.getProjectName(), savedProject.getStatus())
        );

        return savedProject;
    }

    @Transactional
    public Project createProjectFromRequirement(com.academic.model.Requirement req, String actorEmail) {
        Optional<Project> existing = projectRepository.findByLinkedRequirementId(req.getId());
        if (existing.isPresent()) {
            return existing.get();
        }

        String projectCode = generateUniqueProjectCode();
        Project project = new Project(
                req.getTitle(),
                projectCode,
                req.getProblemStatement(),
                req.getBudget(),
                req.getTechnologyStack(),
                ProjectStatus.CREATED,
                req.getId(),
                actorEmail
        );
        project.setAdvanceAmount(req.getAdvanceAmount());
        project.setRemainingAmount(req.getRemainingAmount());
        project.setAdvancePaymentStatus(req.getAdvancePaymentStatus());

        Project saved = projectRepository.save(project);
        auditLogService.log(
                actorEmail,
                "CREATE_PROJECT_FROM_REQUIREMENT",
                String.format("Auto-created unassigned project %s (%s) from Requirement #%d", saved.getProjectCode(), saved.getProjectName(), req.getId())
        );
        return saved;
    }

    public List<Project> getProjectsByDeveloperId(Long devId) {
        return projectRepository.findByDeveloperId(devId);
    }

    public List<Project> getProjectsByReviewerAdminId(Long reviewerId) {
        return projectRepository.findByReviewerAdminId(reviewerId);
    }

    public List<Project> getMarketplaceProjects() {
        return projectRepository.findByIsMarketplaceTrue();
    }

    public List<Project> getAllProjectsList() {
        return projectRepository.findAll();
    }

    @Transactional
    public Project save(Project project) {
        return projectRepository.save(project);
    }

    @Transactional
    public Project updateProject(Long id, ProjectUpdateRequest dto, String actorEmail) {
        Project project = getProjectById(id);

        if (dto.getProjectName() != null && !dto.getProjectName().isBlank()) {
            project.setProjectName(dto.getProjectName());
        }
        if (dto.getDescription() != null) {
            project.setDescription(dto.getDescription());
        }
        if (dto.getBudget() != null) {
            project.setBudget(java.math.BigDecimal.valueOf(dto.getBudget()));
        }
        if (dto.getTechnologyStack() != null) {
            project.setTechnologyStack(dto.getTechnologyStack());
        }
        if (dto.getLinkedRequirementId() != null) {
            project.setLinkedRequirementId(dto.getLinkedRequirementId());
        }

        project.setUpdatedBy(actorEmail);
        Project updatedProject = projectRepository.save(project);

        auditLogService.log(
                actorEmail,
                "UPDATE_PROJECT",
                String.format("Updated details for project %s (%s)", updatedProject.getProjectCode(), updatedProject.getProjectName())
        );

        return updatedProject;
    }

    @Transactional
    public Project changeStatus(Long id, ProjectStatus newStatus, String actorEmail) {
        if (newStatus == null) {
            throw new IllegalArgumentException("Target status cannot be null.");
        }

        Project project = getProjectById(id);
        ProjectStatus currentStatus = project.getStatus();

        if (!currentStatus.isValidTransition(newStatus)) {
            throw new IllegalStateException(String.format(
                    "Invalid status transition: Cannot transition project %s from %s to %s.",
                    project.getProjectCode(), currentStatus, newStatus
            ));
        }

        project.setStatus(newStatus);
        project.setUpdatedBy(actorEmail);
        Project updatedProject = projectRepository.save(project);

        auditLogService.log(
                actorEmail,
                "CHANGE_PROJECT_STATUS",
                String.format("Changed status of project %s (%s) from %s to %s",
                        updatedProject.getProjectCode(), updatedProject.getProjectName(), currentStatus, newStatus)
        );

        return updatedProject;
    }

    public Project getProjectById(Long id) {
        return projectRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + id));
    }

    public Optional<Project> getProjectByLinkedRequirementId(Long reqId) {
        return projectRepository.findByLinkedRequirementId(reqId);
    }

    public List<Project> searchProjects(String search, ProjectStatus status, String techStack, 
                                       LocalDateTime startDate, LocalDateTime endDate, Long assignedUserId) {
        if (assignedUserId != null) {
            return projectRepository.searchAssignedProjects(assignedUserId, (search != null && !search.isBlank()) ? search.trim() : null, status);
        }
        return projectRepository.searchProjects(
                (search != null && !search.isBlank()) ? search.trim() : null,
                status,
                (techStack != null && !techStack.isBlank()) ? techStack.trim() : null,
                startDate,
                endDate,
                null
        );
    }

    public List<Project> getAssignedProjectsForUser(Long userId) {
        return projectRepository.searchAssignedProjects(userId, null, null);
    }

    public Map<String, Object> getDashboardSummary(com.academic.model.User actor) {
        Map<String, Object> dashboard = new HashMap<>();
        
        Long filterUserId = (actor != null && actor.getRole() == com.academic.model.Role.USER) ? actor.getId() : null;
        List<Project> userProjects = searchProjects(null, null, null, null, null, filterUserId);

        long totalProjects = userProjects.size();
        long draftCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.DRAFT).count();
        long approvedCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.APPROVED).count();
        long inProgressCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.IN_PROGRESS).count();
        long completedCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.COMPLETED).count();
        long rejectedCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.REJECTED).count();
        long inactiveCount = userProjects.stream().filter(p -> p.getStatus() == ProjectStatus.INACTIVE).count();

        Map<String, Long> statusCounts = new HashMap<>();
        statusCounts.put("TOTAL", totalProjects);
        statusCounts.put("DRAFT", draftCount);
        statusCounts.put("APPROVED", approvedCount);
        statusCounts.put("IN_PROGRESS", inProgressCount);
        statusCounts.put("COMPLETED", completedCount);
        statusCounts.put("REJECTED", rejectedCount);
        statusCounts.put("INACTIVE", inactiveCount);

        List<Project> recentProjects = userProjects.size() > 5 ? userProjects.subList(0, 5) : userProjects;

        dashboard.put("statusCounts", statusCounts);
        dashboard.put("recentProjects", recentProjects);
        return dashboard;
    }

    @Autowired
    private org.springframework.jdbc.core.JdbcTemplate jdbcTemplate;

    @Transactional
    public void deleteProject(Long id, String actorEmail) {
        Project project = getProjectById(id);
        Integer paid = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM order_management WHERE project_id = ? AND payment_status = 'COMPLETED'", Integer.class, id);
        Integer entitled = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM project_entitlements WHERE project_id = ?", Integer.class, id);
        if ((paid != null && paid > 0) || (entitled != null && entitled > 0)) {
            throw new IllegalStateException("Project " + project.getProjectCode()
                    + " has orders or granted access and cannot be deleted. Archive it instead.");
        }
        String folders = "SELECT id FROM folder_master WHERE project_id = ?";
        jdbcTemplate.update("DELETE FROM file_permissions WHERE asset_id IN (SELECT id FROM asset_master WHERE folder_id IN (" + folders + "))", id);
        jdbcTemplate.update("DELETE FROM asset_master WHERE folder_id IN (" + folders + ")", id);
        jdbcTemplate.update("DELETE FROM folder_permissions WHERE folder_id IN (" + folders + ")", id);
        jdbcTemplate.update("DELETE FROM folder_master WHERE project_id = ?", id);
        jdbcTemplate.update("DELETE FROM project_assignments WHERE project_id = ?", id);
        jdbcTemplate.update("DELETE FROM college_project_allocations WHERE project_id = ?", id);
        projectRepository.delete(project);
        auditLogService.log(actorEmail, "DELETE_PROJECT", "Deleted project " + project.getProjectCode());
    }

    private String generateUniqueProjectCode() {
        String code;
        int attempts = 0;
        do {
            String randomPart = UUID.randomUUID().toString().substring(0, 6).toUpperCase();
            code = "PRJ-" + randomPart;
            attempts++;
            if (attempts > 50) {
                code = "PRJ-" + System.currentTimeMillis();
                break;
            }
        } while (projectRepository.existsByProjectCode(code));
        return code;
    }
}
