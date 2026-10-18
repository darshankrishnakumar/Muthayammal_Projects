import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { PageHeader, Panel, PanelHeader, Tag, Notice, EmptyState } from "@/components/common";
import { apiRequest, endpoints } from "@/services/apiClient";
import {
  FileText,
  Printer,
  RefreshCw,
  Activity,
  BrainCircuit,
  FileCheck2,
  AlertTriangle,
  Download,
  Calendar,
  Layers,
  Heart,
} from "lucide-react";

interface ReportSummaryData {
  generatedAt: string;
  dateRange: {
    startDate: string | null;
    endDate: string | null;
  };
  summary: {
    totalMeasurements: number;
    measurementsByType: Record<string, number>;
    dataQualityBreakdown: Record<string, number>;
    totalEcgRecordings: number;
    ecgByFormat: Record<string, number>;
    totalPredictions: number;
    predictionsByStatus: Record<string, number>;
    totalRecommendations: number;
    activeAlerts: number;
  };
  systemNotes: {
    cnnModelStatus: string;
    reportType: string;
    clinicalNotice: string;
  };
}

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Reports — BioPulse" },
      { name: "description", content: "Clinical summary report and audit logs." },
      { property: "og:title", content: "Reports — BioPulse" },
      { property: "og:description", content: "Clinical summary report and audit logs." },
    ],
  }),
  component: ReportsPage,
});

