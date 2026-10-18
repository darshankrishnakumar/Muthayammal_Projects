import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect, useMemo } from "react";
import { PageHeader, Panel, PanelHeader, Tag, EmptyState, Notice } from "@/components/common";
import { apiRequest, endpoints } from "@/services/apiClient";
import {
  HeartPulse,
  Sparkles,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  ShieldAlert,
  ArrowRight,
  Filter,
} from "lucide-react";

interface RecommendationItem {
  id: string;
  numericId: number;
  category: string;
  kind: string;
  title: string;
  explanation: string;
  nextStep: string;
  related: string;
  reviewStatus: string;
  clinicalNotice: string;
}

export const Route = createFileRoute("/recommendations")({
  head: () => ({
    meta: [
      { title: "Recommendations — BioPulse" },
      { name: "description", content: "Clinical and wellness recommendations and protocol advisories." },
      { property: "og:title", content: "Recommendations — BioPulse" },
      { property: "og:description", content: "Clinical and wellness recommendations and protocol advisories." },
    ],
  }),
  component: RecommendationsPage,
});

function getCategoryTone(category: string): "success" | "warning" | "signal" | "highlight" | "neutral" {
  const cat = category.toLowerCase();
  if (cat.includes("wellness")) return "success";
  if (cat.includes("assessment") || cat.includes("professional") || cat.includes("clinical")) return "warning";
  if (cat.includes("repeat")) return "signal";
  if (cat.includes("quality")) return "highlight";
  return "neutral";
}

function getCategoryIcon(category: string) {
  const cat = category.toLowerCase();
  if (cat.includes("wellness")) return <Sparkles className="size-4 text-success" />;
  if (cat.includes("assessment") || cat.includes("professional") || cat.includes("clinical"))
    return <ShieldAlert className="size-4 text-warning" />;
  if (cat.includes("repeat")) return <RefreshCw className="size-4 text-signal" />;
  return <HelpCircle className="size-4 text-highlight" />;
}

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<RecommendationItem[]>(endpoints.recommendations);
      setRecommendations(data || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const categories = useMemo(() => {
    const cats = Array.from(new Set(recommendations.map((r) => r.category)));
    return ["all", ...cats];
  }, [recommendations]);

  const filtered = useMemo(() => {
    return recommendations.filter((r) => {
      const matchCat = selectedCategory === "all" || r.category === selectedCategory;
      const matchQuery =
        !searchQuery ||
        r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.explanation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.related.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchQuery;
    });
  }, [recommendations, selectedCategory, searchQuery]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recommendations & Clinical Protocols"
        subtitle="Illustrative wellness guidance, measurement quality protocols, and clinical assessment indicators."
        actions={
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={fetchRecommendations}
              disabled={loading}
              className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised disabled:opacity-50"
            >
              <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link
              to="/monitoring"
              className="inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90"
            >
              <HeartPulse className="size-3.5" />
              Health Monitoring
            </Link>
          </div>
        }
      />

      {/* Advisory Banner */}
      <Notice tone="warning" icon={<ShieldAlert />}>
        <strong>Medical Advisory Notice:</strong> Recommendations displayed below are illustrative guidance protocols designed for measurement hygiene and educational reference. They do not constitute a physician prescription, medical diagnosis, or treatment plan. For abnormal vitals or acute chest distress, contact emergency healthcare services immediately.
      </Notice>

      {/* Filter and Search Bar */}
      <Panel className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-1.5">
            <Filter className="mr-1 size-3.5 text-muted-foreground" />
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`rounded-md px-2.5 py-1 text-xs transition-colors capitalize ${
                  selectedCategory === cat
                    ? "bg-surface-raised font-medium text-signal border border-border"
                    : "text-muted-foreground hover:bg-surface hover:text-foreground"
                }`}
              >
                {cat === "all" ? "All Categories" : cat}
              </button>
            ))}
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 size-3 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search guidance..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-56 rounded-md border border-border bg-input pl-7 pr-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:border-signal focus:outline-none"
            >
            </input>
          </div>
        </div>
      </Panel>

      {/* Error state */}
      {error && (
        <Notice tone="warning" icon={<AlertCircle />}>
          {error}
        </Notice>
      )}

      {/* Cards Grid */}
      {loading ? (
        <div className="flex h-48 items-center justify-center">
          <RefreshCw className="size-6 animate-spin text-signal" />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No recommendations match the filter"
          text="Try selecting another category or clearing your search query."
          icon={<HeartPulse className="size-6 text-signal" />}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {filtered.map((item) => {
            const tone = getCategoryTone(item.category);
            const icon = getCategoryIcon(item.category);

            return (
              <Panel key={item.id} className="flex flex-col justify-between p-5 transition-colors hover:border-border/80">
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {icon}
                      <Tag tone={tone} dot>
                        {item.category}
                      </Tag>
                    </div>
                    <span className="font-mono text-[11px] text-muted-foreground">{item.id}</span>
                  </div>

                  <h3 className="mt-3 text-sm font-semibold text-foreground">{item.title}</h3>

                  <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{item.explanation}</p>

                  <div className="mt-4 rounded-md border border-border/60 bg-surface-raised/40 p-3">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-signal">
                      Recommended Next Step
                    </span>
                    <p className="mt-1 flex items-start gap-1.5 text-xs font-medium text-foreground">
                      <ArrowRight className="mt-0.5 size-3.5 shrink-0 text-signal" />
                      {item.nextStep}
                    </p>
                  </div>
                </div>

                <div className="mt-5 flex items-center justify-between border-t border-border/40 pt-3 text-[11px]">
                  <span className="text-muted-foreground">
                    Target Domain: <strong className="text-foreground font-normal">{item.related}</strong>
                  </span>
                  <Tag tone="neutral">Guidance Reference</Tag>
                </div>
              </Panel>
            );
          })}
        </div>
      )}

      {/* Quick Action links */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-xs font-semibold text-foreground">Record New Measurements</h4>
              <p className="text-[11px] text-muted-foreground">Log heart rate, blood pressure, SpO2, and body temp.</p>
            </div>
            <Link
              to="/monitoring"
              className="inline-flex items-center gap-1 rounded border border-border px-2.5 py-1 text-xs text-signal hover:bg-surface-raised"
            >
              Go to Monitoring <ExternalLink className="size-3" />
            </Link>
          </div>
        </Panel>

        <Panel className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-xs font-semibold text-foreground">Upload ECG for 1D CNN Analysis</h4>
              <p className="text-[11px] text-muted-foreground">Analyze rhythm regularity and detect arrhythmias.</p>
            </div>
            <Link
              to="/ecg"
              className="inline-flex items-center gap-1 rounded border border-border px-2.5 py-1 text-xs text-signal hover:bg-surface-raised"
            >
              Upload ECG <ExternalLink className="size-3" />
            </Link>
          </div>
        </Panel>
      </div>
    </div>
  );
}
