"""API route definitions for CodeEcoScan.

This module contains zero business logic.  The route handler
delegates entirely to ``FeatureExtractor`` and ``EnergyRiskScorer``
and returns the result as a Pydantic model.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.analysis.diagnostics import extract_diagnostic_issues
from app.analysis.feature_extractor import FeatureExtractor
from app.core.config import Settings, get_settings
from app.models.schemas import (
    AnalysisResponse,
    CodeInput,
    CommitEntry,
    ErrorResponse,
    ExtractedFeatures,
    FunctionCost,
    LineTiming,
    ProfilingResponse,
    RepoInput,
    RepoSummaryResponse,
    RiskAssessment,
    TopFile,
)
from app.scoring.scoring_engine import EnergyRiskScorer

router = APIRouter(tags=["analysis"])


def _get_feature_extractor(
    settings: Settings = Depends(get_settings),
) -> FeatureExtractor:
    return FeatureExtractor(settings=settings)


def _get_scorer() -> EnergyRiskScorer:
    return EnergyRiskScorer()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Code contains syntax errors."},
        422: {"model": ErrorResponse, "description": "Validation error."},
    },
    summary="Analyze Python code for energy-risk patterns",
)
async def analyze_code(
    payload: CodeInput,
    extractor: FeatureExtractor = Depends(_get_feature_extractor),
    scorer: EnergyRiskScorer = Depends(_get_scorer),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    """Analyze submitted Python code and return features + risk score + line diagnostics."""
    features: ExtractedFeatures = extractor.extract(payload.code)
    assessment: RiskAssessment = scorer.score(features)
    issues = extract_diagnostic_issues(
        payload.code,
        heavy_modules=settings.HEAVY_IMPORT_MODULES,
    )
    return AnalysisResponse(
        extracted_features=features,
        risk_assessment=assessment,
        issues=issues,
    )


# ── Stub endpoints ────────────────────────────────────────────────────────────
# These return placeholder data until backend scanning/profiling is implemented.
# The frontend hooks (useRepoSummary, useRepoHistory, useProfiling) are ready
# to swap in real data once these endpoints are fully implemented.


@router.post(
    "/analyze_repo",
    response_model=RepoSummaryResponse,
    summary="Analyze a GitHub repository (stub)",
)
async def analyze_repo(payload: RepoInput) -> RepoSummaryResponse:
    """Stub — returns placeholder repo analysis data."""
    return RepoSummaryResponse(
        repo_name=payload.repo_url.rstrip("/").split("/")[-1],
        energy_risk=67,
        files_scanned=0,
        energy_per_day=48.3,
        co2_saved=0.84,
        top_files=[],
    )


@router.post(
    "/profile",
    response_model=ProfilingResponse,
    summary="Profile execution cost of Python code (stub)",
)
async def profile_code(payload: CodeInput) -> ProfilingResponse:
    """Stub — returns placeholder profiling data."""
    return ProfilingResponse(
        line_times=[
            LineTiming(line=7, time_ms=12.0),
            LineTiming(line=8, time_ms=148.0),
            LineTiming(line=9, time_ms=450.0),
            LineTiming(line=10, time_ms=450.0),
            LineTiming(line=11, time_ms=380.0),
        ],
        function_costs=[
            FunctionCost(name="train", energy=1.42),
            FunctionCost(name="load_data", energy=0.38),
        ],
        peak_memory=412,
        total_energy=1.80,
    )


@router.get(
    "/repo/commits",
    response_model=list[CommitEntry],
    summary="Get repository commit history with energy deltas (stub)",
)
async def get_repo_commits() -> list[CommitEntry]:
    """Stub — returns placeholder commit history."""
    return [
        CommitEntry(sha="a3f2c91", timestamp="2026-03-11 14:32", file="train.py", message="feat: add batch processing", author="@anuj", delta="+34%", co2_change=0.021, risk="HIGH"),
        CommitEntry(sha="b7e1d03", timestamp="2026-03-11 13:11", file="utils.py", message="refactor: vectorize processing", author="@anuj", delta="-22%", co2_change=-0.014, risk="MED"),
        CommitEntry(sha="c9a4f77", timestamp="2026-03-11 12:58", file="pipeline.py", message="fix: remove DataFrame copy", author="@anuj", delta="-11%", co2_change=-0.007, risk="LOW"),
    ]
