"""
Demo runner — processes all sample input files and prints results.

Usage:
    cd customer_review_intelligence
    python demo_run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ingestion.loader import load_from_csv, load_from_json, load_from_text
from app.pipeline import run_pipeline
from app.models.schemas import PipelineResponse


SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
DIVIDER = "=" * 80


def main():
    print(DIVIDER)
    print("  CUSTOMER REVIEW INTELLIGENCE PLATFORM — DEMO RUN")
    print(DIVIDER)

    # ── 1. CSV Input ──────────────────────────────────────────────────────
    csv_path = SAMPLE_DIR / "electronics_reviews.csv"
    print(f"\n[1/3] Loading CSV: {csv_path.name}")
    with open(csv_path, encoding="utf-8") as f:
        csv_reviews = load_from_csv(f)
    print(f"      Parsed {len(csv_reviews)} reviews")
    csv_result = run_pipeline(csv_reviews, product_id="SMARTX-500")
    _print_report("SMARTX-500 (CSV)", csv_result)

    # ── 2. JSON Input ─────────────────────────────────────────────────────
    json_path = SAMPLE_DIR / "headphones_reviews.json"
    print(f"\n[2/3] Loading JSON: {json_path.name}")
    with open(json_path, encoding="utf-8") as f:
        json_reviews = load_from_json(f.read())
    print(f"      Parsed {len(json_reviews)} reviews")
    json_result = run_pipeline(json_reviews, product_id="HEADPHONE-Z10")
    _print_report("HEADPHONE-Z10 (JSON)", json_result)

    # ── 3. Raw Text Input ─────────────────────────────────────────────────
    text_path = SAMPLE_DIR / "quick_feedback.txt"
    print(f"\n[3/3] Loading Text: {text_path.name}")
    with open(text_path, encoding="utf-8") as f:
        text_reviews = load_from_text(f.read(), product_id="GENERIC-PHONE")
    print(f"      Parsed {len(text_reviews)} reviews")
    text_result = run_pipeline(text_reviews, product_id="GENERIC-PHONE")
    _print_report("GENERIC-PHONE (Text)", text_result)

    # ── Save full JSON output ─────────────────────────────────────────────
    output_path = SAMPLE_DIR / "demo_output.json"
    combined = {
        "smartx_500": csv_result.model_dump(mode="json"),
        "headphone_z10": json_result.model_dump(mode="json"),
        "generic_phone": text_result.model_dump(mode="json"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, default=str)
    print(f"\n{DIVIDER}")
    print(f"  Full JSON report saved to: {output_path}")
    print(DIVIDER)


def _print_report(title: str, result: PipelineResponse):
    print(f"\n{'─' * 80}")
    print(f"  REPORT: {title}")
    print(f"{'─' * 80}")

    # Summary
    print(f"\n  Summary:")
    print(f"    Total input reviews:   {result.total_input}")
    print(f"    Successfully processed:{result.processed}")
    print(f"    Spam flagged:          {result.flagged_spam}")
    print(f"    Duplicates flagged:    {result.flagged_duplicate}")

    # Per-review breakdown
    print(f"\n  Review Analysis:")
    for r in result.analyzed_reviews:
        spam_tag = " [SPAM]" if r.is_spam else ""
        dup_tag = " [DUP]" if r.is_duplicate else ""
        lang_tag = f" [{r.detected_language}]" if r.detected_language != "en" else ""
        features = ", ".join(r.extracted_features) if r.extracted_features else "none"
        text_preview = r.original_text[:60].replace("\n", " ")
        print(f"    {r.review_id[:8]}  {r.overall_sentiment.value:>12}  "
              f"(conf={r.overall_confidence:.2f})  features=[{features}]"
              f"{spam_tag}{dup_tag}{lang_tag}")
        print(f"             \"{text_preview}...\"")

        # Feature-level sentiments
        for fs in r.feature_sentiments:
            sarc = " *SARCASM*" if fs.is_sarcastic else ""
            print(f"               -> {fs.feature:20s}  {fs.sentiment.value:>12}  "
                  f"conf={fs.confidence:.2f}{sarc}")

    # Trend report
    if result.trend_report:
        print(f"\n  Trend Analysis (window={result.trend_report.window_size}):")
        for ft in result.trend_report.feature_trends:
            anomaly = " ** ANOMALY **" if ft.is_anomaly else ""
            print(f"    {ft.feature:20s}  {ft.previous_window_pct:5.1f}% -> "
                  f"{ft.current_window_pct:5.1f}%  "
                  f"{ft.direction.value:>11}  "
                  f"({ft.classification.value}){anomaly}")

    # Recommendations
    if result.insight_report and result.insight_report.recommendations:
        print(f"\n  Prioritized Recommendations:")
        for i, rec in enumerate(result.insight_report.recommendations, 1):
            severity_icon = {
                "critical": "!!!",
                "high": "!! ",
                "medium": "!  ",
                "low": "   ",
            }.get(rec.severity.value, "   ")
            print(f"    {severity_icon} [{rec.severity.value.upper():>8}] {rec.summary}")
            print(f"           Action: {rec.action}")

    # Top features
    if result.insight_report:
        if result.insight_report.top_positive_features:
            print(f"\n  Top Positive Features:")
            for f in result.insight_report.top_positive_features:
                print(f"    + {f['feature']:20s}  {f['count']} mentions ({f['percentage']}%)")
        if result.insight_report.top_negative_features:
            print(f"\n  Top Negative Features:")
            for f in result.insight_report.top_negative_features:
                print(f"    - {f['feature']:20s}  {f['count']} mentions ({f['percentage']}%)")


if __name__ == "__main__":
    main()
