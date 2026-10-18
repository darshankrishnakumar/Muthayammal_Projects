package com.telecom.churn.dto;

import com.telecom.churn.entity.PredictionRecord;
import java.util.List;

public class DashboardStatsDto {
    private long totalCustomers;
    private long churnCount;
    private long noChurnCount;
    private double churnRate;
    private double averageMonthlyCharges;
    private double averageTenure;
    private List<PredictionRecord> recentPredictions;

    public DashboardStatsDto() {}

    public long getTotalCustomers() { return totalCustomers; }
    public void setTotalCustomers(long totalCustomers) { this.totalCustomers = totalCustomers; }

    public long getChurnCount() { return churnCount; }
    public void setChurnCount(long churnCount) { this.churnCount = churnCount; }

    public long getNoChurnCount() { return noChurnCount; }
    public void setNoChurnCount(long noChurnCount) { this.noChurnCount = noChurnCount; }

    public double getChurnRate() { return churnRate; }
    public void setChurnRate(double churnRate) { this.churnRate = churnRate; }

    public double getAverageMonthlyCharges() { return averageMonthlyCharges; }
    public void setAverageMonthlyCharges(double averageMonthlyCharges) { this.averageMonthlyCharges = averageMonthlyCharges; }

    public double getAverageTenure() { return averageTenure; }
    public void setAverageTenure(double averageTenure) { this.averageTenure = averageTenure; }

    public List<PredictionRecord> getRecentPredictions() { return recentPredictions; }
    public void setRecentPredictions(List<PredictionRecord> recentPredictions) { this.recentPredictions = recentPredictions; }
}
