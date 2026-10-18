import measurementRepository from '../repositories/measurementRepository.js';
import { runInTransaction } from '../config/database.js';
import { AppError } from '../utils/response.js';

export const healthService = {
  /**
   * Retrieve list of measurements with optional filters.
   */
  getMeasurements({ measurementType, startDate, endDate, limit = 50, offset = 0 } = {}) {
    const total = measurementRepository.count({ measurementType, startDate, endDate });
    const records = measurementRepository.findMany({ measurementType, startDate, endDate, limit, offset });

    return {
      total,
      limit,
      offset,
      records,
    };
  },

  /**
   * Retrieve a single measurement by ID.
   */
  getMeasurementById(id) {
    const record = measurementRepository.findById(id);
    if (!record) {
      throw new AppError(`Measurement with ID ${id} not found.`, 404, 'MEASUREMENT_NOT_FOUND');
    }
    return record;
  },

  /**
   * Determine data quality status based on physiological plausibility bounds.
   */
  assessDataQuality(type, data) {
    if (type === 'heart_rate') {
      const val = data.value;
      if (val < 40 || val > 180) return 'review_required';
    } else if (type === 'blood_pressure') {
      const sys = data.systolic;
      const dia = data.diastolic;
      if (sys < 80 || sys > 190 || dia < 50 || dia > 120) return 'review_required';
    } else if (type === 'spo2') {
      const val = data.value;
      if (val < 88) return 'review_required';
    } else if (type === 'body_temperature') {
      const val = data.value;
      const isCelsius = data.unit === '°C' || data.unit === 'C';
      if (isCelsius && (val < 35.0 || val > 39.5)) return 'review_required';
      if (!isCelsius && (val < 95.0 || val > 103.1)) return 'review_required';
    }
    return 'valid';
  },

  /**
   * Create a measurement record (handles single and compound inputs).
   * Wrapped in SQLite transaction for atomicity.
   */
  createMeasurement(input) {
    const source = input.source || 'manual';
    const timestamp = input.measuredAt || input.timestamp || new Date().toISOString();

    // Compound measurement bundle
    if (!input.measurementType) {
      const created = [];

      runInTransaction(() => {
        if (input.heartRate !== undefined) {
          const quality = this.assessDataQuality('heart_rate', { value: input.heartRate, unit: 'bpm' });
          const rec = measurementRepository.create({
            measurementType: 'heart_rate',
            numericValue: input.heartRate,
            unit: 'bpm',
            measuredAt: timestamp,
            source,
            dataQualityStatus: quality,
          });
          created.push(rec);
        }
        if (input.systolic !== undefined && input.diastolic !== undefined) {
          const quality = this.assessDataQuality('blood_pressure', { systolic: input.systolic, diastolic: input.diastolic, unit: 'mmHg' });
          const rec = measurementRepository.create({
            measurementType: 'blood_pressure',
            unit: 'mmHg',
            systolicValue: input.systolic,
            diastolicValue: input.diastolic,
            measuredAt: timestamp,
            source,
            dataQualityStatus: quality,
          });
          created.push(rec);
        }
        if (input.spo2 !== undefined) {
          const quality = this.assessDataQuality('spo2', { value: input.spo2, unit: '%' });
          const rec = measurementRepository.create({
            measurementType: 'spo2',
            numericValue: input.spo2,
            unit: '%',
            measuredAt: timestamp,
            source,
            dataQualityStatus: quality,
          });
          created.push(rec);
        }
        if (input.temperature !== undefined) {
          const quality = this.assessDataQuality('body_temperature', { value: input.temperature, unit: '°C' });
          const rec = measurementRepository.create({
            measurementType: 'body_temperature',
            numericValue: input.temperature,
            unit: '°C',
            measuredAt: timestamp,
            source,
            dataQualityStatus: quality,
          });
          created.push(rec);
        }
      });

      return {
        timestamp,
        source,
        createdCount: created.length,
        records: created,
      };
    }

    // Single measurement
    const type = input.measurementType;
    const numericValue = input.value !== undefined ? input.value : null;
    const systolic = input.systolic !== undefined ? input.systolic : null;
    const diastolic = input.diastolic !== undefined ? input.diastolic : null;
    const unit = input.unit;

    const quality = this.assessDataQuality(type, {
      value: numericValue,
      systolic,
      diastolic,
      unit,
    });

    return measurementRepository.create({
      measurementType: type,
      numericValue,
      unit,
      systolicValue: systolic,
      diastolicValue: diastolic,
      measuredAt: timestamp,
      source,
      dataQualityStatus: quality,
    });
  },

  /**
   * Latest measurements and summary statistics.
   */
  getSummary() {
    const types = ['heart_rate', 'blood_pressure', 'spo2', 'body_temperature'];
    const summary = {};

    for (const type of types) {
      const latest = measurementRepository.getLatestByType(type);
      const stats = measurementRepository.getStatisticsByType(type);

      summary[type] = {
        latest: latest || null,
        stats: stats || { count: 0 },
      };
    }

    return summary;
  },

  /**
   * Time-series measurement data formatted for Recharts.
   */
  getTrends({ metric = 'heartRate', startDate, endDate, limit = 100 } = {}) {
    const rows = measurementRepository.getTimeSeriesPoints({ startDate, endDate, limit: limit * 4 });

    if (rows.length === 0) {
      return [];
    }

    // Group by timestamp
    const groupMap = new Map();
    for (const r of rows) {
      const ts = r.measuredAt;
      if (!groupMap.has(ts)) {
        groupMap.set(ts, {
          timestamp: ts,
          heartRate: null,
          systolic: null,
          diastolic: null,
          spo2: null,
          temperature: null,
        });
      }
      const item = groupMap.get(ts);
      if (r.type === 'heart_rate') item.heartRate = r.value;
      else if (r.type === 'blood_pressure') {
        item.systolic = r.systolic;
        item.diastolic = r.diastolic;
      } else if (r.type === 'spo2') item.spo2 = r.value;
      else if (r.type === 'body_temperature') item.temperature = r.value;
    }

    return Array.from(groupMap.values()).slice(-limit);
  },

  /**
   * Delete a measurement by ID.
   */
  deleteMeasurement(id) {
    const record = measurementRepository.findById(id);
    if (!record) {
      throw new AppError(`Measurement with ID ${id} not found.`, 404, 'MEASUREMENT_NOT_FOUND');
    }
    measurementRepository.deleteById(id);
    return {
      id: Number(id),
      deleted: true,
      message: 'Measurement record successfully deleted.',
    };
  },

  /**
   * Update an existing measurement by ID.
   */
  updateMeasurement(id, input) {
    const record = measurementRepository.findById(id);
    if (!record) {
      throw new AppError(`Measurement with ID ${id} not found.`, 404, 'MEASUREMENT_NOT_FOUND');
    }

    const type = record.measurementType;
    const value = input.value !== undefined ? input.value : record.value;
    const systolic = input.systolic !== undefined ? input.systolic : record.systolic;
    const diastolic = input.diastolic !== undefined ? input.diastolic : record.diastolic;
    const unit = input.unit !== undefined ? input.unit : record.unit;
    const measuredAt = input.measuredAt || record.measuredAt;

    // Assess quality if values updated
    const quality = this.assessDataQuality(type, {
      value,
      systolic,
      diastolic,
      unit,
    });

    return measurementRepository.update(id, {
      numericValue: value,
      systolicValue: systolic,
      diastolicValue: diastolic,
      unit,
      measuredAt,
      dataQualityStatus: quality,
    });
  },
};

export default healthService;
