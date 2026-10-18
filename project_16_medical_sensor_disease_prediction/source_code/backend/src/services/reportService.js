import measurementRepository from '../repositories/measurementRepository.js';
import ecgRepository from '../repositories/ecgRepository.js';
import predictionRepository from '../repositories/predictionRepository.js';
import recommendationRepository from '../repositories/recommendationRepository.js';
import alertRepository from '../repositories/alertRepository.js';
import { getDatabase } from '../config/database.js';

export const reportService = {
  /**
   * Summary report metrics across measurements, recordings, predictions, recommendations.
   */
  getSummaryReport({ startDate, endDate } = {}) {
    const db = getDatabase();

    // Measurement counts and breakdowns
    const totalMeasurements = measurementRepository.count({ startDate, endDate });

    const mConditions = [];
    const mParams = [];
    if (startDate) {
      mConditions.push('measured_at >= ?');
      mParams.push(startDate);
    }
    if (endDate) {
      mConditions.push('measured_at <= ?');
      mParams.push(endDate);
    }
    const mWhere = mConditions.length > 0 ? `WHERE ${mConditions.join(' AND ')}` : '';

    const measurementsByType = db.prepare(`
      SELECT measurement_type as type, COUNT(*) as count
      FROM measurements
      ${mWhere}
      GROUP BY measurement_type
    `).all(...mParams);

    const dataQualityBreakdown = db.prepare(`
      SELECT data_quality_status as status, COUNT(*) as count
      FROM measurements
      ${mWhere}
      GROUP BY data_quality_status
    `).all(...mParams);

    // ECG recording counts
    const totalEcgRecordings = ecgRepository.count();
    const ecgByFormat = db.prepare(`
      SELECT file_format as format, COUNT(*) as count
      FROM ecg_recordings
      GROUP BY file_format
    `).all();

    // Prediction counts
    const totalPredictions = predictionRepository.count();
    const predictionsByStatus = predictionRepository.countByStatus();

    // Recommendations count
    const totalRecommendations = recommendationRepository.count();

    // Active/Open alerts count
    const activeAlerts = alertRepository.count({ status: 'open' });

    return {
      generatedAt: new Date().toISOString(),
      dateRange: {
        startDate: startDate || null,
        endDate: endDate || null,
      },
      summary: {
        totalMeasurements,
        measurementsByType: Object.fromEntries(measurementsByType.map((r) => [r.type, r.count])),
        dataQualityBreakdown: Object.fromEntries(dataQualityBreakdown.map((r) => [r.status, r.count])),
        totalEcgRecordings,
        ecgByFormat: Object.fromEntries(ecgByFormat.map((r) => [r.format, r.count])),
        totalPredictions,
        predictionsByStatus,
        totalRecommendations,
        activeAlerts,
      },
      systemNotes: {
        cnnModelStatus: 'not_connected',
        reportType: 'Aggregated Operational Metric Report',
        clinicalNotice: 'This report contains verified recorded system metrics. Automated diagnostic predictions are marked according to model connection state.',
      },
    };
  },

  /**
   * Detailed measurements data report.
   */
  getMeasurementReport({ startDate, endDate, limit = 200 } = {}) {
    const records = measurementRepository.findMany({ startDate, endDate, limit, offset: 0 });

    return {
      totalReturned: records.length,
      records,
    };
  },
};

export default reportService;
