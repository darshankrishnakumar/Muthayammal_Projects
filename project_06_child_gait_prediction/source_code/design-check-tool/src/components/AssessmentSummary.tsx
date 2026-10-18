import type { GaitInput } from "@/services/api";

interface AssessmentSummaryProps {
  data: Partial<GaitInput> & {
    childId?: string;
    age?: number;
    gender?: string;
    date?: string;
  };
  title?: string;
  className?: string;
}

export const PARAM_DEFINITIONS = [
  { key: "heelPressure", label: "Heel Pressure", unit: " kPa", range: "120 - 240 kPa" },
  { key: "toePressure", label: "Toe Pressure", unit: " kPa", range: "90 - 210 kPa" },
  { key: "tiltAngle", label: "Tilt Angle", unit: "°", range: "0 - 15°" },
  { key: "stepDuration", label: "Step Duration", unit: " s", range: "0.4 - 0.7 s" },
  { key: "strideLength", label: "Stride Length", unit: " cm", range: "60 - 120 cm" },
  { key: "walkingSpeed", label: "Walking Speed", unit: " m/s", range: "0.8 - 1.4 m/s" },
] as const;

export function AssessmentSummary({
  data,
  title = "Assessment Summary",
  className = "",
}: AssessmentSummaryProps) {
  return (
    <div className={`rounded-xl border border-border bg-card p-5 sm:p-6 shadow-xs ${className}`}>
      <div className="flex flex-col justify-between gap-1 border-b border-border pb-3 sm:flex-row sm:items-center">
        <h3 className="font-semibold text-foreground text-base">{title}</h3>
        {data.date && (
          <span className="text-xs text-muted-foreground">
            Recorded: {new Date(data.date).toLocaleDateString()}
          </span>
        )}
      </div>

      {/* Child Information Header */}
      {(data.childId || data.age !== undefined || data.gender) && (
        <div className="grid grid-cols-3 gap-3 border-b border-border py-3 text-xs">
          <div>
            <span className="text-muted-foreground block">Child ID</span>
            <span className="font-semibold text-foreground">{data.childId || "—"}</span>
          </div>
          <div>
            <span className="text-muted-foreground block">Age</span>
            <span className="font-semibold text-foreground">
              {data.age !== undefined ? `${data.age} yrs` : "—"}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground block">Gender</span>
            <span className="font-semibold text-foreground">{data.gender || "—"}</span>
          </div>
        </div>
      )}

      {/* Submitted Gait Parameters */}
      <div className="mt-4">
        <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Submitted Gait Parameters
        </p>
        <dl className="grid gap-x-6 gap-y-2.5 text-sm sm:grid-cols-2">
          {PARAM_DEFINITIONS.map((p) => {
            const val = data[p.key as keyof GaitInput];
            const displayVal =
              val !== undefined && val !== null && val !== "" ? `${val}${p.unit}` : "—";
            return (
              <div
                key={p.key}
                className="flex items-center justify-between border-b border-border/50 py-1.5"
              >
                <dt className="text-xs text-muted-foreground">{p.label}</dt>
                <dd className="font-mono text-xs font-semibold text-foreground">{displayVal}</dd>
              </div>
            );
          })}
        </dl>
      </div>
    </div>
  );
}
