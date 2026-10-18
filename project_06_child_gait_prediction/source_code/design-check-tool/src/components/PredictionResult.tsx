import { Link } from "@tanstack/react-router";
import {
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  BookmarkCheck,
  FileText,
  History,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { AssessmentSummary } from "./AssessmentSummary";
import { MedicalDisclaimer } from "./MedicalDisclaimer";
import type { GaitInput, PredictionResponse } from "@/services/api";

interface PredictionResultProps {
  result: PredictionResponse;
  input: GaitInput;
  onSave?: () => void;
  isSaved?: boolean;
}

export function PredictionResult({
  result,
  input,
  onSave,
  isSaved = false,
}: PredictionResultProps) {
  const prediction = result.prediction;
  const isNormal = prediction?.toLowerCase() === "normal";
  const isDiplegic = prediction?.toLowerCase() === "diplegic";
  const isHemiplegic = prediction?.toLowerCase() === "hemiplegic";

  // Color & Badge Configuration adhering strictly to design style
  let badgeClasses = "bg-muted text-foreground border-border";
  let Icon = CheckCircle2;
  let explanation =
    "The entered gait parameters have been evaluated by the machine learning model.";
  let clinicalNote = "Regular developmental observation recommended.";

  if (isNormal) {
    badgeClasses =
      "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
    Icon = CheckCircle2;
    explanation =
      "Current gait parameters were classified as Normal by the trained classification model.";
    clinicalNote =
      "Gait parameters fall within standard reference intervals for bilateral symmetry and velocity.";
  } else if (isDiplegic) {
    badgeClasses =
      "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800";
    Icon = AlertTriangle;
    explanation =
      "Predicted gait pattern: Diplegic. The model detected bilateral parameter variations involving both lower extremities.";
    clinicalNote =
      "Further clinical evaluation by a pediatric specialist may be appropriate to assess lower limb biomechanics.";
  } else if (isHemiplegic) {
    badgeClasses =
      "bg-rose-50 text-rose-900 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800";
    Icon = AlertCircle;
    explanation =
      "Predicted gait pattern: Hemiplegic. The model detected asymmetrical gait characteristics primarily affecting one side.";
    clinicalNote =
      "Further clinical evaluation by a pediatric specialist may be appropriate to investigate asymmetric limb mechanics.";
  }

  // Confidence computation: only display if supplied by backend!
  const hasConfidence = result.confidence !== undefined && result.confidence !== null;
  const confidencePercent = hasConfidence
    ? Math.round(result.confidence! <= 1 ? result.confidence! * 100 : result.confidence!)
    : null;

  return (
    <section className="fade-in space-y-6">
      {/* Result Card */}
      <div className={`rounded-2xl border p-6 sm:p-8 shadow-xs ${badgeClasses}`}>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Icon className="h-5 w-5 shrink-0" />
              <h2 className="text-sm font-semibold uppercase tracking-wider">
                Gait Assessment Result
              </h2>
            </div>
            <p className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">{prediction}</p>
            <p className="mt-1 text-sm opacity-90">{explanation}</p>
          </div>

          {confidencePercent !== null && (
            <div className="rounded-xl border border-current/20 bg-background/50 px-4 py-3 text-center">
              <span className="block text-[11px] font-medium uppercase tracking-wider opacity-80">
                Confidence
              </span>
              <span className="font-mono text-xl font-bold">{confidencePercent}%</span>
            </div>
          )}
        </div>

        <div className="mt-6 border-t border-current/15 pt-4">
          <p className="text-xs leading-relaxed font-medium">
            Clinical observation: <span className="font-normal opacity-90">{clinicalNote}</span>
          </p>
        </div>
      </div>

      {/* Assessment Summary */}
      <AssessmentSummary
        data={{
          ...input,
          date: new Date().toISOString(),
        }}
        title="Assessment Summary"
      />

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-card p-4">
        <div className="flex flex-wrap gap-2.5">
          {onSave && (
            <Button
              type="button"
              variant={isSaved ? "outline" : "default"}
              onClick={onSave}
              disabled={isSaved}
              className="gap-2 text-xs"
            >
              <BookmarkCheck className="h-4 w-4" />
              {isSaved ? "Assessment Saved" : "Save Assessment"}
            </Button>
          )}

          <Button asChild variant="outline" className="gap-2 text-xs">
            <Link to="/reports">
              <FileText className="h-4 w-4" />
              View Report
            </Link>
          </Button>

          <Button asChild variant="outline" className="gap-2 text-xs">
            <Link to="/history">
              <History className="h-4 w-4" />
              View History
            </Link>
          </Button>
        </div>

        <span className="text-[11px] text-muted-foreground">
          Child ID: <span className="font-semibold text-foreground">{input.childId}</span>
        </span>
      </div>

      {/* Medical Disclaimer */}
      <MedicalDisclaimer variant="card" />
    </section>
  );
}
