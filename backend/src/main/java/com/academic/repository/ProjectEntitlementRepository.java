package com.academic.repository;

import com.academic.model.ProjectEntitlement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.Set;

@Repository
public interface ProjectEntitlementRepository extends JpaRepository<ProjectEntitlement, Long> {

    Optional<ProjectEntitlement> findByUserIdAndProjectId(Long userId, Long projectId);

    @Query("SELECT COUNT(e) > 0 FROM ProjectEntitlement e WHERE e.user.id = :userId AND e.project.id = :projectId AND e.active = true")
    boolean hasActive(@Param("userId") Long userId, @Param("projectId") Long projectId);

    @Query("SELECT e.project.id FROM ProjectEntitlement e WHERE e.user.id = :userId AND e.active = true")
    Set<Long> findActiveProjectIdsByUserId(@Param("userId") Long userId);

    @Query("SELECT e FROM ProjectEntitlement e JOIN FETCH e.project WHERE e.user.id = :userId AND e.active = true ORDER BY e.grantedAt DESC")
    List<ProjectEntitlement> findActiveByUserId(@Param("userId") Long userId);

    @Query("SELECT COUNT(e) FROM ProjectEntitlement e WHERE e.project.id = :projectId AND e.active = true")
    long countActiveByProjectId(@Param("projectId") Long projectId);
}
