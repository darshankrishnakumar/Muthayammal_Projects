package com.academic.service;

import com.academic.dto.AssetResponse;
import com.academic.model.Asset;
import com.academic.model.Folder;
import com.academic.model.Project;
import com.academic.repository.AssetRepository;
import com.academic.repository.FolderRepository;
import com.academic.repository.ProjectRepository;
import com.academic.service.storage.FileStorageService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.InputStream;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("null")
public class AssetServiceTest {

    @Mock
    private AssetRepository assetRepository;

    @Mock
    private FolderRepository folderRepository;

    @Mock
    private ProjectRepository projectRepository;

    @Mock
    private FileStorageService storageService;

    @Mock
    private AccessControlService accessControlService;

    @Mock
    private AuditLogService auditLogService;

    @Mock
    private FolderService folderService;

    @InjectMocks
    private AssetService assetService;

    private Project testProject;
    private Folder testFolder;
    private Asset testAssetV1;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(assetService, "maxFileSizeBytes", 52428800L); // 50MB

        testProject = new Project();
        testProject.setId(1L);
        testProject.setProjectCode("PRJ-SECURE");
        testProject.setProjectName("Secure Gateway");

        testFolder = new Folder("SRS", null, testProject, "admin@academic.com");
        testFolder.setId(10L);

