import multer from 'multer';
import { ZodError } from 'zod';
import { sendError, AppError } from '../utils/response.js';
import logger from '../utils/logger.js';
import config from '../config/env.js';

export const errorHandler = (err, req, res, next) => {
  // If response headers are already sent, delegate to Express default handler
  if (res.headersSent) {
    return next(err);
  }

  // Safe error logging without exposing sensitive patient details
  logger.error(`Error processing [${req.method}] ${req.originalUrl}: ${err.message}`, {
    name: err.name,
    code: err.code,
    statusCode: err.statusCode,
  });

  // Handle custom AppError
  if (err instanceof AppError) {
    return sendError(res, err.code, err.message, err.statusCode, err.details);
  }

  // Handle Multer upload errors
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return sendError(
        res,
        'FILE_TOO_LARGE',
        `Uploaded file exceeds the maximum allowed limit of ${config.MAX_UPLOAD_SIZE_MB}MB.`,
        413
      );
    }
    return sendError(res, 'UPLOAD_ERROR', `File upload failed: ${err.message}`, 400);
  }

  // Handle Zod validation errors (if thrown outside validateRequest)
  if (err instanceof ZodError) {
    const details = err.errors.map((e) => ({
      field: e.path.join('.'),
      message: e.message,
    }));
    return sendError(res, 'VALIDATION_ERROR', 'The submitted data is invalid.', 400, details);
  }

  // Handle SQLite errors
  if (err.code && err.code.startsWith('SQLITE_')) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      return sendError(res, 'DB_CONSTRAINT_ERROR', 'Database constraint violation.', 400);
    }
    return sendError(res, 'DATABASE_ERROR', 'A database operation error occurred.', 500);
  }

  // JSON parse error
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return sendError(res, 'INVALID_JSON', 'Malformed JSON in request body.', 400);
  }

  // Default internal server error (never leak stack trace or internal filesystem paths)
  const message = config.isProduction
    ? 'An unexpected internal server error occurred.'
    : err.message || 'An unexpected internal server error occurred.';

  return sendError(res, 'INTERNAL_SERVER_ERROR', message, 500);
};

export default errorHandler;
