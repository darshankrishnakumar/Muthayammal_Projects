import { getDatabase } from '../config/database.js';

export const alertRepository = {
  /**
   * Create an alert record.
   */
  create({
    code = null,
    alertType,
    severity,
    title,
    description,
    relatedMeasurementId = null,
    status = 'open',
  }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO alerts (
        code, alert_type, severity, title, description,
        related_measurement_id, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      code,
      alertType,
      severity,
      title,
      description,
      relatedMeasurementId,
      status
    );

    return this.findById(info.lastInsertRowid);
  },

  /**
   * Find alert by primary key ID.
   */
  findById(id) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        code,
        alert_type as alertType,
        severity,
        title,
        description,
        related_measurement_id as relatedMeasurementId,
        status,
        created_at as createdAt
      FROM alerts
      WHERE id = ?
    `).get(id);
  },

  /**
   * Find alert by code or numeric ID.
   */
  findByCodeOrId(codeOrId) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        code,
        alert_type as alertType,
        severity,
        title,
        description,
        related_measurement_id as relatedMeasurementId,
        status,
        created_at as createdAt
      FROM alerts
      WHERE id = ? OR code = ?
    `).get(codeOrId, codeOrId);
  },

  /**
   * Find multiple alerts ordered chronologically.
   */
  findMany({ status, severity, alertType, limit = 50, offset = 0 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('status = ?');
      params.push(status);
    }
    if (severity) {
      conditions.push('severity = ?');
      params.push(severity);
    }
    if (alertType) {
      conditions.push('alert_type = ?');
      params.push(alertType);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        id,
        code,
        alert_type as alertType,
        severity,
        title,
        description,
        related_measurement_id as relatedMeasurementId,
        status,
        created_at as createdAt
      FROM alerts
      ${whereClause}
      ORDER BY id DESC
      LIMIT ? OFFSET ?
    `).all(...params, limit, offset);
  },

  /**
   * Update status of an alert.
   */
  updateStatus(id, newStatus) {
    const db = getDatabase();
    db.prepare('UPDATE alerts SET status = ? WHERE id = ?').run(newStatus, id);
    return this.findById(id);
  },

  /**
   * Count alerts matching criteria.
   */
  count({ status, severity } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('status = ?');
      params.push(status);
    }
    if (severity) {
      conditions.push('severity = ?');
      params.push(severity);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const row = db.prepare(`SELECT COUNT(*) as total FROM alerts ${whereClause}`).get(...params);
    return row.total;
  },
};

export default alertRepository;
