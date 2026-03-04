"""CodeEcoScan CLI — command-line interface for static energy-risk analysis.

Library-mode interface that reads a Python file, runs it through
the same ``FeatureExtractor`` + ``EnergyRiskScorer`` pipeline as the
API, and optionally computes emissions estimates.

This module has **zero FastAPI dependency**.  It imports only from
the analysis, scoring, emissions, core, and models layers.

Usage::

    python -m app.cli.main path/to/file.py
    python -m app.cli.main path/to/file.py --json
    python -m app.cli.main path/to/file.py --score-only
    python -m app.cli.main path/to/file.py --no-color
    python -m app.cli.main path/to/file.py --threshold 70

    # Emissions estimation
    python -m app.cli.main path/to/file.py --runtime 60 --runs-per-day 10 --hardware laptop
    python -m app.cli.main path/to/file.py --runtime 60 --runs-per-day 10 --compare laptop gpu_server
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.analysis.feature_extractor import FeatureExtractor, MAX_CODE_LENGTH
from app.core.config import Settings
from app.core.exceptions import CodeParsingError, AnalysisError
from app.emissions.carbon_estimator import CarbonEstimator
from app.emissions.models import EmissionsEstimate
from app.models.schemas import AnalysisResponse, ExtractedFeatures, RiskAssessment
from app.scoring.scoring_engine import EnergyRiskScorer

# ---------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_GREEN = "\033[92m"
_CYAN = "\033[96m"
_DIM = "\033[2m"

_RISK_COLORS: dict[str, str] = {
    "Low": _GREEN,
    "Moderate": _YELLOW,
    "High": _RED,
}


def _colorize(text: str, color: str, *, use_color: bool = True) -> str:
    """Wrap ``text`` in ANSI color codes if color is enabled."""
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


# ---------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser.

    Returns:
        Configured ``ArgumentParser`` instance.
    """
    parser = argparse.ArgumentParser(
        prog="codeecoscan",
        description="CodeEcoScan — static energy-risk analysis for Python code.",
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the Python file to analyze.",
    )

    # Output format flags
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output full analysis as JSON (matches API response format).",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Output only the numeric score and risk level.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Exit with code 1 if score >= N. "
            "Makes CodeEcoScan CI-compatible."
        ),
    )

    # Emissions flags
    parser.add_argument(
        "--runtime",
        type=float,
        default=None,
        metavar="SECS",
        help="Runtime of a single execution in seconds.",
    )
    parser.add_argument(
        "--runs-per-day",
        type=int,
        default=None,
        metavar="N",
        help="Number of executions per day.",
    )
    parser.add_argument(
        "--hardware",
        type=str,
        default=None,
        metavar="PROFILE",
        help='Hardware profile: "laptop", "small_cloud_vm", or "gpu_server".',
    )
    parser.add_argument(
        "--carbon-intensity",
        type=float,
        default=0.4,
        metavar="F",
        help=(
            "Grid carbon intensity in kg CO\u2082/kWh. "
            "Default: 0.4 (global grid average, IEA estimate)."
        ),
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        default=None,
        metavar="PROFILE",
        help="Compare emissions across multiple hardware profiles.",
    )

    return parser


# ---------------------------------------------------------------
# File reading
# ---------------------------------------------------------------


def read_file(filepath: str) -> str:
    """Read and return file contents.

    Args:
        filepath: Path to the Python source file.

    Returns:
        File contents as a string.

    Raises:
        SystemExit: If the file is not found or unreadable.
    """
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(2)

    if not path.is_file():
        print(f"Error: Not a file: {filepath}", file=sys.stderr)
        sys.exit(2)

    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: Cannot read file: {exc}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------
# Analysis pipeline
# ---------------------------------------------------------------


def analyze(code: str) -> AnalysisResponse:
    """Run the full analysis + scoring pipeline.

    Args:
        code: Raw Python source code.

    Returns:
        An ``AnalysisResponse`` containing features and risk assessment.

    Raises:
        CodeParsingError: On syntax errors.
        AnalysisError: On unexpected analysis failures.
    """
    settings = Settings()
    extractor = FeatureExtractor(settings=settings)
    scorer = EnergyRiskScorer()

    features: ExtractedFeatures = extractor.extract(code)
    assessment: RiskAssessment = scorer.score(features)

    return AnalysisResponse(
        extracted_features=features,
        risk_assessment=assessment,
    )


