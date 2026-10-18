import { useState, useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { TrendingUp, BarChart2 } from "lucide-react";
import type { AssessmentRecord } from "@/services/api";

interface ProgressChartProps {
  records: AssessmentRecord[];
  selectedChildId?: string;
}

type MetricKey = "walkingSpeed" | "strideLength" | "stepDuration" | "tiltAngle";

const METRICS: { key: MetricKey; label: string; unit: string; color: string }[] = [
  { key: "walkingSpeed", label: "Walking Speed", unit: "m/s", color: "#0284c7" },
  { key: "strideLength", label: "Stride Length", unit: "cm", color: "#0d9488" },
  { key: "stepDuration", label: "Step Duration", unit: "s", color: "#8b5cf6" },
  { key: "tiltAngle", label: "Tilt Angle", unit: "°", color: "#ea580c" },
];

export function ProgressChart({ records, selectedChildId }: ProgressChartProps) {
  const [activeMetric, setActiveMetric] = useState<MetricKey>("walkingSpeed");

  // Filter records by child if specified or take all if only 1 child
  const relevantRecords = useMemo(() => {
    let list = records;
    if (selectedChildId && selectedChildId !== "ALL") {
      list = records.filter((r) => r.childId === selectedChildId);
    }
    // Sort chronologically ascending
    return [...list].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [records, selectedChildId]);

  const currentMetricConfig = METRICS.find((m) => m.key === activeMetric)!;

  // Format data for Recharts
  const chartData = useMemo(() => {
    return relevantRecords.map((r) => ({
      date: new Date(r.date).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      }),
      value: r[activeMetric],
      prediction: r.prediction,
      childId: r.childId,
    }));
  }, [relevantRecords, activeMetric]);

  // Requirement: If data is unavailable (< 2 points), show exact prompt empty state
  if (relevantRecords.length < 2) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <TrendingUp className="h-5 w-5" />
        </div>
        <h3 className="mt-4 text-base font-semibold text-foreground">Gait Progress Over Time</h3>
        <p className="mx-auto mt-2 max-w-md text-xs text-muted-foreground">
          Progress data will appear after multiple gait assessments.
        </p>
        <p className="mt-1 text-[11px] text-muted-foreground/75">
          {relevantRecords.length === 1
            ? "1 assessment recorded so far. At least 2 assessments are required to calculate trend trajectories."
            : "No longitudinal assessments recorded yet."}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-5 sm:p-6 shadow-xs">
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <BarChart2 className="h-4 w-4 text-medical-foreground" />
            <h3 className="font-semibold text-foreground text-base">Gait Progress Over Time</h3>
          </div>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Longitudinal biomechanical trajectories across chronological assessments.
          </p>
        </div>

        {/* Metric Selector Tabs */}
        <div className="flex flex-wrap gap-1.5 rounded-lg border border-border bg-muted/40 p-1">
          {METRICS.map((m) => (
            <button
              key={m.key}
              type="button"
              onClick={() => setActiveMetric(m.key)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                activeMetric === m.key
                  ? "bg-card text-foreground shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart container */}
      <div className="mt-6 h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "var(--border)" }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "var(--border)" }}
              unit={` ${currentMetricConfig.unit}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length > 0 && payload[0]?.payload) {
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-border bg-card p-3 shadow-md text-xs">
                      <p className="font-semibold text-foreground">{data.date}</p>
                      <p className="text-muted-foreground">Child ID: {data.childId}</p>
                      <p
                        className="mt-1 font-mono font-bold"
                        style={{ color: currentMetricConfig.color }}
                      >
                        {currentMetricConfig.label}: {data.value} {currentMetricConfig.unit}
                      </p>
                      <p className="mt-1 text-[11px] text-muted-foreground">
                        Pattern:{" "}
                        <span className="font-medium text-foreground">{data.prediction}</span>
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={currentMetricConfig.color}
              strokeWidth={2.5}
              dot={{ r: 4, strokeWidth: 2, fill: "var(--card)" }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-border/50 pt-3 text-[11px] text-muted-foreground">
        <span>Plotting {chartData.length} sequential sessions</span>
        <span>Unit: {currentMetricConfig.unit}</span>
      </div>
    </div>
  );
}
