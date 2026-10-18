import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Page } from "@/components/Layout";
import { GaitHistoryTable } from "@/components/GaitHistoryTable";
import { ProgressChart } from "@/components/ProgressChart";
import { MedicalDisclaimer } from "@/components/MedicalDisclaimer";
import { fetchAssessments, removeStoredAssessment, type AssessmentRecord } from "@/services/api";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Gait History & Longitudinal Tracking — Child Gait AI" },
      {
        name: "description",
        content:
          "Review historical pediatric gait assessments and longitudinal parameter progression over time.",
      },
    ],
  }),
  component: HistoryPage,
});

function HistoryPage() {
  const [records, setRecords] = useState<AssessmentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChildId, setSelectedChildId] = useState<string>("ALL");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchAssessments();
        setRecords(data);
      } catch (err) {
        console.error("Failed to load assessments", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleDelete = (id: string) => {
    removeStoredAssessment(id);
    setRecords((prev) => prev.filter((r) => r.id !== id));
  };

  return (
    <Page>
      <div className="space-y-10">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Gait Assessment History
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
            Longitudinal records and developmental trajectory tracking for monitored children.
          </p>
        </div>

        {/* Longitudinal Tracking Progress Chart Section */}
        <section aria-label="Longitudinal Tracking">
          <ProgressChart records={records} selectedChildId={selectedChildId} />
        </section>

        {/* Historical Table Section */}
        <section aria-label="Historical Assessments">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-bold text-foreground">Assessment Records</h2>
            <span className="text-xs text-muted-foreground">
              {records.length} {records.length === 1 ? "record" : "records"} found
            </span>
          </div>

          <GaitHistoryTable
            records={records}
            onDeleteRecord={handleDelete}
            onSelectRecord={(rec) => setSelectedChildId(rec.childId)}
          />
        </section>

        <MedicalDisclaimer variant="card" />
      </div>
    </Page>
  );
}
