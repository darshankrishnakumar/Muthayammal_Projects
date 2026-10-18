import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect, useMemo } from "react";
import { PageHeader, Panel, PanelHeader, Tag, EmptyState, Notice } from "@/components/common";
import { getMeasurements, type MeasurementRecord } from "@/services/sensorService";
import { getPredictionHistory, getEcgRecordings, type StoredEcgRecording } from "@/services/predictionService";
import type { PredictionResult } from "@/types/prediction";
import {
  History,
  Activity,
  BrainCircuit,
  FileText,
  RefreshCw,
  Search,
  Filter,
  Download,
  Calendar,
  Clock,
  ArrowUpRight,
} from "lucide-react";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Health History — BioPulse" },
      { name: "description", content: "Chronological timeline of manual vitals, ECG uploads, and CNN inferences." },
      { property: "og:title", content: "Health History — BioPulse" },
      { property: "og:description", content: "Chronological timeline of manual vitals, ECG uploads, and CNN inferences." },
    ],
  }),
  component: HealthHistoryPage,
});

type EventCategory = "vital" | "ecg" | "prediction";

interface TimelineItem {
  id: string;
  category: EventCategory;
  timestamp: string;
  title: string;
  details: string;
  secondaryInfo?: string;
  source: string;
  badgeTone: "success" | "warning" | "signal" | "highlight" | "neutral";
  badgeText: string;
}

