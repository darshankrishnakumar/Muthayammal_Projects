import { Router } from 'express';
import alertController from '../controllers/alertController.js';

const router = Router();

// GET /api/alerts - List alerts
router.get('/', alertController.getAlerts);

// GET /api/alerts/:id - Single alert
router.get('/:id', alertController.getAlertById);

// PATCH /api/alerts/:id/status - Update alert status
router.patch('/:id/status', alertController.updateStatus);

export default router;
