package com.academic.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "requirements", indexes = {
    @Index(name = "idx_req_user_id", columnList = "user_id"),
    @Index(name = "idx_req_status", columnList = "status"),
    @Index(name = "idx_req_user_status", columnList = "user_id, status")
})
public class Requirement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String title;

    @Column(name = "problem_statement", columnDefinition = "TEXT", nullable = false)
    private String problemStatement;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(precision = 12, scale = 2)
    private BigDecimal budget;

    @Column(name = "technology_stack")
    private String technologyStack;

    @Column(name = "image_url", columnDefinition = "LONGTEXT")
    private String imageUrl;

    @Column(name = "audio_url", columnDefinition = "LONGTEXT")
    private String audioUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RequirementStatus status;

    @Column(name = "advance_amount", precision = 12, scale = 2)
    private BigDecimal advanceAmount;

    @Column(name = "remaining_amount", precision = 12, scale = 2)
    private BigDecimal remainingAmount;

    @Column(name = "advance_payment_status", length = 50)
    private String advancePaymentStatus = "PENDING";

    @Column(name = "remaining_payment_status", length = 50)
    private String remainingPaymentStatus = "PENDING";

    @Column(name = "super_admin_notes", columnDefinition = "TEXT")
    private String superAdminNotes;

    /** College of the requesting student, captured at creation for college-scoped queries. */
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "college_id")
    private College college;

    @Column(name = "college_admin_notes", columnDefinition = "TEXT")
    private String collegeAdminNotes;

    @Column(name = "forwarded_by", length = 150)
    private String forwardedBy;

    @Column(name = "forwarded_at")
    private LocalDateTime forwardedAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public Requirement() {}

    public Requirement(User user, String title, String problemStatement, String description, BigDecimal budget, String technologyStack) {
        this.user = user;
        this.title = title;
        this.problemStatement = problemStatement;
        this.description = description;
        this.budget = budget;
        this.technologyStack = technologyStack;
        this.status = RequirementStatus.DRAFT;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = RequirementStatus.DRAFT;
        }
        if (description == null) {
            description = "";
        }
        if (problemStatement == null) {
            problemStatement = "";
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
        if (description == null) {
            description = "";
        }
        if (problemStatement == null) {
            problemStatement = "";
        }
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getProblemStatement() {
        return problemStatement;
    }

    public void setProblemStatement(String problemStatement) {
        this.problemStatement = problemStatement;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public BigDecimal getBudget() {
        return budget;
    }

    public void setBudget(BigDecimal budget) {
        this.budget = budget;
    }

    public String getTechnologyStack() {
        return technologyStack;
    }

    public void setTechnologyStack(String technologyStack) {
        this.technologyStack = technologyStack;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getAudioUrl() {
        return audioUrl;
    }

    public void setAudioUrl(String audioUrl) {
        this.audioUrl = audioUrl;
    }

    public RequirementStatus getStatus() {
        return status;
    }

    public void setStatus(RequirementStatus status) {
        this.status = status;
    }

    public BigDecimal getAdvanceAmount() {
        return advanceAmount;
    }

    public void setAdvanceAmount(BigDecimal advanceAmount) {
        this.advanceAmount = advanceAmount;
    }

    public BigDecimal getRemainingAmount() {
        return remainingAmount;
    }

    public void setRemainingAmount(BigDecimal remainingAmount) {
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

    public String getSuperAdminNotes() {
        return superAdminNotes;
    }

    public void setSuperAdminNotes(String superAdminNotes) {
        this.superAdminNotes = superAdminNotes;
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

    public College getCollege() {
        return college;
    }

    public void setCollege(College college) {
        this.college = college;
    }

    public String getCollegeAdminNotes() {
        return collegeAdminNotes;
    }

    public void setCollegeAdminNotes(String collegeAdminNotes) {
        this.collegeAdminNotes = collegeAdminNotes;
    }

    public String getForwardedBy() {
        return forwardedBy;
    }

    public void setForwardedBy(String forwardedBy) {
        this.forwardedBy = forwardedBy;
    }

    public LocalDateTime getForwardedAt() {
        return forwardedAt;
    }

    public void setForwardedAt(LocalDateTime forwardedAt) {
        this.forwardedAt = forwardedAt;
    }
}