export function HealthHistoryPage() {
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<"all" | EventCategory>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [measurementsRes, ecgRes, predictionsRes] = await Promise.all([
        getMeasurements({ limit: 100 }).catch(() => ({ records: [] })),
        getEcgRecordings({ limit: 50 }).catch(() => ({ recordings: [] })),
        getPredictionHistory().catch(() => []),
      ]);

      const items: TimelineItem[] = [];

      // Process Measurements
      (measurementsRes.records || []).forEach((m: MeasurementRecord) => {
        let valueStr = "";
        let title = "";
        if (m.measurementType === "blood_pressure") {
          title = "Blood Pressure Reading";
          valueStr = `${m.systolic}/${m.diastolic} ${m.unit}`;
        } else if (m.measurementType === "heart_rate") {
          title = "Heart Rate Reading";
          valueStr = `${m.value} ${m.unit}`;
        } else if (m.measurementType === "spo2") {
          title = "Oxygen Saturation (SpO2)";
          valueStr = `${m.value}${m.unit}`;
        } else {
          title = "Body Temperature";
          valueStr = `${m.value} ${m.unit}`;
        }

        items.push({
          id: `meas-${m.id}`,
          category: "vital",
          timestamp: m.measuredAt || m.createdAt,
          title,
          details: valueStr,
          secondaryInfo: `Data Quality: ${m.dataQualityStatus}`,
          source: m.source === "manual" ? "Manual Entry" : m.source,
          badgeTone: "signal",
          badgeText: m.measurementType.replace("_", " "),
        });
      });

      // Process ECG Uploads
      (ecgRes.recordings || []).forEach((e: StoredEcgRecording) => {
        items.push({
          id: `ecg-${e.id}`,
          category: "ecg",
          timestamp: e.createdAt,
          title: "ECG File Upload",
          details: e.originalFilename,
          secondaryInfo: `${e.fileFormat.toUpperCase()} • ${(e.fileSizeBytes / 1024).toFixed(1)} KB`,
          source: "Dataset Upload",
          badgeTone: "highlight",
          badgeText: `ECG #${e.id}`,
        });
      });

      // Process CNN Predictions
      (predictionsRes || []).forEach((p: PredictionResult) => {
        const confText = p.confidence !== null ? `${(p.confidence * 100).toFixed(1)}% confidence` : "pending";
        const cat = p.predictedCategory || "Pending Analysis";
        const isNormal = cat.toLowerCase().includes("normal");

        items.push({
          id: `pred-${p.id}`,
          category: "prediction",
          timestamp: p.analysedAt || new Date().toISOString(),
          title: "1D CNN Arrhythmia Inference",
          details: cat,
          secondaryInfo: `${confText} • Model: ${p.modelName || "Residual CNN"}`,
          source: `ECG #${p.recordingId}`,
          badgeTone: isNormal ? "success" : "warning",
          badgeText: cat,
        });
      });

      // Sort chronological descending (newest first)
      items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

      setTimeline(items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load history items");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredItems = useMemo(() => {
    return timeline.filter((item) => {
      const matchCat = selectedFilter === "all" || item.category === selectedFilter;
      const matchSearch =
        !searchQuery ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.details.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.badgeText.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [timeline, selectedFilter, searchQuery]);

  const handleExportCsv = () => {
    if (timeline.length === 0) return;
    const headers = ["ID", "Category", "Timestamp", "Title", "Details", "SecondaryInfo", "Source"];
    const rows = filteredItems.map((i) =>
      [
        `"${i.id}"`,
        `"${i.category}"`,
        `"${i.timestamp}"`,
        `"${i.title}"`,
        `"${i.details}"`,
        `"${i.secondaryInfo || ""}"`,
        `"${i.source}"`,
      ].join(",")
    );
    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `biopulse-history-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Health History"
        subtitle="Chronological audit stream of manual vital entries, ECG recordings, and CNN predictions."
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
            <button
              type="button"
              onClick={handleExportCsv}
              disabled={filteredItems.length === 0}
              className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised disabled:opacity-50"
            >
              <Download className="size-3.5" />
              Export CSV
            </button>
            <Link
              to="/monitoring"
              className="inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90"
            >
              <Activity className="size-3.5" />
              New Entry
            </Link>
          </div>
        }
      />

      {/* Filter and Search Bar */}
      <Panel className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-1.5">
            <Filter className="mr-1 size-3.5 text-muted-foreground" />
            {[
              { id: "all", label: "All Events" },
              { id: "vital", label: "Manual Vitals" },
              { id: "ecg", label: "ECG Uploads" },
              { id: "prediction", label: "CNN Predictions" },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setSelectedFilter(tab.id as "all" | EventCategory)}
                className={`rounded-md px-2.5 py-1 text-xs transition-colors ${
                  selectedFilter === tab.id
                    ? "bg-surface-raised font-medium text-signal border border-border"
                    : "text-muted-foreground hover:bg-surface hover:text-foreground"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 size-3 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-56 rounded-md border border-border bg-input pl-7 pr-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:border-signal focus:outline-none"
            />
          </div>
        </div>
      </Panel>

      {error && (
        <Notice tone="warning">
          {error}
        </Notice>
      )}

      {/* Timeline Stream */}
      <Panel>
        <PanelHeader
          title={`Audit Records (${filteredItems.length})`}
          subtitle="All records stored in local SQLite database without cloud dependencies."
        />

        {loading ? (
          <div className="flex h-48 items-center justify-center">
            <RefreshCw className="size-6 animate-spin text-signal" />
          </div>
        ) : filteredItems.length === 0 ? (
          <EmptyState
            title="No activity records found"
            text="Add manual health measurements or upload an ECG file to populate your timeline."
            icon={<History className="size-6 text-signal" />}
          />
        ) : (
          <div className="relative pl-6 before:absolute before:bottom-0 before:left-2 before:top-2 before:w-0.5 before:bg-border/60">
            <div className="space-y-6">
              {filteredItems.map((item) => {
                const dateObj = new Date(item.timestamp);
                const isValidDate = !isNaN(dateObj.getTime());
                const formattedDate = isValidDate ? dateObj.toLocaleDateString() : item.timestamp;
                const formattedTime = isValidDate ? dateObj.toLocaleTimeString() : "";

                return (
                  <div key={item.id} className="relative group">
                    {/* Circle icon on the timeline line */}
                    <div className="absolute -left-6 top-1 flex size-4.5 items-center justify-center rounded-full border border-border bg-surface text-signal group-hover:border-signal transition-colors">
                      {item.category === "vital" ? (
                        <Activity className="size-2.5" />
                      ) : item.category === "ecg" ? (
                        <FileText className="size-2.5" />
                      ) : (
                        <BrainCircuit className="size-2.5" />
                      )}
                    </div>

                    <div className="rounded-md border border-border/60 bg-surface-raised/30 p-4 transition-colors hover:border-border hover:bg-surface-raised/50">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs font-semibold text-foreground">{item.title}</h4>
                          <Tag tone={item.badgeTone} dot>
                            {item.badgeText}
                          </Tag>
                        </div>

                        <div className="flex items-center gap-1.5 font-mono text-[11px] text-muted-foreground">
                          <Clock className="size-3" />
                          <span>{formattedDate} {formattedTime}</span>
                        </div>
                      </div>

                      <div className="mt-2 flex flex-wrap items-baseline justify-between gap-2">
                        <div>
                          <p className="font-mono text-sm font-semibold text-foreground">{item.details}</p>
                          {item.secondaryInfo && (
                            <p className="mt-0.5 text-xs text-muted-foreground">{item.secondaryInfo}</p>
                          )}
                        </div>

                        <div className="flex items-center gap-3">
                          <span className="font-mono text-[10px] uppercase text-muted-foreground">
                            Source: {item.source}
                          </span>
                          {item.category === "ecg" && (
                            <Link to="/ecg" className="text-xs text-signal hover:underline inline-flex items-center gap-0.5">
                              View <ArrowUpRight className="size-3" />
                            </Link>
                          )}
                          {item.category === "prediction" && (
                            <Link to="/predictions" className="text-xs text-signal hover:underline inline-flex items-center gap-0.5">
                              Details <ArrowUpRight className="size-3" />
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </Panel>
    </div>
  );
}
