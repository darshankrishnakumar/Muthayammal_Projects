package com.academic.repository;

import com.academic.model.FolderPermission;
import com.academic.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FolderPermissionRepository extends JpaRepository<FolderPermission, Long> {

    List<FolderPermission> findByFolderId(Long folderId);

    Optional<FolderPermission> findByFolderIdAndUserId(Long folderId, Long userId);

    Optional<FolderPermission> findByFolderIdAndRole(Long folderId, Role role);

    @Query("SELECT fp FROM FolderPermission fp WHERE fp.folder.id = :folderId AND (fp.user.id = :userId OR (fp.user IS NULL AND fp.role = :role))")
    List<FolderPermission> findRelevantPermissions(@Param("folderId") Long folderId, @Param("userId") Long userId, @Param("role") Role role);

    void deleteByFolderId(Long folderId);
}
