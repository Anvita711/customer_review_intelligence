"""
Trend detection: time-windowed analysis, anomaly detection, issue classification.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from app.config import settings
from app.models.schemas import (
    AnalyzedReview,
    FeatureTrend,
    IssueClassification,
    SentimentLabel,
    TrendDirection,
    TrendReport,
)


def detect_trends(
    reviews: list[AnalyzedReview],
    product_id: str,
    window_size: int | None = None,
) -> TrendReport:
    """Analyze feature complaint trends across two time windows.

    Splits reviews chronologically into a "previous" window and a "current"
    window, then computes per-feature complaint rates and detects anomalies.
    """
    window_size = window_size or settings.default_window_size

    # Sort by timestamp
    sorted_reviews = sorted(reviews, key=lambda r: r.timestamp)

    if len(sorted_reviews) <= window_size:
        # Not enough data for two windows — treat all as current
        previous = []
        current = sorted_reviews
    else:
        split = len(sorted_reviews) - window_size
        previous = sorted_reviews[:split]
        current = sorted_reviews[split:]

    # Compute per-feature negative mention rates
    prev_rates = _compute_feature_rates(previous)
    curr_rates = _compute_feature_rates(current)

    # Gather all features mentioned in either window
    all_features = set(prev_rates.keys()) | set(curr_rates.keys())

    # Historical rates across all time for anomaly z-score
    all_rates = _compute_feature_rates(sorted_reviews)

    feature_trends: list[FeatureTrend] = []
    for feature in sorted(all_features):
        prev_pct = prev_rates.get(feature, 0.0)
        curr_pct = curr_rates.get(feature, 0.0)
        change = curr_pct - prev_pct

        direction = _classify_direction(prev_pct, curr_pct, change)
        is_anomaly = _check_anomaly(feature, curr_pct, sorted_reviews, window_size)
        classification = _classify_issue(curr_pct, change, len(current))

        feature_trends.append(
            FeatureTrend(
                feature=feature,
                previous_window_pct=round(prev_pct * 100, 1),
                current_window_pct=round(curr_pct * 100, 1),
                direction=direction,
                change_magnitude=round(abs(change) * 100, 1),
                is_anomaly=is_anomaly,
                classification=classification,
            )
        )

    # Sort by severity: anomalies first, then by change magnitude
    feature_trends.sort(key=lambda t: (not t.is_anomaly, -t.change_magnitude))

    return TrendReport(
        product_id=product_id,
        window_size=window_size,
        total_reviews=len(sorted_reviews),
        analysis_timestamp=datetime.now(timezone.utc),
        feature_trends=feature_trends,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _compute_feature_rates(
    reviews: list[AnalyzedReview],
) -> dict[str, float]:
    """Compute fraction of reviews with negative sentiment per feature."""
    if not reviews:
        return {}

    feature_neg_count: dict[str, int] = {}
    for review in reviews:
        for fs in review.feature_sentiments:
            if fs.sentiment in (SentimentLabel.NEGATIVE, SentimentLabel.NEEDS_REVIEW):
                feature_neg_count[fs.feature] = feature_neg_count.get(fs.feature, 0) + 1

    total = len(reviews)
    return {f: count / total for f, count in feature_neg_count.items()}


def _classify_direction(
    prev_pct: float,
    curr_pct: float,
    change: float,
) -> TrendDirection:
    if abs(change) < 0.03:
        return TrendDirection.STABLE
    if change > 0.15:
        return TrendDirection.SPIKE
    if change < -0.15:
        return TrendDirection.DROP
    if change > 0:
        return TrendDirection.INCREASING
    return TrendDirection.DECREASING


def _check_anomaly(
    feature: str,
    current_rate: float,
    all_reviews: list[AnalyzedReview],
    window_size: int,
) -> bool:
    """Check if the current rate is a statistical anomaly using z-score."""
    if len(all_reviews) < window_size * 2:
        return False

    # Compute rolling window rates
    window_rates = []
    for start in range(0, len(all_reviews) - window_size + 1, max(1, window_size // 4)):
        window = all_reviews[start : start + window_size]
        rates = _compute_feature_rates(window)
        window_rates.append(rates.get(feature, 0.0))

    if len(window_rates) < 3:
        return False

    arr = np.array(window_rates)
    mean = arr.mean()
    std = arr.std()

    if std < 0.01:
        return False

    z_score = abs(current_rate - mean) / std
    return z_score > settings.anomaly_z_threshold


def _classify_issue(
    current_rate: float,
    change: float,
    window_count: int,
) -> IssueClassification:
    if current_rate >= settings.systemic_issue_threshold:
        return IssueClassification.SYSTEMIC
    if change > 0.05:
        return IssueClassification.EMERGING
    return IssueClassification.ISOLATED
