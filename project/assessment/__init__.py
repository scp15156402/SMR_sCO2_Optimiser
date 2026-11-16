"""Turning a solved cycle into the four things the brief asks you to defend.

The solver answers "what does this cycle do".  This package answers "what
would it weigh, what would it cost, and is it even allowed" -- and then
"which of these designs is worth considering at all".

Why it lives here and not in `cycles/`
---------------------------------------
Every number in this package is an assumption from one classroom brief:
2.5 kg per kW/K of UA, US$250/kg, US$70/MWh, a 60 t baseline.  None of it
is physics.  Putting it in the solver would make the solver specific to
this problem, which is exactly what the two-layer split exists to prevent.

So the rule is one-way: `assessment` reads a `Result` and never reaches
back.  Nothing here can change a cycle; it can only describe one.
"""
from .cost import CostModel, cost_of
from .mass import MassModel, mass_of
from .metrics import assess, second_law_efficiency
from .moo import CONSTRAINTS, Candidate, feasible, knee, pareto_front

__all__ = [
    "MassModel", "mass_of",
    "CostModel", "cost_of",
    "assess", "second_law_efficiency",
    "CONSTRAINTS", "Candidate", "feasible", "pareto_front", "knee",
]
