package com.academic.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "projects")
public class Project {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "project_name", nullable = false)
    private String projectName;

    @Column(name = "project_code", unique = true, nullable = false)
    private String projectCode;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "budget", precision = 12, scale = 2)
    private java.math.BigDecimal budget;

    @Column(name = "advance_amount", precision = 12, scale = 2)
    private java.math.BigDecimal advanceAmount;

    @Column(name = "remaining_amount", precision = 12, scale = 2)
    private java.math.BigDecimal remainingAmount;

    @Column(name = "advance_payment_status", length = 50)
    private String advancePaymentStatus;

    @Column(name = "remaining_payment_status", length = 50)
    private String remainingPaymentStatus;

    @Column(name = "technology_stack")
    private String technologyStack;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ProjectStatus status = ProjectStatus.CREATED;

    @Enumerated(EnumType.STRING)
    @Column(name = "lifecycle_status", length = 50)
    private ProjectStatus lifecycleStatus = ProjectStatus.CREATED;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "developer_id")
    private User developer;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "reviewer_admin_id")
    private User reviewerAdmin;

    @Column(name = "linked_requirement_id")
    private Long linkedRequirementId;

    @Column(name = "is_marketplace", nullable = false)
    private boolean isMarketplace = false;

    @Column(name = "purchased_by_user_id")
    private Long purchasedByUserId;

    @Column(name = "review_notes", columnDefinition = "TEXT")
    private String reviewNotes;

    @Column(name = "change_request_notes", columnDefinition = "TEXT")
    private String changeRequestNotes;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "created_by")
    private String createdBy;

    @Column(name = "updated_by")
    private String updatedBy;

    public Project() {}

    public Project(String projectName, String projectCode, String description, java.math.BigDecimal budget, 
                   String technologyStack, ProjectStatus status, Long linkedRequirementId, String createdBy) {
        this.projectName = projectName;
        this.projectCode = projectCode;
        this.description = description;
        this.budget = budget;
        this.technologyStack = technologyStack;
        this.status = status != null ? status : ProjectStatus.CREATED;
        this.lifecycleStatus = this.status;
        this.linkedRequirementId = linkedRequirementId;
        this.createdBy = createdBy;
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

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getProjectCode() {
        return projectCode;
    }

    public void setProjectCode(String projectCode) {
        this.projectCode = projectCode;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public java.math.BigDecimal getBudget() {
        return budget;
    }

    public void setBudget(java.math.BigDecimal budget) {
        this.budget = budget;
    }

    public java.math.BigDecimal getAdvanceAmount() {
        return advanceAmount;
    }

    public void setAdvanceAmount(java.math.BigDecimal advanceAmount) {
        this.advanceAmount = advanceAmount;
    }

    public java.math.BigDecimal getRemainingAmount() {
        return remainingAmount;
    }

    public void setRemainingAmount(java.math.BigDecimal remainingAmount) {
        this.remainingAmount = remainingAmount;
    }

    public String getAdvancePaymentStatus() {
        return advancePaymentStatus;
    }

    public void setAdvancePaymentStatus(String advancePaymentStatus) {
        this.advancePaymentStatus = advancePaymentStatus;
    }

    public String getRemainingPaymentStatus() {
        return remainingPaymentStatus;
    }

    public void setRemainingPaymentStatus(String remainingPaymentStatus) {
        this.remainingPaymentStatus = remainingPaymentStatus;
    }

    public ProjectStatus getLifecycleStatus() {
        return lifecycleStatus;
    }

    public void setLifecycleStatus(ProjectStatus lifecycleStatus) {
        this.lifecycleStatus = lifecycleStatus;
    }

    public User getDeveloper() {
        return developer;
    }

    public void setDeveloper(User developer) {
        this.developer = developer;
    }

    public User getReviewerAdmin() {
        return reviewerAdmin;
    }

    public void setReviewerAdmin(User reviewerAdmin) {
        this.reviewerAdmin = reviewerAdmin;
    }

    public boolean isMarketplace() {
        return isMarketplace;
    }

    public void setMarketplace(boolean marketplace) {
        isMarketplace = marketplace;
    }

    public Long getPurchasedByUserId() {
        return purchasedByUserId;
    }

    public void setPurchasedByUserId(Long purchasedByUserId) {
        this.purchasedByUserId = purchasedByUserId;
    }

    public String getReviewNotes() {
        return reviewNotes;
    }

    public void setReviewNotes(String reviewNotes) {
        this.reviewNotes = reviewNotes;
    }

    public String getChangeRequestNotes() {
        return changeRequestNotes;
    }

    public void setChangeRequestNotes(String changeRequestNotes) {
        this.changeRequestNotes = changeRequestNotes;
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

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }

    public String getUpdatedBy() {
        return updatedBy;
    }

    public void setUpdatedBy(String updatedBy) {
        this.updatedBy = updatedBy;
    }
}
