"""Repository scanner — hardened for production security.

Security guarantees:
- URL restricted to https://github.com/* (no file://, ssh://, etc.)
- subprocess never joins user input into a shell string (uses list argv)
- Temp dir is always cleaned up (finally block)
- File size capped at MAX_FILE_BYTES to prevent OOM
- Max files and wall-clock timeout prevent runaway scans on large repos

Temp directory path: /tmp/codeecoscan_<uuid> — deleted on scan completion.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


# ── Security constants ─────────────────────────────────────────────

_ALLOWED_URL_RE = re.compile(r'^https://github\.com/[\w.\-]+/[\w.\-]+(\.git)?/?$')
MAX_FILE_BYTES = 500_000   # 500 KB — skip anything larger
MAX_FILES      = 60        # analyze at most 60 .py files
CLONE_TIMEOUT  = 45        # seconds for git clone
SCAN_TIMEOUT   = 60        # total wall-clock budget for scan phase
_SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".env", ".venv", "env",
    "node_modules", "dist", "build", ".tox", "htmlcov", "docs",
    "site-packages", "migrations",
}


def _validate_url(repo_url: str) -> None:
    """Raise ValueError if the URL does not match the allowed pattern.

    Only https://github.com/<owner>/<repo> URLs are permitted.
    This prevents file://, ssh://, git://, and other protocol injection.
    """
    if not _ALLOWED_URL_RE.match(repo_url.strip()):
        raise ValueError(
            "Repository URL must match https://github.com/<owner>/<repo>. "
            f"Got: {repo_url!r}"
        )


def _safe_name(repo_url: str) -> str:
    """Extract repo name safely from a validated GitHub URL."""
    return repo_url.rstrip("/").rstrip(".git").split("/")[-1]


def _clone_repo(repo_url: str, target_dir: str, timeout: int = CLONE_TIMEOUT) -> None:
    """Shallow-clone (depth=1) a validated GitHub URL into target_dir.

    Uses list-form subprocess to prevent shell injection.
    stderr is captured and redacted before being surfaced.
    """
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--single-branch", repo_url, target_dir],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Repository clone timed out (>45s). Try a smaller repo.")

    if result.returncode != 0:
        # Redact the URL from stderr in case it contains tokens
        msg = result.stderr[:300].replace(repo_url, "<repo>")
        raise RuntimeError(f"Git clone failed: {msg}")


def _find_py_files(root: str, max_files: int = MAX_FILES) -> list[Path]:
    """Walk root, returning up to max_files .py files, skipping known noise dirs."""
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                p = Path(dirpath) / fname
                # Skip if file is too large
                try:
                    if p.stat().st_size > MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                results.append(p)
                if len(results) >= max_files:
                    return results
    return results


def _analyze_file(path: Path, heavy_modules: frozenset[str]) -> dict[str, Any] | None:
    """Analyze a single .py file. Returns None on any error (syntax, IO, etc.)."""
    try:
        code = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    if not code.strip():
        return None

    try:
        from app.analysis.ast_analyzer import CodeStructureAnalyzer
        from app.models.schemas import ExtractedFeatures
        from app.scoring.scoring_engine import EnergyRiskScorer

        analyzer = CodeStructureAnalyzer(heavy_import_modules=heavy_modules)
        result = analyzer.analyze(code)

        features = ExtractedFeatures(
            max_loop_depth=result.max_loop_depth,
            has_nested_loops=result.has_nested_loops,
            function_calls_inside_loops=result.function_calls_inside_loops,
            has_recursion=result.has_recursion,
            recursion_inside_loop=result.recursion_inside_loop,
            heavy_imports_detected=sorted(result.heavy_imports),
        )

        assessment = EnergyRiskScorer().score(features)
        return {
            "file": str(path.name),
            "score": assessment.energy_risk_score,
            "risk_level": assessment.risk_level,
            "breakdown": assessment.risk_breakdown,
        }
    except (SyntaxError, RecursionError, MemoryError, ValueError):
        return None
    except Exception:
        return None


def scan_repository(
    repo_url: str,
    heavy_modules: frozenset[str],
    max_files: int = MAX_FILES,
    timeout: int = CLONE_TIMEOUT,
) -> dict[str, Any]:
    """Clone and scan a GitHub repository.

    Security-hardened entry point:
    1. Validates URL against the https://github.com/* allowlist.
    2. Uses subprocess in list-argv mode (no shell injection).
    3. Deletes the temp dir in a finally block regardless of outcome.
    4. Skips files > 500 KB to prevent OOM.
    5. Stops after MAX_FILES to cap wall-clock time.

    Large repos (django, scikit-learn, etc.) are handled by the file cap —
    only the first 60 Python files are analyzed. For full-repo scans, use
    the async /analyze_repo endpoint which runs this in a background task.

    Returns a summary dict with: repo_name, files_analyzed, repo_score,
    top_files, alerts.
    """
    _validate_url(repo_url)

    repo_name = _safe_name(repo_url)
    tmpdir = tempfile.mkdtemp(prefix="codeecoscan_")
    clone_dir = os.path.join(tmpdir, "repo")

    try:
        _clone_repo(repo_url, clone_dir, timeout=timeout)
        py_files = _find_py_files(clone_dir, max_files=max_files)

        deadline = time.monotonic() + SCAN_TIMEOUT
        results: list[dict] = []
        for pyfile in py_files:
            if time.monotonic() > deadline:
                break
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
                "error": "No analyzable Python files found (all may have syntax errors or exceed the 500 KB file limit).",
            }

        repo_score = int(round(sum(r["score"] for r in results) / len(results)))
        sorted_files = sorted(results, key=lambda r: r["score"], reverse=True)
        top_files = [{"file": r["file"], "score": r["score"]} for r in sorted_files[:10]]
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
        # Always delete the temp dir — disk space safety guarantee
        shutil.rmtree(tmpdir, ignore_errors=True)
