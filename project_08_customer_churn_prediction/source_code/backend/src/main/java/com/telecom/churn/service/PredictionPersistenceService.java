package com.telecom.churn.service;

import com.telecom.churn.dto.CustomerRequestDto;
import com.telecom.churn.dto.MlPredictionResponseDto;
import com.telecom.churn.entity.BillingAccount;
import com.telecom.churn.entity.Customer;
import com.telecom.churn.entity.CustomerServiceEntity;
import com.telecom.churn.entity.PredictionRecord;
import com.telecom.churn.repository.BillingAccountRepository;
import com.telecom.churn.repository.CustomerRepository;
import com.telecom.churn.repository.CustomerServiceRepository;
import com.telecom.churn.repository.PredictionRecordRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class PredictionPersistenceService {

    private static final Logger log = LoggerFactory.getLogger(PredictionPersistenceService.class);

    private final CustomerRepository customerRepo;
    private final CustomerServiceRepository serviceRepo;
    private final BillingAccountRepository billingRepo;
    private final PredictionRecordRepository predictionRepo;

    public PredictionPersistenceService(CustomerRepository customerRepo,
                                        CustomerServiceRepository serviceRepo,
                                        BillingAccountRepository billingRepo,
                                        PredictionRecordRepository predictionRepo) {
        this.customerRepo = customerRepo;
        this.serviceRepo = serviceRepo;
        this.billingRepo = billingRepo;
        this.predictionRepo = predictionRepo;
    }

    @Transactional
    public PredictionRecord savePredictionTransaction(CustomerRequestDto request,
                                                       MlPredictionResponseDto mlResponse,
                                                       String riskLevel,
                                                       Double probability,
                                                       String recommendation) {
        String customerCode = "CUST-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();

        // 1. Relational Customer Record
        Customer customer = new Customer();
        customer.setCustomerCode(customerCode);
        customer.setGender(request.getGender());
        customer.setSeniorCitizen(request.getSeniorCitizen());
        customer.setPartner(request.getPartner());
        customer.setDependents(request.getDependents());
        customer.setTenure(request.getTenure());
        Customer savedCustomer = customerRepo.save(customer);

        // 2. Relational Customer Services Record
        CustomerServiceEntity serviceEntity = new CustomerServiceEntity();
        serviceEntity.setCustomerId(savedCustomer.getId());
        serviceEntity.setPhoneService(request.getPhoneService());
        serviceEntity.setMultipleLines(request.getMultipleLines());
        serviceEntity.setInternetService(request.getInternetService());
        serviceEntity.setOnlineSecurity(request.getOnlineSecurity());
        serviceEntity.setOnlineBackup(request.getOnlineBackup());
        serviceEntity.setDeviceProtection(request.getDeviceProtection());
        serviceEntity.setTechSupport(request.getTechSupport());
        serviceEntity.setStreamingTV(request.getStreamingTV());
        serviceEntity.setStreamingMovies(request.getStreamingMovies());
        serviceRepo.save(serviceEntity);

        // 3. Relational Billing Account Record
        BillingAccount billing = new BillingAccount();
        billing.setCustomerId(savedCustomer.getId());
        billing.setContractType(request.getContract());
        billing.setPaperlessBilling(request.getPaperlessBilling());
        billing.setPaymentMethod(request.getPaymentMethod());
        billing.setMonthlyCharges(request.getMonthlyCharges());
        billing.setTotalCharges(request.getTotalCharges());
        billingRepo.save(billing);

        // 4. Historical Prediction Audit Record
        PredictionRecord record = new PredictionRecord();
        record.setCustomerCode(customerCode);
        record.setTimestamp(LocalDateTime.now());
        record.setPredictedClass(mlResponse.getPrediction());
        record.setChurnProbability(probability);
        record.setRiskLevel(riskLevel);
        record.setRecommendation(recommendation);
        record.setModelVersion(mlResponse.getModel() != null ? mlResponse.getModel() : "Random Forest");

        record.setGender(request.getGender());
        record.setSeniorCitizen(request.getSeniorCitizen());
        record.setPartner(request.getPartner());
        record.setDependents(request.getDependents());
        record.setTenure(request.getTenure());
        record.setPhoneService(request.getPhoneService());
        record.setMultipleLines(request.getMultipleLines());
        record.setInternetService(request.getInternetService());
        record.setOnlineSecurity(request.getOnlineSecurity());
        record.setOnlineBackup(request.getOnlineBackup());
        record.setDeviceProtection(request.getDeviceProtection());
        record.setTechSupport(request.getTechSupport());
        record.setStreamingTV(request.getStreamingTV());
        record.setStreamingMovies(request.getStreamingMovies());
        record.setContract(request.getContract());
        record.setPaperlessBilling(request.getPaperlessBilling());
        record.setPaymentMethod(request.getPaymentMethod());
        record.setMonthlyCharges(request.getMonthlyCharges());
        record.setTotalCharges(request.getTotalCharges());

        PredictionRecord savedRecord = predictionRepo.save(record);
        log.info("Persisted transactional prediction with ID: {}, Customer Code: {}", savedRecord.getId(), customerCode);
        return savedRecord;
    }
}
