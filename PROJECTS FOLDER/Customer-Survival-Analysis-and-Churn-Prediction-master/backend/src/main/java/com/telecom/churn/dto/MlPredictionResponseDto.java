package com.telecom.churn.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MlPredictionResponseDto {
    private String prediction;
    private Double churnProbability;
    private String model;
    private String riskLevel;
    private Map<String, Object> featuresReceived;

    public MlPredictionResponseDto() {}

    public String getPrediction() { return prediction; }
    public void setPrediction(String prediction) { this.prediction = prediction; }

    public Double getChurnProbability() { return churnProbability; }
    public void setChurnProbability(Double churnProbability) { this.churnProbability = churnProbability; }

    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }

    public Map<String, Object> getFeaturesReceived() { return featuresReceived; }
    public void setFeaturesReceived(Map<String, Object> featuresReceived) { this.featuresReceived = featuresReceived; }
}
