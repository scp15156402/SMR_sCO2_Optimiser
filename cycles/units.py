"""Unit helpers.

Everything inside the solver is SI: Pa, K, J/kg, J/kg/K, kg/s, W.
These helpers exist so case files can be written in the units papers quote,
without a unit-parsing grammar.

    from cycles.units import MPa, degC, MW
    P = MPa(20)      # -> 20e6 Pa
    T = degC(500)    # -> 773.15 K
"""

# --- pressure ---------------------------------------------------------------
def Pa(x):  return float(x)
def kPa(x): return float(x) * 1e3
def MPa(x): return float(x) * 1e6
def bar(x): return float(x) * 1e5

# --- temperature ------------------------------------------------------------
def K(x):     return float(x)
def degC(x):  return float(x) + 273.15

# --- energy / power ---------------------------------------------------------
def J(x):   return float(x)
def kJ(x):  return float(x) * 1e3
def MJ(x):  return float(x) * 1e6
def W(x):   return float(x)
def kW(x):  return float(x) * 1e3
def MW(x):  return float(x) * 1e6

# --- conductance ------------------------------------------------------------
def W_per_K(x):  return float(x)
def kW_per_K(x): return float(x) * 1e3
def MW_per_K(x): return float(x) * 1e6

# --- back to readable units (for reporting only) ----------------------------
def to_degC(T):  return T - 273.15
def to_MPa(P):   return P / 1e6
def to_kPa(P):   return P / 1e3
def to_kJ(h):    return h / 1e3
def to_MW(P):    return P / 1e6
def to_kW_per_K(ua): return ua / 1e3
