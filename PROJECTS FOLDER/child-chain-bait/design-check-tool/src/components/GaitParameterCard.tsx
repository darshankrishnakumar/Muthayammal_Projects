import type { LucideIcon } from "lucide-react";

interface GaitParameterCardProps {
  label: string;
  value: number | string;
  unit?: string;
  description?: string;
  icon?: LucideIcon;
  normalRange?: string;
}

export function GaitParameterCard({
  label,
  value,
  unit = "",
  description,
  icon: Icon,
  normalRange,
}: GaitParameterCardProps) {
  return (
    <div className="flex flex-col justify-between rounded-xl border border-border bg-card p-4 shadow-xs transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        {Icon && <Icon className="h-4 w-4 text-medical-foreground" />}
      </div>
      <div className="mt-2 flex items-baseline gap-1">
        <span className="text-xl font-bold tracking-tight text-foreground">{value}</span>
        {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
      </div>
      {(normalRange || description) && (
        <div className="mt-2 border-t border-border/50 pt-2 text-[11px] text-muted-foreground">
          {normalRange && <span className="block">Ref Range: {normalRange}</span>}
          {description && <span className="block">{description}</span>}
        </div>
      )}
    </div>
  );
}
