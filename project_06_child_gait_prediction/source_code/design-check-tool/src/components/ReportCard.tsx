import {
  Printer,
  Download,
  FileText,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Info,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { MedicalDisclaimer } from "./MedicalDisclaimer";
import { PARAM_DEFINITIONS } from "./AssessmentSummary";
import type { AssessmentRecord } from "@/services/api";

interface ReportCardProps {
  record: AssessmentRecord;
}

export function ReportCard({ record }: ReportCardProps) {
  const pred = record.prediction;
  const isNormal = pred?.toLowerCase() === "normal";
  const isDiplegic = pred?.toLowerCase() === "diplegic";
  const isHemiplegic = pred?.toLowerCase() === "hemiplegic";

  let statusBadge = "bg-muted text-foreground border-border";
  let Icon = CheckCircle2;
  let defaultObservation =
    "Parameters have been processed by the machine learning classification model.";

  if (isNormal) {
    statusBadge =
      "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300";
    Icon = CheckCircle2;
    defaultObservation =
      "Current gait parameters were classified as Normal. Biomechanical parameters indicate symmetric stance phases and expected progression velocity for pediatric development.";
  } else if (isDiplegic) {
    statusBadge =
      "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300";
    Icon = AlertTriangle;
    defaultObservation =
      "Current gait parameters reflect bilateral deviations consistent with Diplegic gait patterns. Bilateral step duration and pressure distribution warrant formal pediatric orthopedic review.";
  } else if (isHemiplegic) {
    statusBadge = "bg-rose-50 text-rose-900 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300";
    Icon = AlertCircle;
    defaultObservation =
      "Current gait parameters reflect asymmetrical biomechanics consistent with Hemiplegic gait patterns. Unilateral stance time discrepancy observed.";
  }

  const observationText =
    record.recommendations && record.recommendations.length > 0
      ? record.recommendations.join(" ")
      : defaultObservation;

  const hasConfidence = record.confidence !== undefined && record.confidence !== null;
  const confidencePercent = hasConfidence
    ? Math.round(record.confidence! <= 1 ? record.confidence! * 100 : record.confidence!)
    : null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-6 sm:p-10 shadow-xs print:border-none print:shadow-none space-y-8">
      {/* Report Header */}
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-6 sm:flex-row sm:items-start">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-medical-border bg-medical text-medical-foreground">
              <FileText className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                Pediatric Gait Assessment Report
              </h2>
              <p className="text-xs text-muted-foreground">
                College Medical AI Prototype • Machine Learning Decision-Support
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handlePrint}
            className="gap-1.5 text-xs"
          >
            <Printer className="h-3.5 w-3.5" />
            Print / Save as PDF
          </Button>

          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled
            title="Backend PDF export service not connected in this prototype"
            className="gap-1.5 text-xs cursor-not-allowed opacity-60"
          >
            <Download className="h-3.5 w-3.5" />
            Backend PDF (Offline)
          </Button>
        </div>
      </div>

      {/* 1. Child Information & 2. Assessment Date */}
      <div className="grid gap-4 rounded-xl border border-border/70 bg-muted/20 p-5 sm:grid-cols-4 text-xs">
        <div>
          <span className="block font-medium text-muted-foreground">Child Identifier</span>
          <span className="mt-1 block font-mono text-base font-bold text-foreground">
            {record.childId}
          </span>
        </div>
        <div>
          <span className="block font-medium text-muted-foreground">Age</span>
          <span className="mt-1 block text-sm font-semibold text-foreground">
            {record.age} Years Old
          </span>
        </div>
        <div>
          <span className="block font-medium text-muted-foreground">Gender</span>
          <span className="mt-1 block text-sm font-semibold text-foreground">{record.gender}</span>
        </div>
        <div>
          <span className="block font-medium text-muted-foreground">Assessment Date</span>
          <span className="mt-1 block text-sm font-semibold text-foreground">
            {new Date(record.date).toLocaleDateString(undefined, {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </span>
        </div>
      </div>

      {/* 4. ML Prediction & 5. Confidence */}
      <div className={`rounded-xl border p-5 ${statusBadge}`}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <Icon className="h-6 w-6 shrink-0" />
            <div>
              <span className="text-[11px] font-semibold uppercase tracking-wider opacity-80">
                Machine Learning Prediction
              </span>
              <p className="text-2xl font-bold tracking-tight">{record.prediction} Gait Pattern</p>
            </div>
          </div>

          {confidencePercent !== null && (
            <div className="rounded-lg border border-current/25 bg-background/50 px-3.5 py-2 text-center">
              <span className="block text-[10px] font-medium uppercase tracking-wider opacity-75">
                Model Confidence
              </span>
              <span className="font-mono text-base font-bold">{confidencePercent}%</span>
            </div>
          )}
        </div>
      </div>

      {/* 3. Gait Parameters & 6. Graphical Analysis */}
      <div>
        <div className="mb-3 flex items-center justify-between border-b border-border pb-2">
          <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
            Gait Parameter Analysis
          </h3>
          <span className="text-[11px] text-muted-foreground">Biomechanical Input Comparison</span>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {PARAM_DEFINITIONS.map((def) => {
            const val = record[def.key as keyof AssessmentRecord];
            return (
              <div
                key={def.key}
                className="rounded-lg border border-border bg-card p-3.5 shadow-2xs"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-muted-foreground">{def.label}</span>
                  <span className="font-mono font-bold text-foreground">
                    {val !== undefined ? `${val}${def.unit}` : "—"}
                  </span>
                </div>
                <div className="mt-2 text-[11px] text-muted-foreground/80 flex items-center justify-between border-t border-border/40 pt-1.5">
                  <span>Standard Range:</span>
                  <span className="font-mono">{def.range}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 7. AI Observation */}
      <div className="rounded-xl border border-medical-border bg-medical/30 p-5 text-xs">
        <div className="mb-2 flex items-center gap-2 font-semibold text-foreground">
          <Info className="h-4 w-4 text-medical-foreground" />
          <span>Educational AI Observation</span>
        </div>
        <p className="leading-relaxed text-muted-foreground">{observationText}</p>
        <p className="mt-2 text-[11px] text-muted-foreground/80">
          Suggested Next Step: Continue regular monitoring and consult a qualified healthcare
          professional if gait abnormalities or mobility challenges arise.
        </p>
      </div>

      {/* 8. Disclaimer */}
      <MedicalDisclaimer variant="card" />
    </div>
  );
}
