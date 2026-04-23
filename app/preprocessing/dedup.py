"""
Duplicate and near-duplicate review detection using TF-IDF + cosine similarity.
"""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


def detect_duplicates(
    texts: list[str],
    threshold: float | None = None,
) -> list[tuple[bool, int | None]]:
    """Identify duplicate and near-duplicate reviews.

    Args:
        texts: List of cleaned review texts.
        threshold: Cosine similarity threshold (default from config).

    Returns:
        List of (is_duplicate, cluster_id) tuples aligned with input.
        The first occurrence in a cluster is NOT marked as duplicate;
        subsequent near-duplicates point to the cluster id.
    """
    threshold = threshold or settings.duplicate_similarity_threshold

    if len(texts) < 2:
        return [(False, None)] * len(texts)

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf_matrix)

    n = len(texts)
    results: list[tuple[bool, int | None]] = [(False, None)] * n
    cluster_id = 0
    visited: set[int] = set()

    for i in range(n):
        if i in visited:
            continue
        # Find all near-duplicates of review i
        group = [i]
        for j in range(i + 1, n):
            if j in visited:
                continue
            if sim_matrix[i, j] >= threshold:
                group.append(j)

        if len(group) > 1:
            # First occurrence is canonical; rest are duplicates
            results[group[0]] = (False, cluster_id)
            for idx in group[1:]:
                results[idx] = (True, cluster_id)
                visited.add(idx)
            cluster_id += 1

    return results
