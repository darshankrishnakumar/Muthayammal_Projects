import { useState, useMemo } from "react";
import { Link } from "@tanstack/react-router";
import { Search, Filter, Calendar, Trash2, ArrowRight, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { AssessmentRecord } from "@/services/api";

interface GaitHistoryTableProps {
  records: AssessmentRecord[];
  onDeleteRecord?: (id: string) => void;
  onSelectRecord?: (record: AssessmentRecord) => void;
}

export function GaitHistoryTable({
  records,
  onDeleteRecord,
  onSelectRecord,
}: GaitHistoryTableProps) {
  const [selectedChild, setSelectedChild] = useState<string>("ALL");
  const [dateRange, setDateRange] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Extract distinct child IDs for filter dropdown
  const uniqueChildren = useMemo(() => {
    const ids = Array.from(new Set(records.map((r) => r.childId).filter(Boolean)));
    return ids.sort();
  }, [records]);

  // Filtered records
  const filtered = useMemo(() => {
    return records.filter((r) => {
      // Child filter
      if (selectedChild !== "ALL" && r.childId !== selectedChild) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesChild = r.childId.toLowerCase().includes(q);
        const matchesPred = r.prediction.toLowerCase().includes(q);
        if (!matchesChild && !matchesPred) return false;
      }
      // Date range filter
      if (dateRange !== "ALL") {
        const itemDate = new Date(r.date).getTime();
        const now = Date.now();
        const days = Number(dateRange);
        if (!isNaN(days) && now - itemDate > days * 24 * 60 * 60 * 1000) {
          return false;
        }
      }
      return true;
    });
  }, [records, selectedChild, dateRange, searchQuery]);

  // Empty state if no records in total
  if (records.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card p-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <Activity className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-lg font-semibold text-foreground">
          No gait assessments available yet.
        </h3>
        <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
          Historical records will appear here after you conduct and save child gait assessments.
        </p>
        <div className="mt-6">
          <Button asChild size="default">
            <Link to="/predict">Start New Assessment</Link>
          </Button>
        </div>
      </div>
    );
  }

  const getBadgeClass = (pred: string) => {
    switch (pred.toLowerCase()) {
      case "normal":
        return "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300";
      case "diplegic":
        return "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300";
      case "hemiplegic":
        return "bg-rose-50 text-rose-900 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300";
      default:
        return "bg-muted text-foreground border-border";
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <div className="grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute top-2.5 left-3 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search Child ID or Prediction..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-input bg-card py-2 pr-3 pl-9 text-xs outline-none transition focus:border-ring focus:ring-1 focus:ring-ring"
          />
        </div>

        {/* Select Child */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 shrink-0 text-muted-foreground" />
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            className="w-full rounded-lg border border-input bg-card px-3 py-2 text-xs outline-none transition focus:border-ring focus:ring-1 focus:ring-ring"
          >
            <option value="ALL">Select Child: All Children</option>
            {uniqueChildren.map((cid) => (
              <option key={cid} value={cid}>
                Child: {cid}
              </option>
            ))}
          </select>
        </div>

        {/* Select Date Range */}
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 shrink-0 text-muted-foreground" />
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="w-full rounded-lg border border-input bg-card px-3 py-2 text-xs outline-none transition focus:border-ring focus:ring-1 focus:ring-ring"
          >
            <option value="ALL">Select Date Range: All Time</option>
            <option value="7">Past 7 Days</option>
            <option value="30">Past 30 Days</option>
            <option value="90">Past 3 Months</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      {filtered.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-8 text-center text-sm text-muted-foreground">
          No records match the selected filters.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-border bg-card shadow-xs">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-border bg-muted/40 font-medium text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Child ID</th>
                <th className="px-4 py-3">Age / Gender</th>
                <th className="px-4 py-3">Prediction</th>
                <th className="px-4 py-3">Walking Speed</th>
                <th className="px-4 py-3">Stride Length</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {filtered.map((record) => (
                <tr key={record.id} className="transition-colors hover:bg-muted/30">
                  <td className="px-4 py-3.5 font-medium whitespace-nowrap text-foreground">
                    {new Date(record.date).toLocaleDateString(undefined, {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </td>
                  <td className="px-4 py-3.5 font-semibold text-foreground">{record.childId}</td>
                  <td className="px-4 py-3.5 text-muted-foreground">
                    {record.age}y • {record.gender}
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${getBadgeClass(
                        record.prediction,
                      )}`}
                    >
                      {record.prediction}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-mono text-muted-foreground">
                    {record.walkingSpeed} m/s
                  </td>
                  <td className="px-4 py-3.5 font-mono text-muted-foreground">
                    {record.strideLength} cm
                  </td>
                  <td className="px-4 py-3.5 text-right whitespace-nowrap">
                    <div className="inline-flex items-center gap-1.5">
                      {onSelectRecord && (
                        <button
                          type="button"
                          onClick={() => onSelectRecord(record)}
                          className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                          title="View Details"
                        >
                          <ArrowRight className="h-4 w-4" />
                        </button>
                      )}
                      {onDeleteRecord && (
                        <button
                          type="button"
                          onClick={() => onDeleteRecord(record.id)}
                          className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                          title="Delete Assessment"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
