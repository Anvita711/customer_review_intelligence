import {
  AlertOctagon,
  AlertTriangle,
  Info,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const SEV = {
  critical: {
    icon: AlertOctagon,
    badge: "badge-critical",
    border: "border-red-200",
    bg: "bg-red-50/40",
    ring: "ring-red-100",
    label: "Critical",
  },
  high: {
    icon: AlertTriangle,
    badge: "badge-high",
    border: "border-orange-200",
    bg: "bg-orange-50/40",
    ring: "ring-orange-100",
    label: "High",
  },
  medium: {
    icon: Info,
    badge: "badge-medium",
    border: "border-amber-200",
    bg: "bg-amber-50/30",
    ring: "ring-amber-100",
    label: "Medium",
  },
  low: {
    icon: CheckCircle,
    badge: "badge-low",
    border: "border-emerald-200",
    bg: "bg-emerald-50/30",
    ring: "ring-emerald-100",
    label: "Low",
  },
};

function TrendArrow({ direction }) {
  if (direction === "increasing" || direction === "spike")
    return <ArrowUpRight className="h-3.5 w-3.5 text-red-500" />;
  if (direction === "decreasing" || direction === "drop")
    return <ArrowDownRight className="h-3.5 w-3.5 text-emerald-500" />;
  return <Minus className="h-3.5 w-3.5 text-slate-400" />;
}

function RecCard({ rec }) {
  const [open, setOpen] = useState(
    rec.severity === "critical" || rec.severity === "high",
  );
  const meta = SEV[rec.severity] || SEV.low;
  const SevIcon = meta.icon;

  return (
    <div
      className={clsx(
        "rounded-xl border transition-shadow",
        meta.border,
        open ? meta.bg : "bg-white",
        "hover:shadow-sm",
      )}
    >
      {/* Header row — always visible */}
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-3 px-4 py-3.5 text-left"
      >
        <SevIcon
          className={clsx(
            "h-5 w-5 shrink-0",
            rec.severity === "critical"
              ? "text-red-600"
              : rec.severity === "high"
                ? "text-orange-500"
                : rec.severity === "medium"
                  ? "text-amber-500"
                  : "text-emerald-500",
          )}
        />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className={clsx("badge", meta.badge)}>{meta.label}</span>
            <span className="text-sm font-semibold capitalize text-slate-800">
              {rec.feature.replace(/_/g, " ")}
            </span>
            <span className="flex items-center gap-0.5 text-xs text-slate-500">
              <TrendArrow direction={rec.trend_direction} />
              {rec.previous_pct}% &rarr; {rec.current_pct}%
            </span>
          </div>
          <p className="mt-0.5 line-clamp-1 text-xs text-slate-500">
            {rec.summary}
          </p>
        </div>
        {open ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-slate-400" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-slate-400" />
        )}
      </button>

      {/* Expanded body */}
      {open && (
        <div className="border-t border-slate-100 px-4 pb-4 pt-3">
          <div className="grid gap-3 sm:grid-cols-3">
            <Detail label="Classification" value={rec.classification} />
            <Detail label="Trend Direction" value={rec.trend_direction} />
            <Detail
              label="Change"
              value={`${Math.abs(rec.current_pct - rec.previous_pct).toFixed(1)} pp`}
            />
          </div>
          <div className="mt-3 rounded-lg bg-slate-50 px-3.5 py-3">
            <p className="text-xs font-semibold text-slate-700">
              Recommended Action
            </p>
            <p className="mt-1 text-xs leading-relaxed text-slate-600">
              {rec.action}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <p className="text-[11px] font-medium text-slate-400">{label}</p>
      <p className="text-xs font-semibold capitalize text-slate-700">
        {value}
      </p>
    </div>
  );
}

export default function Recommendations({ insightReport }) {
  if (!insightReport?.recommendations?.length) return null;

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "420ms" }}>
      <div className="card-header">
        <h3 className="text-sm font-semibold text-slate-800">
          Prioritized Recommendations
        </h3>
        <p className="mt-0.5 text-xs text-slate-400">
          Actions ranked by severity — critical items expanded by default
        </p>
      </div>
      <div className="card-body space-y-2">
        {insightReport.recommendations.map((rec, i) => (
          <RecCard key={`${rec.feature}-${i}`} rec={rec} />
        ))}
      </div>
    </div>
  );
}
