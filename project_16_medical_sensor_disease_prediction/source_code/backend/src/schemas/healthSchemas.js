import { z } from 'zod';

const measurementTypeEnum = z.enum(['heart_rate', 'blood_pressure', 'spo2', 'body_temperature']);
const sourceEnum = z.enum(['manual', 'sensor', 'demo']);

// Plausibility checkers
export const validatePlausibility = (type, data) => {
  if (type === 'heart_rate') {
    if (typeof data.value !== 'number' || isNaN(data.value)) {
      return { valid: false, message: 'Heart rate value must be a number.' };
    }
    if (data.value <= 0) {
      return { valid: false, message: 'Heart rate must be a positive number.' };
    }
    if (data.value < 30 || data.value > 250) {
      return { valid: false, message: 'Heart rate is outside plausible physiological range (30 - 250 bpm).' };
    }
    if (data.unit !== 'bpm') {
      return { valid: false, message: 'Heart rate unit must explicitly be bpm.' };
    }
  }

  if (type === 'blood_pressure') {
    const sys = data.systolic ?? data.systolicValue;
    const dia = data.diastolic ?? data.diastolicValue;
    if (typeof sys !== 'number' || typeof dia !== 'number') {
      return { valid: false, message: 'Blood pressure requires both systolic and diastolic numeric values.' };
    }
    if (sys < 50 || sys > 260) {
      return { valid: false, message: 'Systolic value is outside plausible physiological range (50 - 260 mmHg).' };
    }
    if (dia < 30 || dia > 160) {
      return { valid: false, message: 'Diastolic value is outside plausible physiological range (30 - 160 mmHg).' };
    }
    if (sys <= dia) {
      return { valid: false, message: 'Systolic pressure must be greater than diastolic pressure.' };
    }
    if (data.unit !== 'mmHg') {
      return { valid: false, message: 'Blood pressure unit must explicitly be mmHg.' };
    }
  }

  if (type === 'spo2') {
    if (typeof data.value !== 'number' || isNaN(data.value)) {
      return { valid: false, message: 'SpO2 value must be a number.' };
    }
    if (data.value < 0 || data.value > 100) {
      return { valid: false, message: 'SpO2 must be within the physical percentage range of 0 to 100%.' };
    }
    if (data.unit !== '%') {
      return { valid: false, message: 'SpO2 unit must explicitly be %.' };
    }
  }

  if (type === 'body_temperature') {
    if (typeof data.value !== 'number' || isNaN(data.value)) {
      return { valid: false, message: 'Temperature value must be a number.' };
    }
    const unit = data.unit;
    if (unit !== '°C' && unit !== 'C' && unit !== '°F') {
      return { valid: false, message: "Temperature unit must be explicitly '°C', 'C', or '°F'." };
    }
    if ((unit === '°C' || unit === 'C') && (data.value < 30 || data.value > 45)) {
      return { valid: false, message: 'Temperature in Celsius must be within plausible range (30.0 - 45.0 °C).' };
    }
    if (unit === '°F' && (data.value < 86 || data.value > 113)) {
      return { valid: false, message: 'Temperature in Fahrenheit must be within plausible range (86.0 - 113.0 °F).' };
    }
  }

  return { valid: true };
};

// Schema for individual measurement creation
const singleMeasurementSchema = z.object({
  measurementType: measurementTypeEnum,
  value: z.number().optional(),
  unit: z.string().min(1, 'Unit is required'),
  systolic: z.number().optional(),
  diastolic: z.number().optional(),
  source: sourceEnum.default('manual'),
  measuredAt: z.string().datetime({ offset: true }).optional().or(z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)).optional(),
  timestamp: z.string().optional(),
}).superRefine((data, ctx) => {
  const result = validatePlausibility(data.measurementType, data);
  if (!result.valid) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: result.message,
      path: data.measurementType === 'blood_pressure' ? ['systolic'] : ['value'],
    });
  }
});

// Schema for compound measurement bundle (no measurementType field)
const compoundMeasurementSchema = z.object({
  measurementType: z.undefined(),
  timestamp: z.string().datetime({ offset: true }).optional().or(z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)).optional(),
  measuredAt: z.string().optional(),
  heartRate: z.number().min(30, 'Heart rate must be at least 30 bpm').max(250, 'Heart rate must be at most 250 bpm').optional(),
  systolic: z.number().min(50, 'Systolic must be at least 50 mmHg').max(260, 'Systolic must be at most 260 mmHg').optional(),
  diastolic: z.number().min(30, 'Diastolic must be at least 30 mmHg').max(160, 'Diastolic must be at most 160 mmHg').optional(),
  spo2: z.number().min(0, 'SpO2 cannot be below 0%').max(100, 'SpO2 cannot exceed 100%').optional(),
  temperature: z.number().min(30, 'Temperature must be at least 30°C').max(45, 'Temperature must be at most 45°C').optional(),
  source: sourceEnum.default('manual'),
}).superRefine((data, ctx) => {
  if (data.systolic !== undefined && data.diastolic !== undefined) {
    if (data.systolic <= data.diastolic) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Systolic pressure must be greater than diastolic pressure.',
        path: ['systolic'],
      });
    }
  }
});

export const createMeasurementSchema = z.union([singleMeasurementSchema, compoundMeasurementSchema]);

export const measurementQuerySchema = z.object({
  measurementType: measurementTypeEnum.optional(),
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}/, 'Invalid startDate format (YYYY-MM-DD or ISO-8601)').optional(),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}/, 'Invalid endDate format (YYYY-MM-DD or ISO-8601)').optional(),
  limit: z.coerce.number().int().positive().max(200, 'Limit cannot exceed 200').default(50),
  offset: z.coerce.number().int().min(0, 'Offset cannot be negative').default(0),
});

export const trendsQuerySchema = z.object({
  metric: z.enum(['heartRate', 'bloodPressure', 'spo2', 'temperature']).optional().default('heartRate'),
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}/).optional(),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}/).optional(),
  limit: z.coerce.number().int().positive().max(500).default(100),
});

export const idParamSchema = z.object({
  id: z.coerce.number().int().positive('ID must be a positive integer'),
});
