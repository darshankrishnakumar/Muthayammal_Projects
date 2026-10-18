import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PageHeader, Panel, PanelHeader, DemoBadge, Tag } from "@/components/common";
import { BiometricGrid } from "@/components/cards/BiometricGrid";
import { EcgChart } from "@/components/charts/EcgChart";
import { TrendChart } from "@/components/charts/TrendChart";
import { PredictionSummary } from "@/components/cards/PredictionSummary";
import { AlertsPanel } from "@/components/alerts/AlertsPanel";
import { RecommendationCard } from "@/components/cards/RecommendationCard";
import { RecordsTable } from "@/components/tables/RecordsTable";
import { demoAlerts, demoMeasurements, demoRecommendations } from "@/data/demoMeasurements";
import { demoHistory } from "@/data/demoHistory";
import { getHealthSummary, getHealthTrends, type HealthSummaryData } from "@/services/sensorService";
import type { Measurement } from "@/types/health";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Health Monitoring Overview — BioPulse" },
      { name: "description", content: "Review biometric measurements, ECG signals, AI analysis and alerts in one workspace." },
      { property: "og:title", content: "Health Monitoring Overview — BioPulse" },
      { property: "og:description", content: "Biometric monitoring and CNN-assisted analysis dashboard." },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const [realTrends, setRealTrends] = useState<Measurement[]>([]);
  const [realSummary, setRealSummary] = useState<HealthSummaryData | null>(null);
  const [hasRealData, setHasRealData] = useState(false);

  useEffect(() => {
    Promise.all([
      getHealthTrends({ limit: 100 }).catch(() => []),
      getHealthSummary().catch(() => null),
    ]).then(([trends, summary]) => {
      if (Array.isArray(trends) && trends.length > 0) {
        setRealTrends(trends);
        setHasRealData(true);
      }
      if (summary) {
        setRealSummary(summary);
      }
    });
  }, []);

  // Compute latest compound measurement if available
  const activeHistory = hasRealData && realTrends.length > 0 ? realTrends : demoMeasurements;
  const latestItem: Measurement | undefined = realSummary && (
    realSummary.heart_rate?.latest ||
    realSummary.blood_pressure?.latest ||
    realSummary.spo2?.latest ||
    realSummary.body_temperature?.latest
  ) ? {
    timestamp: (
      realSummary.heart_rate?.latest?.measuredAt ||
      realSummary.blood_pressure?.latest?.measuredAt ||
      realSummary.spo2?.latest?.measuredAt ||
      realSummary.body_temperature?.latest?.measuredAt ||
      new Date().toISOString()
    ),
    heartRate: realSummary.heart_rate?.latest?.value ?? activeHistory[activeHistory.length - 1]?.heartRate ?? 72,
    systolic: realSummary.blood_pressure?.latest?.systolic ?? activeHistory[activeHistory.length - 1]?.systolic ?? 120,
    diastolic: realSummary.blood_pressure?.latest?.diastolic ?? activeHistory[activeHistory.length - 1]?.diastolic ?? 80,
    spo2: realSummary.spo2?.latest?.value ?? activeHistory[activeHistory.length - 1]?.spo2 ?? 98,
    temperature: realSummary.body_temperature?.latest?.value ?? activeHistory[activeHistory.length - 1]?.temperature ?? 36.6,
    source: "manual",
  } : undefined;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Health Monitoring Overview"
        subtitle="Review biometric measurements, ECG signals, AI analysis, and health monitoring alerts from one workspace."
        actions={
          hasRealData ? (
            <Tag tone="signal">SQLite Database Live</Tag>
          ) : (
            <DemoBadge label="Demo / Initial State" />
          )
        }
      />

      <BiometricGrid history={activeHistory} latest={latestItem} />

      <div className="grid gap-6 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader
            title="ECG Signal Monitor"
            subtitle="Illustrative ECG — Not a Live Sensor Feed"
            actions={<DemoBadge label="Illustrative" />}
          />
          <EcgChart />
        </Panel>
        <PredictionSummary />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader
            title="Health Trend Analytics"
            actions={hasRealData ? <Tag tone="signal">Real Records</Tag> : <DemoBadge />}
          />
          <TrendChart data={activeHistory} metric="heartRate" />
        </Panel>
        <AlertsPanel alerts={demoAlerts} />
      </div>

      <Panel>
        <PanelHeader
          title="Recommendations"
          actions={<DemoBadge label="Illustrative guidelines" />}
        />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {demoRecommendations.map((r) => (
            <RecommendationCard key={r.id} r={r} />
          ))}
        </div>
      </Panel>

      <Panel>
        <PanelHeader
          title="Recent Analysis History"
          actions={hasRealData ? <Tag tone="signal">Active</Tag> : <DemoBadge />}
        />
        <RecordsTable records={demoHistory} />
      </Panel>
    </div>
  );
}
