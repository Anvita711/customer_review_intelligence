import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral: "#94a3b8",
  mixed: "#a855f7",
  needs_review: "#f59e0b",
};

const LABELS = {
  positive: "Positive",
  negative: "Negative",
  neutral: "Neutral",
  mixed: "Mixed",
  needs_review: "Needs Review",
};

function computeDistribution(reviews) {
  const counts = {};
  const valid = reviews.filter((r) => !r.is_spam && !r.is_duplicate);
  valid.forEach((r) => {
    const s = r.overall_sentiment;
    counts[s] = (counts[s] || 0) + 1;
  });
  return Object.entries(counts)
    .map(([name, value]) => ({
      name: LABELS[name] || name,
      value,
      color: COLORS[name] || "#cbd5e1",
      pct: ((value / valid.length) * 100).toFixed(1),
    }))
    .sort((a, b) => b.value - a.value);
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs shadow-lg">
      <p className="font-semibold text-slate-800">{d.name}</p>
      <p className="text-slate-500">
        {d.value} reviews ({d.pct}%)
      </p>
    </div>
  );
};

/* Centered donut label showing total valid reviews */
function CenterLabel({ viewBox, total }) {
  const { cx, cy } = viewBox;
  return (
    <g>
      <text
        x={cx}
        y={cy - 8}
        textAnchor="middle"
        dominantBaseline="central"
        className="fill-slate-800 text-2xl font-bold"
      >
        {total}
      </text>
      <text
        x={cx}
        y={cy + 14}
        textAnchor="middle"
        dominantBaseline="central"
        className="fill-slate-400 text-[11px]"
      >
        reviews
      </text>
    </g>
  );
}

export default function SentimentChart({ reviews }) {
  const data = computeDistribution(reviews);

  if (!data.length) return null;

  const totalValid = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "240ms" }}>
      <div className="card-header">
        <h3 className="text-sm font-semibold text-slate-800">
          Sentiment Distribution
        </h3>
        <p className="mt-0.5 text-xs text-slate-400">
          Overall sentiment across valid reviews &middot; hover segments for
          details
        </p>
      </div>
      <div className="card-body">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={64}
              outerRadius={100}
              paddingAngle={3}
              dataKey="value"
              stroke="none"
              animationDuration={600}
            >
              {data.map((d, i) => (
                <Cell
                  key={i}
                  fill={d.color}
                  className="outline-none transition-opacity hover:opacity-80"
                />
              ))}
              {/* Total count in the donut hole */}
              <CenterLabel total={totalValid} />
            </Pie>
            <Tooltip
              content={<CustomTooltip />}
              wrapperStyle={{ outline: "none" }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Legend with percentages — replaces the broken in-chart labels */}
        <div className="mt-3 flex flex-wrap justify-center gap-x-5 gap-y-2">
          {data.map((d) => (
            <div key={d.name} className="flex items-center gap-2">
              <span
                className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: d.color }}
              />
              <span className="text-xs font-medium text-slate-700">
                {d.name}
              </span>
              <span className="text-xs tabular-nums text-slate-400">
                {d.pct}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
