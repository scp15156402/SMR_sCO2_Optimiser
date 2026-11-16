"""Ideal-gas backend, for validation.

Constant cp, Pv = RT.  Exists so the solver can reproduce the textbook
air-standard Brayton cycle exactly -- if it does, the layout machinery and
the blocks are right, and any later disagreement with CoolProp is real-fluid
behaviour rather than a bug.

Reference state is arbitrary (h=0, s=0 at T_REF, P_REF); only differences
matter in a cycle.
"""
from __future__ import annotations

import math

T_REF = 298.15
P_REF = 101325.0

# name -> (R [J/kg/K], cp [J/kg/K])
GASES = {
    "AirIdeal":    (287.0,  1005.0),
    "CO2Ideal":    (188.92, 846.0),
    "HeliumIdeal": (2077.0, 5193.0),
    "N2Ideal":     (296.8,  1040.0),
}


class IdealGasBackend:
    name = "idealgas"

    def __init__(self, fluid: str, R: float = None, cp: float = None):
        self.fluid = fluid
        if R is None or cp is None:
            if fluid not in GASES:
                raise KeyError(
                    f"unknown ideal gas {fluid!r}; known: {sorted(GASES)} "
                    f"(or pass R and cp explicitly)"
                )
            R, cp = GASES[fluid]
        self.R = R
        self.cp = cp
        self.gamma = cp / (cp - R)

    # forward
    def h_pt(self, P, T):  return self.cp * (T - T_REF)
    def s_pt(self, P, T):  return self.cp * math.log(T / T_REF) - self.R * math.log(P / P_REF)

    # inverse
    def T_ph(self, P, h):  return T_REF + h / self.cp
    def s_ph(self, P, h):  return self.s_pt(P, self.T_ph(P, h))

    def h_ps(self, P, s):
        T = T_REF * math.exp((s + self.R * math.log(P / P_REF)) / self.cp)
        return self.h_pt(P, T)

    # auxiliary
    def rho_ph(self, P, h): return P / (self.R * self.T_ph(P, h))
    def cp_ph(self, P, h):  return self.cp

    @property
    def T_crit(self): return float("nan")

    @property
    def P_crit(self): return float("nan")

    # --- saturation -------------------------------------------------------
    def has_saturation(self, P):
        """An ideal gas never condenses, so (P, T) is always unambiguous."""
        return False

    def T_sat(self, P):
        raise NotImplementedError("an ideal gas has no saturation line")

    def h_sat(self, P, q):
        raise NotImplementedError("an ideal gas has no saturation line")
