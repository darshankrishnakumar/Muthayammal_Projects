package com.academic.controller;

import com.academic.dto.RequirementSummaryDto;
import com.academic.model.*;
import com.academic.service.AccessControlService;
import com.academic.service.DevelopmentWorkflowService;
import com.academic.service.OrderService;
import com.academic.service.RequirementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/requirements")
public class RequirementController {

    @Autowired
    private RequirementService requirementService;

    @Autowired
    private DevelopmentWorkflowService workflowService;

    @Autowired
    private OrderService orderService;

    @Autowired
    private AccessControlService accessControlService;

    private User actor() {
        return accessControlService.getCurrentAuthenticatedUser();
    }

    /** Own requirements (student), college requirements (admin), all (super admin), assigned (developer). */
    @GetMapping
    public List<RequirementSummaryDto> getRequirements(@RequestParam(required = false) String search,
                                                       @RequestParam(required = false) String status) {
        return requirementService.listForActor(actor(), search, status);
    }

    @GetMapping("/stats")
    public Map<String, Object> getStats() {
        return requirementService.getUserStats(actor());
    }

    @GetMapping("/{id}")
    public Requirement getRequirementById(@PathVariable Long id) {
        return requirementService.getRequirementById(id, actor());
    }

    @GetMapping("/{id}/timeline")
    public List<StatusHistory> timeline(@PathVariable Long id) {
        return requirementService.timeline(id, actor());
    }

    @PostMapping
    public ResponseEntity<Requirement> createRequirement(@RequestBody Requirement requirement) {
        return ResponseEntity.status(HttpStatus.CREATED).body(requirementService.createRequirement(requirement, actor()));
    }

    @PutMapping("/{id}")
    public Requirement updateRequirement(@PathVariable Long id, @RequestBody Requirement requirement) {
        return requirementService.updateRequirement(id, requirement, actor());
    }

    @PostMapping("/{id}/submit")
    public Requirement submitRequirement(@PathVariable Long id) {
        return requirementService.submitRequirement(id, actor());
    }

    /** College admin: FORWARD to the Super Admin, RETURN for changes, or REJECT. */
    @PostMapping("/{id}/college-review")
    public Requirement collegeReview(@PathVariable Long id, @RequestBody Map<String, String> body) {
        return requirementService.collegeReview(id, body.get("action"), body.get("notes"), actor());
    }

    /** Super Admin: APPROVE (with total price and advance), REQUEST_CHANGES or REJECT. */
    @PostMapping("/{id}/review")
    public Map<String, Object> reviewRequirement(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Requirement req = requirementService.superAdminReview(id,
                (String) body.get("action"),
                (String) body.get("notes"),
                toDecimal(body.get("budget")),
                toDecimal(body.get("advanceAmount")),
                actor());
        return Map.of("success", true, "requirement", req);
    }

    /** Advance payment. The amount is the advance quoted by the Super Admin; client amounts are ignored. */
    @PostMapping("/{id}/pay-advance")
    public Map<String, Object> payAdvance(@PathVariable Long id, @RequestBody(required = false) Map<String, Object> body,
                                          @RequestHeader(value = "Idempotency-Key", required = false) String headerKey) {
        String key = headerKey != null ? headerKey : body != null && body.get("idempotencyKey") != null ? body.get("idempotencyKey").toString() : null;
        Order order = orderService.processRequirementAdvancePayment(id, key, actor());
        return Map.of(
                "success", true,
                "message", order.isSimulatedPayment()
                        ? "Advance payment recorded (SIMULATED — development mode)."
                        : "Advance payment verified.",
                "order", order);
    }

    /** Super Admin: create the development project and assign the developer (and optional reviewer). */
    @PostMapping("/{id}/start-development")
    public Project startDevelopment(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Long developerId = body.get("developerId") != null ? Long.valueOf(body.get("developerId").toString()) : null;
        Long reviewerId = body.get("reviewerId") != null && !body.get("reviewerId").toString().isBlank()
                ? Long.valueOf(body.get("reviewerId").toString()) : null;
        return workflowService.startDevelopment(id, developerId, reviewerId, (String) body.get("notes"), actor());
    }

    @DeleteMapping("/{id}")
    public Map<String, Object> deleteRequirementById(@PathVariable Long id) {
        requirementService.deleteRequirement(id, actor());
        return Map.of("success", true, "message", "Requirement deleted.");
    }

    private static BigDecimal toDecimal(Object o) {
        return o == null || o.toString().isBlank() ? null : new BigDecimal(o.toString());
    }
}
