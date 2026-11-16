"""Fractional pressure loss, and its inverse.

Used by every heat exchanger, cooler and heater.  Both directions are needed
because the pressure pass propagates from anchors outward: the turbine outlet
pressure is only reachable by walking *backwards* from the compressor inlet
through the hot-side losses.
"""
from __future__ import annotations


def drop(P_in: float, delta: float) -> float:
    """Downstream pressure after losing a fraction `delta`."""
    return P_in * (1.0 - delta)


def undrop(P_out: float, delta: float) -> float:
    """Upstream pressure that would produce `P_out` after the same loss."""
    return P_out / (1.0 - delta)
