package com.academic.service;

import com.academic.model.EntitlementSource;
import com.academic.model.Project;
import com.academic.model.ProjectEntitlement;
import com.academic.model.User;
import com.academic.repository.ProjectEntitlementRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

/** Grants and revokes full deliverable access. Callers must have verified payment or authority first. */
@Service
public class EntitlementService {

    @Autowired
    private ProjectEntitlementRepository repository;

    @Autowired
    private AuditLogService auditLogService;

    @Transactional
    public ProjectEntitlement grant(User user, Project project, EntitlementSource source, Long orderId, String grantedBy) {
        ProjectEntitlement entitlement = repository.findByUserIdAndProjectId(user.getId(), project.getId())
                .orElseGet(() -> new ProjectEntitlement(user, project, source, orderId, grantedBy));
        entitlement.setActive(true);
        entitlement.setSource(source);
        entitlement.setOrderId(orderId);
        entitlement.setGrantedBy(grantedBy);
        entitlement.setRevokedAt(null);
        ProjectEntitlement saved = repository.save(entitlement);
        auditLogService.log(grantedBy, "ENTITLEMENT_GRANTED",
                String.format("Full access to %s granted to %s (%s%s)", project.getProjectCode(), user.getEmail(), source,
                        orderId != null ? ", order #" + orderId : ""));
        return saved;
    }

    @Transactional
    public void revoke(User user, Project project, String actorEmail) {
        repository.findByUserIdAndProjectId(user.getId(), project.getId()).ifPresent(e -> {
            e.setActive(false);
            e.setRevokedAt(LocalDateTime.now());
            repository.save(e);
            auditLogService.log(actorEmail, "ENTITLEMENT_REVOKED",
                    String.format("Access to %s revoked for %s", project.getProjectCode(), user.getEmail()));
        });
    }

    public boolean hasAccess(Long userId, Long projectId) {
        return repository.hasActive(userId, projectId);
    }

    public Set<Long> entitledProjectIds(Long userId) {
        return repository.findActiveProjectIdsByUserId(userId);
    }

    public List<ProjectEntitlement> activeFor(Long userId) {
        return repository.findActiveByUserId(userId);
    }
}
