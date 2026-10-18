import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect, useMemo } from "react";
import { PageHeader, Panel, PanelHeader, Tag, EmptyState, Notice } from "@/components/common";
import { getPredictionHistory } from "@/services/predictionService";
import { apiRequest, endpoints } from "@/services/apiClient";
import type { PredictionResult } from "@/types/prediction";
import { Activity, BrainCircuit, CheckCircle2, AlertTriangle, RefreshCw, ArrowUpRight, Search, Zap } from "lucide-react";

export const Route = createFileRoute("/predictions")({
  head: () => ({
    meta: [
      { title: "AI Predictions — BioPulse" },
      { name: "description", content: "CNN arrhythmia predictions and classification audit history." },
      { property: "og:title", content: "AI Predictions — BioPulse" },
      { property: "og:description", content: "CNN arrhythmia predictions and classification audit history." },
    ],
  }),
  component: PredictionsPage,
});

function getRhythmTone(category: string | null): "success" | "warning" | "signal" | "highlight" | "neutral" {
  if (!category) return "neutral";
  const cat = category.toLowerCase();
  if (cat.includes("normal")) return "success";
  if (cat.includes("ventricular")) return "warning";
  if (cat.includes("supraventricular")) return "signal";
  if (cat.includes("fusion")) return "highlight";
  return "neutral";
}

