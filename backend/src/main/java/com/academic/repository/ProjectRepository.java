package com.academic.repository;

import com.academic.model.Project;
import com.academic.model.ProjectStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {

    Optional<Project> findByProjectCode(String projectCode);

    Optional<Project> findByLinkedRequirementId(Long linkedRequirementId);

    List<Project> findByDeveloperId(Long developerId);

    List<Project> findByReviewerAdminId(Long reviewerAdminId);

    List<Project> findByIsMarketplaceTrue();

    List<Project> findByPurchasedByUserId(Long purchasedByUserId);

    boolean existsByProjectCode(String projectCode);

    @Query("SELECT DISTINCT p FROM Project p " +
           "LEFT JOIN ProjectAssignment pa ON pa.project.id = p.id " +
           "WHERE (:search IS NULL OR LOWER(p.projectName) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(p.projectCode) LIKE LOWER(CONCAT('%', :search, '%'))) " +
           "AND (:status IS NULL OR p.status = :status) " +
           "AND (:techStack IS NULL OR LOWER(p.technologyStack) LIKE LOWER(CONCAT('%', :techStack, '%'))) " +
           "AND (:startDate IS NULL OR p.createdAt >= :startDate) " +
           "AND (:endDate IS NULL OR p.createdAt <= :endDate) " +
           "AND (:assignedUserId IS NULL OR (pa.user.id = :assignedUserId AND pa.active = true)) " +
           "ORDER BY p.createdAt DESC")
    List<Project> searchProjects(
            @Param("search") String search,
            @Param("status") ProjectStatus status,
            @Param("techStack") String techStack,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            @Param("assignedUserId") Long assignedUserId
    );

    @Query("SELECT DISTINCT p FROM Project p " +
           "LEFT JOIN ProjectAssignment pa ON pa.project.id = p.id " +
           "LEFT JOIN Requirement r ON p.linkedRequirementId = r.id " +
           "WHERE ((pa.user.id = :userId AND pa.active = true) " +
           "   OR (p.developer IS NOT NULL AND p.developer.id = :userId) " +
           "   OR (p.reviewerAdmin IS NOT NULL AND p.reviewerAdmin.id = :userId) " +
           "   OR (p.purchasedByUserId IS NOT NULL AND p.purchasedByUserId = :userId) " +
           "   OR (r.user IS NOT NULL AND r.user.id = :userId)) " +
           "AND (:search IS NULL OR LOWER(p.projectName) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(p.projectCode) LIKE LOWER(CONCAT('%', :search, '%'))) " +
           "AND (:status IS NULL OR p.status = :status) " +
           "ORDER BY p.createdAt DESC")
    List<Project> searchAssignedProjects(
            @Param("userId") Long userId,
            @Param("search") String search,
            @Param("status") ProjectStatus status
    );

    long countByStatus(ProjectStatus status);
}
