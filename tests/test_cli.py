"""Unit tests for the CodeEcoScan CLI.

Tests use temporary files and invoke ``main(argv)`` directly
to avoid subprocess overhead while testing the full pipeline.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

from app.cli.main import main


def _write_tmp_file(code: str, suffix: str = ".py") -> str:
    """Write code to a named temp file and return the path.

    The file is NOT deleted automatically — pytest's tmp handling
    or OS cleanup will manage it.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    )
    tmp.write(code)
    tmp.close()
    return tmp.name


# ------------------------------------------------------------------
# Valid file analysis
# ------------------------------------------------------------------


class TestValidFile:
    """CLI must analyze valid Python files successfully."""

    def test_simple_code_returns_0(self) -> None:
        path = _write_tmp_file("x = 1\n")
        exit_code = main([path, "--no-color"])
        assert exit_code == 0

    def test_full_output_contains_report(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file("for i in range(10):\n    print(i)\n")
        exit_code = main([path, "--no-color"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Energy Risk Score" in captured.out
        assert "Score Breakdown" in captured.out
        assert "Extracted Features" in captured.out

    def test_with_heavy_imports(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file("import torch\nimport pandas\nx = 1\n")
        exit_code = main([path, "--no-color"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "torch" in captured.out
        assert "pandas" in captured.out


# ------------------------------------------------------------------
# JSON output
# ------------------------------------------------------------------


class TestJsonOutput:
    """--json flag must output valid JSON matching API schema."""

    def test_json_output_is_valid(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file(
            "import torch\n"
            "for i in range(10):\n"
            "    for j in range(10):\n"
            "        print(i, j)\n"
        )
        exit_code = main([path, "--json"])
        assert exit_code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "extracted_features" in data
        assert "risk_assessment" in data
        assert isinstance(data["risk_assessment"]["energy_risk_score"], int)
        assert data["risk_assessment"]["risk_level"] in ("Low", "Moderate", "High")
        assert "torch" in data["extracted_features"]["heavy_imports_detected"]

    def test_json_has_all_breakdown_keys(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file("x = 1\n")
        main([path, "--json"])
        data = json.loads(capsys.readouterr().out)
        expected_keys = {"loop_score", "interaction_penalty", "recursion", "heavy_imports"}
        assert set(data["risk_assessment"]["risk_breakdown"].keys()) == expected_keys


# ------------------------------------------------------------------
# Score-only mode
# ------------------------------------------------------------------


class TestScoreOnly:
    """--score-only flag must output a single line."""

    def test_score_only_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file("x = 1\n")
        exit_code = main([path, "--score-only", "--no-color"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Score:" in captured.out
        assert "Risk:" in captured.out
        # Should be a single line
        lines = [l for l in captured.out.strip().splitlines() if l.strip()]
        assert len(lines) == 1


# ------------------------------------------------------------------
# Syntax error handling
# ------------------------------------------------------------------


class TestSyntaxError:
    """CLI must handle syntax errors gracefully."""

    def test_syntax_error_returns_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        path = _write_tmp_file("def foo(:\n    pass\n")
        exit_code = main([path, "--no-color"])
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Syntax error" in captured.err


# ------------------------------------------------------------------
# File not found
# ------------------------------------------------------------------


class TestFileNotFound:
    """CLI must exit cleanly when file doesn't exist."""

    def test_missing_file_returns_2(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["/nonexistent/path/to/file.py"])
        assert exc_info.value.code == 2


# ------------------------------------------------------------------
# Threshold (CI mode)
# ------------------------------------------------------------------


class TestThreshold:
    """--threshold flag controls exit code for CI integration."""

    def test_below_threshold_returns_0(self) -> None:
        path = _write_tmp_file("x = 1\n")  # score = 0
        exit_code = main([path, "--no-color", "--threshold", "70"])
        assert exit_code == 0

    def test_above_threshold_returns_1(self) -> None:
        path = _write_tmp_file(
            "import torch, tensorflow, pandas\n"
            "def process(data):\n"
            "    for i in data:\n"
            "        for j in i:\n"
            "            for k in j:\n"
            "                process(k)\n"
        )
        # High-scoring code: depth 3 + interaction + recursion_in_loop + imports
        exit_code = main([path, "--no-color", "--threshold", "50"])
        assert exit_code == 1
