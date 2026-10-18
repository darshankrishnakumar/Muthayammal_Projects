package com.telecom.churn.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "customers")
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "customer_code", unique = true, nullable = false, length = 64)
    private String customerCode;

    @Column(nullable = false, length = 10)
    private String gender;

    @Column(name = "senior_citizen", nullable = false)
    private Integer seniorCitizen;

    @Column(nullable = false, length = 10)
    private String partner;

    @Column(nullable = false, length = 10)
    private String dependents;

    @Column(nullable = false)
    private Integer tenure;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
    }

    public Customer() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

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

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
