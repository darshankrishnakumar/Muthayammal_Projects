package com.academic.service;

import com.academic.model.*;
import com.academic.repository.CollegeProjectAllocationRepository;
import com.academic.repository.FilePermissionRepository;
import com.academic.repository.FolderPermissionRepository;
import com.academic.repository.ProjectAssignmentRepository;
import com.academic.repository.ProjectEntitlementRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;
import java.util.Objects;

/**
 * Central, deny-by-default authorization for projects, folders, files and college data.
 *
 * Every project resolves to one of three access levels for the current user:
 * <ul>
 *   <li>{@code NONE}    – the project is invisible.</li>
 *   <li>{@code PREVIEW} – metadata and files marked previewable (screenshots, demo video).</li>
 *   <li>{@code FULL}    – every deliverable, subject to folder/file permission rules.</li>
 * </ul>
 * College isolation: ADMIN and USER accounts only ever see projects allocated to, or
 * requested from, their own college.
 */
@Service
@SuppressWarnings("null")
public class AccessControlService {

    private static final Logger logger = LoggerFactory.getLogger(AccessControlService.class);

    public enum ProjectAccessLevel { NONE, PREVIEW, FULL }

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private ProjectAssignmentRepository projectAssignmentRepository;

    @Autowired
    private FolderPermissionRepository folderPermissionRepository;