export function PredictionsPage() {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modelStatus, setModelStatus] = useState<{ status: string; service: string } | null>(null);
  const [selectedClass, setSelectedClass] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionResult | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyData, systemData] = await Promise.all([
        getPredictionHistory().catch(() => []),
        apiRequest<{ cnnModel?: { status: string; service: string } }>(endpoints.systemStatus).catch(() => null),
      ]);
      setPredictions(historyData || []);
      if (systemData?.cnnModel) {
        setModelStatus(systemData.cnnModel);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load predictions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filtered list
  const filteredPredictions = useMemo(() => {
    return predictions.filter((p) => {
      const matchClass =
        selectedClass === "all" ||
        (selectedClass === "normal" && p.predictedCategory?.toLowerCase().includes("normal")) ||
        (selectedClass === "ventricular" && p.predictedCategory?.toLowerCase().includes("ventricular")) ||
        (selectedClass === "supraventricular" && p.predictedCategory?.toLowerCase().includes("supraventricular")) ||
        (selectedClass === "other" && !p.predictedCategory?.toLowerCase().includes("normal") && !p.predictedCategory?.toLowerCase().includes("ventricular"));

      const matchSearch =
        !searchQuery ||
        p.recordingId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.predictedCategory?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.modelName?.toLowerCase().includes(searchQuery.toLowerCase());

      return matchClass && matchSearch;
    });
  }, [predictions, selectedClass, searchQuery]);

  // Statistics
  const stats = useMemo(() => {
    const total = predictions.length;
    const completed = predictions.filter((p) => p.status === "completed" || p.predictedCategory !== null);
    const normalCount = completed.filter((p) => p.predictedCategory?.toLowerCase().includes("normal")).length;
    const ectopicsCount = completed.length - normalCount;
    const confidences = completed.map((p) => p.confidence).filter((c): c is number => c !== null);
    const avgConfidence = confidences.length > 0 ? (confidences.reduce((a, b) => a + b, 0) / confidences.length) * 100 : null;

    return { total, normalCount, ectopicsCount, avgConfidence };
  }, [predictions]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Predictions"
        subtitle="1D CNN arrhythmia classification results, confidence metrics, and prediction audit log."
        actions={
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={fetchData}
              disabled={loading}
              className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised disabled:opacity-50"
            >
              <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link
              to="/ecg"
              className="inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90"
            >
              <Zap className="size-3.5" />
              New ECG Analysis
            </Link>
          </div>
        }
      />

      {/* Model & System Status Banner */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">CNN Service</span>
            <Tag tone={modelStatus?.status === "connected" ? "success" : "signal"} dot>
              {modelStatus?.status === "connected" ? "Active" : "Ready"}
            </Tag>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <BrainCircuit className="size-4 text-signal" />
            <p className="text-sm font-semibold text-foreground">Residual 1D CNN</p>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">Port 5001 • AAMI 5-Class</p>
        </Panel>

        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Analyzed Recordings</span>
            <Activity className="size-3.5 text-muted-foreground" />
          </div>
          <p className="mt-2 text-xl font-bold font-mono text-foreground">{stats.total}</p>
          <p className="mt-1 text-[11px] text-muted-foreground">Total records processed</p>
        </Panel>

        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Rhythm Distribution</span>
            <CheckCircle2 className="size-3.5 text-success" />
          </div>
          <div className="mt-2 flex items-baseline gap-2 font-mono">
            <span className="text-xl font-bold text-success">{stats.normalCount}</span>
            <span className="text-xs text-muted-foreground">Normal /</span>
            <span className="text-xl font-bold text-warning">{stats.ectopicsCount}</span>
            <span className="text-xs text-muted-foreground">Ectopic</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            {stats.total > 0 ? `${((stats.normalCount / stats.total) * 100).toFixed(0)}% Sinus Rhythm` : "No recordings yet"}
          </p>
        </Panel>

        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Mean Confidence</span>
            <span className="font-mono text-xs text-signal">%</span>
          </div>
          <p className="mt-2 text-xl font-bold font-mono text-signal">
            {stats.avgConfidence !== null ? `${stats.avgConfidence.toFixed(1)}%` : "—"}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">Real output probabilities</p>
        </Panel>
      </div>

      {/* Main Predictions Panel */}
      <Panel>
        <PanelHeader
          title="Prediction History & Audit Trail"
          subtitle="Chronological log of verified CNN model inferences stored in SQLite."
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 size-3 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Filter by ID or rhythm..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-7 w-48 rounded-md border border-border bg-input pl-7 pr-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:border-signal focus:outline-none"
                />
              </div>

              <div className="inline-flex rounded-md border border-border bg-input p-0.5 text-xs">
                {[
                  { id: "all", label: "All" },
                  { id: "normal", label: "Normal (N)" },
                  { id: "ventricular", label: "Ventricular (V)" },
                  { id: "supraventricular", label: "Supra (S)" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setSelectedClass(tab.id)}
                    className={`rounded-sm px-2 py-0.5 transition-colors ${
                      selectedClass === tab.id ? "bg-surface-raised font-medium text-signal" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          }
        />

        {error && (
          <div className="mb-4">
            <Notice tone="warning" icon={<AlertTriangle />}>
              {error}
            </Notice>
          </div>
        )}

        {loading ? (
          <div className="flex h-48 items-center justify-center">
            <RefreshCw className="size-6 animate-spin text-signal" />
          </div>
        ) : filteredPredictions.length === 0 ? (
          <EmptyState
            title="No prediction records found"
            text={
              predictions.length === 0
                ? "No ECG recordings have been analyzed by the CNN model yet. Upload an ECG signal file to generate the first real classification."
                : "No prediction records match the current filter criteria."
            }
            icon={<BrainCircuit className="size-6 text-signal" />}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border/80 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="pb-2.5 pl-2 font-mono">Prediction ID</th>
                  <th className="pb-2.5 font-mono">Recording</th>
                  <th className="pb-2.5">Classified Rhythm</th>
                  <th className="pb-2.5">Confidence</th>
                  <th className="pb-2.5">Model Architecture</th>
                  <th className="pb-2.5">Analyzed At</th>
                  <th className="pb-2.5 pr-2 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {filteredPredictions.map((pred) => {
                  const confPct = pred.confidence !== null ? Math.round(pred.confidence * 1000) / 10 : null;
                  const tone = getRhythmTone(pred.predictedCategory);

                  return (
                    <tr key={pred.id} className="transition-colors hover:bg-surface-raised/40">
                      <td className="py-3 pl-2 font-semibold text-foreground">#{pred.id}</td>
                      <td className="py-3 text-signal">
                        <Link to="/ecg" className="hover:underline">
                          ECG-{pred.recordingId}
                        </Link>
                      </td>
                      <td className="py-3 font-sans">
                        <div className="flex items-center gap-1.5">
                          <Tag tone={tone} dot>
                            {pred.predictedCategory || "Pending Analysis"}
                          </Tag>
                        </div>
                      </td>
                      <td className="py-3">
                        {confPct !== null ? (
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-border">
                              <div
                                className={`h-full rounded-full ${
                                  confPct >= 80 ? "bg-success" : confPct >= 60 ? "bg-signal" : "bg-warning"
                                }`}
                                style={{ width: `${confPct}%` }}
                              />
                            </div>
                            <span className="text-[11px] font-semibold text-foreground">{confPct}%</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="py-3 text-[11px] text-muted-foreground font-sans">
                        {pred.modelName || "Residual 1D CNN"}{" "}
                        {pred.modelVersion ? <span className="font-mono text-[10px] text-signal">v{pred.modelVersion}</span> : ""}
                      </td>
                      <td className="py-3 text-[11px] text-muted-foreground font-sans">
                        {pred.analysedAt ? new Date(pred.analysedAt).toLocaleString() : "—"}
                      </td>
                      <td className="py-3 pr-2 text-right">
                        <button
                          type="button"
                          onClick={() => setSelectedPrediction(pred)}
                          className="inline-flex items-center gap-1 rounded border border-border px-2 py-0.5 text-[11px] text-muted-foreground transition-colors hover:bg-surface-raised hover:text-foreground font-sans"
                        >
                          View <ArrowUpRight className="size-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Selected Prediction Modal */}
      {selectedPrediction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-lg border border-border bg-surface p-6 shadow-xl">
            <div className="flex items-start justify-between border-b border-border/80 pb-3">
              <div>
                <h3 className="text-base font-semibold text-foreground">
                  Prediction Audit Record #{selectedPrediction.id}
                </h3>
                <p className="text-xs text-muted-foreground font-mono">ECG Recording ID: {selectedPrediction.recordingId}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedPrediction(null)}
                className="rounded-md p-1 text-muted-foreground hover:bg-surface-raised hover:text-foreground"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="rounded-md border border-border/60 bg-surface-raised/50 p-3">
                <span className="text-[11px] font-medium text-muted-foreground">Classified Rhythm:</span>
                <div className="mt-1 flex items-center gap-2">
                  <Tag tone={getRhythmTone(selectedPrediction.predictedCategory)} dot>
                    {selectedPrediction.predictedCategory || "Unclassified"}
                  </Tag>
                  {selectedPrediction.confidence !== null && (
                    <span className="font-mono font-semibold text-signal">
                      {(selectedPrediction.confidence * 100).toFixed(1)}% Confidence
                    </span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[11px] font-medium text-muted-foreground">Clinical Diagnostic Explanation:</span>
                <p className="mt-1 rounded-md border border-border/40 bg-input p-3 text-xs leading-relaxed text-foreground">
                  {selectedPrediction.explanation || "No explanation recorded for this prediction."}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-muted-foreground">Model Name:</span>
                  <p className="font-mono text-foreground">{selectedPrediction.modelName || "Residual 1D CNN"}</p>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground">Model Version:</span>
                  <p className="font-mono text-foreground">{selectedPrediction.modelVersion || "1.1.0"}</p>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground">Status:</span>
                  <p className="font-mono text-foreground capitalize">{selectedPrediction.status}</p>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground">Analyzed Timestamp:</span>
                  <p className="font-mono text-foreground">
                    {selectedPrediction.analysedAt ? new Date(selectedPrediction.analysedAt).toLocaleString() : "—"}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedPrediction(null)}
                className="rounded-md bg-surface-raised border border-border px-4 py-1.5 text-xs font-medium text-foreground hover:bg-border"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Medical Governance Notice */}
      <Notice tone="neutral" icon={<CheckCircle2 />}>
        <strong>Clinical AI Boundary:</strong> The Residual 1D CNN arrhythmia classifier was trained on patient-segregated MIT-BIH recordings. The model evaluates ECG morphology and rhythm exclusively; it does not process or diagnose from non-ECG vitals (blood pressure, oxygen saturation, temperature). All predictions are advisory decision support.
      </Notice>
    </div>
  );
}
