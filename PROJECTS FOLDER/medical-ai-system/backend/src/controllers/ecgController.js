import ecgService from '../services/ecgService.js';
import { sendSuccess, sendError } from '../utils/response.js';

export const ecgController = {
  async upload(req, res, next) {
    try {
      if (req.fileValidationError) {
        return sendError(
          res,
          req.fileValidationError.code,
          req.fileValidationError.message,
          req.fileValidationError.statusCode
        );
      }

      if (!req.file) {
        return sendError(
          res,
          'NO_FILE_PROVIDED',
          'No ECG file was provided in the upload request.',
          400
        );
      }

      const source = req.body?.source || 'upload';
      const record = await ecgService.saveUploadedRecording(req.file, source);

      return sendSuccess(
        res,
        {
          recordingId: String(record.id),
          id: record.id,
          originalFilename: record.originalFilename,
          storedFilename: record.storedFilename,
          fileFormat: record.fileFormat,
          fileSizeBytes: record.fileSizeBytes,
          samplingFrequencyHz: record.samplingFrequencyHz,
          uploadStatus: record.uploadStatus,
          createdAt: record.createdAt,
        },
        'ECG recording uploaded and registered successfully.',
        201
      );
    } catch (err) {
      next(err);
    }
  },

  async getRecordings(req, res, next) {
    try {
      const result = ecgService.getRecordings(req.query);
      return sendSuccess(res, result, 'ECG recordings retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getRecordingById(req, res, next) {
    try {
      const record = ecgService.getRecordingById(req.params.id);
      return sendSuccess(res, record, 'ECG recording retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async deleteRecording(req, res, next) {
    try {
      const result = ecgService.deleteRecording(req.params.id);
      return sendSuccess(res, result, 'ECG recording deleted successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getRecordingSamples(req, res, next) {
    try {
      const result = ecgService.getRecordingSamples(req.params.id);
      return sendSuccess(res, result, 'ECG recording samples parsed successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default ecgController;
