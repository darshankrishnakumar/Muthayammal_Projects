import { apiRequest, endpoints } from "./apiClient";
import type { Measurement } from "@/types/health";

export interface MeasurementRecord {
  id: number;
  measurementType: "heart_rate" | "blood_pressure" | "spo2" | "body_temperature";
  value: number | null;
  unit: string;
  systolic: number | null;
  diastolic: number | null;
  measuredAt: string;
  source: "manual" | "sensor" | "demo";
  dataQualityStatus: "valid" | "review_required" | "unverified";
  createdAt: string;
}

export interface MeasurementsResponse {
  total: number;
  limit: number;
  offset: number;
  records: MeasurementRecord[];
}

export interface MetricSummaryItem<TStats = Record<string, number>> {
  latest: MeasurementRecord | null;
  stats: TStats & { count: number };
}

export interface HealthSummaryData {
  heart_rate: MetricSummaryItem<{ min?: number; max?: number; avg?: number }>;
  blood_pressure: MetricSummaryItem<{
    minSystolic?: number;
    maxSystolic?: number;
    avgSystolic?: number;
    minDiastolic?: number;
    maxDiastolic?: number;
    avgDiastolic?: number;
  }>;
  spo2: MetricSummaryItem<{ min?: number; max?: number; avg?: number }>;
  body_temperature: MetricSummaryItem<{ min?: number; max?: number; avg?: number }>;
}

export interface CreateManualMeasurementInput {
  heartRate?: number;
  systolic?: number;
  diastolic?: number;
  spo2?: number;
  temperature?: number;
  measuredAt?: string;
  source?: "manual" | "sensor" | "demo";
}

export interface UpdateMeasurementInput {
  value?: number;
  systolic?: number;
  diastolic?: number;
  unit?: string;
  measuredAt?: string;
}

export function getMeasurements(params?: {
  measurementType?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}) {
  const query = new URLSearchParams();
  if (params?.measurementType && params.measurementType !== "all") {
    query.set("measurementType", params.measurementType);
  }
  if (params?.startDate) query.set("startDate", params.startDate);
  if (params?.endDate) query.set("endDate", params.endDate);
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.offset) query.set("offset", String(params.offset));

  const qs = query.toString();
  const url = qs ? `${endpoints.measurements}?${qs}` : endpoints.measurements;
  return apiRequest<MeasurementsResponse>(url);
}

export function getHealthSummary() {
  return apiRequest<HealthSummaryData>(endpoints.healthSummary);
}

export function getHealthTrends(params?: { metric?: string; startDate?: string; endDate?: string; limit?: number }) {
  const query = new URLSearchParams();
  if (params?.metric) query.set("metric", params.metric);
  if (params?.startDate) query.set("startDate", params.startDate);
  if (params?.endDate) query.set("endDate", params.endDate);
  if (params?.limit) query.set("limit", String(params.limit));

  const qs = query.toString();
  const url = qs ? `${endpoints.healthTrends}?${qs}` : endpoints.healthTrends;
  return apiRequest<Measurement[]>(url);
}

export function createManualMeasurement(input: CreateManualMeasurementInput) {
  return apiRequest<{
    timestamp: string;
    source: string;
    createdCount: number;
    records: MeasurementRecord[];
  }>(endpoints.measurements, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...input,
      source: input.source || "manual",
    }),
  });
}

export function updateMeasurement(id: number | string, input: UpdateMeasurementInput) {
  return apiRequest<MeasurementRecord>(endpoints.measurementById(id), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export function deleteMeasurement(id: number | string) {
  return apiRequest<{ id: number; deleted: boolean; message: string }>(endpoints.measurementById(id), {
    method: "DELETE",
  });
}

// Backwards compatibility with any existing imports
export const postMeasurement = (m: Omit<Measurement, "source">) =>
  createManualMeasurement({
    heartRate: m.heartRate,
    systolic: m.systolic,
    diastolic: m.diastolic,
    spo2: m.spo2,
    temperature: m.temperature,
    measuredAt: m.timestamp,
    source: "manual",
  });
