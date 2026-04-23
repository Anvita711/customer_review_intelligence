import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

const SENTIMENT_COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral: "#94a3b8",
  mixed: "#a855f7",
  needs_review: "#f59e0b",
};

function buildFeatureMatrix(reviews) {
  const map = {};
  const valid = reviews.filter((r) => !r.is_spam && !r.is_duplicate);

  valid.forEach((r) => {
    r.feature_sentiments?.forEach((fs) => {
      if (!map[fs.feature]) {
        map[fs.feature] = {
          feature: fs.feature.replace(/_/g, " "),
          positive: 0,
          negative: 0,
          neutral: 0,
          mixed: 0,
          needs_review: 0,
          total: 0,
        };
      }
      map[fs.feature][fs.sentiment] += 1;
      map[fs.feature].total += 1;
    });
  });

  return Object.values(map).sort((a, b) => b.total - a.total);
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-xs shadow-lg">
      <p className="mb-1 font-semibold capitalize text-slate-800">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: p.fill }}
          />
          <span className="text-slate-500">
            {p.dataKey}: {p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function FeatureAnalysis({ reviews }) {
  const data = buildFeatureMatrix(reviews);

  if (!data.length) return null;

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "300ms" }}>
      <div className="card-header">
        <h3 className="text-sm font-semibold text-slate-800">
          Feature-Level Sentiment Breakdown
        </h3>
        <p className="mt-0.5 text-xs text-slate-400">
          How customers feel about each product feature
        </p>
      </div>
      <div className="card-body">
        <ResponsiveContainer width="100%" height={Math.max(280, data.length * 44)}>
          <BarChart data={data} layout="vertical" barCategoryGap="20%">
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
            <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} />
            <YAxis
              dataKey="feature"
              type="category"
              width={110}
              tick={{ fontSize: 12, fill: "#475569", fontWeight: 500 }}
              tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            />
            <Bar dataKey="positive" stackId="a" fill={SENTIMENT_COLORS.positive} radius={[0, 0, 0, 0]} />
            <Bar dataKey="negative" stackId="a" fill={SENTIMENT_COLORS.negative} />
            <Bar dataKey="neutral" stackId="a" fill={SENTIMENT_COLORS.neutral} />
            <Bar dataKey="mixed" stackId="a" fill={SENTIMENT_COLORS.mixed} />
            <Bar dataKey="needs_review" stackId="a" fill={SENTIMENT_COLORS.needs_review} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
