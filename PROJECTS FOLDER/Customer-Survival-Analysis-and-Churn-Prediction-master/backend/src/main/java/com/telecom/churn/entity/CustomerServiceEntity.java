package com.telecom.churn.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "customer_services")
public class CustomerServiceEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "phone_service", nullable = false, length = 10)
    private String phoneService;

    @Column(name = "multiple_lines", nullable = false, length = 30)
    private String multipleLines;

    @Column(name = "internet_service", nullable = false, length = 30)
    private String internetService;

    @Column(name = "online_security", nullable = false, length = 30)
    private String onlineSecurity;

    @Column(name = "online_backup", nullable = false, length = 30)
    private String onlineBackup;

    @Column(name = "device_protection", nullable = false, length = 30)
    private String deviceProtection;

    @Column(name = "tech_support", nullable = false, length = 30)
    private String techSupport;

    @Column(name = "streaming_tv", nullable = false, length = 30)
    private String streamingTV;

    @Column(name = "streaming_movies", nullable = false, length = 30)
    private String streamingMovies;

    public CustomerServiceEntity() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getCustomerId() { return customerId; }
    public void setCustomerId(Long customerId) { this.customerId = customerId; }

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
}
