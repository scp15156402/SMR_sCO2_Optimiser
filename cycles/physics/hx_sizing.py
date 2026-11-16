"""Conductance UA from a temperature profile.

UA is the integral of dQ / dT across the exchanger.  A single log-mean
temperature difference is exact only when dT is linear in Q, which requires
constant specific heats -- false for CO2 near the pseudo-critical line.  So
the exchanger is treated as a chain of short exchangers, each short enough to
be linear, and their conductances are summed.

Returned per unit total mass flow (W/K per kg/s).  Multiply by the solved
mdot to compare with a paper quoting UA in kW/K.
"""
from __future__ import annotations

import math


def lmtd(dT1: float, dT2: float) -> float:
    """Log-mean of two end differences; falls back to the mean when equal."""
    if dT1 <= 0.0 or dT2 <= 0.0:
        return float("nan")
    if abs(dT1 - dT2) < 1e-9 * max(dT1, dT2):
        return 0.5 * (dT1 + dT2)
    return (dT1 - dT2) / math.log(dT1 / dT2)


def ua_from_profile(profile) -> float:
    """Sum the segment conductances. NaN if the profile has a temperature cross."""
    dT = profile.dT
    n = len(dT) - 1
    if n < 1 or min(dT) <= 0.0:
        return float("nan")
    dQ = profile.Q / n
    total = 0.0
    for j in range(1, n + 1):
        lm = lmtd(dT[j], dT[j - 1])
        if not math.isfinite(lm) or lm <= 0.0:
            return float("nan")
        total += dQ / lm
    return total
