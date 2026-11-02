package com.academic.repository;

import com.academic.model.ProjectAssignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProjectAssignmentRepository extends JpaRepository<ProjectAssignment, Long> {

    List<ProjectAssignment> findByProjectId(Long projectId);

    List<ProjectAssignment> findByUserId(Long userId);

    @Query("SELECT pa FROM ProjectAssignment pa WHERE pa.project.id = :projectId AND pa.user.id = :userId AND pa.active = true AND (pa.expiredAt IS NULL OR pa.expiredAt > CURRENT_TIMESTAMP)")
    Optional<ProjectAssignment> findActiveAssignment(@Param("projectId") Long projectId, @Param("userId") Long userId);

    @Query("SELECT pa FROM ProjectAssignment pa WHERE pa.project.id = :projectId AND pa.active = true")
    List<ProjectAssignment> findActiveAssignmentsByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT pa FROM ProjectAssignment pa WHERE pa.user.id = :userId AND pa.active = true")
    List<ProjectAssignment> findActiveAssignmentsByUserId(@Param("userId") Long userId);

    Optional<ProjectAssignment> findByProjectIdAndId(Long projectId, Long id);

    Optional<ProjectAssignment> findByProjectIdAndUserId(Long projectId, Long userId);

    boolean existsByProjectIdAndUserIdAndActiveTrue(Long projectId, Long userId);
}
