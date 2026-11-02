package com.academic.controller;

import com.academic.dto.CatalogItemDto;
import com.academic.dto.CheckoutRequest;
import com.academic.model.Order;
import com.academic.model.User;
import com.academic.service.OrderService;
import com.academic.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @Autowired
    private UserService userService;

    private User getAuthenticatedUser() {
        String email = (String) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        return userService.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Authenticated user session not found."));
    }

    @GetMapping("/catalog")
    public ResponseEntity<List<CatalogItemDto>> getCatalog() {
        return ResponseEntity.ok(orderService.getCatalog());
    }

    @PostMapping("/checkout")
    public ResponseEntity<?> checkout(@RequestBody CheckoutRequest request) {
        try {
            User actor = getAuthenticatedUser();
            Order order = orderService.processCheckout(request, actor);
            return ResponseEntity.status(HttpStatus.CREATED).body(order);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Checkout failed: " + e.getMessage()));
        }
    }

    @GetMapping("/my-orders")
    public ResponseEntity<?> getMyOrders() {
        try {
            User actor = getAuthenticatedUser();
            List<Order> orders = orderService.getUserOrders(actor);
            return ResponseEntity.ok(orders);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Failed to load orders: " + e.getMessage()));
        }
    }

    @GetMapping("/{id}/invoice")
    public ResponseEntity<?> getInvoice(@PathVariable Long id) {
        try {
            User actor = getAuthenticatedUser();
            Map<String, Object> invoice = orderService.getInvoice(id, actor);
            return ResponseEntity.ok(invoice);
        } catch (SecurityException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("message", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Failed to retrieve invoice: " + e.getMessage()));
        }
    }
}
