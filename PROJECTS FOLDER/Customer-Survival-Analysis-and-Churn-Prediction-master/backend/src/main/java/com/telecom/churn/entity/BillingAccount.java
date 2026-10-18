package com.telecom.churn.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "billing_accounts")
public class BillingAccount {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "contract_type", nullable = false, length = 30)
    private String contractType;

    @Column(name = "paperless_billing", nullable = false, length = 10)
    private String paperlessBilling;

    @Column(name = "payment_method", nullable = false, length = 50)
    private String paymentMethod;

    @Column(name = "monthly_charges", nullable = false)
    private Double monthlyCharges;

    @Column(name = "total_charges", nullable = false)
    private Double totalCharges;

    public BillingAccount() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getCustomerId() { return customerId; }
    public void setCustomerId(Long customerId) { this.customerId = customerId; }

    public String getContractType() { return contractType; }
    public void setContractType(String contractType) { this.contractType = contractType; }

    public String getPaperlessBilling() { return paperlessBilling; }
    public void setPaperlessBilling(String paperlessBilling) { this.paperlessBilling = paperlessBilling; }

    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }

    public Double getMonthlyCharges() { return monthlyCharges; }
    public void setMonthlyCharges(Double monthlyCharges) { this.monthlyCharges = monthlyCharges; }

    public Double getTotalCharges() { return totalCharges; }
    public void setTotalCharges(Double totalCharges) { this.totalCharges = totalCharges; }
}
