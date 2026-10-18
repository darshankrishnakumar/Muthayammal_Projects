import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Measurement, MetricKey } from "@/types/health";
import { fmtShort } from "@/utils/format";
import { EmptyState } from "@/components/common";

export const metricMeta: Record<MetricKey, { label: string; unit: string; lines: { key: keyof Measurement; name: string; color: string }[]; domain: [number, number] }> = {
  heartRate: { label: "Heart rate", unit: "BPM", lines: [{ key: "heartRate", name: "Heart rate", color: "var(--color-signal)" }], domain: [50, 100] },
  bloodPressure: { label: "Blood pressure", unit: "mmHg", lines: [{ key: "systolic", name: "Systolic", color: "var(--color-signal)" }, { key: "diastolic", name: "Diastolic", color: "var(--color-highlight)" }], domain: [60, 140] },
  spo2: { label: "SpO₂", unit: "%", lines: [{ key: "spo2", name: "SpO₂", color: "var(--color-signal)" }], domain: [90, 100] },
  temperature: { label: "Temperature", unit: "°C", lines: [{ key: "temperature", name: "Temperature", color: "var(--color-signal)" }], domain: [35.5, 38] },
};

const axis = { stroke: "var(--color-border)", tick: { fill: "var(--color-muted-foreground)", fontSize: 10, fontFamily: "var(--font-mono)" } };

export function TrendChart({ data, metric, height = 260 }: { data: Measurement[]; metric: MetricKey; height?: number }) {
  const meta = metricMeta[metric];
  if (!data.length) return <EmptyState title="No measurements in range" text="Adjust the time range or add a manual demonstration entry." />;
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
          <CartesianGrid stroke="var(--color-grid)" vertical={false} />
          <XAxis dataKey="timestamp" tickFormatter={fmtShort} {...axis} minTickGap={24} />
          <YAxis domain={meta.domain} {...axis} label={{ value: meta.unit, angle: -90, position: "insideLeft", offset: 16, fill: "var(--color-muted-foreground)", fontSize: 10 }} />
          <Tooltip contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 11 }} labelFormatter={(v) => fmtShort(String(v))} formatter={(v: number, n: string) => [`${v} ${meta.unit}`, n]} />
          {meta.lines.length > 1 && <Legend iconType="plainline" wrapperStyle={{ fontSize: 11, color: "var(--color-muted-foreground)" }} />}
          {meta.lines.map((l) => <Line key={String(l.key)} type="monotone" dataKey={l.key} name={l.name} stroke={l.color} strokeWidth={1.5} dot={false} animationDuration={400} />)}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function Sparkline({ data, dataKey }: { data: Measurement[]; dataKey: keyof Measurement }) {
  return (
    <div className="h-10 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}><YAxis hide domain={["dataMin - 2", "dataMax + 2"]} /><Line dataKey={dataKey} stroke="var(--color-signal)" strokeOpacity={0.8} strokeWidth={1.25} dot={false} isAnimationActive={false} /></LineChart>
      </ResponsiveContainer>
    </div>
  );
}
