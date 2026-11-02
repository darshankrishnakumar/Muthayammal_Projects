package com.academic.controller;

import com.academic.model.User;
import com.academic.service.AccessControlService;
import com.academic.service.AllocationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/allocations")
public class AllocationController {

    @Autowired
    private AllocationService allocationService;

    @Autowired
    private AccessControlService accessControlService;

    /** The signed-in college admin's allocations. */
    @GetMapping("/mine")
    @PreAuthorize("hasRole('ADMIN')")
    public List<Map<String, Object>> mine() {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        return allocationService.forCollege(accessControlService.requireCollege(actor).getId(), actor);
    }

    @GetMapping("/colleges/{collegeId}")
    @PreAuthorize("hasAnyRole('SUPER_ADMIN','ADMIN')")
    public List<Map<String, Object>> forCollege(@PathVariable Long collegeId) {
        return allocationService.forCollege(collegeId, accessControlService.getCurrentAuthenticatedUser());
    }

    @GetMapping("/colleges/{collegeId}/board")
    @PreAuthorize("hasRole('SUPER_ADMIN')")
    public List<Map<String, Object>> board(@PathVariable Long collegeId, @RequestParam(required = false) String search) {
        return allocationService.board(collegeId, search);
    }

    @PostMapping
    @PreAuthorize("hasRole('SUPER_ADMIN')")
    public Map<String, Object> allocate(@RequestBody Map<String, Object> body) {
        Long collegeId = toLong(body.get("collegeId"));
        @SuppressWarnings("unchecked")
        List<Number> ids = (List<Number>) body.getOrDefault("projectIds", List.of());
        return allocationService.allocate(collegeId, ids.stream().map(Number::longValue).toList(),
                toDecimal(body.get("priceOverride")), (String) body.get("notes"), actorEmail());
    }

    @PatchMapping("/{id}")
    @PreAuthorize("hasRole('SUPER_ADMIN')")
    public Map<String, Object> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        boolean clear = body.containsKey("priceOverride") && (body.get("priceOverride") == null || body.get("priceOverride").toString().isBlank());
        return allocationService.update(id, clear ? null : toDecimal(body.get("priceOverride")), clear, (String) body.get("notes"), actorEmail());
    }

    @PostMapping("/revoke")
    @PreAuthorize("hasRole('SUPER_ADMIN')")
    public Map<String, Object> revoke(@RequestBody Map<String, Object> body) {
        @SuppressWarnings("unchecked")
        List<Number> ids = (List<Number>) body.getOrDefault("allocationIds", List.of());
        return Map.of("revoked", allocationService.revoke(ids.stream().map(Number::longValue).toList(), actorEmail()));
    }

    private String actorEmail() {
        return accessControlService.getCurrentAuthenticatedUser().getEmail();
    }

    private static Long toLong(Object o) {
        if (o == null) throw new IllegalArgumentException("collegeId is required.");
        return Long.valueOf(o.toString());
    }

    private static BigDecimal toDecimal(Object o) {
        return o == null || o.toString().isBlank() ? null : new BigDecimal(o.toString());
    }
}
