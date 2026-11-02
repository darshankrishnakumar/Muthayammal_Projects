package com.academic.controller;

import com.academic.model.Order;
import com.academic.model.User;
import com.academic.service.AccessControlService;
import com.academic.service.MarketplaceService;
import com.academic.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/marketplace")
public class MarketplaceController {

    @Autowired
    private MarketplaceService marketplaceService;

    @Autowired
    private OrderService orderService;

    @Autowired
    private AccessControlService accessControlService;

    @GetMapping
    public List<Map<String, Object>> browse(@RequestParam(required = false) String search,
                                            @RequestParam(required = false) String domain,
                                            @RequestParam(required = false) String technology,
                                            @RequestParam(required = false) BigDecimal minPrice,
                                            @RequestParam(required = false) BigDecimal maxPrice,
                                            @RequestParam(required = false, defaultValue = "relevance") String sort) {
        return marketplaceService.browse(actor(), search, domain, technology, minPrice, maxPrice, sort);
    }

    @GetMapping("/filters")
    public Map<String, Object> filters() {
        return marketplaceService.filters(actor());
    }

    @GetMapping("/purchased")
    public List<Map<String, Object>> purchased() {
        return marketplaceService.purchased(actor());
    }

    @GetMapping("/{projectId}")
    public Map<String, Object> detail(@PathVariable Long projectId) {
        return marketplaceService.detail(actor(), projectId);
    }

    /** Starts a purchase. The server prices it from the college allocation; any client amount is ignored. */
    @PostMapping("/{projectId}/purchase")
    public ResponseEntity<?> purchase(@PathVariable Long projectId, @RequestBody(required = false) Map<String, Object> body,
                                      @RequestHeader(value = "Idempotency-Key", required = false) String headerKey) {
        String key = headerKey != null ? headerKey : body != null && body.get("idempotencyKey") != null ? body.get("idempotencyKey").toString() : null;
        Order order = orderService.purchaseLibraryProject(projectId, key, actor());
        return ResponseEntity.ok(Map.of(
                "success", true,
                "message", order.isSimulatedPayment()
                        ? "Purchase completed (SIMULATED payment — development mode)."
                        : "Purchase completed. Full access is now available.",
                "order", order));
    }

    private User actor() {
        return accessControlService.getCurrentAuthenticatedUser();
    }
}
