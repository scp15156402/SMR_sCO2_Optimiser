"""Split one stream into two at the same state.

The fraction `x` goes to the *second* outlet, matching the convention in the
sCO2 literature where x (or phi, or the split ratio) is the fraction sent to
the recompressor.  Nothing thermodynamic happens here: both outlets carry the
inlet's pressure and enthalpy, only the flow fractions differ.
"""
from __future__ import annotations

from ..stream import Stream
from .base import Scale, identity_relation, require

TYPE = "splitter"
INLETS = ("in",)
OUTLETS = ("out",)
MULTI_OUT = ("out",)


def pressure_rules(params):
    return [identity_relation("in", "out")], {}


def flow_rule(params):
    x = require(params, "x", "splitter")
    return Scale("in", (("out", 0, 1.0 - x), ("out", 1, x)))


def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    st = inlets["in"]
    x = require(params, "x", block_id)

    flags = []
    if not 0.0 <= x <= 1.0:
        flags.append(f"{block_id}: split fraction {x} outside [0, 1]")

    a = Stream(st.fluid, st.P, st.h, st.flow * (1.0 - x))
    b = Stream(st.fluid, st.P, st.h, st.flow * x)
    return {"out": [a, b]}, {"kind": "splitter", "x": x, "flags": flags}
