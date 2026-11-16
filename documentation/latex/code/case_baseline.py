from cycles import Case, Effectiveness, ThermalPower
from cycles.units import MPa, MW, degC

from brayton_cycle import recuperated

pdf_baseline = Case(
    name="pdf_baseline",
    notes="ME 306 brief baseline: simple recuperated sCO2, 100 MWth",
    fluid="CO2",
    layout=recuperated,
    size=ThermalPower(MW(100)),

    # the compressor inlet anchors both the low pressure and the loop enthalpy
    boundary={"s1": {"T": degC(32), "P": MPa(7.7)}},

    params={
        "COMP":   dict(eta=0.89, P_out=MPa(20)),
        "RECUP":  dict(spec=Effectiveness(0.90), nodes=100),
        "HEATER": dict(T_out=degC(500)),
        "TURB":   dict(eta=0.90),
        "COOLER": dict(T_out=degC(32)),
    },
)

# Second pass: the brief's 1-2% per heat exchanger.
pdf_baseline_dp = pdf_baseline.with_(
    name="pdf_baseline_dp",
    notes="baseline with 1% pressure drop per heat exchanger side",
    params={
        "RECUP":  dict(dp_hot=0.01, dp_cold=0.01),
        "HEATER": dict(dp=0.01),
        "COOLER": dict(dp=0.01),
    },
)
