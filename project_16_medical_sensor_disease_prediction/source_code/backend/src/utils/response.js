/**
 * Standard Success Response Helper
 * @param {import('express').Response} res
 * @param {*} data
 * @param {string} message
 * @param {number} statusCode
 */
export const sendSuccess = (
  res,
  data = null,
  message = 'Request completed successfully',
  statusCode = 200
) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
  });
};

/**
 * Standard Error Response Helper
 * @param {import('express').Response} res
 * @param {string} code - Short machine-readable error code (e.g., VALIDATION_ERROR, MODEL_NOT_CONNECTED)
 * @param {string} message - Human-readable error message
 * @param {number} statusCode - HTTP status code
 * @param {Array|Object|null} details - Optional structured error details
 */
export const sendError = (
  res,
  code = 'INTERNAL_ERROR',
  message = 'An unexpected error occurred.',
  statusCode = 500,
  details = null
) => {
  const payload = {
    success: false,
    code,
    message,
  };

  if (details !== null && details !== undefined) {
    payload.details = details;
  }

  return res.status(statusCode).json(payload);
};

export class AppError extends Error {
  /**
   * @param {string} message
   * @param {number} statusCode
   * @param {string} code
   * @param {any} details
   */
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR', details = null) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}
