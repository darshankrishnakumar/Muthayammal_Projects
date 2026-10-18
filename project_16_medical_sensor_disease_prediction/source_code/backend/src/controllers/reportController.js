import reportService from '../services/reportService.js';
import { sendSuccess } from '../utils/response.js';

export const reportController = {
  async getSummary(req, res, next) {
    try {
      const report = reportService.getSummaryReport(req.query);
      return sendSuccess(res, report, 'Report summary generated successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getMeasurementsReport(req, res, next) {
    try {
      const report = reportService.getMeasurementReport(req.query);
      return sendSuccess(res, report, 'Measurements report generated successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default reportController;
