import { Activity, BarChart3, BrainCircuit, FileText, History, LayoutGrid, Lightbulb, Settings, Waves } from "lucide-react";

export const navItems = [
  { to: "/", label: "Overview", icon: LayoutGrid },
  { to: "/monitoring", label: "Health Monitoring", icon: Activity },
  { to: "/ecg", label: "ECG Analysis", icon: Waves },
  { to: "/predictions", label: "AI Predictions", icon: BrainCircuit },
  { to: "/recommendations", label: "Recommendations", icon: Lightbulb },
  { to: "/history", label: "Health History", icon: History },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export const unusedIcon = BarChart3;
