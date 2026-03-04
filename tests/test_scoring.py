"""Unit tests for EnergyRiskScorer (refined model).

Tests verify the quadratic loop formula, interaction penalty,
tiered recursion scoring, heavy import cap, score cap, and
risk level classification.
"""

from __future__ import annotations

from app.models.schemas import ExtractedFeatures, RiskAssessment
from app.scoring.scoring_engine import EnergyRiskScorer
from app.scoring.scoring_rules import ScoringRules


def _make_scorer(rules: ScoringRules | None = None) -> EnergyRiskScorer:
    """Factory for a scorer with optional custom rules."""
    return EnergyRiskScorer(rules=rules) if rules else EnergyRiskScorer()


def _make_features(
    max_loop_depth: int = 0,
    has_nested_loops: bool = False,
    function_calls_inside_loops: bool = False,
    has_recursion: bool = False,
    recursion_inside_loop: bool = False,
    heavy_imports_detected: list[str] | None = None,
) -> ExtractedFeatures:
    """Factory for ``ExtractedFeatures`` with sensible defaults."""
    return ExtractedFeatures(
        max_loop_depth=max_loop_depth,
        has_nested_loops=has_nested_loops,
        function_calls_inside_loops=function_calls_inside_loops,
        has_recursion=has_recursion,
        recursion_inside_loop=recursion_inside_loop,
        heavy_imports_detected=heavy_imports_detected or [],
    )


# ------------------------------------------------------------------
# Minimal code → Low risk
# ------------------------------------------------------------------


class TestMinimalCode:
    """Code with no features → score 0, Low."""

    def test_zero_score(self) -> None:
        result: RiskAssessment = _make_scorer().score(_make_features())
        assert result.energy_risk_score == 0
        assert result.risk_level == "Low"
        assert all(v == 0 for v in result.risk_breakdown.values())


# ------------------------------------------------------------------
# Quadratic loop scoring: min(5 * depth², 40)
# ------------------------------------------------------------------


class TestQuadraticLoopScoring:
    """Loop score = min(5 * depth², 40)."""

    def test_depth_0(self) -> None:
        result = _make_scorer().score(_make_features(max_loop_depth=0))
        assert result.risk_breakdown["loop_score"] == 0  # 5*0² = 0

    def test_depth_1(self) -> None:
        result = _make_scorer().score(_make_features(max_loop_depth=1))
        assert result.risk_breakdown["loop_score"] == 5  # 5*1² = 5

    def test_depth_2(self) -> None:
        result = _make_scorer().score(_make_features(max_loop_depth=2))
        assert result.risk_breakdown["loop_score"] == 20  # 5*2² = 20

    def test_depth_3(self) -> None:
        result = _make_scorer().score(_make_features(max_loop_depth=3))
        assert result.risk_breakdown["loop_score"] == 40  # min(5*9, 40) = 40

    def test_depth_5_capped(self) -> None:
        result = _make_scorer().score(_make_features(max_loop_depth=5))
        assert result.risk_breakdown["loop_score"] == 40  # min(5*25, 40) = 40


# ------------------------------------------------------------------
# Interaction penalty: depth >= 2 AND calls inside loops → +15
# ------------------------------------------------------------------


class TestInteractionPenalty:
    """Interaction penalty fires only when both conditions are true."""

    def test_depth_2_with_calls(self) -> None:
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=2,
                function_calls_inside_loops=True,
            )
        )
        assert result.risk_breakdown["interaction_penalty"] == 15

    def test_depth_2_without_calls(self) -> None:
        result = _make_scorer().score(
            _make_features(max_loop_depth=2)
        )
        assert result.risk_breakdown["interaction_penalty"] == 0

    def test_depth_1_with_calls(self) -> None:
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=1,
                function_calls_inside_loops=True,
            )
        )
        assert result.risk_breakdown["interaction_penalty"] == 0

    def test_no_loops_no_calls(self) -> None:
        result = _make_scorer().score(_make_features())
        assert result.risk_breakdown["interaction_penalty"] == 0


# ------------------------------------------------------------------
# Tiered recursion scoring
# ------------------------------------------------------------------


class TestRecursionScoring:
    """Recursion: +10 base, +10 additional if inside loop."""

    def test_recursion_only(self) -> None:
        result = _make_scorer().score(
            _make_features(has_recursion=True)
        )
        assert result.risk_breakdown["recursion"] == 10
        assert result.energy_risk_score == 10
        assert result.risk_level == "Low"

    def test_recursion_inside_loop(self) -> None:
        result = _make_scorer().score(
            _make_features(
                has_recursion=True,
                recursion_inside_loop=True,
            )
        )
        assert result.risk_breakdown["recursion"] == 20  # 10 + 10

    def test_no_recursion(self) -> None:
        result = _make_scorer().score(_make_features())
        assert result.risk_breakdown["recursion"] == 0


# ------------------------------------------------------------------
# Heavy imports: min(8 * count, 25)
# ------------------------------------------------------------------


