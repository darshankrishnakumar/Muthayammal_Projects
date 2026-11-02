package com.academic.service;

import com.academic.model.StatusHistory;
import com.academic.repository.StatusHistoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/** Records every lifecycle transition so requirements, projects and orders have a timeline. */
@Service
public class StatusHistoryService {

    public static final String REQUIREMENT = "REQUIREMENT";
    public static final String PROJECT = "PROJECT";
    public static final String ORDER = "ORDER";

    @Autowired
    private StatusHistoryRepository repository;

    public void record(String entityType, Long entityId, Object from, Object to, String actorEmail, String note) {
        repository.save(new StatusHistory(
                entityType,
                entityId,
                from != null ? from.toString() : null,
                to != null ? to.toString() : "UNKNOWN",
                actorEmail != null ? actorEmail : "system",
                note));
    }

    public List<StatusHistory> timeline(String entityType, Long entityId) {
        return repository.findByEntityTypeAndEntityIdOrderByCreatedAtAsc(entityType, entityId);
    }
}
