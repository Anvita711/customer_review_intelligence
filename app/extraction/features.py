"""
Product feature extraction from review text.

Supports three strategies:
1. Rule-based keyword matching (default, zero-dependency)
2. TF-IDF embedding similarity against feature centroids
3. LLM-based extraction (stub — plug in OpenAI / local model)
"""

from __future__ import annotations

import re
from enum import Enum

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


class ExtractionStrategy(str, Enum):
    KEYWORD = "keyword"
    EMBEDDING = "embedding"
    LLM = "llm"


def extract_features(
    text: str,
    strategy: ExtractionStrategy = ExtractionStrategy.KEYWORD,
) -> list[tuple[str, list[str]]]:
    """Extract product features mentioned in a review.

    Returns:
        List of (feature_name, [matched_keywords]) tuples.
    """
    if strategy == ExtractionStrategy.KEYWORD:
        return _keyword_extraction(text)
    if strategy == ExtractionStrategy.EMBEDDING:
        return _embedding_extraction(text)
    if strategy == ExtractionStrategy.LLM:
        return _llm_extraction(text)
    return _keyword_extraction(text)


def extract_features_batch(
    texts: list[str],
    strategy: ExtractionStrategy = ExtractionStrategy.KEYWORD,
) -> list[list[tuple[str, list[str]]]]:
    """Extract features for a batch of reviews."""
    if strategy == ExtractionStrategy.EMBEDDING:
        return _embedding_extraction_batch(texts)
    return [extract_features(t, strategy) for t in texts]


# ── Strategy 1: Keyword Matching ──────────────────────────────────────────────

def _keyword_extraction(text: str) -> list[tuple[str, list[str]]]:
    text_lower = text.lower()
    results = []
    for feature, keywords in settings.feature_keywords.items():
        matched = []
        for kw in keywords:
            # Word-boundary aware matching
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                matched.append(kw)
        if matched:
            results.append((feature, matched))
    return results


# ── Strategy 2: TF-IDF Embedding Similarity ──────────────────────────────────

def _embedding_extraction(text: str) -> list[tuple[str, list[str]]]:
    return _embedding_extraction_batch([text])[0]


def _embedding_extraction_batch(
    texts: list[str],
    threshold: float = 0.15,
) -> list[list[tuple[str, list[str]]]]:
    """Use TF-IDF cosine similarity between reviews and feature descriptions."""
    feature_names = list(settings.feature_keywords.keys())
    feature_descriptions = [
        " ".join(keywords) for keywords in settings.feature_keywords.values()
    ]

    all_docs = texts + feature_descriptions
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    review_vectors = tfidf_matrix[: len(texts)]
    feature_vectors = tfidf_matrix[len(texts) :]

    sim_matrix = cosine_similarity(review_vectors, feature_vectors)

    results: list[list[tuple[str, list[str]]]] = []
    for i in range(len(texts)):
        review_features = []
        for j, fname in enumerate(feature_names):
            if sim_matrix[i, j] >= threshold:
                # Find which keywords actually appear
                matched = [
                    kw
                    for kw in settings.feature_keywords[fname]
                    if re.search(rf"\b{re.escape(kw)}\b", texts[i].lower())
                ]
                review_features.append((fname, matched or [fname]))
        results.append(review_features)
    return results


# ── Strategy 3: LLM Extraction (Stub) ────────────────────────────────────────

def _llm_extraction(text: str) -> list[tuple[str, list[str]]]:
    """Placeholder for LLM-based extraction.

    To activate, integrate with OpenAI / Anthropic / local model:
        prompt = f"Extract product features from: {text}"
        response = llm.complete(prompt)
        # parse structured output
    """
    # Fall back to keyword for now
    return _keyword_extraction(text)
