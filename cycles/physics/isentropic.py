"""Isentropic reference state and the efficiency step.

Shared by the compressor and the turbine -- the only difference between them
is which way the efficiency is applied.  This is the real-fluid replacement
for the air-table pr column: instead of pr2 = pr1 * (P2/P1), we ask the
backend directly for the enthalpy at the outlet pressure and the inlet
entropy.
"""
from __future__ import annotations


def isentropic_outlet_h(backend, P_out: float, s_in: float) -> float:
    """h_s: enthalpy at the outlet pressure on the inlet isentrope."""
    return backend.h_ps(P_out, s_in)


def compress(h_in: float, h_s: float, eta: float) -> float:
    """Real compression: the gap to the isentropic state is widened by 1/eta."""
    return h_in + (h_s - h_in) / eta


def expand(h_in: float, h_s: float, eta: float) -> float:
    """Real expansion: only eta of the isentropic drop is recovered."""
    return h_in - eta * (h_in - h_s)
