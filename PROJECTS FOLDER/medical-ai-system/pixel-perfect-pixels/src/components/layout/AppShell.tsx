import { useEffect, useState, type ReactNode } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { Bell, ChevronRight, Menu, Search, User, X } from "lucide-react";
import { navItems } from "@/components/navigation/nav";
import { BioMark } from "@/components/common";
import { cn } from "@/lib/utils";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { demoAlerts } from "@/data/demoMeasurements";

function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center gap-2.5 border-b border-border px-5">
        <BioMark className="size-7 text-signal" />
        <span className="text-sm font-semibold tracking-[0.2em]">BIOPULSE</span>
      </div>
      <nav aria-label="Primary" className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
        {navItems.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} onClick={onNavigate} activeOptions={{ exact: to === "/" }}
            className="group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm text-sidebar-foreground transition-colors hover:bg-surface hover:text-foreground"
            activeProps={{ className: "bg-surface !text-foreground before:absolute before:left-0 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-signal [&_svg]:!text-signal" }}>
            <Icon className="size-4 text-disabled transition-colors group-hover:text-muted-foreground" strokeWidth={1.75} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="border-t border-border p-4">
        <p className="label-caps mb-2.5">System status</p>
        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between"><span className="text-muted-foreground">Monitoring System</span><span className="flex items-center gap-1.5 text-foreground"><span className="size-1.5 rounded-full bg-success" />Interface Ready</span></div>
          <div className="flex items-center justify-between"><span className="text-muted-foreground">Sensors</span><span className="text-disabled">Not connected</span></div>
        </div>
      </div>
    </div>
  );
}

function Clock() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => { setNow(new Date()); const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  if (!now) return <span className="w-36" />;
  return (
    <time className="hidden font-mono text-xs text-muted-foreground lg:block" dateTime={now.toISOString()}>
      {now.toLocaleDateString("en-GB", { weekday: "short", day: "2-digit", month: "short", year: "numeric" })} · {now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}
    </time>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const current = navItems.find((n) => (n.to === "/" ? pathname === "/" : pathname.startsWith(n.to))) ?? navItems[0];
  const matches = query ? navItems.filter((n) => n.label.toLowerCase().includes(query.toLowerCase())) : [];

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-60 border-r border-border bg-sidebar lg:block">
        <SidebarNav />
      </aside>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button aria-label="Close navigation" className="absolute inset-0 bg-input/80" onClick={() => setOpen(false)} />
          <aside className="relative h-full w-64 border-r border-border bg-sidebar animate-in slide-in-from-left duration-200">
            <button aria-label="Close" onClick={() => setOpen(false)} className="absolute right-3 top-4 text-muted-foreground"><X className="size-5" /></button>
            <SidebarNav onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}
      <div className="lg:pl-60">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/95 px-4 backdrop-blur md:px-6">
          <button aria-label="Open navigation" className="-ml-1 rounded-md p-1.5 text-muted-foreground hover:bg-surface lg:hidden" onClick={() => setOpen(true)}><Menu className="size-5" /></button>
          <div className="min-w-0 flex-1">
            <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <Link to="/" className="hover:text-foreground">BioPulse</Link>
              <ChevronRight className="size-3" />
              <span className="truncate text-foreground">{current.label}</span>
            </nav>
          </div>
          <Clock />
          <div className="relative hidden md:block">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-disabled" />
            <input aria-label="Search pages" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search pages…" className="field h-8 w-48 pl-8 text-xs" />
            {query && (
              <div className="absolute right-0 top-full mt-1 w-56 rounded-md border border-border bg-popover p-1 text-sm">
                {matches.length ? matches.map((m) => (
                  <Link key={m.to} to={m.to} onClick={() => setQuery("")} className="block rounded-sm px-2 py-1.5 hover:bg-surface-raised">{m.label}</Link>
                )) : <p className="px-2 py-1.5 text-xs text-muted-foreground">No matching pages</p>}
              </div>
            )}
          </div>
          <Popover>
            <PopoverTrigger aria-label="Notifications" className="relative rounded-md p-2 text-muted-foreground hover:bg-surface hover:text-foreground">
              <Bell className="size-4" /><span className="absolute right-1.5 top-1.5 size-1.5 rounded-full bg-warning" />
            </PopoverTrigger>
            <PopoverContent align="end" className="w-80 border-border bg-popover p-0">
              <p className="label-caps border-b border-border px-4 py-2.5">Notifications</p>
              {demoAlerts.map((a) => (
                <div key={a.id} className="border-b border-border/60 px-4 py-3 text-xs last:border-0">
                  <p className="font-medium">{a.category}</p><p className="mt-0.5 text-muted-foreground">{a.description}</p>
                </div>
              ))}
            </PopoverContent>
          </Popover>
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-md border border-border px-2 py-1 text-xs hover:bg-surface">
              <span className="grid size-6 place-items-center rounded-sm bg-surface-raised"><User className="size-3.5 text-muted-foreground" /></span>
              <span className="hidden sm:inline">Demo User</span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 border-border bg-popover">
              <DropdownMenuLabel className="text-xs">Demonstration profile<p className="font-normal text-muted-foreground">No authentication in this version</p></DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild><Link to="/settings">Settings</Link></DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className={cn("mx-auto w-full max-w-[1440px] px-4 py-6 md:px-6 md:py-8")}>{children}</main>
      </div>
    </div>
  );
}
