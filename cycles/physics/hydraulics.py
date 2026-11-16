"""Coolant-side pressure drop, and the pump work it implies.

The governing rule for this module: **the solver applies a pressure drop you
state; it never manufactures one.**

That line exists because of what was tried and rejected here.  A
Darcy-Weisbach model was written, taking channel diameter, length and count,
and it had to be removed.  Not because the arithmetic was wrong, but because
this project computes UA and never computes geometry (see the sizing
chapter): the geometry fed to such a model has no connection to the UA
reported beside it, and nothing can check the two against each other.  A
number that looks derived but is invented is worse than an assumption
clearly labelled as one, because only the first gets quoted without its
caveat.

So what is left is honest: you say what the drop is, and the solver tells you
what it costs.

Pressure drops here are **absolute, in pascals**, unlike the fractional drops
used on the cycle side.  That is deliberate.  A fractional drop is right for
the working fluid, whose pressure the cycle sets.  Hydraulic loss in a
cooling circuit is set by dynamic pressure and geometry and has nothing to do
with how far above atmosphere the circuit sits: the same exchanger at the
same flow loses the same 100 kPa at 2 bar as at 6 bar.  Making it fractional
would understate it roughly fiftyfold and, worse, would hand an optimiser a
lever that does not exist, since lowering the circuit pressure would then
appear to reduce pumping power.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoPumping:
    """No circuit modelled.  The default, and an honest one.

    Reports zero pump work rather than a guess.  Use it when you have no
    figure for the pressure drop and do not want to invent one -- the
    cooling duty and conductance are still reported in full.
    """


@dataclass(frozen=True)
class FixedDrop:
    """A stated loss in Pa, the same whatever the flow.

    Fine for a first sensitivity study.  Pump work comes out linear in flow,
    which understates how quickly more coolant gets expensive.
    """
    dP: float


@dataclass(frozen=True)
class QuadraticDrop:
    """dP = dP_ref * (mdot / flow_ref)^2, anchored at a point you know.

    Still an assumption, but a better-shaped one: hydraulic loss goes as the
    square of velocity, so pump work goes as the *cube* of flow.  That
    exponent is what decides whether a coolant-flow sweep has an interior
    optimum, so it matters more than the magnitude.

    `flow_ref` is in the same units as the reported coolant flow: kg/s of
    coolant per kg/s of total cycle flow.
    """
    dP_ref: float
    flow_ref: float


CIRCUIT_MODELS = (NoPumping, FixedDrop, QuadraticDrop)


def pressure_drop(model, flow: float) -> float:
    """Pressure drop in Pa for a coolant flow, in normalised units."""
    if model is None or isinstance(model, NoPumping):
        return 0.0
    if isinstance(model, FixedDrop):
        return model.dP
    if isinstance(model, QuadraticDrop):
        if model.flow_ref <= 0.0:
            raise ValueError("QuadraticDrop.flow_ref must be positive")
        return model.dP_ref * (flow / model.flow_ref) ** 2
    raise TypeError(
        f"circuit must be one of "
        f"{', '.join(m.__name__ for m in CIRCUIT_MODELS)}, "
        f"got {type(model).__name__}")


def pump_work(flow: float, dP: float, rho: float, eta: float) -> float:
    """w = v dP / eta for an incompressible coolant, times its flow.

    Everything is per unit total cycle flow, so this sums with the block
    work terms without anyone needing the plant size.
    """
    if dP <= 0.0 or flow <= 0.0:
        return 0.0
    return flow * dP / (rho * eta)
