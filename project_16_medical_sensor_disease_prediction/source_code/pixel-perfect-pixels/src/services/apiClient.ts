/**
 * Node.js / Express backend integration. Base URL comes from VITE_API_BASE_URL.
 * While unset, the app stays in explicit demonstration mode and no request is sent.
 */
export const API_BASE_URL: string | undefined = import.meta.env["VITE_API_BASE_URL"] || undefined;
export const isDemoMode = !API_BASE_URL;

export class BackendNotConnectedError extends Error {
  constructor() {
    super("Backend not connected. Set VITE_API_BASE_URL to enable the backend integration.");
  }
}

export class ApiError extends Error {
  status: number;
  code: string;
  details?: unknown;

  constructor(message: string, status = 500, code = 'INTERNAL_ERROR', details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE_URL) throw new BackendNotConnectedError();
  const base = API_BASE_URL.replace(/\/api\/?$/, "");
  const normalizedPath = path.startsWith("/api") ? path : `/api${path}`;
  const res = await fetch(`${base}${normalizedPath}`, init);
  if (!res.ok) {
    const errorJson = await res.json().catch(() => null);
    const message = errorJson?.message || `Request failed (${res.status})`;
    const code = errorJson?.code || `HTTP_${res.status}`;
    const details = errorJson?.details;
    throw new ApiError(message, res.status, code, details);
  }
  const json = await res.json();
  if (json && typeof json === "object" && "data" in json) {
    return json.data as T;
  }
  return json as T;
}

export const endpoints = {
  measurements: "/api/health/measurements",
  measurementById: (id: string | number) => `/api/health/measurements/${id}`,
  healthSummary: "/api/health/summary",
  healthTrends: "/api/health/trends",
  ecgUpload: "/api/ecg/upload",
  ecgRecordings: "/api/ecg/recordings",
  ecgRecordingById: (id: string | number) => `/api/ecg/recordings/${id}`,
  ecgSamples: (id: string | number) => `/api/ecg/recordings/${id}/samples`,
  predictions: "/api/predictions",
  predictionHistory: "/api/predictions/history",
  recommendations: "/api/recommendations",
  alerts: "/api/alerts",
  reportsSummary: "/api/reports/summary",
  systemStatus: "/api/system/status",
} as const;
