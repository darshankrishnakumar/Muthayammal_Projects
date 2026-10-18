package com.telecom.churn.service;

import com.telecom.churn.dto.CustomerRequestDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class RecommendationServiceTest {

    private RecommendationService recommendationService;

    @BeforeEach
    void setUp() {
        recommendationService = new RecommendationService();
    }

    @Test
    void testHighRiskRecommendation() {
        CustomerRequestDto req = new CustomerRequestDto();
        req.setContract("Month-to-month");
        req.setInternetService("Fiber optic");
        req.setMonthlyCharges(95.0);
        req.setTenure(2);
        req.setTechSupport("No");

        String rec = recommendationService.generateRecommendation("High", 0.88, req);
        assertNotNull(rec);
        assertTrue(rec.contains("High churn risk"));
        assertTrue(rec.contains("Month-to-month"));
    }

    @Test
    void testLowRiskRecommendation() {
        CustomerRequestDto req = new CustomerRequestDto();
        req.setContract("Two year");
        req.setInternetService("DSL");
        req.setMonthlyCharges(45.0);
        req.setTenure(60);

        String rec = recommendationService.generateRecommendation("Low", 0.12, req);
        assertNotNull(rec);
        assertTrue(rec.contains("Low churn risk"));
        assertTrue(rec.contains("high stability"));
    }
}
