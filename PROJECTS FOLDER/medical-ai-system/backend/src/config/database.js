import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import config from './env.js';
import logger from '../utils/logger.js';

let dbInstance = null;

/**
 * Initializes and configures the SQLite database.
 * Safe to run multiple times without duplicating tables.
 *
 * @param {string} dbPath - File path to the SQLite database or ':memory:'
 * @returns {import('better-sqlite3').Database}
 */
export const initDatabase = (dbPath = config.DATABASE_PATH) => {
  if (dbInstance) {
    return dbInstance;
  }

  // Ensure target directory exists for file-based database
  if (dbPath !== ':memory:') {
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  const db = new Database(dbPath);

  // Configure SQLite pragmas for concurrency, integrity, and performance
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  db.pragma('busy_timeout = 5000');

  // Schema creation
  db.exec(`
    -- TABLE 1: measurements
    CREATE TABLE IF NOT EXISTS measurements (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      measurement_type TEXT NOT NULL CHECK(measurement_type IN ('heart_rate', 'blood_pressure', 'spo2', 'body_temperature')),
      numeric_value REAL,
      unit TEXT NOT NULL,
      systolic_value REAL,
      diastolic_value REAL,
      measured_at TEXT NOT NULL,
      source TEXT NOT NULL CHECK(source IN ('manual', 'sensor', 'demo')),
      data_quality_status TEXT NOT NULL DEFAULT 'unverified' CHECK(data_quality_status IN ('unverified', 'valid', 'review_required', 'unreliable')),
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_measurements_type ON measurements(measurement_type);
    CREATE INDEX IF NOT EXISTS idx_measurements_measured_at ON measurements(measured_at);
    CREATE INDEX IF NOT EXISTS idx_measurements_created_at ON measurements(created_at);

    -- TABLE 2: ecg_recordings
    CREATE TABLE IF NOT EXISTS ecg_recordings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      original_filename TEXT NOT NULL,
      stored_filename TEXT NOT NULL UNIQUE,
      file_path TEXT NOT NULL,
      file_format TEXT NOT NULL,
      file_size_bytes INTEGER NOT NULL,
      recording_duration_seconds REAL,
      sampling_frequency_hz REAL,
      source TEXT NOT NULL DEFAULT 'upload',
      upload_status TEXT NOT NULL DEFAULT 'uploaded' CHECK(upload_status IN ('uploaded', 'verified', 'rejected')),
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_ecg_stored_filename ON ecg_recordings(stored_filename);
    CREATE INDEX IF NOT EXISTS idx_ecg_created_at ON ecg_recordings(created_at);

    -- TABLE 3: predictions
    CREATE TABLE IF NOT EXISTS predictions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ecg_recording_id INTEGER NOT NULL REFERENCES ecg_recordings(id) ON DELETE CASCADE,
      model_name TEXT,
      model_version TEXT,
      predicted_class TEXT,
      confidence_score REAL,
      prediction_status TEXT NOT NULL CHECK(prediction_status IN ('pending', 'processing', 'completed', 'failed', 'model_not_connected')),
      explanation TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_predictions_recording ON predictions(ecg_recording_id);
    CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(prediction_status);

    -- TABLE 4: recommendations
    CREATE TABLE IF NOT EXISTS recommendations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE,
      category TEXT NOT NULL CHECK(category IN (
        'general_wellness', 'measurement_review', 'data_quality', 'professional_assessment',
        'General wellness', 'Repeat measurement', 'Review measurement quality', 'Seek professional medical assessment'
      )),
      kind TEXT NOT NULL DEFAULT 'wellness' CHECK(kind IN ('wellness', 'advisory')),
      title TEXT NOT NULL,
      description TEXT NOT NULL,
      suggested_action TEXT NOT NULL,
      related TEXT,
      source_type TEXT NOT NULL DEFAULT 'reviewed_guideline',
      review_status TEXT NOT NULL DEFAULT 'illustrative' CHECK(review_status IN ('illustrative', 'pending_review', 'reviewed', 'inactive', 'clinically_approved')),
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_recommendations_category ON recommendations(category);
    CREATE INDEX IF NOT EXISTS idx_recommendations_review_status ON recommendations(review_status);

    -- TABLE 5: alerts
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE,
      alert_type TEXT NOT NULL CHECK(alert_type IN ('informational', 'data_quality', 'sensor_connection', 'measurement_review', 'model_availability')),
      severity TEXT NOT NULL CHECK(severity IN ('info', 'low', 'medium', 'high', 'review', 'warning')),
      title TEXT NOT NULL,
      description TEXT NOT NULL,
      related_measurement_id INTEGER REFERENCES measurements(id) ON DELETE SET NULL,
      status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'active', 'acknowledged', 'dismissed', 'resolved')),
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
    CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
    CREATE INDEX IF NOT EXISTS idx_alerts_related_measurement ON alerts(related_measurement_id);

    -- TABLE 6: system_events
    CREATE TABLE IF NOT EXISTS system_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      component TEXT NOT NULL,
      event_type TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_system_events_component ON system_events(component);
    CREATE INDEX IF NOT EXISTS idx_system_events_created_at ON system_events(created_at);
  `);

  // Seed baseline reviewed illustrative recommendations if table is empty
  const recCount = db.prepare('SELECT COUNT(*) as count FROM recommendations').get().count;
  if (recCount === 0) {
    const insertRec = db.prepare(`
      INSERT INTO recommendations (code, category, kind, title, description, suggested_action, related, source_type, review_status)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'reviewed_guideline', 'illustrative')
    `);

    insertRec.run(
      'RC-01',
      'General wellness',
      'wellness',
      'Consistent measurement schedule',
      'Consistent measurement timing improves comparability of readings over time.',
      'Take readings at a similar time each day, seated and rested.',
      'All biometric measurements'
    );
    insertRec.run(
      'RC-02',
      'Repeat measurement',
      'advisory',
      'Rest before repeat measurement',
      'Single readings can be affected by movement, posture, or sensor placement.',
      'Repeat the measurement after 5 minutes of quiet rest.',
      'Heart rate · Blood pressure'
    );
    insertRec.run(
      'RC-03',
      'Review measurement quality',
      'advisory',
      'Check electrode contact',
      'ECG traces with motion artefacts may not be suitable for automated analysis.',
      'Check electrode contact and re-record if the trace is noisy.',
      'ECG recording'
    );
    insertRec.run(
      'RC-04',
      'Seek professional medical assessment',
      'advisory',
      'Consult a healthcare provider',
      'Automated results are not a diagnosis. Persistent symptoms warrant clinical review.',
      'Consult a qualified healthcare professional about any concerns.',
      'CNN analysis (pending)'
    );
  }

  // Seed baseline system alerts if table is empty
  const alertCount = db.prepare('SELECT COUNT(*) as count FROM alerts').get().count;
  if (alertCount === 0) {
    const insertAlert = db.prepare(`
      INSERT INTO alerts (code, alert_type, severity, title, description, status)
      VALUES (?, ?, ?, ?, ?, 'open')
    `);

    insertAlert.run(
      'AL-01',
      'informational',
      'info',
      'System initialized in illustrative mode',
      'Backend is running. Biometric measurements and ECG records can be managed. CNN model inference is pending connection.'
    );
    insertAlert.run(
      'AL-02',
      'model_availability',
      'warning',
      'CNN model not connected',
      'No active 1D CNN model adapter is currently attached. Prediction requests will return MODEL_NOT_CONNECTED until configured.'
    );
  }

  // Record startup system event
  db.prepare(`
    INSERT INTO system_events (component, event_type, status)
    VALUES (?, ?, ?)
  `).run('database', 'initialization', 'connected');

  logger.info(`Database connected at ${dbPath === ':memory:' ? 'in-memory' : dbPath}`);
  dbInstance = db;
  return dbInstance;
};

/**
 * Returns current database instance or initializes default one.
 * @returns {import('better-sqlite3').Database}
 */
export const getDatabase = () => {
  if (!dbInstance) {
    return initDatabase();
  }
  return dbInstance;
};

/**
 * Safely closes database connection.
 */
export const closeDatabase = () => {
  if (dbInstance) {
    dbInstance.close();
    dbInstance = null;
  }
};

/**
 * Executes a callback inside a SQLite transaction.
 * Automatically rolls back on error.
 *
 * @template T
 * @param {Function} callback
 * @returns {T}
 */
export const runInTransaction = (callback) => {
  const db = getDatabase();
  const tx = db.transaction(callback);
  return tx();
};

export default {
  initDatabase,
  getDatabase,
  closeDatabase,
  runInTransaction,
};
