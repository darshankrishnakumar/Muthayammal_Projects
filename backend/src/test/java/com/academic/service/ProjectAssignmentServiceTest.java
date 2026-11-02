package com.academic.service;

import com.academic.model.Project;
import com.academic.model.ProjectAssignment;
import com.academic.model.ProjectStatus;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.model.UserStatus;
import com.academic.repository.ProjectAssignmentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.access.AccessDeniedException;

import java.util.Objects;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("null")
class ProjectAssignmentServiceTest {

    @Mock
    private ProjectAssignmentRepository projectAssignmentRepository;

    @Mock
    private ProjectService projectService;

    @Mock
    private UserService userService;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private ProjectAssignmentService projectAssignmentService;

    private Project sampleProject;
    private User superAdminUser;
    private User assignedAdminUser;
    private User unassignedAdminUser;
    private User sampleUser;

    @BeforeEach
    void setUp() {
        sampleProject = new Project("Test Project", "PRJ-123456", "Desc", java.math.BigDecimal.valueOf(1000.0), "Java", ProjectStatus.APPROVED, null, "superadmin@academic.com");
        sampleProject.setId(10L);

        superAdminUser = new User("superadmin@academic.com", "pass", "Super Admin", Role.SUPER_ADMIN, UserStatus.ACTIVE);
        superAdminUser.setId(1L);

        assignedAdminUser = new User("admin1@academic.com", "pass", "Assigned Admin", Role.ADMIN, UserStatus.ACTIVE);
        assignedAdminUser.setId(2L);

        unassignedAdminUser = new User("admin2@academic.com", "pass", "Unassigned Admin", Role.ADMIN, UserStatus.ACTIVE);
        unassignedAdminUser.setId(3L);

        sampleUser = new User("user1@academic.com", "pass", "Sample User", Role.USER, UserStatus.ACTIVE);
        sampleUser.setId(20L);
    }

    @Test
    @DisplayName("Super Admin can assign project to Admin")
    void testSuperAdminAssignsToAdmin() {
        when(projectService.getProjectById(10L)).thenReturn(sampleProject);
        when(userService.findByEmail("superadmin@academic.com")).thenReturn(Optional.of(superAdminUser));
        when(userService.findById(2L)).thenReturn(Optional.of(assignedAdminUser));
        when(projectAssignmentRepository.findByProjectIdAndUserId(10L, 2L)).thenReturn(Optional.empty());
        when(projectAssignmentRepository.save(any(ProjectAssignment.class)))
                .thenAnswer(i -> Objects.requireNonNull(i.getArgument(0, ProjectAssignment.class)));

        ProjectAssignment result = projectAssignmentService.assignUserToProject(10L, 2L, null, "Managing Admin", "superadmin@academic.com");

        assertNotNull(result);
        assertEquals(sampleProject, result.getProject());
        assertEquals(assignedAdminUser, result.getUser());
        assertTrue(result.isActive());
        verify(auditLogService, times(1)).log(eq("superadmin@academic.com"), eq("ASSIGN_PROJECT_USER"), anyString());
    }

    @Test
    @DisplayName("Assigned Admin can assign project to User")
    void testAssignedAdminAssignsToUser() {
        when(projectService.getProjectById(10L)).thenReturn(sampleProject);
        when(userService.findByEmail("admin1@academic.com")).thenReturn(Optional.of(assignedAdminUser));
        when(userService.findById(20L)).thenReturn(Optional.of(sampleUser));
        when(projectAssignmentRepository.findActiveAssignment(10L, 2L))
                .thenReturn(Optional.of(new ProjectAssignment(sampleProject, assignedAdminUser, null, "superadmin@academic.com", "notes")));
        when(projectAssignmentRepository.findByProjectIdAndUserId(10L, 20L)).thenReturn(Optional.empty());
        when(projectAssignmentRepository.save(any(ProjectAssignment.class)))
                .thenAnswer(i -> Objects.requireNonNull(i.getArgument(0, ProjectAssignment.class)));

        ProjectAssignment result = projectAssignmentService.assignUserToProject(10L, 20L, null, "User assignment", "admin1@academic.com");

        assertNotNull(result);
        assertEquals(sampleProject, result.getProject());
        assertEquals(sampleUser, result.getUser());
        assertTrue(result.isActive());
        verify(auditLogService, times(1)).log(eq("admin1@academic.com"), eq("ASSIGN_PROJECT_USER"), anyString());
    }

