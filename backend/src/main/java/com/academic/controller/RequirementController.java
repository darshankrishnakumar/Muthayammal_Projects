package com.academic.controller;

import com.academic.dto.RequirementSummaryDto;
import com.academic.model.Requirement;
import com.academic.model.RequirementStatus;
import com.academic.model.Role;
import com.academic.model.User;
import com.academic.service.RequirementService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/requirements")
public class RequirementController {

    @Autowired
    private RequirementService requirementService;

    @Autowired
    private UserService userService;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user not found."));
    }

    @GetMapping
    public ResponseEntity<?> getRequirements(
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String status) {
        User actor = getAuthenticatedUser();
        List<RequirementSummaryDto> requirements;

        if (actor.getRole() == Role.USER) {
            requirements = requirementService.getUserRequirements(actor, search, status);
        } else {
            requirements = requirementService.getAllRequirements(search, status);
        }

        return ResponseEntity.ok(requirements);
    }

    @GetMapping("/stats")
    public ResponseEntity<?> getStats() {
        User actor = getAuthenticatedUser();
        Map<String, Object> stats = requirementService.getUserStats(actor);
        return ResponseEntity.ok(stats);
    }

    @GetMapping("/approved")
    public ResponseEntity<?> getApprovedRequirements() {
        List<Requirement> approved = requirementService.getApprovedRequirements();
        return ResponseEntity.ok(approved);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getRequirementById(@PathVariable Long id) {
        try {
            User actor = getAuthenticatedUser();
            Requirement req = requirementService.getRequirementById(id, actor);
            return ResponseEntity.ok(req);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping
    public ResponseEntity<?> createRequirement(@RequestBody Requirement requirement) {
        try {
            User actor = getAuthenticatedUser();
            Requirement created = requirementService.createRequirement(requirement, actor);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateRequirement(@PathVariable Long id, @RequestBody Requirement requirement) {
        try {
            User actor = getAuthenticatedUser();
            Requirement updated = requirementService.updateRequirement(id, requirement, actor);
            return ResponseEntity.ok(updated);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/{id}/submit")
    public ResponseEntity<?> submitRequirement(@PathVariable Long id) {
        try {
            User actor = getAuthenticatedUser();
            Requirement submitted = requirementService.submitRequirement(id, actor);
            return ResponseEntity.ok(submitted);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", e.getMessage()));
        }
    }

    @Autowired
    private com.academic.service.OrderService orderService;

    @Autowired
    private com.academic.service.NotificationService notificationService;

    @PostMapping("/{id}/pay-advance")
    public ResponseEntity<?> payAdvance(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, Object> body) {
        try {
            User actor = getAuthenticatedUser();
            Double amount = body != null && body.containsKey("amount") ? Double.valueOf(body.get("amount").toString()) : null;
            String idempotencyKey = body != null && body.containsKey("idempotencyKey") ? (String) body.get("idempotencyKey") : null;

            var order = orderService.processRequirementAdvancePayment(id, amount, idempotencyKey, actor);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Advance payment received and verified successfully.",
                    "order", order
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/{id}/review")
    public ResponseEntity<?> reviewRequirement(
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN && actor.getRole() != Role.ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        String action = body.getOrDefault("action", "APPROVE");
        String notes = body.getOrDefault("notes", "");

        try {
            Requirement req = requirementService.getRequirementEntityById(id);
            if ("APPROVE".equalsIgnoreCase(action)) {
                req.setStatus(RequirementStatus.APPROVED);
                notificationService.sendNotification(req.getUser().getEmail(), "USER",
                        "Requirement Approved!",
                        "Your requirement '" + req.getTitle() + "' has been approved by Super Admin. Project initialization is now underway.",
                        "/requirements");
            } else if ("REQUEST_CHANGES".equalsIgnoreCase(action)) {
                req.setStatus(RequirementStatus.CHANGES_REQUESTED);
                req.setSuperAdminNotes(notes);
                notificationService.sendNotification(req.getUser().getEmail(), "USER",
                        "Changes Requested on Requirement",
                        "Super Admin requested revisions for '" + req.getTitle() + "': " + notes,
                        "/requirements");
            } else if ("REJECT".equalsIgnoreCase(action)) {
                req.setStatus(RequirementStatus.REJECTED);
                req.setSuperAdminNotes(notes);
                notificationService.sendNotification(req.getUser().getEmail(), "USER",
                        "Requirement Update",
                        "Your requirement '" + req.getTitle() + "' has been closed: " + notes,
                        "/requirements");
            }
            req.setSuperAdminNotes(notes);
            Requirement saved = requirementService.save(req);
            return ResponseEntity.ok(Map.of("success", true, "requirement", saved));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/{id}/approve")
    public ResponseEntity<?> approveRequirement(@PathVariable Long id) {
        try {
            User actor = getAuthenticatedUser();
            Requirement approved = requirementService.approveRequirement(id, actor);
            return ResponseEntity.ok(approved);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/{id}/reject")
    public ResponseEntity<?> rejectRequirement(@PathVariable Long id) {
        try {
            User actor = getAuthenticatedUser();
            Requirement rejected = requirementService.rejectRequirement(id, actor);
            return ResponseEntity.ok(rejected);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteRequirementById(@PathVariable Long id) {
        User actor = getAuthenticatedUser();
        if (actor.getRole() == Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied."));
        }

        try {
            requirementService.deleteRequirement(id, actor.getEmail());
            return ResponseEntity.ok(Map.of("success", true, "message", "Requirement successfully deleted."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @DeleteMapping
    public ResponseEntity<?> deleteAllRequirements() {
        User actor = getAuthenticatedUser();
        if (actor.getRole() != Role.SUPER_ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", "Access denied. Only Super Admin can delete all requirements."));
        }

        try {
            requirementService.deleteAllRequirements(actor.getEmail());
            return ResponseEntity.ok(Map.of("success", true, "message", "All requirements successfully deleted."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
