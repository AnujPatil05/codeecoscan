"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request models ─────────────────────────────────────────────────

class CodeInput(BaseModel):
    code: str = Field(..., min_length=1, description="Raw Python source code.")


class RepoInput(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL.")


# ── Core feature/scoring models ────────────────────────────────────

class ExtractedFeatures(BaseModel):
    max_loop_depth: int = Field(..., ge=0)
    has_nested_loops: bool
    function_calls_inside_loops: bool
    has_recursion: bool
    recursion_inside_loop: bool
    heavy_imports_detected: list[str]


class RiskAssessment(BaseModel):
    energy_risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    risk_breakdown: dict[str, int]


class DiagnosticIssue(BaseModel):
    line: int
    type: str
    severity: str
    message: str


class AnalysisResponse(BaseModel):
    extracted_features: ExtractedFeatures
    risk_assessment: RiskAssessment
    issues: list[DiagnosticIssue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


# ── Profiling models ───────────────────────────────────────────────

class LineTiming(BaseModel):
    line: int
    time_ms: float
    category: str = "low"  # 'critical' | 'warning' | 'low'


class FunctionCost(BaseModel):
    name: str
    energy: float
    start_line: int = 0
    end_line: int = 0


class ProfilingResponse(BaseModel):
    line_times: list[LineTiming]
    function_costs: list[FunctionCost]
    peak_memory: int
    total_energy: float


# ── Repository scanning models ─────────────────────────────────────

class TopFile(BaseModel):
    file: str
    score: int


class AlertEntry(BaseModel):
    file: str
    issue: str


class RepoSummaryResponse(BaseModel):
    repo_name: str
    energy_risk: int
    files_scanned: int
    energy_per_day: float
    co2_saved: float
    top_files: list[TopFile] = Field(default_factory=list)
    alerts: list[dict] = Field(default_factory=list)


# ── History models ─────────────────────────────────────────────────

class AnalysisHistoryEntry(BaseModel):
    id: int
    timestamp: str
    source: str
    filename: str
    score: int
    risk_level: str
    issue_count: int
    co2_kg_per_day: float


class CommitEntry(BaseModel):
    sha: int | str
    timestamp: str
    file: str
    message: str
    author: str
    delta: str
    co2_change: float
    risk: str


class RepoJobResponse(BaseModel):
    """Immediate response from POST /analyze_repo — contains job_id to poll."""
    job_id: str
    status: str   # 'queued'
    message: str  # human-readable


class RepoJobStatus(BaseModel):
    """Polled from GET /jobs/{job_id}."""
    job_id: str
    status: str          # 'queued' | 'running' | 'done' | 'error'
    result: dict | None = None
    error: str | None = None
    elapsed_s: float = 0.0


# ── Error ──────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
