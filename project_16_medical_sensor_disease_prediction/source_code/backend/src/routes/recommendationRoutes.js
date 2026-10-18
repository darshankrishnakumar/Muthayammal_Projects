import { Router } from 'express';
import recommendationController from '../controllers/recommendationController.js';

const router = Router();

// GET /api/recommendations - List reviewed recommendations
router.get('/', recommendationController.getRecommendations);

// GET /api/recommendations/:id - Single recommendation
router.get('/:id', recommendationController.getRecommendationById);

export default router;
