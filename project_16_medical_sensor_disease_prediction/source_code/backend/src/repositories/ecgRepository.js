import { getDatabase } from '../config/database.js';

export const ecgRepository = {
  /**
   * Save ECG metadata into SQLite.
   */
  create({
    originalFilename,
    storedFilename,
    filePath,
    fileFormat,
    fileSizeBytes,
    recordingDurationSeconds = null,
    samplingFrequencyHz = null,
    source = 'upload',
    uploadStatus = 'uploaded',
  }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO ecg_recordings (
        original_filename, stored_filename, file_path, file_format, file_size_bytes,
        recording_duration_seconds, sampling_frequency_hz, source, upload_status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      originalFilename,
      storedFilename,
      filePath,
      fileFormat,
      fileSizeBytes,
      recordingDurationSeconds,
      samplingFrequencyHz,
      source,
      uploadStatus
    );

    return this.findById(info.lastInsertRowid);
  },

  /**
   * Find recording by ID.
   */
  findById(id) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        original_filename as originalFilename,
        stored_filename as storedFilename,
        file_path as filePath,
        file_format as fileFormat,
        file_size_bytes as fileSizeBytes,
        recording_duration_seconds as recordingDurationSeconds,
        sampling_frequency_hz as samplingFrequencyHz,
        source,
        upload_status as uploadStatus,
        created_at as createdAt
      FROM ecg_recordings
      WHERE id = ?
    `).get(id);
  },

  /**
   * Find recording by unique stored filename.
   */
  findByStoredFilename(storedFilename) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        original_filename as originalFilename,
        stored_filename as storedFilename,
        file_path as filePath,
        file_format as fileFormat,
        file_size_bytes as fileSizeBytes,
        recording_duration_seconds as recordingDurationSeconds,
        sampling_frequency_hz as samplingFrequencyHz,
        source,
        upload_status as uploadStatus,
        created_at as createdAt
      FROM ecg_recordings
      WHERE stored_filename = ?
    `).get(storedFilename);
  },

  /**
   * Find multiple recordings with filtering and pagination.
   */
  findMany({ status, source, limit = 20, offset = 0 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('upload_status = ?');
      params.push(status);
    }
    if (source) {
      conditions.push('source = ?');
      params.push(source);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        id,
        original_filename as originalFilename,
        stored_filename as storedFilename,
        file_format as fileFormat,
        file_size_bytes as fileSizeBytes,
        recording_duration_seconds as recordingDurationSeconds,
        sampling_frequency_hz as samplingFrequencyHz,
        source,
        upload_status as uploadStatus,
        created_at as createdAt
      FROM ecg_recordings
      ${whereClause}
      ORDER BY id DESC
      LIMIT ? OFFSET ?
    `).all(...params, limit, offset);
  },

  /**
   * Count total recordings matching criteria.
   */
  count({ status, source } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('upload_status = ?');
      params.push(status);
    }
    if (source) {
      conditions.push('source = ?');
      params.push(source);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const row = db.prepare(`SELECT COUNT(*) as total FROM ecg_recordings ${whereClause}`).get(...params);
    return row.total;
  },

  /**
   * Safely delete record by ID.
   */
  deleteById(id) {
    const db = getDatabase();
    return db.prepare('DELETE FROM ecg_recordings WHERE id = ?').run(id);
  },
};

export default ecgRepository;
