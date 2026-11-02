package com.academic.service;

import com.academic.model.AuditLog;
import com.academic.repository.AuditLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

@Service
public class AuditLogService {

    private static final Logger logger = LoggerFactory.getLogger(AuditLogService.class);

    @Autowired
    private AuditLogRepository auditLogRepository;

    @Value("${audit.log.enabled:true}")
    private boolean auditLogEnabled;

    @Value("${audit.log.level:MODERATE}")
    private String auditLogLevel;

    /**
     * High-frequency routine events that generate high volume with low auditing value.
     */
    private static final Set<String> IGNORED_ACTIONS = Set.of(
            "LOGIN",
            "LOGOUT",
            "OTP_RESENT",
            "OTP_VERIFIED",
            "SYSTEM_INIT",
            "VIEW_FILE",
            "VIEW_PROJECT",
            "VIEW_REQUIREMENT"
    );

    /**
     * Critical, high-impact security, deletion, and financial settlement actions.
     */
    private static final Set<String> CRITICAL_ACTIONS = Set.of(
            "DELETE_USER",
            "DELETE_PROJECT",
            "DELETE_ALL_PROJECTS",
            "DELETE_REQUIREMENT",
            "DELETE_ALL_REQUIREMENTS",
            "ADMIN_PRESET_APPLIED",
            "ADMIN_PERMISSION_GRANTED",
            "ADMIN_PERMISSION_REVOKED",
            "ADMIN_PERMISSIONS_BULK_UPDATED",
            "ADMIN_USERS_ASSIGNED",
            "ROLE_UPDATE",
            "UPDATE_USER_ROLE",
            "APPROVE_REQUIREMENT",
            "REJECT_REQUIREMENT",
            "ADVANCE_PAYMENT_COMPLETED",
            "FINAL_PAYMENT_COMPLETED",
            "MARKETPLACE_PURCHASE_COMPLETED",
            "FOLDER_DELETE",
            "FILE_DELETE"
    );

    @Transactional
    public void log(String actorEmail, String action, String details) {
        if (!auditLogEnabled) {
            return;
        }

        if (action == null || action.trim().isEmpty()) {
            return;
        }

        String normalizedAction = action.trim().toUpperCase();

        // 1. Filter out low-value routine events
        if (IGNORED_ACTIONS.contains(normalizedAction)) {
            return;
        }

        // 2. Enforce configured log level filtering
        String level = (auditLogLevel != null) ? auditLogLevel.trim().toUpperCase() : "MODERATE";

        if ("CRITICAL".equals(level)) {
            // Under CRITICAL level, only persist high-risk security & deletion events
            if (!CRITICAL_ACTIONS.contains(normalizedAction)) {
                return;
            }
        }
        // Under MODERATE (default) level, persist all mutations & critical events, skipping IGNORED_ACTIONS.
        // Under ALL level, persist all non-ignored events.

        try {
            AuditLog log = new AuditLog(actorEmail, normalizedAction, details);
            auditLogRepository.save(log);
        } catch (Exception e) {
            logger.warn("Failed to persist audit log for action: {} by actor: {}. Error: {}", normalizedAction, actorEmail, e.getMessage());
        }
    }

    public List<AuditLog> getAllLogs(LocalDateTime startDate, LocalDateTime endDate) {
        if (startDate != null && endDate != null) {
            return auditLogRepository.findByTimestampBetweenOrderByTimestampDesc(startDate, endDate);
        }
        return auditLogRepository.findAllByOrderByTimestampDesc();
    }

    public List<AuditLog> getRestrictedLogs(LocalDateTime startDate, LocalDateTime endDate) {
        if (startDate != null && endDate != null) {
            return auditLogRepository.findRestrictedLogsByDateRange(startDate, endDate);
        }
        return auditLogRepository.findRestrictedLogs();
    }
}
