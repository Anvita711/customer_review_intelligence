import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from "recharts";
import { TrendingUp, TrendingDown, Minus, Zap, AlertTriangle } from "lucide-react";
import clsx from "clsx";

const directionMeta = {
  increasing: { icon: TrendingUp, color: "text-red-600", bg: "bg-red-50" },
  decreasing: { icon: TrendingDown, color: "text-emerald-600", bg: "bg-emerald-50" },
  stable: { icon: Minus, color: "text-slate-500", bg: "bg-slate-100" },
  spike: { icon: Zap, color: "text-red-600", bg: "bg-red-50" },
  drop: { icon: TrendingDown, color: "text-emerald-600", bg: "bg-emerald-50" },
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-xs shadow-lg">
      <p className="mb-1 font-semibold capitalize text-slate-800">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: p.fill }}
            />
            {p.dataKey === "prev" ? "Previous" : "Current"}
          </span>
          <span className="font-semibold">{p.value}%</span>
        </div>
      ))}
    </div>
  );
};

export default function TrendChart({ trendReport }) {
  if (!trendReport?.feature_trends?.length) return null;

  const chartData = trendReport.feature_trends.map((ft) => ({
    feature: ft.feature.replace(/_/g, " "),
    prev: ft.previous_window_pct,
    curr: ft.current_window_pct,
    direction: ft.direction,
    anomaly: ft.is_anomaly,
    classification: ft.classification,
  }));

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "360ms" }}>
      <div className="card-header flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-800">
            Complaint Trend Analysis
          </h3>
          <p className="mt-0.5 text-xs text-slate-400">
            Negative mention rate: previous window vs. current window
            (size&nbsp;{trendReport.window_size})
          </p>
        </div>
      </div>
      <div className="card-body space-y-5">
        {/* Bar chart */}
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} barCategoryGap="25%">
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="feature"
              tick={{ fontSize: 11, fill: "#475569" }}
              tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
              formatter={(v) => (v === "prev" ? "Previous Window" : "Current Window")}
            />
            <Bar dataKey="prev" fill="#93c5fd" radius={[4, 4, 0, 0]} />
            <Bar dataKey="curr" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>

        {/* Detail pills */}
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {trendReport.feature_trends.map((ft) => {
            const meta = directionMeta[ft.direction] || directionMeta.stable;
            const DirIcon = meta.icon;
            return (
              <div
                key={ft.feature}
                className={clsx(
                  "flex items-center gap-3 rounded-lg border px-3 py-2.5",
                  ft.is_anomaly
                    ? "border-red-200 bg-red-50/60"
                    : "border-slate-200 bg-white",
                )}
              >
                <div
                  className={clsx(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
                    meta.bg,
                  )}
                >
                  <DirIcon className={clsx("h-4 w-4", meta.color)} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold capitalize text-slate-800">
                    {ft.feature.replace(/_/g, " ")}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {ft.previous_window_pct}% &rarr; {ft.current_window_pct}%
                    <span className="ml-1 capitalize text-slate-400">
                      ({ft.classification})
                    </span>
                  </p>
                </div>
                {ft.is_anomaly && (
                  <AlertTriangle className="h-4 w-4 shrink-0 text-red-500" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