export function ReportsPage() {
  const [reportData, setReportData] = useState<ReportSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<ReportSummaryData>(endpoints.reportsSummary);
      setReportData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handlePrint = () => {
    window.print();
  };

  const handleExportJson = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `biopulse-report-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="print:hidden">
        <PageHeader
          title="Clinical Summary Reports"
          subtitle="Aggregated biometric audit logs, ECG recording statistics, and CNN prediction metrics."
          actions={
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={fetchReport}
                disabled={loading}
                className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised disabled:opacity-50"
              >
                <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </button>
              <button
                type="button"
                onClick={handleExportJson}
                disabled={!reportData}
                className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised disabled:opacity-50"
              >
                <Download className="size-3.5" />
                Export JSON
              </button>
              <button
                type="button"
                onClick={handlePrint}
                disabled={!reportData}
                className="inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                <Printer className="size-3.5" />
                Print / Save PDF
              </button>
            </div>
          }
        />
      </div>

      {error && (
        <Notice tone="warning" icon={<AlertTriangle />}>
          {error}
        </Notice>
      )}

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <RefreshCw className="size-8 animate-spin text-signal" />
        </div>
      ) : !reportData ? (
        <EmptyState
          title="No Report Available"
          text="Click refresh or ensure the backend service is reachable."
          icon={<FileText className="size-8 text-signal" />}
        />
      ) : (
        <div className="space-y-6 font-sans">
          {/* Printable Report Header */}
          <Panel className="border-border/80 bg-surface p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border/60 pb-5">
              <div>
                <div className="flex items-center gap-2">
                  <div className="flex size-7 items-center justify-center rounded-md bg-signal/10 text-signal">
                    <Heart className="size-4" />
                  </div>
                  <h2 className="text-lg font-bold tracking-tight text-foreground">BioPulse Clinical System Audit Report</h2>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{reportData.systemNotes.reportType}</p>
              </div>

              <div className="text-right font-mono text-xs">
                <p className="text-muted-foreground">
                  Generated: <span className="text-foreground">{new Date(reportData.generatedAt).toLocaleString()}</span>
                </p>
                <div className="mt-1 flex items-center justify-end gap-2">
                  <span className="text-muted-foreground">Model Status:</span>
                  <Tag tone={reportData.systemNotes.cnnModelStatus === "connected" ? "success" : "signal"} dot>
                    {reportData.systemNotes.cnnModelStatus}
                  </Tag>
                </div>
              </div>
            </div>

            {/* Quick KPI Grid */}
            <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-md border border-border/60 bg-surface-raised/40 p-3">
                <span className="text-[11px] font-medium text-muted-foreground">Total Measurements</span>
                <p className="mt-1 text-2xl font-bold font-mono text-foreground">{reportData.summary.totalMeasurements}</p>
                <span className="text-[10px] text-muted-foreground">Across all vital types</span>
              </div>

              <div className="rounded-md border border-border/60 bg-surface-raised/40 p-3">
                <span className="text-[11px] font-medium text-muted-foreground">ECG Recordings</span>
                <p className="mt-1 text-2xl font-bold font-mono text-foreground">{reportData.summary.totalEcgRecordings}</p>
                <span className="text-[10px] text-muted-foreground">Validated waveforms</span>
              </div>

              <div className="rounded-md border border-border/60 bg-surface-raised/40 p-3">
                <span className="text-[11px] font-medium text-muted-foreground">CNN Predictions</span>
                <p className="mt-1 text-2xl font-bold font-mono text-signal">{reportData.summary.totalPredictions}</p>
                <span className="text-[10px] text-muted-foreground">AAMI 5-class inferences</span>
              </div>

              <div className="rounded-md border border-border/60 bg-surface-raised/40 p-3">
                <span className="text-[11px] font-medium text-muted-foreground">Active Threshold Alerts</span>
                <p className="mt-1 text-2xl font-bold font-mono text-warning">{reportData.summary.activeAlerts}</p>
                <span className="text-[10px] text-muted-foreground">Requiring review</span>
              </div>
            </div>

            {/* Section 1: Vital Measurements Breakdown */}
            <div className="mt-6">
              <h3 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <Activity className="size-3.5 text-signal" />
                Biometric Measurement Inventory
              </h3>
              <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="rounded-md border border-border/60 p-4">
                  <h4 className="text-xs font-medium text-foreground">Recordings by Vital Parameter</h4>
                  <div className="mt-3 space-y-2 font-mono text-xs">
                    {Object.entries(reportData.summary.measurementsByType).length > 0 ? (
                      Object.entries(reportData.summary.measurementsByType).map(([type, count]) => (
                        <div key={type} className="flex items-center justify-between border-b border-border/30 pb-1.5 last:border-0">
                          <span className="capitalize text-muted-foreground">{type.replace("_", " ")}</span>
                          <span className="font-semibold text-foreground">{count}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-muted-foreground">No measurements recorded yet.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-md border border-border/60 p-4">
                  <h4 className="text-xs font-medium text-foreground">Data Quality Classification</h4>
                  <div className="mt-3 space-y-2 font-mono text-xs">
                    {Object.entries(reportData.summary.dataQualityBreakdown).length > 0 ? (
                      Object.entries(reportData.summary.dataQualityBreakdown).map(([status, count]) => (
                        <div key={status} className="flex items-center justify-between border-b border-border/30 pb-1.5 last:border-0">
                          <span className="capitalize text-muted-foreground">{status}</span>
                          <span className="font-semibold text-success">{count}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-muted-foreground">No quality metrics available.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Section 2: ECG & CNN Analysis Audit */}
            <div className="mt-6 border-t border-border/60 pt-5">
              <h3 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <BrainCircuit className="size-3.5 text-signal" />
                ECG Signal Files & CNN Arrhythmia Inferences
              </h3>
              <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="rounded-md border border-border/60 p-4">
                  <h4 className="text-xs font-medium text-foreground">ECG File Formats</h4>
                  <div className="mt-3 space-y-2 font-mono text-xs">
                    {Object.entries(reportData.summary.ecgByFormat).length > 0 ? (
                      Object.entries(reportData.summary.ecgByFormat).map(([fmt, count]) => (
                        <div key={fmt} className="flex items-center justify-between border-b border-border/30 pb-1.5 last:border-0">
                          <span className="uppercase text-muted-foreground">{fmt}</span>
                          <span className="font-semibold text-foreground">{count}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-muted-foreground">No ECG files uploaded yet.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-md border border-border/60 p-4">
                  <h4 className="text-xs font-medium text-foreground">Prediction Status Summary</h4>
                  <div className="mt-3 space-y-2 font-mono text-xs">
                    {Object.entries(reportData.summary.predictionsByStatus).length > 0 ? (
                      Object.entries(reportData.summary.predictionsByStatus).map(([st, count]) => (
                        <div key={st} className="flex items-center justify-between border-b border-border/30 pb-1.5 last:border-0">
                          <span className="capitalize text-muted-foreground">{st}</span>
                          <span className="font-semibold text-signal">{count}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-muted-foreground">No inferences recorded.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Section 3: Compliance & Architecture Statement */}
            <div className="mt-6 rounded-md border border-border/60 bg-surface-raised/30 p-4 text-xs">
              <h4 className="font-semibold text-foreground">System Specifications & Architecture Integrity</h4>
              <p className="mt-1 leading-relaxed text-muted-foreground">
                {reportData.systemNotes.clinicalNotice}
              </p>
              <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] md:grid-cols-4 font-mono">
                <div>
                  <span className="text-muted-foreground">Model Engine:</span>
                  <p className="font-medium text-foreground">Residual 1D CNN</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Dataset Source:</span>
                  <p className="font-medium text-foreground">MIT-BIH Arrhythmia</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Storage Engine:</span>
                  <p className="font-medium text-foreground">SQLite (WAL Mode)</p>
                </div>
                <div>
                  <span className="text-muted-foreground">IoT Dependency:</span>
                  <p className="font-medium text-success">None (Manual Entry)</p>
                </div>
              </div>
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
}
