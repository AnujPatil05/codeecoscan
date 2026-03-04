"""Hardware power-draw profiles for emissions estimation.

Provides built-in profiles for common execution environments and
a lookup function for retrieving them by name.

This module has zero dependencies on FastAPI, scoring, or analysis
layers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HardwareProfile:
    """Immutable descriptor for a hardware execution environment.

    Attributes:
        name: Human-readable profile name (e.g. ``"laptop"``).
        power_watts: Average power draw of the hardware in watts
            during code execution.
    """

    name: str
    power_watts: float


# ------------------------------------------------------------------
# Built-in profiles
# ------------------------------------------------------------------

LAPTOP = HardwareProfile(name="laptop", power_watts=45.0)
"""Typical developer laptop (45 W average during code execution)."""

SMALL_CLOUD_VM = HardwareProfile(name="small_cloud_vm", power_watts=120.0)
"""Small cloud VM (e.g. 2–4 vCPU, no GPU) — 120 W average."""

GPU_SERVER = HardwareProfile(name="gpu_server", power_watts=300.0)
"""GPU-equipped server (e.g. single NVIDIA A100) — 300 W average."""

_BUILTIN_PROFILES: dict[str, HardwareProfile] = {
    profile.name: profile
    for profile in (LAPTOP, SMALL_CLOUD_VM, GPU_SERVER)
}


def get_profile(name: str) -> HardwareProfile:
    """Look up a built-in hardware profile by name.

    Args:
        name: Profile name (case-sensitive).  Must be one of
            ``"laptop"``, ``"small_cloud_vm"``, or ``"gpu_server"``.

    Returns:
        The matching ``HardwareProfile``.

    Raises:
        ValueError: If no profile matches the given name.
    """
    profile = _BUILTIN_PROFILES.get(name)
    if profile is None:
        valid = ", ".join(sorted(_BUILTIN_PROFILES.keys()))
        raise ValueError(
            f"Unknown hardware profile: {name!r}. "
            f"Valid profiles: {valid}"
        )
    return profile
