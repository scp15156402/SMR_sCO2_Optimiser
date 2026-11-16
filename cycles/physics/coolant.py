"""Sizing a cycle stream against an external coolant supply.

A cooler that rejects heat to cooling water is a counterflow heat exchanger
whose cold stream leaves the cycle instead of coming back round.  Nothing
else about it is special, so this module reuses the recuperator's own
profile and sizing functions rather than reimplementing them: the only new
work is deciding how much coolant flows.

The coolant is specified by its pinch against the cycle stream; the coolant
flow that achieves that pinch is found by bracketing, and everything
downstream works from that flow.

Why this lives in physics/ and not in the cooler block
------------------------------------------------------
Because every cooler wants it.  A recompression cycle has one, partial
cooling has two, and the intercooled layout has a precooler and an
intercooler.  Leaving it inside one block would mean either duplicating it
or special-casing the precooler, and the whole architecture is built on
blocks being interchangeable.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..numerics.roots import solve_monotone
from ..specs import COOLANT_SPECS
from ..stream import Stream
from . import hx_profile, hx_sizing, hydraulics


@dataclass(frozen=True)
class CoolantSide:
    """Everything the coolant side of one cooler turned out to need."""
    fluid: str
    flow: float              # kg/s of coolant per kg/s of total cycle flow
    T_in: float
    T_out: float
    P: float
    pinch: float
    pinch_at: float
    UA_per_flow: float
    dP: float                # Pa across the circuit, as stated
    pump_w: float            # W per kg/s of total cycle flow
    profile: object
    flags: tuple


def size(hot_in, hot_out, duty, spec, props, *, fluid, T_in, P,
         circuit=None, pump_eta=0.80, nodes=100, block_id="?") -> CoolantSide:
    """Size one cooler against its coolant supply.

    `duty` is already fixed by the cycle: the cooler was told what outlet
    temperature to deliver, so how much heat has to move is not in question.
    What this works out is the coolant flow that moves it, the approach that
    results, and the conductance that implies.
    """
    if not isinstance(spec, COOLANT_SPECS):
        raise TypeError(
            f"block {block_id!r}: coolant spec must be one of "
            f"{', '.join(c.__name__ for c in COOLANT_SPECS)}, "
            f"got {type(spec).__name__}")

    pc = props(fluid)
    h_in = pc.h_pt(P, T_in)

    def profile_for(flow):
        """A trial coolant flow fixes its outlet enthalpy by energy balance.

        The coolant-side pressure is held at P across the exchanger.  Unlike
        the cycle side, where a 1-2 % drop moves cp enough to shift the
        pinch, a liquid coolant's enthalpy and density barely move over a
        few hundred kPa, so a pressure profile would change nothing
        thermally.  The drop still costs pump work, which is accounted for
        separately below.
        """
        coolant_in = Stream(fluid, P, h_in, flow)
        return hx_profile.build(
            props, hot_in, coolant_in, hot_out.h, duty,
            P_hot_in=hot_in.P, P_hot_out=hot_out.P,
            P_cold_in=P, P_cold_out=P, nodes=nodes)

    def flow_for_outlet(T_out):
        h_out = pc.h_pt(P, T_out)
        if h_out <= h_in:
            raise ValueError(
                f"block {block_id!r}: coolant outlet {T_out:.2f} K is not "
                f"above its inlet {T_in:.2f} K")
        return duty / (h_out - h_in)

    # --- CoolantPinch: bracket the coolant flow that gives the pinch -----
    T_hot_in = props(hot_in.fluid).T_ph(hot_in.P, hot_in.h)
    flow = solve_monotone(
        lambda f: profile_for(f).pinch, spec.value,
        flow_for_outlet(T_hot_in - 0.01),            # least coolant
        flow_for_outlet(T_in + 0.5),                 # most coolant
        tol=1e-6)

    if flow <= 0.0:
        raise ValueError(f"block {block_id!r}: coolant flow must be positive")

    prof = profile_for(flow)
    T_out = pc.T_ph(P, h_in + duty / flow)

    flags = []
    if prof.pinch <= 0.0:
        flags.append(f"{block_id}: coolant temperature cross, "
                     f"pinch {prof.pinch:.2f} K")

    dP = hydraulics.pressure_drop(circuit, flow)
    if dP >= P:
        flags.append(f"{block_id}: stated coolant pressure drop "
                     f"{dP/1e3:.0f} kPa is at or above the "
                     f"{P/1e3:.0f} kPa operating pressure")
    rho = pc.rho_ph(P, h_in)

    return CoolantSide(
        fluid=fluid, flow=flow, T_in=T_in, T_out=T_out, P=P,
        pinch=prof.pinch, pinch_at=prof.pinch_at,
        UA_per_flow=hx_sizing.ua_from_profile(prof),
        dP=dP, pump_w=hydraulics.pump_work(flow, dP, rho, pump_eta),
        profile=prof, flags=tuple(flags))
