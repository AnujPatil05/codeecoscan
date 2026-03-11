"""Repository scanner for CodeEcoScan.

Clones a GitHub repository (using git CLI via subprocess),
scans all .py files, runs the analyzer on each, and aggregates
results into a summary.

Uses a temporary directory per scan to avoid conflicts.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def _clone_repo(repo_url: str, target_dir: str, timeout: int = 60) -> None:
    """Clone a git repository into target_dir (shallow clone, depth=1)."""
    result = subprocess.run(
        ["git", "clone", "--depth=1", "--single-branch", repo_url, target_dir],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr[:500]}")


def _find_py_files(root: str, max_files: int = 100) -> list[Path]:
    """Find all .py files under root, excluding common non-application paths."""
    _SKIP_DIRS = {".git", "__pycache__", "venv", ".env", "node_modules", "dist", "build", ".tox"}
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                results.append(Path(dirpath) / fname)
                if len(results) >= max_files:
                    return results
    return results


def _analyze_file(path: Path, heavy_modules: frozenset[str]) -> dict[str, Any] | None:
    """Analyze a single .py file and return a result dict, or None on error."""
    try:
        code = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    if not code.strip():
        return None

    try:
        from app.analysis.ast_analyzer import CodeStructureAnalyzer
        from app.scoring.scoring_engine import EnergyRiskScorer
        from app.models.schemas import ExtractedFeatures

        analyzer = CodeStructureAnalyzer(heavy_import_modules=heavy_modules)
        result = analyzer.analyze(code)

        extractor_result = ExtractedFeatures(
            max_loop_depth=result.max_loop_depth,
            has_nested_loops=result.has_nested_loops,
            function_calls_inside_loops=result.function_calls_inside_loops,
            has_recursion=result.has_recursion,
            recursion_inside_loop=result.recursion_inside_loop,
            heavy_imports_detected=sorted(result.heavy_imports),
        )

        scorer = EnergyRiskScorer()
        assessment = scorer.score(extractor_result)

        return {
            "file": str(path.name),
            "score": assessment.energy_risk_score,
            "risk_level": assessment.risk_level,
            "breakdown": assessment.risk_breakdown,
        }
    except SyntaxError:
        return None
    except Exception:
        return None


def scan_repository(
    repo_url: str,
    heavy_modules: frozenset[str],
    max_files: int = 80,
    timeout: int = 60,
) -> dict[str, Any]:
    """Clone and scan a GitHub repository.

    Returns a summary dict with:
        repo_name, files_analyzed, repo_score, top_files, alerts
    """
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    tmpdir = tempfile.mkdtemp(prefix="codeecoscan_")
    clone_dir = os.path.join(tmpdir, "repo")

    try:
        _clone_repo(repo_url, clone_dir, timeout=timeout)
        py_files = _find_py_files(clone_dir, max_files=max_files)

        results: list[dict] = []
        for pyfile in py_files:
            r = _analyze_file(pyfile, heavy_modules)
            if r:
                results.append(r)

        if not results:
            return {
                "repo_name": repo_name,
                "files_analyzed": 0,
                "repo_score": 0,
                "top_files": [],
                "alerts": [],
                "error": "No analyzable Python files found.",
            }

        # Aggregate: risk-weighted mean
        total_score = sum(r["score"] for r in results)
        repo_score = int(round(total_score / len(results)))

        # Top files by score (descending)
        sorted_files = sorted(results, key=lambda r: r["score"], reverse=True)
        top_files = [{"file": r["file"], "score": r["score"]} for r in sorted_files[:10]]

        # Alerts: files with score >= 70
        alerts = [
            {"file": r["file"], "issue": f"Energy Risk: {r['risk_level']} ({r['score']}/100)"}
            for r in sorted_files if r["score"] >= 70
        ]

        return {
            "repo_name": repo_name,
            "files_analyzed": len(results),
            "repo_score": repo_score,
            "top_files": top_files,
            "alerts": alerts,
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
