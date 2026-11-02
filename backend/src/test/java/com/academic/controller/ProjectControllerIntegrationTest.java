package com.academic.controller;

import com.academic.config.JwtTokenProvider;
import com.academic.dto.ProjectCreateRequest;
import com.academic.model.ProjectStatus;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@SuppressWarnings("null")
class ProjectControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("Unauthenticated request to /api/projects should return 401 Unauthorized")
    void testUnauthenticatedAccessDenied() throws Exception {
        mockMvc.perform(get("/api/projects"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Super Admin can list projects and create project")
    void testSuperAdminCreateAndListProjects() throws Exception {
        String superAdminToken = jwtTokenProvider.generateToken("superadmin@academic.com", "SUPER_ADMIN");

        // List projects
        mockMvc.perform(get("/api/projects")
                        .header("Authorization", "Bearer " + superAdminToken))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON));

        // Create project
        ProjectCreateRequest request = new ProjectCreateRequest();
        request.setProjectName("Super Admin Project");
        request.setDescription("Created by Super Admin");
        request.setBudget(7500.00);
        request.setTechnologyStack("Spring Boot, React");
        request.setStatus(ProjectStatus.DRAFT);

        mockMvc.perform(post("/api/projects")
                        .header("Authorization", "Bearer " + superAdminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.projectCode").exists())
                .andExpect(jsonPath("$.projectName").value("Super Admin Project"));
    }

    @Test
    @DisplayName("Admin role cannot create projects (Admin can only create folders)")
    void testAdminCannotCreateProject() throws Exception {
        String adminToken = jwtTokenProvider.generateToken("admin@academic.com", "ADMIN");

        // List projects allowed
        mockMvc.perform(get("/api/projects")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk());

        // Create project denied
        ProjectCreateRequest request = new ProjectCreateRequest();
        request.setProjectName("Admin Unauthorized Project");

        mockMvc.perform(post("/api/projects")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.message").value("Access denied. Only Super Admin is authorized to create new projects."));
    }

    @Test
    @DisplayName("Regular user cannot create projects, but can view projects (RBAC enforcement)")
    void testRegularUserCannotCreateProject() throws Exception {
        String userToken = jwtTokenProvider.generateToken("user@academic.com", "USER");

        // List projects view allowed
        mockMvc.perform(get("/api/projects")
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isOk());

        // Create project denied
        ProjectCreateRequest request = new ProjectCreateRequest();
        request.setProjectName("Unauthorized Project");

        mockMvc.perform(post("/api/projects")
                        .header("Authorization", "Bearer " + userToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.message").value("Access denied. Only Super Admin is authorized to create new projects."));
    }
}