# ---------------------------------------------------------------
# Emissions helpers
# ---------------------------------------------------------------


def _validate_emissions_args(args: argparse.Namespace) -> str | None:
    """Validate emissions flag combinations.

    Returns:
        An error message string if validation fails, else ``None``.
    """
    has_runtime = args.runtime is not None
    has_runs = args.runs_per_day is not None
    has_hw = args.hardware is not None
    has_compare = args.compare is not None

    # No emissions flags at all → nothing to validate
    if not has_runtime and not has_runs and not has_hw and not has_compare:
        return None

    # Partial specification
    if not has_runtime or not has_runs:
        return (
            "--runtime and --runs-per-day are both required "
            "for emissions estimation."
        )

    if not has_hw and not has_compare:
        return (
            "Either --hardware or --compare is required "
            "for emissions estimation."
        )

    return None


def _wants_emissions(args: argparse.Namespace) -> bool:
    """Return True if the user requested emissions estimation."""
    return (
        args.runtime is not None
        and args.runs_per_day is not None
        and (args.hardware is not None or args.compare is not None)
    )


def _compute_emissions(
    args: argparse.Namespace,
    assessment: RiskAssessment,
) -> dict[str, EmissionsEstimate]:
    """Compute emissions for one or more hardware profiles.

    Args:
        args: Parsed CLI arguments.
        assessment: Risk assessment from the scoring engine.

    Returns:
        Dict mapping profile name → ``EmissionsEstimate``.

    Raises:
        ValueError: If a hardware profile name is invalid.
    """
    estimator = CarbonEstimator()
    profiles: list[str] = (
        args.compare if args.compare is not None else [args.hardware]
    )

    results: dict[str, EmissionsEstimate] = {}
    for profile in profiles:
        results[profile] = estimator.estimate(
            risk_assessment=assessment,
            runtime_seconds=args.runtime,
            runs_per_day=args.runs_per_day,
            hardware_profile=profile,
            carbon_intensity=args.carbon_intensity,
        )
    return results


# ---------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------


def print_json(
    response: AnalysisResponse,
    emissions: dict[str, EmissionsEstimate] | None = None,
) -> None:
    """Print the full analysis response as formatted JSON."""
    data: dict = response.model_dump()

    if emissions is not None:
        if len(emissions) == 1:
            # Single hardware → emissions_estimate
            data["emissions_estimate"] = next(iter(emissions.values())).model_dump()
        else:
            # Multiple → emissions_comparison
            data["emissions_comparison"] = {
                name: est.model_dump() for name, est in emissions.items()
            }

    print(json.dumps(data, indent=2))


def print_score_only(
    assessment: RiskAssessment, *, use_color: bool = True
) -> None:
    """Print only the score and risk level."""
    level_color = _RISK_COLORS.get(assessment.risk_level, "")
    colored_level = _colorize(assessment.risk_level, level_color, use_color=use_color)
    score_str = _colorize(str(assessment.energy_risk_score), _BOLD, use_color=use_color)
    print(f"Score: {score_str}/100  Risk: {colored_level}")


def print_emissions_single(
    estimate: EmissionsEstimate, *, use_color: bool = True
) -> None:
    """Print emissions for a single hardware profile."""
    header = _colorize("Emissions Estimate", _BOLD + _CYAN, use_color=use_color)
    _times = "\u00d7"
    _sub2 = "\u2082"
    print(f"\n  {header}")
    print(f"    Hardware:            {estimate.hardware_profile}")
    print(f"    Runtime:             {estimate.runtime_seconds}s {_times} {estimate.runs_per_day} runs/day")
    print(f"    Energy:              {estimate.energy_wh_per_day:.2f} Wh/day")
    print(f"    CO{_sub2}:                 {estimate.co2_kg_per_day:.4f} kg/day")
    print(f"    Carbon intensity:    {estimate.carbon_intensity_used} kg CO{_sub2}/kWh (global grid avg, IEA)")


def print_emissions_comparison(
    emissions: dict[str, EmissionsEstimate], *, use_color: bool = True
) -> None:
    """Print a comparison table across multiple hardware profiles."""
    header = _colorize("Emissions Comparison", _BOLD + _CYAN, use_color=use_color)
    _sub2 = "\u2082"
    _dash = "\u2500"
    co2_header = f"CO{_sub2} (kg/day)"
    print(f"\n  {header}")
    print(f"    {'Profile':<20s} {'Energy (Wh/day)':>16s} {co2_header:>14s}")
    print(f"    {_dash * 20} {_dash * 16} {_dash * 14}")
    for name, est in emissions.items():
        print(f"    {name:<20s} {est.energy_wh_per_day:>16.2f} {est.co2_kg_per_day:>14.4f}")


