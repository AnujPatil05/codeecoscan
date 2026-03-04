"""Configurable scoring rules for the Energy Risk Scoring Engine.

All weights and thresholds are stored in structured, immutable
configuration objects.  To tune the scoring system, modify the
values in ``DEFAULT_SCORING_RULES`` — no other file needs to change.

This module has zero dependencies on FastAPI, Pydantic, or any
external framework.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoopScoreRule:
    """Parameters for the quadratic loop-depth score.

    Formula: ``min(coefficient * depth², cap)``

    Attributes:
        coefficient: Multiplier for ``depth²``.
        cap: Maximum contribution from loop depth.
    """

    coefficient: int = 5
    cap: int = 40


@dataclass(frozen=True, slots=True)
class RecursionRule:
    """Tiered recursion scoring.

    Attributes:
        base: Score if recursion is detected.
        inside_loop_bonus: Additional score if recursion occurs
            inside a loop body.
    """

    base: int = 10
    inside_loop_bonus: int = 10


@dataclass(frozen=True, slots=True)
class HeavyImportRule:
    """Parameters for heavy-import scoring.

    Formula: ``min(per_module * count, cap)``

    Attributes:
        per_module: Score per heavy import module detected.
        cap: Maximum total contribution from heavy imports.
    """

    per_module: int = 8
    cap: int = 25


@dataclass(frozen=True, slots=True)
class ScoringRules:
    """Complete set of scoring weights and thresholds.

    All values are immutable.  To create a custom rule set, construct
    a new ``ScoringRules`` instance with the desired overrides.

    Attributes:
        loop_score: Quadratic loop-depth scoring parameters.
        interaction_penalty: Flat penalty when ``max_loop_depth >= 2``
            AND ``function_calls_inside_loops`` are both true.
        recursion: Tiered recursion scoring parameters.
        heavy_import: Heavy-import scoring parameters.
        score_cap: Absolute maximum for the final risk score.
        low_threshold: Scores in ``[0, low_threshold)`` are "Low" risk.
        moderate_threshold: Scores in ``[low_threshold, moderate_threshold)``
            are "Moderate" risk.  Scores ``>= moderate_threshold`` are "High".
    """

    loop_score: LoopScoreRule = LoopScoreRule()
    interaction_penalty: int = 15
    recursion: RecursionRule = RecursionRule()
    heavy_import: HeavyImportRule = HeavyImportRule()
    score_cap: int = 100
    low_threshold: int = 35
    moderate_threshold: int = 70


DEFAULT_SCORING_RULES: ScoringRules = ScoringRules()
"""Singleton default rule set used by ``EnergyRiskScorer``."""
