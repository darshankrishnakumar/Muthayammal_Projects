package com.academic.service;

import com.academic.model.*;
import com.academic.repository.CollegeProjectAllocationRepository;
import com.academic.repository.CollegeRepository;
import com.academic.repository.ProjectRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/**
 * College -> library project allocations. Allocating never copies a project or its files;
 * revoking hides the project from the college's marketplace but keeps access that students
 * already paid for.
 */
@Service
public class AllocationService {

    @Autowired
    private CollegeProjectAllocationRepository allocationRepository;

    @Autowired
    private CollegeRepository collegeRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private AccessControlService accessControlService;

    @Autowired
    private AuditLogService auditLogService;

    /** Allocations of one college. SUPER_ADMIN: any college; ADMIN: only their own. */
    @Transactional(readOnly = true)
    public List<Map<String, Object>> forCollege(Long collegeId, User actor) {
        assertCanViewCollege(collegeId, actor);
        return allocationRepository.findByCollegeId(collegeId).stream().map(this::row).toList();
    }

    /**
     * Allocation board for the Super Admin: every library project with this college's
     * allocation state.
     */
    @Transactional(readOnly = true)
    public List<Map<String, Object>> board(Long collegeId, String search) {
        College college = collegeRepository.findById(collegeId)
                .orElseThrow(() -> new NoSuchElementException("College not found with ID: " + collegeId));
        Map<Long, CollegeProjectAllocation> byProject = new HashMap<>();
        for (CollegeProjectAllocation a : allocationRepository.findByCollegeId(college.getId())) {
            byProject.put(a.getProject().getId(), a);
        }
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Project p : projectRepository.searchLibrary(search == null || search.isBlank() ? null : search.trim(), null, null)) {
            if (p.getCatalogStatus() == CatalogStatus.ARCHIVED && !byProject.containsKey(p.getId())) {
                continue;
            }
            CollegeProjectAllocation a = byProject.get(p.getId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("projectId", p.getId());
            m.put("projectCode", p.getProjectCode());
            m.put("projectName", p.getProjectName());
            m.put("domain", p.getDomain());
            m.put("technologyStack", p.getTechnologyStack());
            m.put("catalogStatus", p.getCatalogStatus());
            m.put("listPrice", p.getPrice());
            m.put("allocationId", a != null ? a.getId() : null);
            m.put("allocated", a != null && a.isActive());
            m.put("revoked", a != null && !a.isActive());
            m.put("priceOverride", a != null ? a.getPriceOverride() : null);
            m.put("effectivePrice", a != null ? a.getEffectivePrice() : p.getPrice());
            m.put("allocatedAt", a != null ? a.getAllocatedAt() : null);
            rows.add(m);
        }
        return rows;
    }

    @Transactional
    public Map<String, Object> allocate(Long collegeId, List<Long> projectIds, BigDecimal priceOverride, String notes, String actorEmail) {
        College college = collegeRepository.findById(collegeId)
                .orElseThrow(() -> new NoSuchElementException("College not found with ID: " + collegeId));
        if (projectIds == null || projectIds.isEmpty()) {
            throw new IllegalArgumentException("Select at least one project to allocate.");
        }
        if (priceOverride != null && priceOverride.signum() < 0) {
            throw new IllegalArgumentException("Price cannot be negative.");
        }
        int created = 0, reactivated = 0, unchanged = 0;
        for (Long projectId : new LinkedHashSet<>(projectIds)) {
            Project project = projectRepository.findById(projectId)
                    .orElseThrow(() -> new NoSuchElementException("Project not found with ID: " + projectId));
            if (!project.isLibrary()) {
                throw new IllegalArgumentException(project.getProjectCode() + " is not a library project.");
            }
            if (project.getCatalogStatus() == CatalogStatus.ARCHIVED) {
                throw new IllegalArgumentException(project.getProjectCode() + " is archived and cannot be allocated.");
            }
            Optional<CollegeProjectAllocation> existing = allocationRepository.findByCollegeIdAndProjectId(collegeId, projectId);
            if (existing.isPresent() && existing.get().isActive()) {
                if (priceOverride != null) {
                    existing.get().setPriceOverride(priceOverride);
                    allocationRepository.save(existing.get());
                }
                unchanged++;
                continue;
            }
            CollegeProjectAllocation a = existing.orElseGet(CollegeProjectAllocation::new);
            boolean isNew = a.getId() == null;
            a.setCollege(college);
            a.setProject(project);
            a.setActive(true);
            a.setPriceOverride(priceOverride);
            a.setNotes(notes);
            a.setAllocatedBy(actorEmail);
            a.setAllocatedAt(LocalDateTime.now());
            a.setRevokedAt(null);
            a.setRevokedBy(null);
            allocationRepository.save(a);
            if (isNew) created++; else reactivated++;
        }
        auditLogService.log(actorEmail, "PROJECTS_ALLOCATED",
                String.format("Allocated %d project(s) to %s (%d new, %d restored, %d already allocated)",
                        projectIds.size(), college.getName(), created, reactivated, unchanged));
        return Map.of("created", created, "reactivated", reactivated, "unchanged", unchanged);
    }

