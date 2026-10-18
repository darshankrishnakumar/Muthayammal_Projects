import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Upload,
  FileCheck,
  AlertCircle,
  Play,
  Waves,
  FileText,
  Clock,
  Trash2,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  HelpCircle,
  FileCode2,
} from "lucide-react";
import { PageHeader, Panel, PanelHeader, Tag, Notice, EmptyState, InfoTip, KV } from "@/components/common";
import { EcgChart } from "@/components/charts/EcgChart";
import { Button } from "@/components/ui/button";
import {
  uploadEcg,
  getEcgRecordings,
  getEcgRecordingSamples,
  deleteEcgRecording,
  requestPrediction,
  getPredictionHistory,
  parseEcgFile,
  type StoredEcgRecording,
} from "@/services/predictionService";
import { ApiError } from "@/services/apiClient";
import type { PredictionResult } from "@/types/prediction";
import { fmtDateTime } from "@/utils/format";

export const Route = createFileRoute("/ecg")({
  head: () => ({
    meta: [
      { title: "ECG Analysis — BioPulse" },
      { name: "description", content: "ECG signal file upload, waveform visualization, and 1D CNN arrhythmia classification interface." },
      { property: "og:title", content: "ECG Analysis — BioPulse" },
      { property: "og:description", content: "ECG signal processing and CNN classification." },
    ],
  }),
  component: EcgAnalysisPage,
});

