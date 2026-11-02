package com.academic.repository;

import com.academic.model.Notification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface NotificationRepository extends JpaRepository<Notification, Long> {

    List<Notification> findByRecipientEmailOrderByCreatedAtDesc(String recipientEmail);

    List<Notification> findByRecipientEmailAndIsReadFalseOrderByCreatedAtDesc(String recipientEmail);

    long countByRecipientEmailAndIsReadFalse(String recipientEmail);
}
