package com.academic.repository;

import com.academic.model.AdminUserAssignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AdminUserAssignmentRepository extends JpaRepository<AdminUserAssignment, Long> {

    List<AdminUserAssignment> findByAdminUserId(Long adminUserId);

    List<AdminUserAssignment> findByAssignedUserId(Long assignedUserId);

    Optional<AdminUserAssignment> findByAdminUserIdAndAssignedUserId(Long adminUserId, Long assignedUserId);

    boolean existsByAdminUserIdAndAssignedUserId(Long adminUserId, Long assignedUserId);

    void deleteByAdminUserIdAndAssignedUserId(Long adminUserId, Long assignedUserId);

    void deleteByAdminUserId(Long adminUserId);

    @Query("SELECT a.assignedUser.id FROM AdminUserAssignment a WHERE a.adminUser.id = :adminUserId")
    List<Long> findAssignedUserIdsByAdminUserId(@Param("adminUserId") Long adminUserId);
}
