package com.academic.controller;

import com.academic.model.AuditLog;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.service.AuditLogService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/audit-logs")
public class AuditLogController {

    @Autowired
    private AuditLogService auditLogService;

    @Autowired
    private UserService userService;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user not found."));
    }

    @GetMapping
    public ResponseEntity<?> getAuditLogs(@RequestParam(required = false) String date) {
        User actor = getAuthenticatedUser();

        // Enforce RBAC: Regular Users cannot read audit logs
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(403).body(Map.of("message", "Access denied."));
        }

        LocalDateTime startDate = null;
        LocalDateTime endDate = null;

        if (date != null && !date.trim().isEmpty()) {
            try {
                LocalDate parsedDate = LocalDate.parse(date.trim());
                startDate = parsedDate.atStartOfDay();
                endDate = parsedDate.atTime(LocalTime.MAX);
            } catch (Exception e) {
                return ResponseEntity.badRequest().body(Map.of("message", "Invalid date format. Expected YYYY-MM-DD."));
            }
        }

        List<AuditLog> logs;
        if (actor.getRole() == Role.SUPER_ADMIN) {
            logs = auditLogService.getAllLogs(startDate, endDate);
        } else {
            logs = auditLogService.getRestrictedLogs(startDate, endDate);
        }

        return ResponseEntity.ok(logs);
    }
}
