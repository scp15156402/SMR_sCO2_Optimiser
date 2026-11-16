"""Heat addition from the source.

Mirror of the cooler.  `T_out` is the turbine inlet temperature; in an
indirect plant that is the reactor core outlet less the approach across the
intermediate heat exchanger, so the case file -- not this block -- decides
where the number comes from.
"""
from __future__ import annotations

from ..stream import Stream
from .base import Identity, drop_relation, require

TYPE = "heater"
INLETS = ("in",)
OUTLETS = ("out",)


def pressure_rules(params):
    return [drop_relation("in", "out", params.get("dp", 0.0))], {}


def flow_rule(params):
    return Identity((("in", "out"),))


def fixed_outlets(params):
    """The outlet state is pinned by `T_out`, independent of what comes in.

    This is what makes the expansion branch of a recuperated cycle solvable
    without knowing the recuperator: the turbine inlet is the heater outlet,
    and that is fixed at the turbine inlet temperature.  Telling the ordering
    pass so removes a whole tear loop.
    """
    if "T_out" in params:
        return {"out": {"T": params["T_out"]}}
    return {}


def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    st = inlets["in"]
    T_out = require(params, "T_out", block_id)
    p = props(st.fluid)

    h_out = p.h_pt(P_out["out"], T_out)
    out = Stream(st.fluid, P_out["out"], h_out, st.flow)
    q = h_out - st.h

    flags = []
    if q < 0.0:
        flags.append(f"{block_id}: outlet colder than inlet, heater is cooling")

    extras = {
        "kind": "heater",
        "q": q,
        "q_total": q * st.flow,
        "T_out": T_out,
        "T_in": p.T_ph(st.P, st.h),
        "flags": flags,
    }

    # Optional: the temperature of the boundary the heat crosses on its way
    # in.  This block has no heat-source model, so nothing here can derive
    # it -- but a user who knows their reactor can state it, and the exergy
    # analysis then has what it needs.  Stated, never invented, which is the
    # same rule the coolant circuit models follow.
    if "T_source" in params:
        T_b = params["T_source"]
        if T_b <= T_out:
            flags.append(
                f"{block_id}: heat source at {T_b-273.15:.1f} degC is not "
                f"above the outlet it must heat to {T_out-273.15:.1f} degC")
        extras["T_source"] = T_b

    return {"out": out}, extras
