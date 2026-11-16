"""Unit helpers.

Everything inside the solver is SI: Pa, K, J/kg, J/kg/K, kg/s, W.
These helpers exist so case files can be written in the units papers quote,
without a unit-parsing grammar.

    from cycles.units import MPa, degC, MW
    P = MPa(20)      # -> 20e6 Pa
    T = degC(500)    # -> 773.15 K
"""

# --- pressure ---------------------------------------------------------------
def kPa(x): return float(x) * 1e3
def MPa(x): return float(x) * 1e6

# --- temperature ------------------------------------------------------------
def K(x):     return float(x)
def degC(x):  return float(x) + 273.15

# --- power ------------------------------------------------------------------
def MW(x):  return float(x) * 1e6
