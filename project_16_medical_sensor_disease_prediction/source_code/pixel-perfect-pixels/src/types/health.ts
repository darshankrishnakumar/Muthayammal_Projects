export type MetricKey = "heartRate" | "bloodPressure" | "spo2" | "temperature";

export type DataSource = "demo" | "manual" | "sensor";

export interface Measurement {
  timestamp: string; // ISO
  heartRate: number; // BPM
  systolic: number; // mmHg
  diastolic: number; // mmHg
  spo2: number; // %
  temperature: number; // °C
  source: DataSource;
}

export interface Recommendation {
  id: string;
  category: "General wellness" | "Repeat measurement" | "Review measurement quality" | "Seek professional medical assessment";
  kind: "wellness" | "advisory";
  explanation: string;
  nextStep: string;
  related: string;
}

export type AlertPriority = "info" | "review" | "warning";

export interface HealthAlert {
  id: string;
  category: string;
  description: string;
  detail: string;
  timestamp: string | null;
  priority: AlertPriority;
}

export type RecordType = "Measurement" | "ECG recording" | "Analysis" | "Recommendation";
export type AnalysisStatus = "Pending integration" | "Not analysed" | "Validation failed" | "Recorded";

export interface HistoryRecord {
  id: string;
  date: string; // ISO
  type: RecordType;
  status: AnalysisStatus;
  result: string;
  notes: string;
}