    @Autowired
    private FilePermissionRepository filePermissionRepository;

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private ProjectEntitlementRepository entitlementRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    /**
     * Retrieves the currently authenticated User entity from the SecurityContext.
     */
    public User getCurrentAuthenticatedUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new AccessDeniedException("Unauthenticated: No active security session found.");
        }

        String email = auth.getName();
        return userRepository.findByEmailAndDeletedFalse(email)
                .orElseThrow(() -> new AccessDeniedException("Authenticated user not found or deactivated: " + email));
    }

    // ------------------------------------------------------------------
    // Project access levels
    // ------------------------------------------------------------------

    public ProjectAccessLevel getAccessLevel(Project project, User user) {
        if (project == null || user == null || user.isDeleted() || user.getStatus() != UserStatus.ACTIVE) {
            return ProjectAccessLevel.NONE;
        }
        Long projectId = project.getId();

        switch (user.getRole()) {
            case SUPER_ADMIN:
                return ProjectAccessLevel.FULL;

            case PROJECT_DEVELOPER: {
                boolean assigned = isDeveloperOf(project, user)
                        || projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent();
                return assigned ? ProjectAccessLevel.FULL : ProjectAccessLevel.NONE;
            }

            case ADMIN: {
                if (project.getReviewerAdmin() != null && Objects.equals(project.getReviewerAdmin().getId(), user.getId())) {
                    return ProjectAccessLevel.FULL;
                }
                if (projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent()) {
                    return ProjectAccessLevel.PREVIEW;
                }
                Long collegeId = collegeIdOf(user);
                if (collegeId == null) {
                    return ProjectAccessLevel.NONE;
                }
                if (project.isLibrary()) {
                    return allocationRepository.findActive(collegeId, projectId).isPresent()
                            ? ProjectAccessLevel.PREVIEW : ProjectAccessLevel.NONE;
                }
                return Objects.equals(requirementCollegeId(project), collegeId)
                        ? ProjectAccessLevel.PREVIEW : ProjectAccessLevel.NONE;
            }

            case USER:
            default: {
                if (entitlementRepository.hasActive(user.getId(), projectId)
                        || projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent()) {
                    return ProjectAccessLevel.FULL;
                }
                if (project.isLibrary()) {
                    Long collegeId = collegeIdOf(user);
                    boolean visible = collegeId != null
                            && project.getCatalogStatus() == CatalogStatus.PUBLISHED
                            && allocationRepository.findActive(collegeId, projectId).isPresent();
                    return visible ? ProjectAccessLevel.PREVIEW : ProjectAccessLevel.NONE;
                }
                return isRequesterOf(project, user) ? ProjectAccessLevel.PREVIEW : ProjectAccessLevel.NONE;
            }
        }
    }

    public ProjectAccessLevel getAccessLevel(Long projectId, User user) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));
        return getAccessLevel(project, user);
    }

    /**
     * Validates that the current user may at least see the project (PREVIEW or FULL).
     */
    public void validateProjectAccess(Long projectId) {
        User user = getCurrentAuthenticatedUser();
        assertActive(user);

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));

        if (getAccessLevel(project, user) == ProjectAccessLevel.NONE) {
            throw new AccessDeniedException(String.format("Access Denied: You are not assigned to project %s.", project.getProjectCode()));
        }
        logger.debug("Project access granted to {} ({}) for project {}", user.getEmail(), user.getRole(), project.getProjectCode());
    }

    /**
     * Validates that the current user holds full access to the project's deliverables.
     */
    public void validateFullProjectAccess(Long projectId) {
        User user = getCurrentAuthenticatedUser();
        assertActive(user);
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));
        ProjectAccessLevel level = getAccessLevel(project, user);
        if (level == ProjectAccessLevel.NONE) {
            throw new AccessDeniedException(String.format("Access Denied: You are not assigned to project %s.", project.getProjectCode()));
        }
        if (level != ProjectAccessLevel.FULL) {
            throw new AccessDeniedException("Access Denied: Deliverables for " + project.getProjectCode() + " unlock after purchase or final payment.");
        }
    }

    // ------------------------------------------------------------------
    // Folder and file permissions
    // ------------------------------------------------------------------

    /**
     * Evaluates effective permission for a folder for the current user.
     * Precedence: User-specific permission -> Role-specific permission -> Default ALLOWED.
     */
    public boolean isFolderAllowed(Folder folder, User user) {
        if (user.getRole() == Role.SUPER_ADMIN) {
            return true;
        }

        var userPerm = folderPermissionRepository.findByFolderIdAndUserId(folder.getId(), user.getId());
        if (userPerm.isPresent()) {
            return userPerm.get().getPermissionStatus() == PermissionStatus.ALLOWED;
        }

        var rolePerm = folderPermissionRepository.findByFolderIdAndRole(folder.getId(), user.getRole());
        if (rolePerm.isPresent()) {
            return rolePerm.get().getPermissionStatus() == PermissionStatus.ALLOWED;
        }

        return true;
    }

    public boolean isAssetAllowed(Asset asset, User user) {
        if (user.getRole() == Role.SUPER_ADMIN) {
            return true;
        }
        Project project = asset.getFolder() != null ? asset.getFolder().getProject() : null;
        return isAssetAllowed(asset, user, getAccessLevel(project, user));
    }

    /**
     * Evaluates effective permission for an asset given an already-resolved project level.
     * PREVIEW only exposes previewable assets. Folder DENIED -> File DENIED.
     * Precedence: User-specific -> Role-specific -> Default ALLOWED.
     */
    public boolean isAssetAllowed(Asset asset, User user, ProjectAccessLevel level) {
        if (user.getRole() == Role.SUPER_ADMIN) {
            return true;
        }
        if (level == ProjectAccessLevel.NONE) {
            return false;
        }
        if (level == ProjectAccessLevel.PREVIEW && !asset.isPreviewable()) {
            return false;
        }

        if (!isFolderAllowed(asset.getFolder(), user)) {
            return false;
        }

        var userPerm = filePermissionRepository.findByAssetIdAndUserId(asset.getId(), user.getId());
        if (userPerm.isPresent()) {
            return userPerm.get().getPermissionStatus() == PermissionStatus.ALLOWED;
        }

        var rolePerm = filePermissionRepository.findByAssetIdAndRole(asset.getId(), user.getRole());
        if (rolePerm.isPresent()) {
            return rolePerm.get().getPermissionStatus() == PermissionStatus.ALLOWED;
        }

        return true;
    }

    /**
     * Validates that the current user has clearance for the project owning the folder.
     */
    public void validateFolderAccess(Folder folder) {
        if (folder == null || folder.getProject() == null) {
            throw new NoSuchElementException("Folder or associated project not found.");
        }
        if (!folder.isActive()) {
            throw new NoSuchElementException("Folder is inactive or has been deleted.");
        }
        validateProjectAccess(folder.getProject().getId());

        User user = getCurrentAuthenticatedUser();
        if (!isFolderAllowed(folder, user)) {
            throw new AccessDeniedException("Access Denied: You do not have clearance for folder " + folder.getName());
        }
    }

    /**
     * Validates the complete chain for viewing an Asset:
     * authenticated -> project visible -> full access or previewable -> folder -> file permission.
     */
    public void validateAssetAccess(Asset asset) {
        if (asset == null) {
            throw new NoSuchElementException("Asset record not found.");
        }
        if (!asset.isActive()) {
            throw new NoSuchElementException("Asset is deactivated or deleted.");
        }
        if (asset.getFolder() == null) {
            throw new NoSuchElementException("Asset folder association is missing.");
        }

        User user = getCurrentAuthenticatedUser();
        assertActive(user);
        Project project = asset.getFolder().getProject();
        validateProjectAccess(project.getId());

        ProjectAccessLevel level = getAccessLevel(project, user);
        if (!isAssetAllowed(asset, user, level)) {
            if (level == ProjectAccessLevel.PREVIEW && !asset.isPreviewable()) {
                throw new AccessDeniedException("Access Denied: This file unlocks after purchase or final payment.");
            }
            throw new AccessDeniedException("Access Denied: You do not have clearance for file " + asset.getOriginalFileName());
        }
    }

    /**
     * Validates management permissions (creating/modifying folders or files).
     * SUPER_ADMIN manages every project; a PROJECT_DEVELOPER manages only custom projects
     * assigned to them. College admins and students are read-only.
     */
    public void validateWriteClearance(Long projectId) {
        User user = getCurrentAuthenticatedUser();
        assertActive(user);
        if (user.getRole() == Role.USER) {
            throw new AccessDeniedException("Access Denied: Regular users have read-only view access and cannot create, modify, or delete folders/files.");
        }
        if (user.getRole() == Role.ADMIN) {
            throw new AccessDeniedException("Access Denied: College administrators have read-only access to project files.");
        }
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));
        if (user.getRole() == Role.PROJECT_DEVELOPER) {
            if (project.isLibrary() || !isDeveloperOf(project, user)) {
                throw new AccessDeniedException(String.format("Access Denied: Project %s is not assigned to you.", project.getProjectCode()));
            }
        }
    }

    // ------------------------------------------------------------------
    // College isolation helpers
    // ------------------------------------------------------------------

    public College requireCollege(User user) {
        if (user.getCollege() == null) {
            throw new IllegalStateException("Your account is not linked to a college. Contact the platform administrator.");
        }
        if (!user.getCollege().isActive()) {
            throw new AccessDeniedException("Your college account is currently inactive.");
        }
        return user.getCollege();
    }

    public boolean sameCollege(User a, User b) {
        Long ca = collegeIdOf(a);
        Long cb = collegeIdOf(b);
        return ca != null && ca.equals(cb);
    }

    /**
     * SUPER_ADMIN manages anyone except other super admins' credentials elsewhere;
     * an ADMIN manages only USER (student) accounts of their own college.
     */
    public void assertCanManageUser(User actor, User target) {
        if (actor.getRole() == Role.SUPER_ADMIN) {
            return;
        }
        if (actor.getRole() == Role.ADMIN && target.getRole() == Role.USER && sameCollege(actor, target)) {
            return;
        }
        throw new AccessDeniedException("Access denied: you cannot manage this account.");
    }

    /** Whether the actor may see a requirement (owner, own-college admin, super admin, assigned developer). */
    public boolean canViewRequirement(User actor, Requirement req) {
        switch (actor.getRole()) {
            case SUPER_ADMIN:
                return true;
            case ADMIN:
                return req.getCollege() != null && Objects.equals(req.getCollege().getId(), collegeIdOf(actor));
            case PROJECT_DEVELOPER:
                return projectRepository.findByLinkedRequirementId(req.getId())
                        .map(p -> isDeveloperOf(p, actor))
                        .orElse(false);
            case USER:
            default:
                return req.getUser() != null && Objects.equals(req.getUser().getId(), actor.getId());
        }
    }

    public boolean isDeveloperOf(Project project, User user) {
        return project.getDeveloper() != null && Objects.equals(project.getDeveloper().getId(), user.getId());
    }

    public boolean isRequesterOf(Project project, User user) {
        if (project.getLinkedRequirementId() == null) {
            return false;
        }
        return requirementRepository.findById(project.getLinkedRequirementId())
                .map(r -> r.getUser() != null && Objects.equals(r.getUser().getId(), user.getId()))
                .orElse(false);
    }

    private Long requirementCollegeId(Project project) {
        if (project.getLinkedRequirementId() == null) {
            return null;
        }
        return requirementRepository.findById(project.getLinkedRequirementId())
                .map(r -> r.getCollege() != null ? r.getCollege().getId() : null)
                .orElse(null);
    }

    private static Long collegeIdOf(User user) {
        return user != null && user.getCollege() != null ? user.getCollege().getId() : null;
    }

    private static void assertActive(User user) {
        if (user.isDeleted() || user.getStatus() != UserStatus.ACTIVE) {
            throw new AccessDeniedException("User account is deactivated.");
        }
    }
}
