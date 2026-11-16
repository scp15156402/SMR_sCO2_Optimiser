"""ME 306 project brief -- partial cooling layout.

R4 has to decide whether intercooling or partial cooling is worth adding, so
this case exists to let that decision be computed rather than argued.

Three pressure levels, which is the structural difference from every other
layout here:

    turbine exhaust   s7   6.0 MPa    (free variable, set by PCOMP's ratio)
    main compressor   s1   7.7 MPa    (the brief's constraint, at the critical point)
    maximum           s2  20.0 MPa    (the brief's ceiling)

The turbine exhaust sits below the critical pressure.  That is safe here
because the whole low-pressure side stays above 31 degC, and above the
critical *temperature* there is no saturation line at any pressure -- so no
two-phase risk.  The brief's ">= 7.7 MPa" constraint is on the main
compressor inlet, which is honoured.
"""
from cycles import Case, Effectiveness, ThermalPower
from cycles.units import MPa, MW, degC

from brayton_cycle import partial_cooling

P_LOW = MPa(6.0)       # turbine exhaust
P_MID = MPa(7.7)       # main compressor inlet, at the critical point
P_HIGH = MPa(20.0)     # the brief's ceiling

pdf_partial_cooling = Case(
    name="pdf_partial_cooling",
    notes="ME 306 brief, partial cooling sCO2, 100 MWth, split 0.30",
    fluid="CO2",
    layout=partial_cooling,
    size=ThermalPower(MW(100)),

    boundary={"s1": {"T": degC(32), "P": P_MID}},
    pressures={"s7": P_LOW},          # anchors the third pressure level

    params={
        "MC":     dict(eta=0.89, P_out=P_HIGH),
        "RC":     dict(eta=0.89, P_out=P_HIGH),
        "PCOMP":  dict(eta=0.89, P_out=P_MID),
        "LTR":    dict(spec=Effectiveness(0.90), nodes=100),
        "HTR":    dict(spec=Effectiveness(0.90), nodes=100),
        "HEATER": dict(T_out=degC(500)),
        "TURB":   dict(eta=0.90),
        "PC1":    dict(T_out=degC(32)),
        "PC2":    dict(T_out=degC(32)),
        "SPLIT":  dict(x=0.30),
    },
)
