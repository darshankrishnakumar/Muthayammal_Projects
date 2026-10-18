import fs from 'fs';
import config from './config/env.js';
import { initDatabase, closeDatabase } from './config/database.js';
import createApp from './app.js';
import logger from './utils/logger.js';

// Ensure storage directories exist
[config.ECG_STORAGE_PATH, config.REPORTS_STORAGE_PATH].forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Initialize database
initDatabase();

// Create application
const app = createApp();

// Start HTTP Server
const server = app.listen(config.PORT, () => {
  logger.info(`=======================================================`);
  logger.info(`Medical AI Backend running on port ${config.PORT}`);
  logger.info(`Environment: ${config.NODE_ENV}`);
  logger.info(`Database: ${config.DATABASE_PATH}`);
  logger.info(`ECG Storage: ${config.ECG_STORAGE_PATH}`);
  logger.info(`Allowed Origins: ${config.FRONTEND_URL.join(', ')}`);
  logger.info(`CNN Model Status: ${config.MODEL_SERVICE_URL ? 'Configured (' + config.MODEL_SERVICE_URL + ')' : 'Not Connected (Explicit 503 Enforced)'}`);
  logger.info(`=======================================================`);
});

// Graceful shutdown handling
const shutdown = (signal) => {
  logger.info(`Received ${signal}. Shutting down gracefully...`);
  server.close(() => {
    logger.info('HTTP server closed.');
    closeDatabase();
    logger.info('Database connection closed.');
    process.exit(0);
  });

  // Force shutdown after timeout if pending connections hang
  setTimeout(() => {
    logger.error('Could not close connections in time, forcefully shutting down.');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

export default server;
