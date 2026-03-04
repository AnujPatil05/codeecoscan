"""API route definitions for CodeEcoScan.

This module contains zero business logic.  The route handler
delegates entirely to ``FeatureExtractor`` and ``EnergyRiskScorer``
and returns the result as a Pydantic model.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.analysis.feature_extractor import FeatureExtractor
from app.core.config import Settings, get_settings
from app.models.schemas import (
    AnalysisResponse,
    CodeInput,
    ErrorResponse,
    ExtractedFeatures,
    RiskAssessment,
)
from app.scoring.scoring_engine import EnergyRiskScorer

router = APIRouter(tags=["analysis"])


def _get_feature_extractor(
    settings: Settings = Depends(get_settings),
) -> FeatureExtractor:
    """Dependency provider for ``FeatureExtractor``."""
    return FeatureExtractor(settings=settings)


def _get_scorer() -> EnergyRiskScorer:
    """Dependency provider for ``EnergyRiskScorer``.

    Uses default scoring rules.  To support per-request rule
    overrides in the future, this can be extended to read from
    query parameters or request headers.
    """
    return EnergyRiskScorer()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Code contains syntax errors."},
        422: {"model": ErrorResponse, "description": "Validation error."},
    },
    summary="Analyze Python code for energy-risk patterns",
    description=(
        "Parses the submitted Python source code using ``ast.parse``, "
        "extracts structural features, and computes an energy risk score."
    ),
)
async def analyze_code(
    payload: CodeInput,
    extractor: FeatureExtractor = Depends(_get_feature_extractor),
    scorer: EnergyRiskScorer = Depends(_get_scorer),
) -> AnalysisResponse:
    """Analyze submitted Python code and return features + risk score.

    The handler contains no business logic — it delegates to
    ``FeatureExtractor.extract()`` and ``EnergyRiskScorer.score()``.
    """
    features: ExtractedFeatures = extractor.extract(payload.code)
    assessment: RiskAssessment = scorer.score(features)
    return AnalysisResponse(
        extracted_features=features,
        risk_assessment=assessment,
    )
