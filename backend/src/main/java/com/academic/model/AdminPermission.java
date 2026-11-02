package com.academic.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "admin_permissions", uniqueConstraints = {
    @UniqueConstraint(name = "uk_admin_permission_key", columnNames = {"admin_user_id", "permission_key"})
})
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class AdminPermission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "admin_user_id", nullable = false)
    @JsonIgnoreProperties({"password", "otpCode", "otpExpiry", "hibernateLazyInitializer", "handler"})
    private User adminUser;

    @Enumerated(EnumType.STRING)
    @Column(name = "permission_key", nullable = false, length = 100)
    private PermissionKey permissionKey;

    @Enumerated(EnumType.STRING)
    @Column(name = "data_scope", nullable = false, length = 50)
    private DataScope dataScope = DataScope.GLOBAL;

    @Column(name = "granted_by", nullable = false)
    private String grantedBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    public AdminPermission() {}

    public AdminPermission(User adminUser, PermissionKey permissionKey, DataScope dataScope, String grantedBy) {
        this.adminUser = adminUser;
        this.permissionKey = permissionKey;
        this.dataScope = dataScope != null ? dataScope : DataScope.GLOBAL;
        this.grantedBy = grantedBy;
        this.createdAt = LocalDateTime.now();
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

    public PermissionKey getPermissionKey() {
        return permissionKey;
    }

    public void setPermissionKey(PermissionKey permissionKey) {
        this.permissionKey = permissionKey;
    }

    public DataScope getDataScope() {
        return dataScope;
    }

    public void setDataScope(DataScope dataScope) {
        this.dataScope = dataScope;
    }

    public String getGrantedBy() {
        return grantedBy;
    }

    public void setGrantedBy(String grantedBy) {
        this.grantedBy = grantedBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
