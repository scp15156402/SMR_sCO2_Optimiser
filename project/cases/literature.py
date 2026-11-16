"""Published cases, reproduced to check the solver against someone else's.

Every other validation in this project is internal.  The air case proves the
algebra is right; energy closure proves nothing leaks; node convergence
proves the discretisation is fine.  None of them can catch a transposed
property argument or a unit slip on the CO2 side, because all three would
pass with the properties wrong.

Only reproducing a published number can catch that, which is why these
cases exist and why no sCO2 result should be quoted before they run.

Kim et al., Energy 147 (2018) 1216-1226
---------------------------------------
Table 1 gives the conditions; the conclusions give the optimum.  Their
definitions were checked against ours before comparing, because a matching
number from mismatched definitions would be worse than no check:

  * Split ratio.  Their eq. (6) is (1-sr) h3 + sr h10 = h4, with h10 the
    recompressor outlet, so sr is the fraction sent to the recompressor --
    the same direction as our `x`.
  * Effectiveness.  Their eq. (4) is enthalpy-based,
    q / min(q_max_hot, q_max_cold), which is ours.
  * LTR effectiveness.  Their eq. (5) carries a (1-sr) on the cold-side
    limit.  So does ours, because the cold stream's flow fraction is
    already (1-x) and `duty_limits` multiplies by it.
  * Cycle work.  Their eq. (8) weights each compressor by its own flow,
    which is what summing `w_total` does.

No pressure drops are mentioned, so none are applied.
"""
from cycles import Case, Effectiveness, MassFlow, ThermalPower
from cycles.units import MPa, MW, degC

from brayton_cycle import recompression

# Kim Table 1
KIM_ETA_TURBINE = 0.90
KIM_ETA_COMPRESSOR = 0.85
KIM_EFFECTIVENESS = 0.95
KIM_T_COMP_IN = degC(32)
KIM_P_LOW = MPa(7.4)
KIM_T_TURB_IN = degC(550)

# Kim's reported optimum, conclusion 1
KIM_RP = 2.6
KIM_P_HIGH = MPa(19.24)
KIM_SPLIT = 0.307
KIM_ETA_REPORTED = 0.4467


def kim_case(x=KIM_SPLIT, P_high=KIM_P_HIGH, eps=KIM_EFFECTIVENESS,
             name="kim_2018"):
    return Case(
        name=name,
        notes="Kim et al. Energy 147 (2018), Table 1 conditions, "
              "reported optimum rp 2.6 / sr 0.307 / eta 44.67 %",
        fluid="CO2",
        layout=recompression,
        size=ThermalPower(MW(100)),          # efficiency is size-independent
        boundary={"s1": {"T": KIM_T_COMP_IN, "P": KIM_P_LOW}},
        params={
            "MC":     dict(eta=KIM_ETA_COMPRESSOR, P_out=P_high),
            "RC":     dict(eta=KIM_ETA_COMPRESSOR, P_out=P_high),
            "LTR":    dict(spec=Effectiveness(eps), nodes=100),
            "HTR":    dict(spec=Effectiveness(eps), nodes=100),
            "SPLIT":  dict(x=x),
            "HEATER": dict(T_out=KIM_T_TURB_IN),
            "TURB":   dict(eta=KIM_ETA_TURBINE),
            "PC":     dict(T_out=KIM_T_COMP_IN),
        },
    )


kim_2018 = kim_case()
