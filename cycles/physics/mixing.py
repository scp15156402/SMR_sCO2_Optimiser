"""Adiabatic merge of two or more streams at the same pressure."""
from __future__ import annotations


def mix(streams):
    """Flow-weighted enthalpy; flows add.  Returns (h, flow)."""
    total = sum(s.flow for s in streams)
    if total <= 0.0:
        raise ValueError("mixer received no flow")
    h = sum(s.flow * s.h for s in streams) / total
    return h, total


def pressure_mismatch(streams) -> float:
    """Largest relative pressure difference between the inlets.

    Nonzero means the flowsheet is wired wrong, so the solver reports it
    rather than silently averaging states at different pressures.
    """
    ps = [s.P for s in streams]
    return (max(ps) - min(ps)) / max(ps)
