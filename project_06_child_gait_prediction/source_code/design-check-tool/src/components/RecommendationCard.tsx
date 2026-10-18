import { Sparkles, Info, ShieldAlert, ArrowRight } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { MedicalDisclaimer } from "./MedicalDisclaimer";
import type { AssessmentRecord } from "@/services/api";

interface RecommendationCardProps {
  record?: AssessmentRecord | null | undefined;
}

export function RecommendationCard({ record }: RecommendationCardProps) {
  // If no record is selected/present
  if (!record) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-medical text-medical-foreground">
          <Sparkles className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-base font-semibold text-foreground">AI Recommendations</h3>
        <p className="mx-auto mt-2 max-w-md text-xs text-muted-foreground">
          AI recommendations will be available after backend integration or following a completed
          gait assessment.
        </p>
        <div className="mt-6">
          <Button asChild size="sm">
            <Link to="/predict">Perform Gait Assessment</Link>
          </Button>
        </div>
      </div>
    );
  }

  const pred = record.prediction?.toLowerCase();
  const isNormal = pred === "normal";
  const isDiplegic = pred === "diplegic";
  const isHemiplegic = pred === "hemiplegic";

  // If backend provided specific recommendations array
  const hasBackendRecs = record.recommendations && record.recommendations.length > 0;

  let observation = "Current gait parameters were classified by the machine learning model.";
  let nextStep =
    "Continue regular monitoring and consult a qualified healthcare professional if concerns arise.";

  if (hasBackendRecs) {
    observation = record.recommendations![0] ?? observation;
    if (record.recommendations!.length > 1) {
      nextStep = record.recommendations![1] ?? nextStep;
    }
  } else if (isNormal) {
    observation = "Current gait parameters were classified as Normal.";
    nextStep =
      "Continue regular developmental monitoring and consult a qualified healthcare professional if concerns arise.";
  } else if (isDiplegic) {
    observation = "Current gait parameters were classified as Diplegic pattern.";
    nextStep =
      "Consult a pediatric orthopedic specialist or physical therapist for formal clinical gait analysis and targeted functional guidance.";
  } else if (isHemiplegic) {
    observation = "Current gait parameters were classified as Hemiplegic pattern.";
    nextStep =
      "Recommend clinical assessment by a pediatric neurologist or rehabilitation clinician to evaluate unilateral limb coordination.";
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col gap-2 border-b border-border pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-medical-border bg-medical text-medical-foreground">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-foreground">AI-Based Recommendations</h3>
              <p className="text-xs text-muted-foreground">
                Educational observations generated from the gait assessment for Child{" "}
                <span className="font-semibold text-foreground">{record.childId}</span>
              </p>
            </div>
          </div>

          <span className="self-start rounded-full border border-border bg-muted/60 px-3 py-1 font-mono text-xs font-medium text-foreground sm:self-auto">
            Classified: {record.prediction}
          </span>
        </div>

        {/* Observation Block */}
        <div className="mt-6 space-y-4 text-xs">
          <div className="rounded-xl border border-border bg-muted/20 p-4">
            <span className="font-semibold uppercase tracking-wider text-muted-foreground block text-[10px]">
              Prediction
            </span>
            <p className="mt-1 text-sm font-bold text-foreground">“{record.prediction}”</p>
          </div>

          <div className="rounded-xl border border-medical-border bg-medical/30 p-4">
            <span className="font-semibold uppercase tracking-wider text-medical-foreground block text-[10px]">
              AI Observation
            </span>
            <p className="mt-1 text-sm text-foreground leading-relaxed">“{observation}”</p>
          </div>

          <div className="rounded-xl border border-border bg-card p-4">
            <span className="font-semibold uppercase tracking-wider text-muted-foreground block text-[10px]">
              Suggested Next Step
            </span>
            <p className="mt-1 text-sm text-foreground leading-relaxed">“{nextStep}”</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
          <Link
            to="/reports"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"
          >
            <span>View Full Assessment Report</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
          <span className="text-[11px] text-muted-foreground">
            Assessment Date: {new Date(record.date).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Safety Notice */}
      <MedicalDisclaimer variant="card" />
    </div>
  );
}
