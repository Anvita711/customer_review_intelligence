"""
FastAPI route definitions.
"""

from __future__ import annotations

import io
import logging

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.config import settings
from app.extraction.features import ExtractionStrategy
from app.ingestion.loader import load_from_csv, load_from_json, load_from_text
from app.models.schemas import (
    BulkReviewInput,
    HealthResponse,
    PipelineResponse,
    TextReviewInput,
)
from app.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(version=settings.version)


@router.post("/analyze/json", response_model=PipelineResponse)
async def analyze_json(
    payload: BulkReviewInput,
    strategy: ExtractionStrategy = Query(
        ExtractionStrategy.KEYWORD,
        description="Feature extraction strategy",
    ),
    include_trends: bool = Query(True),
    include_insights: bool = Query(True),
):
    """Analyze reviews submitted as JSON."""
    if not payload.reviews:
        raise HTTPException(status_code=400, detail="No reviews provided")

    logger.info("Received %d reviews via JSON", len(payload.reviews))
    return run_pipeline(
        payload.reviews,
        extraction_strategy=strategy,
        include_trends=include_trends,
        include_insights=include_insights,
    )


@router.post("/analyze/csv", response_model=PipelineResponse)
async def analyze_csv(
    file: UploadFile = File(..., description="CSV file with review_text column"),
    strategy: ExtractionStrategy = Query(ExtractionStrategy.KEYWORD),
    include_trends: bool = Query(True),
    include_insights: bool = Query(True),
):
    """Analyze reviews from an uploaded CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    reviews = load_from_csv(io.StringIO(text))

    if not reviews:
        raise HTTPException(status_code=400, detail="No valid reviews found in CSV")

    logger.info("Parsed %d reviews from CSV upload", len(reviews))
    return run_pipeline(
        reviews,
        extraction_strategy=strategy,
        include_trends=include_trends,
        include_insights=include_insights,
    )


@router.post("/analyze/text", response_model=PipelineResponse)
async def analyze_text(
    payload: TextReviewInput,
    strategy: ExtractionStrategy = Query(ExtractionStrategy.KEYWORD),
    include_trends: bool = Query(False),
    include_insights: bool = Query(False),
):
    """Analyze a single text review or newline-separated batch."""
    reviews = load_from_text(payload.text, product_id=payload.product_id)

    if not reviews:
        raise HTTPException(status_code=400, detail="No review text provided")

    logger.info("Received %d reviews from raw text", len(reviews))
    return run_pipeline(
        reviews,
        product_id=payload.product_id,
        extraction_strategy=strategy,
        include_trends=include_trends,
        include_insights=include_insights,
    )


@router.post("/analyze/file-json", response_model=PipelineResponse)
async def analyze_json_file(
    file: UploadFile = File(..., description="JSON file with review objects"),
    strategy: ExtractionStrategy = Query(ExtractionStrategy.KEYWORD),
    include_trends: bool = Query(True),
    include_insights: bool = Query(True),
):
    """Analyze reviews from an uploaded JSON file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be a .json")

    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    reviews = load_from_json(text)

    if not reviews:
        raise HTTPException(status_code=400, detail="No valid reviews found in JSON")

    logger.info("Parsed %d reviews from JSON upload", len(reviews))
    return run_pipeline(
        reviews,
        extraction_strategy=strategy,
        include_trends=include_trends,
        include_insights=include_insights,
    )
