package com.academic.controller;

import com.academic.model.*;
import com.academic.repository.ProjectRepository;
import com.academic.repository.RequirementRepository;
import com.academic.repository.UserRepository;
import com.academic.service.AccessControlService;
import com.academic.service.AdminAccessControlService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/access-control")
@SuppressWarnings("null")
public class AdminAccessControlController {

    @Autowired
    private com.academic.service.UserService userService;

    @Autowired
    private AdminAccessControlService adminAccessControlService;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private RequirementRepository requirementRepository;

    @GetMapping({"/admins/{adminId}/permissions", "/admin/{adminId}/permissions"})
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> getAdminPermissions(@PathVariable Long adminId) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        // Only Super Admin or the admin themselves can view their permissions
        if (caller.getRole() != Role.SUPER_ADMIN && !caller.getId().equals(adminId)) {
            return ResponseEntity.status(403).body(Map.of("error", "Forbidden: Cannot view permissions for other admins."));
        }
        return ResponseEntity.ok(adminAccessControlService.getAdminPermissions(adminId));
    }

    @PostMapping({"/admins/{adminId}/permissions", "/admin/{adminId}/permissions"})
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> updateAdminPermissions(
            @PathVariable Long adminId,
            @RequestBody List<AdminAccessControlService.AdminPermissionRequest> requests) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        if (caller.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(403).body(Map.of("error", "Forbidden: Only Super Admin can modify admin permissions."));
        }
        List<AdminPermission> updated = adminAccessControlService.updateAdminPermissions(adminId, requests, caller);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Admin permissions updated successfully.",
                "permissions", updated
        ));
    }

    @PostMapping({
            "/admins/{adminId}/apply-preset",
            "/admin/{adminId}/apply-preset",
            "/admins/{adminId}/preset/{presetName}",
            "/admin/{adminId}/preset/{presetName}"
    })
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> applyPreset(
            @PathVariable Long adminId,
            @PathVariable(required = false) String presetName,
            @RequestBody(required = false) Map<String, String> payload) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        if (caller.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(403).body(Map.of("error", "Forbidden: Only Super Admin can apply presets."));
        }
        String preset = (presetName != null && !presetName.isBlank()) 
                ? presetName 
                : (payload != null ? payload.get("preset") : null);

        if (preset == null || preset.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Preset name is required (e.g. COMPANY_ADMIN, ONBOARDING_ADMIN, PROJECT_REVIEWER, FULL_ADMIN)."));
        }
        List<AdminPermission> perms = adminAccessControlService.applyPreset(adminId, preset, caller);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "preset", preset,
                "message", "Preset applied successfully.",
                "permissionsCount", perms.size()
        ));
    }

    @GetMapping({"/admins/{adminId}/assigned-users", "/admin/{adminId}/assigned-users", "/admin/{adminId}/users", "/admins/{adminId}/users"})
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> getAssignedUsers(@PathVariable Long adminId) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        if (caller.getRole() != Role.SUPER_ADMIN && !caller.getId().equals(adminId)) {
            return ResponseEntity.status(403).body(Map.of("error", "Forbidden."));
        }
        return ResponseEntity.ok(adminAccessControlService.getAssignedUsers(adminId));
    }

    @PostMapping({"/admins/{adminId}/assign-users", "/admin/{adminId}/assign-users", "/admin/{adminId}/users", "/admins/{adminId}/users"})
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> assignUsers(
            @PathVariable Long adminId,
            @RequestBody(required = false) Map<String, List<Long>> payload) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        if (caller.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(403).body(Map.of("error", "Forbidden: Only Super Admin can assign users to admins."));
        }
        List<?> rawIds = (payload != null && payload.get("userIds") != null) ? payload.get("userIds") : List.of();
        List<Long> userIds = new ArrayList<>();
        for (Object idObj : rawIds) {
            if (idObj instanceof Number num) {
                userIds.add(num.longValue());
            } else if (idObj != null) {
                userIds.add(Long.valueOf(idObj.toString()));
            }
        }
        List<AdminUserAssignment> assignments = adminAccessControlService.assignUsersToAdmin(adminId, userIds, caller);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Users assigned to admin successfully.",
                "assignedCount", assignments.size()
        ));
    }

    @GetMapping("/developers")
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> getDevelopers() {
        List<User> developers = userRepository.findByRoleAndDeletedFalse(Role.PROJECT_DEVELOPER);
        return ResponseEntity.ok(developers);
    }

    @GetMapping("/overview")
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'ADMIN')")
    public ResponseEntity<?> getOverview() {
        Map<String, Object> stats = new HashMap<>();

        stats.put("totalUsers", userRepository.count());
        stats.put("totalProjects", projectRepository.count());
        stats.put("pendingRequirements", requirementRepository.countByStatus(RequirementStatus.SUBMITTED)
                + requirementRepository.countByStatus(RequirementStatus.ADVANCE_PAYMENT_COMPLETED));
        stats.put("projectsInDevelopment", projectRepository.countByStatus(ProjectStatus.IN_PROGRESS)
                + projectRepository.countByStatus(ProjectStatus.DEVELOPER_ASSIGNED));
        stats.put("projectsAwaitingReview", projectRepository.countByStatus(ProjectStatus.READY_FOR_REVIEW));
        stats.put("projectsAwaitingFinalPayment", projectRepository.countByStatus(ProjectStatus.READY_FOR_FINAL_PAYMENT));
        return ResponseEntity.ok(stats);
    }

    @PostMapping("/users/{userId}/role")
    public ResponseEntity<?> updateUserRole(
            @PathVariable Long userId,
            @RequestBody Map<String, String> payload) {
        User caller = accessControlService.getCurrentAuthenticatedUser();
        if (caller.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(403).body(Map.of("message", "Forbidden: Only Super Admin can change user roles."));
        }
        String roleStr = payload.get("role");
        if (roleStr == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "Role is required."));
        }
        Role role = Role.valueOf(roleStr);
        if (role == Role.SUPER_ADMIN) {
            return ResponseEntity.status(403).body(Map.of("message", "Super Admin cannot be granted through the API."));
        }
        if (caller.getId().equals(userId)) {
            return ResponseEntity.badRequest().body(Map.of("message", "You cannot change your own role."));
        }
        User target = userRepository.findById(userId)
                .orElseThrow(() -> new java.util.NoSuchElementException("User not found: " + userId));
        Long collegeId = payload.get("collegeId") != null && !payload.get("collegeId").isBlank() ? Long.valueOf(payload.get("collegeId")) : null;
        User saved = userService.changeRoleAndCollege(target, role, collegeId, caller.getEmail());
        return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "User role updated to " + role,
                "user", saved
        ));
    }
}
