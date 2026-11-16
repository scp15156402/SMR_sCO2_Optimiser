"""Temperature profile through a counterflow exchanger, and the pinch.

Discretised in *duty*, not length: equal slices of Q.  Enthalpies at each node
are then exact from the energy balance, and temperatures follow from T(P,h).
A varying specific heat shows up automatically as a bend in the curve -- which
is the whole point, because that bend is what puts the pinch *inside* the
exchanger rather than at an end.

The same arrays feed the T-Q plot, so this function lives below both the
solver and the plotting layer.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    x: tuple          # 0 at the cold end, 1 at the hot end
    T_hot: tuple
    T_cold: tuple
    dT: tuple
    Q: float          # total duty, W per kg/s of total flow

    @property
    def pinch(self) -> float:
        return min(self.dT)

    @property
    def pinch_at(self) -> float:
        return self.x[min(range(len(self.dT)), key=lambda i: self.dT[i])]


def _lerp(a, b, t):
    return a + (b - a) * t


def build(props, hot_in, cold_in, hot_out_h, Q, P_hot_in, P_hot_out,
          P_cold_in, P_cold_out, nodes=100) -> Profile:
    """Walk the exchanger from the cold end in `nodes` equal-duty steps.

    x = 0 is where the cold stream enters and the hot stream leaves.
    Pressure is interpolated linearly along each side; with the 1-2% losses
    typical of a PCHE the difference against a mean-pressure assumption is
    negligible.
    """
    ph = props(hot_in.fluid)
    pc = props(cold_in.fluid)
    f_hot, f_cold = hot_in.flow, cold_in.flow

    xs, Th, Tc, dT = [], [], [], []
    for j in range(nodes + 1):
        x = j / nodes
        h_c = cold_in.h + x * Q / f_cold
        h_h = hot_out_h + x * Q / f_hot
        P_c = _lerp(P_cold_in, P_cold_out, x)
        P_h = _lerp(P_hot_out, P_hot_in, x)
        t_h = ph.T_ph(P_h, h_h)
        t_c = pc.T_ph(P_c, h_c)
        xs.append(x)
        Th.append(t_h)
        Tc.append(t_c)
        dT.append(t_h - t_c)

    return Profile(tuple(xs), tuple(Th), tuple(Tc), tuple(dT), Q)