        testAssetV1 = new Asset(
                testFolder,
                "spec_v1.pdf",
                "spec_v1.pdf",
                "application/pdf",
                "pdf",
                1024L,
                "project_1/folder_10/uuid_spec_v1.pdf",
                1,
                true,
                null,
                "Initial SRS draft",
                "admin@academic.com"
        );
        testAssetV1.setId(100L);
    }

    @Test
    @DisplayName("Should successfully upload file, store in storage and save metadata")
    void testUploadAssetSuccess() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "System_Architecture.pdf",
                "application/pdf",
                "Sample PDF content".getBytes()
        );

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(testFolder));
        when(assetRepository.findActiveInFolderByOriginalFileName(10L, "System_Architecture.pdf")).thenReturn(Optional.empty());
        when(storageService.storeFile(any(InputStream.class), eq("System_Architecture.pdf"), eq(1L), eq(10L)))
                .thenReturn("project_1/folder_10/uuid_System_Architecture.pdf");

        when(assetRepository.save(any(Asset.class))).thenAnswer(i -> {
            Asset a = i.getArgument(0);
            a.setId(101L);
            return a;
        });

        AssetResponse mockResp = new AssetResponse();
        mockResp.setId(101L);
        mockResp.setOriginalFileName("System_Architecture.pdf");
        mockResp.setVersionNo(1);
        when(folderService.mapToAssetResponse(any(Asset.class))).thenReturn(mockResp);

        AssetResponse result = assetService.uploadAsset(1L, 10L, file, "Architecture diagrams", "admin@academic.com");

        assertNotNull(result);
        assertEquals(101L, result.getId());
        assertEquals("System_Architecture.pdf", result.getOriginalFileName());
        verify(storageService, times(1)).storeFile(any(InputStream.class), eq("System_Architecture.pdf"), eq(1L), eq(10L));
        verify(assetRepository, times(1)).save(any(Asset.class));
        verify(auditLogService, times(1)).log(eq("admin@academic.com"), eq("UPLOAD_FILE"), anyString());
    }

    @Test
    @DisplayName("Should reject oversized files exceeding the configured limit")
    void testRejectOversizedFile() {
        ReflectionTestUtils.setField(assetService, "maxFileSizeBytes", 100L); // Small limit 100 bytes

        MockMultipartFile largeFile = new MockMultipartFile(
                "file",
                "Huge_Dump.sql",
                "text/plain",
                new byte[2048]
        );

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(testFolder));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () ->
                assetService.uploadAsset(1L, 10L, largeFile, "SQL dump", "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("exceeds the maximum allowed threshold"));
        verify(storageService, never()).storeFile(any(), any(), any(), any());
    }

    @Test
    @DisplayName("Should reject filenames with directory traversal patterns")
    void testRejectPathTraversalFilename() {
        MockMultipartFile traversalFile = new MockMultipartFile(
                "file",
                "../../etc/passwd.txt",
                "text/plain",
                "malicious payload".getBytes()
        );

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(testFolder));

        SecurityException ex = assertThrows(SecurityException.class, () ->
                assetService.uploadAsset(1L, 10L, traversalFile, "Attack attempt", "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("Illegal path traversal"));
    }

    @Test
    @DisplayName("Should reject duplicate active filename in the same folder")
    void testRejectDuplicateFilenameInSameFolder() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "spec_v1.pdf",
                "application/pdf",
                "content".getBytes()
        );

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(testFolder));
        when(assetRepository.findActiveInFolderByOriginalFileName(10L, "spec_v1.pdf")).thenReturn(Optional.of(testAssetV1));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () ->
                assetService.uploadAsset(1L, 10L, file, "Duplicate file", "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("already exists in folder"));
        verify(storageService, never()).storeFile(any(), any(), any(), any());
    }

    @Test
    @DisplayName("Rollback Safety: Should clean up storage file if database save throws exception")
    void testStorageRollbackOnDatabaseFailure() {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "Word content".getBytes()
        );

        String generatedStoragePath = "project_1/folder_10/uuid_document.docx";

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(testFolder));
        when(assetRepository.findActiveInFolderByOriginalFileName(10L, "document.docx")).thenReturn(Optional.empty());
        when(storageService.storeFile(any(), eq("document.docx"), eq(1L), eq(10L))).thenReturn(generatedStoragePath);

        // Simulate DB crash
        when(assetRepository.save(any(Asset.class))).thenThrow(new RuntimeException("MySQL DB Connection Timeout"));

        RuntimeException ex = assertThrows(RuntimeException.class, () ->
                assetService.uploadAsset(1L, 10L, file, "Description", "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("Database error saving asset metadata. File storage rolled back"));
        // Verify rollback: storageService.deleteFile was executed
        verify(storageService, times(1)).deleteFile(generatedStoragePath);
    }

    @Test
    @DisplayName("Should version asset (v1 -> v2) without overwriting original and linking parent")
    void testReplaceAssetVersioning() {
        MockMultipartFile newVersionFile = new MockMultipartFile(
                "file",
                "spec_v2.pdf",
                "application/pdf",
                "Updated spec content".getBytes()
        );

        when(assetRepository.findByIdAndActiveTrue(100L)).thenReturn(Optional.of(testAssetV1));
        when(storageService.storeFile(any(), eq("spec_v2.pdf"), eq(1L), eq(10L)))
                .thenReturn("project_1/folder_10/uuid_spec_v2.pdf");

        when(assetRepository.save(any(Asset.class))).thenAnswer(i -> {
            Asset a = i.getArgument(0);
            if (a.getId() == null) a.setId(102L);
            return a;
        });

        AssetResponse mockResp = new AssetResponse();
        mockResp.setId(102L);
        mockResp.setVersionNo(2);
        mockResp.setCurrentVersion(true);
        when(folderService.mapToAssetResponse(any(Asset.class))).thenReturn(mockResp);

        AssetResponse response = assetService.replaceAsset(100L, newVersionFile, "Added Section 4", "admin@academic.com");

        assertNotNull(response);
        assertEquals(2, response.getVersionNo());
        assertTrue(response.isCurrentVersion());
        assertFalse(testAssetV1.isCurrentVersion()); // Old version deactivated as current
        verify(storageService, times(1)).storeFile(any(), eq("spec_v2.pdf"), eq(1L), eq(10L));
        verify(auditLogService, times(1)).log(eq("admin@academic.com"), eq("REPLACE_FILE_VERSION"), anyString());
    }

    @Test
    @DisplayName("Should restore previous version correctly")
    void testRestoreVersion() {
        Asset testAssetV2 = new Asset(
                testFolder, "spec_v2.pdf", "spec_v2.pdf", "application/pdf", "pdf", 2048L,
                "project_1/folder_10/uuid_spec_v2.pdf", 2, true, testAssetV1, "V2 desc", "admin@academic.com"
        );
        testAssetV2.setId(102L);
        testAssetV1.setCurrentVersion(false);

        List<Asset> history = Arrays.asList(testAssetV2, testAssetV1);

        when(assetRepository.findByIdAndActiveTrue(102L)).thenReturn(Optional.of(testAssetV2));
        when(assetRepository.findVersionHistoryByRootId(100L)).thenReturn(history);

        AssetResponse mockResp = new AssetResponse();
        mockResp.setId(100L);
        mockResp.setVersionNo(1);
        mockResp.setCurrentVersion(true);
        when(folderService.mapToAssetResponse(testAssetV1)).thenReturn(mockResp);

        AssetResponse response = assetService.restoreVersion(102L, 1, "admin@academic.com");

        assertNotNull(response);
        assertEquals(1, response.getVersionNo());
        assertTrue(testAssetV1.isCurrentVersion());
        assertFalse(testAssetV2.isCurrentVersion());
        verify(auditLogService, times(1)).log(eq("admin@academic.com"), eq("RESTORE_FILE_VERSION"), anyString());
    }
}
