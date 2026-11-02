package com.academic.service;

import com.academic.model.*;
import com.academic.repository.ProjectRepository;
import com.academic.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Collections;
import java.util.NoSuchElementException;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class SecureViewerAccessControlTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private ProjectRepository projectRepository;

    @Mock
    private com.academic.repository.FolderPermissionRepository folderPermissionRepository;

    @Mock
    private com.academic.repository.FilePermissionRepository filePermissionRepository;

    @Mock
    private com.academic.repository.ProjectAssignmentRepository projectAssignmentRepository;

    @InjectMocks
    private AccessControlService accessControlService;

    private Project testProject;
    private Folder testFolder;
    private Asset testAsset;
    private User superAdminUser;
    private User regularUser;

    @BeforeEach
    void setUp() {
        testProject = new Project();
        testProject.setId(1L);
        testProject.setProjectCode("PRJ-ALPHA");
        testProject.setProjectName("Alpha Intelligence Project");

        testFolder = new Folder("Design", null, testProject, "admin@academic.com");
        testFolder.setId(10L);

        testAsset = new Asset(
                testFolder,
                "architecture_spec.pdf",
                "architecture_spec.pdf",
                "application/pdf",
                "pdf",
                1024L,
                "uploads/project_1/design/arch.pdf",
                1,
                true,
                null,
                "System architecture doc",
                "admin@academic.com"
        );
        testAsset.setId(100L);

        superAdminUser = new User("superadmin@academic.com", "pass", "Super Admin", Role.SUPER_ADMIN, UserStatus.ACTIVE);
        superAdminUser.setId(1L);

        regularUser = new User("researcher@academic.com", "pass", "Researcher One", Role.USER, UserStatus.ACTIVE);
        regularUser.setId(2L);
    }

    private void mockSecurityContext(String email, String role) {
        Authentication auth = new UsernamePasswordAuthenticationToken(
                email,
                "n/a",
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role))
        );
        SecurityContext securityContext = mock(SecurityContext.class);
        when(securityContext.getAuthentication()).thenReturn(auth);
        SecurityContextHolder.setContext(securityContext);
    }

    @Test
    @DisplayName("Access Chain: SUPER_ADMIN has full view clearance")
    void testSuperAdminAccessGranted() {
        mockSecurityContext("superadmin@academic.com", "SUPER_ADMIN");
        when(userRepository.findByEmailAndDeletedFalse("superadmin@academic.com")).thenReturn(Optional.of(superAdminUser));
        when(projectRepository.findById(1L)).thenReturn(Optional.of(testProject));

        assertDoesNotThrow(() -> accessControlService.validateAssetAccess(testAsset));
    }

    @Test
    @DisplayName("Access Chain: Assigned Regular USER has read-only view clearance")
    void testUserViewAccessGranted() {
        mockSecurityContext("researcher@academic.com", "USER");
        when(userRepository.findByEmailAndDeletedFalse("researcher@academic.com")).thenReturn(Optional.of(regularUser));
        when(projectRepository.findById(1L)).thenReturn(Optional.of(testProject));
        when(projectAssignmentRepository.findActiveAssignment(1L, regularUser.getId()))
                .thenReturn(Optional.of(new ProjectAssignment(testProject, regularUser, null, "admin@academic.com", "notes")));

        assertDoesNotThrow(() -> accessControlService.validateAssetAccess(testAsset));
    }

    @Test
    @DisplayName("Access Chain: Unassigned Regular USER is DENIED access to project files")
    void testUnassignedUserViewAccessDenied() {
        mockSecurityContext("researcher@academic.com", "USER");
        when(userRepository.findByEmailAndDeletedFalse("researcher@academic.com")).thenReturn(Optional.of(regularUser));
        when(projectRepository.findById(1L)).thenReturn(Optional.of(testProject));
        when(projectAssignmentRepository.findActiveAssignment(1L, regularUser.getId()))
                .thenReturn(Optional.empty());

        AccessDeniedException ex = assertThrows(AccessDeniedException.class, () ->
                accessControlService.validateAssetAccess(testAsset)
        );

        assertTrue(ex.getMessage().contains("You are not assigned to project"));
    }

    @Test
    @DisplayName("Write Clearance: Regular USER cannot create, edit, or delete folders/files (write clearance DENIED)")
    void testUserWriteAccessDenied() {
        mockSecurityContext("researcher@academic.com", "USER");
        when(userRepository.findByEmailAndDeletedFalse("researcher@academic.com")).thenReturn(Optional.of(regularUser));

        AccessDeniedException ex = assertThrows(AccessDeniedException.class, () ->
                accessControlService.validateWriteClearance(1L)
        );

        assertTrue(ex.getMessage().contains("Regular users have read-only view access"));
    }

    @Test
    @DisplayName("Access Chain: Deactivated user must be DENIED access regardless of role")
    void testDeactivatedUserAccessDenied() {
        regularUser.setDeleted(true);
        mockSecurityContext("researcher@academic.com", "USER");
        when(userRepository.findByEmailAndDeletedFalse("researcher@academic.com")).thenReturn(Optional.of(regularUser));

        AccessDeniedException ex = assertThrows(AccessDeniedException.class, () ->
                accessControlService.validateAssetAccess(testAsset)
        );

        assertTrue(ex.getMessage().contains("User account is deactivated"));
    }

    @Test
    @DisplayName("Access Chain: Inactive asset must be rejected")
    void testInactiveAssetAccessRejected() {
        testAsset.setActive(false);

        NoSuchElementException ex = assertThrows(NoSuchElementException.class, () ->
                accessControlService.validateAssetAccess(testAsset)
        );

        assertTrue(ex.getMessage().contains("Asset is deactivated or deleted"));
    }
}
