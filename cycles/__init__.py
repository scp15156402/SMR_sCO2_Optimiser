"""cycles -- a block-based solver for closed thermodynamic power cycles.

Nothing in this package knows what a Brayton cycle is, or that CO2 exists.
A cycle is a list of blocks and the streams between them; a run is a Case
giving the numbers.  sCO2, air-standard Brayton, Rankine and a
Joule-Thomson cryocooler are all layouts, not code.

    from cycles import solve
    from cycles.units import MPa, degC, MW

    result = solve(my_case)
    print(result.metrics["eta_th"])
"""
from __future__ import annotations

from .case import Case, Numerics
from .flowsheet import Flowsheet, Node
from .result import Result
from .solve import solve
from .physics.exergy import Environment
from .physics.hydraulics import FixedDrop, NoPumping, QuadraticDrop
from .specs import (CoolantPinch, Effectiveness, MassFlow, Pinch,
                    ThermalPower, UAperFlow)
from .stream import Stream

__version__ = "0.1.0"

__all__ = [
    "Case", "Numerics", "Flowsheet", "Node", "Result", "Stream", "solve",
    "Effectiveness", "Pinch", "UAperFlow",
    "CoolantPinch",
    "NoPumping", "FixedDrop", "QuadraticDrop",
    "Environment",
    "ThermalPower", "MassFlow",
]
