"""
Tests for the review intelligence pipeline.
"""

from datetime import datetime, timezone

import pytest

from app.extraction.features import ExtractionStrategy, extract_features
from app.ingestion.loader import load_from_csv, load_from_json, load_from_text
from app.models.schemas import ReviewInput, SentimentLabel
from app.pipeline import run_pipeline
from app.preprocessing.cleaner import clean_text
from app.preprocessing.dedup import detect_duplicates
from app.preprocessing.language import detect_language, translate_hindi_tokens
from app.preprocessing.spam import detect_spam
from app.sentiment.analyzer import analyze_feature_sentiment, compute_overall_sentiment


# ── Ingestion Tests ───────────────────────────────────────────────────────────

class TestIngestion:
    def test_load_csv(self):
        csv_data = (
            "review_text,timestamp,product_id\n"
            '"Great battery life!",2026-01-01,PROD-1\n'
            '"Terrible packaging.",2026-01-02,PROD-1\n'
        )
        reviews = load_from_csv(csv_data)
        assert len(reviews) == 2
        assert reviews[0].review_text == "Great battery life!"
        assert reviews[0].product_id == "PROD-1"

    def test_load_json(self):
        json_data = '[{"review_text": "Good phone", "product_id": "P1"}]'
        reviews = load_from_json(json_data)
        assert len(reviews) == 1
        assert reviews[0].product_id == "P1"

    def test_load_text(self):
        text = "Line one review\nLine two review\n\n"
        reviews = load_from_text(text, product_id="TEST")
        assert len(reviews) == 2
        assert reviews[0].product_id == "TEST"

    def test_empty_csv(self):
        reviews = load_from_csv("review_text\n")
        assert len(reviews) == 0


# ── Cleaning Tests ────────────────────────────────────────────────────────────

class TestCleaner:
    def test_basic_clean(self):
        result = clean_text("  Hello WORLD!!!  ")
        assert result == "hello world!"

    def test_url_removal(self):
        result = clean_text("Check https://example.com for details")
        assert "example.com" not in result

    def test_html_removal(self):
        result = clean_text("This is <b>bold</b> text")
        assert "<b>" not in result

    def test_repeated_chars(self):
        result = clean_text("sooooo goooood")
        assert "oo" in result
        assert "ooo" not in result


# ── Language Tests ────────────────────────────────────────────────────────────

class TestLanguage:
    def test_english_detection(self):
        lang = detect_language("This phone has great battery life")
        assert lang == "en"

    def test_hindi_translation(self):
        result = translate_hindi_tokens("bahut accha phone")
        assert "very" in result
        assert "good" in result


# ── Dedup Tests ───────────────────────────────────────────────────────────────

class TestDedup:
    def test_exact_duplicates(self):
        texts = [
            "This is a great product with amazing features",
            "This is a great product with amazing features",
            "Completely different review about something else entirely",
        ]
        results = detect_duplicates(texts)
        assert results[0][0] is False  # first is canonical
        assert results[1][0] is True   # second is duplicate
        assert results[2][0] is False  # third is unique

    def test_no_duplicates(self):
        texts = [
            "Battery life is terrible and drains fast",
            "Camera quality is excellent for photos",
        ]
        results = detect_duplicates(texts)
        assert all(not is_dup for is_dup, _ in results)


# ── Spam Tests ────────────────────────────────────────────────────────────────

class TestSpam:
    def test_short_review_flagged(self):
        texts = ["ok"]
        results = detect_spam(texts)
        assert results[0][0] is True
        assert results[0][1] == "too_short"

    def test_repetitive_text(self):
        texts = ["good good good good good good good good good good"]
        results = detect_spam(texts)
        assert results[0][0] is True
        assert results[0][1] == "repetitive_text"


# ── Feature Extraction Tests ─────────────────────────────────────────────────

class TestFeatureExtraction:
    def test_keyword_extraction(self):
        features = extract_features(
            "the battery drains fast and the camera is blurry",
            strategy=ExtractionStrategy.KEYWORD,
        )
        feature_names = [f for f, _ in features]
        assert "battery" in feature_names
        assert "camera" in feature_names

    def test_no_features(self):
        features = extract_features(
            "lorem ipsum dolor sit amet",
            strategy=ExtractionStrategy.KEYWORD,
        )
        assert len(features) == 0


# ── Sentiment Tests ───────────────────────────────────────────────────────────

class TestSentiment:
    def test_positive_sentiment(self):
        features = [("camera", ["camera"])]
        results = analyze_feature_sentiment("the camera is excellent and amazing", features)
        assert len(results) == 1
        assert results[0].sentiment == SentimentLabel.POSITIVE

    def test_negative_sentiment(self):
        features = [("battery", ["battery"])]
        results = analyze_feature_sentiment("the battery is terrible and awful", features)
        assert len(results) == 1
        assert results[0].sentiment == SentimentLabel.NEGATIVE

    def test_negation_handling(self):
        features = [("camera", ["camera"])]
        results = analyze_feature_sentiment("the camera is not good at all", features)
        assert len(results) == 1
        assert results[0].sentiment == SentimentLabel.NEGATIVE

    def test_sarcasm_detection(self):
        features = [("battery", ["battery"])]
        results = analyze_feature_sentiment(
            'yeah right the battery has "great" life dies by noon',
            features,
        )
        assert len(results) == 1
        assert results[0].is_sarcastic is True


# ── Full Pipeline Test ────────────────────────────────────────────────────────

class TestPipeline:
    def test_end_to_end(self):
        reviews = [
            ReviewInput(
                review_text="Battery is terrible, drains in 2 hours",
                timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                product_id="TEST-1",
            ),
            ReviewInput(
                review_text="Camera quality is excellent, very sharp photos",
                timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
                product_id="TEST-1",
            ),
            ReviewInput(
                review_text="Packaging was damaged, box arrived crushed",
                timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc),
                product_id="TEST-1",
            ),
            ReviewInput(
                review_text="Great display, AMOLED screen is vibrant",
                timestamp=datetime(2026, 1, 4, tzinfo=timezone.utc),
                product_id="TEST-1",
            ),
            ReviewInput(
                review_text="Performance is smooth, no lag at all",
                timestamp=datetime(2026, 1, 5, tzinfo=timezone.utc),
                product_id="TEST-1",
            ),
        ]
        result = run_pipeline(reviews, product_id="TEST-1")

        assert result.status == "success"
        assert result.total_input == 5
        assert result.processed == 5
        assert len(result.analyzed_reviews) == 5

        # Check that features were extracted
        all_features = set()
        for r in result.analyzed_reviews:
            all_features.update(r.extracted_features)
        assert "battery" in all_features
        assert "camera" in all_features

    def test_empty_input(self):
        result = run_pipeline([])
        assert result.total_input == 0
        assert result.processed == 0
