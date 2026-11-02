package com.academic.repository;

import com.academic.model.Requirement;
import com.academic.model.RequirementStatus;
import com.academic.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RequirementRepository extends JpaRepository<Requirement, Long> {

    List<Requirement> findByUser(User user);

    List<Requirement> findByStatus(RequirementStatus status);

    long countByStatus(RequirementStatus status);

    long countByUser(User user);

    long countByUserAndStatus(User user, RequirementStatus status);

    @Query("SELECT r FROM Requirement r WHERE r.user = :user " +
           "AND (:status IS NULL OR r.status = :status) " +
           "AND (:query IS NULL OR LOWER(r.title) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(r.problemStatement) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<Requirement> searchUserRequirements(@Param("user") User user,
                                             @Param("status") RequirementStatus status,
                                             @Param("query") String query);

    @Query("SELECT r FROM Requirement r WHERE (:status IS NULL OR r.status = :status) " +
           "AND (:query IS NULL OR LOWER(r.title) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(r.problemStatement) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<Requirement> searchAllRequirements(@Param("status") RequirementStatus status,
                                            @Param("query") String query);

    @Query("SELECT r FROM Requirement r WHERE r.college.id = :collegeId " +
           "AND (:status IS NULL OR r.status = :status) " +
           "AND (:query IS NULL OR LOWER(r.title) LIKE LOWER(CONCAT('%', :query, '%'))) " +
           "ORDER BY r.createdAt DESC")
    List<Requirement> searchCollegeRequirements(@Param("collegeId") Long collegeId,
                                                @Param("status") RequirementStatus status,
                                                @Param("query") String query);

    @Query("SELECT COUNT(r) FROM Requirement r WHERE r.college.id = :collegeId AND r.status = :status")
    long countByCollegeAndStatus(@Param("collegeId") Long collegeId, @Param("status") RequirementStatus status);

    @Query("SELECT COUNT(r) FROM Requirement r WHERE r.college.id = :collegeId")
    long countByCollege(@Param("collegeId") Long collegeId);
}
