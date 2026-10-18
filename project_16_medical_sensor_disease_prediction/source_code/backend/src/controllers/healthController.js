import healthService from '../services/healthService.js';
import { sendSuccess } from '../utils/response.js';

export const healthController = {
  async getMeasurements(req, res, next) {
    try {
      const result = healthService.getMeasurements(req.query);
      return sendSuccess(res, result, 'Measurements retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getMeasurementById(req, res, next) {
    try {
      const record = healthService.getMeasurementById(req.params.id);
      return sendSuccess(res, record, 'Measurement retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async createMeasurement(req, res, next) {
    try {
      const created = healthService.createMeasurement(req.body);
      return sendSuccess(res, created, 'Measurement record created successfully.', 201);
    } catch (err) {
      next(err);
    }
  },

  async getSummary(req, res, next) {
    try {
      const summary = healthService.getSummary();
      return sendSuccess(res, summary, 'Health summary statistics retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getTrends(req, res, next) {
    try {
      const trends = healthService.getTrends(req.query);
      return sendSuccess(res, trends, 'Trend time-series data retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async updateMeasurement(req, res, next) {
    try {
      const updated = healthService.updateMeasurement(req.params.id, req.body);
      return sendSuccess(res, updated, 'Measurement record updated successfully.');
    } catch (err) {
      next(err);
    }
  },

  async deleteMeasurement(req, res, next) {
    try {
      const result = healthService.deleteMeasurement(req.params.id);
      return sendSuccess(res, result, 'Measurement record deleted successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default healthController;
