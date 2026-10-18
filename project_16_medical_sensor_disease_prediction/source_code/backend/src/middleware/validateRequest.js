import { ZodError } from 'zod';
import { sendError } from '../utils/response.js';

export const validateRequest = (schemas = {}) => {
  return (req, res, next) => {
    try {
      if (schemas.params) {
        req.params = schemas.params.parse(req.params);
      }
      if (schemas.query) {
        req.query = schemas.query.parse(req.query);
      }
      if (schemas.body) {
        req.body = schemas.body.parse(req.body);
      }
      next();
    } catch (err) {
      if (err instanceof ZodError) {
        const details = err.errors.map((e) => ({
          field: e.path.join('.'),
          message: e.message,
          code: e.code,
        }));
        return sendError(
          res,
          'VALIDATION_ERROR',
          'The submitted data is invalid.',
          400,
          details
        );
      }
      next(err);
    }
  };
};

export default validateRequest;
