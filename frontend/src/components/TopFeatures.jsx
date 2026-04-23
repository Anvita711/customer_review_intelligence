import { ThumbsUp, ThumbsDown } from "lucide-react";
import clsx from "clsx";

function FeatureList({ title, icon: Icon, items, colorClass, barClass }) {
  if (!items?.length) return null;
  const maxCount = items[0]?.count || 1;

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <Icon className={clsx("h-4 w-4", colorClass)} />
        <h4 className="text-xs font-semibold text-slate-700">{title}</h4>
      </div>
      <div className="space-y-2.5">
        {items.map((f) => (
          <div key={f.feature}>
            <div className="mb-0.5 flex items-center justify-between">
              <span className="text-xs font-medium capitalize text-slate-700">
                {f.feature.replace(/_/g, " ")}
              </span>
              <span className="text-[11px] font-semibold text-slate-500">
                {f.percentage}%
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className={clsx("h-full rounded-full transition-all", barClass)}
                style={{ width: `${(f.count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TopFeatures({ insightReport }) {
  if (!insightReport) return null;

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "300ms" }}>
      <div className="card-header">
        <h3 className="text-sm font-semibold text-slate-800">
          Feature Highlights
        </h3>
        <p className="mt-0.5 text-xs text-slate-400">
          Most mentioned features by sentiment
        </p>
      </div>
      <div className="card-body space-y-6">
        <FeatureList
          title="Top Positive"
          icon={ThumbsUp}
          items={insightReport.top_positive_features}
          colorClass="text-emerald-600"
          barClass="bg-emerald-500"
        />
        <FeatureList
          title="Top Negative"
          icon={ThumbsDown}
          items={insightReport.top_negative_features}
          colorClass="text-red-500"
          barClass="bg-red-500"
        />
      </div>
    </div>
  );
}
