package com.academic.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Full access to a project's protected deliverables for one user. Created only from a
 * verified payment, a delivered custom project, or an explicit Super Admin grant.
 */
@Entity
@Table(name = "project_entitlements", uniqueConstraints = {
        @UniqueConstraint(name = "uk_entitlement_user_project", columnNames = {"user_id", "project_id"})
}, indexes = {
        @Index(name = "idx_entitlement_project", columnList = "project_id")
})
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ProjectEntitlement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonIgnoreProperties({"password", "otpCode", "otpExpiry", "hibernateLazyInitializer", "handler"})
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    @JsonIgnoreProperties({"developer", "reviewerAdmin", "hibernateLazyInitializer", "handler"})
    private Project project;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private EntitlementSource source;

    @Column(name = "order_id")
    private Long orderId;

    @Column(nullable = false)
    private boolean active = true;

    @Column(name = "granted_by", nullable = false, length = 150)
    private String grantedBy;

    @Column(name = "granted_at", nullable = false)
    private LocalDateTime grantedAt;

    @Column(name = "revoked_at")
    private LocalDateTime revokedAt;

    public ProjectEntitlement() {}

    public ProjectEntitlement(User user, Project project, EntitlementSource source, Long orderId, String grantedBy) {
        this.user = user;
        this.project = project;
        this.source = source;
        this.orderId = orderId;
        this.grantedBy = grantedBy;
        this.active = true;
    }

    @PrePersist
    protected void onCreate() {
        if (grantedAt == null) {
            grantedAt = LocalDateTime.now();
        }
    }

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

    public Project getProject() {
        return project;
    }

    public void setProject(Project project) {
        this.project = project;
    }

    public EntitlementSource getSource() {
        return source;
    }

    public void setSource(EntitlementSource source) {
        this.source = source;
    }

    public Long getOrderId() {
        return orderId;
    }

    public void setOrderId(Long orderId) {
        this.orderId = orderId;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public String getGrantedBy() {
        return grantedBy;
    }

    public void setGrantedBy(String grantedBy) {
        this.grantedBy = grantedBy;
    }

    public LocalDateTime getGrantedAt() {
        return grantedAt;
    }

    public void setGrantedAt(LocalDateTime grantedAt) {
        this.grantedAt = grantedAt;
    }

    public LocalDateTime getRevokedAt() {
        return revokedAt;
    }

    public void setRevokedAt(LocalDateTime revokedAt) {
        this.revokedAt = revokedAt;
    }
}
