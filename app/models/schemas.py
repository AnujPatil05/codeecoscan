"""Pydantic schemas for API request/response models.

All models use Pydantic v2 ``BaseModel`` with strict type annotations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    """Request body for the ``POST /analyze`` endpoint."""

    code: str = Field(
        ...,
        min_length=1,
        description="Raw Python source code to analyze.",
        examples=["def hello():\n    print('world')"],
    )


class RepoInput(BaseModel):
    """Request body for the ``POST /analyze_repo`` endpoint."""

    repo_url: str = Field(
        ...,
        description="GitHub repository URL to scan.",
        examples=["https://github.com/user/repo"],
    )


class ExtractedFeatures(BaseModel):
    """Structural features extracted from the submitted code."""

    max_loop_depth: int = Field(..., ge=0)
    has_nested_loops: bool
    function_calls_inside_loops: bool
    has_recursion: bool
    recursion_inside_loop: bool
    heavy_imports_detected: list[str]


class RiskAssessment(BaseModel):
    """Energy risk scoring result."""

    energy_risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    risk_breakdown: dict[str, int]


class DiagnosticIssue(BaseModel):
    """A line-level diagnostic issue detected in the code."""

    line: int = Field(..., description="1-indexed line number.")
    type: str = Field(..., description="Issue type identifier.")
    severity: str = Field(..., description="'high', 'medium', or 'low'.")
    message: str = Field(..., description="Human-readable description.")


class AnalysisResponse(BaseModel):
    """Successful response for the /analyze endpoint."""

    extracted_features: ExtractedFeatures
    risk_assessment: RiskAssessment
    issues: list[DiagnosticIssue] = Field(
        default_factory=list,
        description="Line-level diagnostic issues found in the code.",
    )


# ── Stub response models ──────────────────────────────

class TopFile(BaseModel):
    file: str
    score: int


class RepoSummaryResponse(BaseModel):
    repo_name: str
    energy_risk: int
    files_scanned: int
    energy_per_day: float
    co2_saved: float
    top_files: list[TopFile] = Field(default_factory=list)


class LineTiming(BaseModel):
    line: int
    time_ms: float


class FunctionCost(BaseModel):
    name: str
    energy: float


class ProfilingResponse(BaseModel):
    line_times: list[LineTiming]
    function_costs: list[FunctionCost]
    peak_memory: int
    total_energy: float


class CommitEntry(BaseModel):
    sha: str
    timestamp: str
    file: str
    message: str
    author: str
    delta: str
    co2_change: float
    risk: str


class ErrorResponse(BaseModel):
    """Consistent error response body."""

    detail: str
