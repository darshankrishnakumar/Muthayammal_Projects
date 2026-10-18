package com.telecom.churn.dto;

import java.time.LocalDateTime;

public class PredictionResponseDto {

    private Boolean success;
    private Long id;
    private LocalDateTime timestamp;
    private String prediction;
    private Double churnProbability;
    private String riskLevel;
    private String recommendation;
    private String model;
    private CustomerRequestDto customerDetails;

    public PredictionResponseDto() {}

    public PredictionResponseDto(Boolean success, Long id, LocalDateTime timestamp,
                                 String prediction, Double churnProbability,
                                 String riskLevel, String recommendation,
                                 String model, CustomerRequestDto customerDetails) {
        this.success = success;
        this.id = id;
        this.timestamp = timestamp;
        this.prediction = prediction;
        this.churnProbability = churnProbability;
        this.riskLevel = riskLevel;
        this.recommendation = recommendation;
        this.model = model;
        this.customerDetails = customerDetails;
    }

    public Boolean getSuccess() { return success; }
    public void setSuccess(Boolean success) { this.success = success; }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }

    public String getPrediction() { return prediction; }
    public void setPrediction(String prediction) { this.prediction = prediction; }

    public Double getChurnProbability() { return churnProbability; }
    public void setChurnProbability(Double churnProbability) { this.churnProbability = churnProbability; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }

    public String getRecommendation() { return recommendation; }
    public void setRecommendation(String recommendation) { this.recommendation = recommendation; }

    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }

    public CustomerRequestDto getCustomerDetails() { return customerDetails; }
    public void setCustomerDetails(CustomerRequestDto customerDetails) { this.customerDetails = customerDetails; }
}
