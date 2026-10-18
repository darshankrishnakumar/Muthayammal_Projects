import { apiRequest, endpoints, ApiError } from "./apiClient";
import type { PredictionResult } from "@/types/prediction";

export interface StoredEcgRecording {
  id: number;
  originalFilename: string;
  storedFilename: string;
  fileFormat: string;
  fileSizeBytes: number;
  recordingDurationSeconds: number | null;
  samplingFrequencyHz: number | null;
  uploadStatus: string;
  source: string;
  createdAt: string;
}

export interface EcgRecordingsResponse {
  total: number;
  limit: number;
  offset: number;
  recordings: StoredEcgRecording[];
}

export interface EcgSamplesResponse {
  recordingId: number;
  originalFilename: string;
  samplingFrequencyHz: number;
  samples: { t: number; mv: number }[];
  pointCount: number;
  durationSeconds: number;
}

export function uploadEcg(file: File, source = "upload") {
  const body = new FormData();
  body.append("file", file);
  body.append("source", source);
  return apiRequest<{
    recordingId: string;
    id: number;
    originalFilename: string;
    storedFilename: string;
    fileFormat: string;
    fileSizeBytes: number;
    samplingFrequencyHz: number | null;
    uploadStatus: string;
    createdAt: string;
  }>(endpoints.ecgUpload, { method: "POST", body });
}

export function getEcgRecordings(params?: { status?: string; source?: string; limit?: number; offset?: number }) {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.source) query.set("source", params.source);
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.offset) query.set("offset", String(params.offset));

  const qs = query.toString();
  const url = qs ? `${endpoints.ecgRecordings}?${qs}` : endpoints.ecgRecordings;
  return apiRequest<EcgRecordingsResponse>(url);
}

export function getEcgRecordingById(id: string | number) {
  return apiRequest<StoredEcgRecording>(endpoints.ecgRecordingById(id));
}

export function getEcgRecordingSamples(id: string | number) {
  return apiRequest<EcgSamplesResponse>(endpoints.ecgSamples(id));
}

export function deleteEcgRecording(id: string | number) {
  return apiRequest<{ id: number; deleted: boolean; message: string }>(endpoints.ecgRecordingById(id), {
    method: "DELETE",
  });
}

export function requestPrediction(recordingId: string | number) {
  return apiRequest<PredictionResult>(endpoints.predictions, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recordingId: Number(recordingId) }),
  });
}

export function getPredictionHistory() {
  return apiRequest<PredictionResult[]>(endpoints.predictionHistory);
}

async function readFileAsText(file: File): Promise<string> {
  if (typeof file.text === "function") {
    return await file.text();
  }
  if (typeof file.arrayBuffer === "function") {
    const buf = await file.arrayBuffer();
    return new TextDecoder().decode(buf);
  }
  if (typeof FileReader !== "undefined") {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result ?? ""));
      reader.onerror = () => reject(reader.error || new Error("Failed to read file"));
      reader.readAsText(file);
    });
  }
  return "";
}

/**
 * Validates and parses client-side ECG files (CSV, TXT, JSON) to reject arbitrary non-ECG files
 * and provide immediate real waveform preview.
 */
export async function parseEcgFile(file: File): Promise<{
  samples: { t: number; mv: number }[];
  sampleRate: number;
  pointCount: number;
  durationSeconds: number;
}> {
  const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  const maxBytes = 10 * 1024 * 1024; // 10MB
  if (file.size > maxBytes) {
    throw new Error(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds maximum allowed 10 MB.`);
  }

  const sampleRate = 360;
  const maxPoints = 1800; // 5s preview
  const text = await readFileAsText(file);

  if (!text || text.trim().length === 0) {
    throw new Error("The selected file is empty.");
  }

  const samples: { t: number; mv: number }[] = [];

  if (ext === ".json") {
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new Error("Invalid JSON syntax in ECG file.");
    }

    const rawArray: unknown[] = Array.isArray(parsed)
      ? parsed
      : (parsed && typeof parsed === "object" && ("data" in parsed || "samples" in parsed)
          // @ts-expect-error dynamic access
          ? (parsed.data || parsed.samples)
          : []);

    if (!Array.isArray(rawArray) || rawArray.length === 0) {
      throw new Error("JSON structure does not contain an array of numeric ECG signal samples.");
    }

    const count = Math.min(rawArray.length, maxPoints);
    for (let i = 0; i < count; i++) {
      const item = rawArray[i];
      const val = typeof item === "number" ? item : (item && typeof item === "object" && "mv" in item ? Number(item.mv) : NaN);
      if (isNaN(val)) {
        throw new Error("JSON contains non-numeric values in ECG signal data.");
      }
      samples.push({
        t: Math.round((i / sampleRate) * 1000) / 1000,
        mv: Math.round(val * 1000) / 1000,
      });
    }
  } else if (ext === ".csv" || ext === ".txt") {
    const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
    if (lines.length < 5) {
      throw new Error("ECG recording file has insufficient rows (at least 5 samples required).");
    }

    let pointIdx = 0;
    let numericRowsCount = 0;

    for (const line of lines) {
      if (pointIdx >= maxPoints) break;
      const parts = line.split(/[,\s\t]+/).map((p) => p.trim()).filter(Boolean);
      const nums = parts.map(Number).filter((n) => !isNaN(n));
      if (nums.length === 0) {
        continue; // header line
      }
      numericRowsCount++;
      // If time + voltage or just voltage
      const val = nums.length > 1 ? nums[1] : nums[0];
      samples.push({
        t: Math.round((pointIdx / sampleRate) * 1000) / 1000,
        mv: Math.round(val * 1000) / 1000,
      });
      pointIdx++;
    }

    if (numericRowsCount < 5) {
      throw new Error("File structure is not a valid ECG signal: no numeric voltage readings found.");
    }
  } else {
    // Binary formats like .dat or .edf are uploaded directly for backend/ML processing
    // Client-side preview for binary without heavy parsers:
    return {
      samples: [],
      sampleRate,
      pointCount: 0,
      durationSeconds: 0,
    };
  }

  return {
    samples,
    sampleRate,
    pointCount: samples.length,
    durationSeconds: samples.length > 0 ? Math.round((samples.length / sampleRate) * 10) / 10 : 0,
  };
}

/** Placeholder shown until a real model returns output. Never contains invented values. */
export const pendingPrediction: PredictionResult = {
  id: "—",
  recordingId: "DEMO-ECG-001",
  status: "integration_pending",
  modelName: "1D CNN (TensorFlow/Keras)",
  modelVersion: null,
  predictedCategory: null,
  confidence: null,
  analysedAt: null,
  explanation: null,
};
