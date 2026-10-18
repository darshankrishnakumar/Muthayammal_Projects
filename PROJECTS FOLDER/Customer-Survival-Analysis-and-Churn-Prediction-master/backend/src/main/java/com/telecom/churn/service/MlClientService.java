package com.telecom.churn.service;

import com.telecom.churn.dto.CustomerRequestDto;
import com.telecom.churn.dto.MlPredictionResponseDto;
import com.telecom.churn.dto.ModelMetricsDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class MlClientService {

    private static final Logger log = LoggerFactory.getLogger(MlClientService.class);

    private final RestTemplate restTemplate;

    @Value("${ml.service.url:http://127.0.0.1:8000}")
    private String mlServiceUrl;

    public MlClientService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public MlPredictionResponseDto getPrediction(CustomerRequestDto request) {
        String url = mlServiceUrl + "/predict";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<CustomerRequestDto> entity = new HttpEntity<>(request, headers);

        try {
            log.info("Forwarding customer features to Python ML service at: {}", url);
            ResponseEntity<MlPredictionResponseDto> response = restTemplate.postForEntity(url, entity, MlPredictionResponseDto.class);
            return response.getBody();
        } catch (Exception e) {
            log.error("Failed to connect to Python ML service at {}: {}", url, e.getMessage());
            throw new RuntimeException("Python ML Service communication error: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> checkMlHealth() {
        String url = mlServiceUrl + "/health";
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> resp = restTemplate.getForObject(url, Map.class);
            return resp;
        } catch (Exception e) {
            log.warn("ML Service health check failed: {}", e.getMessage());
            return Map.of(
                    "status", "DOWN",
                    "error", e.getMessage(),
                    "serviceUrl", mlServiceUrl
            );
        }
    }

    public ModelMetricsDto getModelMetrics() {
        String url = mlServiceUrl + "/metrics";
        try {
            return restTemplate.getForObject(url, ModelMetricsDto.class);
        } catch (Exception e) {
            log.error("Failed to fetch model metrics from Python ML service: {}", e.getMessage());
            throw new RuntimeException("Could not retrieve model metrics: " + e.getMessage(), e);
        }
    }
}
