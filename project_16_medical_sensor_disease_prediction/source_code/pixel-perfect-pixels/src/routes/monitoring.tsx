import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useMemo, useCallback } from "react";
import {
  HeartPulse,
  Gauge,
  Droplets,
  Thermometer,
  PlusCircle,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Edit2,
  Trash2,
  Filter,
  Calendar,
  Activity,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";
import { PageHeader, Panel, PanelHeader, Tag, Notice, EmptyState, InfoTip } from "@/components/common";
import { TrendChart } from "@/components/charts/TrendChart";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  getHealthSummary,
  getHealthTrends,
  getMeasurements,
  createManualMeasurement,
  updateMeasurement,
  deleteMeasurement,
  type HealthSummaryData,
  type MeasurementRecord,
} from "@/services/sensorService";
import type { Measurement, MetricKey } from "@/types/health";
import { fmtDateTime } from "@/utils/format";

export const Route = createFileRoute("/monitoring")({
  head: () => ({
    meta: [
      { title: "Health Monitoring — BioPulse" },
      { name: "description", content: "Manual health measurement entry, SQLite persistence, physiological bounds validation, and trend monitoring." },
      { property: "og:title", content: "Health Monitoring — BioPulse" },
      { property: "og:description", content: "Biometric measurement logging and analysis." },
    ],
  }),
  component: HealthMonitoringPage,
});