def print_full(
    response: AnalysisResponse,
    emissions: dict[str, EmissionsEstimate] | None = None,
    *,
    use_color: bool = True,
) -> None:
    """Print the complete human-readable analysis report."""
    features = response.extracted_features
    assessment = response.risk_assessment

    # Header
    header = _colorize("CodeEcoScan Analysis Report", _BOLD + _CYAN, use_color=use_color)
    print(f"\n{header}")
    print(_colorize("=" * 40, _DIM, use_color=use_color))

    # Risk score
    level_color = _RISK_COLORS.get(assessment.risk_level, "")
    score_str = _colorize(
        f"{assessment.energy_risk_score}/100", _BOLD, use_color=use_color
    )
    level_str = _colorize(assessment.risk_level, level_color + _BOLD, use_color=use_color)
    print(f"\n  Energy Risk Score: {score_str}  [{level_str}]")

    # Breakdown
    print(f"\n  {_colorize('Score Breakdown:', _BOLD, use_color=use_color)}")
    for component, value in assessment.risk_breakdown.items():
        label = component.replace("_", " ").title()
        val_str = _colorize(f"+{value}", _BOLD, use_color=use_color) if value > 0 else " 0"
        print(f"    {label:<30s} {val_str}")

    # Features
    print(f"\n  {_colorize('Extracted Features:', _BOLD, use_color=use_color)}")
    print(f"    Max loop depth:              {features.max_loop_depth}")
    print(f"    Nested loops:                {features.has_nested_loops}")
    print(f"    Calls inside loops:          {features.function_calls_inside_loops}")
    print(f"    Recursion:                   {features.has_recursion}")
    print(f"    Recursion inside loop:       {features.recursion_inside_loop}")
    if features.heavy_imports_detected:
        imports_str = ", ".join(features.heavy_imports_detected)
        print(f"    Heavy imports:               {imports_str}")
    else:
        print(f"    Heavy imports:               (none)")

    # Emissions (if present)
    if emissions is not None:
        if len(emissions) == 1:
            print_emissions_single(
                next(iter(emissions.values())), use_color=use_color
            )
        else:
            print_emissions_comparison(emissions, use_color=use_color)

    print()


# ---------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Output is printed exactly once by one of three mutually exclusive
    formatters.  The threshold check runs independently afterward
    and only affects the exit code — it never produces output.

    When ``--threshold`` is set without ``--json`` or ``--score-only``,
    the output defaults to score-only mode to keep CI logs clean.

    Emissions are computed only when ``--runtime``, ``--runs-per-day``,
    and either ``--hardware`` or ``--compare`` are all provided.
    The ``--score-only`` mode always ignores emissions output.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Exit code: 0 for success (or score below threshold),
        1 if score >= threshold, 2 for errors.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color: bool = not args.no_color

    # --- Read file ---
    code: str = read_file(args.file)

    # --- Analyze ---
    try:
        response: AnalysisResponse = analyze(code)
    except CodeParsingError as exc:
        print(
            _colorize(f"Error: {exc.message}", _RED, use_color=use_color),
            file=sys.stderr,
        )
        return 2
    except AnalysisError as exc:
        print(
            _colorize(f"Error: {exc.message}", _RED, use_color=use_color),
            file=sys.stderr,
        )
        return 2

    # --- Emissions (optional) ---
    emissions: dict[str, EmissionsEstimate] | None = None

    validation_error = _validate_emissions_args(args)
    if validation_error is not None:
        print(f"Error: {validation_error}", file=sys.stderr)
        return 2

    if _wants_emissions(args):
        try:
            emissions = _compute_emissions(args, response.risk_assessment)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

    # --- Output (exactly once — mutually exclusive branches) ---
    if args.json_output:
        print_json(response, emissions)
    elif args.score_only or args.threshold is not None:
        # --score-only OR --threshold without explicit format → score-only
        # Score-only NEVER includes emissions output
        print_score_only(response.risk_assessment, use_color=use_color)
    else:
        print_full(response, emissions, use_color=use_color)

    # --- Threshold check (exit code only, no additional output) ---
    if args.threshold is not None:
        if response.risk_assessment.energy_risk_score >= args.threshold:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
