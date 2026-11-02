package com.academic.service;

import com.academic.dto.AssetResponse;
import com.academic.dto.BreadcrumbDto;
import com.academic.dto.FolderRequest;
import com.academic.dto.FolderResponse;
import com.academic.model.Asset;
import com.academic.model.Folder;
import com.academic.model.Project;
import com.academic.model.User;
import com.academic.repository.AssetRepository;
import com.academic.repository.FolderRepository;
import com.academic.repository.ProjectRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@SuppressWarnings("null")
public class FolderService {

    private static final Logger logger = LoggerFactory.getLogger(FolderService.class);

    @Autowired
    private FolderRepository folderRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private AuditLogService auditLogService;

    /**
     * Retrieve all root folders and nested structure for a project.
     */
    @Transactional(readOnly = true)
    public List<FolderResponse> getProjectFolders(Long projectId) {
        accessControlService.validateProjectAccess(projectId);

        List<Folder> rootFolders = folderRepository.findByProjectIdAndParentFolderIsNullAndActiveTrue(projectId);
        return rootFolders.stream()
                .map(this::mapToFolderResponseWithChildren)
                .collect(Collectors.toList());
    }

    /**
     * Retrieve single folder details with breadcrumbs, subfolders, and assets.
     */
    @Transactional(readOnly = true)
    public FolderResponse getFolderDetails(Long projectId, Long folderId) {
        accessControlService.validateProjectAccess(projectId);

        Folder folder = folderRepository.findByIdAndProjectIdAndActiveTrue(folderId, projectId)
                .orElseThrow(() -> new NoSuchElementException("Folder not found with ID: " + folderId + " in project " + projectId));

        return mapToFolderResponseWithChildren(folder);
    }

