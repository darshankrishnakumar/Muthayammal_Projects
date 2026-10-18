import { Link } from "@tanstack/react-router";
import { Activity } from "lucide-react";
import { MedicalDisclaimer } from "./MedicalDisclaimer";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-border bg-card/50">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md border border-medical-border bg-medical text-medical-foreground">
              <Activity className="h-4 w-4" />
            </div>
            <span className="text-sm font-semibold text-foreground">Child Gait AI</span>
            <span className="text-xs text-muted-foreground">• College Academic ML Project</span>
          </div>

          <div className="flex flex-wrap justify-center gap-5 text-xs text-muted-foreground">
            <Link to="/" className="hover:text-foreground">
              Home
            </Link>
            <Link to="/predict" className="hover:text-foreground">
              Prediction
            </Link>
            <Link to="/history" className="hover:text-foreground">
              History
            </Link>
            <Link to="/reports" className="hover:text-foreground">
              Reports
            </Link>
            <Link to="/recommendations" className="hover:text-foreground">
              Recommendations
            </Link>
            <Link to="/about" className="hover:text-foreground">
              About
            </Link>
          </div>
        </div>

        <div className="mt-6 border-t border-border/60 pt-4 text-center">
          <MedicalDisclaimer variant="subtle" className="mx-auto max-w-3xl" />
          <p className="mt-2 text-[11px] text-muted-foreground">
            Designed for educational exploration of pediatric gait biomechanics & pattern
            classification.
          </p>
        </div>
      </div>
    </footer>
  );
}
