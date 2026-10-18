import { Car, Brain, Sparkles, Database, History } from 'lucide-react';
import { formatMethodName } from '../types';

interface HeaderProps {
  activeModelName?: string;
  onOpenDataset: () => void;
  onOpenBenchmarks: () => void;
  onOpenHistory: () => void;
  historyCount?: number;
}

export function Header({
  activeModelName = 'Random Forest Regression',
  onOpenDataset,
  onOpenBenchmarks,
  onOpenHistory,
  historyCount = 0,
}: HeaderProps) {
  return (
    <header id="app-header" className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Car className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">Car Price Prediction System</h1>
              <span className="hidden sm:inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Valuation Engine Active
              </span>
            </div>
            <p className="text-xs text-slate-500">Smart Automotive Valuation Engine &bull; Market Analytics</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            id="view-history-btn"
            onClick={onOpenHistory}
            type="button"
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-50/50 text-blue-700 hover:bg-blue-100/70 transition-colors cursor-pointer"
          >
            <History className="w-3.5 h-3.5 text-blue-600" />
            <span className="whitespace-nowrap">History</span>
            {historyCount > 0 && (
              <span className="ml-0.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-blue-600 text-white">
                {historyCount}
              </span>
            )}
          </button>

          <button
            id="view-benchmarks-btn"
            onClick={onOpenBenchmarks}
            type="button"
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <Brain className="w-3.5 h-3.5 text-blue-600" />
            <span className="whitespace-nowrap">Valuation Benchmarks</span>
          </button>

          <button
            id="view-dataset-btn"
            onClick={onOpenDataset}
            type="button"
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <Database className="w-3.5 h-3.5 text-emerald-600" />
            <span className="whitespace-nowrap">Explore Dataset</span>
          </button>

          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-xs text-slate-600">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span className="font-medium text-slate-800">{formatMethodName(activeModelName)}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
