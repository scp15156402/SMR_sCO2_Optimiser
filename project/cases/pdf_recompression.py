"""ME 306 project brief -- recompression layout.

Same operating conditions as the baseline; the layout changes and two
recuperators replace one.  The split fraction starts at 0.3, inside the
brief's allowed range of 0 to 0.5, and is the main thing to sweep.

The brief constrains the recuperator pinch to >= 5 K, so the pinch-specified
variant below is the fair basis for comparing layouts: equal pinch means
equally aggressive heat exchangers on both sides of the comparison.
"""
from cycles import Case, Effectiveness, Pinch, ThermalPower
from cycles.units import K, MPa, MW, degC

from brayton_cycle import recompression

pdf_recompression = Case(
    name="pdf_recompression",
    notes="ME 306 brief, recompression sCO2, 100 MWth, split 0.30",
    fluid="CO2",
    layout=recompression,
    size=ThermalPower(MW(100)),

    boundary={"s1": {"T": degC(32), "P": MPa(7.7)}},

    params={
        "MC":     dict(eta=0.89, P_out=MPa(20)),
        "RC":     dict(eta=0.89, P_out=MPa(20)),
        "LTR":    dict(spec=Effectiveness(0.90), nodes=100),
        "HTR":    dict(spec=Effectiveness(0.90), nodes=100),
        "HEATER": dict(T_out=degC(500)),
        "TURB":   dict(eta=0.90),
        "PC":     dict(T_out=degC(32)),
        "SPLIT":  dict(x=0.30),
    },
)

# Pinch-specified variant: the brief's 5 K constraint taken as the design target.
pdf_recompression_pinch = pdf_recompression.with_(
    name="pdf_recompression_pinch",
    notes="recompression sized to the brief's 5 K minimum pinch",
    params={
        "LTR": dict(spec=Pinch(K(5))),
        "HTR": dict(spec=Pinch(K(5))),
    },
)
