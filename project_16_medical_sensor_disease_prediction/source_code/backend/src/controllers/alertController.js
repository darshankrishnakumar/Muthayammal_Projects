import alertService from '../services/alertService.js';
import { sendSuccess } from '../utils/response.js';

export const alertController = {
  async getAlerts(req, res, next) {
    try {
      const alerts = alertService.getAlerts(req.query);
      return sendSuccess(res, alerts, 'Alerts retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getAlertById(req, res, next) {
    try {
      const alert = alertService.getAlertById(req.params.id);
      return sendSuccess(res, alert, 'Alert retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async updateStatus(req, res, next) {
    try {
      const updated = alertService.updateAlertStatus(req.params.id, req.body.status);
      return sendSuccess(res, updated, 'Alert status updated successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default alertController;
