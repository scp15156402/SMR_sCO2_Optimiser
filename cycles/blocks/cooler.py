"""Heat rejection to a sink.

Two levels of detail, chosen by what the case supplies.

  T_out only          The working fluid leaves at a set temperature and the
                      sink is assumed perfect.  One property call.

  plus a coolant      A cooling-water (or air) side is sized against that
                      duty: the block reports the coolant flow it demands,
                      the temperature profile against it, the pinch, the UA,
                      and the pump work the circuit costs.

The second mode is what lets a sink be *sized against a supply* rather than
wished into existence, and it matters more here than intuition suggests.
Near the critical point most of the heat is rejected within a few degrees of
the compressor inlet temperature, so the approach against the coolant is
small and the flow demanded is large.  Cooling duty is a siting constraint
for a small modular reactor, so it is an output worth having.

This block stays thin on purpose.  The sizing itself lives in
`physics/coolant.py` because every cooler wants it, not just the precooler:
recompression has one, partial cooling has two, the intercooled layout has a
precooler and an intercooler.  Blocks are meant to be interchangeable, so a
capability that several of them share belongs below them rather than inside
one of them.
"""
from __future__ import annotations

from ..physics import coolant
from ..stream import Stream
from .base import Identity, drop_relation, require

TYPE = "cooler"
INLETS = ("in",)
OUTLETS = ("out",)


def pressure_rules(params):
    return [drop_relation("in", "out", params.get("dp", 0.0))], {}


def flow_rule(params):
    return Identity((("in", "out"),))


def fixed_outlets(params):
    """The outlet state is pinned by `T_out`, independent of what comes in.

    Declaring this lets the ordering pass treat the cooler outlet as known
    before the cycle is solved, which can remove a tear loop.
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
    q = st.h - h_out

    flags = []
    if q < 0.0:
        flags.append(f"{block_id}: outlet warmer than inlet, cooler is heating")

    extras = {
        "kind": "cooler",
        "q": q,
        "q_total": q * st.flow,
        "T_out": T_out,
        "T_in": p.T_ph(st.P, st.h),
        "flags": flags,
    }

    # The coolant side never changes the cycle -- the duty was already fixed
    # by T_out -- so it is skipped while the tear loop is still converging
    # and computed once on the final pass.
    spec = params.get("coolant")
    if diagnostics and spec is not None and q * st.flow > 0.0:
        side = coolant.size(
            st, out, q * st.flow, spec, props,
            fluid=require(params, "coolant_fluid", block_id),
            T_in=require(params, "coolant_T_in", block_id),
            P=params.get("coolant_P", 6e5),
            circuit=params.get("circuit"),
            pump_eta=params.get("pump_eta", 0.80),
            nodes=params.get("nodes", 100),
            block_id=block_id)
        flags.extend(side.flags)
        extras.update({
            "coolant_fluid": side.fluid,
            "coolant_flow": side.flow,
            "coolant_T_in": side.T_in,
            "coolant_T_out": side.T_out,
            "coolant_P": side.P,
            "coolant_dP": side.dP,
            "coolant_pinch": side.pinch,
            "coolant_pinch_at": side.pinch_at,
            "coolant_UA_per_flow": side.UA_per_flow,
            "coolant_profile": side.profile,
            "pump_w_total": side.pump_w,
        })

    return {"out": out}, extras
