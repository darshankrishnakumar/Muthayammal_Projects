import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const backendRoot = path.resolve(__dirname, '../../');

// Load environment variables from backend root .env file
dotenv.config({ path: path.join(backendRoot, '.env') });

const resolvePath = (filePath) => {
  if (path.isAbsolute(filePath)) return filePath;
  return path.resolve(backendRoot, filePath);
};

export const config = {
  PORT: parseInt(process.env.PORT || '5000', 10),
  NODE_ENV: process.env.NODE_ENV || 'development',
  FRONTEND_URL: process.env.FRONTEND_URL
    ? process.env.FRONTEND_URL.split(',').map((url) => url.trim())
    : ['http://localhost:5173', 'http://localhost:8080'],
  DATABASE_PATH: resolvePath(process.env.DATABASE_PATH || './storage/medical.db'),
  ECG_STORAGE_PATH: resolvePath(process.env.ECG_STORAGE_PATH || './storage/ecg'),
  REPORTS_STORAGE_PATH: resolvePath(process.env.REPORTS_STORAGE_PATH || './storage/reports'),
  MAX_UPLOAD_SIZE_MB: parseInt(process.env.MAX_UPLOAD_SIZE_MB || '10', 10),
  MODEL_SERVICE_URL: process.env.MODEL_SERVICE_URL ? process.env.MODEL_SERVICE_URL.trim() : null,
  isProduction: process.env.NODE_ENV === 'production',
  isTest: process.env.NODE_ENV === 'test',
};

export default config;
