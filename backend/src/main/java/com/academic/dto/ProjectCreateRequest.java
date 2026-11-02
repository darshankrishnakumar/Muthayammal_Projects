package com.academic.dto;

import com.academic.model.ProjectStatus;

public class ProjectCreateRequest {
    private String projectName;
    private String description;
    private Double budget;
    private String technologyStack;
    private ProjectStatus status;
    private Long linkedRequirementId;

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Double getBudget() {
        return budget;
    }

    public void setBudget(Double budget) {
        this.budget = budget;
    }

    public String getTechnologyStack() {
        return technologyStack;
    }

    public void setTechnologyStack(String technologyStack) {
        this.technologyStack = technologyStack;
    }

    public ProjectStatus getStatus() {
        return status;
    }

    public void setStatus(ProjectStatus status) {
        this.status = status;
    }

    public Long getLinkedRequirementId() {
        return linkedRequirementId;
    }

    public void setLinkedRequirementId(Long linkedRequirementId) {
        this.linkedRequirementId = linkedRequirementId;
    }
}
