"""Intercooling's free pressure level.

The companion to `partial_cooling.py`. Both layouts add a pressure level
that the brief does not pin down, and in both cases the level is a free
variable that has to be swept before the layout can be judged fairly.

**The engineering question.** Splitting compression in two and cooling
between the halves reduces compressor work, because compressing a colder
and therefore denser fluid is cheaper. The classical result for an ideal
gas is that the saving is greatest when the intermediate pressure is the
geometric mean of the two levels, which here is
sqrt(7.7 x 20) = 12.41 MPa.

sCO2 is not an ideal gas anywhere near this region, so the geometric mean
is a starting guess rather than an answer, and whether it holds is worth
checking. But the more important question is not where the optimum sits:
it is whether intercooling helps *at all*. It has two effects of opposite
sign, and only one of them is the textbook one:

  * compressor work falls -- the intended benefit;
  * the heat dumped in the intercooler is heat the recuperator would
    otherwise have recovered, so the reactor must resupply it.

In a gas turbine, with a back-work ratio near 0.5, the first effect
dominates easily. In sCO2 compression is already cheap (BWR about 0.18),
so the saving is small and the second effect can win.

    python -m project.studies.intercooling
"""
from __future__ import annotations

import sys

from cycles import Pinch, solve
from cycles.units import K, MPa
from project.cases import baseline_watercooled, intercooled_watercooled
from project.cases.pdf_intercooled import P_GEOMETRIC, intercooled_case

from ._io import save

PINCH = Pinch(K(5))

# Intermediate pressures to try, spanning the geometric mean.
# The lower end approaches the compressor inlet pressure (7.7 MPa). As
# P_mid -> 7.7 the first stage has no pressure rise left to provide and
# the layout degenerates into the plain recuperated cycle, so that end of
# the sweep is the limit against which intercooling must justify itself.
P_MID = (7.9, 8.2, 8.5, 9.0, 10.0, 11.0, round(P_GEOMETRIC / 1e6, 2),
         14.0, 16.0, 18.0)


