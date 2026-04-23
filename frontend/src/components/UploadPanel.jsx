import { useState, useCallback } from "react";
import {
  Upload,
  FileText,
  FileSpreadsheet,
  Type,
  ChevronDown,
  Loader2,
  AlertCircle,
} from "lucide-react";
import clsx from "clsx";

const STRATEGIES = [
  { value: "keyword", label: "Keyword Matching", desc: "Fast, rule-based" },
  {
    value: "embedding",
    label: "Embedding Similarity",
    desc: "TF-IDF vectors",
  },
];

export default function UploadPanel({ onAnalyze, loading, error }) {
  const [mode, setMode] = useState("file"); // "file" | "text"
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [productId, setProductId] = useState("");
  const [strategy, setStrategy] = useState("keyword");
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && /\.(csv|json)$/i.test(dropped.name)) {
      setFile(dropped);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files[0]) setFile(e.target.files[0]);
  };

  const handleSubmit = () => {
    if (mode === "file" && file) {
      onAnalyze({ type: "file", file, strategy });
    } else if (mode === "text" && text.trim()) {
      onAnalyze({ type: "text", text, productId: productId || "unknown", strategy });
    }
  };

  const canSubmit =
    !loading &&
    ((mode === "file" && file) || (mode === "text" && text.trim()));

  return (
    <div className="animate-fade-in mx-auto max-w-3xl">
      {/* Hero text */}
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          Analyze Customer Reviews
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-base text-slate-500">
          Upload a file or paste reviews to uncover sentiment trends,
          feature-level insights, and prioritized action items.
        </p>
      </div>

      {/* Mode toggle */}
      <div className="mb-6 flex justify-center">
        <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1">
          <button
            onClick={() => setMode("file")}
            className={clsx(
              "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-all",
              mode === "file"
                ? "bg-white text-slate-900 shadow-sm"
                : "text-slate-500 hover:text-slate-700",
            )}
          >
            <Upload className="h-4 w-4" />
            Upload File
          </button>
          <button
            onClick={() => setMode("text")}
            className={clsx(
              "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-all",
              mode === "text"
                ? "bg-white text-slate-900 shadow-sm"
                : "text-slate-500 hover:text-slate-700",
            )}
          >
            <Type className="h-4 w-4" />
            Paste Text
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-body space-y-5">
          {/* ── File upload ─────────────────────────────────── */}
          {mode === "file" && (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={clsx(
                "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-14 transition-colors",
                dragOver
                  ? "border-indigo-400 bg-indigo-50"
                  : file
                    ? "border-emerald-300 bg-emerald-50/50"
                    : "border-slate-300 bg-slate-50 hover:border-slate-400",
              )}
            >
              {file ? (
                <>
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100">
                    {file.name.endsWith(".csv") ? (
                      <FileSpreadsheet className="h-6 w-6 text-emerald-600" />
                    ) : (
                      <FileText className="h-6 w-6 text-emerald-600" />
                    )}
                  </div>
                  <p className="mt-3 text-sm font-semibold text-slate-800">
                    {file.name}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                  <button
                    onClick={() => setFile(null)}
                    className="mt-3 text-xs font-medium text-indigo-600 hover:text-indigo-800"
                  >
                    Remove and choose another
                  </button>
                </>
              ) : (
                <>
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-200">
                    <Upload className="h-6 w-6 text-slate-500" />
                  </div>
                  <p className="mt-3 text-sm font-semibold text-slate-700">
                    Drag and drop your file here
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    Supports CSV and JSON files
                  </p>
                  <label className="btn-secondary mt-4 cursor-pointer text-xs">
                    Browse Files
                    <input
                      type="file"
                      accept=".csv,.json"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </label>
                </>
              )}
            </div>
          )}

          {/* ── Text paste ──────────────────────────────────── */}
          {mode === "text" && (
            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">
                  Product ID
                  <span className="ml-1 text-xs font-normal text-slate-400">
                    (optional)
                  </span>
                </label>
                <input
                  type="text"
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                  placeholder="e.g. PHONE-X100"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm
                             text-slate-800 placeholder:text-slate-400
                             focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">
                  Reviews
                  <span className="ml-1 text-xs font-normal text-slate-400">
                    (one per line)
                  </span>
                </label>
                <textarea
                  rows={8}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={
                    "Battery drains in just 2 hours. Very disappointing.\nExcellent camera quality! Photos are sharp and vibrant.\nPackaging was crushed on arrival. Very poor handling."
                  }
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm
                             leading-relaxed text-slate-800 placeholder:text-slate-400
                             focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
                <p className="mt-1 text-right text-xs text-slate-400">
                  {text.split("\n").filter((l) => l.trim()).length} reviews
                </p>
              </div>
            </div>
          )}

          {/* ── Strategy selector ───────────────────────────── */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">
              Feature Extraction Strategy
            </label>
            <div className="relative">
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full appearance-none rounded-lg border border-slate-300 bg-white
                           px-3.5 py-2.5 pr-10 text-sm text-slate-800
                           focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              >
                {STRATEGIES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label} — {s.desc}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
          </div>

          {/* ── Error ───────────────────────────────────────── */}
          {error && (
            <div className="flex items-start gap-3 rounded-lg bg-red-50 px-4 py-3">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* ── Submit ──────────────────────────────────────── */}
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="btn-primary w-full"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing Reviews…
              </>
            ) : (
              "Run Analysis"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
