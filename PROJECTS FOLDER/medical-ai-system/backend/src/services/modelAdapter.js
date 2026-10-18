import config from '../config/env.js';
import logger from '../utils/logger.js';

/**
 * CNN Model Adapter Interface
 *
 * This adapter manages communication with a validated 1D CNN inference engine.
 * Future integration options:
 * 1. TensorFlow.js Model: Load converted Keras model (`model.json` + binary weights)
 *    using `@tensorflow/tfjs-node` or `@tensorflow/tfjs`.
 *    Note: requires model conversion via `tensorflowjs_converter --input_format=keras`.
 *    ECG preprocessing (filtering, baseline wander removal, normalization to [0,1] or z-score,
 *    and segmentation to fixed length e.g., 187 or 3600 samples) must be matched exactly.
 * 2. Dedicated Model Microservice: Secured REST/gRPC endpoint running an optimized inference server
 *    configured via `MODEL_SERVICE_URL`.
 *
 * SAFETY INVARIANT:
 * This system will NEVER fabricate synthetic classifications or fake confidence scores.
 * Unless a real validated model is verified and reachable, it strictly reports not connected.
 */

class CnnModelAdapter {
  constructor() {
    this.serviceUrl = config.MODEL_SERVICE_URL;
    this.modelName = '1D CNN Arrhythmia Classifier';
    this.modelVersion = null;
  }

  /**
   * Check if a verified CNN model engine is active and reachable.
   * @returns {Promise<boolean>}
   */
  async isModelConnected() {
    if (!this.serviceUrl) {
      return false;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(`${this.serviceUrl}/health`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!res.ok) return false;
      const json = await res.json().catch(() => null);
      return Boolean(json && (json.status === 'healthy' || json.ready === true));
    } catch (err) {
      logger.warn(`Model service ping failed at ${this.serviceUrl}: ${err.message}`);
      return false;
    }
  }

  /**
   * Execute CNN inference on an ECG file.
   * @param {Object} options
   * @param {string} options.filePath
   * @param {string} options.fileFormat
   * @param {number} options.recordingId
   * @returns {Promise<Object>}
   */
  async runInference({ filePath, fileFormat, recordingId }) {
    const isConnected = await this.isModelConnected();
    if (!isConnected) {
      const error = new Error('The CNN model has not been connected.');
      error.code = 'MODEL_NOT_CONNECTED';
      error.statusCode = 503;
      throw error;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.serviceUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filePath,
          fileFormat,
          recordingId,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorJson = await response.json().catch(() => null);
        const error = new Error(errorJson?.message || `Model inference failed with status ${response.status}`);
        error.code = errorJson?.code || 'INFERENCE_ERROR';
        error.statusCode = response.status >= 500 ? 502 : response.status;
        throw error;
      }

      const result = await response.json();
      return {
        modelName: result.modelName || this.modelName,
        modelVersion: result.modelVersion || '1.0.0',
        predictedClass: result.predictedClass,
        predictedCode: result.predictedCode,
        confidenceScore: typeof result.confidenceScore === 'number' ? result.confidenceScore : null,
        classProbabilities: result.classProbabilities || null,
        explanation: result.explanation || null,
      };
    } catch (err) {
      if (err.name === 'AbortError') {
        const timeoutError = new Error('Inference request timed out.');
        timeoutError.code = 'INFERENCE_TIMEOUT';
        timeoutError.statusCode = 504;
        throw timeoutError;
      }
      throw err;
    }
  }

  /**
   * Returns current adapter status metadata.
   */
  getStatus() {
    return {
      name: this.modelName,
      version: this.modelVersion,
      serviceUrl: this.serviceUrl ? '[CONFIGURED]' : null,
      status: this.serviceUrl ? 'validating' : 'not_connected',
      adapterType: 'TensorFlow/HTTP_Service',
    };
  }
}

export const modelAdapter = new CnnModelAdapter();
export default modelAdapter;
