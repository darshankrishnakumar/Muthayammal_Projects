import { z } from 'zod';

export const createPredictionSchema = z.object({
  ecgRecordingId: z.coerce.number().int().positive().optional(),
  recordingId: z.union([z.coerce.number().int().positive(), z.string().min(1)]).optional(),
}).refine((data) => data.ecgRecordingId !== undefined || data.recordingId !== undefined, {
  message: 'Either ecgRecordingId or recordingId must be provided.',
  path: ['ecgRecordingId'],
});

export const predictionIdParamSchema = z.object({
  id: z.coerce.number().int().positive('Prediction ID must be a positive integer'),
});

export const predictionQuerySchema = z.object({
  status: z.enum(['pending', 'processing', 'completed', 'failed', 'model_not_connected']).optional(),
  limit: z.coerce.number().int().positive().max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});
