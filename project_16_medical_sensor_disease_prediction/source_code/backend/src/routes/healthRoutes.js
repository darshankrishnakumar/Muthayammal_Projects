import { Router } from 'express';
import healthController from '../controllers/healthController.js';
import validateRequest from '../middleware/validateRequest.js';
import {
  createMeasurementSchema,
  measurementQuerySchema,
  trendsQuerySchema,
  idParamSchema,
} from '../schemas/healthSchemas.js';

const router = Router();

// GET /api/health/summary - Summary statistics
router.get('/summary', healthController.getSummary);

// GET /api/health/trends - Time series data for Recharts
router.get(
  '/trends',
  validateRequest({ query: trendsQuerySchema }),
  healthController.getTrends
);

// GET /api/health/measurements - Measurement history with filters
router.get(
  '/measurements',
  validateRequest({ query: measurementQuerySchema }),
  healthController.getMeasurements
);

// POST /api/health/measurements - Create measurement
router.post(
  '/measurements',
  validateRequest({ body: createMeasurementSchema }),
  healthController.createMeasurement
);

// GET /api/health/measurements/:id - Single measurement
router.get(
  '/measurements/:id',
  validateRequest({ params: idParamSchema }),
  healthController.getMeasurementById
);

// PUT /api/health/measurements/:id - Update measurement
router.put(
  '/measurements/:id',
  validateRequest({ params: idParamSchema }),
  healthController.updateMeasurement
);

// DELETE /api/health/measurements/:id - Delete measurement safely
router.delete(
  '/measurements/:id',
  validateRequest({ params: idParamSchema }),
  healthController.deleteMeasurement
);

export default router;
