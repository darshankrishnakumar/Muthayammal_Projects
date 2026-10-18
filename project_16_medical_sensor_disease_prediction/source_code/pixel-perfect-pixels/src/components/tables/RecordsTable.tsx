import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Eye, Search, SearchX } from "lucide-react";
import type { HistoryRecord } from "@/types/health";
import { DemoBadge, EmptyState, KV, Tag } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { fmtDateTime } from "@/utils/format";

const statusTone = (s: string) => (s === "Validation failed" ? "warning" : s === "Recorded" ? "success" : s === "Pending integration" ? "signal" : "neutral") as "warning" | "success" | "signal" | "neutral";

export function RecordsTable({ records, pageSize = 6, showTypeFilter = false }: { records: HistoryRecord[]; pageSize?: number; showTypeFilter?: boolean }) {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");
  const [type, setType] = useState("all");
  const [from, setFrom] = useState("");
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<HistoryRecord | null>(null);

  const filtered = useMemo(() => records.filter((r) =>
    (!q || `${r.id} ${r.type} ${r.result}`.toLowerCase().includes(q.toLowerCase())) &&
    (status === "all" || r.status === status) &&
    (type === "all" || r.type === type) &&
    (!from || r.date.slice(0, 10) >= from)), [records, q, status, type, from]);
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const p = Math.min(page, pages - 1);
  const rows = filtered.slice(p * pageSize, p * pageSize + pageSize);
  const reset = (fn: () => void) => { fn(); setPage(0); };

  return (
    <div>
      <div className="mb-3 grid gap-2 sm:grid-cols-2 lg:flex lg:flex-wrap">
        <div className="relative lg:w-64"><Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-disabled" />
          <input aria-label="Search records" className="field pl-8" placeholder="Search ID, type, result" value={q} onChange={(e) => reset(() => setQ(e.target.value))} /></div>
        <input aria-label="From date" type="date" className="field lg:w-44" value={from} onChange={(e) => reset(() => setFrom(e.target.value))} />
        <select aria-label="Status filter" className="field lg:w-48" value={status} onChange={(e) => reset(() => setStatus(e.target.value))}>
          <option value="all">All statuses</option>{["Recorded", "Not analysed", "Pending integration", "Validation failed"].map((s) => <option key={s}>{s}</option>)}
        </select>
        {showTypeFilter && <select aria-label="Record type" className="field lg:w-44" value={type} onChange={(e) => reset(() => setType(e.target.value))}>
          <option value="all">All record types</option>{["Measurement", "ECG recording", "Analysis", "Recommendation"].map((s) => <option key={s}>{s}</option>)}
        </select>}
      </div>
      {rows.length === 0 ? <EmptyState icon={<SearchX />} title="No records match these filters" text="Clear the search or widen the date range." /> : (
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="w-full min-w-[640px] text-left text-xs">
            <thead className="bg-surface text-muted-foreground"><tr>{["Record ID", "Recording date", "Data type", "Analysis status", "Result category", ""].map((h) => <th key={h} className="label-caps px-3 py-2.5 font-medium">{h}</th>)}</tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t border-border/70 transition-colors hover:bg-surface/50">
                  <td className="px-3 py-2.5 font-mono">{r.id}</td>
                  <td className="px-3 py-2.5 font-mono text-muted-foreground">{fmtDateTime(r.date)}</td>
                  <td className="px-3 py-2.5">{r.type}</td>
                  <td className="px-3 py-2.5"><Tag tone={statusTone(r.status)} dot>{r.status}</Tag></td>
                  <td className="px-3 py-2.5 text-muted-foreground">{r.result}</td>
                  <td className="px-3 py-2.5 text-right"><Button variant="ghost" size="sm" onClick={() => setSelected(r)}><Eye />View</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
        <span>{filtered.length} demonstration records</span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" className="size-7" aria-label="Previous page" disabled={p === 0} onClick={() => setPage(p - 1)}><ChevronLeft /></Button>
          <span className="font-mono">{p + 1} / {pages}</span>
          <Button variant="outline" size="icon" className="size-7" aria-label="Next page" disabled={p >= pages - 1} onClick={() => setPage(p + 1)}><ChevronRight /></Button>
        </div>
      </div>
      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="border-border bg-popover">
          {selected && <>
            <SheetHeader><SheetTitle className="font-mono">{selected.id}</SheetTitle><SheetDescription>Record details</SheetDescription></SheetHeader>
            <div className="px-4"><div className="mb-4"><DemoBadge label="Demonstration record" /></div>
              <dl><KV k="Date" v={fmtDateTime(selected.date)} /><KV k="Type" v={selected.type} /><KV k="Status" v={selected.status} /><KV k="Result" v={selected.result} /><KV k="Storage" v="Not persisted" /></dl>
              <p className="mt-4 text-xs text-muted-foreground">{selected.notes}</p></div>
          </>}
        </SheetContent>
      </Sheet>
    </div>
  );
}