export function EcgAnalysisPage() {
  // Upload and file selection state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileValidationStatus, setFileValidationStatus] = useState<"idle" | "validating" | "valid" | "invalid">("idle");
  const [fileValidationMessage, setFileValidationMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState<string | null>(null);

  // Active recording & waveform state
  const [activeRecording, setActiveRecording] = useState<StoredEcgRecording | null>(null);
  const [waveformSamples, setWaveformSamples] = useState<{ t: number; mv: number }[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);

  // Analysis / Inference state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<PredictionResult | null>(null);
  const [modelStatus, setModelStatus] = useState<{
    code: string | null;
    message: string | null;
    isError: boolean;
  }>({ code: null, message: null, isError: false });

  // List data
  const [recordings, setRecordings] = useState<StoredEcgRecording[]>([]);
  const [predictionHistory, setPredictionHistory] = useState<PredictionResult[]>([]);
  const [loadingLists, setLoadingLists] = useState(false);

  // Refresh recording lists and prediction history
  const loadLists = useCallback(async () => {
    setLoadingLists(true);
    try {
      const [recsRes, histRes] = await Promise.all([
        getEcgRecordings({ limit: 50 }).catch(() => ({ total: 0, limit: 50, offset: 0, recordings: [] })),
        getPredictionHistory().catch(() => []),
      ]);

      setRecordings(recsRes.recordings);
      setPredictionHistory(histRes);

      // Default active recording to first one if none selected
      if (!activeRecording && recsRes.recordings.length > 0) {
        selectRecording(recsRes.recordings[0]);
      }
    } catch (err: unknown) {
      console.error("Failed to load ECG data:", err);
    } finally {
      setLoadingLists(false);
    }
  }, [activeRecording]);

  useEffect(() => {
    loadLists();
  }, [loadLists]);

  // Select a recording and fetch its waveform samples
  const selectRecording = async (rec: StoredEcgRecording) => {
    setActiveRecording(rec);
    setAnalysisResult(null);
    setModelStatus({ code: null, message: null, isError: false });
    setLoadingSamples(true);

    try {
      const sampleData = await getEcgRecordingSamples(rec.id);
      if (sampleData && sampleData.samples && sampleData.samples.length > 0) {
        setWaveformSamples(sampleData.samples);
      } else {
        setWaveformSamples([]);
      }
    } catch {
      // If server file is binary or samples not extracted, waveform falls back to standard display
      setWaveformSamples([]);
    } finally {
      setLoadingSamples(false);
    }
  };

  // Handle local file selection and pre-upload structure validation
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setUploadSuccessMessage(null);
    setFileValidationStatus("validating");
    setFileValidationMessage(null);

    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    const allowed = [".csv", ".txt", ".dat", ".json", ".edf"];
    if (!allowed.includes(ext)) {
      setFileValidationStatus("invalid");
      setFileValidationMessage(`Unsupported file format '${ext}'. Allowed formats: ${allowed.join(", ")}`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setFileValidationStatus("invalid");
      setFileValidationMessage(`File size exceeds 10 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB).`);
      return;
    }

    try {
      const parsed = await parseEcgFile(file);
      setFileValidationStatus("valid");
      setFileValidationMessage(
        parsed.pointCount > 0
          ? `Verified valid ECG signal: parsed ${parsed.pointCount} voltage samples (${parsed.durationSeconds}s @ ${parsed.sampleRate} Hz).`
          : "Binary ECG recording format verified for upload."
      );
      if (parsed.samples.length > 0) {
        setWaveformSamples(parsed.samples);
      }
    } catch (err: unknown) {
      setFileValidationStatus("invalid");
      setFileValidationMessage(err instanceof Error ? err.message : "Invalid ECG file structure.");
    }
  };

  // Upload file to backend
  const handleUpload = async () => {
    if (!selectedFile || fileValidationStatus === "invalid") return;

    setIsUploading(true);
    setUploadSuccessMessage(null);
    try {
      const result = await uploadEcg(selectedFile);
      setUploadSuccessMessage(
        `ECG recording '${result.originalFilename}' successfully uploaded and registered (ID: #${result.id}).`
      );

      // Reload list and set as active recording
      await loadLists();
      const updatedRecs = await getEcgRecordings({ limit: 1 });
      if (updatedRecs.recordings.length > 0) {
        await selectRecording(updatedRecs.recordings[0]);
      }
    } catch (err: unknown) {
      setFileValidationStatus("invalid");
      setFileValidationMessage(err instanceof Error ? err.message : "Failed to upload ECG recording.");
    } finally {
      setIsUploading(false);
    }
  };

  // Run CNN Analysis
  const handleRunAnalysis = async () => {
    if (!activeRecording) return;

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setModelStatus({ code: null, message: null, isError: false });

    try {
      const res = await requestPrediction(activeRecording.id);
      setAnalysisResult(res);
      setModelStatus({
        code: "MODEL_CONNECTED",
        message: "Analysis completed successfully by the 1D CNN model.",
        isError: false,
      });
      await loadLists();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 503 || err.code === "MODEL_NOT_CONNECTED") {
          setModelStatus({
            code: "MODEL_NOT_CONNECTED",
            message:
              "The CNN model inference service has not been connected. Medical Safety Guard Active: synthetic predictions and fake confidence scores are strictly never fabricated.",
            isError: true,
          });
        } else {
          setModelStatus({
            code: err.code || "ANALYSIS_ERROR",
            message: err.message || "Failed to process ECG analysis request.",
            isError: true,
          });
        }
      } else {
        setModelStatus({
          code: "MODEL_NOT_CONNECTED",
          message:
            "The 1D CNN inference service is currently offline or unreachable. No synthetic results generated.",
          isError: true,
        });
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Delete recording
  const handleDeleteRecording = async (id: number) => {
    try {
      await deleteEcgRecording(id);
      if (activeRecording?.id === id) {
        setActiveRecording(null);
        setWaveformSamples([]);
        setAnalysisResult(null);
      }
      await loadLists();
    } catch (err: unknown) {
      console.error("Failed to delete recording:", err);
    }
  };

  // Generate a sample MIT-BIH benchmark CSV for immediate offline testing
  const handleLoadSampleDataset = () => {
    // Generate a valid 5-second simulated lead II ECG sequence with realistic P-QRS-T complex points
    const lines = ["time_sec,mlii_voltage_mv"];
    const fs = 360;
    const durationSec = 5;
    const totalPoints = fs * durationSec;
    const heartRateBpm = 75;
    const rPeakPeriod = (60 / heartRateBpm) * fs;

    for (let i = 0; i < totalPoints; i++) {
      const t = Math.round((i / fs) * 1000) / 1000;
      const phase = (i % rPeakPeriod) / rPeakPeriod;
      let mv = 0.05 * Math.sin(2 * Math.PI * 0.5 * t); // Baseline slight wander

      // P wave (phase 0.15 - 0.25)
      if (phase >= 0.15 && phase <= 0.25) {
        mv += 0.18 * Math.sin(Math.PI * ((phase - 0.15) / 0.1));
      }
      // Q dip (phase 0.28 - 0.30)
      else if (phase >= 0.28 && phase <= 0.3) {
        mv -= 0.15 * Math.sin(Math.PI * ((phase - 0.28) / 0.02));
      }
      // R peak (phase 0.30 - 0.34)
      else if (phase > 0.3 && phase <= 0.34) {
        mv += 1.25 * Math.sin(Math.PI * ((phase - 0.3) / 0.04));
      }
      // S dip (phase 0.34 - 0.37)
      else if (phase > 0.34 && phase <= 0.37) {
        mv -= 0.35 * Math.sin(Math.PI * ((phase - 0.34) / 0.03));
      }
      // T wave (phase 0.45 - 0.65)
      else if (phase >= 0.45 && phase <= 0.65) {
        mv += 0.32 * Math.sin(Math.PI * ((phase - 0.45) / 0.2));
      }

      // Add subtle physiological noise
      mv += (Math.random() - 0.5) * 0.02;
      lines.push(`${t},${mv.toFixed(4)}`);
    }

    const csvBlob = new Blob([lines.join("\n")], { type: "text/csv" });
    const sampleFile = new File([csvBlob], "mitbih_sample_100_lead_II.csv", { type: "text/csv" });

    // Trigger file change with the generated valid sample
    setSelectedFile(sampleFile);
    parseEcgFile(sampleFile).then((parsed) => {
      setFileValidationStatus("valid");
      setFileValidationMessage(
        `Benchmark sample generated: ${parsed.pointCount} points (${parsed.durationSeconds}s @ 360 Hz). Ready to upload.`
      );
      setWaveformSamples(parsed.samples);
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="ECG Upload & 1D CNN Arrhythmia Analysis"
        subtitle="ECG recording upload, signal structure validation, waveform trace preview, and MIT-BIH 1D CNN classification pipeline."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleLoadSampleDataset}>
              <FileCode2 className="size-3.5 mr-1.5 text-signal" />
              Load MIT-BIH Sample CSV
            </Button>
            <Button variant="outline" size="sm" onClick={loadLists} disabled={loadingLists}>
              <RefreshCw className={`size-3.5 mr-1.5 ${loadingLists ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Safety Invariant Notice */}
      <Notice tone="signal" icon={<ShieldCheck />}>
        <div className="space-y-1">
          <p className="font-medium text-foreground">Medical AI Safety & Model Guardrails</p>
          <p className="text-muted-foreground">
            The 1D CNN arrhythmia classifier operates strictly on verified ECG signal files.
            The system strictly enforces an explicit <span className="font-mono text-signal">503 MODEL_NOT_CONNECTED</span> guard
            and will never generate synthetic diagnoses or simulated confidence scores.
            Arbitrary non-ECG files are verified and rejected prior to classification.
          </p>
        </div>
      </Notice>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column: Upload & Active File Details (5 cols) */}
        <div className="space-y-6 lg:col-span-5">
          {/* Upload Panel */}
          <Panel>
            <PanelHeader
              title="Upload ECG Recording"
              subtitle="Supported formats: .csv, .txt, .json, .dat, .edf (Max 10 MB)"
              icon={<Upload />}
            />

            <div className="space-y-4">
              {/* File Dropzone */}
              <div className="relative rounded-lg border-2 border-dashed border-border p-6 text-center transition-colors hover:border-signal/50 bg-surface/30">
                <input
                  type="file"
                  id="ecg-file-upload"
                  accept=".csv,.txt,.json,.dat,.edf"
                  onChange={handleFileChange}
                  className="absolute inset-0 size-full cursor-pointer opacity-0"
                />
                <div className="flex flex-col items-center">
                  <div className="rounded-full bg-surface p-3 text-signal mb-2">
                    <Waves className="size-6" />
                  </div>
                  <p className="text-sm font-medium text-foreground">
                    {selectedFile ? selectedFile.name : "Choose an ECG recording file"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Drag and drop or browse files on your device
                  </p>
                  {selectedFile && (
                    <span className="mt-2 text-[11px] font-mono text-muted-foreground">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </span>
                  )}
                </div>
              </div>

              {/* Validation Status Indicator */}
              {fileValidationStatus === "validating" && (
                <div className="flex items-center gap-2 rounded border border-border bg-surface p-2.5 text-xs text-muted-foreground">
                  <RefreshCw className="size-3.5 animate-spin text-signal" />
                  <span>Validating ECG signal structure...</span>
                </div>
              )}

              {fileValidationStatus === "valid" && (
                <div className="flex items-start gap-2 rounded border border-success/40 bg-success/10 p-2.5 text-xs text-success">
                  <FileCheck className="size-4 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">File Structure Validated</p>
                    <p className="text-[11px] text-muted-foreground mt-0.5">{fileValidationMessage}</p>
                  </div>
                </div>
              )}

              {fileValidationStatus === "invalid" && (
                <div className="flex items-start gap-2 rounded border border-warning/50 bg-warning/10 p-2.5 text-xs text-warning">
                  <AlertCircle className="size-4 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Validation Error</p>
                    <p className="text-[11px] text-muted-foreground mt-0.5">{fileValidationMessage}</p>
                  </div>
                </div>
              )}

              {uploadSuccessMessage && (
                <div className="flex items-center gap-2 rounded border border-success/40 bg-success/10 p-2.5 text-xs text-success">
                  <FileCheck className="size-4 shrink-0" />
                  <span>{uploadSuccessMessage}</span>
                </div>
              )}

              <Button
                type="button"
                onClick={handleUpload}
                disabled={!selectedFile || fileValidationStatus !== "valid" || isUploading}
                className="w-full bg-primary text-primary-foreground font-medium hover:bg-primary/90"
              >
                <Upload className="size-3.5 mr-1.5" />
                {isUploading ? "Uploading & Storing..." : "Upload Recording to Server"}
              </Button>
            </div>
          </Panel>

          {/* Active Recording Details Panel */}
          <Panel>
            <PanelHeader
              title="Active ECG Recording"
              subtitle="Metadata of the currently selected recording."
              icon={<FileText />}
              actions={
                activeRecording && (
                  <Tag tone={activeRecording.uploadStatus === "verified" ? "success" : "neutral"}>
                    {activeRecording.uploadStatus}
                  </Tag>
                )
              }
            />

            {activeRecording ? (
              <div className="space-y-4">
                <dl className="divide-y divide-border/60">
                  <KV k="Recording ID" v={`#${activeRecording.id}`} />
                  <KV k="Original Filename" v={activeRecording.originalFilename} />
                  <KV k="File Format" v={activeRecording.fileFormat.toUpperCase()} />
                  <KV k="File Size" v={`${(activeRecording.fileSizeBytes / 1024).toFixed(1)} KB`} />
                  <KV k="Sampling Rate" v={`${activeRecording.samplingFrequencyHz || 360} Hz`} />
                  <KV k="Upload Date" v={fmtDateTime(activeRecording.createdAt)} />
                </dl>

                {/* Analysis Button */}
                <div className="pt-2">
                  <Button
                    type="button"
                    onClick={handleRunAnalysis}
                    disabled={isAnalyzing}
                    className="w-full bg-primary text-primary-foreground font-medium hover:bg-primary/90"
                  >
                    <Play className={`size-3.5 mr-1.5 ${isAnalyzing ? "animate-spin" : ""}`} />
                    {isAnalyzing ? "Querying 1D CNN Inference Engine..." : "Run CNN Arrhythmia Analysis"}
                  </Button>
                </div>

                {/* Model / Analysis Status Feedback */}
                {modelStatus.code && (
                  <div
                    className={`rounded-md border p-3 text-xs leading-relaxed ${
                      modelStatus.isError
                        ? "border-warning/50 bg-warning/10 text-foreground"
                        : "border-success/40 bg-success/10 text-success"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {modelStatus.isError ? (
                        <ShieldAlert className="size-4 shrink-0 text-warning mt-0.5" />
                      ) : (
                        <ShieldCheck className="size-4 shrink-0 text-success mt-0.5" />
                      )}
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-medium">Status: {modelStatus.code}</span>
                        </div>
                        <p className="mt-1 text-muted-foreground">{modelStatus.message}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Classification Result Card (Only when returned by real model) */}
                {analysisResult && (analysisResult.predictedCategory || (analysisResult as unknown as { predictedClass?: string }).predictedClass) && (
                  <div className="rounded-md border border-signal/40 bg-surface p-3.5 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Predicted Rhythm:</span>
                      <Tag tone="signal">
                        {analysisResult.predictedCategory || (analysisResult as unknown as { predictedClass?: string }).predictedClass}
                      </Tag>
                    </div>
                    {(analysisResult.confidence !== null || (analysisResult as unknown as { confidenceScore?: number }).confidenceScore !== undefined) && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Confidence Score:</span>
                        <span className="font-mono text-sm text-foreground">
                          {(
                            (analysisResult.confidence ??
                              (analysisResult as unknown as { confidenceScore?: number }).confidenceScore ??
                              0) * 100
                          ).toFixed(1)}%
                        </span>
                      </div>
                    )}
                    {analysisResult.modelName && (
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Model Architecture:</span>
                        <span className="font-mono">{analysisResult.modelName}</span>
                      </div>
                    )}
                    {analysisResult.explanation && (
                      <div className="border-t border-border/60 pt-2 text-xs text-muted-foreground leading-relaxed">
                        {analysisResult.explanation}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <EmptyState
                title="No active recording selected"
                text="Upload an ECG file or pick a recording from the table below."
              />
            )}
          </Panel>
        </div>

        {/* Right Column: Waveform Chart & History (7 cols) */}
        <div className="space-y-6 lg:col-span-7">
          {/* Waveform Chart Panel */}
          <Panel>
            <PanelHeader
              title="ECG Signal Waveform Preview"
              subtitle={
                waveformSamples.length > 0
                  ? `Displaying ${waveformSamples.length} parsed points (Lead II amplitude in mV)`
                  : "Illustrative reference baseline until an ECG signal file is uploaded."
              }
              actions={
                <Tag tone={waveformSamples.length > 0 ? "signal" : "neutral"}>
                  {waveformSamples.length > 0 ? "Signal Parsed" : "Illustrative"}
                </Tag>
              }
              icon={<Waves />}
            />

            {loadingSamples ? (
              <div className="flex h-60 items-center justify-center">
                <RefreshCw className="size-6 animate-spin text-signal" />
              </div>
            ) : (
              <EcgChart data={waveformSamples.length > 0 ? waveformSamples : undefined} height={280} />
            )}

            <div className="mt-3 flex flex-wrap items-center justify-between text-[11px] text-muted-foreground border-t border-border/60 pt-2.5">
              <span>Calibration: 1 mV = 10 mm · Standard paper speed: 25 mm/s</span>
              <span className="font-mono">Time unit: Seconds · Amplitude: Millivolts (mV)</span>
            </div>
          </Panel>

          {/* Uploaded Recordings Repository */}
          <Panel>
            <PanelHeader
              title="Uploaded ECG Recordings"
              subtitle={`${recordings.length} recordings stored in server repository.`}
              icon={<FileText />}
            />

            {recordings.length === 0 ? (
              <EmptyState
                title="No recordings in repository"
                text="Upload an ECG dataset file (.csv, .txt, .json) or load the MIT-BIH sample."
              />
            ) : (
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="w-full min-w-[550px] text-left text-xs">
                  <thead className="bg-surface text-muted-foreground">
                    <tr>
                      <th className="px-3 py-2.5 font-medium font-mono">ID</th>
                      <th className="px-3 py-2.5 font-medium">Filename</th>
                      <th className="px-3 py-2.5 font-medium">Format</th>
                      <th className="px-3 py-2.5 font-medium font-mono">Upload Date</th>
                      <th className="px-3 py-2.5 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recordings.map((rec) => (
                      <tr
                        key={rec.id}
                        className={`border-t border-border/70 transition-colors hover:bg-surface/50 ${
                          activeRecording?.id === rec.id ? "bg-surface/70" : ""
                        }`}
                      >
                        <td className="px-3 py-2.5 font-mono text-muted-foreground">#{rec.id}</td>
                        <td className="px-3 py-2.5 font-medium text-foreground">
                          {rec.originalFilename}
                        </td>
                        <td className="px-3 py-2.5 font-mono text-muted-foreground uppercase">
                          {rec.fileFormat}
                        </td>
                        <td className="px-3 py-2.5 font-mono text-muted-foreground">
                          {fmtDateTime(rec.createdAt)}
                        </td>
                        <td className="px-3 py-2.5 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Button
                              variant={activeRecording?.id === rec.id ? "secondary" : "outline"}
                              size="sm"
                              onClick={() => selectRecording(rec)}
                              className="h-7 px-2 text-xs"
                            >
                              Select
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteRecording(rec.id)}
                              className="h-7 px-2 text-xs text-warning hover:text-warning"
                            >
                              <Trash2 className="size-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>

          {/* Prediction History Table */}
          <Panel>
            <PanelHeader
              title="ECG Analysis & Prediction History"
              subtitle="Verifiable inference records saved in SQLite database."
              icon={<Cpu />}
            />

            {predictionHistory.length === 0 ? (
              <EmptyState
                title="No completed predictions"
                text="Predictions will be recorded here when generated by a connected, trained 1D CNN model."
              />
            ) : (
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="w-full min-w-[500px] text-left text-xs">
                  <thead className="bg-surface text-muted-foreground">
                    <tr>
                      <th className="px-3 py-2.5 font-medium font-mono">Prediction ID</th>
                      <th className="px-3 py-2.5 font-medium">Recording</th>
                      <th className="px-3 py-2.5 font-medium">Predicted Rhythm</th>
                      <th className="px-3 py-2.5 font-medium">Confidence</th>
                      <th className="px-3 py-2.5 font-medium font-mono">Analysed At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictionHistory.map((h) => (
                      <tr key={h.id} className="border-t border-border/70 hover:bg-surface/50">
                        <td className="px-3 py-2.5 font-mono text-muted-foreground">#{h.id}</td>
                        <td className="px-3 py-2.5 font-mono">#{h.recordingId}</td>
                        <td className="px-3 py-2.5 font-medium text-foreground">
                          {h.predictedCategory || "Pending"}
                        </td>
                        <td className="px-3 py-2.5 font-mono">
                          {h.confidence !== null ? `${(h.confidence * 100).toFixed(1)}%` : "—"}
                        </td>
                        <td className="px-3 py-2.5 font-mono text-muted-foreground">
                          {h.analysedAt ? fmtDateTime(h.analysedAt) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
