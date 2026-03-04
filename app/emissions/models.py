"""Data models for emissions estimation.

Framework-agnostic Pydantic models used by ``CarbonEstimator``
to represent estimation results.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmissionsEstimate(BaseModel):
    """Result of a carbon emissions estimation.

    All values are deterministic and computed from the provided
    scenario parameters — no runtime inference is performed.

    Attributes:
        runtime_seconds: Duration of a single code execution run.
        runs_per_day: Number of times the code is executed per day.
        hardware_profile: Name of the hardware profile used.
        energy_wh_per_day: Total energy consumed per day in watt-hours.
        co2_kg_per_day: Estimated CO₂ emissions per day in kilograms.
        carbon_intensity_used: Grid carbon intensity factor used
            (kg CO₂ per kWh).
    """

    runtime_seconds: float = Field(
        ..., ge=0, description="Duration of one run in seconds."
    )
    runs_per_day: int = Field(
        ..., ge=0, description="Number of executions per day."
    )
    hardware_profile: str = Field(
        ..., description="Name of the hardware profile used."
    )
    energy_wh_per_day: float = Field(
        ..., ge=0, description="Energy consumed per day (Wh)."
    )
    co2_kg_per_day: float = Field(
        ..., ge=0, description="CO₂ emissions per day (kg)."
    )
    carbon_intensity_used: float = Field(
        ..., gt=0, description="Carbon intensity factor (kg CO₂ / kWh)."
    )
