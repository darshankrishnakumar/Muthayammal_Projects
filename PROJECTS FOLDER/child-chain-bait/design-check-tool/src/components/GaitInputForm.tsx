import { useState, type FormEvent } from "react";
import { Loader2, Footprints, User, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { GaitInput } from "@/services/api";

interface GaitInputFormProps {
  onSubmit: (input: GaitInput) => Promise<void>;
  loading: boolean;
}

export const PARAM_INPUTS = [
  {
    key: "heelPressure" as const,
    label: "Heel Pressure",
    unit: "kPa",
    placeholder: "e.g. 180",
    min: 1,
    max: 1000,
    hint: "Peak pressure at heel strike phase",
  },
  {
    key: "toePressure" as const,
    label: "Toe Pressure",
    unit: "kPa",
    placeholder: "e.g. 145",
    min: 1,
    max: 1000,
    hint: "Peak pressure during toe-off phase",
  },
  {
    key: "tiltAngle" as const,
    label: "Tilt Angle",
    unit: "°",
    placeholder: "e.g. 6.5",
    min: 0,
    max: 90,
    step: "0.1",
    hint: "Coronal/sagittal foot tilt deviation",
  },
  {
    key: "stepDuration" as const,
    label: "Step Duration",
    unit: "s",
    placeholder: "e.g. 0.52",
    min: 0.1,
    max: 5,
    step: "0.01",
    hint: "Time elapsed from initial contact to next contact",
  },
  {
    key: "strideLength" as const,
    label: "Stride Length",
    unit: "cm",
    placeholder: "e.g. 84",
    min: 10,
    max: 250,
    step: "0.5",
    hint: "Distance between consecutive contacts of the same foot",
  },
  {
    key: "walkingSpeed" as const,
    label: "Walking Speed",
    unit: "m/s",
    placeholder: "e.g. 1.05",
    min: 0.1,
    max: 5,
    step: "0.01",
    hint: "Mean linear velocity during the gait cycle",
  },
];

export function GaitInputForm({ onSubmit, loading }: GaitInputFormProps) {
  const [childId, setChildId] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");

  const [params, setParams] = useState<Record<string, string>>({
    heelPressure: "",
    toePressure: "",
    tiltAngle: "",
    stepDuration: "",
    strideLength: "",
    walkingSpeed: "",
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  const handleParamChange = (key: string, val: string) => {
    setParams((prev) => ({ ...prev, [key]: val }));
    setValidationError(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validation
    if (!childId.trim()) {
      setValidationError("Please enter a valid Child ID.");
      return;
    }
    const ageNum = Number(age);
    if (!age || isNaN(ageNum) || ageNum <= 0 || ageNum > 18) {
      setValidationError("Please enter a valid Age between 1 and 18.");
      return;
    }
    if (!gender) {
      setValidationError("Please select a Gender.");
      return;
    }

    for (const p of PARAM_INPUTS) {
      const val = Number(params[p.key]);
      if (params[p.key] === "" || isNaN(val) || val <= 0) {
        setValidationError(`Please enter a valid positive numeric value for ${p.label}.`);
        return;
      }
    }

    const payload: GaitInput = {
      childId: childId.trim(),
      age: ageNum,
      gender,
      heelPressure: Number(params["heelPressure"]),
      toePressure: Number(params["toePressure"]),
      tiltAngle: Number(params["tiltAngle"]),
      stepDuration: Number(params["stepDuration"]),
      strideLength: Number(params["strideLength"]),
      walkingSpeed: Number(params["walkingSpeed"]),
    };

    await onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-xs"
    >
      {/* Form Header */}
      <div className="border-b border-border pb-5">
        <h2 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
          Child Gait Assessment
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Enter the child's gait parameters to generate a machine learning prediction.
        </p>
      </div>

      {validationError && (
        <div className="mt-5 rounded-lg border border-destructive/30 bg-destructive/10 p-3.5 text-xs font-medium text-destructive">
          {validationError}
        </div>
      )}

      {/* Section 1: Child Information */}
      <div className="mt-6">
        <div className="mb-4 flex items-center gap-2">
          <User className="h-4 w-4 text-medical-foreground" />
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Child Information
          </h3>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="childId" className="mb-1.5 block text-xs font-medium text-foreground">
              Child ID <span className="text-destructive">*</span>
            </label>
            <input
              id="childId"
              type="text"
              required
              disabled={loading}
              placeholder="e.g. C-104"
              value={childId}
              onChange={(e) => {
                setChildId(e.target.value);
                setValidationError(null);
              }}
              className="w-full rounded-lg border border-input bg-card px-3.5 py-2 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
            />
          </div>

          <div>
            <label htmlFor="age" className="mb-1.5 block text-xs font-medium text-foreground">
              Age (Years) <span className="text-destructive">*</span>
            </label>
            <input
              id="age"
              type="number"
              min={1}
              max={18}
              required
              disabled={loading}
              placeholder="e.g. 7"
              value={age}
              onChange={(e) => {
                setAge(e.target.value);
                setValidationError(null);
              }}
              className="w-full rounded-lg border border-input bg-card px-3.5 py-2 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
            />
          </div>

          <div>
            <label htmlFor="gender" className="mb-1.5 block text-xs font-medium text-foreground">
              Gender <span className="text-destructive">*</span>
            </label>
            <select
              id="gender"
              required
              disabled={loading}
              value={gender}
              onChange={(e) => {
                setGender(e.target.value);
                setValidationError(null);
              }}
              className="w-full rounded-lg border border-input bg-card px-3.5 py-2 text-sm text-foreground outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
            >
              <option value="" disabled>
                Select Gender
              </option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>
      </div>

      {/* Section 2: Gait Parameters */}
      <div className="mt-8 border-t border-border pt-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Footprints className="h-4 w-4 text-medical-foreground" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Gait Parameters
            </h3>
          </div>
          <span className="text-xs text-muted-foreground hidden sm:inline">
            Measurable biomechanical sensors
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PARAM_INPUTS.map((p) => (
            <div key={p.key} className="flex flex-col">
              <label
                htmlFor={p.key}
                className="mb-1.5 flex items-center justify-between text-xs font-medium text-foreground"
              >
                <span>
                  {p.label} <span className="text-destructive">*</span>
                </span>
                <span className="text-[11px] text-muted-foreground font-mono">({p.unit})</span>
              </label>
              <input
                id={p.key}
                type="number"
                step={p.step ?? "any"}
                min={p.min}
                max={p.max}
                required
                disabled={loading}
                placeholder={p.placeholder}
                value={params[p.key]}
                onChange={(e) => handleParamChange(p.key, e.target.value)}
                className="w-full rounded-lg border border-input bg-card px-3.5 py-2 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
              />
              <span className="mt-1 text-[11px] text-muted-foreground flex items-center gap-1">
                <HelpCircle className="h-3 w-3 shrink-0 opacity-60" /> {p.hint}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button & Status */}
      <div className="mt-8 flex flex-col items-center justify-between gap-4 border-t border-border pt-6 sm:flex-row">
        <p className="text-xs text-muted-foreground">
          Parameters are evaluated against the trained multi-class classification model.
        </p>
        <Button
          type="submit"
          disabled={loading}
          size="lg"
          className="w-full sm:w-auto min-w-[170px] shadow-xs cursor-pointer font-medium"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing gait parameters…</span>
            </>
          ) : (
            "Predict Gait"
          )}
        </Button>
      </div>
    </form>
  );
}
