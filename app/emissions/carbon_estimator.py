"""Carbon emissions estimator for CodeEcoScan.

Computes scenario-based energy consumption and CO₂ emissions from
user-supplied runtime parameters and hardware profiles.

This module is **framework-agnostic** — it has zero dependency on
FastAPI, the scoring engine, or the AST analysis layer.  It can
be used independently from CLI tools, batch scripts, or API routes.

Assumptions
-----------
- Power draw is constant and equal to the hardware profile's
  ``power_watts`` for the entire ``runtime_seconds``.
- Carbon intensity is a flat grid-average factor (kg CO₂ per kWh).
  The default of 0.4 kg/kWh is a global average approximation
  (source: IEA 2023 World Energy Outlook).
- No PUE (Power Usage Effectiveness) overhead is modeled.
- No idle power or startup cost is included.

Thread-safety guarantee
-----------------------
``CarbonEstimator`` is stateless.  ``estimate()`` is a pure function
that reads inputs, computes, and returns a result.
"""

from __future__ import annotations

from app.emissions.hardware_profiles import get_profile, HardwareProfile
from app.emissions.models import EmissionsEstimate
from app.models.schemas import RiskAssessment


class CarbonEstimator:
    """Deterministic carbon emissions estimator.

    Computes energy consumption and CO₂ emissions for a given
    scenario defined by runtime duration, execution frequency,
    and hardware profile.

    The ``risk_assessment`` parameter is accepted for future
    extensibility (e.g. risk-weighted estimation) but is **not**
    used in the current formula — energy math is purely
    physics-based.
    """

    def estimate(
        self,
        risk_assessment: RiskAssessment,
        runtime_seconds: float,
        runs_per_day: int,
        hardware_profile: str,
        carbon_intensity: float = 0.4,
    ) -> EmissionsEstimate:
        """Compute emissions estimate for a scenario.

        Args:
            risk_assessment: Risk assessment from the scoring engine.
                Reserved for future risk-weighted extensions.
            runtime_seconds: Duration of a single code execution
                in seconds.  Must be >= 0.
            runs_per_day: Number of times the code runs per day.
                Must be >= 0.
            hardware_profile: Name of a built-in hardware profile
                (``"laptop"``, ``"small_cloud_vm"``, ``"gpu_server"``).
            carbon_intensity: Grid carbon intensity in kg CO₂ per
                kWh.  Defaults to 0.4 (global average).

        Returns:
            A fully populated ``EmissionsEstimate``.

        Raises:
            ValueError: If ``hardware_profile`` is not recognized,
                ``runtime_seconds < 0``, ``runs_per_day < 0``, or
                ``carbon_intensity <= 0``.
        """
        if runtime_seconds < 0:
            raise ValueError(
                f"runtime_seconds must be >= 0, got {runtime_seconds}"
            )
        if runs_per_day < 0:
            raise ValueError(
                f"runs_per_day must be >= 0, got {runs_per_day}"
            )
        if carbon_intensity <= 0:
            raise ValueError(
                f"carbon_intensity must be > 0, got {carbon_intensity}"
            )

        profile: HardwareProfile = get_profile(hardware_profile)

        # Energy per run: (watts × seconds) / 3600 = watt-hours
        energy_wh_per_run: float = (
            profile.power_watts * runtime_seconds
        ) / 3600.0

        # Energy per day
        energy_wh_per_day: float = energy_wh_per_run * runs_per_day

        # CO₂ per day: (Wh / 1000) × carbon_intensity = kg CO₂
        co2_kg_per_day: float = (energy_wh_per_day / 1000.0) * carbon_intensity

        return EmissionsEstimate(
            runtime_seconds=runtime_seconds,
            runs_per_day=runs_per_day,
            hardware_profile=profile.name,
            energy_wh_per_day=round(energy_wh_per_day, 6),
            co2_kg_per_day=round(co2_kg_per_day, 6),
            carbon_intensity_used=carbon_intensity,
        )
