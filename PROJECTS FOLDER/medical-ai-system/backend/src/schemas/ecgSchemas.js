import { z } from 'zod';

export const ecgIdParamSchema = z.object({
  id: z.coerce.number().int().positive('Recording ID must be a positive integer'),
});

export const ecgQuerySchema = z.object({
  status: z.enum(['uploaded', 'verified', 'rejected']).optional(),
  source: z.string().optional(),
  limit: z.coerce.number().int().positive().max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});
