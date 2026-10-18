import type { ReactNode } from "react";
import { Info, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";

export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return <section className={cn("panel p-5", className)}>{children}</section>;
}

export function PanelHeader({ title, subtitle, actions, icon }: { title: string; subtitle?: ReactNode; actions?: ReactNode; icon?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0">
        <h2 className="flex items-center gap-2 text-sm font-medium text-foreground">
          {icon && <span className="text-muted-foreground [&_svg]:size-4">{icon}</span>}
          {title}
        </h2>
        {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

type Tone = "neutral" | "signal" | "success" | "warning" | "highlight" | "disabled";
const tones: Record<Tone, string> = {
  neutral: "border-border text-muted-foreground",
  signal: "border-signal/40 text-signal bg-signal/5",
  success: "border-success/40 text-success bg-success/5",
  warning: "border-warning/50 text-warning bg-warning/5",
  highlight: "border-highlight/40 text-highlight bg-highlight/5",
  disabled: "border-border text-disabled",
};

export function Tag({ tone = "neutral", children, dot }: { tone?: Tone; children: ReactNode; dot?: boolean }) {
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-sm border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider", tones[tone])}>
      {dot && <span className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}

export const DemoBadge = ({ label = "Demo data" }: { label?: string }) => <Tag tone="highlight">{label}</Tag>;

export function InfoTip({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex">
      <button type="button" aria-label={text} className="text-disabled transition-colors hover:text-muted-foreground focus-visible:text-signal">
        <Info className="size-3.5" />
      </button>
      <span role="tooltip" className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 w-56 -translate-x-1/2 rounded-md border border-border bg-popover p-2 text-xs normal-case leading-relaxed tracking-normal text-popover-foreground opacity-0 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100">
        {text}
      </span>
    </span>
  );
}

export function EmptyState({ title, text, icon }: { title: string; text?: string; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-md border border-dashed border-border px-6 py-10 text-center">
      <span className="mb-3 text-disabled [&_svg]:size-6">{icon ?? <Inbox />}</span>
      <p className="text-sm font-medium">{title}</p>
      {text && <p className="mt-1 max-w-sm text-xs text-muted-foreground">{text}</p>}
    </div>
  );
}

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-xl font-semibold tracking-tight md:text-2xl">{title}</h1>
        {subtitle && <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Notice({ tone = "neutral", children, icon }: { tone?: "neutral" | "warning" | "signal"; children: ReactNode; icon?: ReactNode }) {
  return (
    <div className={cn("flex items-start gap-2.5 rounded-md border px-3 py-2.5 text-xs leading-relaxed",
      tone === "warning" ? "border-warning/40 bg-warning/5 text-foreground" : tone === "signal" ? "border-signal/30 bg-signal/5 text-foreground" : "border-border bg-surface text-muted-foreground")}>
      <span className={cn("mt-0.5 [&_svg]:size-3.5", tone === "warning" ? "text-warning" : tone === "signal" ? "text-signal" : "text-muted-foreground")}>{icon ?? <Info />}</span>
      <div>{children}</div>
    </div>
  );
}

export function KV({ k, v }: { k: string; v: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-border/60 py-2 text-xs last:border-0">
      <dt className="text-muted-foreground">{k}</dt>
      <dd className="text-right font-mono text-foreground">{v}</dd>
    </div>
  );
}

export function Segmented<T extends string>({ value, onChange, options, label }: { value: T; onChange: (v: T) => void; options: { value: T; label: string }[]; label: string }) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-md border border-border bg-input p-0.5">
      {options.map((o) => (
        <button key={o.value} type="button" role="radio" aria-checked={value === o.value} onClick={() => onChange(o.value)}
          className={cn("rounded-sm px-2.5 py-1 text-xs transition-colors", value === o.value ? "bg-surface-raised text-signal" : "text-muted-foreground hover:text-foreground")}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function BioMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" aria-hidden="true">
      <rect x="1.5" y="1.5" width="29" height="29" rx="4" stroke="currentColor" strokeOpacity=".35" />
      <path d="M4 17h6l2-5 3 10 3-14 2.5 9H28" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
