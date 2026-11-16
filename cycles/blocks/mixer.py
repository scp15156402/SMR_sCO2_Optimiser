"""Merge streams at the same pressure.

Flow-weighted enthalpy.  The temperature mismatch between the merging streams
is reported because mixing at different temperatures generates entropy for
nothing -- in a recompression cycle the optimum split is close to where that
mismatch vanishes, so it doubles as a diagnostic for how well tuned the split
is.
"""
from __future__ import annotations

from ..physics.mixing import mix, pressure_mismatch
from ..stream import Stream
from .base import Sum

TYPE = "mixer"
INLETS = ("in",)
OUTLETS = ("out",)
MULTI_IN = ("in",)


def pressure_rules(params):
    from .base import identity_relation
    return [identity_relation("in", "out")], {}


def flow_rule(params):
    return Sum("in", "out")


def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    streams = inlets["in"]
    if len(streams) < 2:
        raise ValueError(f"block {block_id!r}: mixer needs at least two inlets")

    fluids = {s.fluid for s in streams}
    if len(fluids) > 1:
        raise ValueError(f"block {block_id!r}: cannot mix fluids {sorted(fluids)}")

    h, flow = mix(streams)
    out = Stream(streams[0].fluid, P_out["out"], h, flow)

    p = props(out.fluid)
    temps = [p.T_ph(s.P, s.h) for s in streams]

    flags = []
    mismatch = pressure_mismatch(streams)
    if mismatch > 1e-6:
        flags.append(
            f"{block_id}: inlets differ in pressure by {mismatch*100:.2f}% "
            f"- check the flowsheet wiring"
        )

    return {"out": out}, {
        "kind": "mixer",
        "T_in": tuple(temps),
        "T_mismatch": max(temps) - min(temps),
        "flags": flags,
    }
