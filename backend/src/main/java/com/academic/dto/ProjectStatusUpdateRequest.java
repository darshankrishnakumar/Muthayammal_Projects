package com.academic.dto;

import com.academic.model.ProjectStatus;

public class ProjectStatusUpdateRequest {
    private ProjectStatus status;

    public ProjectStatus getStatus() {
        return status;
    }

    public void setStatus(ProjectStatus status) {
        this.status = status;
    }
}
