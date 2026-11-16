"""Validation: air-standard Brayton cycle, ideal gas.

This case is the genericity test for the whole solver.  Swap the property
backend to an ideal gas and the same blocks, the same passes and the same
layout must reproduce the closed-form result from a first-course formula
sheet:

    T2s = T1 * rp**((g-1)/g)        T4s = T3 / rp**((g-1)/g)
    eta_ideal = 1 - rp**(-(g-1)/g)

If that holds, nothing in the solver is secretly assuming CO2 or real-gas
behaviour, and any later disagreement with CoolProp is physics rather than a
bug.  `runs/validate_air.py` checks it numerically.
"""
from cycles import Case, MassFlow
from cycles.units import MPa, degC, kPa

from brayton_cycle import simple

RP = 10.0
P1 = kPa(100)

air_brayton_ideal = Case(
    name="air_brayton_ideal",
    notes="air-standard Brayton, ideal gas, rp=10, eta_c=eta_t=1",
    fluid="AirIdeal",
    backend="idealgas",
    layout=simple,
    size=MassFlow(1.0),

    boundary={"s1": {"T": degC(15), "P": P1}},

    params={
        "COMP":   dict(eta=1.0, P_out=P1 * RP),
        "HEATER": dict(T_out=degC(1000)),
        "TURB":   dict(eta=1.0),
        "COOLER": dict(T_out=degC(15)),
    },
)

# Same cycle with real machines, to check the efficiency definitions.
air_brayton_real = air_brayton_ideal.with_(
    name="air_brayton_real",
    notes="air-standard Brayton with eta_c=0.85, eta_t=0.90",
    params={"COMP": dict(eta=0.85), "TURB": dict(eta=0.90)},
)
