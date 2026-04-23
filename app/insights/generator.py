"""
Insight generation: prioritized recommendations from trend analysis.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from app.models.schemas import (
    AnalyzedReview,
    InsightReport,
    IssueClassification,
    IssueSeverity,
    Recommendation,
    SentimentLabel,
    TrendReport,
)


def generate_insights(
    reviews: list[AnalyzedReview],
    trend_report: TrendReport,
    product_id: str,
) -> InsightReport:
    """Produce a prioritized insight report from analyzed reviews and trends."""
    recommendations = _build_recommendations(trend_report)
    top_positive = _top_features_by_sentiment(reviews, SentimentLabel.POSITIVE, n=5)
    top_negative = _top_features_by_sentiment(reviews, SentimentLabel.NEGATIVE, n=5)

    spam_count = sum(1 for r in reviews if r.is_spam)
    dup_count = sum(1 for r in reviews if r.is_duplicate)

    return InsightReport(
        product_id=product_id,
        generated_at=datetime.now(timezone.utc),
        total_reviews_analyzed=len(reviews),
        flagged_reviews=spam_count + dup_count,
        spam_reviews=spam_count,
        duplicate_reviews=dup_count,
        recommendations=recommendations,
        top_positive_features=top_positive,
        top_negative_features=top_negative,
    )


def _build_recommendations(trend_report: TrendReport) -> list[Recommendation]:
    """Convert feature trends into actionable recommendations."""
    recs: list[Recommendation] = []

    for ft in trend_report.feature_trends:
        severity = _compute_severity(ft.current_window_pct, ft.change_magnitude, ft.is_anomaly)
        action = _suggest_action(ft.feature, severity, ft.classification, ft.direction)
        summary = _format_summary(ft)

        recs.append(
            Recommendation(
                feature=ft.feature,
                severity=severity,
                trend_direction=ft.direction,
                classification=ft.classification,
                previous_pct=ft.previous_window_pct,
                current_pct=ft.current_window_pct,
                action=action,
                summary=summary,
            )
        )

    # Sort: critical first, then high, medium, low
    priority_order = {
        IssueSeverity.CRITICAL: 0,
        IssueSeverity.HIGH: 1,
        IssueSeverity.MEDIUM: 2,
        IssueSeverity.LOW: 3,
    }
    recs.sort(key=lambda r: priority_order[r.severity])
    return recs


def _compute_severity(
    current_pct: float,
    change_magnitude: float,
    is_anomaly: bool,
) -> IssueSeverity:
    if is_anomaly and current_pct > 30:
        return IssueSeverity.CRITICAL
    if current_pct > 25 or (change_magnitude > 20 and current_pct > 15):
        return IssueSeverity.HIGH
    if current_pct > 10 or change_magnitude > 10:
        return IssueSeverity.MEDIUM
    return IssueSeverity.LOW


def _suggest_action(
    feature: str,
    severity: IssueSeverity,
    classification: IssueClassification,
    direction,
) -> str:
    actions = {
        IssueSeverity.CRITICAL: (
            f"URGENT: Investigate {feature} immediately. "
            f"This is a {'systemic' if classification == IssueClassification.SYSTEMIC else 'rapidly emerging'} "
            f"issue affecting a large portion of customers. Escalate to product team."
        ),
        IssueSeverity.HIGH: (
            f"Schedule priority review of {feature}. "
            f"{'This issue is widespread across users' if classification == IssueClassification.SYSTEMIC else 'Complaint rate is climbing fast'}. "
            f"Assign dedicated owner for resolution."
        ),
        IssueSeverity.MEDIUM: (
            f"Monitor {feature} closely. Consider adding to next sprint backlog. "
            f"Gather more data to determine if this becomes a larger issue."
        ),
        IssueSeverity.LOW: (
            f"Track {feature} — currently low impact. "
            f"No immediate action required but include in periodic quality review."
        ),
    }
    return actions[severity]


def _format_summary(ft) -> str:
    if ft.previous_window_pct > 0:
        return (
            f"{ft.feature.replace('_', ' ').title()} complaints "
            f"{'increased' if ft.current_window_pct > ft.previous_window_pct else 'decreased'} "
            f"from {ft.previous_window_pct}% to {ft.current_window_pct}% "
            f"— {ft.classification.value} issue"
        )
    return (
        f"{ft.feature.replace('_', ' ').title()} has {ft.current_window_pct}% "
        f"negative mention rate — {ft.classification.value} issue"
    )


def _top_features_by_sentiment(
    reviews: list[AnalyzedReview],
    sentiment: SentimentLabel,
    n: int = 5,
) -> list[dict]:
    counter: Counter = Counter()
    for review in reviews:
        for fs in review.feature_sentiments:
            if fs.sentiment == sentiment:
                counter[fs.feature] += 1

    total = max(len(reviews), 1)
    return [
        {"feature": feat, "count": count, "percentage": round(count / total * 100, 1)}
        for feat, count in counter.most_common(n)
    ]
