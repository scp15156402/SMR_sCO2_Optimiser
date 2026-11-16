"""Real-fluid backend (Helmholtz equations of state via CoolProp).

This is the default.  For CO2 near its critical point the (P,s) and (P,h)
inverses are iterative inside CoolProp and can be slow or fail if the state
sits exactly on the saturation line -- keep the compressor inlet a couple of
kelvin above T_crit and that never bites.
"""
from __future__ import annotations

from CoolProp.CoolProp import PropsSI


class CoolPropBackend:
    name = "coolprop"

    def __init__(self, fluid: str):
        self.fluid = fluid
        self._Tc = PropsSI("Tcrit", fluid)
        self._Pc = PropsSI("pcrit", fluid)

    def h_pt(self, P, T):  return PropsSI("H", "P", P, "T", T, self.fluid)
    def s_pt(self, P, T):  return PropsSI("S", "P", P, "T", T, self.fluid)
    def T_ph(self, P, h):  return PropsSI("T", "P", P, "H", h, self.fluid)
    def s_ph(self, P, h):  return PropsSI("S", "P", P, "H", h, self.fluid)
    def h_ps(self, P, s):  return PropsSI("H", "P", P, "S", s, self.fluid)
    def rho_ph(self, P, h): return PropsSI("D", "P", P, "H", h, self.fluid)
    def cp_ph(self, P, h): return PropsSI("C", "P", P, "H", h, self.fluid)

    @property
    def T_crit(self): return self._Tc

    @property
    def P_crit(self): return self._Pc

    # --- saturation -------------------------------------------------------
    def has_saturation(self, P):
        """Is there a two-phase dome at this pressure?"""
        return P < self._Pc

    def T_sat(self, P):
        return PropsSI("T", "P", P, "Q", 0.0, self.fluid)

    def h_sat(self, P, q):
        """Saturated enthalpy: q=0 is liquid, q=1 is vapour."""
        return PropsSI("H", "P", P, "Q", q, self.fluid)
