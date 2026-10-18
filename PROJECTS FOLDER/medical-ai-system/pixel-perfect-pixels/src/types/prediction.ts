export type PredictionStatus = "integration_pending" | "queued" | "processing" | "complete" | "error";

/** Shape the future FastAPI /api/predictions endpoint is expected to return. */
export interface PredictionResult {
  id: string;
  recordingId: string;
  status: PredictionStatus;
  modelName: string | null;
  modelVersion: string | null;
  predictedCategory: string | null;
  confidence: number | null; // 0..1, only from real model output
  analysedAt: string | null;
  explanation: string | null;
}

export interface EcgRecording {
  id: string;
  label: string;
  source: string;
  durationSec: number | null;
  samplingHz: number | null;
  quality: string | null;
  status: string;
}
