import config from '../config/env.js';

const levels = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

const currentLevel = config.isProduction ? levels.INFO : levels.DEBUG;

const formatMessage = (level, message, meta = null) => {
  const timestamp = new Date().toISOString();
  let log = `[${timestamp}] [${level}] ${message}`;
  if (meta) {
    // Sanitize any potential sensitive medical/file data
    const sanitizedMeta = typeof meta === 'object' ? { ...meta } : { value: meta };
    delete sanitizedMeta.rawEcg;
    delete sanitizedMeta.signal;
    delete sanitizedMeta.patientData;
    delete sanitizedMeta.buffer;
    log += ` ${JSON.stringify(sanitizedMeta)}`;
  }
  return log;
};

export const logger = {
  debug: (message, meta) => {
    if (currentLevel <= levels.DEBUG && !config.isTest) {
      console.debug(formatMessage('DEBUG', message, meta));
    }
  },
  info: (message, meta) => {
    if (currentLevel <= levels.INFO && !config.isTest) {
      console.log(formatMessage('INFO', message, meta));
    }
  },
  warn: (message, meta) => {
    if (currentLevel <= levels.WARN) {
      console.warn(formatMessage('WARN', message, meta));
    }
  },
  error: (message, meta) => {
    if (currentLevel <= levels.ERROR) {
      console.error(formatMessage('ERROR', message, meta));
    }
  },
};

export default logger;
