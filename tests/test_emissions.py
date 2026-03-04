"""Unit tests for CarbonEstimator and hardware profiles.

Tests verify deterministic emissions math, hardware profile lookup,
edge cases, and custom carbon intensity.
"""

from __future__ import annotations

import pytest

from app.emissions.carbon_estimator import CarbonEstimator
from app.emissions.hardware_profiles import get_profile, LAPTOP, SMALL_CLOUD_VM, GPU_SERVER
from app.emissions.models import EmissionsEstimate
from app.models.schemas import RiskAssessment


def _make_assessment(score: int = 0) -> RiskAssessment:
    """Factory for a minimal RiskAssessment."""
    return RiskAssessment(
        energy_risk_score=score,
        risk_level="Low",
        risk_breakdown={
            "loop_score": 0,
            "interaction_penalty": 0,
            "recursion": 0,
            "heavy_imports": 0,
        },
    )


# ------------------------------------------------------------------
# Hardware profile lookup
# ------------------------------------------------------------------


class TestHardwareProfiles:
    """Built-in profile lookup and validation."""

    def test_laptop_profile(self) -> None:
        p = get_profile("laptop")
        assert p.name == "laptop"
        assert p.power_watts == 45.0

    def test_small_cloud_vm_profile(self) -> None:
        p = get_profile("small_cloud_vm")
        assert p.name == "small_cloud_vm"
        assert p.power_watts == 120.0

    def test_gpu_server_profile(self) -> None:
        p = get_profile("gpu_server")
        assert p.name == "gpu_server"
        assert p.power_watts == 300.0

    def test_invalid_profile_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown hardware profile"):
            get_profile("quantum_computer")


# ------------------------------------------------------------------
# Laptop scenario
# ------------------------------------------------------------------


class TestLaptopScenario:
    """Laptop (45W), 60s runtime, 10 runs/day."""

    def test_laptop_emissions(self) -> None:
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=60.0,
            runs_per_day=10,
            hardware_profile="laptop",
        )
        # energy_wh_per_run = (45 × 60) / 3600 = 0.75 Wh
        # energy_wh_per_day = 0.75 × 10 = 7.5 Wh
        # co2_kg_per_day = (7.5 / 1000) × 0.4 = 0.003 kg
        assert result.energy_wh_per_day == pytest.approx(7.5)
        assert result.co2_kg_per_day == pytest.approx(0.003)
        assert result.hardware_profile == "laptop"
        assert result.carbon_intensity_used == 0.4


# ------------------------------------------------------------------
# Small VM scenario
# ------------------------------------------------------------------


class TestSmallVMScenario:
    """Small cloud VM (120W), 120s runtime, 50 runs/day."""

    def test_small_vm_emissions(self) -> None:
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=120.0,
            runs_per_day=50,
            hardware_profile="small_cloud_vm",
        )
        # energy_wh_per_run = (120 × 120) / 3600 = 4.0 Wh
        # energy_wh_per_day = 4.0 × 50 = 200.0 Wh
        # co2_kg_per_day = (200 / 1000) × 0.4 = 0.08 kg
        assert result.energy_wh_per_day == pytest.approx(200.0)
        assert result.co2_kg_per_day == pytest.approx(0.08)


# ------------------------------------------------------------------
# GPU server scenario
# ------------------------------------------------------------------


class TestGPUServerScenario:
    """GPU server (300W), 300s runtime, 100 runs/day."""

    def test_gpu_server_emissions(self) -> None:
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=300.0,
            runs_per_day=100,
            hardware_profile="gpu_server",
        )
        # energy_wh_per_run = (300 × 300) / 3600 = 25.0 Wh
        # energy_wh_per_day = 25.0 × 100 = 2500.0 Wh
        # co2_kg_per_day = (2500 / 1000) × 0.4 = 1.0 kg
        assert result.energy_wh_per_day == pytest.approx(2500.0)
        assert result.co2_kg_per_day == pytest.approx(1.0)


# ------------------------------------------------------------------
# Custom carbon intensity
# ------------------------------------------------------------------


class TestCustomCarbonIntensity:
    """Override default carbon intensity factor."""

    def test_high_carbon_grid(self) -> None:
        """Coal-heavy grid: 0.9 kg CO₂/kWh."""
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=60.0,
            runs_per_day=10,
            hardware_profile="laptop",
            carbon_intensity=0.9,
        )
        # energy_wh_per_day = 7.5 Wh (same as laptop scenario)
        # co2_kg_per_day = (7.5 / 1000) × 0.9 = 0.00675 kg
        assert result.co2_kg_per_day == pytest.approx(0.00675)
        assert result.carbon_intensity_used == 0.9

    def test_low_carbon_grid(self) -> None:
        """Renewables-heavy grid: 0.05 kg CO₂/kWh."""
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=60.0,
            runs_per_day=10,
            hardware_profile="laptop",
            carbon_intensity=0.05,
        )
        # co2_kg_per_day = (7.5 / 1000) × 0.05 = 0.000375 kg
        assert result.co2_kg_per_day == pytest.approx(0.000375)


# ------------------------------------------------------------------
# Edge cases: zero runtime, zero runs
# ------------------------------------------------------------------


class TestEdgeCases:
    """Zero values must produce zero emissions."""

    def test_zero_runtime(self) -> None:
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=0.0,
            runs_per_day=100,
            hardware_profile="laptop",
        )
        assert result.energy_wh_per_day == 0.0
        assert result.co2_kg_per_day == 0.0

    def test_zero_runs_per_day(self) -> None:
        estimator = CarbonEstimator()
        result = estimator.estimate(
            risk_assessment=_make_assessment(),
            runtime_seconds=60.0,
            runs_per_day=0,
            hardware_profile="laptop",
        )
        assert result.energy_wh_per_day == 0.0
        assert result.co2_kg_per_day == 0.0


# ------------------------------------------------------------------
# Invalid hardware profile
# ------------------------------------------------------------------


class TestInvalidProfile:
    """CarbonEstimator must propagate ValueError for bad profiles."""

    def test_invalid_profile_in_estimate(self) -> None:
        estimator = CarbonEstimator()
        with pytest.raises(ValueError, match="Unknown hardware profile"):
            estimator.estimate(
                risk_assessment=_make_assessment(),
                runtime_seconds=60.0,
                runs_per_day=10,
                hardware_profile="mainframe",
            )
