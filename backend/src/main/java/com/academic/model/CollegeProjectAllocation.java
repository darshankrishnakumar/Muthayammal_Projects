package com.academic.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Grants a college access to one library project. The project and its files exist once;
 * allocations only reference them, so the same project can serve any number of colleges.
 */
@Entity
@Table(name = "college_project_allocations", uniqueConstraints = {
        @UniqueConstraint(name = "uk_college_project", columnNames = {"college_id", "project_id"})
}, indexes = {
        @Index(name = "idx_alloc_college_active", columnList = "college_id, active"),
        @Index(name = "idx_alloc_project", columnList = "project_id")
})
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class CollegeProjectAllocation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "college_id", nullable = false)
    private College college;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "project_id", nullable = false)
    @JsonIgnoreProperties({"developer", "reviewerAdmin", "hibernateLazyInitializer", "handler"})
    private Project project;

    /** College-specific price; null means the library list price applies. */
    @Column(name = "price_override", precision = 12, scale = 2)
    private BigDecimal priceOverride;

    @Column(nullable = false)
    private boolean active = true;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(name = "allocated_by", nullable = false, length = 150)
    private String allocatedBy;

    @Column(name = "allocated_at", nullable = false)
    private LocalDateTime allocatedAt;

    @Column(name = "revoked_by", length = 150)
    private String revokedBy;

    @Column(name = "revoked_at")
    private LocalDateTime revokedAt;

    public CollegeProjectAllocation() {}

    @PrePersist
    protected void onCreate() {
        if (allocatedAt == null) {
            allocatedAt = LocalDateTime.now();
        }
    }

    /** Price a student of this college pays. */
    @Transient
    public BigDecimal getEffectivePrice() {
        if (priceOverride != null) {
            return priceOverride;
        }
        return project != null ? project.getPrice() : null;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public College getCollege() {
        return college;
    }

    public void setCollege(College college) {
        this.college = college;
    }

    public Project getProject() {
        return project;
    }

    public void setProject(Project project) {
        this.project = project;
    }

    public BigDecimal getPriceOverride() {
        return priceOverride;
    }

    public void setPriceOverride(BigDecimal priceOverride) {
        this.priceOverride = priceOverride;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getAllocatedBy() {
        return allocatedBy;
    }

    public void setAllocatedBy(String allocatedBy) {
        this.allocatedBy = allocatedBy;
    }

    public LocalDateTime getAllocatedAt() {
        return allocatedAt;
    }

    public void setAllocatedAt(LocalDateTime allocatedAt) {
        this.allocatedAt = allocatedAt;
    }

    public String getRevokedBy() {
        return revokedBy;
    }

    public void setRevokedBy(String revokedBy) {
        this.revokedBy = revokedBy;
    }

    public LocalDateTime getRevokedAt() {
        return revokedAt;
    }

    public void setRevokedAt(LocalDateTime revokedAt) {
        this.revokedAt = revokedAt;
    }
}
