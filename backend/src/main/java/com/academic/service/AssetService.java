package com.academic.service;

import com.academic.dto.AssetResponse;
import com.academic.dto.AssetVersionDto;
import com.academic.model.Asset;
import com.academic.model.Folder;
import com.academic.repository.AssetRepository;
import com.academic.repository.FolderRepository;
import com.academic.service.storage.FileStorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AssetService {

    private static final Logger logger = LoggerFactory.getLogger(AssetService.class);

    @Value("${academic.upload.max-file-size-bytes:52428800}") // 50 MB default
    private long maxFileSizeBytes;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private FolderRepository folderRepository;

    @Autowired
    private FileStorageService storageService;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private FolderService folderService;

    // Allowed File Extensions Whitelist
    private static final Set<String> ALLOWED_EXTENSIONS = new HashSet<>(Arrays.asList(
            // Documents
            "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "csv", "txt", "rtf", "md",
            // Images
            "png", "jpg", "jpeg", "gif", "svg", "webp", "bmp", "ico",
            // Video & Audio
            "mp4", "webm", "mkv", "mov", "avi", "mp3", "wav", "ogg", "aac", "m4a",
            // Archives
            "zip", "tar", "gz", "7z", "rar",
            // Source Code & Config
            "java", "js", "jsx", "ts", "tsx", "py", "c", "cpp", "h", "hpp", "cs", "go",
            "html", "htm", "css", "scss", "json", "xml", "yaml", "yml", "sql", "sh", "bat", "properties", "ipynb",
            // Databases
            "db", "sqlite", "sqlite3"
    ));

    /**
     * Upload a new asset to a project folder.
     */
    @Transactional
    public AssetResponse uploadAsset(Long projectId, Long folderId, MultipartFile file, String description, String actorEmail) {
        // Step 1: Access Control Chain
        accessControlService.validateWriteClearance(projectId);

        // Step 2: Validate Folder & Project Affiliation
        Folder folder = folderRepository.findByIdAndProjectIdAndActiveTrue(folderId, projectId)
                .orElseThrow(() -> new NoSuchElementException("Folder not found with ID: " + folderId + " in project ID: " + projectId));

        // Step 3: Server-side File Validation
        validateIncomingFile(file);

        String rawFilename = file.getOriginalFilename();
        String originalFilename = rawFilename != null ? StringUtils.cleanPath(rawFilename) : "unnamed_file";
        String extension = getFileExtension(originalFilename);
        String mimeType = detectMimeType(file.getContentType(), extension);
        long fileSize = file.getSize();

        // Step 4: Duplicate Check in same folder
        Optional<Asset> existingDuplicate = assetRepository.findActiveInFolderByOriginalFileName(folderId, originalFilename);
        if (existingDuplicate.isPresent()) {
            throw new IllegalArgumentException(String.format(
                    "A file named '%s' already exists in folder '%s'. To update this file, use the version replace feature.",
                    originalFilename, folder.getName()
            ));
        }

        // Step 5: Save to Private Storage
        String storagePath = null;
        try (InputStream inputStream = file.getInputStream()) {
            storagePath = storageService.storeFile(inputStream, originalFilename, projectId, folderId);
        } catch (IOException e) {
            throw new RuntimeException("Failed to read uploaded file payload: " + e.getMessage(), e);
        }

        // Step 6: Save Metadata in MySQL with Rollback Safety
        try {
            Asset asset = new Asset(
                    folder,
                    originalFilename,
                    originalFilename,
                    mimeType,
                    extension,
                    fileSize,
                    storagePath,
                    1,
                    true,
                    null,
                    description,
                    actorEmail
            );

            Asset saved = assetRepository.save(asset);

            auditLogService.log(
                    actorEmail,
                    "UPLOAD_FILE",
                    String.format("Uploaded asset '%s' (v1, %d bytes) to folder '%s' in project %s",
                            saved.getOriginalFileName(), saved.getFileSize(), folder.getName(), folder.getProject().getProjectCode())
            );

            return folderService.mapToAssetResponse(saved);
        } catch (Exception ex) {
            // Rollback Safety: Clean up physical file from storage if DB fails
            logger.error("DB persistence failed after file storage write. Executing storage rollback for: {}", storagePath, ex);
            storageService.deleteFile(storagePath);
            throw new RuntimeException("Database error saving asset metadata. File storage rolled back: " + ex.getMessage(), ex);
        }
    }

    /**
     * Replace an existing asset / Upload a new version (v1 -> v2).
     */
    @Transactional
    public AssetResponse replaceAsset(Long assetId, MultipartFile file, String changeNotes, String actorEmail) {
        Asset currentAsset = assetRepository.findByIdAndActiveTrue(assetId)
                .orElseThrow(() -> new NoSuchElementException("Asset not found with ID: " + assetId));

        Long projectId = currentAsset.getFolder().getProject().getId();
        accessControlService.validateWriteClearance(projectId);

        validateIncomingFile(file);

        String rawFilename = file.getOriginalFilename();
        String originalFilename = rawFilename != null ? StringUtils.cleanPath(rawFilename) : "unnamed_file";
        String extension = getFileExtension(originalFilename);
        String mimeType = detectMimeType(file.getContentType(), extension);
        long fileSize = file.getSize();

        // Determine root asset in the version chain
        Asset rootAsset = currentAsset.getParentAsset() != null ? currentAsset.getParentAsset() : currentAsset;

        // Save new version to private storage
        String storagePath = null;
        try (InputStream is = file.getInputStream()) {
            storagePath = storageService.storeFile(is, originalFilename, projectId, currentAsset.getFolder().getId());
        } catch (IOException e) {
            throw new RuntimeException("Failed to stream replacement file: " + e.getMessage(), e);
        }

        try {
            // Supersede current version
            currentAsset.setCurrentVersion(false);
            assetRepository.save(currentAsset);

            int newVersionNo = currentAsset.getVersionNo() + 1;
            String newDescription = changeNotes != null && !changeNotes.trim().isEmpty()
                    ? changeNotes.trim()
                    : "Updated version " + newVersionNo + " replacing " + currentAsset.getOriginalFileName();

            Asset newVersion = new Asset(
                    currentAsset.getFolder(),
                    originalFilename,
                    originalFilename,
                    mimeType,
                    extension,
                    fileSize,
                    storagePath,
                    newVersionNo,
                    true,
                    rootAsset,
                    newDescription,
                    actorEmail
            );

            Asset savedNewVersion = assetRepository.save(newVersion);

            auditLogService.log(
                    actorEmail,
                    "REPLACE_FILE_VERSION",
                    String.format("Uploaded new version (v%d) for asset '%s' (Root ID: %d)",
                            newVersionNo, savedNewVersion.getOriginalFileName(), rootAsset.getId())
            );

            return folderService.mapToAssetResponse(savedNewVersion);
        } catch (Exception ex) {
            logger.error("DB persistence failed during version replacement. Rolling back storage file: {}", storagePath, ex);
            storageService.deleteFile(storagePath);
            throw new RuntimeException("Failed to save new asset version in database: " + ex.getMessage(), ex);
        }
    }

    /**
     * Retrieve asset resource for secure streaming view.
     * Enforces the 4-tier server-side access check chain.
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getAssetForSecureView(Long assetId, Integer versionNo) {
        Asset asset = assetRepository.findByIdAndActiveTrue(assetId)
                .orElseThrow(() -> new NoSuchElementException("Asset not found with ID: " + assetId));

        // If specific version is requested and differs from this asset's version
        if (versionNo != null && !versionNo.equals(asset.getVersionNo())) {
            Asset rootAsset = asset.getParentAsset() != null ? asset.getParentAsset() : asset;
            List<Asset> versions = assetRepository.findVersionHistoryByRootId(rootAsset.getId());
            asset = versions.stream()
                    .filter(v -> v.getVersionNo().equals(versionNo))
                    .findFirst()
                    .orElseThrow(() -> new NoSuchElementException(String.format("Version %d not found for asset '%s'", versionNo, rootAsset.getOriginalFileName())));
        }

        // Server-Side Access Control Chain
        accessControlService.validateAssetAccess(asset);

        Resource resource = storageService.loadFileAsResource(asset.getStoragePath());

        Map<String, Object> result = new HashMap<>();
        result.put("resource", resource);
        result.put("asset", asset);
        result.put("mimeType", asset.getMimeType());
        result.put("fileName", asset.getOriginalFileName());
        result.put("fileSize", asset.getFileSize());

        return result;
    }

    /**
     * Get version history for an asset.
     */
    @Transactional(readOnly = true)
    public List<AssetVersionDto> getVersionHistory(Long assetId) {
        Asset asset = assetRepository.findByIdAndActiveTrue(assetId)
                .orElseThrow(() -> new NoSuchElementException("Asset not found with ID: " + assetId));

        accessControlService.validateAssetAccess(asset);

        Asset rootAsset = asset.getParentAsset() != null ? asset.getParentAsset() : asset;
        List<Asset> history = assetRepository.findVersionHistoryByRootId(rootAsset.getId());

        return history.stream()
                .map(a -> new AssetVersionDto(
                        a.getId(),
                        a.getVersionNo(),
                        a.getOriginalFileName(),
                        a.getFileSize(),
                        a.getMimeType(),
                        a.getUploadedBy(),
                        a.getCreatedAt(),
                        a.isCurrentVersion(),
                        a.getDescription()
                ))
                .collect(Collectors.toList());
    }

    /**
     * Restore a previous version to become the current active version.
     */
    @Transactional
    public AssetResponse restoreVersion(Long assetId, Integer targetVersionNo, String actorEmail) {
        Asset currentAsset = assetRepository.findByIdAndActiveTrue(assetId)
                .orElseThrow(() -> new NoSuchElementException("Asset not found with ID: " + assetId));

        Long projectId = currentAsset.getFolder().getProject().getId();
        accessControlService.validateWriteClearance(projectId);

        Asset rootAsset = currentAsset.getParentAsset() != null ? currentAsset.getParentAsset() : currentAsset;
        List<Asset> history = assetRepository.findVersionHistoryByRootId(rootAsset.getId());

        Asset targetAsset = history.stream()
                .filter(a -> a.getVersionNo().equals(targetVersionNo))
                .findFirst()
                .orElseThrow(() -> new NoSuchElementException(String.format("Version %d not found in asset history", targetVersionNo)));

        // Mark all versions as non-current, mark target as current
        for (Asset item : history) {
            item.setCurrentVersion(item.getId().equals(targetAsset.getId()));
            assetRepository.save(item);
        }

        auditLogService.log(
                actorEmail,
                "RESTORE_FILE_VERSION",
                String.format("Restored asset '%s' to version v%d", targetAsset.getOriginalFileName(), targetVersionNo)
        );

        return folderService.mapToAssetResponse(targetAsset);
    }

    /**
     * Server-side File Validation Rules
     */
    private void validateIncomingFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Upload rejected: File payload is empty.");
        }

        if (file.getSize() > maxFileSizeBytes) {
            throw new IllegalArgumentException(String.format(
                    "Upload rejected: File size (%d bytes) exceeds the maximum allowed threshold (%d bytes / %.1f MB).",
                    file.getSize(), maxFileSizeBytes, (double) maxFileSizeBytes / (1024 * 1024)
            ));
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.trim().isEmpty()) {
            throw new IllegalArgumentException("Upload rejected: Missing filename.");
        }

        if (originalFilename.contains("..") || originalFilename.contains("/") || originalFilename.contains("\\")) {
            throw new SecurityException("Upload rejected: Illegal path traversal sequence in filename.");
        }

        String extension = getFileExtension(originalFilename).toLowerCase();
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new IllegalArgumentException(String.format(
                    "Upload rejected: File type '.%s' is not supported. Please upload a valid document, image, media, archive, or code file.",
                    extension
            ));
        }
    }

    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == filename.length() - 1) {
            return "";
        }
        return filename.substring(lastDotIndex + 1);
    }

    private String detectMimeType(String contentType, String extension) {
        if (contentType != null && !contentType.equals("application/octet-stream") && !contentType.trim().isEmpty()) {
            return contentType;
        }

        switch (extension.toLowerCase()) {
            case "pdf": return "application/pdf";
            case "doc": return "application/msword";
            case "docx": return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
            case "ppt": return "application/vnd.ms-powerpoint";
            case "pptx": return "application/vnd.openxmlformats-officedocument.presentationml.presentation";
            case "xls": return "application/vnd.ms-excel";
            case "xlsx": return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
            case "png": return "image/png";
            case "jpg":
            case "jpeg": return "image/jpeg";
            case "gif": return "image/gif";
            case "svg": return "image/svg+xml";
            case "webp": return "image/webp";
            case "mp4": return "video/mp4";
            case "webm": return "video/webm";
            case "mp3": return "audio/mpeg";
            case "wav": return "audio/wav";
            case "ogg": return "audio/ogg";
            case "zip": return "application/zip";
            case "json": return "application/json";
            case "sql":
            case "txt":
            case "md":
            case "java":
            case "js":
            case "jsx":
            case "ts":
            case "tsx":
            case "py":
            case "c":
            case "cpp":
            case "html":
            case "css": return "text/plain";
            default: return "application/octet-stream";
        }
    }
}
