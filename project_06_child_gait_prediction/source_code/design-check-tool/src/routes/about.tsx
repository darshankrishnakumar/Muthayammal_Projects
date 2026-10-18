import { createFileRoute } from "@tanstack/react-router";
import { ArrowDown, Code2, Cpu, Database, CheckCircle2, ShieldAlert } from "lucide-react";
import { Page } from "@/components/Layout";
import { MedicalDisclaimer } from "@/components/MedicalDisclaimer";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — Child Gait AI" },
      {
        name: "description",
        content:
          "About Child Gait AI — A college-level machine learning project analyzing gait biomechanics and predicting pediatric gait patterns.",
      },
    ],
  }),
  component: AboutPage,
});

const gaitCategories = [
  {
    name: "Normal",
    badge:
      "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300",
    description:
      "Represents typical pediatric bilateral symmetry, expected velocity, and balanced heel-to-toe pressure distribution.",
  },
  {
    name: "Diplegic",
    badge: "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300",
    description:
      "A gait pattern involving bilateral lower extremity characteristics, often associated with altered tilt angle, reduced stride length, and altered stance phases.",
  },
  {
    name: "Hemiplegic",
    badge: "bg-rose-50 text-rose-900 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300",
    description:
      "A gait pattern predominantly affecting one side of the body, characterized by asymmetric limb duration, unequal heel/toe pressure, and unilateral compensation.",
  },
];

const technologies = [
  { name: "React", category: "Frontend", detail: "Interactive UI & Component Architecture" },
  { name: "TypeScript", category: "Language", detail: "Type-safe client data modeling" },
  {
    name: "Tailwind CSS",
    category: "Styling",
    detail: "Responsive design & medical token styling",
  },
  { name: "Python", category: "ML Service", detail: "Data preprocessing & mathematical modeling" },
  {
    name: "Scikit-learn",
    category: "ML Framework",
    detail: "Model training, cross-validation, and metrics",
  },
  {
    name: "Random Forest",
    category: "Algorithm",
    detail: "Ensemble decision-tree multi-class classifier",
  },
  {
    name: "Spring Boot",
    category: "Backend API",
    detail: "RESTful orchestration and secure microservices",
  },
  { name: "MySQL", category: "Storage", detail: "Relational persistence for longitudinal records" },
];

const workflowSteps = [
  {
    title: "Gait Parameters",
    desc: "Heel pressure, toe pressure, tilt angle, step duration, stride length, and speed are captured.",
  },
  {
    title: "Data Preprocessing",
    desc: "Data cleaning, feature scaling, and normalization into model-compatible tensors.",
  },
  {
    title: "Machine Learning Model",
    desc: "Trained Random Forest / ensemble classifier evaluates multi-dimensional biomechanical boundaries.",
  },
  {
    title: "Gait Prediction",
    desc: "Multi-class categorization into Normal, Diplegic, or Hemiplegic gait patterns.",
  },
  {
    title: "Tracking & Reports",
    desc: "Longitudinal parameter storage, graphical trend plotting, and educational decision-support observations.",
  },
];

function AboutPage() {
  return (
    <Page>
      <div className="mx-auto max-w-4xl space-y-12">
        {/* Main Heading & Intro */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            About Child Gait AI
          </h1>
          <p className="mt-3 text-base text-muted-foreground leading-relaxed sm:text-lg">
            This project demonstrates how machine learning can be used to analyze measurable gait
            parameters and predict gait patterns in children.
          </p>
          <div className="mt-4 rounded-xl border border-medical-border bg-medical/30 p-4 text-xs text-muted-foreground leading-relaxed">
            <span className="font-semibold text-foreground">Academic Scope: </span>
            Developed as a college-level academic computer science and medical engineering
            prototype. It emphasizes explainable biomechanical parameters and transparent ML
            decision-support.
          </div>
        </div>

        {/* Gait Categories */}
        <section>
          <h2 className="text-xl font-bold tracking-tight text-foreground">
            Target Gait Classifications
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            The machine learning model is trained to evaluate three primary pediatric
            classifications:
          </p>

          <div className="mt-5 grid gap-4 sm:grid-cols-3">
            {gaitCategories.map((c) => (
              <div
                key={c.name}
                className="flex flex-col justify-between rounded-2xl border border-border bg-card p-5 shadow-xs"
              >
                <div>
                  <span
                    className={`inline-block rounded-full border px-3 py-0.5 text-xs font-semibold ${c.badge}`}
                  >
                    {c.name}
                  </span>
                  <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                    {c.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Workflow Diagram */}
        <section>
          <h2 className="text-xl font-bold tracking-tight text-foreground">
            System Workflow Architecture
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            End-to-end data pipeline from sensor parameter acquisition to longitudinal reporting:
          </p>

          <div className="mt-6 space-y-2">
            {workflowSteps.map((step, idx) => (
              <div key={step.title} className="flex flex-col items-center">
                <div className="w-full rounded-xl border border-border bg-card p-4 shadow-2xs">
                  <div className="flex items-start gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/40 font-mono text-xs font-bold text-foreground">
                      {idx + 1}
                    </span>
                    <div>
                      <h3 className="text-sm font-semibold text-foreground">{step.title}</h3>
                      <p className="mt-0.5 text-xs text-muted-foreground">{step.desc}</p>
                    </div>
                  </div>
                </div>

                {idx < workflowSteps.length - 1 && (
                  <div className="py-1">
                    <ArrowDown className="h-4 w-4 text-muted-foreground/60" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Technology Stack */}
        <section>
          <h2 className="text-xl font-bold tracking-tight text-foreground">Technology Stack</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Full-stack machine learning architecture designed for research and educational
            reproducibility:
          </p>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {technologies.map((t) => (
              <div key={t.name} className="rounded-xl border border-border bg-card p-4 shadow-xs">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block">
                  {t.category}
                </span>
                <span className="mt-1 block text-sm font-bold text-foreground">{t.name}</span>
                <span className="mt-1 block text-[11px] text-muted-foreground leading-snug">
                  {t.detail}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Medical Notice */}
        <MedicalDisclaimer variant="card" />
      </div>
    </Page>
  );
}