    @Test
    @DisplayName("Unassigned Admin cannot assign project to User (DENIED)")
    void testUnassignedAdminCannotAssignUser() {
        when(projectService.getProjectById(10L)).thenReturn(sampleProject);
        when(userService.findByEmail("admin2@academic.com")).thenReturn(Optional.of(unassignedAdminUser));
        when(userService.findById(20L)).thenReturn(Optional.of(sampleUser));
        when(projectAssignmentRepository.findActiveAssignment(10L, 3L)).thenReturn(Optional.empty());

        AccessDeniedException ex = assertThrows(AccessDeniedException.class, () ->
                projectAssignmentService.assignUserToProject(10L, 20L, null, "notes", "admin2@academic.com")
        );

        assertTrue(ex.getMessage().contains("You cannot assign users to a project that is not assigned to you"));
    }

    @Test
    @DisplayName("Admin cannot assign another Admin (must only assign regular Users)")
    void testAdminCannotAssignAnotherAdmin() {
        User anotherAdmin = new User("admin3@academic.com", "pass", "Admin Three", Role.ADMIN, UserStatus.ACTIVE);
        anotherAdmin.setId(4L);

        when(projectService.getProjectById(10L)).thenReturn(sampleProject);
        when(userService.findByEmail("admin1@academic.com")).thenReturn(Optional.of(assignedAdminUser));
        when(userService.findById(4L)).thenReturn(Optional.of(anotherAdmin));
        when(projectAssignmentRepository.findActiveAssignment(10L, 2L))
                .thenReturn(Optional.of(new ProjectAssignment(sampleProject, assignedAdminUser, null, "superadmin@academic.com", "notes")));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () ->
                projectAssignmentService.assignUserToProject(10L, 4L, null, "notes", "admin1@academic.com")
        );

        assertTrue(ex.getMessage().contains("Admins can only assign projects to regular Users"));
    }

    @Test
    @DisplayName("Should prevent duplicate assignment if active assignment already exists")
    void testPreventDuplicateAssignment() {
        ProjectAssignment existingAssignment = new ProjectAssignment(sampleProject, sampleUser, null, "superadmin@academic.com", "existing");
        existingAssignment.setActive(true);

        when(projectService.getProjectById(10L)).thenReturn(sampleProject);
        when(userService.findByEmail("superadmin@academic.com")).thenReturn(Optional.of(superAdminUser));
        when(userService.findById(20L)).thenReturn(Optional.of(sampleUser));
        when(projectAssignmentRepository.findByProjectIdAndUserId(10L, 20L)).thenReturn(Optional.of(existingAssignment));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                projectAssignmentService.assignUserToProject(10L, 20L, null, "new assignment", "superadmin@academic.com")
        );

        assertEquals("Project already assigned to this user.", exception.getMessage());
    }

    @Test
    @DisplayName("Should deactivate assignment by user")
    void testDeactivateAssignmentByUser() {
        ProjectAssignment assignment = new ProjectAssignment(sampleProject, sampleUser, null, "superadmin@academic.com", "notes");
        when(projectAssignmentRepository.findByProjectIdAndUserId(10L, 20L)).thenReturn(Optional.of(assignment));
        when(projectAssignmentRepository.save(any(ProjectAssignment.class)))
                .thenAnswer(i -> Objects.requireNonNull(i.getArgument(0, ProjectAssignment.class)));

        projectAssignmentService.deactivateAssignmentByUser(10L, 20L, "superadmin@academic.com");

        assertFalse(assignment.isActive());
        assertNotNull(assignment.getDeactivatedAt());
        verify(auditLogService, times(1)).log(eq("superadmin@academic.com"), eq("REMOVE_PROJECT_ASSIGNMENT"), anyString());
    }
}
