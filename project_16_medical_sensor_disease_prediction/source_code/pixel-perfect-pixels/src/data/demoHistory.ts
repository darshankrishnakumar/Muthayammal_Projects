import type { HistoryRecord } from "@/types/health";

const types = ["Measurement", "ECG recording", "Analysis", "Recommendation"] as const;
const statusFor = { Measurement: "Recorded", "ECG recording": "Not analysed", Analysis: "Pending integration", Recommendation: "Recorded" } as const;
const resultFor = { Measurement: "—", "ECG recording": "Awaiting CNN model", Analysis: "Model integration pending", Recommendation: "Illustrative content" } as const;

export const demoHistory: HistoryRecord[] = Array.from({ length: 24 }, (_, i) => {
  const type = types[i % 4]!;
  return {
    id: `DEMO-${String(1024 - i).padStart(4, "0")}`,
    date: new Date(Date.UTC(2026, 9, 9, 9) - i * 31 * 3600 * 1000).toISOString(),
    type,
    status: i === 6 ? "Validation failed" : statusFor[type],
    result: i === 6 ? "File format not supported" : resultFor[type],
    notes: "Demonstration record. Not stored in any database.",
  };
});
