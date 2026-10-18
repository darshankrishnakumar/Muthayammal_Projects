import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { FileText, ArrowRight, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Page } from "@/components/Layout";
import { ReportCard } from "@/components/ReportCard";
import { fetchAssessments, type AssessmentRecord } from "@/services/api";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Gait Assessment Reports — Child Gait AI" },
      {
        name: "description",
        content:
          "Generate and review formal pediatric gait evaluation reports with parameter breakdown and AI observations.",
      },
    ],
  }),
  component: ReportsPage,
});

function ReportsPage() {
  const [records, setRecords] = useState<AssessmentRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchAssessments();
        setRecords(data);
        if (data.length > 0 && data[0]) {
          setSelectedId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load assessments for reports", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const selectedRecord = records.find((r) => r.id === selectedId) || records[0];

  return (
    <Page>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              Gait Reports
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
              Comprehensive biomechanical evaluation reports and educational summaries.
            </p>
          </div>

          {records.length > 1 && (
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <User className="h-4 w-4 text-muted-foreground" />
              <select
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
                className="rounded-lg border border-input bg-card px-3 py-1.5 text-xs outline-none transition focus:border-ring focus:ring-1 focus:ring-ring"
              >
                {records.map((r) => (
                  <option key={r.id} value={r.id}>
                    Child {r.childId} — {new Date(r.date).toLocaleDateString()} ({r.prediction})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Empty State when no assessment exists */}
        {records.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-card p-12 text-center shadow-xs">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-medical text-medical-foreground">
              <FileText className="h-6 w-6" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-foreground">
              Complete a gait assessment to generate a report.
            </h3>
            <p className="mx-auto mt-2 max-w-sm text-xs text-muted-foreground">
              No previous assessments found in the system. Complete an initial assessment to view
              full graphical analysis and report breakdown.
            </p>
            <div className="mt-6">
              <Button asChild size="default">
                <Link to="/predict">
                  <span>Start Assessment</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        ) : selectedRecord ? (
          <ReportCard record={selectedRecord} />
        ) : null}
      </div>
    </Page>
  );
}
