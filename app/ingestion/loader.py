"""
Input layer: load reviews from CSV, JSON, or raw text.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from app.models.schemas import ReviewInput


def load_from_csv(source: str | io.StringIO) -> list[ReviewInput]:
    """Parse reviews from a CSV string or file-like object.

    Expected columns: review_text, timestamp (optional), product_id (optional),
    reviewer_id (optional).
    """
    if isinstance(source, str):
        source = io.StringIO(source)

    reader = csv.DictReader(source)
    reviews: list[ReviewInput] = []
    for row in reader:
        text = row.get("review_text", "").strip()
        if not text:
            continue
        reviews.append(
            ReviewInput(
                review_text=text,
                timestamp=_parse_ts(row.get("timestamp")),
                product_id=row.get("product_id", "unknown").strip() or "unknown",
                reviewer_id=row.get("reviewer_id", "").strip() or None,
            )
        )
    return reviews


def load_from_json(source: str) -> list[ReviewInput]:
    """Parse reviews from a JSON string (list of objects or single object)."""
    data = json.loads(source)
    if isinstance(data, dict):
        data = [data]

    reviews: list[ReviewInput] = []
    for item in data:
        text = item.get("review_text", "").strip()
        if not text:
            continue
        reviews.append(
            ReviewInput(
                review_text=text,
                timestamp=_parse_ts(item.get("timestamp")),
                product_id=item.get("product_id", "unknown"),
                reviewer_id=item.get("reviewer_id"),
            )
        )
    return reviews


def load_from_text(text: str, product_id: str = "unknown") -> list[ReviewInput]:
    """Treat each non-empty line as a separate review."""
    reviews: list[ReviewInput] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        reviews.append(
            ReviewInput(
                review_text=line,
                timestamp=datetime.now(timezone.utc),
                product_id=product_id,
            )
        )
    return reviews


def _parse_ts(raw: str | None) -> datetime:
    if not raw or not raw.strip():
        return datetime.now(timezone.utc)
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)
