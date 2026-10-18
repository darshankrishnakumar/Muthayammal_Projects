import fs from 'fs';
import { getDatabase } from '../config/database.js';
import config from '../config/env.js';
import modelAdapter from '../services/modelAdapter.js';
import { sendSuccess } from '../utils/response.js';

export const systemController = {
  async getStatus(req, res, next) {
    try {
      // 1. Verify Database
      let dbStatus = 'disconnected';
      try {
        const db = getDatabase();
        const row = db.prepare('SELECT 1 as test').get();
        if (row && row.test === 1) {
          dbStatus = 'connected';
        }
      } catch {
        dbStatus = 'error';
      }

      // 2. Verify ECG storage directory
      let ecgStorageStatus = 'unavailable';
      try {
        if (fs.existsSync(config.ECG_STORAGE_PATH)) {
          ecgStorageStatus = 'available';
        }
      } catch {
        ecgStorageStatus = 'error';
      }

      // 3. Verify CNN Model Status (Live probe - honest status)
      const isModelConnected = await modelAdapter.isModelConnected();
      const cnnModelStatus = isModelConnected ? 'connected' : 'not_connected';

      const data = {
        backend: 'online',
        database: dbStatus,
        cnnModel: cnnModelStatus,
        ecgStorage: ecgStorageStatus,
        version: '1.0.0',
        environment: config.NODE_ENV,
        activeSensors: 'not_connected', // IoT sensors currently not attached
        timestamp: new Date().toISOString(),
      };

      return sendSuccess(res, data, 'System status checked successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default systemController;
