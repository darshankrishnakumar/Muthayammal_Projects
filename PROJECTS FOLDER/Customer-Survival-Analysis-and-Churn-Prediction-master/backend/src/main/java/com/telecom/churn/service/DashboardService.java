package com.telecom.churn.service;

import com.telecom.churn.dto.DashboardStatsDto;
import com.telecom.churn.entity.PredictionRecord;
import com.telecom.churn.repository.PredictionRecordRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DashboardService {

    private final PredictionRecordRepository repository;

    public DashboardService(PredictionRecordRepository repository) {
        this.repository = repository;
    }

    public DashboardStatsDto getDashboardStats() {
        DashboardStatsDto stats = new DashboardStatsDto();
        long total = repository.count();
        long churn = repository.countByPredictedClass("Churn");
        long noChurn = total - churn;

        stats.setTotalCustomers(total);
        stats.setChurnCount(churn);
        stats.setNoChurnCount(noChurn);

        double rate = total > 0 ? ((double) churn / total) * 100.0 : 0.0;
        stats.setChurnRate(Math.round(rate * 100.0) / 100.0);

        Double avgMonthly = repository.getAverageMonthlyCharges();
        stats.setAverageMonthlyCharges(avgMonthly != null ? Math.round(avgMonthly * 100.0) / 100.0 : 0.0);

        Double avgTenure = repository.getAverageTenure();
        stats.setAverageTenure(avgTenure != null ? Math.round(avgTenure * 10.0) / 10.0 : 0.0);

        List<PredictionRecord> all = repository.findAllByOrderByTimestampDesc();
        stats.setRecentPredictions(all.stream().limit(10).toList());

        return stats;
    }
}
