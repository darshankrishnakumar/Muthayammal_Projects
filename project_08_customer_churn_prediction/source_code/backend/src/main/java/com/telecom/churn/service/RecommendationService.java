package com.telecom.churn.service;

import com.telecom.churn.dto.CustomerRequestDto;
import org.springframework.stereotype.Service;

@Service
public class RecommendationService {

    public String generateRecommendation(String riskLevel, Double probability, CustomerRequestDto customer) {
        StringBuilder sb = new StringBuilder();

        if ("High".equalsIgnoreCase(riskLevel)) {
            sb.append("High churn risk detected (").append(String.format("%.1f", probability * 100)).append("%). ");
            if ("Month-to-month".equalsIgnoreCase(customer.getContract())) {
                sb.append("Customer is on a Month-to-month contract; consider offering an annual commitment incentive or discount plan. ");
            }
            if ("Fiber optic".equalsIgnoreCase(customer.getInternetService()) && customer.getMonthlyCharges() > 80.0) {
                sb.append("Customer has premium monthly billing ($")
                  .append(String.format("%.2f", customer.getMonthlyCharges()))
                  .append("); evaluate service bundle options to improve price satisfaction. ");
            }
            if ("No".equalsIgnoreCase(customer.getTechSupport())) {
                sb.append("Tech Support is not activated; offering complimentary onboarding assistance may strengthen customer retention. ");
            }
            if (customer.getTenure() != null && customer.getTenure() <= 12) {
                sb.append("Customer is in early lifecycle tenure (").append(customer.getTenure()).append(" months); schedule a proactive retention check-in call.");
            } else {
                sb.append("Review available customer service records and explore suitable contract plan updates.");
            }
        } else if ("Medium".equalsIgnoreCase(riskLevel)) {
            sb.append("Moderate churn risk (").append(String.format("%.1f", probability * 100)).append("%). ");
            if ("Month-to-month".equalsIgnoreCase(customer.getContract())) {
                sb.append("Evaluate eligibility for term contract promotions or digital loyalty rewards. ");
            }
            sb.append("Monitor customer engagement and maintain responsive customer support touchpoints.");
        } else {
            sb.append("Low churn risk (").append(String.format("%.1f", probability * 100)).append("%). ");
            sb.append("Customer exhibits high stability. Maintain regular service quality and standard engagement notifications.");
        }

        return sb.toString().trim();
    }
}
