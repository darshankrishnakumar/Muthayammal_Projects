import type { ReactNode } from "react";
export { Navbar } from "./Navbar";
export { Footer } from "./Footer";
export { MedicalDisclaimer } from "./MedicalDisclaimer";

export function Page({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <main className={`fade-in mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 ${className}`}>
      {children}
    </main>
  );
}
