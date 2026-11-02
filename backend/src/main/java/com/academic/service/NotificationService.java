package com.academic.service;

import com.academic.model.Notification;
import com.academic.repository.NotificationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@SuppressWarnings("null")
public class NotificationService {

    @Autowired
    private NotificationRepository notificationRepository;

    @Transactional
    public Notification sendNotification(String recipientEmail, String recipientRole, String title, String message, String linkUrl) {
        if (recipientEmail == null || recipientEmail.isBlank()) {
            return null;
        }
        Notification notification = new Notification(
                recipientEmail.trim().toLowerCase(),
                recipientRole != null ? recipientRole : "USER",
                title,
                message,
                linkUrl
        );
        return notificationRepository.save(notification);
    }

    public List<Notification> getMyNotifications(String email) {
        if (email == null) return List.of();
        return notificationRepository.findByRecipientEmailOrderByCreatedAtDesc(email.trim().toLowerCase());
    }

    public long getUnreadCount(String email) {
        if (email == null) return 0;
        return notificationRepository.countByRecipientEmailAndIsReadFalse(email.trim().toLowerCase());
    }

    @Transactional
    public void markAsRead(Long notificationId, String userEmail) {
        notificationRepository.findById(notificationId).ifPresent(n -> {
            if (n.getRecipientEmail().equalsIgnoreCase(userEmail)) {
                n.setRead(true);
                notificationRepository.save(n);
            }
        });
    }

    @Transactional
    public void markAllAsRead(String userEmail) {
        List<Notification> unread = notificationRepository.findByRecipientEmailAndIsReadFalseOrderByCreatedAtDesc(userEmail.trim().toLowerCase());
        unread.forEach(n -> n.setRead(true));
        notificationRepository.saveAll(unread);
    }
}
