package com.academic.service;

import com.academic.model.*;
import com.academic.repository.AdminPermissionRepository;
import com.academic.repository.AdminUserAssignmentRepository;
import com.academic.repository.ProjectRepository;
import com.academic.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@SuppressWarnings("null")
public class AdminAccessControlService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AdminPermissionRepository adminPermissionRepository;

    @Autowired
    private AdminUserAssignmentRepository adminUserAssignmentRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private AuditLogService auditLogService;

    /**
     * Checks whether an admin possesses a specific permission.
     */
    public boolean hasPermission(User adminUser, PermissionKey key) {
        if (adminUser == null) return false;
        if (adminUser.getRole() == Role.SUPER_ADMIN) return true;
        if (adminUser.getRole() != Role.ADMIN) return false;

        return adminPermissionRepository.findByAdminUserIdAndPermissionKey(adminUser.getId(), key).isPresent();
    }

    /**
     * Gets the data scope associated with an admin's permission.
     */
    public DataScope getScope(User adminUser, PermissionKey key) {
        if (adminUser == null) return null;
        if (adminUser.getRole() == Role.SUPER_ADMIN) return DataScope.GLOBAL;
        if (adminUser.getRole() != Role.ADMIN) return null;

        return adminPermissionRepository.findByAdminUserIdAndPermissionKey(adminUser.getId(), key)
                .map(AdminPermission::getDataScope)
                .orElse(null);
    }

    /**
     * Verifies if an admin has clearance to view/manage a specific user.
     */
    public boolean canAccessUser(User actor, Long targetUserId) {
        if (actor == null || targetUserId == null) return false;
        if (actor.getRole() == Role.SUPER_ADMIN) return true;
        if (actor.getRole() == Role.USER) {
            return actor.getId().equals(targetUserId);
        }
        if (actor.getRole() != Role.ADMIN) return false;

        DataScope scope = getScope(actor, PermissionKey.USER_VIEW);
        if (scope == null) return false;

        if (scope == DataScope.GLOBAL) return true;

        if (scope == DataScope.ASSIGNED_ONLY || scope == DataScope.USER_ASSIGNED) {
            return adminUserAssignmentRepository.existsByAdminUserIdAndAssignedUserId(actor.getId(), targetUserId);
        }

        return false;
    }

    /**
     * Verifies if an admin has clearance to review a specific project.
     */
    public boolean canReviewProject(User actor, Long projectId) {
        if (actor == null || projectId == null) return false;
        if (actor.getRole() == Role.SUPER_ADMIN) return true;
        if (actor.getRole() != Role.ADMIN) return false;

        DataScope scope = getScope(actor, PermissionKey.PROJECT_REVIEW);
        if (scope == null) return false;

        if (scope == DataScope.GLOBAL) return true;

        Project project = projectRepository.findById(projectId).orElse(null);
        if (project == null) return false;

        if (scope == DataScope.PROJECT_ASSIGNED || scope == DataScope.ASSIGNED_ONLY) {
            return project.getReviewerAdmin() != null && project.getReviewerAdmin().getId().equals(actor.getId());
        }

        return false;
    }

    /**
     * Grant a single permission to an Admin (Super Admin only).
     */
    @Transactional
    public AdminPermission grantPermission(Long adminId, PermissionKey key, DataScope scope, User caller) {
        enforceSuperAdmin(caller);
        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new NoSuchElementException("Admin user not found: " + adminId));

        if (admin.getRole() != Role.ADMIN) {
            throw new IllegalArgumentException("Permissions can only be assigned to accounts with ADMIN role.");
        }

        AdminPermission perm = adminPermissionRepository.findByAdminUserIdAndPermissionKey(adminId, key)
                .orElse(new AdminPermission(admin, key, scope, caller.getEmail()));

        perm.setDataScope(scope != null ? scope : DataScope.GLOBAL);
        perm.setGrantedBy(caller.getEmail());
        AdminPermission saved = adminPermissionRepository.save(perm);

        auditLogService.log(caller.getEmail(), "ADMIN_PERMISSION_GRANTED",
                String.format("Granted %s (%s) to admin %s", key, scope, admin.getEmail()));

        return saved;
    }

    /**
     * Revoke a single permission from an Admin (Super Admin only).
     */
    @Transactional
    public void revokePermission(Long adminId, PermissionKey key, User caller) {
        enforceSuperAdmin(caller);
        adminPermissionRepository.findByAdminUserIdAndPermissionKey(adminId, key).ifPresent(p -> {
            adminPermissionRepository.delete(p);
            auditLogService.log(caller.getEmail(), "ADMIN_PERMISSION_REVOKED",
                    String.format("Revoked %s from admin ID %d", key, adminId));
        });
    }

    /**
     * Assigns multiple permissions at once.
     */
    @Transactional
    public List<AdminPermission> updateAdminPermissions(Long adminId, List<AdminPermissionRequest> requests, User caller) {
        enforceSuperAdmin(caller);
        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new NoSuchElementException("Admin not found: " + adminId));

        if (admin.getRole() != Role.ADMIN) {
            throw new IllegalArgumentException("Permissions can only be granted to ADMIN role users.");
        }

        adminPermissionRepository.deleteByAdminUserId(adminId);
        adminPermissionRepository.flush();

        List<AdminPermission> newPerms = new ArrayList<>();
        for (AdminPermissionRequest req : requests) {
            newPerms.add(new AdminPermission(admin, req.getPermissionKey(), req.getDataScope(), caller.getEmail()));
        }

        List<AdminPermission> saved = adminPermissionRepository.saveAll(newPerms);
        auditLogService.log(caller.getEmail(), "ADMIN_PERMISSIONS_BULK_UPDATED",
                String.format("Updated %d permissions for admin %s", saved.size(), admin.getEmail()));
        return saved;
    }

    /**
     * Applies standard role presets for quick configuration by Super Admin.
     */
    @Transactional
    public List<AdminPermission> applyPreset(Long adminId, String presetName, User caller) {
        enforceSuperAdmin(caller);
        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new NoSuchElementException("Admin not found: " + adminId));

        adminPermissionRepository.deleteByAdminUserId(adminId);
        adminPermissionRepository.flush();
        List<AdminPermission> perms = new ArrayList<>();

        switch (presetName.toUpperCase()) {
            case "COMPANY_ADMIN":
                perms.add(new AdminPermission(admin, PermissionKey.USER_VIEW, DataScope.GLOBAL, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_VIEW, DataScope.GLOBAL, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_CREATE, DataScope.GLOBAL, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_EDIT, DataScope.GLOBAL, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.REPORT_VIEW, DataScope.GLOBAL, caller.getEmail()));
                break;

            case "ONBOARDING_ADMIN":
            case "PARTNER_ADMIN":
                perms.add(new AdminPermission(admin, PermissionKey.USER_VIEW, DataScope.USER_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.USER_ONBOARD, DataScope.USER_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.USER_VIEW_REQUIREMENTS, DataScope.USER_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.USER_VIEW_PROJECTS, DataScope.USER_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.USER_VIEW_ORDERS, DataScope.USER_ASSIGNED, caller.getEmail()));
                break;

            case "PROJECT_REVIEWER":
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_VIEW, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_VIEW_DETAILS, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_VIEW_FILES, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_REVIEW, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_APPROVE, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                perms.add(new AdminPermission(admin, PermissionKey.PROJECT_REQUEST_CHANGES, DataScope.PROJECT_ASSIGNED, caller.getEmail()));
                break;

            case "FULL_ADMIN":
                for (PermissionKey key : PermissionKey.values()) {
                    perms.add(new AdminPermission(admin, key, DataScope.GLOBAL, caller.getEmail()));
                }
                break;

            default:
                throw new IllegalArgumentException("Unknown preset: " + presetName);
        }

        List<AdminPermission> saved = adminPermissionRepository.saveAll(perms);
        auditLogService.log(caller.getEmail(), "ADMIN_PRESET_APPLIED",
                String.format("Applied preset %s (%d permissions) to admin %s", presetName, saved.size(), admin.getEmail()));
        return saved;
    }

    /**
     * Assigns users to an Onboarding/Partner Admin for scoped access.
     */
    @Transactional
    public List<AdminUserAssignment> assignUsersToAdmin(Long adminId, List<Long> userIds, User caller) {
        enforceSuperAdmin(caller);
        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new NoSuchElementException("Admin not found: " + adminId));

        adminUserAssignmentRepository.deleteByAdminUserId(adminId);
        adminUserAssignmentRepository.flush();

        List<AdminUserAssignment> assignments = new ArrayList<>();
        for (Long userId : userIds) {
            User user = userRepository.findById(userId).orElse(null);
            if (user != null && user.getRole() == Role.USER) {
                assignments.add(new AdminUserAssignment(admin, user, caller.getEmail(), "Assigned by Super Admin"));
            }
        }

        List<AdminUserAssignment> saved = adminUserAssignmentRepository.saveAll(assignments);
        auditLogService.log(caller.getEmail(), "ADMIN_USERS_ASSIGNED",
                String.format("Assigned %d users to admin %s", saved.size(), admin.getEmail()));
        return saved;
    }

    public List<AdminPermission> getAdminPermissions(Long adminId) {
        return adminPermissionRepository.findByAdminUserId(adminId);
    }

    public List<AdminUserAssignment> getAssignedUsers(Long adminId) {
        return adminUserAssignmentRepository.findByAdminUserId(adminId);
    }

    private void enforceSuperAdmin(User caller) {
        if (caller == null || (caller.getRole() != Role.SUPER_ADMIN && !"superadmin@academic.com".equalsIgnoreCase(caller.getEmail()))) {
            throw new AccessDeniedException("Forbidden: Only SUPER_ADMIN is authorized to manage Admin permissions and assignments.");
        }
    }

    public static class AdminPermissionRequest {
        private PermissionKey permissionKey;
        private DataScope dataScope = DataScope.GLOBAL;

        public PermissionKey getPermissionKey() { return permissionKey; }
        public void setPermissionKey(PermissionKey permissionKey) { this.permissionKey = permissionKey; }
        public DataScope getDataScope() { return dataScope; }
        public void setDataScope(DataScope dataScope) { this.dataScope = dataScope; }
    }
}
