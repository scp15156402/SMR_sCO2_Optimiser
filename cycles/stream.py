"""The one object every block speaks.

A Stream is pure data: pressure, specific enthalpy, and what fraction of the
total cycle mass flow it carries.  Temperature, entropy, density and cp are
*derived* from (P, h) by a property backend -- never stored.

(P, h) is chosen deliberately over (P, T): inside a saturation dome P and T
are not independent, so (P, T) cannot identify a state.  (P, h) always can.
That single choice is what lets this solver run Rankine cycles later without
touching any block.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Stream:
    fluid: str
    P: float            # Pa
    h: float            # J/kg
    flow: float = 1.0   # fraction of total cycle mass flow

    def with_(self, **kw) -> "Stream":
        return replace(self, **kw)

    def describe(self, props) -> dict:
        """Full state, for reporting.  Needs a property backend."""
        p = props(self.fluid)
        return {
            "fluid": self.fluid,
            "P": self.P,
            "h": self.h,
            "T": p.T_ph(self.P, self.h),
            "s": p.s_ph(self.P, self.h),
            "rho": p.rho_ph(self.P, self.h),
            "flow": self.flow,
        }
