package com.academic.dto;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class FolderResponse {
    private Long id;
    private String name;
    private Long parentFolderId;
    private Long projectId;
    private String createdBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<BreadcrumbDto> breadcrumbs = new ArrayList<>();
    private List<FolderResponse> subFolders = new ArrayList<>();
    private List<AssetResponse> assets = new ArrayList<>();
    private boolean restricted = false;

    public FolderResponse() {}

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Long getParentFolderId() {
        return parentFolderId;
    }

    public void setParentFolderId(Long parentFolderId) {
        this.parentFolderId = parentFolderId;
    }

    public Long getProjectId() {
        return projectId;
    }

    public void setProjectId(Long projectId) {
        this.projectId = projectId;
    }

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
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

    public List<BreadcrumbDto> getBreadcrumbs() {
        return breadcrumbs;
    }

    public void setBreadcrumbs(List<BreadcrumbDto> breadcrumbs) {
        this.breadcrumbs = breadcrumbs;
    }

    public List<FolderResponse> getSubFolders() {
        return subFolders;
    }

    public void setSubFolders(List<FolderResponse> subFolders) {
        this.subFolders = subFolders;
    }

    public List<AssetResponse> getAssets() {
        return assets;
    }

    public void setAssets(List<AssetResponse> assets) {
        this.assets = assets;
    }

    public boolean isRestricted() {
        return restricted;
    }

    public void setRestricted(boolean restricted) {
        this.restricted = restricted;
    }
}
