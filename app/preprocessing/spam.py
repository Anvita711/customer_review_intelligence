"""
Spam / bot review detection.

Heuristics:
1. Repetitive patterns (same short phrase repeated)
2. High similarity cluster (many reviews with near-identical text)
3. Suspiciously short or generic content
4. Excessive punctuation or ALL CAPS in original text
"""

from __future__ import annotations

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


def detect_spam(
    texts: list[str],
    original_texts: list[str] | None = None,
) -> list[tuple[bool, str | None]]:
    """Flag likely spam/bot reviews.

    Args:
        texts: Cleaned review texts.
        original_texts: Raw texts (for caps/punctuation heuristics).

    Returns:
        List of (is_spam, reason) tuples.
    """
    original_texts = original_texts or texts
    n = len(texts)
    results: list[tuple[bool, str | None]] = [(False, None)] * n

    # Pass 1: individual heuristics
    for i in range(n):
        reason = _check_individual(texts[i], original_texts[i])
        if reason:
            results[i] = (True, reason)

    # Pass 2: cluster-based detection (many similar reviews → likely bot)
    cluster_flags = _check_similarity_clusters(texts)
    for i, (flagged, reason) in enumerate(cluster_flags):
        if flagged and not results[i][0]:
            results[i] = (True, reason)

    return results


def _check_individual(cleaned: str, original: str) -> str | None:
    """Run per-review spam heuristics."""
    # Too short
    if len(cleaned.split()) < settings.min_review_length:
        return "too_short"

    # Repetitive phrases: "good good good good"
    words = cleaned.split()
    if len(words) >= 4:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            return "repetitive_text"

    # Excessive caps in original
    alpha_chars = [c for c in original if c.isalpha()]
    if len(alpha_chars) > 10:
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if caps_ratio > 0.8:
            return "excessive_caps"

    # Excessive repeated punctuation in original
    if re.search(r"[!?]{5,}", original):
        return "excessive_punctuation"

    return None


def _check_similarity_clusters(
    texts: list[str],
) -> list[tuple[bool, str | None]]:
    """Flag reviews that appear in suspiciously large similar clusters."""
    n = len(texts)
    results: list[tuple[bool, str | None]] = [(False, None)] * n

    if n < settings.spam_min_cluster_size:
        return results

    vectorizer = TfidfVectorizer(max_features=3000, stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return results

    sim_matrix = cosine_similarity(tfidf_matrix)
    threshold = settings.spam_similarity_threshold

    for i in range(n):
        similar_count = sum(
            1 for j in range(n) if i != j and sim_matrix[i, j] >= threshold
        )
        if similar_count >= settings.spam_min_cluster_size:
            results[i] = (True, f"bot_cluster(similar_to={similar_count})")

    return results
