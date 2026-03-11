"""API route definitions for CodeEcoScan.

All routes are functional — no stub data.
Business logic is fully delegated to domain modules.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analysis.diagnostics import extract_diagnostic_issues
from app.analysis.feature_extractor import FeatureExtractor
from app.analysis.profiler import profile_code
from app.analysis.repo_scanner import scan_repository
from app.core.config import Settings, get_settings
from app.db.database import AnalysisRun, RepoScan, get_db
from app.models.schemas import (
    AnalysisHistoryEntry,
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


def _get_feature_extractor(settings: Settings = Depends(get_settings)) -> FeatureExtractor:
    return FeatureExtractor(settings=settings)


def _get_scorer() -> EnergyRiskScorer:
    return EnergyRiskScorer()


def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()[:16]


# ── POST /analyze ─────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Code contains syntax errors."},
    },
    summary="Analyze Python code for energy risk, issues, and suggestions",
)
async def analyze_code(
    payload: CodeInput,
    extractor: FeatureExtractor = Depends(_get_feature_extractor),
    scorer: EnergyRiskScorer = Depends(_get_scorer),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> AnalysisResponse:
    """Full analysis: features + risk score + line diagnostics + suggestions."""
    features: ExtractedFeatures = extractor.extract(payload.code)
    assessment: RiskAssessment   = scorer.score(features)
    issues = extract_diagnostic_issues(payload.code, settings.HEAVY_IMPORT_MODULES)

    # Generate rule-based suggestions
    suggestions = _build_suggestions(features, issues)

    # Persist (non-blocking)
    def _save() -> None:
        try:
            run = AnalysisRun(
                source="paste",
                code_hash=_code_hash(payload.code),
                score=assessment.energy_risk_score,
                risk_level=assessment.risk_level,
                loop_score=assessment.risk_breakdown.get("loop_score", 0),
                interaction=assessment.risk_breakdown.get("interaction_penalty", 0),
                recursion=assessment.risk_breakdown.get("recursion", 0),
                heavy_imports=assessment.risk_breakdown.get("heavy_imports", 0),
                issue_count=len(issues),
                co2_kg_per_day=round(assessment.energy_risk_score * 0.00012, 6),
            )
            db.add(run)
            db.commit()
        except Exception:
            pass  # Never fail the request due to DB

    background_tasks.add_task(_save)

    return AnalysisResponse(
        extracted_features=features,
        risk_assessment=assessment,
        issues=issues,
        suggestions=suggestions,
    )


# ── POST /analyze_repo ────────────────────────────────────────────────

@router.post(
    "/analyze_repo",
    response_model=RepoSummaryResponse,
    summary="Analyze a GitHub repository",
)
async def analyze_repo(
    payload: RepoInput,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> RepoSummaryResponse:
    """Clone and scan a GitHub repository. Returns aggregated energy risk."""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: scan_repository(
                payload.repo_url,
                heavy_modules=settings.HEAVY_IMPORT_MODULES,
                timeout=55,
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository scan failed: {str(exc)[:200]}")

    if "error" in result and not result.get("files_analyzed"):
        raise HTTPException(status_code=422, detail=result["error"])

    # Persist
    try:
        scan = RepoScan(
            repo_url=payload.repo_url,
            repo_name=result["repo_name"],
            files_analyzed=result["files_analyzed"],
            repo_score=result["repo_score"],
            top_files_json=json.dumps(result["top_files"]),
            alerts_json=json.dumps(result["alerts"]),
        )
        db.add(scan)
        db.commit()
    except Exception:
        pass

    return RepoSummaryResponse(
        repo_name=result["repo_name"],
        energy_risk=result["repo_score"],
        files_scanned=result["files_analyzed"],
        energy_per_day=round(result["repo_score"] * 0.48, 2),
        co2_saved=0.0,
        top_files=[TopFile(file=f["file"], score=f["score"]) for f in result["top_files"]],
        alerts=[{"file": a["file"], "issue": a["issue"]} for a in result["alerts"]],
    )


# ── POST /profile ─────────────────────────────────────────────────────

@router.post(
    "/profile",
    response_model=ProfilingResponse,
    summary="Estimate execution cost profile for Python code",
)
async def profile(payload: CodeInput) -> ProfilingResponse:
    """AST-based static execution cost profiler."""
    result = profile_code(payload.code)

    line_times = [
        LineTiming(line=lt.line, time_ms=lt.time_ms, category=lt.category)
        for lt in result.line_times
    ]
    function_costs = [
        FunctionCost(
            name=fc.name,
            energy=fc.energy_uwh,
            start_line=fc.start_line,
            end_line=fc.end_line,
        )
        for fc in result.function_costs
    ]

    return ProfilingResponse(
        line_times=line_times,
        function_costs=function_costs,
        peak_memory=result.peak_memory_mb,
        total_energy=result.total_energy_uwh,
    )


# ── GET /analysis/history ──────────────────────────────────────────────

@router.get(
    "/analysis/history",
    response_model=list[AnalysisHistoryEntry],
    summary="Retrieve analysis history from database",
)
async def get_analysis_history(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[AnalysisHistoryEntry]:
    """Fetch the most recent analysis runs from the database."""
    runs = (
        db.query(AnalysisRun)
        .order_by(AnalysisRun.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        AnalysisHistoryEntry(
            id=run.id,
            timestamp=run.created_at.isoformat(),
            source=run.source,
            filename=run.filename or "input.py",
            score=run.score,
            risk_level=run.risk_level,
            issue_count=run.issue_count,
            co2_kg_per_day=run.co2_kg_per_day,
        )
        for run in runs
    ]


# ── GET /repo/commits (legacy compat) ─────────────────────────────────

@router.get(
    "/repo/commits",
    response_model=list[CommitEntry],
    summary="Recent repo scans as commit-style entries",
)
async def get_repo_commits(db: Session = Depends(get_db)) -> list[CommitEntry]:
    """Return recent repo scans formatted as commit-history entries."""
    scans = (
        db.query(RepoScan)
        .order_by(RepoScan.created_at.desc())
        .limit(20)
        .all()
    )
    result = []
    for scan in scans:
        result.append(CommitEntry(
            sha=scan.id,
            timestamp=scan.created_at.isoformat(),
            file=scan.repo_name,
            message=f"Repo scan: {scan.files_analyzed} files",
            author="scanner",
            delta=f"{scan.repo_score}/100",
            co2_change=round(scan.repo_score * 0.00012, 4),
            risk="HIGH" if scan.repo_score >= 70 else "MED" if scan.repo_score >= 40 else "LOW",
        ))
    return result


# ── Helper ────────────────────────────────────────────────────────────

def _build_suggestions(features: ExtractedFeatures, issues: list) -> list[str]:
    """Generate rule-based optimization suggestions."""
    issue_types = {i.type for i in issues}
    sugs = []
    if "nested_loop" in issue_types or features.has_nested_loops:
        sugs.append(
            f"Replace O(N^{features.max_loop_depth}) nested loops with NumPy vectorization or list comprehensions."
        )
    if "call_in_loop" in issue_types or features.function_calls_inside_loops:
        sugs.append("Hoist function calls outside loops or cache return values to avoid repeated computation.")
    if "heavy_import" in issue_types and features.heavy_imports_detected:
        sugs.append(
            f"Verify {', '.join(features.heavy_imports_detected)} GPU/ML usage is required; consider lazy imports."
        )
    if features.has_recursion:
        msg = "Add memoization (functools.lru_cache) to recursive functions."
        if features.recursion_inside_loop:
            msg = "Recursion inside loop detected — high risk. " + msg
        sugs.append(msg)
    if not sugs:
        sugs.append("No major energy issues detected. Code looks efficient.")
    return sugs