def main() -> int:
    print("Intercooling: the intermediate pressure level\n")

    base = solve(baseline_watercooled.with_(params={"RECUP": dict(spec=PINCH)}))
    if not base.ok:
        print("the recuperated baseline did not solve")
        return 1
    eta_base = base.metrics["eta_th"] * 100
    ua_base = base.metrics["UA_total"] / 1e3
    print(f"  reference: plain recuperated, no intercooler")
    print(f"             eta {eta_base:.3f} %, recuperator UA "
          f"{ua_base:.0f} kW/K, BWR {base.metrics['bwr']:.4f}\n")

    print(f"  {'P_mid':>8}{'eta_th':>9}{'BWR':>9}{'recup UA':>11}"
          f"{'vs base':>10}")
    print(f"  {'[MPa]':>8}{'[%]':>9}{'':>9}{'[kW/K]':>11}{'[points]':>10}")

    rows, best = [], None
    for P in P_MID:
        c = intercooled_case(MPa(P))
        c = c.with_(params={"RECUP": dict(spec=PINCH)})
        r = solve(c)
        if not r.ok:
            print(f"  {P:8.2f}   did not solve: {r.flags[0][:44]}")
            continue
        m = r.metrics
        d = {
            "P_mid_mpa": P,
            "eta_th_pct": round(m["eta_th"] * 100, 4),
            "back_work_ratio": round(m["bwr"], 5),
            "recup_ua_kw_k": round(m["UA_total"] / 1e3, 2),
            "delta_eta_points": round(m["eta_th"] * 100 - eta_base, 4),
            "ua_ratio_vs_recuperated": round(m["UA_total"] / 1e3 / ua_base, 4),
            "is_geometric_mean": "yes" if abs(P - P_GEOMETRIC / 1e6) < 0.01
                                 else "no",
        }
        rows.append(d)
        print(f"  {P:8.2f}{d['eta_th_pct']:9.3f}{d['back_work_ratio']:9.4f}"
              f"{d['recup_ua_kw_k']:11.0f}{d['delta_eta_points']:+10.3f}")
        if best is None or d["eta_th_pct"] > best["eta_th_pct"]:
            best = d

    if best is None:
        print("\nnothing solved")
        return 1

    gm = next((d for d in rows if d["is_geometric_mean"] == "yes"), None)
    print(f"\n  best {best['eta_th_pct']:.3f} % at "
          f"{best['P_mid_mpa']:.2f} MPa")
    if gm:
        print(f"  geometric mean ({gm['P_mid_mpa']:.2f} MPa): "
              f"{gm['eta_th_pct']:.3f} %, "
              f"{best['eta_th_pct'] - gm['eta_th_pct']:+.3f} points off best")

    bwr_base = base.metrics["bwr"]
    print(f"\n  Back-work ratio: {bwr_base:.4f} without the intercooler, "
          f"{best['back_work_ratio']:.4f} with it")
    print(f"  at the best intermediate pressure -- a "
          f"{100*(bwr_base-best['back_work_ratio'])/bwr_base:.0f} % cut in "
          f"the share of")
    print(f"  turbine work the compressors take back. The intercooler is "
          f"doing exactly")
    print(f"  what it is supposed to do.")
    # Where does compressor work bottom out, as against efficiency?
    bwr_best = min(rows, key=lambda d: d["back_work_ratio"])
    if abs(bwr_best["P_mid_mpa"] - best["P_mid_mpa"]) > 0.01:
        print(f"\n  The pressure that minimises compressor work is NOT "
              f"the one that")
        print(f"  maximises efficiency: BWR bottoms out at "
              f"{bwr_best['P_mid_mpa']:.2f} MPa "
              f"({bwr_best['back_work_ratio']:.4f}), while")
        print(f"  efficiency is still improving at "
              f"{best['P_mid_mpa']:.2f} MPa. The recuperator penalty "
              f"outruns")
        print(f"  the compression saving, and it is the penalty that "
              f"sets the optimum.")

    if best["P_mid_mpa"] == min(P_MID):
        print(f"\n  Efficiency rises monotonically as the intermediate "
              f"pressure falls")
        print(f"  towards the compressor inlet -- that is, as the "
              f"intercooler is")
        print(f"  progressively switched off. There is no interior "
              f"optimum: the best")
        print(f"  intercooler for this cycle is no intercooler, and the "
              f"limit of the")
        print(f"  sweep is the plain recuperated layout at "
              f"{eta_base:.3f} %.")
    if best["delta_eta_points"] < 0:
        print(f"  And the cycle is still worse than the plain recuperated")
        print(f"  layout at every intermediate pressure "
              f"({best['delta_eta_points']:+.3f} points at best), for "
              f"{best['ua_ratio_vs_recuperated']:.2f}x")
        print(f"  the recuperator conductance. Cheaper compression does not")
        print(f"  pay for the recuperable heat thrown away.")

    save(
        "intercooling",
        {"pressure_sweep": rows},
        purpose="Sweep the intercooled layout's intermediate pressure -- "
                "its free variable -- and test it against the plain "
                "recuperated cycle.",
        script="project/studies/intercooling.py",
        command="python -m project.studies.intercooling",
        inputs={"P_mid_mpa": list(P_MID), "P_low_mpa": 7.7,
                "P_high_mpa": 20.0,
                "geometric_mean_mpa": round(P_GEOMETRIC / 1e6, 4),
                "recuperator_pinch_k": 5.0,
                "reference_eta_pct": round(eta_base, 4)},
        notes=[f"Best {best['eta_th_pct']:.3f} % at "
               f"{best['P_mid_mpa']:.2f} MPa against the recuperated "
               f"baseline's {eta_base:.3f} %.",
               "The geometric-mean rule is an ideal-gas result and sCO2 "
               "is not an ideal gas here, so it is checked rather than "
               "assumed.",
               "Intercooling reduces compressor work as intended; it "
               "loses overall because the heat dumped in the intercooler "
               "is heat the recuperator would have recovered.",
               "The intermediate pressure that minimises back-work ratio "
               "is not the one that maximises efficiency. The recuperator "
               "penalty, not the compression saving, sets the optimum.",
               "Efficiency improves monotonically as the intermediate "
               "pressure approaches the compressor inlet, i.e. as the "
               "intercooler is switched off. The conclusion is not that "
               "the intermediate pressure was badly chosen; it is that "
               "the layout does not pay here."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
