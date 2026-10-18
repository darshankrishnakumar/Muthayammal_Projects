import { Droplets, HeartPulse, Gauge, Thermometer } from "lucide-react";
import type { Measurement } from "@/types/health";
import { MetricCard } from "./MetricCard";

export function BiometricGrid({ history, latest }: { history: Measurement[]; latest?: Measurement }) {
  const m = latest ?? history[history.length - 1];
  if (!m) return null;
  const source = m.source === "manual" ? "manual" : "demo";
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard name="Heart Rate" value={m.heartRate} unit="BPM" timestamp={m.timestamp} icon={<HeartPulse />} history={history} sparkKey="heartRate" source={source}
        info="Beats per minute. Future source: MAX30102 optical sensor. Sample value shown." />
      <MetricCard name="Blood Pressure" value={<>{m.systolic}<span className="text-muted-foreground">/</span>{m.diastolic}</>} unit="mmHg · SYS/DIA" timestamp={m.timestamp} icon={<Gauge />} history={history} sparkKey="systolic" source={source}
        info="Systolic / diastolic pressure. Requires a dedicated cuff — not measured by the MAX30102." />
      <MetricCard name="Blood Oxygen" value={m.spo2} unit="SpO₂ %" timestamp={m.timestamp} icon={<Droplets />} history={history} sparkKey="spo2" source={source}
        info="Peripheral oxygen saturation (SpO₂). Future source: MAX30102. Sample value shown." />
      <MetricCard name="Body Temperature" value={m.temperature.toFixed(1)} unit="°C" timestamp={m.timestamp} icon={<Thermometer />} history={history} sparkKey="temperature" source={source}
        info="Body temperature in degrees Celsius. Sample value shown." />
    </div>
  );
}
