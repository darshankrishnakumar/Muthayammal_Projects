package com.telecom.churn.controller;

import com.telecom.churn.dto.CustomerRequestDto;
import com.telecom.churn.dto.DashboardStatsDto;
import com.telecom.churn.dto.MlPredictionResponseDto;
import com.telecom.churn.dto.ModelMetricsDto;
import com.telecom.churn.dto.PredictionResponseDto;
import com.telecom.churn.entity.PredictionRecord;
import com.telecom.churn.exception.ResourceNotFoundException;
import com.telecom.churn.repository.PredictionRecordRepository;
import com.telecom.churn.service.DashboardService;
import com.telecom.churn.service.MlClientService;
import com.telecom.churn.service.PredictionPersistenceService;
import com.telecom.churn.service.RecommendationService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api")
public class PredictionController {

    private static final Logger log = LoggerFactory.getLogger(PredictionController.class);

    private final MlClientService mlClientService;
    private final RecommendationService recommendationService;
    private final DashboardService dashboardService;
    private final PredictionRecordRepository repository;
    private final PredictionPersistenceService persistenceService;

    public PredictionController(MlClientService mlClientService,
                                RecommendationService recommendationService,
                                DashboardService dashboardService,
                                PredictionRecordRepository repository,
                                PredictionPersistenceService persistenceService) {
        this.mlClientService = mlClientService;
        this.recommendationService = recommendationService;
        this.dashboardService = dashboardService;
        this.repository = repository;
        this.persistenceService = persistenceService;
    }

    @PostMapping("/predict")
    public ResponseEntity<PredictionResponseDto> predictChurn(@Valid @RequestBody CustomerRequestDto request) {
        log.info("Received churn prediction request for customer with tenure={} months, contract={}",
                request.getTenure(), request.getContract());

        // 1. Forward features to Python ML service
        MlPredictionResponseDto mlResponse = mlClientService.getPrediction(request);

        // 2. Determine risk level and recommendation
        String riskLevel = mlResponse.getRiskLevel() != null ? mlResponse.getRiskLevel() : "Low";
        Double prob = mlResponse.getChurnProbability() != null ? mlResponse.getChurnProbability() : 0.0;
        String recommendation = recommendationService.generateRecommendation(riskLevel, prob, request);

        // 3. Atomically persist to normalized SQL tables and audit history
        PredictionRecord saved = persistenceService.savePredictionTransaction(
                request, mlResponse, riskLevel, prob, recommendation
        );
        log.info("Saved prediction record with ID: {}", saved.getId());

        // 4. Return structured response to React
        PredictionResponseDto response = new PredictionResponseDto(
                true,
                saved.getId(),
                saved.getTimestamp(),
                saved.getPredictedClass(),
                saved.getChurnProbability(),
                saved.getRiskLevel(),
                saved.getRecommendation(),
                saved.getModelVersion(),
                request
        );

        return ResponseEntity.ok(response);
    }

    @GetMapping("/dashboard")
    public ResponseEntity<DashboardStatsDto> getDashboard() {
        return ResponseEntity.ok(dashboardService.getDashboardStats());
    }

    @GetMapping("/model-metrics")
    public ResponseEntity<ModelMetricsDto> getModelMetrics() {
        return ResponseEntity.ok(mlClientService.getModelMetrics());
    }

    @GetMapping("/history")
    public ResponseEntity<List<PredictionRecord>> getHistory() {
        return ResponseEntity.ok(repository.findAllByOrderByTimestampDesc());
    }

    @GetMapping("/history/{id}")
    public ResponseEntity<PredictionRecord> getHistoryById(@PathVariable Long id) {
        PredictionRecord record = repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Prediction record not found with ID: " + id));
        return ResponseEntity.ok(record);
    }
}
