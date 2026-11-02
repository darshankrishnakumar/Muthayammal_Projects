package com.academic.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "admin_user_assignments", uniqueConstraints = {
    @UniqueConstraint(name = "uk_admin_user_assign", columnNames = {"admin_user_id", "assigned_user_id"})
})
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class AdminUserAssignment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "admin_user_id", nullable = false)
    @JsonIgnoreProperties({"password", "otpCode", "otpExpiry", "hibernateLazyInitializer", "handler"})
    private User adminUser;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "assigned_user_id", nullable = false)
    @JsonIgnoreProperties({"password", "otpCode", "otpExpiry", "hibernateLazyInitializer", "handler"})
    private User assignedUser;

    @Column(name = "assigned_by", nullable = false)
    private String assignedBy;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(name = "assigned_at", nullable = false, updatable = false)
    private LocalDateTime assignedAt = LocalDateTime.now();

    public AdminUserAssignment() {}

    public AdminUserAssignment(User adminUser, User assignedUser, String assignedBy, String notes) {
        this.adminUser = adminUser;
        this.assignedUser = assignedUser;
        this.assignedBy = assignedBy;
        this.notes = notes;
        this.assignedAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getAdminUser() {
        return adminUser;
    }

    public void setAdminUser(User adminUser) {
        this.adminUser = adminUser;
    }

    public User getAssignedUser() {
        return assignedUser;
    }

    public void setAssignedUser(User assignedUser) {
        this.assignedUser = assignedUser;
    }

    public String getAssignedBy() {
        return assignedBy;
    }

    public void setAssignedBy(String assignedBy) {
        this.assignedBy = assignedBy;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public LocalDateTime getAssignedAt() {
        return assignedAt;
    }

    public void setAssignedAt(LocalDateTime assignedAt) {
        this.assignedAt = assignedAt;
    }
}
