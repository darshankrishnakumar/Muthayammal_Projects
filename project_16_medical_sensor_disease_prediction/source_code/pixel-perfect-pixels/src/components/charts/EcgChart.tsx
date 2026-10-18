import { useMemo } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { buildIllustrativeEcg } from "@/data/demoECG";

const axis = { stroke: "var(--color-border)", tick: { fill: "var(--color-muted-foreground)", fontSize: 10, fontFamily: "var(--font-mono)" } };

export function EcgChart({ seconds = 5, height = 240, data: external }: { seconds?: number; height?: number; data?: { t: number; mv: number }[] }) {
  const data = useMemo(() => external ?? buildIllustrativeEcg(seconds), [seconds, external]);
  const max = data.at(-1)?.t ?? seconds;
  return (
    <div className="signal-grid rounded-md border border-border p-2" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 4, left: -12 }}>
          <CartesianGrid stroke="var(--color-grid)" strokeDasharray="0" />
          <XAxis dataKey="t" type="number" domain={[0, max]} tickCount={Math.min(11, Math.ceil(max) + 1)} {...axis} tickFormatter={(v) => `${v}s`} />
          <YAxis domain={[-0.5, 1.3]} ticks={[-0.5, 0, 0.5, 1]} {...axis} tickFormatter={(v) => `${v}`} label={{ value: "mV", angle: -90, position: "insideLeft", offset: 20, fill: "var(--color-muted-foreground)", fontSize: 10 }} />
          <Tooltip contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 11 }} labelFormatter={(v) => `t = ${v}s`} formatter={(v: number) => [`${v} mV`, "Amplitude"]} />
          <Line type="monotone" dataKey="mv" stroke="var(--color-signal)" strokeWidth={1.25} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
