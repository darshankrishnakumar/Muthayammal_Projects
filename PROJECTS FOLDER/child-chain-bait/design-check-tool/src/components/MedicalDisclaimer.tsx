import { ShieldAlert } from "lucide-react";

interface MedicalDisclaimerProps {
  className?: string;
  variant?: "subtle" | "banner" | "card";
}

export function MedicalDisclaimer({ className = "", variant = "subtle" }: MedicalDisclaimerProps) {
  if (variant === "banner") {
    return (
      <aside
        aria-label="Medical Disclaimer"
        className={`flex items-start gap-3 rounded-lg border border-medical-border bg-medical/50 p-4 text-xs text-muted-foreground ${className}`}
      >
        <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-medical-foreground" />
        <div>
          <span className="font-semibold text-foreground">Academic ML Prototype Disclaimer: </span>
          This application is a college-level machine learning prototype intended for educational
          and decision-support purposes. It does not replace professional medical diagnosis,
          clinical assessment, or treatment.
        </div>
      </aside>
    );
  }

  if (variant === "card") {
    return (
      <div
        className={`rounded-xl border border-border bg-card p-5 text-xs text-muted-foreground ${className}`}
      >
        <div className="mb-2 flex items-center gap-2 font-medium text-foreground">
          <ShieldAlert className="h-4 w-4 text-medical-foreground" />
          <span>Medical Notice</span>
        </div>
        <p className="leading-relaxed">
          This application is a college-level machine learning prototype intended for educational
          and decision-support purposes. It does not replace professional medical diagnosis,
          clinical assessment, or treatment. Always consult qualified healthcare professionals for
          pediatric gait evaluation.
        </p>
      </div>
    );
  }

  return (
    <p className={`text-xs text-muted-foreground ${className}`}>
      <span className="font-medium">Disclaimer:</span> This application is a college-level machine
      learning prototype intended for educational and decision-support purposes. It does not replace
      professional medical diagnosis, clinical assessment, or treatment.
    </p>
  );
}
