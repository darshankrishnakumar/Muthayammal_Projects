import { useState } from "react";
import { BellOff, ChevronDown } from "lucide-react";
import type { HealthAlert } from "@/types/health";
import { EmptyState, Panel, PanelHeader, Tag } from "@/components/common";
import { Button } from "@/components/ui/button";
import { fmtDateTime } from "@/utils/format";
import { cn } from "@/lib/utils";

const tone = { info: "signal", review: "highlight", warning: "warning" } as const;

export function AlertsPanel({ alerts: initial }: { alerts: HealthAlert[] }) {
  const [alerts, setAlerts] = useState(initial);
  const [open, setOpen] = useState<string | null>(null);
  return (
    <Panel>
      <PanelHeader title="Health Alerts" subtitle="Interface notices · demonstration messages"
        actions={alerts.length > 0 && <Button variant="ghost" size="sm" onClick={() => setAlerts([])}>Dismiss all</Button>} />
      {alerts.length === 0 ? <EmptyState icon={<BellOff />} title="No alerts" text="Notices will appear here when data sources are connected." /> : (
        <ul className="space-y-2">
          {alerts.map((a) => (
            <li key={a.id} className="rounded-md border border-border bg-surface/60">
              <button className="flex w-full items-start gap-3 p-3 text-left" aria-expanded={open === a.id} onClick={() => setOpen(open === a.id ? null : a.id)}>
                <span className={cn("mt-1.5 size-1.5 shrink-0 rounded-full", a.priority === "warning" ? "bg-warning" : a.priority === "review" ? "bg-highlight" : "bg-signal")} />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2"><span className="text-xs font-medium">{a.category}</span><Tag tone={tone[a.priority]}>{a.priority}</Tag></div>
                  <p className="mt-1 text-xs text-muted-foreground">{a.description}</p>
                </div>
                <ChevronDown className={cn("mt-0.5 size-4 text-disabled transition-transform", open === a.id && "rotate-180")} />
              </button>
              {open === a.id && (
                <div className="border-t border-border/60 px-3 py-2.5 pl-7 text-xs text-muted-foreground">
                  <p>{a.detail}</p>
                  <p className="mt-1.5 font-mono text-[11px] text-disabled">{a.timestamp ? fmtDateTime(a.timestamp) : "Timestamp not available"}</p>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