function toLocalDatetimeString(date: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export function HealthMonitoringPage() {
  // Form state
  const [heartRate, setHeartRate] = useState<string>("");
  const [systolic, setSystolic] = useState<string>("");
  const [diastolic, setDiastolic] = useState<string>("");
  const [spo2, setSpo2] = useState<string>("");
  const [temperature, setTemperature] = useState<string>("");
  const [measuredAt, setMeasuredAt] = useState<string>(() => toLocalDatetimeString(new Date()));

  // UI state
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({});

  // Data state
  const [summary, setSummary] = useState<HealthSummaryData | null>(null);
  const [trends, setTrends] = useState<Measurement[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<MetricKey>("heartRate");
  const [records, setRecords] = useState<MeasurementRecord[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loadingData, setLoadingData] = useState(false);

  // Table filters
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStartDate, setFilterStartDate] = useState<string>("");
  const [filterEndDate, setFilterEndDate] = useState<string>("");

  // Edit dialog state
  const [editingRecord, setEditingRecord] = useState<MeasurementRecord | null>(null);
  const [editValue, setEditValue] = useState<string>("");
  const [editSystolic, setEditSystolic] = useState<string>("");
  const [editDiastolic, setEditDiastolic] = useState<string>("");
  const [editMeasuredAt, setEditMeasuredAt] = useState<string>("");
  const [savingEdit, setSavingEdit] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  // Delete dialog state
  const [deletingRecord, setDeletingRecord] = useState<MeasurementRecord | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Refresh all dashboard data from backend
  const loadDashboardData = useCallback(async () => {
    setLoadingData(true);
    try {
      const [sumRes, trendRes, measRes] = await Promise.all([
        getHealthSummary().catch(() => null),
        getHealthTrends({ limit: 100 }).catch(() => []),
        getMeasurements({
          measurementType: filterType !== "all" ? filterType : undefined,
          startDate: filterStartDate || undefined,
          endDate: filterEndDate || undefined,
          limit: 100,
        }).catch(() => ({ total: 0, limit: 100, offset: 0, records: [] })),
      ]);

      if (sumRes) setSummary(sumRes);
      if (Array.isArray(trendRes)) setTrends(trendRes);
      if (measRes) {
        setRecords(measRes.records);
        setTotalRecords(measRes.total);
      }
    } catch (err: unknown) {
      console.error("Failed to load monitoring data:", err);
    } finally {
      setLoadingData(false);
    }
  }, [filterType, filterStartDate, filterEndDate]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Client-side validation for manual entry form
  const validateForm = () => {
    const errs: Record<string, string> = {};

    const hasAny = heartRate || systolic || diastolic || spo2 || temperature;
    if (!hasAny) {
      errs.form = "Please enter at least one health measurement.";
      return errs;
    }

    if (heartRate) {
      const hr = Number(heartRate);
      if (isNaN(hr)) errs.heartRate = "Heart rate must be numeric.";
      else if (hr < 30 || hr > 250) errs.heartRate = "Plausible heart rate is between 30 and 250 BPM.";
    }

    if (systolic || diastolic) {
      if (!systolic) errs.systolic = "Systolic pressure is required when diastolic is entered.";
      if (!diastolic) errs.diastolic = "Diastolic pressure is required when systolic is entered.";

      if (systolic && diastolic) {
        const sys = Number(systolic);
        const dia = Number(diastolic);
        if (isNaN(sys)) errs.systolic = "Systolic must be numeric.";
        else if (sys < 50 || sys > 260) errs.systolic = "Plausible systolic pressure is 50-260 mmHg.";

        if (isNaN(dia)) errs.diastolic = "Diastolic must be numeric.";
        else if (dia < 30 || dia > 160) errs.diastolic = "Plausible diastolic pressure is 30-160 mmHg.";

        if (!isNaN(sys) && !isNaN(dia) && sys <= dia) {
          errs.systolic = "Systolic pressure must be strictly greater than diastolic pressure.";
        }
      }
    }

    if (spo2) {
      const sp = Number(spo2);
      if (isNaN(sp)) errs.spo2 = "SpO2 must be numeric.";
      else if (sp < 0 || sp > 100) errs.spo2 = "SpO2 must be between 0% and 100%.";
    }

    if (temperature) {
      const temp = Number(temperature);
      if (isNaN(temp)) errs.temperature = "Temperature must be numeric.";
      else if (temp < 30 || temp > 45) errs.temperature = "Plausible body temperature is 30.0°C to 45.0°C.";
    }

    if (!measuredAt) {
      errs.measuredAt = "Measurement timestamp is required.";
    }

    return errs;
  };

  const handleResetForm = () => {
    setHeartRate("");
    setSystolic("");
    setDiastolic("");
    setSpo2("");
    setTemperature("");
    setMeasuredAt(toLocalDatetimeString(new Date()));
    setClientErrors({});
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    setErrorMsg(null);

    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setClientErrors(validationErrors);
      setErrorMsg("Please fix the validation errors before saving.");
      return;
    }
    setClientErrors({});

    setSubmitting(true);
    try {
      const isoTimestamp = new Date(measuredAt).toISOString();
      const payload: {
        heartRate?: number;
        systolic?: number;
        diastolic?: number;
        spo2?: number;
        temperature?: number;
        measuredAt: string;
        source: "manual";
      } = {
        measuredAt: isoTimestamp,
        source: "manual",
      };

      if (heartRate) payload.heartRate = Number(heartRate);
      if (systolic && diastolic) {
        payload.systolic = Number(systolic);
        payload.diastolic = Number(diastolic);
      }
      if (spo2) payload.spo2 = Number(spo2);
      if (temperature) payload.temperature = Number(temperature);

      const res = await createManualMeasurement(payload);
      setSuccessMsg(
        `Successfully saved ${res.createdCount} measurement(s) to SQLite database at ${fmtDateTime(isoTimestamp)}.`
      );
      handleResetForm();
      await loadDashboardData();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to record manual measurement.";
      setErrorMsg(message);
    } finally {
      setSubmitting(false);
    }
  };

  // Open Edit Dialog
  const handleOpenEdit = (rec: MeasurementRecord) => {
    setEditingRecord(rec);
    setEditError(null);
    setEditMeasuredAt(rec.measuredAt ? toLocalDatetimeString(new Date(rec.measuredAt)) : "");

    if (rec.measurementType === "blood_pressure") {
      setEditSystolic(rec.systolic !== null ? String(rec.systolic) : "");
      setEditDiastolic(rec.diastolic !== null ? String(rec.diastolic) : "");
      setEditValue("");
    } else {
      setEditValue(rec.value !== null ? String(rec.value) : "");
      setEditSystolic("");
      setEditDiastolic("");
    }
  };

  // Save Edit
  const handleSaveEdit = async () => {
    if (!editingRecord) return;
    setEditError(null);
    setSavingEdit(true);

    try {
      const payload: {
        value?: number;
        systolic?: number;
        diastolic?: number;
        measuredAt?: string;
      } = {};

      if (editMeasuredAt) {
        payload.measuredAt = new Date(editMeasuredAt).toISOString();
      }

      if (editingRecord.measurementType === "blood_pressure") {
        const sys = Number(editSystolic);
        const dia = Number(editDiastolic);
        if (isNaN(sys) || sys < 50 || sys > 260) {
          throw new Error("Systolic pressure must be between 50 and 260 mmHg.");
        }
        if (isNaN(dia) || dia < 30 || dia > 160) {
          throw new Error("Diastolic pressure must be between 30 and 160 mmHg.");
        }
        if (sys <= dia) {
          throw new Error("Systolic pressure must be greater than diastolic pressure.");
        }
        payload.systolic = sys;
        payload.diastolic = dia;
      } else {
        const val = Number(editValue);
        if (isNaN(val)) throw new Error("Value must be a valid number.");

        if (editingRecord.measurementType === "heart_rate" && (val < 30 || val > 250)) {
          throw new Error("Heart rate must be between 30 and 250 BPM.");
        }
        if (editingRecord.measurementType === "spo2" && (val < 0 || val > 100)) {
          throw new Error("SpO2 must be between 0 and 100%.");
        }
        if (editingRecord.measurementType === "body_temperature" && (val < 30 || val > 45)) {
          throw new Error("Temperature must be between 30°C and 45°C.");
        }
        payload.value = val;
      }

      await updateMeasurement(editingRecord.id, payload);
      setEditingRecord(null);
      await loadDashboardData();
    } catch (err: unknown) {
      setEditError(err instanceof Error ? err.message : "Failed to update record.");
    } finally {
      setSavingEdit(false);
    }
  };

  // Delete Action
  const handleConfirmDelete = async () => {
    if (!deletingRecord) return;
    setDeleting(true);
    try {
      await deleteMeasurement(deletingRecord.id);
      setDeletingRecord(null);
      await loadDashboardData();
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to delete record.");
    } finally {
      setDeleting(false);
    }
  };

  // Helper for rendering measurement type labels and tags
  const renderTypeLabel = (type: string) => {
    switch (type) {
      case "heart_rate":
        return <span className="flex items-center gap-1.5"><HeartPulse className="size-3.5 text-signal" /> Heart Rate</span>;
      case "blood_pressure":
        return <span className="flex items-center gap-1.5"><Gauge className="size-3.5 text-warning" /> Blood Pressure</span>;
      case "spo2":
        return <span className="flex items-center gap-1.5"><Droplets className="size-3.5 text-signal" /> Oxygen (SpO₂)</span>;
      case "body_temperature":
        return <span className="flex items-center gap-1.5"><Thermometer className="size-3.5 text-highlight" /> Temperature</span>;
      default:
        return type;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Health Monitoring & Manual Measurement"
        subtitle="Manual biometric data entry, physiological plausibility verification, SQLite database persistence, and longitudinal trend analytics."
        actions={
          <Button variant="outline" size="sm" onClick={loadDashboardData} disabled={loadingData}>
            <RefreshCw className={`size-3.5 mr-1.5 ${loadingData ? "animate-spin" : ""}`} />
            Refresh Data
          </Button>
        }
      />

      {/* Safety Notice Banner */}
      <Notice tone="signal" icon={<ShieldCheck />}>
        <div className="space-y-1">
          <p className="font-medium text-foreground">Manual Health Measurement Mode — No Live Sensor Required</p>
          <p className="text-muted-foreground">
            This system functions entirely via manual data entry and offline dataset uploads without physical IoT or wearable sensors.
            Entries are validated against physiological bounds and persisted to the SQLite database.
            This application is an educational decision-support prototype and does not replace professional clinical evaluation or prescribe medications.
          </p>
        </div>
      </Notice>

      {/* Feedback Messages */}
      {successMsg && (
        <div className="flex items-center gap-2 rounded-md border border-success/40 bg-success/10 px-4 py-3 text-xs text-success">
          <CheckCircle2 className="size-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="flex items-center gap-2 rounded-md border border-warning/50 bg-warning/10 px-4 py-3 text-xs text-warning">
          <AlertTriangle className="size-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Latest Measurement Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {/* Heart Rate Card */}
        <article className="panel flex flex-col p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <HeartPulse className="size-3.5 text-signal" />
              <span>Heart Rate</span>
              <InfoTip text="Resting heart rate in beats per minute. Normal physiological range: 60 - 100 BPM." />
            </div>
            <Tag tone="signal">Manual</Tag>
          </div>
          <div className="mt-4 flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-medium tracking-tight">
              {summary?.heart_rate?.latest?.value ?? "—"}
            </span>
            <span className="text-xs text-muted-foreground">BPM</span>
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-[11px] text-muted-foreground">
            <span className="font-mono">
              {summary?.heart_rate?.latest?.measuredAt ? fmtDateTime(summary.heart_rate.latest.measuredAt) : "No entries yet"}
            </span>
            <Tag tone={summary?.heart_rate?.latest?.dataQualityStatus === "review_required" ? "warning" : "success"}>
              {summary?.heart_rate?.latest ? (summary.heart_rate.latest.dataQualityStatus === "review_required" ? "Review" : "Normal") : "Pending"}
            </Tag>
          </div>
        </article>

        {/* Blood Pressure Card */}
        <article className="panel flex flex-col p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Gauge className="size-3.5 text-warning" />
              <span>Blood Pressure</span>
              <InfoTip text="Systolic over diastolic arterial pressure. Normal target: < 120/80 mmHg." />
            </div>
            <Tag tone="signal">Manual</Tag>
          </div>
          <div className="mt-4 flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-medium tracking-tight">
              {summary?.blood_pressure?.latest ? (
                <>
                  {summary.blood_pressure.latest.systolic}
                  <span className="text-muted-foreground font-sans">/</span>
                  {summary.blood_pressure.latest.diastolic}
                </>
              ) : (
                "—"
              )}
            </span>
            <span className="text-xs text-muted-foreground">mmHg SYS/DIA</span>
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-[11px] text-muted-foreground">
            <span className="font-mono">
              {summary?.blood_pressure?.latest?.measuredAt ? fmtDateTime(summary.blood_pressure.latest.measuredAt) : "No entries yet"}
            </span>
            <Tag tone={summary?.blood_pressure?.latest?.dataQualityStatus === "review_required" ? "warning" : "success"}>
              {summary?.blood_pressure?.latest ? (summary.blood_pressure.latest.dataQualityStatus === "review_required" ? "Review" : "Normal") : "Pending"}
            </Tag>
          </div>
        </article>

        {/* SpO2 Card */}
        <article className="panel flex flex-col p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Droplets className="size-3.5 text-signal" />
              <span>Blood Oxygen</span>
              <InfoTip text="Peripheral blood oxygen saturation (SpO2 percentage). Normal range: 95 - 100%." />
            </div>
            <Tag tone="signal">Manual</Tag>
          </div>
          <div className="mt-4 flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-medium tracking-tight">
              {summary?.spo2?.latest?.value ?? "—"}
            </span>
            <span className="text-xs text-muted-foreground">SpO₂ %</span>
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-[11px] text-muted-foreground">
            <span className="font-mono">
              {summary?.spo2?.latest?.measuredAt ? fmtDateTime(summary.spo2.latest.measuredAt) : "No entries yet"}
            </span>
            <Tag tone={summary?.spo2?.latest?.dataQualityStatus === "review_required" ? "warning" : "success"}>
              {summary?.spo2?.latest ? (summary.spo2.latest.dataQualityStatus === "review_required" ? "Review" : "Normal") : "Pending"}
            </Tag>
          </div>
        </article>

        {/* Temperature Card */}
        <article className="panel flex flex-col p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Thermometer className="size-3.5 text-highlight" />
              <span>Body Temperature</span>
              <InfoTip text="Body core temperature in degrees Celsius (°C). Normal range: 36.1 - 37.2°C." />
            </div>
            <Tag tone="signal">Manual</Tag>
          </div>
          <div className="mt-4 flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-medium tracking-tight">
              {summary?.body_temperature?.latest?.value !== undefined && summary?.body_temperature?.latest?.value !== null
                ? Number(summary.body_temperature.latest.value).toFixed(1)
                : "—"}
            </span>
            <span className="text-xs text-muted-foreground">°C</span>
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-[11px] text-muted-foreground">
            <span className="font-mono">
              {summary?.body_temperature?.latest?.measuredAt ? fmtDateTime(summary.body_temperature.latest.measuredAt) : "No entries yet"}
            </span>
            <Tag tone={summary?.body_temperature?.latest?.dataQualityStatus === "review_required" ? "warning" : "success"}>
              {summary?.body_temperature?.latest ? (summary.body_temperature.latest.dataQualityStatus === "review_required" ? "Review" : "Normal") : "Pending"}
            </Tag>
          </div>
        </article>
      </div>

      {/* Manual Measurement Entry Form */}
      <Panel>
        <PanelHeader
          title="Manual Health Measurement Entry"
          subtitle="Record patient vital signs directly into SQLite. All fields are evaluated against clinical plausibility standards."
          actions={
            <div className="flex items-center gap-2">
              <Tag tone="signal">Source: Manual Entry</Tag>
            </div>
          }
          icon={<PlusCircle />}
        />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {/* Heart Rate */}
            <div>
              <label htmlFor="input-hr" className="block text-xs font-medium text-foreground mb-1.5">
                Heart Rate <span className="text-muted-foreground font-mono">(BPM)</span>
              </label>
              <input
                id="input-hr"
                type="number"
                min="30"
                max="250"
                step="1"
                placeholder="e.g. 72"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.heartRate ? "border-warning" : "border-border"
                }`}
                value={heartRate}
                onChange={(e) => setHeartRate(e.target.value)}
              />
              {clientErrors.heartRate && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.heartRate}</p>
              )}
            </div>

            {/* Systolic BP */}
            <div>
              <label htmlFor="input-sys" className="block text-xs font-medium text-foreground mb-1.5">
                Systolic BP <span className="text-muted-foreground font-mono">(mmHg)</span>
              </label>
              <input
                id="input-sys"
                type="number"
                min="50"
                max="260"
                step="1"
                placeholder="e.g. 120"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.systolic ? "border-warning" : "border-border"
                }`}
                value={systolic}
                onChange={(e) => setSystolic(e.target.value)}
              />
              {clientErrors.systolic && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.systolic}</p>
              )}
            </div>

            {/* Diastolic BP */}
            <div>
              <label htmlFor="input-dia" className="block text-xs font-medium text-foreground mb-1.5">
                Diastolic BP <span className="text-muted-foreground font-mono">(mmHg)</span>
              </label>
              <input
                id="input-dia"
                type="number"
                min="30"
                max="160"
                step="1"
                placeholder="e.g. 80"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.diastolic ? "border-warning" : "border-border"
                }`}
                value={diastolic}
                onChange={(e) => setDiastolic(e.target.value)}
              />
              {clientErrors.diastolic && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.diastolic}</p>
              )}
            </div>

            {/* Oxygen Saturation */}
            <div>
              <label htmlFor="input-spo2" className="block text-xs font-medium text-foreground mb-1.5">
                Oxygen Saturation <span className="text-muted-foreground font-mono">(SpO2 %)</span>
              </label>
              <input
                id="input-spo2"
                type="number"
                min="0"
                max="100"
                step="1"
                placeholder="e.g. 98"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.spo2 ? "border-warning" : "border-border"
                }`}
                value={spo2}
                onChange={(e) => setSpo2(e.target.value)}
              />
              {clientErrors.spo2 && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.spo2}</p>
              )}
            </div>

            {/* Body Temperature */}
            <div>
              <label htmlFor="input-temp" className="block text-xs font-medium text-foreground mb-1.5">
                Temperature <span className="text-muted-foreground font-mono">(°C)</span>
              </label>
              <input
                id="input-temp"
                type="number"
                min="30.0"
                max="45.0"
                step="0.1"
                placeholder="e.g. 36.6"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.temperature ? "border-warning" : "border-border"
                }`}
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
              />
              {clientErrors.temperature && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.temperature}</p>
              )}
            </div>

            {/* Measurement Date and Time */}
            <div>
              <label htmlFor="input-date" className="block text-xs font-medium text-foreground mb-1.5">
                Date & Time <span className="text-muted-foreground font-mono">(Local)</span>
              </label>
              <input
                id="input-date"
                type="datetime-local"
                className={`w-full rounded-md border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-signal ${
                  clientErrors.measuredAt ? "border-warning" : "border-border"
                }`}
                value={measuredAt}
                onChange={(e) => setMeasuredAt(e.target.value)}
              />
              {clientErrors.measuredAt && (
                <p className="mt-1 text-[11px] text-warning">{clientErrors.measuredAt}</p>
              )}
            </div>
          </div>

          {clientErrors.form && (
            <p className="text-xs text-warning">{clientErrors.form}</p>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/60 pt-3">
            <span className="text-xs text-muted-foreground">
              Source: <span className="text-foreground font-mono">Manual Entry</span> · Plausibility Guard: <span className="text-success font-mono">Active</span>
            </span>
            <div className="flex items-center gap-2">
              <Button type="button" variant="outline" size="sm" onClick={handleResetForm} disabled={submitting}>
                <RotateCcw className="size-3.5 mr-1" />
                Reset
              </Button>
              <Button type="submit" size="sm" disabled={submitting} className="bg-primary text-primary-foreground hover:bg-primary/90 font-medium">
                <PlusCircle className="size-3.5 mr-1" />
                {submitting ? "Saving to Database..." : "Save Measurement"}
              </Button>
            </div>
          </div>
        </form>
      </Panel>

      {/* Health Trend Analytics Chart */}
      <Panel>
        <PanelHeader
          title="Health Trend Analytics"
          subtitle="Longitudinal time-series measurements plotted from the SQLite database records."
          actions={
            <div className="flex flex-wrap items-center gap-1.5 rounded-md border border-border bg-surface p-1">
              {(
                [
                  { key: "heartRate", label: "Heart Rate" },
                  { key: "bloodPressure", label: "Blood Pressure" },
                  { key: "spo2", label: "SpO₂" },
                  { key: "temperature", label: "Temperature" },
                ] as const
              ).map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setSelectedMetric(key)}
                  className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                    selectedMetric === key
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          }
        />
        <TrendChart data={trends} metric={selectedMetric} height={280} />
      </Panel>

      {/* Measurement History Table */}
      <Panel>
        <PanelHeader
          title="Measurement History"
          subtitle={`Displaying ${records.length} of ${totalRecords} records stored in the SQLite database.`}
          icon={<Activity />}
        />

        {/* Filter bar */}
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:flex lg:flex-wrap items-center">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="size-3.5" />
            <span>Filters:</span>
          </div>

          <select
            aria-label="Filter by measurement type"
            className="rounded-md border border-border bg-input px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-signal"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="all">All Measurement Types</option>
            <option value="heart_rate">Heart Rate (BPM)</option>
            <option value="blood_pressure">Blood Pressure (mmHg)</option>
            <option value="spo2">Oxygen Saturation (SpO2)</option>
            <option value="body_temperature">Body Temperature (°C)</option>
          </select>

          <div className="flex items-center gap-1.5">
            <span className="text-xs text-muted-foreground">From:</span>
            <input
              type="date"
              aria-label="Start date filter"
              className="rounded-md border border-border bg-input px-2.5 py-1.5 font-mono text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-signal"
              value={filterStartDate}
              onChange={(e) => setFilterStartDate(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-xs text-muted-foreground">To:</span>
            <input
              type="date"
              aria-label="End date filter"
              className="rounded-md border border-border bg-input px-2.5 py-1.5 font-mono text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-signal"
              value={filterEndDate}
              onChange={(e) => setFilterEndDate(e.target.value)}
            />
          </div>

          {(filterType !== "all" || filterStartDate || filterEndDate) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setFilterType("all");
                setFilterStartDate("");
                setFilterEndDate("");
              }}
            >
              Clear Filters
            </Button>
          )}
        </div>

        {/* History Table */}
        {records.length === 0 ? (
          <EmptyState
            title="No measurement records found"
            text="Add a manual measurement using the form above or widen the date filter range."
          />
        ) : (
          <div className="overflow-x-auto rounded-md border border-border">
            <table className="w-full min-w-[700px] text-left text-xs">
              <thead className="bg-surface text-muted-foreground">
                <tr>
                  <th className="px-3 py-2.5 font-medium font-mono">ID</th>
                  <th className="px-3 py-2.5 font-medium">Type</th>
                  <th className="px-3 py-2.5 font-medium">Measurement Value</th>
                  <th className="px-3 py-2.5 font-medium font-mono">Timestamp</th>
                  <th className="px-3 py-2.5 font-medium">Source</th>
                  <th className="px-3 py-2.5 font-medium">Quality</th>
                  <th className="px-3 py-2.5 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id} className="border-t border-border/70 transition-colors hover:bg-surface/50">
                    <td className="px-3 py-2.5 font-mono text-muted-foreground">#{r.id}</td>
                    <td className="px-3 py-2.5">{renderTypeLabel(r.measurementType)}</td>
                    <td className="px-3 py-2.5 font-mono font-medium text-foreground">
                      {r.measurementType === "blood_pressure" ? (
                        <>
                          {r.systolic}/{r.diastolic} <span className="text-muted-foreground text-[11px] font-normal">{r.unit}</span>
                        </>
                      ) : (
                        <>
                          {r.value} <span className="text-muted-foreground text-[11px] font-normal">{r.unit}</span>
                        </>
                      )}
                    </td>
                    <td className="px-3 py-2.5 font-mono text-muted-foreground">{fmtDateTime(r.measuredAt)}</td>
                    <td className="px-3 py-2.5">
                      <Tag tone={r.source === "manual" ? "signal" : "neutral"}>
                        {r.source === "manual" ? "Manual Entry" : r.source}
                      </Tag>
                    </td>
                    <td className="px-3 py-2.5">
                      <Tag tone={r.dataQualityStatus === "review_required" ? "warning" : "success"} dot>
                        {r.dataQualityStatus === "review_required" ? "Review required" : "Valid"}
                      </Tag>
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOpenEdit(r)}
                          className="h-7 px-2 text-xs"
                        >
                          <Edit2 className="size-3 mr-1" />
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeletingRecord(r)}
                          className="h-7 px-2 text-xs text-warning hover:text-warning"
                        >
                          <Trash2 className="size-3 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Edit Measurement Dialog */}
      <Dialog open={!!editingRecord} onOpenChange={(open) => !open && setEditingRecord(null)}>
        <DialogContent className="sm:max-w-md bg-card border-border">
          <DialogHeader>
            <DialogTitle>Edit Measurement Record #{editingRecord?.id}</DialogTitle>
            <DialogDescription>
              Update measurement value and timestamp safely in SQLite.
            </DialogDescription>
          </DialogHeader>

          {editError && (
            <div className="rounded border border-warning/40 bg-warning/10 p-2 text-xs text-warning">
              {editError}
            </div>
          )}

          <div className="space-y-3 py-2">
            {editingRecord?.measurementType === "blood_pressure" ? (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Systolic (mmHg)</label>
                  <input
                    type="number"
                    className="w-full rounded border border-border bg-input px-3 py-1.5 font-mono text-sm"
                    value={editSystolic}
                    onChange={(e) => setEditSystolic(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">Diastolic (mmHg)</label>
                  <input
                    type="number"
                    className="w-full rounded border border-border bg-input px-3 py-1.5 font-mono text-sm"
                    value={editDiastolic}
                    onChange={(e) => setEditDiastolic(e.target.value)}
                  />
                </div>
              </div>
            ) : (
              <div>
                <label className="block text-xs font-medium mb-1">
                  Value ({editingRecord?.unit})
                </label>
                <input
                  type="number"
                  step="any"
                  className="w-full rounded border border-border bg-input px-3 py-1.5 font-mono text-sm"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium mb-1">Measurement Date & Time</label>
              <input
                type="datetime-local"
                className="w-full rounded border border-border bg-input px-3 py-1.5 font-mono text-sm"
                value={editMeasuredAt}
                onChange={(e) => setEditMeasuredAt(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button variant="outline" size="sm" onClick={() => setEditingRecord(null)} disabled={savingEdit}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleSaveEdit} disabled={savingEdit} className="bg-primary text-primary-foreground">
              {savingEdit ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deletingRecord} onOpenChange={(open) => !open && setDeletingRecord(null)}>
        <DialogContent className="sm:max-w-md bg-card border-border">
          <DialogHeader>
            <DialogTitle>Confirm Delete Measurement</DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete record #{deletingRecord?.id} ({deletingRecord?.measurementType}) from the SQLite database?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" size="sm" onClick={() => setDeletingRecord(null)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="destructive" size="sm" onClick={handleConfirmDelete} disabled={deleting}>
              {deleting ? "Deleting..." : "Delete Permanently"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
