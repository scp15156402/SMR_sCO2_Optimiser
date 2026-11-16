"""Intercooling the compression, which the brief lists as an option.

Splitting compression into two stages and cooling between them is the
classic way to cut compressor work: the second stage then handles denser
fluid, so the integral v dP over the upper pressure span is smaller.

It works here, in the sense that the back-work ratio really does fall.  It
also loses, and the reason is worth understanding because it is the same
fact that makes this cycle attractive in the first place.

A gas turbine spends about half its turbine output on compression, so
shaving that is worth a great deal.  sCO2 compressing near the critical
point spends about 18 %, because the fluid is nearly incompressible there.
There is simply much less to save -- and the saving is paid for by throwing
away heat in the intercooler at a temperature the recuperator could have
recovered from, which the reactor must then put back.

The intermediate pressure is the free variable.  The geometric mean of the
two pressure levels, 12.41 MPa here, is the classic ideal-gas optimum and is
included for reference; for a real fluid it is not the optimum and the sweep
below shows the best point sitting lower.
"""
import math

from cycles import Case, Effectiveness, Pinch, ThermalPower
from cycles.units import K, MPa, MW, degC

from brayton_cycle import intercooled

P_LOW, P_HIGH = MPa(7.7), MPa(20.0)
P_GEOMETRIC = math.sqrt(P_LOW * P_HIGH)          # 12.41 MPa


def intercooled_case(P_mid, spec=None, T_ic=degC(32), name=None):
    """Brief conditions, two-stage compression with an intercooler."""
    return Case(
        name=name or f"intercooled_{P_mid/1e6:.1f}MPa",
        notes=f"two-stage compression, intercooled to "
              f"{T_ic-273.15:.0f} degC at {P_mid/1e6:.2f} MPa",
        fluid="CO2",
        layout=intercooled,
        size=ThermalPower(MW(100)),
        boundary={"s1": {"T": degC(32), "P": P_LOW}},
        params={
            "LPC":    dict(eta=0.89, P_out=P_mid),
            "IC":     dict(T_out=T_ic),
            "HPC":    dict(eta=0.89, P_out=P_HIGH),
            "RECUP":  dict(spec=spec or Effectiveness(0.90), nodes=100),
            "HEATER": dict(T_out=degC(500)),
            "TURB":   dict(eta=0.90),
            "PC":     dict(T_out=degC(32)),
        },
    )


# the one that goes in the layout comparison: same 5 K pinch as the others
pdf_intercooled = intercooled_case(
    MPa(10.0), spec=Pinch(K(5)), name="pdf_intercooled")

pdf_intercooled_geometric = intercooled_case(
    P_GEOMETRIC, spec=Pinch(K(5)), name="pdf_intercooled_geometric")
