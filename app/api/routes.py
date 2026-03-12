"""API route definitions for CodeEcoScan.

All routes are functional — no stub data.
Business logic is fully delegated to domain modules.

Repo scanning is asynchronous:
  POST /analyze_repo → {job_id, status: "queued"} (immediate)
  GET  /jobs/{job_id} → {status, result, error}   (poll every 2s)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
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
    RepoJobResponse,
    RepoJobStatus,
    RepoSummaryResponse,
    RiskAssessment,
    TopFile,
)
from app.scoring.scoring_engine import EnergyRiskScorer

router = APIRouter(tags=["analysis"])

# ── In-memory job store ───────────────────────────────────────────────
# Maps job_id → {status, result, error, started_at}
# status: "queued" | "running" | "done" | "error"
_JOBS: dict[str, dict[str, Any]] = {}
_MAX_JOBS = 100   # keep only most recent N jobs



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


# ── POST /analyze_repo — async job ───────────────────────────────────

@router.post(
    "/analyze_repo",
    response_model=RepoJobResponse,
    summary="Queue a GitHub repository scan (non-blocking)",
)
async def analyze_repo(
    payload: RepoInput,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> RepoJobResponse:
    """Submit a repo scan job.

    Returns immediately with a job_id.
    Poll GET /jobs/{job_id} every 2s until status == 'done' or 'error'.
    """
    # URL guard — scanner also validates, but fail fast here
    import re
    if not re.match(r'^https://github\.com/[\w.\-]+/[\w.\-]+(\.git)?/?$', payload.repo_url):
        raise HTTPException(status_code=400, detail="Only https://github.com/<owner>/<repo> URLs are accepted.")

    job_id = str(uuid.uuid4())[:8]
    _JOBS[job_id] = {"status": "queued", "result": None, "error": None, "started_at": datetime.utcnow().isoformat()}

    # Evict oldest jobs if over cap
    if len(_JOBS) > _MAX_JOBS:
        oldest = sorted(_JOBS.keys())[0]
        del _JOBS[oldest]

    def _run_scan() -> None:
        _JOBS[job_id]["status"] = "running"
        try:
            result = scan_repository(
                payload.repo_url,
                heavy_modules=settings.HEAVY_IMPORT_MODULES,
            )
            _JOBS[job_id]["status"] = "done"
            _JOBS[job_id]["result"] = result
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
                
                # Also cross-save to AnalysisRun so EmissionMatrix sees it
                risk_level = "Complete"
                if result["repo_score"] >= 70: risk_level = "High"
                elif result["repo_score"] >= 40: risk_level = "Moderate"
                else: risk_level = "Low"

                db.add(AnalysisRun(
                    source="GitHub Repo",
                    filename=result["repo_name"],
                    score=result["repo_score"],
                    risk_level=risk_level,
                    issue_count=len(result["alerts"]),
                    co2_kg_per_day=round(result["repo_score"] * 0.48 * 0.0003, 4), # approximate mapping
                ))
                
                db.commit()
            except Exception:
                db.rollback()
        except Exception as exc:
            _JOBS[job_id]["status"] = "error"
            _JOBS[job_id]["error"] = str(exc)[:300]

    background_tasks.add_task(_run_scan)
    return RepoJobResponse(
        job_id=job_id,
        status="queued",
        message=f"Repo scan queued. Poll /jobs/{job_id} every 2s for results.",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=RepoJobStatus,
    summary="Poll the status of a repo scan job",
)
async def get_job_status(job_id: str) -> RepoJobStatus:
    """Poll a background repo-scan job."""
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    started = datetime.fromisoformat(job["started_at"])
    elapsed = (datetime.utcnow() - started).total_seconds()

    result_out = None
    if job["status"] == "done" and job["result"]:
        r = job["result"]
        result_out = {
            "repo_name":     r.get("repo_name"),
            "energy_risk":   r.get("repo_score"),
            "files_scanned": r.get("files_analyzed"),
            "energy_per_day": round(r.get("repo_score", 0) * 0.48, 2),
            "co2_saved":     0.0,
            "top_files":     r.get("top_files", []),
            "alerts":        r.get("alerts", []),
        }

    return RepoJobStatus(
        job_id=job_id,
        status=job["status"],
        result=result_out,
        error=job.get("error"),
        elapsed_s=round(elapsed, 1),
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
