import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  Footprints,
  History,
  FileText,
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Page } from "@/components/Layout";
import { MedicalDisclaimer } from "@/components/MedicalDisclaimer";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Child Gait Assessment Using Machine Learning" },
      {
        name: "description",
        content:
          "An interactive machine learning system for analyzing gait parameters and identifying gait patterns in children.",
      },
    ],
  }),
  component: HomePage,
});

const features = [
  {
    title: "1. Gait Prediction",
    description: "Analyze measurable gait parameters using machine learning.",
    icon: Footprints,
    link: "/predict",
    linkText: "Start Assessment",
  },
  {
    title: "2. Gait Tracking",
    description: "Monitor gait measurements across multiple assessments.",
    icon: History,
    link: "/history",
    linkText: "View Tracking",
  },
  {
    title: "3. Graphical Reports",
    description: "Visualize changes in gait parameters over time.",
    icon: FileText,
    link: "/reports",
    linkText: "Open Reports",
  },
  {
    title: "4. AI Recommendations",
    description: "Generate educational observations based on prediction results.",
    icon: Sparkles,
    link: "/recommendations",
    linkText: "Read Insights",
  },
];

function HomePage() {
  return (
    <Page>
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl border border-border bg-card p-8 sm:p-12 md:p-16 shadow-xs text-center">
        {/* Simple Medical/AI Visual: Clean badge icon */}
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-medical-border bg-medical text-medical-foreground shadow-2xs">
          <Activity className="h-8 w-8" />
        </div>

        <div className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/60 px-3 py-1 text-xs font-medium text-muted-foreground mb-4">
          <ShieldCheck className="h-3.5 w-3.5 text-medical-foreground" />
          <span>College Academic ML Prototype • Pediatric Biomechanics</span>
        </div>

        <h1 className="mx-auto max-w-3xl text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl md:text-5xl">
          Child Gait Assessment Using Machine Learning
        </h1>

        <p className="mx-auto mt-4 max-w-2xl text-base text-muted-foreground sm:text-lg">
          An interactive machine learning system for analyzing gait parameters and identifying gait
          patterns.
        </p>

        {/* Call to Actions */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3.5">
          <Button asChild size="lg" className="min-w-[190px] shadow-xs cursor-pointer font-medium">
            <Link to="/predict">Start Gait Assessment</Link>
          </Button>

          <Button asChild variant="outline" size="lg" className="min-w-[170px] cursor-pointer">
            <Link to="/history">View Gait History</Link>
          </Button>
        </div>

        {/* Gait Categories Pill preview */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-2 border-t border-border/60 pt-6 text-xs text-muted-foreground">
          <span className="font-medium">Supported Classifications:</span>
          <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 font-medium text-emerald-800 border border-emerald-200">
            Normal
          </span>
          <span className="rounded-full bg-amber-50 px-2.5 py-0.5 font-medium text-amber-900 border border-amber-200">
            Diplegic
          </span>
          <span className="rounded-full bg-rose-50 px-2.5 py-0.5 font-medium text-rose-900 border border-rose-200">
            Hemiplegic
          </span>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section className="mt-12">
        <div className="mb-6 text-center sm:text-left">
          <h2 className="text-xl font-bold tracking-tight text-foreground">
            Core Prototype Capabilities
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Structured workflow from biomechanical inputs to longitudinal evaluation.
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex flex-col justify-between rounded-2xl border border-border bg-card p-6 shadow-xs transition-shadow hover:shadow-sm"
            >
              <div>
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-muted/60 text-foreground">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold text-foreground">{f.title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  {f.description}
                </p>
              </div>

              <div className="mt-6 border-t border-border/50 pt-4">
                <Link
                  to={f.link}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  <span>{f.linkText}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Subtle Medical Disclaimer */}
      <div className="mt-12">
        <MedicalDisclaimer variant="banner" />
      </div>
    </Page>
  );
}
