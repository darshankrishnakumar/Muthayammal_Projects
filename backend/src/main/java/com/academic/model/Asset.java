package com.academic.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "asset_master")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Asset {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "folder_id", nullable = false)
    @JsonIgnore
    private Folder folder;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "original_file_name", nullable = false)
    private String originalFileName;

    @Column(name = "mime_type", nullable = false, length = 150)
    private String mimeType;

    @Column(nullable = false, length = 50)
    private String extension;

    @Column(name = "file_size", nullable = false)
    private Long fileSize;

    @Column(name = "storage_path", nullable = false, length = 500)
    @JsonIgnore
    private String storagePath;

    @Column(name = "version_no", nullable = false)
    private Integer versionNo = 1;

    @Column(name = "is_current_version", nullable = false)
    private boolean isCurrentVersion = true;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_asset_id")
    @JsonIgnore
    private Asset parentAsset;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "uploaded_by", nullable = false)
    private String uploadedBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(nullable = false)
    private boolean active = true;

    public Asset() {}

    public Asset(Folder folder, String fileName, String originalFileName, String mimeType,
                 String extension, Long fileSize, String storagePath, Integer versionNo,
                 boolean isCurrentVersion, Asset parentAsset, String description, String uploadedBy) {
        this.folder = folder;
        this.fileName = fileName;
        this.originalFileName = originalFileName;
        this.mimeType = mimeType;
        this.extension = extension;
        this.fileSize = fileSize;
        this.storagePath = storagePath;
        this.versionNo = versionNo != null ? versionNo : 1;
        this.isCurrentVersion = isCurrentVersion;
        this.parentAsset = parentAsset;
        this.description = description;
        this.uploadedBy = uploadedBy;
        this.active = true;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Folder getFolder() {
        return folder;
    }

    public void setFolder(Folder folder) {
        this.folder = folder;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getOriginalFileName() {
        return originalFileName;
    }

    public void setOriginalFileName(String originalFileName) {
        this.originalFileName = originalFileName;
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType;
    }

    public String getExtension() {
        return extension;
    }

    public void setExtension(String extension) {
        this.extension = extension;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public String getStoragePath() {
        return storagePath;
    }

    public void setStoragePath(String storagePath) {
        this.storagePath = storagePath;
    }

    public Integer getVersionNo() {
        return versionNo;
    }

    public void setVersionNo(Integer versionNo) {
        this.versionNo = versionNo;
    }

    public boolean isCurrentVersion() {
        return isCurrentVersion;
    }

    public void setCurrentVersion(boolean currentVersion) {
        isCurrentVersion = currentVersion;
    }

    public Asset getParentAsset() {
        return parentAsset;
    }

    public void setParentAsset(Asset parentAsset) {
        this.parentAsset = parentAsset;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getUploadedBy() {
        return uploadedBy;
    }

    public void setUploadedBy(String uploadedBy) {
        this.uploadedBy = uploadedBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }
}
