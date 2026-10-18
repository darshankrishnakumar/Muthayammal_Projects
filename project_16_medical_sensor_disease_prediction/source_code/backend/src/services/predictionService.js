import fs from 'fs';
import predictionRepository from '../repositories/predictionRepository.js';
import ecgService from './ecgService.js';
import modelAdapter from './modelAdapter.js';
import { AppError } from '../utils/response.js';

export const predictionService = {
  /**
   * Process an AI prediction request for an ECG recording.
   * STRICT SAFETY RULE:
   * Will NEVER return synthetic predictions or fake confidence scores.
   * If model is not connected, fails with HTTP 503 and code MODEL_NOT_CONNECTED.
   */
  async createPrediction(recordingId) {
    // 1 & 2. Verify recording exists
    const recording = ecgService.getRecordingById(recordingId);

    // 3. Confirm file is accessible on disk
    if (!recording._internalPath || !fs.existsSync(recording._internalPath)) {
      throw new AppError('The associated ECG recording file is inaccessible on disk.', 404, 'FILE_NOT_FOUND');
    }

    // 4. Confirm a real model adapter is connected
    const isModelReady = await modelAdapter.isModelConnected();
    if (!isModelReady) {
      throw new AppError(
        'The CNN model has not been connected.',
        503,
        'MODEL_NOT_CONNECTED'
      );
    }

    // 5 & 6. Pass recording to model adapter and run inference
    const inferenceResult = await modelAdapter.runInference({
      filePath: recording._internalPath,
      fileFormat: recording.fileFormat,
      recordingId: recording.id,
    });

    // 7. Save genuine result to database
    return predictionRepository.create({
      ecgRecordingId: recording.id,
      modelName: inferenceResult.modelName,
      modelVersion: inferenceResult.modelVersion,
      predictedClass: inferenceResult.predictedClass,
      confidenceScore: inferenceResult.confidenceScore,
      predictionStatus: 'completed',
      explanation: inferenceResult.explanation || null,
    });
  },

  /**
   * List predictions with pagination.
   */
  getPredictions({ status, limit = 20, offset = 0 } = {}) {
    const total = predictionRepository.count({ status });
    const rows = predictionRepository.findMany({ status, limit, offset });

    return {
      total,
      limit,
      offset,
      predictions: rows,
    };
  },

  /**
   * Get single prediction by ID.
   */
  getPredictionById(id) {
    const row = predictionRepository.findById(id);
    if (!row) {
      throw new AppError(`Prediction with ID ${id} not found.`, 404, 'PREDICTION_NOT_FOUND');
    }
    return row;
  },

  /**
   * Retrieve prediction history matching frontend PredictionResult shape.
   */
  getPredictionHistory() {
    const rows = predictionRepository.getHistory(50);

    return rows.map((r) => ({
      ...r,
      id: String(r.id),
      recordingId: String(r.recordingId),
      confidence: r.confidence !== null ? Number(r.confidence) : null,
    }));
  },
};

export default predictionService;
