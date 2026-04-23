import { useState, useMemo } from "react";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Filter,
  AlertTriangle,
  Copy,
  Bot,
} from "lucide-react";
import clsx from "clsx";

const PAGE_SIZE = 10;

const SENTIMENT_STYLE = {
  positive: "badge-positive",
  negative: "badge-negative",
  neutral: "badge-neutral",
  mixed: "badge-mixed",
  needs_review: "badge-needs_review",
};

export default function ReviewTable({ reviews }) {
  const [search, setSearch] = useState("");
  const [sentimentFilter, setSentimentFilter] = useState("all");
  const [flagFilter, setFlagFilter] = useState("all"); // all | clean | spam | duplicate
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    let list = reviews;

    if (sentimentFilter !== "all") {
      list = list.filter((r) => r.overall_sentiment === sentimentFilter);
    }
    if (flagFilter === "clean") {
      list = list.filter((r) => !r.is_spam && !r.is_duplicate);
    } else if (flagFilter === "spam") {
      list = list.filter((r) => r.is_spam);
    } else if (flagFilter === "duplicate") {
      list = list.filter((r) => r.is_duplicate);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (r) =>
          r.original_text.toLowerCase().includes(q) ||
          r.extracted_features.some((f) => f.includes(q)),
      );
    }

    return list;
  }, [reviews, sentimentFilter, flagFilter, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages - 1);
  const pageSlice = filtered.slice(
    safePage * PAGE_SIZE,
    (safePage + 1) * PAGE_SIZE,
  );

  return (
    <div className="card animate-slide-up" style={{ animationDelay: "480ms" }}>
      <div className="card-header">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">
              Review Details
            </h3>
            <p className="mt-0.5 text-xs text-slate-400">
              {filtered.length} of {reviews.length} reviews shown
            </p>
          </div>

          {/* Filters row */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Search */}
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(0);
                }}
                placeholder="Search reviews..."
                className="h-8 w-48 rounded-md border border-slate-200 bg-white pl-8 pr-3 text-xs
                           text-slate-700 placeholder:text-slate-400 focus:border-indigo-400
                           focus:outline-none focus:ring-1 focus:ring-indigo-200"
              />
            </div>

            {/* Sentiment filter */}
            <select
              value={sentimentFilter}
              onChange={(e) => {
                setSentimentFilter(e.target.value);
                setPage(0);
              }}
              className="h-8 rounded-md border border-slate-200 bg-white px-2 text-xs text-slate-600
                         focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-200"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
              <option value="mixed">Mixed</option>
              <option value="needs_review">Needs Review</option>
            </select>

            {/* Flag filter */}
            <select
              value={flagFilter}
              onChange={(e) => {
                setFlagFilter(e.target.value);
                setPage(0);
              }}
              className="h-8 rounded-md border border-slate-200 bg-white px-2 text-xs text-slate-600
                         focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-200"
            >
              <option value="all">All Reviews</option>
              <option value="clean">Clean Only</option>
              <option value="spam">Spam Only</option>
              <option value="duplicate">Duplicates Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/60">
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Review
              </th>
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Sentiment
              </th>
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Conf.
              </th>
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Features
              </th>
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Lang
              </th>
              <th className="whitespace-nowrap px-4 py-2.5 font-semibold text-slate-500">
                Flags
              </th>
            </tr>
          </thead>
          <tbody>
            {pageSlice.map((r) => (
              <tr
                key={r.review_id}
                className={clsx(
                  "border-b border-slate-50 transition-colors hover:bg-slate-50/80",
                  r.is_spam && "bg-red-50/30",
                  r.is_duplicate && !r.is_spam && "bg-amber-50/30",
                )}
              >
                <td className="max-w-xs px-4 py-3">
                  <p className="line-clamp-2 leading-relaxed text-slate-700">
                    {r.original_text}
                  </p>
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <span
                    className={clsx(
                      "badge",
                      SENTIMENT_STYLE[r.overall_sentiment],
                    )}
                  >
                    {r.overall_sentiment.replace("_", " ")}
                  </span>
                </td>
                <td className="whitespace-nowrap px-4 py-3 font-mono text-slate-600">
                  {r.overall_confidence.toFixed(2)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {r.extracted_features.length > 0
                      ? r.extracted_features.map((f) => (
                          <span
                            key={f}
                            className="inline-block rounded bg-indigo-50 px-1.5 py-0.5 text-[11px] font-medium capitalize text-indigo-700"
                          >
                            {f.replace(/_/g, " ")}
                          </span>
                        ))
                      : <span className="text-slate-300">—</span>}
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 uppercase text-slate-500">
                  {r.detected_language}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <div className="flex gap-1.5">
                    {r.is_spam && (
                      <span className="flex items-center gap-1 rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-semibold text-red-700">
                        <Bot className="h-3 w-3" /> SPAM
                      </span>
                    )}
                    {r.is_duplicate && (
                      <span className="flex items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700">
                        <Copy className="h-3 w-3" /> DUP
                      </span>
                    )}
                    {r.feature_sentiments?.some((fs) => fs.is_sarcastic) && (
                      <span className="flex items-center gap-1 rounded bg-purple-100 px-1.5 py-0.5 text-[10px] font-semibold text-purple-700">
                        <AlertTriangle className="h-3 w-3" /> SARC
                      </span>
                    )}
                    {!r.is_spam && !r.is_duplicate && !r.feature_sentiments?.some((fs) => fs.is_sarcastic) && (
                      <span className="text-slate-300">—</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {pageSlice.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-sm text-slate-400">
                  No reviews match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3">
          <p className="text-xs text-slate-400">
            Page {safePage + 1} of {totalPages}
          </p>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={safePage === 0}
              className="rounded-md border border-slate-200 p-1.5 text-slate-500 hover:bg-slate-50
                         disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={safePage >= totalPages - 1}
              className="rounded-md border border-slate-200 p-1.5 text-slate-500 hover:bg-slate-50
                         disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
