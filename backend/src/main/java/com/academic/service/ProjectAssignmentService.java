package com.academic.service;

import com.academic.model.Project;
import com.academic.model.ProjectAssignment;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.ProjectAssignmentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;

@Service
@SuppressWarnings("null")
public class ProjectAssignmentService {

    @Autowired
    private ProjectAssignmentRepository projectAssignmentRepository;

    @Autowired
    private ProjectService projectService;

    @Autowired
    private UserService userService;

    @Autowired
    private AuditLogService auditLogService;

    @Transactional
    public ProjectAssignment assignUserToProject(Long projectId, Long userId, LocalDateTime expiredAt, String notes, String actorEmail) {
        Project project = projectService.getProjectById(projectId);
        User actor = userService.findByEmail(actorEmail)
                .orElseThrow(() -> new AccessDeniedException("Authenticated user context not found."));

        User targetUser = userService.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("User not found with ID: " + userId));

        if (targetUser.isDeleted() || targetUser.getStatus() != UserStatus.ACTIVE) {
            throw new IllegalArgumentException("Cannot assign inactive or deleted user account.");
        }

        // ROLE-BASED WORKFLOW HIERARCHY VALIDATION:
        if (actor.getRole() == Role.ADMIN) {
            // Rule 1: Admin must be explicitly assigned to this project by Super Admin
            boolean isAssignedToAdmin = projectAssignmentRepository.findActiveAssignment(projectId, actor.getId()).isPresent();
            if (!isAssignedToAdmin) {
                throw new AccessDeniedException("Access Denied: You cannot assign users to a project that is not assigned to you by the Super Admin.");
            }

            // Rule 2: Admin can only assign regular USER accounts
            if (targetUser.getRole() != Role.USER) {
                throw new IllegalArgumentException("Admins can only assign projects to regular Users.");
            }
        } else if (actor.getRole() == Role.USER) {
            // Rule 3: Regular users cannot assign projects
            throw new AccessDeniedException("Access Denied: Regular users are unauthorized to assign projects.");
        } else if (actor.getRole() == Role.SUPER_ADMIN) {
            // Super Admin can assign project to ADMIN (to manage) or directly to USER
            if (targetUser.getRole() != Role.ADMIN && targetUser.getRole() != Role.USER) {
                throw new IllegalArgumentException("Super Admin can only assign projects to Admins or Users.");
            }
        }

        // Check if an existing assignment record exists for this (projectId, userId)
        Optional<ProjectAssignment> existingOpt = projectAssignmentRepository.findByProjectIdAndUserId(projectId, userId);
        if (existingOpt.isPresent()) {
            ProjectAssignment existing = existingOpt.get();
            if (existing.isActive()) {
                throw new IllegalArgumentException("Project already assigned to this user.");
            }
            // Reactivate previous assignment
            existing.setActive(true);
            existing.setAssignedAt(LocalDateTime.now());
            existing.setDeactivatedAt(null);
            existing.setExpiredAt(expiredAt);
            existing.setAssignedBy(actorEmail);
            if (notes != null && !notes.isBlank()) existing.setNotes(notes);

            ProjectAssignment saved = projectAssignmentRepository.save(existing);
            auditLogService.log(
                    actorEmail,
                    "ASSIGN_PROJECT_USER",
                    String.format("Reactivated assignment for %s %s (%s) to project %s (%s)",
                            targetUser.getRole(), targetUser.getFullName(), targetUser.getEmail(), project.getProjectCode(), project.getProjectName())
            );
            return saved;
        }

        ProjectAssignment assignment = new ProjectAssignment(project, targetUser, expiredAt, actorEmail, notes);
        ProjectAssignment savedAssignment = projectAssignmentRepository.save(assignment);

        auditLogService.log(
                actorEmail,
                "ASSIGN_PROJECT_USER",
                String.format("Assigned %s %s (%s) to project %s (%s)",
                        targetUser.getRole(), targetUser.getFullName(), targetUser.getEmail(), project.getProjectCode(), project.getProjectName())
        );

        return savedAssignment;
    }

    public List<ProjectAssignment> getAssignmentsByProject(Long projectId) {
        projectService.getProjectById(projectId);
        return projectAssignmentRepository.findByProjectId(projectId);
    }

    public List<ProjectAssignment> getActiveAssignmentsByProject(Long projectId) {
        projectService.getProjectById(projectId);
        return projectAssignmentRepository.findActiveAssignmentsByProjectId(projectId);
    }

    public List<ProjectAssignment> getAssignmentsByUser(Long userId) {
        return projectAssignmentRepository.findByUserId(userId);
    }

    public List<ProjectAssignment> getActiveAssignmentsByUser(Long userId) {
        return projectAssignmentRepository.findActiveAssignmentsByUserId(userId);
    }

    @Transactional
    public ProjectAssignment updateAssignment(Long projectId, Long assignmentId, LocalDateTime expiredAt, Boolean active, String notes, String actorEmail) {
        ProjectAssignment assignment = projectAssignmentRepository.findByProjectIdAndId(projectId, assignmentId)
                .orElseThrow(() -> new NoSuchElementException("Assignment not found with ID: " + assignmentId + " for project ID: " + projectId));

        if (expiredAt != null) {
            assignment.setExpiredAt(expiredAt);
        }
        if (notes != null) {
            assignment.setNotes(notes);
        }
        if (active != null) {
            assignment.setActive(active);
            if (!active) {
                assignment.setDeactivatedAt(LocalDateTime.now());
            } else {
                assignment.setDeactivatedAt(null);
            }
        }

        ProjectAssignment updated = projectAssignmentRepository.save(assignment);

        auditLogService.log(
                actorEmail,
                "UPDATE_PROJECT_ASSIGNMENT",
                String.format("Updated assignment #%d for user %s on project %s",
                        updated.getId(), updated.getUser().getEmail(), updated.getProject().getProjectCode())
        );

        return updated;
    }

    @Transactional
    public void removeAssignment(Long projectId, Long assignmentId, String actorEmail) {
        ProjectAssignment assignment = projectAssignmentRepository.findByProjectIdAndId(projectId, assignmentId)
                .orElseThrow(() -> new NoSuchElementException("Assignment not found with ID: " + assignmentId + " for project ID: " + projectId));

        assignment.setActive(false);
        assignment.setDeactivatedAt(LocalDateTime.now());
        projectAssignmentRepository.save(assignment);

        auditLogService.log(
                actorEmail,
                "REMOVE_PROJECT_ASSIGNMENT",
                String.format("Revoked assignment #%d for user %s on project %s",
                        assignment.getId(), assignment.getUser().getEmail(), assignment.getProject().getProjectCode())
        );
    }

    @Transactional
    public void deactivateAssignmentByUser(Long projectId, Long userId, String actorEmail) {
        ProjectAssignment assignment = projectAssignmentRepository.findByProjectIdAndUserId(projectId, userId)
                .orElseThrow(() -> new NoSuchElementException("Active assignment not found for user ID: " + userId + " on project ID: " + projectId));

        assignment.setActive(false);
        assignment.setDeactivatedAt(LocalDateTime.now());
        projectAssignmentRepository.save(assignment);

        auditLogService.log(
                actorEmail,
                "REMOVE_PROJECT_ASSIGNMENT",
                String.format("Revoked assignment for user ID %d on project ID %d", userId, projectId)
        );
    }
}
