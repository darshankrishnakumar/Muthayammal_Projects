import { getDatabase } from '../config/database.js';

export const predictionRepository = {
  /**
   * Save a genuine prediction result.
   */
  create({
    ecgRecordingId,
    modelName = null,
    modelVersion = null,
    predictedClass = null,
    confidenceScore = null,
    predictionStatus,
    explanation = null,
  }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO predictions (
        ecg_recording_id, model_name, model_version, predicted_class,
        confidence_score, prediction_status, explanation
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      ecgRecordingId,
      modelName,
      modelVersion,
      predictedClass,
      confidenceScore,
      predictionStatus,
      explanation
    );

    return this.findById(info.lastInsertRowid);
  },

  /**
   * Find prediction by ID.
   */
  findById(id) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        p.id,
        p.ecg_recording_id as ecgRecordingId,
        r.original_filename as originalFilename,
        p.model_name as modelName,
        p.model_version as modelVersion,
        p.predicted_class as predictedClass,
        p.predicted_class as predictedCategory,
        p.confidence_score as confidenceScore,
        p.confidence_score as confidence,
        p.prediction_status as predictionStatus,
        p.explanation,
        p.created_at as createdAt
      FROM predictions p
      LEFT JOIN ecg_recordings r ON r.id = p.ecg_recording_id
      WHERE p.id = ?
    `).get(id);
  },

  /**
   * Find predictions for a specific ECG recording.
   */
  findByRecordingId(recordingId) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        p.id,
        p.ecg_recording_id as ecgRecordingId,
        p.model_name as modelName,
        p.model_version as modelVersion,
        p.predicted_class as predictedClass,
        p.confidence_score as confidenceScore,
        p.prediction_status as predictionStatus,
        p.explanation,
        p.created_at as createdAt
      FROM predictions p
      WHERE p.ecg_recording_id = ?
      ORDER BY p.id DESC
    `).all(recordingId);
  },

  /**
   * Find multiple predictions with pagination.
   */
  findMany({ status, limit = 20, offset = 0 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('p.prediction_status = ?');
      params.push(status);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        p.id,
        p.ecg_recording_id as ecgRecordingId,
        r.original_filename as originalFilename,
        p.model_name as modelName,
        p.model_version as modelVersion,
        p.predicted_class as predictedClass,
        p.confidence_score as confidenceScore,
        p.prediction_status as predictionStatus,
        p.explanation,
        p.created_at as createdAt
      FROM predictions p
      LEFT JOIN ecg_recordings r ON r.id = p.ecg_recording_id
      ${whereClause}
      ORDER BY p.id DESC
      LIMIT ? OFFSET ?
    `).all(...params, limit, offset);
  },

  /**
   * Count predictions by status.
   */
  countByStatus() {
    const db = getDatabase();
    const rows = db.prepare(`
      SELECT prediction_status as status, COUNT(*) as count
      FROM predictions
      GROUP BY prediction_status
    `).all();

    return Object.fromEntries(rows.map((r) => [r.status, r.count]));
  },

  /**
   * Total count of prediction records.
   */
  count({ status } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('prediction_status = ?');
      params.push(status);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const row = db.prepare(`SELECT COUNT(*) as total FROM predictions ${whereClause}`).get(...params);
    return row.total;
  },

  /**
   * Retrieve prediction history.
   */
  getHistory(limit = 50) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        p.id,
        p.ecg_recording_id as recordingId,
        p.prediction_status as status,
        p.model_name as modelName,
        p.model_version as modelVersion,
        p.predicted_class as predictedCategory,
        p.confidence_score as confidence,
        p.created_at as analysedAt,
        p.explanation
      FROM predictions p
      ORDER BY p.id DESC
      LIMIT ?
    `).all(limit);
  },
};

export default predictionRepository;
