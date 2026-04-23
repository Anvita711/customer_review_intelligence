"""
Feature-level sentiment analysis with sarcasm detection.

Approach:
- Lexicon-based scoring with negation handling
- Contextual window around feature mentions
- Sarcasm heuristics (contrast patterns, known phrases)
- Ambiguity detection → mark as needs_review
"""

from __future__ import annotations

import re

from app.config import settings
from app.models.schemas import FeatureSentiment, SentimentLabel


CONTEXT_WINDOW = 15  # words before/after feature mention to analyze


def analyze_feature_sentiment(
    text: str,
    features: list[tuple[str, list[str]]],
) -> list[FeatureSentiment]:
    """Compute sentiment for each extracted feature in a review.

    Args:
        text: The cleaned review text.
        features: List of (feature_name, matched_keywords).

    Returns:
        List of FeatureSentiment objects.
    """
    words = text.lower().split()
    results: list[FeatureSentiment] = []

    for feature_name, keywords in features:
        # Extract context windows around every keyword mention
        contexts = _extract_contexts(words, keywords)

        if not contexts:
            # Feature was matched but no word-level context — use full text
            contexts = [words]

        pos_score, neg_score, total_words = 0.0, 0.0, 0
        is_sarcastic = False

        for ctx in contexts:
            p, n = _score_context(ctx)
            pos_score += p
            neg_score += n
            total_words += len(ctx)
            if _detect_sarcasm(ctx, text):
                is_sarcastic = True

        sentiment, confidence = _resolve_sentiment(
            pos_score, neg_score, is_sarcastic
        )

        results.append(
            FeatureSentiment(
                feature=feature_name,
                sentiment=sentiment,
                confidence=round(confidence, 2),
                mentions=keywords,
                is_sarcastic=is_sarcastic,
            )
        )

    return results


def compute_overall_sentiment(
    feature_sentiments: list[FeatureSentiment],
    text: str,
) -> tuple[SentimentLabel, float]:
    """Derive overall review sentiment from feature-level sentiments.

    Falls back to full-text analysis if no features were extracted.
    """
    if not feature_sentiments:
        words = text.lower().split()
        pos, neg = _score_context(words)
        sarcastic = _detect_sarcasm(words, text)
        return _resolve_sentiment(pos, neg, sarcastic)

    pos_count = sum(1 for fs in feature_sentiments if fs.sentiment == SentimentLabel.POSITIVE)
    neg_count = sum(1 for fs in feature_sentiments if fs.sentiment == SentimentLabel.NEGATIVE)
    neutral_count = sum(1 for fs in feature_sentiments if fs.sentiment == SentimentLabel.NEUTRAL)
    needs_review = sum(1 for fs in feature_sentiments if fs.sentiment == SentimentLabel.NEEDS_REVIEW)

    total = len(feature_sentiments)
    avg_confidence = sum(fs.confidence for fs in feature_sentiments) / total

    if needs_review > total / 2:
        return SentimentLabel.NEEDS_REVIEW, avg_confidence
    if pos_count > neg_count and pos_count > neutral_count:
        return SentimentLabel.POSITIVE, avg_confidence
    if neg_count > pos_count and neg_count > neutral_count:
        return SentimentLabel.NEGATIVE, avg_confidence
    if pos_count > 0 and neg_count > 0:
        return SentimentLabel.MIXED, avg_confidence
    return SentimentLabel.NEUTRAL, avg_confidence


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _extract_contexts(
    words: list[str],
    keywords: list[str],
) -> list[list[str]]:
    """Find context windows around keyword mentions."""
    contexts = []
    for kw in keywords:
        kw_words = kw.lower().split()
        for i in range(len(words) - len(kw_words) + 1):
            if words[i : i + len(kw_words)] == kw_words:
                start = max(0, i - CONTEXT_WINDOW)
                end = min(len(words), i + len(kw_words) + CONTEXT_WINDOW)
                contexts.append(words[start:end])
    return contexts


def _score_context(words: list[str]) -> tuple[float, float]:
    """Score a context window for positive/negative signals with negation."""
    pos_score = 0.0
    neg_score = 0.0
    negation_active = False

    for i, word in enumerate(words):
        clean_word = word.strip(".,!?\"'")

        # Negation detection
        if clean_word in settings.negation_words:
            negation_active = True
            continue

        # Reset negation after 3 words
        if negation_active and i > 0:
            lookback = max(0, i - 3)
            has_recent_negation = any(
                words[j].strip(".,!?\"'") in settings.negation_words
                for j in range(lookback, i)
            )
            if not has_recent_negation:
                negation_active = False

        if clean_word in settings.positive_words:
            if negation_active:
                neg_score += 1.0
            else:
                pos_score += 1.0
        elif clean_word in settings.negative_words:
            if negation_active:
                pos_score += 0.5  # negated negative is weakly positive
            else:
                neg_score += 1.0

    return pos_score, neg_score


def _detect_sarcasm(context_words: list[str], full_text: str) -> bool:
    """Heuristic sarcasm detection.

    Signals:
    - Known sarcastic phrases
    - Contrast pattern: positive word followed closely by negative word
    - Excessive exclamation with negative context
    """
    text_lower = full_text.lower()

    # Check known sarcasm phrases
    for phrase in settings.sarcasm_indicators:
        if phrase in text_lower:
            return True

    # Contrast pattern: positive word within 5 words of negative word
    for i, word in enumerate(context_words):
        clean = word.strip(".,!?\"'")
        if clean in settings.positive_words:
            window = context_words[i + 1 : i + 6]
            for w in window:
                if w.strip(".,!?\"'") in settings.negative_words:
                    return True

    # Quote marks around positive words can indicate sarcasm
    if re.search(r'"(good|great|amazing|excellent|best)"', text_lower):
        return True

    return False


def _resolve_sentiment(
    pos_score: float,
    neg_score: float,
    is_sarcastic: bool,
) -> tuple[SentimentLabel, float]:
    """Convert scores to a sentiment label and confidence."""
    total = pos_score + neg_score

    if total == 0:
        return SentimentLabel.NEUTRAL, 0.5

    if is_sarcastic:
        # Sarcasm flips the apparent sentiment
        pos_score, neg_score = neg_score, pos_score
        total = pos_score + neg_score

    dominance = abs(pos_score - neg_score) / total
    confidence = 0.5 + (dominance * 0.5)  # map [0,1] → [0.5,1.0]

    # Ambiguous cases
    if dominance < 0.2:
        if pos_score > 0 and neg_score > 0:
            return SentimentLabel.NEEDS_REVIEW, round(confidence, 2)
        return SentimentLabel.NEUTRAL, round(confidence, 2)

    if pos_score > neg_score:
        return SentimentLabel.POSITIVE, round(confidence, 2)
    return SentimentLabel.NEGATIVE, round(confidence, 2)