class TestHeavyImportScoring:
    """Heavy import scoring with cap at 25."""

    def test_single_import(self) -> None:
        result = _make_scorer().score(
            _make_features(heavy_imports_detected=["torch"])
        )
        assert result.risk_breakdown["heavy_imports"] == 8  # 8*1

    def test_two_imports(self) -> None:
        result = _make_scorer().score(
            _make_features(heavy_imports_detected=["torch", "tensorflow"])
        )
        assert result.risk_breakdown["heavy_imports"] == 16  # 8*2

    def test_three_imports_at_cap(self) -> None:
        result = _make_scorer().score(
            _make_features(
                heavy_imports_detected=["torch", "tensorflow", "pandas"]
            )
        )
        # 8*3 = 24 < 25 → 24
        assert result.risk_breakdown["heavy_imports"] == 24

    def test_four_imports_capped(self) -> None:
        result = _make_scorer().score(
            _make_features(
                heavy_imports_detected=[
                    "torch", "tensorflow", "pandas", "sklearn"
                ]
            )
        )
        # 8*4 = 32 → capped at 25
        assert result.risk_breakdown["heavy_imports"] == 25


# ------------------------------------------------------------------
# Score cap at 100
# ------------------------------------------------------------------


class TestScoreCap:
    """Final score must never exceed 100."""

    def test_maximum_everything(self) -> None:
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=5,
                has_nested_loops=True,
                function_calls_inside_loops=True,
                has_recursion=True,
                recursion_inside_loop=True,
                heavy_imports_detected=[
                    "torch", "tensorflow", "pandas", "sklearn", "keras"
                ],
            )
        )
        # 40 (loop capped) + 15 (interaction) + 20 (recursion) + 25 (imports capped) = 100
        assert result.energy_risk_score == 100
        assert result.risk_level == "High"


# ------------------------------------------------------------------
# Risk level boundaries: 0–34 Low, 35–69 Moderate, 70–100 High
# ------------------------------------------------------------------


class TestRiskLevelBoundaries:
    """Exact boundary classification with new thresholds."""

    def test_score_0_is_low(self) -> None:
        result = _make_scorer().score(_make_features())
        assert result.risk_level == "Low"

    def test_score_34_is_low(self) -> None:
        """34 < 35 → Low."""
        # depth_2 (20) + recursion (10) = 30 → Low
        result = _make_scorer().score(
            _make_features(max_loop_depth=2, has_recursion=True)
        )
        assert result.energy_risk_score == 30
        assert result.risk_level == "Low"

    def test_score_35_is_moderate(self) -> None:
        """35 >= 35 → Moderate."""
        # depth_2 (20) + interaction (15) = 35
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=2,
                function_calls_inside_loops=True,
            )
        )
        assert result.energy_risk_score == 35
        assert result.risk_level == "Moderate"

    def test_score_69_is_moderate(self) -> None:
        """69 < 70 → Moderate."""
        # depth_3 (40) + recursion (10) + heavy 2 (16) = 66
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=3,
                has_recursion=True,
                heavy_imports_detected=["torch", "tensorflow"],
            )
        )
        assert result.energy_risk_score == 66
        assert result.risk_level == "Moderate"

    def test_score_70_is_high(self) -> None:
        """70 >= 70 → High."""
        # depth_3 (40) + interaction (15) + recursion_inside_loop (20) = 75
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=3,
                has_nested_loops=True,
                function_calls_inside_loops=True,
                has_recursion=True,
                recursion_inside_loop=True,
            )
        )
        assert result.energy_risk_score == 75
        assert result.risk_level == "High"


# ------------------------------------------------------------------
# End-to-end composite scenarios
# ------------------------------------------------------------------


class TestCompositeScenarios:
    """Full-stack scoring scenarios."""

    def test_nested_loops_with_calls_and_imports(self) -> None:
        """Depth 2, calls inside, 2 heavy imports."""
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=2,
                has_nested_loops=True,
                function_calls_inside_loops=True,
                heavy_imports_detected=["torch", "pandas"],
            )
        )
        # 20 (loop) + 15 (interaction) + 0 (recursion) + 16 (imports) = 51
        assert result.energy_risk_score == 51
        assert result.risk_level == "Moderate"

    def test_shallow_code_with_recursion_in_loop(self) -> None:
        """Depth 1, recursion inside that loop."""
        result = _make_scorer().score(
            _make_features(
                max_loop_depth=1,
                function_calls_inside_loops=True,
                has_recursion=True,
                recursion_inside_loop=True,
            )
        )
        # 5 (loop) + 0 (interaction, depth < 2) + 20 (recursion) = 25
        assert result.energy_risk_score == 25
        assert result.risk_level == "Low"


# ------------------------------------------------------------------
# Breakdown completeness
# ------------------------------------------------------------------


class TestBreakdownCompleteness:
    """Breakdown must always contain all four components."""

    def test_all_keys_present(self) -> None:
        result = _make_scorer().score(_make_features())
        expected_keys = {
            "loop_score",
            "interaction_penalty",
            "recursion",
            "heavy_imports",
        }
        assert set(result.risk_breakdown.keys()) == expected_keys


# ------------------------------------------------------------------
# Custom rules
# ------------------------------------------------------------------


class TestCustomRules:
    """Scorer must respect custom rule configurations."""

    def test_custom_recursion_weight(self) -> None:
        from app.scoring.scoring_rules import RecursionRule

        rules = ScoringRules(recursion=RecursionRule(base=30, inside_loop_bonus=20))
        result = _make_scorer(rules).score(
            _make_features(has_recursion=True, recursion_inside_loop=True)
        )
        assert result.risk_breakdown["recursion"] == 50  # 30 + 20

    def test_custom_thresholds(self) -> None:
        rules = ScoringRules(low_threshold=10, moderate_threshold=20)
        result = _make_scorer(rules).score(
            _make_features(has_recursion=True)  # score = 10
        )
        assert result.risk_level == "Moderate"  # 10 >= 10
