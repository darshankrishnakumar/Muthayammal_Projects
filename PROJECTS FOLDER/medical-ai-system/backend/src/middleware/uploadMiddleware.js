import multer from 'multer';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import config from '../config/env.js';

// Ensure storage directory exists
if (!fs.existsSync(config.ECG_STORAGE_PATH)) {
  fs.mkdirSync(config.ECG_STORAGE_PATH, { recursive: true });
}

const ALLOWED_EXTENSIONS = new Set(['.csv', '.txt', '.dat', '.json', '.edf']);

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, config.ECG_STORAGE_PATH);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    // Safe generated server filename using cryptographically strong UUID
    const safeName = `${Date.now()}-${crypto.randomUUID()}${ext}`;
    cb(null, safeName);
  },
});

const fileFilter = (req, file, cb) => {
  const ext = path.extname(file.originalname).toLowerCase();

  // Guard against path traversal patterns in client-supplied filename
  if (file.originalname.includes('..') || file.originalname.includes('/') || file.originalname.includes('\\')) {
    req.fileValidationError = {
      code: 'INVALID_FILENAME',
      message: 'Invalid filename detected. Path traversal characters are not permitted.',
      statusCode: 400,
    };
    return cb(null, false);
  }

  if (!ALLOWED_EXTENSIONS.has(ext)) {
    req.fileValidationError = {
      code: 'UNSUPPORTED_MEDIA_TYPE',
      message: `Unsupported file format '${ext}'. Allowed formats: ${Array.from(ALLOWED_EXTENSIONS).join(', ')}.`,
      statusCode: 415,
    };
    return cb(null, false);
  }

  cb(null, true);
};

const maxSizeBytes = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024;

export const uploadEcgFile = multer({
  storage,
  limits: {
    fileSize: maxSizeBytes,
    files: 1,
  },
  fileFilter,
});

export default uploadEcgFile;
