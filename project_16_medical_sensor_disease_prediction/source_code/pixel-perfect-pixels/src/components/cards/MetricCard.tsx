import type { ReactNode } from "react";
import type { Measurement } from "@/types/health";
import { DemoBadge, InfoTip, Tag } from "@/components/common";
import { Sparkline } from "@/components/charts/TrendChart";
import { fmtDateTime } from "@/utils/format";

export interface MetricCardProps {
  name: string;
  value: ReactNode;
  unit: string;
  timestamp: string;
  info: string;
  icon: ReactNode;
  history?: Measurement[];
  sparkKey?: keyof Measurement;
  source?: "demo" | "manual";
}

export function MetricCard({ name, value, unit, timestamp, info, icon, history, sparkKey, source = "demo" }: MetricCardProps) {
  return (
    <article className="panel flex flex-col p-4">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="text-disabled [&_svg]:size-3.5">{icon}</span>{name}<InfoTip text={info} />
        </div>
        {source === "manual" ? <Tag tone="signal">Manual</Tag> : <DemoBadge />}
      </div>
      <div className="mt-4 flex items-baseline gap-1.5">
        <span className="font-mono text-3xl font-medium tracking-tight">{value}</span>
        <span className="text-xs text-muted-foreground">{unit}</span>
      </div>
      {history && sparkKey && <div className="mt-3"><Sparkline data={history} dataKey={sparkKey} /></div>}
      <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-[11px] text-muted-foreground">
        <span className="font-mono">{fmtDateTime(timestamp)}</span>
        <span className="text-disabled">Status: not assessed</span>
      </div>
    </article>
  );
}
