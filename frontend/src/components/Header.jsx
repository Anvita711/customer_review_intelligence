import { Activity, BarChart3, Brain } from "lucide-react";

export default function Header({ hasResults, onReset }) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo / Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 shadow-sm">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold leading-tight text-slate-900">
              Review Intelligence
            </h1>
            <p className="text-[11px] font-medium leading-none text-slate-400">
              Customer Feedback Analytics
            </p>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {hasResults && (
            <button onClick={onReset} className="btn-secondary text-xs">
              <BarChart3 className="h-3.5 w-3.5" />
              New Analysis
            </button>
          )}
          <div className="flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5">
            <Activity className="h-3 w-3 text-emerald-600" />
            <span className="text-xs font-medium text-emerald-700">
              System Online
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
