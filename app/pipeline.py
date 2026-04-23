"""
Orchestration pipeline: wires together all processing stages.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

from app.config import settings
from app.extraction.features import ExtractionStrategy, extract_features
from app.insights.generator import generate_insights
from app.models.schemas import (
    AnalyzedReview,
    InsightReport,
    PipelineResponse,
    ReviewInput,
    TrendReport,
)
from app.preprocessing.cleaner import clean_text
from app.preprocessing.dedup import detect_duplicates
from app.preprocessing.language import process_language
from app.preprocessing.spam import detect_spam
from app.sentiment.analyzer import analyze_feature_sentiment, compute_overall_sentiment
from app.trends.detector import detect_trends

logger = logging.getLogger(__name__)


def run_pipeline(
    reviews: list[ReviewInput],
    product_id: str | None = None,
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.KEYWORD,
    include_trends: bool = True,
    include_insights: bool = True,
) -> PipelineResponse:
    """Execute the full review intelligence pipeline.

    Stages:
        1. Clean text
        2. Detect language & translate
        3. Detect duplicates
        4. Detect spam
        5. Extract features
        6. Analyze sentiment
        7. Detect trends
        8. Generate insights
    """
    if not reviews:
        pid = product_id or "unknown"
        return PipelineResponse(
            product_id=pid,
            total_input=0,
            processed=0,
            flagged_spam=0,
            flagged_duplicate=0,
            analyzed_reviews=[],
        )

    pid = product_id or reviews[0].product_id

    # ── Stage 1 & 2: Clean + Language ─────────────────────────────────────
    cleaned_texts: list[str] = []
    original_texts: list[str] = []
    languages: list[str] = []
    translated: list[str | None] = []

    for review in reviews:
        original_texts.append(review.review_text)
        cleaned = clean_text(review.review_text)
        lang, processed_text, trans = process_language(cleaned)
        cleaned_texts.append(processed_text)
        languages.append(lang)
        translated.append(trans)

    logger.info("Cleaned %d reviews", len(reviews))

    # ── Stage 3: Duplicate Detection ─────────────────────────────────────
    dup_results = detect_duplicates(cleaned_texts)
    logger.info(
        "Found %d duplicates", sum(1 for d, _ in dup_results if d)
    )

    # ── Stage 4: Spam Detection ──────────────────────────────────────────
    spam_results = detect_spam(cleaned_texts, original_texts)
    logger.info(
        "Flagged %d spam reviews", sum(1 for s, _ in spam_results if s)
    )

    # ── Stage 5-6: Feature Extraction + Sentiment ────────────────────────
    analyzed: list[AnalyzedReview] = []

    for i, review in enumerate(reviews):
        review_id = _generate_id(review.review_text, review.product_id, i)
        is_dup, cluster_id = dup_results[i]
        is_spam, spam_reason = spam_results[i]

        # Extract features
        features = extract_features(cleaned_texts[i], strategy=extraction_strategy)
        feature_names = [f for f, _ in features]

        # Sentiment per feature
        feature_sentiments = analyze_feature_sentiment(cleaned_texts[i], features)

        # Overall sentiment
        overall_sentiment, overall_confidence = compute_overall_sentiment(
            feature_sentiments, cleaned_texts[i]
        )

        analyzed.append(
            AnalyzedReview(
                review_id=review_id,
                original_text=review.review_text,
                cleaned_text=cleaned_texts[i],
                timestamp=review.timestamp or datetime.now(timezone.utc),
                product_id=review.product_id,
                detected_language=languages[i],
                is_duplicate=is_dup,
                is_spam=is_spam,
                spam_reason=spam_reason,
                extracted_features=feature_names,
                feature_sentiments=feature_sentiments,
                overall_sentiment=overall_sentiment,
                overall_confidence=round(overall_confidence, 2),
            )
        )

    logger.info("Analyzed %d reviews", len(analyzed))

    # ── Stage 7: Trend Detection ─────────────────────────────────────────
    # Use only valid (non-spam, non-duplicate) reviews for trend analysis
    valid_reviews = [r for r in analyzed if not r.is_spam and not r.is_duplicate]

    trend_report: TrendReport | None = None
    if include_trends and len(valid_reviews) >= 5:
        trend_report = detect_trends(valid_reviews, pid)
        logger.info("Trend analysis complete: %d features tracked", len(trend_report.feature_trends))

    # ── Stage 8: Insight Generation ──────────────────────────────────────
    insight_report: InsightReport | None = None
    if include_insights and trend_report:
        insight_report = generate_insights(valid_reviews, trend_report, pid)
        logger.info(
            "Generated %d recommendations", len(insight_report.recommendations)
        )

    return PipelineResponse(
        product_id=pid,
        total_input=len(reviews),
        processed=len(analyzed),
        flagged_spam=sum(1 for r in analyzed if r.is_spam),
        flagged_duplicate=sum(1 for r in analyzed if r.is_duplicate),
        analyzed_reviews=analyzed,
        trend_report=trend_report,
        insight_report=insight_report,
    )


def _generate_id(text: str, product_id: str, index: int) -> str:
    raw = f"{product_id}:{index}:{text[:100]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
