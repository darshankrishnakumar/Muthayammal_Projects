package com.academic.repository;

import com.academic.model.College;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CollegeRepository extends JpaRepository<College, Long> {

    Optional<College> findByCodeIgnoreCase(String code);

    boolean existsByCodeIgnoreCase(String code);

    List<College> findAllByOrderByNameAsc();

    List<College> findByActiveTrueOrderByNameAsc();
}
