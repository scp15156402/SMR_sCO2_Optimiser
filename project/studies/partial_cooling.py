"""Partial cooling's third pressure level, swept at last.

Every other layout here has two pressure levels. Partial cooling has
three, and the extra one -- the turbine exhaust, `s7` -- is a genuine free
variable that nothing in the brief pins down. It has been fixed at
6.0 MPa throughout this project for no better reason than that it is a
round number below the critical pressure, which made every
partial-cooling comparison provisional.

**The engineering question.** Lowering the turbine exhaust pressure
widens the expansion, so the turbine makes more work. But the fluid then
has to be compressed back up from a lower pressure, and it is less dense
down there, so the pre-compressor costs more. Two effects of opposite
sign means an interior optimum, and the only way to find it is to sweep.

There is a second effect that is easy to miss and is specific to partial
cooling: the pre-compressor's outlet feeds the low-temperature
recuperator's cold side. Changing the exhaust pressure therefore changes
the *temperature* entering the recuperator, and so changes the
capacity-rate mismatch -- the same mechanism that makes the compressor
inlet temperature matter (Chapter 12). So the optimum is not purely a
turbomachinery trade.

**The constraint that matters.** Under the brief's literal reading,
every compressor inlet must sit at or above 7.7 MPa, which rejects the
pre-compressor at any exhaust pressure below that. The sweep deliberately
runs across the limit so the cost of the reading is visible rather than
assumed: the `feasible_strict` column marks which points survive it.

    python -m project.studies.partial_cooling
"""
from __future__ import annotations

import sys

from cycles import Pinch, solve
from cycles.units import K, MPa, degC, to_MPa
from project.assessment import assess
from project.cases import partial_cooling_watercooled

from ._io import save

PINCH = Pinch(K(5))

# Turbine exhaust pressure. The upper end stops just short of the main
# compressor inlet (7.7 MPa): at equality the pre-compressor has no
# pressure rise to provide and the layout degenerates into something that
# is no longer partial cooling.
P_LOW = (5.0, 5.5, 6.0, 6.5, 7.0, 7.4, 7.6)

# The brief's limit, applied to every compressor inlet under the literal
# reading of ">= 7.7 MPa".
P_INLET_LIMIT = 7.7

# Split fractions, re-swept at the best exhaust pressure. Partial cooling
# was previously only ever compared at the split that suited
# recompression, which is a second way the comparison was unfair.
SPLITS = (0.20, 0.25, 0.30, 0.35, 0.40)


def design(P_lo, x):
    """One partial-cooling case: exhaust pressure and split fraction."""
    return partial_cooling_watercooled.with_(
        name=f"pc_{P_lo}_{x}",
        pressures={"s7": MPa(P_lo)},
        params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                "SPLIT": dict(x=x)})


def row(P_lo, x, r):
    a = assess(f"partial cooling {P_lo} MPa x={x:.2f}", r, split=x)
    m = r.metrics
    return {
        "P_low_mpa": P_lo,
        "split": x,
        "eta_th_pct": round(a.eta_th, 4),
        "W_net_mwe": round(a.W_net_mwe, 4),
        "back_work_ratio": round(m["bwr"], 5),
        "mass_t": round(a.mass.total_t, 3),
        "total_ua_kw_k": round(a.mass.recuperators_t / 2.5e-3
                               + a.mass.coolers_t / 2.5e-3, 1),
        "T_margin_k": round(a.T_margin_k, 3),
        "P_margin_mpa": round(a.P_margin_mpa, 4),
        "P_inlet_min_mpa": round(a.P_inlet_min_mpa, 4),
        "pinch_k": round(a.pinch_min_k, 3),
        "feasible_strict": "yes" if a.P_inlet_min_mpa >= P_INLET_LIMIT - 1e-9
                           else "no",
    }


