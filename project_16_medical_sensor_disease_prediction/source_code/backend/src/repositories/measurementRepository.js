import { getDatabase } from '../config/database.js';

export const measurementRepository = {
  /**
   * Insert a new measurement into the database using parameterized statement.
   */
  create({
    measurementType,
    numericValue = null,
    unit,
    systolicValue = null,
    diastolicValue = null,
    measuredAt,
    source,
    dataQualityStatus = 'unverified',
  }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO measurements (
        measurement_type, numeric_value, unit, systolic_value, diastolic_value,
        measured_at, source, data_quality_status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      measurementType,
      numericValue,
      unit,
      systolicValue,
      diastolicValue,
      measuredAt,
      source,
      dataQualityStatus
    );

    return this.findById(info.lastInsertRowid);
  },

  /**
   * Find measurement by primary key ID.
   */
  findById(id) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        measurement_type as measurementType,
        numeric_value as value,
        unit,
        systolic_value as systolic,
        diastolic_value as diastolic,
        measured_at as measuredAt,
        source,
        data_quality_status as dataQualityStatus,
        created_at as createdAt
      FROM measurements
      WHERE id = ?
    `).get(id);
  },

  /**
   * Find measurements with optional filters and pagination.
   */
  findMany({ measurementType, startDate, endDate, limit = 50, offset = 0 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (measurementType) {
      conditions.push('measurement_type = ?');
      params.push(measurementType);
    }
    if (startDate) {
      conditions.push('measured_at >= ?');
      params.push(startDate);
    }
    if (endDate) {
      conditions.push('measured_at <= ?');
      params.push(endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const stmt = db.prepare(`
      SELECT
        id,
        measurement_type as measurementType,
        numeric_value as value,
        unit,
        systolic_value as systolic,
        diastolic_value as diastolic,
        measured_at as measuredAt,
        source,
        data_quality_status as dataQualityStatus,
        created_at as createdAt
      FROM measurements
      ${whereClause}
      ORDER BY measured_at DESC
      LIMIT ? OFFSET ?
    `);

    return stmt.all(...params, limit, offset);
  },

  /**
   * Count measurements matching filters.
   */
  count({ measurementType, startDate, endDate } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (measurementType) {
      conditions.push('measurement_type = ?');
      params.push(measurementType);
    }
    if (startDate) {
      conditions.push('measured_at >= ?');
      params.push(startDate);
    }
    if (endDate) {
      conditions.push('measured_at <= ?');
      params.push(endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const row = db.prepare(`SELECT COUNT(*) as total FROM measurements ${whereClause}`).get(...params);
    return row.total;
  },

  /**
   * Get latest measurement for a given measurement type.
   */
  getLatestByType(type) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        measurement_type as measurementType,
        numeric_value as value,
        unit,
        systolic_value as systolic,
        diastolic_value as diastolic,
        measured_at as measuredAt,
        source,
        data_quality_status as dataQualityStatus,
        created_at as createdAt
      FROM measurements
      WHERE measurement_type = ?
      ORDER BY measured_at DESC
      LIMIT 1
    `).get(type);
  },

  /**
   * Compute aggregate statistics for a given measurement type.
   */
  getStatisticsByType(type) {
    const db = getDatabase();
    if (type === 'blood_pressure') {
      return db.prepare(`
        SELECT
          COUNT(*) as count,
          MIN(systolic_value) as minSystolic,
          MAX(systolic_value) as maxSystolic,
          ROUND(AVG(systolic_value), 1) as avgSystolic,
          MIN(diastolic_value) as minDiastolic,
          MAX(diastolic_value) as maxDiastolic,
          ROUND(AVG(diastolic_value), 1) as avgDiastolic
        FROM measurements
        WHERE measurement_type = 'blood_pressure'
      `).get();
    }

    return db.prepare(`
      SELECT
        COUNT(*) as count,
        MIN(numeric_value) as min,
        MAX(numeric_value) as max,
        ROUND(AVG(numeric_value), 1) as avg
      FROM measurements
      WHERE measurement_type = ?
    `).get(type);
  },

  /**
   * Get raw chronological measurement points for trend analysis.
   */
  getTimeSeriesPoints({ startDate, endDate, limit = 400 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (startDate) {
      conditions.push('measured_at >= ?');
      params.push(startDate);
    }
    if (endDate) {
      conditions.push('measured_at <= ?');
      params.push(endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        measurement_type as type,
        numeric_value as value,
        systolic_value as systolic,
        diastolic_value as diastolic,
        measured_at as measuredAt
      FROM measurements
      ${whereClause}
      ORDER BY measured_at ASC
      LIMIT ?
    `).all(...params, limit);
  },

  /**
   * Delete a measurement record by ID.
   */
  deleteById(id) {
    const db = getDatabase();
    const info = db.prepare('DELETE FROM measurements WHERE id = ?').run(id);
    return info.changes > 0;
  },

  /**
   * Update a measurement record by ID.
   */
  update(id, { numericValue, systolicValue, diastolicValue, unit, measuredAt, dataQualityStatus }) {
    const db = getDatabase();
    const updates = [];
    const params = [];

    if (numericValue !== undefined) {
      updates.push('numeric_value = ?');
      params.push(numericValue);
    }
    if (systolicValue !== undefined) {
      updates.push('systolic_value = ?');
      params.push(systolicValue);
    }
    if (diastolicValue !== undefined) {
      updates.push('diastolic_value = ?');
      params.push(diastolicValue);
    }
    if (unit !== undefined) {
      updates.push('unit = ?');
      params.push(unit);
    }
    if (measuredAt !== undefined) {
      updates.push('measured_at = ?');
      params.push(measuredAt);
    }
    if (dataQualityStatus !== undefined) {
      updates.push('data_quality_status = ?');
      params.push(dataQualityStatus);
    }

    if (updates.length > 0) {
      params.push(id);
      db.prepare(`UPDATE measurements SET ${updates.join(', ')} WHERE id = ?`).run(...params);
    }

    return this.findById(id);
  },
};

export default measurementRepository;