    /**
     * Create a new folder (root or nested).
     */
    @Transactional
    public FolderResponse createFolder(Long projectId, FolderRequest request, String actorEmail) {
        accessControlService.validateWriteClearance(projectId);

        if (request.getName() == null || request.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("Folder name cannot be empty.");
        }

        String folderName = request.getName().trim();
        validateFolderNameCharacters(folderName);

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));

        Folder parentFolder = null;
        if (request.getParentFolderId() != null) {
            parentFolder = folderRepository.findByIdAndProjectIdAndActiveTrue(request.getParentFolderId(), projectId)
                    .orElseThrow(() -> new NoSuchElementException("Parent folder not found with ID: " + request.getParentFolderId() + " in project " + projectId));

            // Check duplicate name in parent folder
            Optional<Folder> existing = folderRepository.findChildByNameAndParentIdIgnoreCase(projectId, folderName, parentFolder.getId());
            if (existing.isPresent()) {
                throw new IllegalArgumentException("A folder named '" + folderName + "' already exists in the selected directory.");
            }
        } else {
            // Check duplicate root folder
            Optional<Folder> existing = folderRepository.findRootByNameAndProjectIdIgnoreCase(projectId, folderName);
            if (existing.isPresent()) {
                throw new IllegalArgumentException("A root folder named '" + folderName + "' already exists in project " + project.getProjectCode() + ".");
            }
        }

        Folder folder = new Folder(folderName, parentFolder, project, actorEmail);
        Folder saved = folderRepository.save(folder);

        auditLogService.log(
                actorEmail,
                "CREATE_FOLDER",
                String.format("Created folder '%s' (ID: %d) in project %s", saved.getName(), saved.getId(), project.getProjectCode())
        );

        return mapToFolderResponseWithChildren(saved);
    }

    /**
     * Rename or move a folder.
     */
    @Transactional
    public FolderResponse updateFolder(Long projectId, Long folderId, FolderRequest request, String actorEmail) {
        accessControlService.validateWriteClearance(projectId);

        Folder folder = folderRepository.findByIdAndProjectIdAndActiveTrue(folderId, projectId)
                .orElseThrow(() -> new NoSuchElementException("Folder not found with ID: " + folderId));

        if (request.getName() != null && !request.getName().trim().isEmpty()) {
            String newName = request.getName().trim();
            validateFolderNameCharacters(newName);

            // Duplicate check
            if (folder.getParentFolder() != null) {
                folderRepository.findChildByNameAndParentIdIgnoreCase(projectId, newName, folder.getParentFolder().getId())
                        .ifPresent(dup -> {
                            if (!dup.getId().equals(folder.getId())) {
                                throw new IllegalArgumentException("A folder named '" + newName + "' already exists in this directory.");
                            }
                        });
            } else {
                folderRepository.findRootByNameAndProjectIdIgnoreCase(projectId, newName)
                        .ifPresent(dup -> {
                            if (!dup.getId().equals(folder.getId())) {
                                throw new IllegalArgumentException("A root folder named '" + newName + "' already exists.");
                            }
                        });
            }
            folder.setName(newName);
        }

        // Handle moving folder (prevent cycles)
        if (request.getParentFolderId() != null) {
            if (request.getParentFolderId().equals(folder.getId())) {
                throw new IllegalArgumentException("A folder cannot be its own parent.");
            }

            Folder newParent = folderRepository.findByIdAndProjectIdAndActiveTrue(request.getParentFolderId(), projectId)
                    .orElseThrow(() -> new NoSuchElementException("New parent folder not found with ID: " + request.getParentFolderId()));

            // Cycle detection: Verify newParent is not a descendant of folder
            if (isDescendantOf(newParent, folder)) {
                throw new IllegalStateException("Invalid hierarchy: Cannot move a folder inside one of its own subfolders (cycle detected).");
            }

            folder.setParentFolder(newParent);
        }

        Folder updated = folderRepository.save(folder);

        auditLogService.log(
                actorEmail,
                "UPDATE_FOLDER",
                String.format("Updated folder '%s' (ID: %d) in project %s", updated.getName(), updated.getId(), updated.getProject().getProjectCode())
        );

        return mapToFolderResponseWithChildren(updated);
    }

    /**
     * Safe folder deactivation/deletion.
     */
    @Transactional
    public void deleteFolder(Long projectId, Long folderId, String actorEmail) {
        accessControlService.validateWriteClearance(projectId);

        Folder folder = folderRepository.findByIdAndProjectIdAndActiveTrue(folderId, projectId)
                .orElseThrow(() -> new NoSuchElementException("Folder not found with ID: " + folderId));

        long childFolderCount = folderRepository.countByParentFolderIdAndActiveTrue(folderId);
        long assetCount = assetRepository.countByFolderIdAndActiveTrue(folderId);

        if (childFolderCount > 0 || assetCount > 0) {
            throw new IllegalStateException(String.format(
                    "Cannot delete folder '%s': It contains %d subfolder(s) and %d file(s). Please empty or move its contents first.",
                    folder.getName(), childFolderCount, assetCount
            ));
        }

        folder.setActive(false);
        folderRepository.save(folder);

        auditLogService.log(
                actorEmail,
                "DELETE_FOLDER",
                String.format("Deactivated folder '%s' (ID: %d) in project %s", folder.getName(), folder.getId(), folder.getProject().getProjectCode())
        );
    }

    /**
     * Checks whether candidate is a descendant of ancestor (cycle prevention).
     */
    public boolean isDescendantOf(Folder candidate, Folder ancestor) {
        Folder current = candidate;
        while (current != null) {
            if (current.getId().equals(ancestor.getId())) {
                return true;
            }
            current = current.getParentFolder();
        }
        return false;
    }

    /**
     * Builds breadcrumb path from root to target folder.
     */
    public List<BreadcrumbDto> buildBreadcrumbs(Folder folder) {
        List<BreadcrumbDto> crumbs = new ArrayList<>();
        Folder current = folder;
        while (current != null) {
            crumbs.add(0, new BreadcrumbDto(current.getId(), current.getName()));
            current = current.getParentFolder();
        }
        return crumbs;
    }

    /**
     * Initialize standard academic folder tree:
     * - Documentation (SRS, Design, Reports)
     * - Source Code (Frontend, Backend)
     * - Database (SQL)
     * - Resources (Images, Videos, References)
     */
    @Transactional
    public void initializeDefaultFolders(Long projectId, String actorEmail) {
        Project project = projectRepository.findById(projectId).orElse(null);
        if (project == null) return;

        List<String> defaultFolders = Arrays.asList("Documentation", "Source Code", "Database", "Demo Video", "Screenshots", "Presentation", "Resources");

        for (String folderName : defaultFolders) {
            Optional<Folder> existing = folderRepository.findByProjectIdAndParentFolderIsNullAndActiveTrue(projectId)
                    .stream()
                    .filter(f -> f.getName().equalsIgnoreCase(folderName))
                    .findFirst();

            if (existing.isEmpty()) {
                Folder root = new Folder(folderName, null, project, actorEmail);
                folderRepository.save(root);
            }
        }
        logger.info("Initialized standard default folders {} for project ID: {}", defaultFolders, projectId);
    }

    private FolderResponse mapToFolderResponseWithChildren(Folder folder) {
        User currentUser = accessControlService.getCurrentAuthenticatedUser();
        return mapToFolderResponseWithChildren(folder, currentUser,
                accessControlService.getAccessLevel(folder.getProject(), currentUser));
    }

    private FolderResponse mapToFolderResponseWithChildren(Folder folder, User currentUser, AccessControlService.ProjectAccessLevel level) {
        boolean folderAllowed = accessControlService.isFolderAllowed(folder, currentUser);

        FolderResponse response = new FolderResponse();
        response.setId(folder.getId());
        response.setName(folder.getName());
        response.setParentFolderId(folder.getParentFolder() != null ? folder.getParentFolder().getId() : null);
        response.setProjectId(folder.getProject() != null ? folder.getProject().getId() : null);
        response.setCreatedBy(folder.getCreatedBy());
        response.setCreatedAt(folder.getCreatedAt());
        response.setUpdatedAt(folder.getUpdatedAt());
        response.setBreadcrumbs(buildBreadcrumbs(folder));
        response.setRestricted(!folderAllowed);

        // Subfolders
        List<Folder> childFolders = folderRepository.findByParentFolderIdAndActiveTrue(folder.getId());
        response.setSubFolders(childFolders.stream()
                .map(child -> mapToFolderResponseWithChildren(child, currentUser, level))
                .collect(Collectors.toList()));

        // Current active files in this folder (filter to accessible only for non-superadmin)
        List<Asset> assets = assetRepository.findByFolderIdAndIsCurrentVersionTrueAndActiveTrue(folder.getId());
        List<AssetResponse> mappedAssets = new ArrayList<>();

        for (Asset asset : assets) {
            boolean assetAllowed = accessControlService.isAssetAllowed(asset, currentUser, level);
            AssetResponse resp = mapToAssetResponse(asset, assetAllowed);

            // If folder is restricted or asset is restricted, still return mapped item with restricted=true so UI can show 🔒 or filter
            mappedAssets.add(resp);
        }

        response.setAssets(mappedAssets);
        return response;
    }

    public AssetResponse mapToAssetResponse(Asset asset) {
        User currentUser = accessControlService.getCurrentAuthenticatedUser();
        return mapToAssetResponse(asset, accessControlService.isAssetAllowed(asset, currentUser));
    }

    public AssetResponse mapToAssetResponse(Asset asset, boolean assetAllowed) {
        AssetResponse resp = new AssetResponse();
        resp.setId(asset.getId());
        resp.setFolderId(asset.getFolder() != null ? asset.getFolder().getId() : null);
        resp.setProjectId(asset.getFolder() != null && asset.getFolder().getProject() != null ? asset.getFolder().getProject().getId() : null);
        resp.setFileName(asset.getFileName());
        resp.setOriginalFileName(asset.getOriginalFileName());
        resp.setMimeType(asset.getMimeType());
        resp.setExtension(asset.getExtension());
        resp.setFileSize(asset.getFileSize());
        resp.setVersionNo(asset.getVersionNo());
        resp.setCurrentVersion(asset.isCurrentVersion());
        resp.setDescription(asset.getDescription());
        resp.setUploadedBy(asset.getUploadedBy());
        resp.setCreatedAt(asset.getCreatedAt());
        resp.setUpdatedAt(asset.getUpdatedAt());
        resp.setRestricted(!assetAllowed);
        resp.setCategory(asset.getCategory() != null ? asset.getCategory().name() : null);
        resp.setPreviewable(asset.isPreviewable());
        return resp;
    }

    private void validateFolderNameCharacters(String name) {
        if (name.contains("/") || name.contains("\\") || name.contains(":") || name.contains("*") ||
            name.contains("?") || name.contains("\"") || name.contains("<") || name.contains(">") || name.contains("|")) {
            throw new IllegalArgumentException("Folder name cannot contain special path characters (/ \\ : * ? \" < > |).");
        }
        if (name.length() > 100) {
            throw new IllegalArgumentException("Folder name cannot exceed 100 characters.");
        }
    }
}
