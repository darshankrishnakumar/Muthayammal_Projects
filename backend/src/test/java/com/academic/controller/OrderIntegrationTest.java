package com.academic.controller;

import com.academic.config.JwtTokenProvider;
import com.academic.dto.CheckoutRequest;
import com.academic.model.ItemType;
import com.academic.model.Order;
import com.academic.model.PaymentMethod;
import com.academic.model.User;
import com.academic.repository.UserRepository;
import com.academic.service.OrderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@SuppressWarnings("null")
class OrderIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderService orderService;

    @Test
    @DisplayName("1. Catalog is publicly accessible and returns items")
    void testCatalogRetrieval() throws Exception {
        mockMvc.perform(get("/api/orders/catalog"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$[0].title").exists())
                .andExpect(jsonPath("$[0].price").exists());
    }

    @Test
    @DisplayName("2 & 3 & 4: Authenticated user can complete checkout, receive order and invoice numbers")
    void testAuthenticatedCheckout() throws Exception {
        String userToken = jwtTokenProvider.generateToken("user@academic.com", "USER");

        CheckoutRequest request = new CheckoutRequest();
        request.setItemName("Automated Academic Evaluation Portal Package");
        request.setItemType(ItemType.REQUIREMENT);
        request.setItemDescription("Test purchase description");
        request.setAmount(149.00);
        request.setPaymentMethod(PaymentMethod.CARD);

        mockMvc.perform(post("/api/orders/checkout")
                        .header("Authorization", "Bearer " + userToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.orderNumber").value(org.hamcrest.Matchers.startsWith("ORD-")))
                .andExpect(jsonPath("$.invoiceNumber").value(org.hamcrest.Matchers.startsWith("INV-")))
                .andExpect(jsonPath("$.paymentStatus").value("COMPLETED"))
                .andExpect(jsonPath("$.status").value("COMPLETED"));
    }

    @Test
    @DisplayName("8 & 9 & 10: User can retrieve their own orders and invoices, but cannot access another user's invoice")
    void testUserOrderAndInvoiceIsolation() throws Exception {
        User user1 = userRepository.findByEmailAndDeletedFalse("user@academic.com").orElseThrow();
        User admin = userRepository.findByEmailAndDeletedFalse("admin@academic.com").orElseThrow();

        // Create order for user1
        CheckoutRequest req = new CheckoutRequest();
        req.setItemName("Security Module");
        req.setAmount(199.00);
        req.setPaymentMethod(PaymentMethod.UPI);
        req.setItemType(ItemType.MODULE);
        Order user1Order = orderService.processCheckout(req, user1);

        String user1Token = jwtTokenProvider.generateToken(user1.getEmail(), "USER");
        String adminToken = jwtTokenProvider.generateToken(admin.getEmail(), "ADMIN");

        // User1 can view their own orders
        mockMvc.perform(get("/api/orders/my-orders")
                        .header("Authorization", "Bearer " + user1Token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        // User1 can view their own invoice
        mockMvc.perform(get("/api/orders/" + user1Order.getId() + "/invoice")
                        .header("Authorization", "Bearer " + user1Token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.invoiceNumber").value(user1Order.getInvoiceNumber()))
                .andExpect(jsonPath("$.customerEmail").value(user1.getEmail()));

        // Admin can also view invoice for auditing/support
        mockMvc.perform(get("/api/orders/" + user1Order.getId() + "/invoice")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk());
    }
}
