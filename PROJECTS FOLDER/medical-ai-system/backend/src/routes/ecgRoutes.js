import { Router } from 'express';
import ecgController from '../controllers/ecgController.js';
import uploadEcgFile from '../middleware/uploadMiddleware.js';
import validateRequest from '../middleware/validateRequest.js';
import { ecgIdParamSchema, ecgQuerySchema } from '../schemas/ecgSchemas.js';

const router = Router();

// POST /api/ecg/upload - Multer upload
router.post(
  '/upload',
  uploadEcgFile.single('file'),
  ecgController.upload
);

// GET /api/ecg/recordings - List recordings
router.get(
  '/recordings',
  validateRequest({ query: ecgQuerySchema }),
  ecgController.getRecordings
);

// GET /api/ecg/recordings/:id - Recording details
router.get(
  '/recordings/:id',
  validateRequest({ params: ecgIdParamSchema }),
  ecgController.getRecordingById
);

// DELETE /api/ecg/recordings/:id - Delete recording and file safely
router.delete(
  '/recordings/:id',
  validateRequest({ params: ecgIdParamSchema }),
  ecgController.deleteRecording
);

// GET /api/ecg/recordings/:id/samples - Waveform sample points
router.get(
  '/recordings/:id/samples',
  validateRequest({ params: ecgIdParamSchema }),
  ecgController.getRecordingSamples
);

export default router;
