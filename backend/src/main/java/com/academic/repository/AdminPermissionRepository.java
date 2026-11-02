package com.academic.repository;

import com.academic.model.AdminPermission;
import com.academic.model.PermissionKey;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AdminPermissionRepository extends JpaRepository<AdminPermission, Long> {

    List<AdminPermission> findByAdminUserId(Long adminUserId);

    Optional<AdminPermission> findByAdminUserIdAndPermissionKey(Long adminUserId, PermissionKey permissionKey);

    boolean existsByAdminUserIdAndPermissionKey(Long adminUserId, PermissionKey permissionKey);

    void deleteByAdminUserId(Long adminUserId);
}
