import { useState, useCallback } from "react";
import Header from "./components/Header";
import LandingHero from "./components/LandingHero";
import UploadPanel from "./components/UploadPanel";
import SummaryCards from "./components/SummaryCards";
import SentimentChart from "./components/SentimentChart";
import FeatureAnalysis from "./components/FeatureAnalysis";
import TrendChart from "./components/TrendChart";
import Recommendations from "./components/Recommendations";
import TopFeatures from "./components/TopFeatures";
import ReviewTable from "./components/ReviewTable";
import ExportButton from "./components/ExportButton";
import { analyzeCSV, analyzeJSON, analyzeText } from "./api";
import { Package } from "lucide-react";

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      let result;
      if (payload.type === "file") {
        const ext = payload.file.name.split(".").pop().toLowerCase();
        result =
          ext === "csv"
            ? await analyzeCSV(payload.file, payload.strategy)
            : await analyzeJSON(payload.file, payload.strategy);
      } else {
        result = await analyzeText(
          payload.text,
          payload.productId,
          payload.strategy,
        );
      }
      setData(result);
    } catch (e) {
      setError(e.message || "Analysis failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleReset = () => {
    setData(null);
    setError(null);
  };

  return (
    <div className="flex min-h-full flex-col">
      <Header hasResults={!!data} onReset={handleReset} />

      <main className="flex-1">
        {/* ── Landing + Upload Screen ─────────────────────── */}
        {!data && (
          <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
            <LandingHero />
            <div id="upload-panel" className="mt-16">
              <UploadPanel
                onAnalyze={handleAnalyze}
                loading={loading}
                error={error}
              />
            </div>
          </div>
        )}

        {/* ── Results Dashboard ──────────────────────────── */}
        {data && (
          <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {/* Title row */}
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100">
                  <Package className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {data.product_id}
                  </h2>
                  <p className="text-xs text-slate-500">
                    Analysis of {data.total_input} reviews
                  </p>
                </div>
              </div>
              <ExportButton data={data} />
            </div>

            {/* Summary cards */}
            <SummaryCards data={data} />

            {/* Two-column: charts left, top features right */}
            <div className="mt-6 grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <SentimentChart reviews={data.analyzed_reviews} />
              </div>
              <div>
                <TopFeatures insightReport={data.insight_report} />
              </div>
            </div>

            {/* Feature analysis — full width */}
            <div className="mt-6">
              <FeatureAnalysis reviews={data.analyzed_reviews} />
            </div>

            {/* Trend + Recommendations side-by-side on large screens */}
            <div className="mt-6 grid gap-6 xl:grid-cols-2">
              <TrendChart trendReport={data.trend_report} />
              <Recommendations insightReport={data.insight_report} />
            </div>

            {/* Review table — full width */}
            <div className="mt-6">
              <ReviewTable reviews={data.analyzed_reviews} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 py-4 text-center text-xs text-slate-400">
        Review Intelligence Platform v1.0 &mdash; Customer Feedback Analytics
      </footer>
    </div>
  );
}
