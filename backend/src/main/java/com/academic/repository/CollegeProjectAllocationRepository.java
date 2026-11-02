package com.academic.repository;

import com.academic.model.CollegeProjectAllocation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CollegeProjectAllocationRepository extends JpaRepository<CollegeProjectAllocation, Long> {

    Optional<CollegeProjectAllocation> findByCollegeIdAndProjectId(Long collegeId, Long projectId);

    @Query("SELECT a FROM CollegeProjectAllocation a WHERE a.college.id = :collegeId AND a.project.id = :projectId AND a.active = true")
    Optional<CollegeProjectAllocation> findActive(@Param("collegeId") Long collegeId, @Param("projectId") Long projectId);

    @Query("SELECT a FROM CollegeProjectAllocation a WHERE a.college.id = :collegeId ORDER BY a.active DESC, a.allocatedAt DESC")
    List<CollegeProjectAllocation> findByCollegeId(@Param("collegeId") Long collegeId);

    @Query("SELECT a FROM CollegeProjectAllocation a WHERE a.college.id = :collegeId AND a.active = true")
    List<CollegeProjectAllocation> findActiveByCollegeId(@Param("collegeId") Long collegeId);

    @Query("SELECT a FROM CollegeProjectAllocation a WHERE a.project.id = :projectId AND a.active = true")
    List<CollegeProjectAllocation> findActiveByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT COUNT(a) FROM CollegeProjectAllocation a WHERE a.college.id = :collegeId AND a.active = true")
    long countActiveByCollegeId(@Param("collegeId") Long collegeId);

    @Query("SELECT COUNT(DISTINCT a.project.id) FROM CollegeProjectAllocation a WHERE a.active = true")
    long countDistinctAllocatedProjects();

    long countByActiveTrue();
}
