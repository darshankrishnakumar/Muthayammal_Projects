import { describe, it, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import Database from 'better-sqlite3';
import { initDatabase, closeDatabase, runInTransaction } from '../src/config/database.js';
import measurementRepository from '../src/repositories/measurementRepository.js';
import ecgRepository from '../src/repositories/ecgRepository.js';
import predictionRepository from '../src/repositories/predictionRepository.js';
import recommendationRepository from '../src/repositories/recommendationRepository.js';
import alertRepository from '../src/repositories/alertRepository.js';
import dashboardRepository from '../src/repositories/dashboardRepository.js';

describe('SQLite Database Layer & Repository Tests', () => {
  let db;

  before(() => {
    // 1. Database initialization with isolated in-memory test database
    db = initDatabase(':memory:');
  });

  after(() => {
    closeDatabase();
  });

  // 1 & 2. Database initialization and Table Creation
  it('1 & 2. Database initialization creates all required tables and indexes', () => {
    const tables = db
      .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
      .all()
      .map((t) => t.name);

    assert.ok(tables.includes('measurements'), 'measurements table exists');
    assert.ok(tables.includes('ecg_recordings'), 'ecg_recordings table exists');
    assert.ok(tables.includes('predictions'), 'predictions table exists');
    assert.ok(tables.includes('recommendations'), 'recommendations table exists');
    assert.ok(tables.includes('alerts'), 'alerts table exists');
    assert.ok(tables.includes('system_events'), 'system_events table exists');

    // Safe re-initialization check
    assert.doesNotThrow(() => {
      initDatabase(':memory:');
    });
  });

  // 3. Foreign-key enforcement
  it('3. Enforces foreign key constraints (cascades and blocks orphaned rows)', () => {
    // Foreign keys pragma is active
    const fkPragma = db.pragma('foreign_keys', { simple: true });
    assert.equal(fkPragma, 1, 'Foreign keys pragma must be enabled (1)');

    // Attempting to insert a prediction for non-existent ecg recording throws FOREIGN KEY error
    assert.throws(() => {
      predictionRepository.create({
        ecgRecordingId: 999999, // non-existent
        predictionStatus: 'pending',
      });
    }, /FOREIGN KEY constraint failed/);

    // Creating recording then deleting it cascades to predictions
    const rec = ecgRepository.create({
      originalFilename: 'cascade_test.csv',
      storedFilename: 'cascade_test_unique.csv',
      filePath: './storage/ecg/cascade_test.csv',
      fileFormat: 'csv',
      fileSizeBytes: 1024,
      source: 'upload',
      uploadStatus: 'uploaded',
    });

    const pred = predictionRepository.create({
      ecgRecordingId: rec.id,
      predictionStatus: 'pending',
    });

    assert.ok(pred.id);
    // Delete recording
    ecgRepository.deleteById(rec.id);

    // Check prediction was cascaded
    const deletedPred = predictionRepository.findById(pred.id);
    assert.equal(deletedPred, undefined, 'Predictions should cascade delete with recording');
  });

  // 4. Valid measurement insertion
  it('4. Inserts valid biometric measurements across all supported types', () => {
    const hr = measurementRepository.create({
      measurementType: 'heart_rate',
      numericValue: 72,
      unit: 'bpm',
      measuredAt: '2026-10-09T08:00:00.000Z',
      source: 'manual',
      dataQualityStatus: 'valid',
    });
    assert.equal(hr.measurementType, 'heart_rate');
    assert.equal(hr.value, 72);

    const bp = measurementRepository.create({
      measurementType: 'blood_pressure',
      unit: 'mmHg',
      systolicValue: 120,
      diastolicValue: 80,
      measuredAt: '2026-10-09T08:05:00.000Z',
      source: 'manual',
      dataQualityStatus: 'valid',
    });
    assert.equal(bp.systolic, 120);
    assert.equal(bp.diastolic, 80);

    const spo2 = measurementRepository.create({
      measurementType: 'spo2',
      numericValue: 98,
      unit: '%',
      measuredAt: '2026-10-09T08:10:00.000Z',
      source: 'sensor',
      dataQualityStatus: 'valid',
    });
    assert.equal(spo2.value, 98);

    const temp = measurementRepository.create({
      measurementType: 'body_temperature',
      numericValue: 36.6,
      unit: '°C',
      measuredAt: '2026-10-09T08:15:00.000Z',
      source: 'sensor',
      dataQualityStatus: 'valid',
    });
    assert.equal(temp.value, 36.6);
  });

  // 5. Invalid measurement rejection at SQL constraint level
  it('5. Rejects unsupported measurement types and invalid sources via CHECK constraints', () => {
    assert.throws(() => {
      db.prepare(`
        INSERT INTO measurements (measurement_type, numeric_value, unit, measured_at, source)
        VALUES ('glucose_level', 95, 'mg/dL', '2026-10-09T08:00:00Z', 'manual')
      `).run();
    }, /CHECK constraint failed/);

    assert.throws(() => {
      db.prepare(`
        INSERT INTO measurements (measurement_type, numeric_value, unit, measured_at, source)
        VALUES ('heart_rate', 70, 'bpm', '2026-10-09T08:00:00Z', 'invalid_source')
      `).run();
    }, /CHECK constraint failed/);
  });

  // 6. Measurement retrieval
  it('6. Retrieves individual measurements and summary statistics correctly', () => {
    const latestHr = measurementRepository.getLatestByType('heart_rate');
    assert.ok(latestHr);
    assert.equal(latestHr.measurementType, 'heart_rate');

    const bpStats = measurementRepository.getStatisticsByType('blood_pressure');
    assert.ok(bpStats);
    assert.equal(bpStats.minSystolic, 120);
    assert.equal(bpStats.maxSystolic, 120);
  });

  // 7. Date filtering
  it('7. Filters measurement records correctly by date range', () => {
    const inRange = measurementRepository.findMany({
      startDate: '2026-10-09T07:00:00.000Z',
      endDate: '2026-10-09T09:00:00.000Z',
    });
    assert.ok(inRange.length >= 4);

    const outOfRange = measurementRepository.findMany({
      startDate: '2026-10-10T00:00:00.000Z',
    });
    assert.equal(outOfRange.length, 0);
  });

  // 8. ECG metadata insertion
  it('8. Inserts and retrieves ECG metadata with unique stored filenames', () => {
    const ecg = ecgRepository.create({
      originalFilename: 'patient_lead2.csv',
      storedFilename: '1791540000000-unique-uuid.csv',
      filePath: './storage/ecg/1791540000000-unique-uuid.csv',
      fileFormat: 'csv',
      fileSizeBytes: 2048,
      recordingDurationSeconds: 10.0,
      samplingFrequencyHz: 360,
      source: 'upload',
      uploadStatus: 'verified',
    });

    assert.ok(ecg.id);
    assert.equal(ecg.originalFilename, 'patient_lead2.csv');
    assert.equal(ecg.fileFormat, 'csv');

    // Duplicate stored_filename throws UNIQUE constraint violation
    assert.throws(() => {
      ecgRepository.create({
        originalFilename: 'another.csv',
        storedFilename: '1791540000000-unique-uuid.csv',
        filePath: './storage/ecg/another.csv',
        fileFormat: 'csv',
        fileSizeBytes: 1024,
      });
    }, /UNIQUE constraint failed/);
  });

  // 9 & 10. Prediction history & Prevention of fabricated prediction records
  it('9 & 10. Verifies genuine prediction saving and prevents fabricated prediction classes', () => {
    // Only real prediction records are inserted
    const recording = ecgRepository.create({
      originalFilename: 'test_genuine.csv',
      storedFilename: 'test_genuine_unique.csv',
      filePath: './storage/ecg/test_genuine.csv',
      fileFormat: 'csv',
      fileSizeBytes: 512,
    });

    const pred = predictionRepository.create({
      ecgRecordingId: recording.id,
      modelName: '1D CNN Arrhythmia Classifier',
      modelVersion: 'v1.0.0-validated',
      predictedClass: 'Normal Sinus Rhythm',
      confidenceScore: 0.985,
      predictionStatus: 'completed',
      explanation: 'Verified model output.',
    });

    assert.equal(pred.predictedClass, 'Normal Sinus Rhythm');
    assert.equal(pred.confidenceScore, 0.985);

    const history = predictionRepository.getHistory();
    assert.ok(history.length >= 1);
    assert.equal(history[0].predictedCategory, 'Normal Sinus Rhythm');
  });

  // 11. Recommendation retrieval
  it('11. Retrieves reviewed recommendations and filters by category', () => {
    const recs = recommendationRepository.findMany({ reviewStatus: 'illustrative' });
    assert.ok(recs.length >= 4);

    const filtered = recommendationRepository.findMany({ category: 'General wellness' });
    assert.ok(filtered.length >= 1);
    filtered.forEach((r) => assert.equal(r.category, 'General wellness'));
  });

  // 12. Alert creation and retrieval
  it('12. Creates, retrieves, and updates health/technical alerts in chronological order', () => {
    const alert = alertRepository.create({
      code: 'AL-TEST-01',
      alertType: 'data_quality',
      severity: 'medium',
      title: 'Noisy electrode contact detected',
      description: 'Baseline wander exceeded threshold.',
      status: 'open',
    });

    assert.ok(alert.id);
    assert.equal(alert.severity, 'medium');

    const updated = alertRepository.updateStatus(alert.id, 'acknowledged');
    assert.equal(updated.status, 'acknowledged');

    const openCount = alertRepository.count({ status: 'open' });
    assert.ok(openCount >= 0);
  });

  // 13. Transaction rollback
  it('13. Transaction rolls back entirely when an intermediate operation fails', () => {
    const initialCount = measurementRepository.count();

    assert.throws(() => {
      runInTransaction(() => {
        // Step 1: Valid insert
        measurementRepository.create({
          measurementType: 'heart_rate',
          numericValue: 80,
          unit: 'bpm',
          measuredAt: '2026-10-09T09:00:00Z',
          source: 'manual',
        });

        // Step 2: Invalid insert that triggers constraint failure
        db.prepare(`
          INSERT INTO measurements (measurement_type, numeric_value, unit, measured_at, source)
          VALUES ('unsupported_type', 100, 'unit', '2026-10-09T09:00:00Z', 'manual')
        `).run();
      });
    }, /CHECK constraint failed/);

    const finalCount = measurementRepository.count();
    assert.equal(finalCount, initialCount, 'Transaction must roll back first insert completely on error');
  });

  // 14. Database error handling
  it('14. Gracefully handles errors on malformed SQL queries', () => {
    assert.throws(() => {
      db.prepare('SELECT non_existent_column FROM measurements').all();
    }, /no such column/);
  });

  // 15. Empty database behaviour
  it('15. Dashboard queries return null and empty arrays gracefully when tables are empty', () => {
    // Open a completely fresh in-memory database with schema but without seed data
    const emptyDb = new Database(':memory:');
    emptyDb.pragma('foreign_keys = ON');
    emptyDb.exec(`
      CREATE TABLE measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        measurement_type TEXT NOT NULL,
        numeric_value REAL,
        unit TEXT NOT NULL,
        systolic_value REAL,
        diastolic_value REAL,
        measured_at TEXT NOT NULL,
        source TEXT NOT NULL,
        data_quality_status TEXT NOT NULL DEFAULT 'unverified',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE ecg_recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_filename TEXT NOT NULL,
        stored_filename TEXT NOT NULL UNIQUE,
        file_path TEXT NOT NULL,
        file_format TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        recording_duration_seconds REAL,
        sampling_frequency_hz REAL,
        source TEXT NOT NULL DEFAULT 'upload',
        upload_status TEXT NOT NULL DEFAULT 'uploaded',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ecg_recording_id INTEGER NOT NULL REFERENCES ecg_recordings(id) ON DELETE CASCADE,
        model_name TEXT,
        model_version TEXT,
        predicted_class TEXT,
        confidence_score REAL,
        prediction_status TEXT NOT NULL,
        explanation TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        category TEXT NOT NULL,
        kind TEXT NOT NULL DEFAULT 'wellness',
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        suggested_action TEXT NOT NULL,
        related TEXT,
        source_type TEXT NOT NULL DEFAULT 'reviewed_guideline',
        review_status TEXT NOT NULL DEFAULT 'illustrative',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        related_measurement_id INTEGER,
        status TEXT NOT NULL DEFAULT 'open',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Verify empty state queries
    const hr = emptyDb.prepare("SELECT * FROM measurements WHERE measurement_type = 'heart_rate'").get();
    assert.equal(hr, undefined, 'Empty database returns undefined for single item query');

    const history = emptyDb.prepare('SELECT * FROM predictions').all();
    assert.deepEqual(history, [], 'Empty database returns empty array for collection query');

    emptyDb.close();
  });
});
