"""Energy Risk Scoring Engine.

Translates ``ExtractedFeatures`` into a deterministic, explainable
risk assessment using configurable weighted rules.

This module is **framework-agnostic** — it depends only on the
Pydantic models in ``app.models.schemas`` and the scoring rules
in ``app.scoring.scoring_rules``.  It can be used from FastAPI
routes, CLI tools, or batch pipelines without modification.

Thread-safety guarantee
-----------------------
``EnergyRiskScorer`` stores only an immutable ``ScoringRules``
reference.  The ``score()`` method is a pure function with no
side effects — it reads the input, computes a result, and returns
it.  No mutable state is involved.

Scoring formula
---------------
::

    loop_score       = min(coefficient * depth², cap)
    interaction      = penalty  IF depth >= 2 AND calls_inside_loops
    recursion_score  = base     IF has_recursion
                     + bonus    IF recursion_inside_loop
    heavy_score      = min(per_module * count, cap)

    total = clamp(sum, 0, score_cap)
"""

from __future__ import annotations

from app.models.schemas import ExtractedFeatures, RiskAssessment
from app.scoring.scoring_rules import DEFAULT_SCORING_RULES, ScoringRules


class EnergyRiskScorer:
    """Deterministic energy-risk scorer.

    Computes a weighted risk score from structural code features
    and classifies it into a risk level.

    Args:
        rules: Scoring rules to use.  Defaults to
            ``DEFAULT_SCORING_RULES``.
    """

    def __init__(self, rules: ScoringRules = DEFAULT_SCORING_RULES) -> None:
        self._rules: ScoringRules = rules

    def score(self, features: ExtractedFeatures) -> RiskAssessment:
        """Compute risk assessment from extracted features.

        Args:
            features: Structural features from the analysis engine.

        Returns:
            A fully populated ``RiskAssessment`` with score,
            risk level, and per-component breakdown.
        """
        breakdown: dict[str, int] = {}

        # --- Loop complexity score: min(coeff * depth², cap) ---
        loop_score: int = min(
            self._rules.loop_score.coefficient
            * (features.max_loop_depth ** 2),
            self._rules.loop_score.cap,
        )
        breakdown["loop_score"] = loop_score

        # --- Interaction penalty: depth >= 2 AND calls inside loops ---
        interaction: int = (
            self._rules.interaction_penalty
            if (
                features.max_loop_depth >= 2
                and features.function_calls_inside_loops
            )
            else 0
        )
        breakdown["interaction_penalty"] = interaction

        # --- Recursion: base + optional inside-loop bonus ---
        recursion_score: int = 0
        if features.has_recursion:
            recursion_score += self._rules.recursion.base
            if features.recursion_inside_loop:
                recursion_score += self._rules.recursion.inside_loop_bonus
        breakdown["recursion"] = recursion_score

        # --- Heavy imports: min(per_module * count, cap) ---
        heavy_score: int = min(
            self._rules.heavy_import.per_module
            * len(features.heavy_imports_detected),
            self._rules.heavy_import.cap,
        )
        breakdown["heavy_imports"] = heavy_score

        # --- Aggregate ---
        raw_total: int = sum(breakdown.values())
        capped_total: int = max(0, min(raw_total, self._rules.score_cap))

        risk_level: str = self._classify(capped_total)

        return RiskAssessment(
            energy_risk_score=capped_total,
            risk_level=risk_level,
            risk_breakdown=breakdown,
        )

    def _classify(self, score: int) -> str:
        """Classify a numeric score into a risk level string."""
        if score < self._rules.low_threshold:
            return "Low"
        if score < self._rules.moderate_threshold:
            return "Moderate"
        return "High"
