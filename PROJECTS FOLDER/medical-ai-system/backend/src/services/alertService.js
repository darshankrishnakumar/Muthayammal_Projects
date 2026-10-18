import alertRepository from '../repositories/alertRepository.js';
import { AppError } from '../utils/response.js';

export const alertService = {
  /**
   * Retrieve alerts with optional filters.
   */
  getAlerts({ status, severity, alertType } = {}) {
    const rows = alertRepository.findMany({ status, severity, alertType });

    return rows.map((r) => ({
      id: r.code || `AL-${String(r.id).padStart(2, '0')}`,
      numericId: r.id,
      category: r.alertType === 'informational' ? 'Informational' :
                r.alertType === 'sensor_connection' ? 'Sensor connection issue' :
                r.alertType === 'measurement_review' ? 'Measurement review required' :
                r.alertType === 'model_availability' ? 'Model integration status' : 'Data-quality alert',
      description: r.title,
      detail: r.description,
      priority: r.severity,
      status: r.status,
      timestamp: r.createdAt,
      relatedMeasurementId: r.relatedMeasurementId,
    }));
  },

  /**
   * Retrieve single alert by ID or Code.
   */
  getAlertById(id) {
    const row = alertRepository.findByCodeOrId(id);
    if (!row) {
      throw new AppError(`Alert '${id}' not found.`, 404, 'ALERT_NOT_FOUND');
    }

    return {
      id: row.code || `AL-${String(row.id).padStart(2, '0')}`,
      numericId: row.id,
      alertType: row.alertType,
      severity: row.severity,
      title: row.title,
      description: row.description,
      status: row.status,
      createdAt: row.createdAt,
      relatedMeasurementId: row.relatedMeasurementId,
    };
  },

  /**
   * Update status of an alert.
   */
  updateAlertStatus(id, newStatus) {
    const validStatuses = ['open', 'active', 'acknowledged', 'dismissed', 'resolved'];
    if (!validStatuses.includes(newStatus)) {
      throw new AppError(
        `Invalid status '${newStatus}'. Allowed: ${validStatuses.join(', ')}`,
        400,
        'INVALID_STATUS'
      );
    }

    const existing = alertRepository.findByCodeOrId(id);
    if (!existing) {
      throw new AppError(`Alert '${id}' not found.`, 404, 'ALERT_NOT_FOUND');
    }

    alertRepository.updateStatus(existing.id, newStatus);
    return this.getAlertById(existing.id);
  },
};

export default alertService;
