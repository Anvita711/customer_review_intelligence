import { BarChart3, MessageSquare, Sparkles, TrendingUp, ShieldCheck } from "lucide-react";

const features = [
  {
    title: "Instant sentiment snapshots",
    description: "See customer mood, review balance, and emotion trends in seconds.",
    icon: Sparkles,
  },
  {
    title: "Feature-level intelligence",
    description: "Surface what matters most with topic extraction and prioritized action items.",
    icon: BarChart3,
  },
  {
    title: "Trend-aware recommendations",
    description: "Turn review signals into product improvements and operational wins.",
    icon: TrendingUp,
  },
  {
    title: "Secure, data-first experience",
    description: "Process CSV, JSON or raw text with clean interfaces built for modern teams.",
    icon: ShieldCheck,
  },
];

export default function LandingHero() {
  return (
    <section className="overflow-hidden rounded-[2rem] bg-slate-950 text-white shadow-2xl shadow-slate-900/20">
      <div className="relative overflow-hidden px-6 py-16 sm:px-10 lg:px-14">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(99,102,241,0.35),_transparent_25%),radial-gradient(circle_at_bottom_left,_rgba(16,185,129,0.22),_transparent_20%)]" />
        <div className="relative mx-auto max-w-6xl">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
            <div className="max-w-2xl">
              <span className="inline-flex rounded-full bg-white/10 px-4 py-1 text-sm font-semibold uppercase tracking-[0.24em] text-cyan-200">
                Landing experience
              </span>
              <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Transform reviews into clarity, confidence, and product momentum.
              </h2>
              <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
                Upload your customer feedback or paste review text to surface sentiment, feature insights, and trend signals in a modern dashboard designed for product, support, and growth teams.
              </p>
              <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
                <a href="#upload-panel" className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-indigo-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:scale-[1.01]">
                  Start analysis
                </a>
                <div className="rounded-full bg-white/5 px-4 py-3 text-sm text-slate-300">
                  Built for thoughtful review analytics, instantly.
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {features.slice(0, 2).map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                    <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-cyan-300">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="mt-5 text-lg font-semibold text-white">{feature.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-300">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2">
            {features.slice(2).map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-cyan-300">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-5 text-lg font-semibold text-white">{feature.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
