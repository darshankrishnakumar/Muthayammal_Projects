import { Link } from "@tanstack/react-router";
import { BrainCircuit } from "lucide-react";
import { KV, Notice, Panel, PanelHeader, Tag } from "@/components/common";
import { Button } from "@/components/ui/button";
import { pendingPrediction } from "@/services/predictionService";

export function PredictionSummary() {
  const p = pendingPrediction;
  return (
    <Panel className="flex flex-col">
      <PanelHeader title="CNN ANALYSIS SUMMARY" icon={<BrainCircuit />} actions={<Tag tone="warning" dot>Integration pending</Tag>} />
      <div className="mb-4 rounded-md border border-dashed border-border bg-input/60 px-4 py-5 text-center">
        <p className="label-caps">Predicted category</p>
        <p className="mt-2 text-sm text-muted-foreground">Model integration pending</p>
      </div>
      <dl className="flex-1">
        <KV k="Selected recording" v={p.recordingId} />
        <KV k="Analysis status" v="Not analysed" />
        <KV k="Model confidence" v={<span className="text-disabled">Unavailable</span>} />
        <KV k="Analysis timestamp" v={<span className="text-disabled">—</span>} />
      </dl>
      <div className="mt-4 space-y-3">
        <Notice>AI-assisted classification is not a confirmed medical diagnosis.</Notice>
        <Button variant="outline" size="sm" className="w-full" asChild><Link to="/predictions">View detailed analysis</Link></Button>
      </div>
    </Panel>
  );
}
