package com.academic.repository;

import com.academic.model.StatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StatusHistoryRepository extends JpaRepository<StatusHistory, Long> {

    List<StatusHistory> findByEntityTypeAndEntityIdOrderByCreatedAtAsc(String entityType, Long entityId);
}
