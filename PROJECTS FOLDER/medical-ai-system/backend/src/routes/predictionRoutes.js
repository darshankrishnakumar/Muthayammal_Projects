import { Router } from 'express';
import predictionController from '../controllers/predictionController.js';
import validateRequest from '../middleware/validateRequest.js';
import {
  createPredictionSchema,
  predictionIdParamSchema,
  predictionQuerySchema,
} from '../schemas/predictionSchemas.js';

const router = Router();

// GET /api/predictions/history - History (mapped for frontend PredictionResult interface)
router.get('/history', predictionController.getPredictionHistory);

// POST /api/predictions - Run or request prediction
router.post(
  '/',
  validateRequest({ body: createPredictionSchema }),
  predictionController.requestPrediction
);

// GET /api/predictions - List predictions
router.get(
  '/',
  validateRequest({ query: predictionQuerySchema }),
  predictionController.getPredictions
);

// GET /api/predictions/:id - Single prediction
router.get(
  '/:id',
  validateRequest({ params: predictionIdParamSchema }),
  predictionController.getPredictionById
);

export default router;
