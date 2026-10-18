import type { Recommendation } from "@/types/health";
import { Tag } from "@/components/common";

export function RecommendationCard({ r }: { r: Recommendation }) {
  return (
    <article className="rounded-md border border-border bg-surface/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-medium">{r.category}</span>
        <Tag tone={r.kind === "wellness" ? "success" : "neutral"}>{r.kind === "wellness" ? "Wellness info" : "Advisory"}</Tag>
      </div>
      <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{r.explanation}</p>
      <p className="mt-3 text-xs"><span className="text-disabled">Next step · </span>{r.nextStep}</p>
      <p className="mt-1.5 font-mono text-[10px] uppercase tracking-wider text-disabled">Related: {r.related}</p>
    </article>
  );
}
