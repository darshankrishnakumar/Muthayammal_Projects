import type { HealthAlert, Measurement, Recommendation } from "@/types/health";
import type { SensorStatus } from "@/types/sensor";

// Fixed illustrative series (no randomness) — DEMO DATA, not patient measurements.
const base = Date.UTC(2026, 9, 9, 8, 0);
const hr = [72, 74, 71, 76, 78, 75, 73, 70, 72, 77, 79, 74, 73, 71, 75, 76, 74, 72, 73, 75, 77, 74, 72, 73, 74, 76, 75, 73, 72, 74];
const sys = [118, 120, 117, 121, 123, 119, 118, 116, 119, 122, 124, 120, 118, 117, 121, 122, 120, 118, 119, 121, 123, 120, 118, 119, 120, 122, 121, 119, 118, 120];
const dia = [78, 79, 77, 80, 81, 79, 78, 76, 78, 80, 82, 79, 78, 77, 79, 80, 79, 78, 78, 79, 81, 79, 77, 78, 79, 80, 79, 78, 77, 79];
const sp = [98, 98, 97, 98, 99, 98, 97, 98, 98, 97, 98, 99, 98, 98, 97, 98, 98, 99, 98, 97, 98, 98, 97, 98, 99, 98, 98, 97, 98, 98];
const tp = [36.6, 36.7, 36.6, 36.8, 36.9, 36.7, 36.6, 36.5, 36.6, 36.8, 36.9, 36.7, 36.6, 36.6, 36.7, 36.8, 36.7, 36.6, 36.6, 36.7, 36.8, 36.7, 36.6, 36.6, 36.7, 36.8, 36.7, 36.6, 36.6, 36.7];

export const demoMeasurements: Measurement[] = hr.map((h, i) => ({
  timestamp: new Date(base - (hr.length - 1 - i) * 24 * 3600 * 1000).toISOString(),
  heartRate: h,
  systolic: sys[i]!,
  diastolic: dia[i]!,
  spo2: sp[i]!,
  temperature: tp[i]!,
  source: "demo",
}));

export const demoAlerts: HealthAlert[] = [
  { id: "AL-01", category: "Informational", description: "Interface running in demonstration mode.", detail: "All values on screen are illustrative sample data. No sensor or backend is connected.", timestamp: null, priority: "info" },
  { id: "AL-02", category: "Sensor connection issue", description: "No sensor device is connected.", detail: "IoT sensor integration (e.g. MAX30102, temperature probe) is planned for a future phase.", timestamp: null, priority: "warning" },
  { id: "AL-03", category: "Measurement review required", description: "Example: manual entry awaiting review.", detail: "Illustrative alert showing how measurement-review notices will appear once data validation rules are connected.", timestamp: "2026-10-08T14:20:00Z", priority: "review" },
];

export const demoRecommendations: Recommendation[] = [
  { id: "RC-01", category: "General wellness", kind: "wellness", explanation: "Consistent measurement timing improves comparability of readings over time.", nextStep: "Take readings at a similar time each day, seated and rested.", related: "All biometric measurements" },
  { id: "RC-02", category: "Repeat measurement", kind: "advisory", explanation: "Single readings can be affected by movement, posture or sensor placement.", nextStep: "Repeat the measurement after 5 minutes of rest.", related: "Heart rate · Blood pressure" },
  { id: "RC-03", category: "Review measurement quality", kind: "advisory", explanation: "ECG traces with motion artefacts may not be suitable for automated analysis.", nextStep: "Check electrode contact and re-record if the trace is noisy.", related: "ECG recording" },
  { id: "RC-04", category: "Seek professional medical assessment", kind: "advisory", explanation: "Automated results are not a diagnosis. Persistent symptoms warrant clinical review.", nextStep: "Consult a qualified healthcare professional about any concerns.", related: "CNN analysis (pending)" },
];

export const demoSensors: SensorStatus[] = [
  { id: "max30102", name: "MAX30102", measures: "Heart rate · SpO₂", state: "not_connected" },
  { id: "ecg", name: "ECG front-end (AD8232)", measures: "ECG signal", state: "not_connected" },
  { id: "temp", name: "Temperature sensor", measures: "Body temperature", state: "not_connected" },
  { id: "bp", name: "Blood pressure cuff", measures: "Systolic · Diastolic", state: "not_connected" },
];
