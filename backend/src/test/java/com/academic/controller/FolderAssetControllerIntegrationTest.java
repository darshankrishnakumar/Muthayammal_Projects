package com.academic.controller;

import com.academic.config.JwtTokenProvider;
import com.academic.dto.AssetResponse;
import com.academic.dto.FolderRequest;
import com.academic.dto.FolderResponse;
import com.academic.service.AssetService;
import com.academic.service.FolderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.*;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = {FolderController.class, AssetController.class})
@AutoConfigureMockMvc(addFilters = false)
@SuppressWarnings("null")
class FolderAssetControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @MockBean
    private com.academic.repository.UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private FolderService folderService;

    @MockBean
    private AssetService assetService;

    @Test
    @WithMockUser(username = "admin@academic.com", roles = {"ADMIN"})
    @DisplayName("Authenticated Admin can list folders via GET /api/projects/{id}/folders")
    void testAdminGetProjectFolders() throws Exception {
        FolderResponse folder1 = new FolderResponse();
        folder1.setId(10L);
        folder1.setName("Documentation");
        folder1.setProjectId(1L);

        when(folderService.getProjectFolders(1L)).thenReturn(Collections.singletonList(folder1));

        mockMvc.perform(get("/api/projects/1/folders"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(10L))
                .andExpect(jsonPath("$[0].name").value("Documentation"));
    }

    @Test
    @WithMockUser(username = "admin@academic.com", roles = {"ADMIN"})
    @DisplayName("Authenticated Admin can create folder via POST /api/projects/{id}/folders")
    void testAdminCreateFolder() throws Exception {
        FolderRequest request = new FolderRequest("SRS", 10L);

        FolderResponse created = new FolderResponse();
        created.setId(20L);
        created.setName("SRS");
        created.setParentFolderId(10L);
        created.setProjectId(1L);

        when(folderService.createFolder(eq(1L), any(FolderRequest.class), any())).thenReturn(created);

        mockMvc.perform(post("/api/projects/1/folders")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(20L))
                .andExpect(jsonPath("$.name").value("SRS"))
                .andExpect(jsonPath("$.parentFolderId").value(10L));
    }

    @Test
    @WithMockUser(username = "admin@academic.com", roles = {"ADMIN"})
    @DisplayName("Authenticated Admin can upload file via POST /api/assets/upload")
    void testAdminUploadAsset() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "Specification.pdf",
                "application/pdf",
                "Mock PDF Content".getBytes()
        );

        AssetResponse assetResp = new AssetResponse();
        assetResp.setId(100L);
        assetResp.setFolderId(20L);
        assetResp.setProjectId(1L);
        assetResp.setOriginalFileName("Specification.pdf");
        assetResp.setMimeType("application/pdf");
        assetResp.setVersionNo(1);

        when(assetService.uploadAsset(eq(1L), eq(20L), any(), any(), any()))
                .thenReturn(assetResp);

        mockMvc.perform(multipart("/api/assets/upload")
                        .file(file)
                        .param("projectId", "1")
                        .param("folderId", "20")
                        .param("description", "Initial release")
                        .with(csrf()))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(100L))
                .andExpect(jsonPath("$.originalFileName").value("Specification.pdf"))
                .andExpect(jsonPath("$.versionNo").value(1));
    }

    @Test
    @WithMockUser(username = "admin@academic.com", roles = {"ADMIN"})
    @DisplayName("Authenticated user can view asset content via GET /api/assets/{id}/view")
    void testViewAsset() throws Exception {
        ByteArrayResource resource = new ByteArrayResource("PDF Content Stream".getBytes());
        Map<String, Object> viewData = new HashMap<>();
        viewData.put("resource", resource);
        viewData.put("mimeType", "application/pdf");
        viewData.put("fileName", "Specification.pdf");

        when(assetService.getAssetForSecureView(eq(100L), isNull())).thenReturn(viewData);

        mockMvc.perform(get("/api/assets/100/view"))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/pdf"))
                .andExpect(header().string("Content-Disposition", "inline; filename=\"Specification.pdf\""))
                .andExpect(header().string("Cache-Control", "no-cache, no-store, must-revalidate"))
                .andExpect(content().bytes("PDF Content Stream".getBytes()));
    }

    @Test
    @WithMockUser(username = "admin@academic.com", roles = {"ADMIN"})
    @DisplayName("Authenticated Admin can replace file version via PUT /api/assets/{id}/replace")
    void testReplaceAsset() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "Specification_v2.pdf",
                "application/pdf",
                "Updated PDF Content".getBytes()
        );

        AssetResponse assetResp = new AssetResponse();
        assetResp.setId(101L);
        assetResp.setOriginalFileName("Specification_v2.pdf");
        assetResp.setVersionNo(2);
        assetResp.setCurrentVersion(true);

        when(assetService.replaceAsset(eq(100L), any(), any(), any()))
                .thenReturn(assetResp);

        mockMvc.perform(multipart(HttpMethod.PUT, "/api/assets/100/replace")
                        .file(file)
                        .param("changeNotes", "Updated to v2")
                        .with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(101L))
                .andExpect(jsonPath("$.versionNo").value(2))
                .andExpect(jsonPath("$.currentVersion").value(true));
    }
}
