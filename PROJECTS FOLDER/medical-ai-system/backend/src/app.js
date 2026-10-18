import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import config from './config/env.js';
import healthRoutes from './routes/healthRoutes.js';
import ecgRoutes from './routes/ecgRoutes.js';
import predictionRoutes from './routes/predictionRoutes.js';
import recommendationRoutes from './routes/recommendationRoutes.js';
import alertRoutes from './routes/alertRoutes.js';
import reportRoutes from './routes/reportRoutes.js';
import systemRoutes from './routes/systemRoutes.js';
import notFoundHandler from './middleware/notFoundHandler.js';
import errorHandler from './middleware/errorHandler.js';
import { sendSuccess } from './utils/response.js';

export const createApp = () => {
  const app = express();

  // Security Headers via Helmet
  app.use(
    helmet({
      contentSecurityPolicy: false, // Allows clean REST API usage
      crossOriginResourcePolicy: { policy: 'cross-origin' },
    })
  );

  // CORS Configuration
  const allowedOrigins = Array.isArray(config.FRONTEND_URL)
    ? config.FRONTEND_URL
    : [config.FRONTEND_URL];

  app.use(
    cors({
      origin: (origin, callback) => {
        // Allow requests with no origin (e.g. mobile apps, curl, server-side SSR)
        if (!origin) return callback(null, true);
        if (
          allowedOrigins.includes(origin) ||
          allowedOrigins.includes('*') ||
          origin.startsWith('http://localhost:') ||
          origin.startsWith('http://127.0.0.1:')
        ) {
          return callback(null, true);
        }
        return callback(new Error(`Origin ${origin} not allowed by CORS.`));
      },
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    })
  );

  // Request Body Parsers
  app.use(express.json({ limit: '2mb' }));
  app.use(express.urlencoded({ extended: true, limit: '2mb' }));

  // Root and Health Check Endpoints
  app.get('/', (req, res) => {
    return sendSuccess(res, {
      service: 'Medical AI Health Monitoring Backend',
      version: '1.0.0',
      status: 'online',
    }, 'Medical AI Backend API is active.');
  });

  app.get('/health', (req, res) => {
    return sendSuccess(res, {
      status: 'healthy',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    }, 'Backend is healthy.');
  });

  app.get('/api/health-check', (req, res) => {
    return sendSuccess(res, {
      status: 'healthy',
      uptime: process.uptime(),
    }, 'API health check passed.');
  });

  // Handle URL prefix normalization (e.g., if client calls /api/api/...)
  app.use((req, res, next) => {
    if (req.url.startsWith('/api/api/')) {
      req.url = req.url.replace('/api/api/', '/api/');
    }
    next();
  });

  // Register API Routers
  app.use('/api/health', healthRoutes);
  app.use('/api/ecg', ecgRoutes);
  app.use('/api/predictions', predictionRoutes);
  app.use('/api/recommendations', recommendationRoutes);
  app.use('/api/alerts', alertRoutes);
  app.use('/api/reports', reportRoutes);
  app.use('/api/system', systemRoutes);

  // 404 Handler
  app.use(notFoundHandler);

  // Centralized Error Handler
  app.use(errorHandler);

  return app;
};

export default createApp;
