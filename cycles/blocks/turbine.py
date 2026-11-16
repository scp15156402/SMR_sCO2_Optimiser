"""Turbine.

Mirror of the compressor: only eta of the isentropic drop is recovered.
Usually carries no pressure rule of its own -- its outlet pressure is found
by walking backwards from the compressor inlet through the hot-side losses.
"""
from __future__ import annotations

from ..physics.isentropic import expand, isentropic_outlet_h
from ..stream import Stream
from .base import Identity, ratio_relation, require

TYPE = "turbine"
INLETS = ("in",)
OUTLETS = ("out",)


def pressure_rules(params):
    if "P_out" in params:
        return [], {"out": params["P_out"]}
    if "ratio" in params:
        return [ratio_relation("in", "out", 1.0 / params["ratio"])], {}
    return [], {}


def flow_rule(params):
    return Identity((("in", "out"),))


def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    st = inlets["in"]
    eta = require(params, "eta", block_id)
    p = props(st.fluid)

    s_in = p.s_ph(st.P, st.h)
    h_s = isentropic_outlet_h(p, P_out["out"], s_in)
    h = expand(st.h, h_s, eta)

    out = Stream(st.fluid, P_out["out"], h, st.flow)
    w = st.h - h
    return {"out": out}, {
        "kind": "turbine",
        "w": w,
        "w_isentropic": st.h - h_s,
        "w_total": w * st.flow,
        "w_lost": (st.h - h_s) - w,
        "ratio": st.P / P_out["out"],
    }
