package com.telecom.churn.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class CustomerRequestDto {

    @NotBlank(message = "Gender is required")
    @JsonAlias({"gender", "Gender"})
    private String gender = "Male";

    @NotNull(message = "SeniorCitizen is required (0 or 1)")
    @Min(0)
    @Max(1)
    @JsonAlias({"seniorCitizen", "SeniorCitizen", "senior_citizen"})
    private Integer seniorCitizen = 0;

    @NotBlank(message = "Partner is required (Yes or No)")
    @JsonAlias({"partner", "Partner"})
    private String partner = "No";

    @NotBlank(message = "Dependents is required (Yes or No)")
    @JsonAlias({"dependents", "Dependents"})
    private String dependents = "No";

    @NotNull(message = "Tenure is required (months)")
    @Min(0)
    @Max(120)
    @JsonAlias({"tenure", "tenureMonths", "Tenure", "TenureMonths"})
    private Integer tenure = 1;

    @NotBlank(message = "PhoneService is required")
    @JsonAlias({"phoneService", "PhoneService", "phone_service"})
    private String phoneService = "Yes";

    @NotBlank(message = "MultipleLines is required")
    @JsonAlias({"multipleLines", "MultipleLines", "multiple_lines"})
    private String multipleLines = "No";

    @NotBlank(message = "InternetService is required")
    @JsonAlias({"internetService", "InternetService", "internet_service"})
    private String internetService = "Fiber optic";

    @NotBlank(message = "OnlineSecurity is required")
    @JsonAlias({"onlineSecurity", "OnlineSecurity", "online_security"})
    private String onlineSecurity = "No";

    @NotBlank(message = "OnlineBackup is required")
    @JsonAlias({"onlineBackup", "OnlineBackup", "online_backup"})
    private String onlineBackup = "No";

    @NotBlank(message = "DeviceProtection is required")
    @JsonAlias({"deviceProtection", "DeviceProtection", "device_protection"})
    private String deviceProtection = "No";

    @NotBlank(message = "TechSupport is required")
    @JsonAlias({"techSupport", "TechSupport", "tech_support"})
    private String techSupport = "No";

    @NotBlank(message = "StreamingTV is required")
    @JsonAlias({"streamingTV", "StreamingTV", "streaming_tv", "streamingTv"})
    private String streamingTV = "No";

    @NotBlank(message = "StreamingMovies is required")
    @JsonAlias({"streamingMovies", "StreamingMovies", "streaming_movies"})
    private String streamingMovies = "No";

    @NotBlank(message = "Contract is required")
    @JsonAlias({"contract", "Contract"})
    private String contract = "Month-to-month";

    @NotBlank(message = "PaperlessBilling is required")
    @JsonAlias({"paperlessBilling", "PaperlessBilling", "paperless_billing"})
    private String paperlessBilling = "Yes";

    @NotBlank(message = "PaymentMethod is required")
    @JsonAlias({"paymentMethod", "PaymentMethod", "payment_method"})
    private String paymentMethod = "Electronic check";

    @NotNull(message = "MonthlyCharges is required")
    @DecimalMin(value = "0.0", inclusive = false, message = "MonthlyCharges must be greater than 0")
    @JsonAlias({"monthlyCharges", "MonthlyCharges", "monthly_charges"})
    private Double monthlyCharges = 70.0;

    @JsonAlias({"totalCharges", "TotalCharges", "total_charges"})
    private Double totalCharges;

    public CustomerRequestDto() {}

    // Getters and Setters
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

    public Double getTotalCharges() {
        if (totalCharges == null && monthlyCharges != null && tenure != null) {
            return monthlyCharges * Math.max(1, tenure);
        }
        return totalCharges;
    }
    public void setTotalCharges(Double totalCharges) { this.totalCharges = totalCharges; }
}
