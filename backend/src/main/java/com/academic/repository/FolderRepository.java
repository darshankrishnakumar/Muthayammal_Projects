package com.academic.repository;

import com.academic.model.Folder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FolderRepository extends JpaRepository<Folder, Long> {

    List<Folder> findByProjectIdAndActiveTrue(Long projectId);

    List<Folder> findByProjectIdAndParentFolderIsNullAndActiveTrue(Long projectId);

    List<Folder> findByParentFolderIdAndActiveTrue(Long parentFolderId);

    Optional<Folder> findByIdAndProjectIdAndActiveTrue(Long id, Long projectId);

    Optional<Folder> findByIdAndActiveTrue(Long id);

    @Query("SELECT f FROM Folder f WHERE f.project.id = :projectId AND LOWER(f.name) = LOWER(:name) AND f.parentFolder IS NULL AND f.active = true")
    Optional<Folder> findRootByNameAndProjectIdIgnoreCase(@Param("projectId") Long projectId, @Param("name") String name);

    @Query("SELECT f FROM Folder f WHERE f.project.id = :projectId AND LOWER(f.name) = LOWER(:name) AND f.parentFolder.id = :parentId AND f.active = true")
    Optional<Folder> findChildByNameAndParentIdIgnoreCase(@Param("projectId") Long projectId, @Param("name") String name, @Param("parentId") Long parentId);

    long countByParentFolderIdAndActiveTrue(Long parentFolderId);

    @Query("SELECT f FROM Folder f WHERE f.project.id = :projectId ORDER BY f.createdAt ASC")
    List<Folder> findAllByProjectId(@Param("projectId") Long projectId);
}
