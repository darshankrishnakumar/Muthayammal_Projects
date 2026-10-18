package com.telecom.churn.repository;

import com.telecom.churn.entity.PredictionRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PredictionRecordRepository extends JpaRepository<PredictionRecord, Long> {

    List<PredictionRecord> findAllByOrderByTimestampDesc();

    long countByPredictedClass(String predictedClass);

    @Query("SELECT AVG(p.monthlyCharges) FROM PredictionRecord p")
    Double getAverageMonthlyCharges();

    @Query("SELECT AVG(p.tenure) FROM PredictionRecord p")
    Double getAverageTenure();
}
