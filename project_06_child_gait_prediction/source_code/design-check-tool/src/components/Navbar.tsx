import { Link } from "@tanstack/react-router";
import { Activity, Menu, X } from "lucide-react";
import { useState } from "react";

const navItems = [
  { to: "/", label: "Home", exact: true },
  { to: "/predict", label: "Prediction", exact: false },
  { to: "/history", label: "Gait History", exact: false },
  { to: "/reports", label: "Reports", exact: false },
  { to: "/recommendations", label: "AI Recommendations", exact: false },
  { to: "/about", label: "About", exact: false },
];

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const linkBase =
    "text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-md hover:bg-muted/60";
  const activeProps = {
    className:
      "text-sm font-semibold text-foreground bg-primary/30 border border-primary/40 px-3 py-1.5 rounded-md",
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-card/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-90">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-medical-border bg-medical text-medical-foreground shadow-xs">
            <Activity className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold tracking-tight text-foreground text-base">
              Child Gait AI
            </span>
            <span className="text-[10px] text-muted-foreground -mt-0.5 tracking-wider uppercase">
              ML Prototype
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav aria-label="Main Navigation" className="hidden items-center gap-1 md:flex">
          {navItems.map((item) =>
            item.exact ? (
              <Link
                key={item.to}
                to={item.to}
                className={linkBase}
                activeProps={activeProps}
                activeOptions={{ exact: true }}
              >
                {item.label}
              </Link>
            ) : (
              <Link key={item.to} to={item.to} className={linkBase} activeProps={activeProps}>
                {item.label}
              </Link>
            ),
          )}
        </nav>

        {/* Mobile Hamburger Button */}
        <button
          type="button"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((prev) => !prev)}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-foreground hover:bg-muted md:hidden"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileOpen && (
        <div className="border-b border-border bg-card px-4 pt-2 pb-4 shadow-md md:hidden">
          <nav className="flex flex-col gap-1">
            {navItems.map((item) =>
              item.exact ? (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  activeProps={{
                    className:
                      "rounded-md bg-primary/30 font-semibold text-foreground px-3 py-2 text-sm border border-primary/40",
                  }}
                  activeOptions={{ exact: true }}
                >
                  {item.label}
                </Link>
              ) : (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  activeProps={{
                    className:
                      "rounded-md bg-primary/30 font-semibold text-foreground px-3 py-2 text-sm border border-primary/40",
                  }}
                >
                  {item.label}
                </Link>
              ),
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