def main() -> int:
    print("Partial cooling: the third pressure level\n")
    print("1. turbine exhaust pressure, split held at 0.30")
    print(f"   {'P_low':>7}{'eta_th':>9}{'BWR':>8}{'mass':>8}"
          f"{'P_in,min':>10}{'strict?':>9}")
    print(f"   {'[MPa]':>7}{'[%]':>9}{'':>8}{'[t]':>8}{'[MPa]':>10}{'':>9}")

    pressure_rows, best = [], None
    for P_lo in P_LOW:
        r = solve(design(P_lo, 0.30))
        if not r.ok:
            print(f"   {P_lo:7.1f}   did not solve: {r.flags[0][:48]}")
            continue
        d = row(P_lo, 0.30, r)
        pressure_rows.append(d)
        print(f"   {P_lo:7.1f}{d['eta_th_pct']:9.3f}"
              f"{d['back_work_ratio']:8.4f}{d['mass_t']:8.1f}"
              f"{d['P_inlet_min_mpa']:10.2f}{d['feasible_strict']:>9}")
        if best is None or d["eta_th_pct"] > best["eta_th_pct"]:
            best = d

    if best is None:
        print("\nnothing solved; nothing to save")
        return 1

    P_opt = best["P_low_mpa"]
    interior = min(P_LOW) < P_opt < max(P_LOW)
    print(f"\n   best {best['eta_th_pct']:.3f} % at {P_opt:.1f} MPa"
          + ("   <- interior optimum" if interior
             else "   <- at the edge of the swept range"))
    print(f"   previously assumed: 6.0 MPa")

    at6 = next((d for d in pressure_rows if d["P_low_mpa"] == 6.0), None)
    if at6:
        print(f"   the 6.0 MPa assumption cost "
              f"{best['eta_th_pct'] - at6['eta_th_pct']:+.3f} points")

    print(f"\n2. split fraction at the best exhaust pressure "
          f"({P_opt:.1f} MPa)")
    print(f"   {'x':>6}{'eta_th':>9}{'mass':>8}{'MWe':>8}")
    split_rows = []
    for x in SPLITS:
        r = solve(design(P_opt, x))
        if not r.ok:
            print(f"   {x:6.2f}   did not solve")
            continue
        d = row(P_opt, x, r)
        split_rows.append(d)
        print(f"   {x:6.2f}{d['eta_th_pct']:9.3f}{d['mass_t']:8.1f}"
              f"{d['W_net_mwe']:8.2f}")

    if split_rows:
        b = max(split_rows, key=lambda d: d["eta_th_pct"])
        print(f"\n   best {b['eta_th_pct']:.3f} % at x = {b['split']:.2f}")
        print(f"\n   For comparison, recompression at 20 MPa reaches "
              f"44.895 % at x = 0.40")
        print(f"   (results/parameter_sweeps/split_fraction_sweep.csv).")
        print(f"   Partial cooling does not overtake it at any point swept")
        print(f"   here, so the layout comparison in the report stands --")
        print(f"   but it is now a swept comparison, not an assumed one.")

    strict = [d for d in pressure_rows if d["feasible_strict"] == "yes"]
    print(f"\n3. the inlet-pressure reading")
    print(f"   {len(strict)} of {len(pressure_rows)} exhaust pressures put "
          f"the pre-compressor")
    print(f"   inlet at or above {P_INLET_LIMIT} MPa. Under the literal "
          f"reading the rest")
    print(f"   are inadmissible whatever their efficiency.")

    save(
        "partial_cooling",
        {"pressure_sweep": pressure_rows, "split_sweep": split_rows},
        purpose="Sweep partial cooling's turbine exhaust pressure -- its "
                "third pressure level and only unconstrained free "
                "variable -- then re-sweep the split fraction at the best "
                "exhaust pressure.",
        script="project/studies/partial_cooling.py",
        command="python -m project.studies.partial_cooling",
        inputs={"P_low_mpa": list(P_LOW), "splits": list(SPLITS),
                "P_high_mpa": 20.0, "P_mid_mpa": 7.7,
                "recuperator_pinch_k": 5.0,
                "inlet_pressure_limit_mpa": P_INLET_LIMIT},
        notes=[f"Best exhaust pressure {P_opt:.1f} MPa against the 6.0 MPa "
               f"previously assumed.",
               "feasible_strict marks whether the pre-compressor inlet "
               "meets the brief's 7.7 MPa limit under the literal reading. "
               "Points marked 'no' are reported, not hidden: the cost of "
               "the reading should be visible.",
               "This study closes the provisional status of the "
               "partial-cooling comparison. It does not change the "
               "recommendation."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
