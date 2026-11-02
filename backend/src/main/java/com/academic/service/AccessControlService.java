package com.academic.service;

import com.academic.model.Asset;
import com.academic.model.Folder;
import com.academic.model.Project;
import com.academic.model.ProjectStatus;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.repository.ProjectRepository;
import com.academic.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;

@Service
@SuppressWarnings("null")
public class AccessControlService {

    private static final Logger logger = LoggerFactory.getLogger(AccessControlService.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private com.academic.repository.ProjectAssignmentRepository projectAssignmentRepository;

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

    /**
     * Validates that the current user has clearance to access a specific Project.
     * Hierarchy:
     * 1. SUPER_ADMIN / ADMIN -> Full clearance
     * 2. USER -> Must have an active entry in PROJECT_ASSIGNMENT
     */
    public void validateProjectAccess(Long projectId) {
        User user = getCurrentAuthenticatedUser();

        if (user.isDeleted() || user.getStatus() != com.academic.model.UserStatus.ACTIVE) {
            throw new AccessDeniedException("User account is deactivated.");
        }

        // Verify project exists
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));

        // Hierarchy Enforcement:
        // 1. SUPER_ADMIN -> Unrestricted global access
        if (user.getRole() == Role.SUPER_ADMIN) {
            logger.debug("Project access granted to SUPER_ADMIN {}", user.getEmail());
            return;
        }

        // 2. PROJECT_DEVELOPER -> Access restricted strictly to assigned projects
        if (user.getRole() == Role.PROJECT_DEVELOPER) {
            boolean isDevAssigned = (project.getDeveloper() != null && project.getDeveloper().getId().equals(user.getId()))
                    || projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent();
            if (!isDevAssigned) {
                throw new AccessDeniedException(String.format("Access Denied: Project %s is not assigned to you.", project.getProjectCode()));
            }
            return;
        }

        // 3. ADMIN -> Reviewer assignment check or project assignment
        if (user.getRole() == Role.ADMIN) {
            boolean isReviewer = (project.getReviewerAdmin() != null && project.getReviewerAdmin().getId().equals(user.getId()));
            boolean hasAssignment = projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent();
            if (!isReviewer && !hasAssignment) {
                throw new AccessDeniedException(String.format("Access Denied: You are not assigned to project %s (%s).", project.getProjectCode(), project.getProjectName()));
            }
            return;
        }

        // 4. USER -> Must be assigned AND must fulfill payment and approval access requirements
        boolean hasAssignment = projectAssignmentRepository.findActiveAssignment(projectId, user.getId()).isPresent()
                || (project.getPurchasedByUserId() != null && project.getPurchasedByUserId().equals(user.getId()));

        if (!hasAssignment) {
            throw new AccessDeniedException(String.format("Access Denied: You are not assigned to project %s.", project.getProjectCode()));
        }

        // Check Marketplace vs Custom Requirement Payment Gating
        if (project.isMarketplace()) {
            // For Marketplace items, access is granted if purchased
            if (project.getPurchasedByUserId() == null || !project.getPurchasedByUserId().equals(user.getId())) {
                throw new AccessDeniedException("Access Denied: This marketplace project has not been purchased by your account.");
            }
        } else if (project.getLinkedRequirementId() != null) {
            // For Custom Requirement projects with payment lifecycle, access is granted ONLY when:
            // Advance = COMPLETED && Review = APPROVED / ACCESS_GRANTED && Remaining = COMPLETED
            boolean isAdvancePaid = "COMPLETED".equalsIgnoreCase(project.getAdvancePaymentStatus());
            boolean isRemainingPaid = "COMPLETED".equalsIgnoreCase(project.getRemainingPaymentStatus());
            boolean isAccessGranted = project.getStatus() == ProjectStatus.ACCESS_GRANTED 
                    || project.getStatus() == ProjectStatus.COMPLETED
                    || project.getLifecycleStatus() == ProjectStatus.ACCESS_GRANTED
                    || project.getLifecycleStatus() == ProjectStatus.COMPLETED;

            if (!isAdvancePaid || !isRemainingPaid || !isAccessGranted) {
                throw new AccessDeniedException(String.format("Access Denied: Protected deliverables for project %s are locked. Please complete the remaining payment to unlock access.", project.getProjectCode()));
            }
        }

        logger.debug("Project access granted to user {} ({}) for project {}", user.getEmail(), user.getRole(), project.getProjectCode());
    }

    @Autowired
    private com.academic.repository.FolderPermissionRepository folderPermissionRepository;

    @Autowired
    private com.academic.repository.FilePermissionRepository filePermissionRepository;

    /**
     * Evaluates effective permission for a folder for the current user.
     * Precedence: User-specific permission -> Role-specific permission -> Default ALLOWED.
     */
    public boolean isFolderAllowed(Folder folder, User user) {
        if (user.getRole() == Role.SUPER_ADMIN) {
            return true;
        }

        // Check User-specific permission
        var userPerm = folderPermissionRepository.findByFolderIdAndUserId(folder.getId(), user.getId());
        if (userPerm.isPresent()) {
            return userPerm.get().getPermissionStatus() == com.academic.model.PermissionStatus.ALLOWED;
        }

        // Check Role-specific permission
        var rolePerm = folderPermissionRepository.findByFolderIdAndRole(folder.getId(), user.getRole());
        if (rolePerm.isPresent()) {
            return rolePerm.get().getPermissionStatus() == com.academic.model.PermissionStatus.ALLOWED;
        }

        // Default ALLOWED
        return true;
    }

    /**
     * Evaluates effective permission for an asset for the current user.
     * Folder -> File Inheritance: Folder DENIED -> File DENIED.
     * Precedence: User-specific -> Role-specific -> Default ALLOWED.
     */
    public boolean isAssetAllowed(Asset asset, User user) {
        if (user.getRole() == Role.SUPER_ADMIN) {
            return true;
        }

        // 1. Folder Inheritance: Check Folder permission first
        if (!isFolderAllowed(asset.getFolder(), user)) {
            return false;
        }

        // 2. Check User-specific file permission
        var userPerm = filePermissionRepository.findByAssetIdAndUserId(asset.getId(), user.getId());
        if (userPerm.isPresent()) {
            return userPerm.get().getPermissionStatus() == com.academic.model.PermissionStatus.ALLOWED;
        }

        // 3. Check Role-specific file permission
        var rolePerm = filePermissionRepository.findByAssetIdAndRole(asset.getId(), user.getRole());
        if (rolePerm.isPresent()) {
            return rolePerm.get().getPermissionStatus() == com.academic.model.PermissionStatus.ALLOWED;
        }

        // Default ALLOWED
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
     * Validates the complete 4-tier chain for viewing/accessing an Asset:
     * 1. Authenticate user
     * 2. Check Project Clearance
     * 3. Check Folder Permission
     * 4. Check File Permission
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
        validateProjectAccess(asset.getFolder().getProject().getId());

        if (!isAssetAllowed(asset, user)) {
            throw new AccessDeniedException("Access Denied: You do not have clearance for file " + asset.getOriginalFileName());
        }
    }

    /**
     * Validates management permissions (creating/modifying folders or files).
     * SUPER_ADMIN and ADMIN have write clearance. Regular USER has read-only access.
     */
    public void validateWriteClearance(Long projectId) {
        User user = getCurrentAuthenticatedUser();
        if (user.getRole() == Role.USER) {
            throw new AccessDeniedException("Access Denied: Regular users have read-only view access and cannot create, modify, or delete folders/files.");
        }
        validateProjectAccess(projectId);
    }
}
