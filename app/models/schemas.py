"""
Pydantic models for the entire pipeline.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    NEEDS_REVIEW = "needs_review"


class TrendDirection(str, Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    SPIKE = "spike"
    DROP = "drop"


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueClassification(str, Enum):
    ISOLATED = "isolated"
    EMERGING = "emerging"
    SYSTEMIC = "systemic"


# ── Input Models ───────────────────────────────────────────────────────────────

class ReviewInput(BaseModel):
    review_text: str
    timestamp: datetime | None = None
    product_id: str = "unknown"
    reviewer_id: str | None = None


class BulkReviewInput(BaseModel):
    reviews: list[ReviewInput]


class TextReviewInput(BaseModel):
    text: str
    product_id: str = "unknown"


# ── Pipeline Internal Models ───────────────────────────────────────────────────

class CleanedReview(BaseModel):
    original_text: str
    cleaned_text: str
    timestamp: datetime
    product_id: str
    reviewer_id: str | None = None
    detected_language: str = "en"
    translated_text: str | None = None
    is_duplicate: bool = False
    duplicate_cluster_id: int | None = None
    is_spam: bool = False
    spam_reason: str | None = None


class FeatureSentiment(BaseModel):
    feature: str
    sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    mentions: list[str] = Field(default_factory=list)
    is_sarcastic: bool = False


class AnalyzedReview(BaseModel):
    review_id: str
    original_text: str
    cleaned_text: str
    timestamp: datetime
    product_id: str
    detected_language: str
    is_duplicate: bool
    is_spam: bool
    spam_reason: str | None = None
    extracted_features: list[str]
    feature_sentiments: list[FeatureSentiment]
    overall_sentiment: SentimentLabel
    overall_confidence: float


# ── Trend Models ───────────────────────────────────────────────────────────────

class FeatureTrend(BaseModel):
    feature: str
    previous_window_pct: float
    current_window_pct: float
    direction: TrendDirection
    change_magnitude: float  # absolute percentage point change
    is_anomaly: bool = False
    classification: IssueClassification


class TrendReport(BaseModel):
    product_id: str
    window_size: int
    total_reviews: int
    analysis_timestamp: datetime
    feature_trends: list[FeatureTrend]


# ── Insight Models ─────────────────────────────────────────────────────────────

class Recommendation(BaseModel):
    feature: str
    severity: IssueSeverity
    trend_direction: TrendDirection
    classification: IssueClassification
    previous_pct: float
    current_pct: float
    action: str
    summary: str


class InsightReport(BaseModel):
    product_id: str
    generated_at: datetime
    total_reviews_analyzed: int
    flagged_reviews: int
    spam_reviews: int
    duplicate_reviews: int
    recommendations: list[Recommendation]
    top_positive_features: list[dict]
    top_negative_features: list[dict]


# ── API Response Models ────────────────────────────────────────────────────────

class PipelineResponse(BaseModel):
    status: str = "success"
    product_id: str
    total_input: int
    processed: int
    flagged_spam: int
    flagged_duplicate: int
    analyzed_reviews: list[AnalyzedReview]
    trend_report: TrendReport | None = None
    insight_report: InsightReport | None = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
