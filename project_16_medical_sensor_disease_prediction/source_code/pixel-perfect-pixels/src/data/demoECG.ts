import type { EcgRecording } from "@/types/prediction";

/**
 * Illustrative ECG: a prepared, deterministic PQRST template built from
 * Gaussian components and repeated at a fixed rhythm. It is NOT a recording
 * of any patient and NOT a live sensor feed.
 */
export const ECG_RENDER_HZ = 250;
const BEAT_SEC = 0.83; // ~72 BPM template

const waves = [
  { a: 0.12, mu: 0.16, s: 0.025 }, // P
  { a: -0.1, mu: 0.25, s: 0.01 }, // Q
  { a: 1.1, mu: 0.28, s: 0.012 }, // R
  { a: -0.22, mu: 0.31, s: 0.012 }, // S
  { a: 0.28, mu: 0.52, s: 0.045 }, // T
];

function sampleAt(t: number) {
  const p = t % BEAT_SEC;
  return waves.reduce((v, w) => v + w.a * Math.exp(-((p - w.mu) ** 2) / (2 * w.s ** 2)), 0);
}

export function buildIllustrativeEcg(seconds: number) {
  const n = Math.round(seconds * ECG_RENDER_HZ);
  return Array.from({ length: n }, (_, i) => {
    const t = i / ECG_RENDER_HZ;
    return { t: Number(t.toFixed(3)), mv: Number(sampleAt(t).toFixed(3)) };
  });
}

export const illustrativeRecording: EcgRecording = {
  id: "DEMO-ECG-001",
  label: "Illustrative ECG template",
  source: "Synthetic PQRST template (frontend demo)",
  durationSec: 10,
  samplingHz: ECG_RENDER_HZ,
  quality: null,
  status: "Illustrative — not recorded",
};
