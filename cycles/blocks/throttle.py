"""Isenthalpic expansion through a restriction.

Not used by any Brayton layout, and present on purpose: it is the one block
Rankine regeneration needs (the trap that drains a closed feedwater heater),
it is the Joule-Thomson orifice of a cryocooler, and it is the bypass valve
in a control study.  Three lines of physics that keep the library honest
about being a cycle solver rather than a Brayton solver.
"""
from __future__ import annotations

from ..stream import Stream
from .base import Identity, ratio_relation

TYPE = "throttle"
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
    out = Stream(st.fluid, P_out["out"], st.h, st.flow)   # h is conserved
    p = props(st.fluid)
    return {"out": out}, {
        "kind": "throttle",
        "dT": p.T_ph(out.P, out.h) - p.T_ph(st.P, st.h),   # Joule-Thomson effect
        "dP": st.P - out.P,
    }
