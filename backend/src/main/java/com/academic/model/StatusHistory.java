package com.academic.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/** Append-only timeline of state changes for requirements, projects and orders. */
@Entity
@Table(name = "status_history", indexes = {
        @Index(name = "idx_status_history_entity", columnList = "entity_type, entity_id")
})
public class StatusHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "entity_type", nullable = false, length = 30)
    private String entityType;

    @Column(name = "entity_id", nullable = false)
    private Long entityId;

    @Column(name = "from_status", length = 60)
    private String fromStatus;

    @Column(name = "to_status", nullable = false, length = 60)
    private String toStatus;

    @Column(name = "actor_email", nullable = false, length = 150)
    private String actorEmail;

    @Column(columnDefinition = "TEXT")
    private String note;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public StatusHistory() {}

    public StatusHistory(String entityType, Long entityId, String fromStatus, String toStatus, String actorEmail, String note) {
        this.entityType = entityType;
        this.entityId = entityId;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.actorEmail = actorEmail;
        this.note = note;
    }

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getEntityType() {
        return entityType;
    }

    public void setEntityType(String entityType) {
        this.entityType = entityType;
    }

    public Long getEntityId() {
        return entityId;
    }

    public void setEntityId(Long entityId) {
        this.entityId = entityId;
    }

    public String getFromStatus() {
        return fromStatus;
    }

    public void setFromStatus(String fromStatus) {
        this.fromStatus = fromStatus;
    }

    public String getToStatus() {
        return toStatus;
    }

    public void setToStatus(String toStatus) {
        this.toStatus = toStatus;
    }

    public String getActorEmail() {
        return actorEmail;
    }

    public void setActorEmail(String actorEmail) {
        this.actorEmail = actorEmail;
    }

    public String getNote() {
        return note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
