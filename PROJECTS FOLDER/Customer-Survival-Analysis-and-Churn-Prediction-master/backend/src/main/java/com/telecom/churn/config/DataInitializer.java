package com.telecom.churn.config;

import com.telecom.churn.entity.PredictionRecord;
import com.telecom.churn.repository.PredictionRecordRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDateTime;

@Configuration
public class DataInitializer {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    @Bean
    public CommandLineRunner initDatabase(PredictionRecordRepository repository) {
        return args -> {
            if (repository.count() == 0) {
                log.info("Initializing baseline prediction history records for dashboard...");

                saveRecord(repository, "Female", 0, "Yes", "No", 1, "No", "No phone service",
                        "DSL", "No", "Yes", "No", "No", "No", "No", "Month-to-month", "Yes",
                        "Electronic check", 29.85, 29.85, "Churn", 0.61, "Medium",
                        "Moderate churn risk (61.0%). Evaluate eligibility for term contract promotions.",
                        LocalDateTime.now().minusHours(24));

                saveRecord(repository, "Male", 0, "No", "No", 34, "Yes", "No",
                        "DSL", "Yes", "No", "Yes", "No", "No", "No", "One year", "No",
                        "Mailed check", 56.95, 1889.50, "No Churn", 0.22, "Low",
                        "Low churn risk (22.0%). Customer exhibits high stability. Maintain regular service quality.",
                        LocalDateTime.now().minusHours(20));

                saveRecord(repository, "Male", 0, "No", "No", 2, "Yes", "No",
                        "DSL", "Yes", "Yes", "No", "No", "No", "No", "Month-to-month", "Yes",
                        "Mailed check", 53.85, 108.15, "Churn", 0.72, "High",
                        "High churn risk detected (72.0%). Customer is on a Month-to-month contract; consider offering an annual commitment incentive.",
                        LocalDateTime.now().minusHours(18));

                saveRecord(repository, "Male", 0, "No", "No", 45, "No", "No phone service",
                        "DSL", "Yes", "No", "Yes", "Yes", "No", "No", "One year", "No",
                        "Bank transfer (automatic)", 42.30, 1840.75, "No Churn", 0.18, "Low",
                        "Low churn risk (18.0%). Customer exhibits high stability.",
                        LocalDateTime.now().minusHours(14));

                saveRecord(repository, "Female", 0, "No", "No", 2, "Yes", "No",
                        "Fiber optic", "No", "No", "No", "No", "No", "No", "Month-to-month", "Yes",
                        "Electronic check", 70.70, 151.65, "Churn", 0.84, "High",
                        "High churn risk detected (84.0%). Customer is on a Month-to-month contract with premium fiber billing; schedule proactive outreach.",
                        LocalDateTime.now().minusHours(10));

                saveRecord(repository, "Female", 0, "No", "No", 8, "Yes", "Yes",
                        "Fiber optic", "No", "No", "Yes", "No", "Yes", "Yes", "Month-to-month", "Yes",
                        "Electronic check", 99.65, 820.50, "Churn", 0.79, "High",
                        "High churn risk detected (79.0%). Customer is on a Month-to-month contract with high monthly charges ($99.65).",
                        LocalDateTime.now().minusHours(6));

                saveRecord(repository, "Male", 0, "No", "Yes", 22, "Yes", "Yes",
                        "Fiber optic", "No", "Yes", "No", "No", "Yes", "No", "Month-to-month", "Yes",
                        "Credit card (automatic)", 89.10, 1949.40, "No Churn", 0.38, "Medium",
                        "Moderate churn risk (38.0%). Evaluate eligibility for digital loyalty rewards.",
                        LocalDateTime.now().minusHours(3));

                saveRecord(repository, "Female", 0, "No", "No", 10, "No", "No phone service",
                        "DSL", "Yes", "No", "No", "No", "No", "No", "Month-to-month", "No",
                        "Mailed check", 29.75, 301.90, "No Churn", 0.32, "Low",
                        "Low churn risk (32.0%). Customer exhibits high stability.",
                        LocalDateTime.now().minusHours(1));

                log.info("Finished seeding baseline prediction records.");
            }
        };
    }

    private void saveRecord(PredictionRecordRepository repo, String gender, int senior, String partner,
                            String dependents, int tenure, String phone, String lines, String internet,
                            String sec, String backup, String dev, String tech, String tv, String movies,
                            String contract, String paperless, String payment, double monthly, double total,
                            String pred, double prob, String risk, String rec, LocalDateTime time) {
        PredictionRecord r = new PredictionRecord();
        r.setGender(gender);
        r.setSeniorCitizen(senior);
        r.setPartner(partner);
        r.setDependents(dependents);
        r.setTenure(tenure);
        r.setPhoneService(phone);
        r.setMultipleLines(lines);
        r.setInternetService(internet);
        r.setOnlineSecurity(sec);
        r.setOnlineBackup(backup);
        r.setDeviceProtection(dev);
        r.setTechSupport(tech);
        r.setStreamingTV(tv);
        r.setStreamingMovies(movies);
        r.setContract(contract);
        r.setPaperlessBilling(paperless);
        r.setPaymentMethod(payment);
        r.setMonthlyCharges(monthly);
        r.setTotalCharges(total);
        r.setPredictedClass(pred);
        r.setChurnProbability(prob);
        r.setRiskLevel(risk);
        r.setRecommendation(rec);
        r.setModelVersion("Random Forest");
        r.setTimestamp(time);
        repo.save(r);
    }
}
