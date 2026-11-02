package com.academic.repository;

import com.academic.model.FilePermission;
import com.academic.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FilePermissionRepository extends JpaRepository<FilePermission, Long> {

    List<FilePermission> findByAssetId(Long assetId);

    Optional<FilePermission> findByAssetIdAndUserId(Long assetId, Long userId);

    Optional<FilePermission> findByAssetIdAndRole(Long assetId, Role role);

    @Query("SELECT fp FROM FilePermission fp WHERE fp.asset.id = :assetId AND (fp.user.id = :userId OR (fp.user IS NULL AND fp.role = :role))")
    List<FilePermission> findRelevantPermissions(@Param("assetId") Long assetId, @Param("userId") Long userId, @Param("role") Role role);

    void deleteByAssetId(Long assetId);
}
