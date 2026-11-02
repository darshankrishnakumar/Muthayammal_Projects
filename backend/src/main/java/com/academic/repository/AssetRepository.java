package com.academic.repository;

import com.academic.model.Asset;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssetRepository extends JpaRepository<Asset, Long> {

    List<Asset> findByFolderIdAndIsCurrentVersionTrueAndActiveTrue(Long folderId);

    @Query("SELECT a FROM Asset a WHERE a.folder.id = :folderId AND LOWER(a.originalFileName) = LOWER(:originalFileName) AND a.isCurrentVersion = true AND a.active = true")
    Optional<Asset> findActiveInFolderByOriginalFileName(@Param("folderId") Long folderId, @Param("originalFileName") String originalFileName);

    @Query("SELECT a FROM Asset a WHERE a.folder.id = :folderId AND LOWER(a.fileName) = LOWER(:fileName) AND a.isCurrentVersion = true AND a.active = true")
    Optional<Asset> findActiveInFolderByFileName(@Param("folderId") Long folderId, @Param("fileName") String fileName);

    Optional<Asset> findByIdAndActiveTrue(Long id);

    @Query("SELECT a FROM Asset a WHERE (a.id = :rootId OR a.parentAsset.id = :rootId) AND a.active = true ORDER BY a.versionNo DESC")
    List<Asset> findVersionHistoryByRootId(@Param("rootId") Long rootId);

    long countByFolderIdAndActiveTrue(Long folderId);

    @Query("SELECT a FROM Asset a WHERE a.folder.project.id = :projectId AND a.isCurrentVersion = true AND a.active = true")
    List<Asset> findCurrentAssetsByProjectId(@Param("projectId") Long projectId);
}
