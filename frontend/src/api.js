const BASE = "/api/v1";

export async function analyzeCSV(file, strategy = "keyword") {
  const form = new FormData();
  form.append("file", file);
  const params = new URLSearchParams({
    strategy,
    include_trends: "true",
    include_insights: "true",
  });
  const res = await fetch(`${BASE}/analyze/csv?${params}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function analyzeJSON(file, strategy = "keyword") {
  const form = new FormData();
  form.append("file", file);
  const params = new URLSearchParams({
    strategy,
    include_trends: "true",
    include_insights: "true",
  });
  const res = await fetch(`${BASE}/analyze/file-json?${params}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function analyzeText(
  text,
  productId = "unknown",
  strategy = "keyword",
) {
  const params = new URLSearchParams({
    strategy,
    include_trends: "true",
    include_insights: "true",
  });
  const res = await fetch(`${BASE}/analyze/text?${params}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, product_id: productId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}
