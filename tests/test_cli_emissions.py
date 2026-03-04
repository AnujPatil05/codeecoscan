"""Unit tests for CLI emissions integration.

Tests verify emissions flags, comparison mode, JSON output with
emissions, validation errors, and interactions with --score-only
and --threshold.
"""

from __future__ import annotations

import json
import tempfile

import pytest

from app.cli.main import main


def _write_tmp_file(code: str) -> str:
    """Write code to a temp file and return the path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    tmp.write(code)
    tmp.close()
    return tmp.name


_SIMPLE_CODE = "x = 1\n"
_LOOP_CODE = (
    "import torch\n"
    "for i in range(10):\n"
    "    for j in range(10):\n"
    "        print(i, j)\n"
)


# ------------------------------------------------------------------
# Single hardware emissions
# ------------------------------------------------------------------


class TestSingleHardwareEmissions:
    """--runtime + --runs-per-day + --hardware triggers emissions."""

    def test_laptop_emissions_printed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
        ])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Emissions Estimate" in out
        assert "laptop" in out
        assert "Wh/day" in out
        assert "kg/day" in out

    def test_gpu_server_emissions(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "300",
            "--runs-per-day", "100",
            "--hardware", "gpu_server",
        ])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "gpu_server" in out


# ------------------------------------------------------------------
# Compare mode
# ------------------------------------------------------------------


class TestCompareMode:
    """--compare produces a comparison table."""

    def test_compare_two_profiles(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--compare", "laptop", "gpu_server",
        ])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Emissions Comparison" in out
        assert "laptop" in out
        assert "gpu_server" in out

    def test_compare_ignores_hardware_flag(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--compare takes priority over --hardware."""
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
            "--compare", "small_cloud_vm", "gpu_server",
        ])
        assert exit_code == 0
        out = capsys.readouterr().out
        # Should show compare table, not single laptop
        assert "Emissions Comparison" in out
        assert "small_cloud_vm" in out
        assert "gpu_server" in out


# ------------------------------------------------------------------
# Missing param errors
# ------------------------------------------------------------------


class TestMissingParamErrors:
    """Incomplete emissions flags → error exit 2."""

    def test_runtime_without_runs(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--hardware", "laptop",
        ])
        assert exit_code == 2
        err = capsys.readouterr().err
        assert "--runtime" in err and "--runs-per-day" in err

    def test_runs_without_runtime(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runs-per-day", "10",
            "--hardware", "laptop",
        ])
        assert exit_code == 2
        err = capsys.readouterr().err
        assert "--runtime" in err

    def test_runtime_and_runs_without_hardware(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
        ])
        assert exit_code == 2
        err = capsys.readouterr().err
        assert "--hardware" in err or "--compare" in err

    def test_invalid_hardware_profile(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "mainframe",
        ])
        assert exit_code == 2
        err = capsys.readouterr().err
        assert "Unknown hardware profile" in err


# ------------------------------------------------------------------
# JSON mode with emissions
# ------------------------------------------------------------------


class TestJsonWithEmissions:
    """--json includes emissions data."""

    def test_json_single_hardware(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--json",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
        ])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert "emissions_estimate" in data
        assert data["emissions_estimate"]["hardware_profile"] == "laptop"
        assert "energy_wh_per_day" in data["emissions_estimate"]

    def test_json_compare_mode(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--json",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--compare", "laptop", "gpu_server",
        ])
        assert exit_code == 0
        data = json.loads(capsys.readouterr().out)
        assert "emissions_comparison" in data
        assert "laptop" in data["emissions_comparison"]
        assert "gpu_server" in data["emissions_comparison"]

    def test_json_without_emissions_flags(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """JSON without emissions flags → no emissions keys."""
        path = _write_tmp_file(_SIMPLE_CODE)
        main([path, "--json"])
        data = json.loads(capsys.readouterr().out)
        assert "emissions_estimate" not in data
        assert "emissions_comparison" not in data


# ------------------------------------------------------------------
# --score-only ignores emissions
# ------------------------------------------------------------------


class TestScoreOnlyIgnoresEmissions:
    """--score-only must never print emissions output."""

    def test_score_only_with_emissions_flags(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)
        exit_code = main([
            path, "--score-only", "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
        ])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Score:" in out
        assert "Emissions" not in out
        assert "Wh/day" not in out


# ------------------------------------------------------------------
# Threshold still works with emissions
# ------------------------------------------------------------------


class TestThresholdWithEmissions:
    """--threshold exit codes are unaffected by emissions flags."""

    def test_below_threshold_with_emissions(self) -> None:
        path = _write_tmp_file(_SIMPLE_CODE)  # score = 0
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
            "--threshold", "70",
        ])
        assert exit_code == 0

    def test_above_threshold_with_emissions(self) -> None:
        path = _write_tmp_file(_LOOP_CODE)  # high-scoring code
        exit_code = main([
            path, "--no-color",
            "--runtime", "60",
            "--runs-per-day", "10",
            "--hardware", "laptop",
            "--threshold", "30",
        ])
        assert exit_code == 1
