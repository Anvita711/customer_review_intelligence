"""
Streamlit dashboard for the Customer Review Intelligence Platform.

Run with:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Review Intelligence",
    page_icon="📊",
    layout="wide",
)

API_BASE = "http://localhost:8000/api/v1"


def main():
    st.title("Customer Review Intelligence Platform")
    st.markdown("Analyze customer reviews for sentiment, trends, and actionable insights.")

    tab_upload, tab_text, tab_results = st.tabs(["Upload File", "Paste Text", "Results Explorer"])

    # Session state for storing last results
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # ── Tab 1: File Upload ────────────────────────────────────────────────
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload a CSV or JSON file",
            type=["csv", "json"],
            help="CSV must have a 'review_text' column. JSON should be a list of review objects.",
        )
        col1, col2 = st.columns(2)
        with col1:
            strategy = st.selectbox(
                "Extraction Strategy",
                ["keyword", "embedding"],
                index=0,
                key="upload_strategy",
            )
        with col2:
            include_trends = st.checkbox("Include Trend Analysis", value=True, key="upload_trends")

        if st.button("Analyze File", type="primary", key="btn_file"):
            if uploaded_file is None:
                st.warning("Please upload a file first.")
            else:
                with st.spinner("Running analysis pipeline..."):
                    result = _analyze_file(uploaded_file, strategy, include_trends)
                    if result:
                        st.session_state.last_result = result
                        st.success(f"Analyzed {result['processed']} reviews!")

    # ── Tab 2: Paste Text ─────────────────────────────────────────────────
    with tab_text:
        text_input = st.text_area(
            "Paste review(s) — one per line",
            height=200,
            placeholder="The battery life is terrible, drains in 2 hours.\nExcellent camera quality, photos are sharp.",
        )
        product_id = st.text_input("Product ID", value="demo-product", key="text_pid")
        col1, col2 = st.columns(2)
        with col1:
            strategy_text = st.selectbox(
                "Extraction Strategy",
                ["keyword", "embedding"],
                index=0,
                key="text_strategy",
            )
        with col2:
            trends_text = st.checkbox("Include Trend Analysis", value=False, key="text_trends")

        if st.button("Analyze Text", type="primary", key="btn_text"):
            if not text_input.strip():
                st.warning("Please enter some review text.")
            else:
                with st.spinner("Running analysis pipeline..."):
                    result = _analyze_text(text_input, product_id, strategy_text, trends_text)
                    if result:
                        st.session_state.last_result = result
                        st.success(f"Analyzed {result['processed']} reviews!")

    # ── Tab 3: Results ────────────────────────────────────────────────────
    with tab_results:
        if st.session_state.last_result is None:
            st.info("Run an analysis first to see results here.")
        else:
            _render_results(st.session_state.last_result)


# ── API Calls ─────────────────────────────────────────────────────────────────

def _analyze_file(uploaded_file, strategy: str, include_trends: bool) -> dict | None:
    try:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        endpoint = f"{API_BASE}/analyze/csv" if ext == "csv" else f"{API_BASE}/analyze/file-json"
        resp = requests.post(
            endpoint,
            files={"file": (uploaded_file.name, uploaded_file.getvalue())},
            params={"strategy": strategy, "include_trends": include_trends, "include_insights": include_trends},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running on localhost:8000?")
        return None
    except requests.HTTPError as e:
        st.error(f"API error: {e.response.text}")
        return None


def _analyze_text(text: str, product_id: str, strategy: str, include_trends: bool) -> dict | None:
    try:
        resp = requests.post(
            f"{API_BASE}/analyze/text",
            json={"text": text, "product_id": product_id},
            params={"strategy": strategy, "include_trends": include_trends, "include_insights": include_trends},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running on localhost:8000?")
        return None
    except requests.HTTPError as e:
        st.error(f"API error: {e.response.text}")
        return None


# ── Rendering ─────────────────────────────────────────────────────────────────

def _render_results(data: dict):
    st.header(f"Product: {data['product_id']}")

    # ── Summary Metrics ───────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews", data["total_input"])
    col2.metric("Processed", data["processed"])
    col3.metric("Spam Flagged", data["flagged_spam"])
    col4.metric("Duplicates", data["flagged_duplicate"])

    # ── Sentiment Distribution ────────────────────────────────────────────
    st.subheader("Sentiment Distribution")
    reviews = data.get("analyzed_reviews", [])
    if reviews:
        sentiments = [r["overall_sentiment"] for r in reviews if not r["is_spam"] and not r["is_duplicate"]]
        if sentiments:
            sent_df = pd.DataFrame(sentiments, columns=["sentiment"])
            chart_data = sent_df["sentiment"].value_counts()
            st.bar_chart(chart_data)

    # ── Feature Sentiment Heatmap ─────────────────────────────────────────
    st.subheader("Feature-Level Sentiment")
    feature_rows = []
    for r in reviews:
        if r["is_spam"] or r["is_duplicate"]:
            continue
        for fs in r.get("feature_sentiments", []):
            feature_rows.append({
                "Feature": fs["feature"],
                "Sentiment": fs["sentiment"],
                "Confidence": fs["confidence"],
                "Sarcastic": fs.get("is_sarcastic", False),
            })
    if feature_rows:
        feat_df = pd.DataFrame(feature_rows)
        # Pivot: feature x sentiment counts
        pivot = feat_df.pivot_table(
            index="Feature", columns="Sentiment", values="Confidence", aggfunc="count", fill_value=0
        )
        st.dataframe(pivot, use_container_width=True)

        # Avg confidence per feature
        avg_conf = feat_df.groupby("Feature")["Confidence"].mean().sort_values(ascending=False)
        st.bar_chart(avg_conf)

    # ── Recommendations ───────────────────────────────────────────────────
    insight = data.get("insight_report")
    if insight and insight.get("recommendations"):
        st.subheader("Prioritized Recommendations")
        for rec in insight["recommendations"]:
            severity = rec["severity"]
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            with st.expander(f"{icon} [{severity.upper()}] {rec['feature'].replace('_', ' ').title()}", expanded=(severity in ("critical", "high"))):
                st.markdown(f"**Summary:** {rec['summary']}")
                st.markdown(f"**Trend:** {rec['previous_pct']}% → {rec['current_pct']}% ({rec['trend_direction']})")
                st.markdown(f"**Classification:** {rec['classification']}")
                st.markdown(f"**Action:** {rec['action']}")

    # ── Trend Chart ───────────────────────────────────────────────────────
    trend = data.get("trend_report")
    if trend and trend.get("feature_trends"):
        st.subheader("Feature Complaint Trends")
        trend_rows = []
        for ft in trend["feature_trends"]:
            trend_rows.append({
                "Feature": ft["feature"],
                "Previous %": ft["previous_window_pct"],
                "Current %": ft["current_window_pct"],
                "Direction": ft["direction"],
                "Anomaly": ft["is_anomaly"],
            })
        trend_df = pd.DataFrame(trend_rows)
        st.dataframe(trend_df, use_container_width=True)

        # Bar chart: previous vs current
        chart_df = trend_df.set_index("Feature")[["Previous %", "Current %"]]
        st.bar_chart(chart_df)

    # ── Top Features ──────────────────────────────────────────────────────
    if insight:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Positive Features")
            pos = insight.get("top_positive_features", [])
            if pos:
                st.dataframe(pd.DataFrame(pos), use_container_width=True)
            else:
                st.info("No positive features detected.")
        with col2:
            st.subheader("Top Negative Features")
            neg = insight.get("top_negative_features", [])
            if neg:
                st.dataframe(pd.DataFrame(neg), use_container_width=True)
            else:
                st.info("No negative features detected.")

    # ── Raw Review Table ──────────────────────────────────────────────────
    with st.expander("Raw Analyzed Reviews"):
        if reviews:
            table_rows = []
            for r in reviews:
                table_rows.append({
                    "ID": r["review_id"][:8],
                    "Text": r["original_text"][:100],
                    "Sentiment": r["overall_sentiment"],
                    "Confidence": r["overall_confidence"],
                    "Features": ", ".join(r["extracted_features"]),
                    "Language": r["detected_language"],
                    "Spam": r["is_spam"],
                    "Duplicate": r["is_duplicate"],
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

    # ── Download JSON ─────────────────────────────────────────────────────
    st.download_button(
        "Download Full JSON Report",
        data=json.dumps(data, indent=2, default=str),
        file_name="review_intelligence_report.json",
        mime="application/json",
    )


if __name__ == "__main__":
    main()
