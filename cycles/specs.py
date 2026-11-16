"""Specifications: the small tagged values that say *what a run fixes*.

Heat-exchanger specs and plant-size specs are separate ideas, but they share
one property: each one decides which loop the solver has to run.  Keeping them
as tiny frozen classes (rather than magic strings) means a typo is an error at
import, not a wrong answer at run time.
"""
from __future__ import annotations

from dataclasses import dataclass


# --- heat exchanger ---------------------------------------------------------
@dataclass(frozen=True)
class Effectiveness:
    """Q = value * min(Q_hot_limit, Q_cold_limit).  Explicit, no loop."""
    value: float


@dataclass(frozen=True)
class Pinch:
    """Minimum temperature difference anywhere in the exchanger, in K.

    Solved by bisection on effectiveness: pinch falls monotonically as
    effectiveness rises.
    """
    value: float


@dataclass(frozen=True)
class UAperFlow:
    """Conductance per unit total cycle mass flow, in W/K per (kg/s).

    Absolute UA in W/K needs mdot, which needs q_in, which needs this -- an
    extra outer loop.  Per-flow UA keeps the solve explicit.  Multiply by the
    reported mdot to compare against a paper that quotes UA in kW/K.
    """
    value: float


# --- coolant side -----------------------------------------------------------
# A cooler rejecting heat to an external supply is a counterflow exchanger
# with one stream leaving the cycle, so it wants the same treatment as the
# recuperator: say which quantity you are pinning and let the rest follow.
# The pinch reduces to a coolant mass flow, the way the three above reduce to
# an effectiveness.
@dataclass(frozen=True)
class CoolantPinch:
    """Minimum approach between the cycle stream and the coolant, in K.

    Solved by bracketing on coolant flow: less coolant means a hotter,
    steeper coolant curve, so the pinch falls monotonically as flow falls.
    """
    value: float


COOLANT_SPECS = (CoolantPinch,)


# --- plant size -------------------------------------------------------------
@dataclass(frozen=True)
class ThermalPower:
    """Total heat into the cycle, in W.  mdot = Q_th / q_in."""
    value: float


@dataclass(frozen=True)
class MassFlow:
    """Total cycle mass flow, in kg/s, given directly."""
    value: float


SIZE_SPECS = (ThermalPower, MassFlow)
