"""The contract every block keeps.

A block module exports five things:

    TYPE            str, the name used in a layout file
    INLETS/OUTLETS  port names; a port listed in MULTI_* carries a list
    pressure_rules  (params) -> (relations, anchors)   -- runs before enthalpies
    flow_rule       (params) -> FlowRule               -- runs before enthalpies
    evaluate        (inlets, P_out, params, props) -> (outlets, extras)

and may optionally export:

    fixed_outlets   (params) -> {port: {"T": ...}}   -- outlet states that do
                    not depend on the inlets.  A heater whose outlet
                    temperature is given is the case that matters: it lets the
                    solver start the expansion branch before the recuperator
                    network is closed, which removes a tear.

Pressure and flow are declared *separately* from evaluate because both are
resolved across the whole flowsheet before any enthalpy is known.  A
compressor knows its outlet pressure is r times its inlet without knowing
anything thermodynamic; a splitter knows how it divides flow.  Declaring
those as relations is what lets one generic pass handle every layout.

Relations are invertible on purpose.  The turbine outlet pressure in a
recuperated cycle is not reachable by walking forwards from the compressor
inlet -- only by walking backwards from it, through the hot-side losses.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# --- pressure ---------------------------------------------------------------
@dataclass(frozen=True)
class Relation:
    """Pressure link between two ports, usable in either direction."""
    src: str
    dst: str
    forward: Callable[[float], float]
    backward: Callable[[float], float]


def identity_relation(src: str, dst: str) -> Relation:
    return Relation(src, dst, lambda P: P, lambda P: P)


def ratio_relation(src: str, dst: str, ratio: float) -> Relation:
    return Relation(src, dst, lambda P: P * ratio, lambda P: P / ratio)


def drop_relation(src: str, dst: str, delta: float) -> Relation:
    from ..physics.pressure_drop import drop, undrop
    return Relation(src, dst, lambda P: drop(P, delta), lambda P: undrop(P, delta))


# --- flow -------------------------------------------------------------------
@dataclass(frozen=True)
class Identity:
    """Flow passes straight through, port to port."""
    pairs: tuple        # ((in_port, out_port), ...)


@dataclass(frozen=True)
class Scale:
    """One inlet divided among outlets by fixed fractions."""
    inlet: str
    outlets: tuple      # ((out_port, index, fraction), ...)


@dataclass(frozen=True)
class Sum:
    """Several inlets merged into one outlet."""
    inlet: str
    outlet: str


FlowRule = Identity | Scale | Sum


# --- helpers shared by block implementations --------------------------------
def require(params: dict, key: str, block_id: str = "?"):
    if key not in params:
        raise KeyError(f"block {block_id!r} is missing required parameter {key!r}")
    return params[key]
