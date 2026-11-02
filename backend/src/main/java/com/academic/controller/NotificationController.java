package com.academic.controller;

import com.academic.model.Notification;
import com.academic.model.User;
import com.academic.service.AccessControlService;
import com.academic.service.NotificationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    @Autowired
    private NotificationService notificationService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public ResponseEntity<?> getMyNotifications() {
        User user = accessControlService.getCurrentAuthenticatedUser();
        List<Notification> list = notificationService.getMyNotifications(user.getEmail());
        long unread = notificationService.getUnreadCount(user.getEmail());
        return ResponseEntity.ok(Map.of(
                "notifications", list,
                "unreadCount", unread
        ));
    }

    @PostMapping("/{id}/read")
    public ResponseEntity<?> markAsRead(@PathVariable Long id) {
        User user = accessControlService.getCurrentAuthenticatedUser();
        notificationService.markAsRead(id, user.getEmail());
        return ResponseEntity.ok(Map.of("success", true));
    }

    @PostMapping("/read-all")
    public ResponseEntity<?> markAllAsRead() {
        User user = accessControlService.getCurrentAuthenticatedUser();
        notificationService.markAllAsRead(user.getEmail());
        return ResponseEntity.ok(Map.of("success", true));
    }
}
