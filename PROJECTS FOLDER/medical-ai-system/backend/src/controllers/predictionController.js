import predictionService from '../services/predictionService.js';
import { sendSuccess } from '../utils/response.js';

export const predictionController = {
  async requestPrediction(req, res, next) {
    try {
      const recordingId = req.body.ecgRecordingId ?? req.body.recordingId;
      const prediction = await predictionService.createPrediction(recordingId);
      return sendSuccess(res, prediction, 'Prediction generated successfully.', 200);
    } catch (err) {
      next(err);
    }
  },

  async getPredictions(req, res, next) {
    try {
      const result = predictionService.getPredictions(req.query);
      return sendSuccess(res, result, 'Predictions retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getPredictionById(req, res, next) {
    try {
      const prediction = predictionService.getPredictionById(req.params.id);
      return sendSuccess(res, prediction, 'Prediction retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getPredictionHistory(req, res, next) {
    try {
      const history = predictionService.getPredictionHistory();
      return sendSuccess(res, history, 'Prediction history retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default predictionController;
