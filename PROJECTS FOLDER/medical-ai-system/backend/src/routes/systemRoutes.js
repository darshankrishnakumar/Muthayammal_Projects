import { Router } from 'express';
import systemController from '../controllers/systemController.js';

const router = Router();

// GET /api/system/status - Live verified system status
router.get('/status', systemController.getStatus);

export default router;
