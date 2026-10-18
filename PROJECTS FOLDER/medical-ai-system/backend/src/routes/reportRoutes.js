import { Router } from 'express';
import reportController from '../controllers/reportController.js';

const router = Router();

// GET /api/reports/summary - Operational report summary
router.get('/summary', reportController.getSummary);

// GET /api/reports/measurements - Detailed measurements report
router.get('/measurements', reportController.getMeasurementsReport);

export default router;
