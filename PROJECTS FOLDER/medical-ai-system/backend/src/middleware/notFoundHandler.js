import { sendError } from '../utils/response.js';

export const notFoundHandler = (req, res) => {
  return sendError(
    res,
    'RESOURCE_NOT_FOUND',
    `Cannot ${req.method} ${req.originalUrl}`,
    404
  );
};

export default notFoundHandler;
