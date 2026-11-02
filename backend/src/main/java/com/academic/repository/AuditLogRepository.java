package com.academic.repository;

import com.academic.model.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {

    List<AuditLog> findAllByOrderByTimestampDesc();

    List<AuditLog> findByTimestampBetweenOrderByTimestampDesc(LocalDateTime startDate, LocalDateTime endDate);

    // Restricted logs for standard Admins without date filter
    @Query("SELECT l FROM AuditLog l WHERE " +
           "LOWER(l.details) NOT LIKE '%super_admin%' AND " +
           "LOWER(l.details) NOT LIKE '%administrator account%' AND " +
           "LOWER(l.action) != 'system_init' " +
           "ORDER BY l.timestamp DESC")
    List<AuditLog> findRestrictedLogs();

    // Restricted logs for standard Admins with exact date range filter
    @Query("SELECT l FROM AuditLog l WHERE " +
           "l.timestamp >= :startDate AND l.timestamp <= :endDate AND " +
           "LOWER(l.details) NOT LIKE '%super_admin%' AND " +
           "LOWER(l.details) NOT LIKE '%administrator account%' AND " +
           "LOWER(l.action) != 'system_init' " +
           "ORDER BY l.timestamp DESC")
    List<AuditLog> findRestrictedLogsByDateRange(@Param("startDate") LocalDateTime startDate, 
                                                @Param("endDate") LocalDateTime endDate);

    List<AuditLog> findTop10ByOrderByTimestampDesc();
}
