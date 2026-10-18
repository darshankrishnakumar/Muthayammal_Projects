package com.telecom.churn.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "prediction_history")
public class PredictionRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    @Column(nullable = false)
    private String predictedClass;

    @Column(nullable = false)
    private Double churnProbability;

    @Column(nullable = false)
    private String riskLevel;

    @Column(length = 1000)
    private String recommendation;

    private String modelVersion;

    @Column(name = "customer_code", length = 64)
    private String customerCode;

    // Customer Features
    private String gender;
    private Integer seniorCitizen;
    private String partner;
    private String dependents;
    private Integer tenure;
    private String phoneService;
    private String multipleLines;
    private String internetService;
    private String onlineSecurity;
    private String onlineBackup;
    private String deviceProtection;
    private String techSupport;
    private String streamingTV;
    private String streamingMovies;
    private String contract;
    private String paperlessBilling;
    private String paymentMethod;
    private Double monthlyCharges;
    private Double totalCharges;

    @PrePersist
    public void prePersist() {
        if (this.timestamp == null) {
            this.timestamp = LocalDateTime.now();
        }
    }

    public PredictionRecord() {}

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }

    public String getPredictedClass() { return predictedClass; }
    public void setPredictedClass(String predictedClass) { this.predictedClass = predictedClass; }

    public Double getChurnProbability() { return churnProbability; }
    public void setChurnProbability(Double churnProbability) { this.churnProbability = churnProbability; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }

    public String getRecommendation() { return recommendation; }
    public void setRecommendation(String recommendation) { this.recommendation = recommendation; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public String getCustomerCode() { return customerCode; }
    public void setCustomerCode(String customerCode) { this.customerCode = customerCode; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public Integer getSeniorCitizen() { return seniorCitizen; }
    public void setSeniorCitizen(Integer seniorCitizen) { this.seniorCitizen = seniorCitizen; }

    public String getPartner() { return partner; }
    public void setPartner(String partner) { this.partner = partner; }

    public String getDependents() { return dependents; }
    public void setDependents(String dependents) { this.dependents = dependents; }

    public Integer getTenure() { return tenure; }
    public void setTenure(Integer tenure) { this.tenure = tenure; }

    public String getPhoneService() { return phoneService; }
    public void setPhoneService(String phoneService) { this.phoneService = phoneService; }

    public String getMultipleLines() { return multipleLines; }
    public void setMultipleLines(String multipleLines) { this.multipleLines = multipleLines; }

    public String getInternetService() { return internetService; }
    public void setInternetService(String internetService) { this.internetService = internetService; }

    public String getOnlineSecurity() { return onlineSecurity; }
    public void setOnlineSecurity(String onlineSecurity) { this.onlineSecurity = onlineSecurity; }

    public String getOnlineBackup() { return onlineBackup; }
    public void setOnlineBackup(String onlineBackup) { this.onlineBackup = onlineBackup; }

    public String getDeviceProtection() { return deviceProtection; }
    public void setDeviceProtection(String deviceProtection) { this.deviceProtection = deviceProtection; }

    public String getTechSupport() { return techSupport; }
    public void setTechSupport(String techSupport) { this.techSupport = techSupport; }

    public String getStreamingTV() { return streamingTV; }
    public void setStreamingTV(String streamingTV) { this.streamingTV = streamingTV; }

    public String getStreamingMovies() { return streamingMovies; }
    public void setStreamingMovies(String streamingMovies) { this.streamingMovies = streamingMovies; }

    public String getContract() { return contract; }
    public void setContract(String contract) { this.contract = contract; }

    public String getPaperlessBilling() { return paperlessBilling; }
    public void setPaperlessBilling(String paperlessBilling) { this.paperlessBilling = paperlessBilling; }

    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }

    public Double getMonthlyCharges() { return monthlyCharges; }
    public void setMonthlyCharges(Double monthlyCharges) { this.monthlyCharges = monthlyCharges; }

    public Double getTotalCharges() { return totalCharges; }
    public void setTotalCharges(Double totalCharges) { this.totalCharges = totalCharges; }
}
