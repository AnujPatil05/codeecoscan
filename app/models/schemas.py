"""Pydantic schemas for API request/response models.

All models use Pydantic v2 ``BaseModel`` with strict type annotations.
"""

from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    """Request body for the ``POST /analyze`` endpoint.

    Attributes:
        code: Raw Python source code to analyze. Must be non-empty.
    """

    code: str = Field(
        ...,
        min_length=1,
        description="Raw Python source code to analyze.",
        examples=["def hello():\n    print('world')"],
    )


class ExtractedFeatures(BaseModel):
    """Structural features extracted from the submitted code.

    Attributes:
        max_loop_depth: Deepest nesting level of loops found (0 if none).
        has_nested_loops: True if any loop is nested inside another.
        function_calls_inside_loops: True if any ``Call`` node appears
            inside a loop body.
        has_recursion: True if direct recursion is detected (a function
            calling itself by name).
        heavy_imports_detected: Sorted list of energy-heavy module names
            found in import statements.
    """

    max_loop_depth: int = Field(
        ..., ge=0, description="Maximum loop nesting depth."
    )
    has_nested_loops: bool = Field(
        ..., description="Whether nested loops exist."
    )
    function_calls_inside_loops: bool = Field(
        ..., description="Whether function calls occur inside loops."
    )
    has_recursion: bool = Field(
        ..., description="Whether direct recursion is detected."
    )
    recursion_inside_loop: bool = Field(
        ..., description="Whether a recursive call occurs inside a loop body."
    )
    heavy_imports_detected: list[str] = Field(
        ..., description="List of detected heavy import module names."
    )


class RiskAssessment(BaseModel):
    """Energy risk scoring result.

    Attributes:
        energy_risk_score: Overall risk score from 0 to 100.
        risk_level: Classification — ``"Low"``, ``"Moderate"``, or
            ``"High"``.
        risk_breakdown: Per-component score contributions.
    """

    energy_risk_score: int = Field(
        ..., ge=0, le=100, description="Overall energy risk score (0–100)."
    )
    risk_level: str = Field(
        ..., description='Risk classification: "Low", "Moderate", or "High".',
    )
    risk_breakdown: dict[str, int] = Field(
        ..., description="Per-component score contributions.",
    )


class AnalysisResponse(BaseModel):
    """Successful response wrapper for the analysis endpoint.

    Attributes:
        extracted_features: The structural analysis results.
        risk_assessment: The energy risk scoring results.
    """

    extracted_features: ExtractedFeatures
    risk_assessment: RiskAssessment


class ErrorResponse(BaseModel):
    """Consistent error response body.

    Attributes:
        detail: Human-readable error description.
    """

    detail: str
