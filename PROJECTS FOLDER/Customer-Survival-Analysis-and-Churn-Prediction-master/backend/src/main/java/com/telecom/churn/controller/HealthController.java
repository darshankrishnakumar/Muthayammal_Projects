package com.telecom.churn.controller;

import com.telecom.churn.service.MlClientService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class HealthController {

    private final MlClientService mlClientService;

    public HealthController(MlClientService mlClientService) {
        this.mlClientService = mlClientService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> getHealth() {
        Map<String, Object> mlHealth = mlClientService.checkMlHealth();
        boolean isMlUp = "UP".equalsIgnoreCase(String.valueOf(mlHealth.get("status")));

        Map<String, Object> health = new HashMap<>();
        health.put("backendStatus", "UP");
        health.put("timestamp", LocalDateTime.now());
        health.put("mlServiceStatus", isMlUp ? "UP" : "DOWN");
        health.put("mlDetails", mlHealth);
        health.put("overallStatus", isMlUp ? "HEALTHY" : "DEGRADED");

        return ResponseEntity.ok(health);
    }
}
