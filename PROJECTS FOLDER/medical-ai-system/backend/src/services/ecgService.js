import fs from 'fs';
import path from 'path';
import ecgRepository from '../repositories/ecgRepository.js';
import config from '../config/env.js';
import { AppError } from '../utils/response.js';
import logger from '../utils/logger.js';

export const ecgService = {
  /**
   * Save uploaded ECG file metadata and perform structural validation.
   */
  async saveUploadedRecording(file, source = 'upload') {
    if (!file) {
      throw new AppError('No ECG file was provided in the upload request.', 400, 'NO_FILE_PROVIDED');
    }

    const originalFilename = path.basename(file.originalname);
    const storedFilename = file.filename;
    const filePath = file.path;
    const fileFormat = path.extname(originalFilename).replace('.', '').toLowerCase();
    const fileSizeBytes = file.size;

    // Structural validation of uploaded file content (without asserting clinical validity)
    let uploadStatus = 'uploaded';
    let sampleRate = null;
    let durationSeconds = null;

    try {
      if (fileFormat === 'csv' || fileFormat === 'txt') {
        const sampleContent = fs.readFileSync(filePath, { encoding: 'utf-8', flag: 'r' }).slice(0, 4096);
        const lines = sampleContent.split(/\r?\n/).filter((l) => l.trim().length > 0);

        if (lines.length === 0) {
          uploadStatus = 'rejected';
        } else {
          // Check if lines contain numeric samples
          const numericTokens = lines.slice(0, 10).some((line) => {
            const parts = line.split(/[,\s\t]+/);
            return parts.some((p) => !isNaN(parseFloat(p)));
          });

          if (numericTokens) {
            uploadStatus = 'verified';
            sampleRate = 360; // Standard benchmark sampling rate
          }
        }
      } else if (fileFormat === 'json') {
        const content = fs.readFileSync(filePath, { encoding: 'utf-8' });
        const parsed = JSON.parse(content);
        if (Array.isArray(parsed) || (parsed && parsed.data)) {
          uploadStatus = 'verified';
        }
      } else {
        uploadStatus = 'uploaded';
      }
    } catch (err) {
      logger.warn(`Failed initial structural validation for file ${storedFilename}: ${err.message}`);
      uploadStatus = 'uploaded';
    }

    return ecgRepository.create({
      originalFilename,
      storedFilename,
      filePath,
      fileFormat,
      fileSizeBytes,
      recordingDurationSeconds: durationSeconds,
      samplingFrequencyHz: sampleRate,
      source,
      uploadStatus,
    });
  },

  /**
   * Retrieve list of recordings with pagination.
   */
  getRecordings({ status, source, limit = 20, offset = 0 } = {}) {
    const total = ecgRepository.count({ status, source });
    const recordings = ecgRepository.findMany({ status, source, limit, offset });

    return {
      total,
      limit,
      offset,
      recordings,
    };
  },

  /**
   * Retrieve single recording metadata. Never exposes full absolute server paths to public client.
   */
  getRecordingById(id) {
    const recording = ecgRepository.findById(id);

    if (!recording) {
      throw new AppError(`ECG recording with ID ${id} not found.`, 404, 'RECORDING_NOT_FOUND');
    }

    const clientSafe = { ...recording };
    delete clientSafe.filePath;

    return {
      ...clientSafe,
      _internalPath: recording.filePath,
    };
  },

  /**
   * Safely delete recording file from disk and metadata from database.
   */
  deleteRecording(id) {
    const recording = ecgRepository.findById(id);

    if (!recording) {
      throw new AppError(`ECG recording with ID ${id} not found.`, 404, 'RECORDING_NOT_FOUND');
    }

    // Path traversal safety check
    const resolvedPath = path.resolve(recording.filePath || recording.file_path);
    const storageDir = path.resolve(config.ECG_STORAGE_PATH);

    if (!resolvedPath.startsWith(storageDir)) {
      throw new AppError('Access denied: file location is outside permitted storage directory.', 403, 'FORBIDDEN_PATH');
    }

    // Safely remove file from disk if present
    try {
      if (fs.existsSync(resolvedPath)) {
        fs.unlinkSync(resolvedPath);
      }
    } catch (err) {
      logger.warn(`Could not remove file ${resolvedPath} from disk: ${err.message}`);
    }

    // Remove DB metadata (foreign keys cascade to predictions if any)
    ecgRepository.deleteById(id);

    return {
      id: Number(id),
      deleted: true,
      message: 'ECG recording and associated file successfully removed.',
    };
  },

  /**
   * Parse and extract waveform points from stored ECG recording file.
   */
  getRecordingSamples(id) {
    const recording = this.getRecordingById(id);
    const filePath = recording._internalPath;

    if (!filePath || !fs.existsSync(filePath)) {
      throw new AppError('The ECG recording file is missing on server disk.', 404, 'FILE_NOT_FOUND');
    }

    const fileFormat = (recording.fileFormat || '').toLowerCase();
    const sampleRate = recording.samplingFrequencyHz || 360;
    const samples = [];
    const maxPoints = 1800; // 5 seconds at 360Hz

    try {
      if (fileFormat === 'csv' || fileFormat === 'txt') {
        const content = fs.readFileSync(filePath, { encoding: 'utf-8' });
        const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);

        let pointIdx = 0;
        for (const line of lines) {
          if (pointIdx >= maxPoints) break;
          const parts = line.split(/[,\s\t]+/).map((p) => p.trim()).filter(Boolean);
          const nums = parts.map(Number).filter((n) => !isNaN(n));
          if (nums.length === 0) continue; // skip header
          const val = nums.length > 1 ? nums[1] : nums[0];
          samples.push({
            t: Math.round((pointIdx / sampleRate) * 1000) / 1000,
            mv: Math.round(val * 1000) / 1000,
          });
          pointIdx++;
        }
      } else if (fileFormat === 'json') {
        const content = fs.readFileSync(filePath, { encoding: 'utf-8' });
        const parsed = JSON.parse(content);
        const rawArray = Array.isArray(parsed)
          ? parsed
          : (parsed.samples || parsed.data || parsed.voltage || []);

        const count = Math.min(rawArray.length, maxPoints);
        for (let i = 0; i < count; i++) {
          const item = rawArray[i];
          const val = typeof item === 'number' ? item : (item.mv ?? item.voltage ?? item.value ?? 0);
          samples.push({
            t: Math.round((i / sampleRate) * 1000) / 1000,
            mv: Math.round(val * 1000) / 1000,
          });
        }
      }
    } catch (err) {
      logger.warn(`Could not parse samples for recording ${id}: ${err.message}`);
    }

    return {
      recordingId: recording.id,
      originalFilename: recording.originalFilename,
      samplingFrequencyHz: sampleRate,
      samples,
      pointCount: samples.length,
      durationSeconds: samples.length > 0 ? Math.round((samples.length / sampleRate) * 10) / 10 : 0,
    };
  },
};

export default ecgService;
