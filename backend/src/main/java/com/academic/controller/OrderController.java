package com.academic.controller;

import com.academic.model.Order;
import com.academic.model.User;
import com.academic.service.AccessControlService;
import com.academic.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Order history, invoices and payment configuration. Purchases themselves are started from
 * the marketplace, requirement and project endpoints so the server can price them.
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @Autowired
    private AccessControlService accessControlService;

    @Value("${academic.payments.currency:INR}")
    private String currency;

    /** Own orders for students; college orders for admins; all orders for the super admin. */
    @GetMapping
    public List<Order> listOrders() {
        return orderService.getOrdersForActor(accessControlService.getCurrentAuthenticatedUser());
    }

    @GetMapping("/my-orders")
    public List<Order> getMyOrders() {
        return orderService.getUserOrders(accessControlService.getCurrentAuthenticatedUser());
    }

    @GetMapping("/{id}/invoice")
    public Map<String, Object> getInvoice(@PathVariable Long id) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        return orderService.getInvoice(id, actor);
    }

    @GetMapping("/{id}/transactions")
    public ResponseEntity<?> getTransactions(@PathVariable Long id) {
        User actor = accessControlService.getCurrentAuthenticatedUser();
        return ResponseEntity.ok(orderService.getTransactions(id, actor));
    }

    /** Lets the UI label simulated payments and disable checkout when no gateway is configured. */
    @GetMapping("/payment-config")
    public Map<String, Object> paymentConfig() {
        return Map.of(
                "available", orderService.isPaymentAvailable(),
                "simulation", orderService.isSimulationMode(),
                "currency", currency);
    }
}