    @Transactional
    public Map<String, Object> update(Long allocationId, BigDecimal priceOverride, boolean clearPrice, String notes, String actorEmail) {
        CollegeProjectAllocation a = get(allocationId);
        if (priceOverride != null && priceOverride.signum() < 0) {
            throw new IllegalArgumentException("Price cannot be negative.");
        }
        if (clearPrice) {
            a.setPriceOverride(null);
        } else if (priceOverride != null) {
            a.setPriceOverride(priceOverride);
        }
        if (notes != null) {
            a.setNotes(notes);
        }
        allocationRepository.save(a);
        auditLogService.log(actorEmail, "ALLOCATION_UPDATED",
                String.format("%s @ %s price=%s", a.getProject().getProjectCode(), a.getCollege().getName(), a.getEffectivePrice()));
        return row(a);
    }

    @Transactional
    public int revoke(List<Long> allocationIds, String actorEmail) {
        int n = 0;
        for (Long id : allocationIds) {
            CollegeProjectAllocation a = get(id);
            if (!a.isActive()) continue;
            a.setActive(false);
            a.setRevokedAt(LocalDateTime.now());
            a.setRevokedBy(actorEmail);
            allocationRepository.save(a);
            auditLogService.log(actorEmail, "ALLOCATION_REVOKED",
                    a.getProject().getProjectCode() + " revoked from " + a.getCollege().getName());
            n++;
        }
        return n;
    }

    private CollegeProjectAllocation get(Long id) {
        return allocationRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Allocation not found with ID: " + id));
    }

    private void assertCanViewCollege(Long collegeId, User actor) {
        if (actor.getRole() == Role.SUPER_ADMIN) return;
        if (actor.getRole() == Role.ADMIN && actor.getCollege() != null && actor.getCollege().getId().equals(collegeId)) return;
        throw new AccessDeniedException("Access denied: you can only view allocations for your own college.");
    }

    private Map<String, Object> row(CollegeProjectAllocation a) {
        Project p = a.getProject();
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", a.getId());
        m.put("collegeId", a.getCollege().getId());
        m.put("collegeName", a.getCollege().getName());
        m.put("projectId", p.getId());
        m.put("projectCode", p.getProjectCode());
        m.put("projectName", p.getProjectName());
        m.put("domain", p.getDomain());
        m.put("technologyStack", p.getTechnologyStack());
        m.put("catalogStatus", p.getCatalogStatus());
        m.put("listPrice", p.getPrice());
        m.put("priceOverride", a.getPriceOverride());
        m.put("effectivePrice", a.getEffectivePrice());
        m.put("active", a.isActive());
        m.put("notes", a.getNotes());
        m.put("allocatedBy", a.getAllocatedBy());
        m.put("allocatedAt", a.getAllocatedAt());
        m.put("revokedAt", a.getRevokedAt());
        return m;
    }
}
