package com.academic.service;

import com.academic.dto.BreadcrumbDto;
import com.academic.dto.FolderRequest;
import com.academic.dto.FolderResponse;
import com.academic.model.Folder;
import com.academic.model.Project;
import com.academic.repository.AssetRepository;
import com.academic.repository.FolderRepository;
import com.academic.repository.ProjectRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("null")
public class FolderServiceTest {

    @Mock
    private FolderRepository folderRepository;

    @Mock
    private AssetRepository assetRepository;

    @Mock
    private ProjectRepository projectRepository;

    @Mock
    private AccessControlService accessControlService;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private FolderService folderService;

    private Project testProject;
    private Folder rootFolder;
    private Folder subFolder;

    @BeforeEach
    void setUp() {
        testProject = new Project();
        testProject.setId(1L);
        testProject.setProjectCode("PRJ-TEST");
        testProject.setProjectName("Academic Research System");

        rootFolder = new Folder("Documentation", null, testProject, "admin@academic.com");
        rootFolder.setId(10L);

        subFolder = new Folder("SRS", rootFolder, testProject, "admin@academic.com");
        subFolder.setId(20L);
    }

    @Test
    @DisplayName("Should successfully create a root folder")
    void testCreateRootFolder() {
        FolderRequest request = new FolderRequest("Source Code", null);

        when(projectRepository.findById(1L)).thenReturn(Optional.of(testProject));
        when(folderRepository.findRootByNameAndProjectIdIgnoreCase(1L, "Source Code")).thenReturn(Optional.empty());
        when(folderRepository.save(any(Folder.class))).thenAnswer(i -> {
            Folder f = i.getArgument(0);
            f.setId(30L);
            return f;
        });

        FolderResponse response = folderService.createFolder(1L, request, "admin@academic.com");

        assertNotNull(response);
        assertEquals("Source Code", response.getName());
        assertNull(response.getParentFolderId());
        verify(folderRepository, times(1)).save(any(Folder.class));
        verify(auditLogService, times(1)).log(eq("admin@academic.com"), eq("CREATE_FOLDER"), anyString());
    }

    @Test
    @DisplayName("Should prevent duplicate folder names in the same parent folder")
    void testPreventDuplicateFolderInSameParent() {
        FolderRequest request = new FolderRequest("SRS", 10L);

        when(projectRepository.findById(1L)).thenReturn(Optional.of(testProject));
        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(rootFolder));
        when(folderRepository.findChildByNameAndParentIdIgnoreCase(1L, "SRS", 10L)).thenReturn(Optional.of(subFolder));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () ->
                folderService.createFolder(1L, request, "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("already exists in the selected directory"));
        verify(folderRepository, never()).save(any(Folder.class));
    }

    @Test
    @DisplayName("Should build correct breadcrumb trail from leaf to root")
    void testBreadcrumbTrail() {
        Folder deepFolder = new Folder("Drafts", subFolder, testProject, "admin@academic.com");
        deepFolder.setId(30L);

        List<BreadcrumbDto> crumbs = folderService.buildBreadcrumbs(deepFolder);

        assertEquals(3, crumbs.size());
        assertEquals("Documentation", crumbs.get(0).getName());
        assertEquals(10L, crumbs.get(0).getId());
        assertEquals("SRS", crumbs.get(1).getName());
        assertEquals(20L, crumbs.get(1).getId());
        assertEquals("Drafts", crumbs.get(2).getName());
        assertEquals(30L, crumbs.get(2).getId());
    }

    @Test
    @DisplayName("Should prevent cycle: Folder cannot become its own parent")
    void testPreventSelfParenting() {
        FolderRequest request = new FolderRequest("Documentation", 10L);

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(rootFolder));

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, () ->
                folderService.updateFolder(1L, 10L, request, "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("cannot be its own parent"));
    }

    @Test
    @DisplayName("Should prevent cycle: Cannot move root folder into its own subfolder descendant")
    void testPreventCycleWithDescendant() {
        FolderRequest request = new FolderRequest("Documentation", 20L); // Moving root (10) into subfolder (20)

        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(rootFolder));
        when(folderRepository.findByIdAndProjectIdAndActiveTrue(20L, 1L)).thenReturn(Optional.of(subFolder));

        IllegalStateException ex = assertThrows(IllegalStateException.class, () ->
                folderService.updateFolder(1L, 10L, request, "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("cycle detected"));
    }

    @Test
    @DisplayName("Should reject deleting a folder containing files or subfolders")
    void testSafeFolderDeletion() {
        when(folderRepository.findByIdAndProjectIdAndActiveTrue(10L, 1L)).thenReturn(Optional.of(rootFolder));
        when(folderRepository.countByParentFolderIdAndActiveTrue(10L)).thenReturn(1L);
        when(assetRepository.countByFolderIdAndActiveTrue(10L)).thenReturn(3L);

        IllegalStateException ex = assertThrows(IllegalStateException.class, () ->
                folderService.deleteFolder(1L, 10L, "admin@academic.com")
        );

        assertTrue(ex.getMessage().contains("It contains 1 subfolder(s) and 3 file(s)"));
        verify(folderRepository, never()).save(argThat(f -> !f.isActive()));
    }
}
