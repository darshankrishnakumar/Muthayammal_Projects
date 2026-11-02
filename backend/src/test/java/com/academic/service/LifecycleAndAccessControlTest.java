package com.academic.service;

import com.academic.model.*;
import com.academic.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("null")
class LifecycleAndAccessControlTest {

    @Mock
    private AdminPermissionRepository adminPermissionRepository;

    @Mock
    private AdminUserAssignmentRepository adminUserAssignmentRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private AdminAccessControlService adminAccessControlService;

    private User sampleAdmin;
    private User regularUser;

    @BeforeEach
    void setUp() {
        sampleAdmin = new User("admin.test@academic.com", "secret", "Test Admin", Role.ADMIN, UserStatus.ACTIVE);
        sampleAdmin.setId(10L);

        regularUser = new User("user.test@academic.com", "secret", "Test User", Role.USER, UserStatus.ACTIVE);
        regularUser.setId(20L);
    }

    @Test
    @DisplayName("Admin Scoping: hasPermission should return true if permission key exists")
    void testHasPermission() {
        when(adminPermissionRepository.findByAdminUserIdAndPermissionKey(10L, PermissionKey.USER_VIEW))
                .thenReturn(Optional.of(new AdminPermission(sampleAdmin, PermissionKey.USER_VIEW, DataScope.GLOBAL, "superadmin@academic.com")));

        boolean allowed = adminAccessControlService.hasPermission(sampleAdmin, PermissionKey.USER_VIEW);
        assertTrue(allowed);
    }

    @Test
    @DisplayName("Admin Scoping: canAccessUser should respect USER_ASSIGNED data scope")
    void testUserScopingAccess() {
        when(adminPermissionRepository.findByAdminUserIdAndPermissionKey(10L, PermissionKey.USER_VIEW))
                .thenReturn(Optional.of(new AdminPermission(sampleAdmin, PermissionKey.USER_VIEW, DataScope.USER_ASSIGNED, "superadmin@academic.com")));

        when(adminUserAssignmentRepository.existsByAdminUserIdAndAssignedUserId(10L, 20L)).thenReturn(true);
        when(adminUserAssignmentRepository.existsByAdminUserIdAndAssignedUserId(10L, 99L)).thenReturn(false);

        assertTrue(adminAccessControlService.canAccessUser(sampleAdmin, 20L));
        assertFalse(adminAccessControlService.canAccessUser(sampleAdmin, 99L));
    }

    @Test
    @DisplayName("Presets: applying COMPANY_ADMIN should grant company-level permissions")
    void testApplyPreset() {
        User superAdmin = new User("superadmin@academic.com", "secret", "Super Admin", Role.SUPER_ADMIN, UserStatus.ACTIVE);
        when(userRepository.findById(10L)).thenReturn(Optional.of(sampleAdmin));

        adminAccessControlService.applyPreset(10L, "COMPANY_ADMIN", superAdmin);

        verify(adminPermissionRepository, times(1)).saveAll(anyList());
        verify(auditLogService, atLeastOnce()).log(eq("superadmin@academic.com"), eq("ADMIN_PRESET_APPLIED"), anyString());
    }
}
