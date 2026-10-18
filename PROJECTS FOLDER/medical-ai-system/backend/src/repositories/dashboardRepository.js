import measurementRepository from './measurementRepository.js';
import ecgRepository from './ecgRepository.js';
import predictionRepository from './predictionRepository.js';
import alertRepository from './alertRepository.js';
import recommendationRepository from './recommendationRepository.js';

export const dashboardRepository = {
  /**
   * Retrieves aggregated dashboard state strictly from genuine database records.
   * If records are missing, returns NULL or empty collections without synthetic data.
   */
  getDashboardOverview() {
    // 1. Latest vitals (heart rate, blood pressure, spo2, body temperature)
    const latestHeartRate = measurementRepository.getLatestByType('heart_rate');
    const latestBloodPressure = measurementRepository.getLatestByType('blood_pressure');
    const latestSpo2 = measurementRepository.getLatestByType('spo2');
    const latestTemperature = measurementRepository.getLatestByType('body_temperature');

    // 2. ECG recording count
    const ecgRecordingCount = ecgRepository.count();

    // 3. Genuine prediction history and status breakdown
    const predictionHistory = predictionRepository.getHistory(10);
    const predictionStatusCounts = predictionRepository.countByStatus();

    // 4. Open alerts
    const openAlerts = alertRepository.findMany({ status: 'open', limit: 10 });

    // 5. Available recommendations
    const recommendations = recommendationRepository.findMany({ reviewStatus: 'illustrative' });

    return {
      vitals: {
        heartRate: latestHeartRate ? {
          value: latestHeartRate.value,
          unit: latestHeartRate.unit,
          measuredAt: latestHeartRate.measuredAt,
          status: latestHeartRate.dataQualityStatus,
        } : null,
        bloodPressure: latestBloodPressure ? {
          systolic: latestBloodPressure.systolic,
          diastolic: latestBloodPressure.diastolic,
          unit: latestBloodPressure.unit,
          measuredAt: latestBloodPressure.measuredAt,
          status: latestBloodPressure.dataQualityStatus,
        } : null,
        spo2: latestSpo2 ? {
          value: latestSpo2.value,
          unit: latestSpo2.unit,
          measuredAt: latestSpo2.measuredAt,
          status: latestSpo2.dataQualityStatus,
        } : null,
        temperature: latestTemperature ? {
          value: latestTemperature.value,
          unit: latestTemperature.unit,
          measuredAt: latestTemperature.measuredAt,
          status: latestTemperature.dataQualityStatus,
        } : null,
      },
      analytics: {
        totalEcgRecordings: ecgRecordingCount,
        predictionStatusCounts,
        recentPredictions: predictionHistory,
        openAlerts,
        recommendations,
      },
    };
  },
};

export default dashboardRepository;
