package com.academic.dto;

import java.time.LocalDateTime;

public class AssetVersionDto {
    private Long id;
    private Integer versionNo;
    private String originalFileName;
    private Long fileSize;
    private String mimeType;
    private String uploadedBy;
    private LocalDateTime createdAt;
    private boolean currentVersion;
    private String description;

    public AssetVersionDto() {}

    public AssetVersionDto(Long id, Integer versionNo, String originalFileName, Long fileSize,
                           String mimeType, String uploadedBy, LocalDateTime createdAt,
                           boolean currentVersion, String description) {
        this.id = id;
        this.versionNo = versionNo;
        this.originalFileName = originalFileName;
        this.fileSize = fileSize;
        this.mimeType = mimeType;
        this.uploadedBy = uploadedBy;
        this.createdAt = createdAt;
        this.currentVersion = currentVersion;
        this.description = description;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getVersionNo() {
        return versionNo;
    }

    public void setVersionNo(Integer versionNo) {
        this.versionNo = versionNo;
    }

    public String getOriginalFileName() {
        return originalFileName;
    }

    public void setOriginalFileName(String originalFileName) {
        this.originalFileName = originalFileName;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType;
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

    public boolean isCurrentVersion() {
        return currentVersion;
    }

    public void setCurrentVersion(boolean currentVersion) {
        this.currentVersion = currentVersion;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
