"""Regenerate the data behind the figures in the theory document.

The plots in documentation/ are built from numbers this solver produces, not
from sketches, so they must be rebuilt whenever the model changes. Run this,
then rebuild the PDF:

    python -m tools.make_figures
    cd documentation/latex && make

Writes to documentation/latex/data/.
"""
from __future__ import annotations

import pathlib
import sys

from CoolProp.CoolProp import PropsSI

from cycles import Effectiveness, Pinch, solve
from cycles.units import K
from project.cases import baseline_watercooled, pdf_baseline
from project.studies._io import load

OUT = pathlib.Path(__file__).resolve().parents[1] / "documentation" / "latex" / "data"


def _dump_profile(path, profile, q_total):
    """A heat exchanger temperature profile, x rescaled to absolute duty."""
    with open(path, "w") as f:
        f.write("Q Thot Tcold dT\n")
        for x, th, tc, d in zip(profile.x, profile.T_hot, profile.T_cold,
                                profile.dT):
            f.write(f"{x*q_total/1e3:.4f} {th-273.15:.4f} "
                    f"{tc-273.15:.4f} {d:.4f}\n")


from project.cases import (intercooled_watercooled,
                           partial_cooling_watercooled,
                           recompression_watercooled)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # --- recuperator T-Q profile ------------------------------------------
    r = solve(pdf_baseline)
    e = r.blocks["RECUP"]
    _dump_profile(OUT / "recup_profile.dat", e["profile"], e["Q"])
    print(f"recup      Q={e['Q']/1e3:7.1f} kJ/kg  pinch={e['pinch']:6.2f} K "
          f"at x={e['pinch_at']:.2f}")

    # --- precooler against cooling water: the internal pinch --------------
    rw = solve(baseline_watercooled)
    ec = rw.blocks["COOLER"]
    _dump_profile(OUT / "precooler_profile.dat", ec["coolant_profile"],
                  ec["q_total"])
    print(f"precooler  Q={ec['q_total']/1e3:7.1f} kJ/kg  "
          f"pinch={ec['coolant_pinch']:6.2f} K at x={ec['coolant_pinch_at']:.2f}")

    # --- the cost divergence: UA and efficiency against effectiveness -----
    with open(OUT / "ua_vs_eps.dat", "w") as f:
        f.write("eps UA eta pinch\n")
        for i in range(27):
            eps = 0.70 + i * 0.01
            rr = solve(pdf_baseline.with_(
                params={"RECUP": dict(spec=Effectiveness(eps))}))
            if rr.metrics:
                f.write(f"{eps:.3f} {rr.metrics['UA_total']/1e3:.3f} "
                        f"{rr.metrics['eta_th']*100:.4f} "
                        f"{rr.metrics['pinch_min']:.3f}\n")
    print("ua_vs_eps  written")

    # --- the cp mismatch that causes the pinch ----------------------------
    with open(OUT / "cp_co2.dat", "w") as f:
        f.write("T cp_hp cp_lp\n")
        for i in range(141):
            T = 303.15 + i * 2.0
            f.write(f"{T-273.15:.2f} "
                    f"{PropsSI('C','P',20e6,'T',T,'CO2')/1e3:.5f} "
                    f"{PropsSI('C','P',7.7e6,'T',T,'CO2')/1e3:.5f}\n")
    print("cp_co2     written")

    # --- exergy destruction by kind, every layout -------------------------
    # One row per layout, one column per component kind, so a stacked bar
    # chart reads straight off it. The heater is absent from every row
    # because no heat-source model exists; it is missing identically, so
    # the rows stay comparable.
    PINCH = Pinch(K(5))
    layouts = [
        ("recuperated",     baseline_watercooled,        {"RECUP": PINCH}),
        ("recompression",   recompression_watercooled,   {"LTR": PINCH, "HTR": PINCH}),
        ("partial-cooling", partial_cooling_watercooled, {"LTR": PINCH, "HTR": PINCH}),
        ("intercooled",     intercooled_watercooled,     {}),
    ]
    kinds = ("heat_exchanger", "turbine", "cooler", "compressor", "mixer")
    with open(OUT / "exergy_by_layout.dat", "w") as f:
        f.write("layout " + " ".join(kinds) + " total eta\n")
        for name, case, specs in layouts:
            c = case.with_(params={k: dict(spec=v) for k, v in specs.items()}) \
                if specs else case
            r = solve(c)
            if not r.ok:
                continue
            bk = r.exergy["by_kind"]
            cells = " ".join(
                f"{(bk.get(k) or 0.0)/1e6:.4f}" for k in kinds)
            f.write(f"{name} {cells} {r.exergy['E_D_known']/1e6:.4f} "
                    f"{r.metrics['eta_th']*100:.4f}\n")
    print("exergy_by_layout written")

    # --- how destruction moves with the split fraction --------------------
    with open(OUT / "exergy_vs_x.dat", "w") as f:
        f.write("x eta compressors recups mixer coolers total UA\n")
        for i in range(21):
            x = 0.15 + i * 0.015
            r = solve(recompression_watercooled.with_(
                name=f"x{x:.3f}",
                params={"LTR": dict(spec=Effectiveness(0.90)),
                        "HTR": dict(spec=Effectiveness(0.90)),
                        "SPLIT": dict(x=x)}))
            if not r.ok:
                continue
            bk = r.exergy["by_kind"]
            f.write(f"{x:.4f} {r.metrics['eta_th']*100:.4f} "
                    f"{(bk.get('compressor') or 0)/1e6:.4f} "
                    f"{(bk.get('heat_exchanger') or 0)/1e6:.4f} "
                    f"{(bk.get('mixer') or 0)/1e6:.4f} "
                    f"{(bk.get('cooler') or 0)/1e6:.4f} "
                    f"{r.exergy['E_D_known']/1e6:.4f} "
                    f"{r.metrics['UA_total']/1e3:.1f}\n")
    print("exergy_vs_x written")

    deliverable_plots(OUT)

    print(f"\nall data in {OUT}")
    return 0


def deliverable_plots(OUT):
    """Translate saved study output into pgfplots tables.

    This function used to solve cycles of its own. It no longer solves
    anything: every number it writes was computed by a study in
    `project/studies/` and read back from `results/`. Run the studies
    first; `load()` says which command to run if a file is missing.
    """
    # --- T-s diagram of the selected design ---------------------------
    # Read, not re-solved. The selected design is whatever
    # `selected_design.py` rebuilt from the trade-off's knee row, so this
    # figure is the recommendation by construction.
    states = load("selected_design", "state_points")
    with open(OUT / "ts_recompression.dat", "w") as f:
        f.write("s T P h stream\n")
        for r in sorted(states, key=lambda r: (len(r["stream"]),
                                               r["stream"])):
            f.write(f"{r['s_kj_kgk']:.5f} {r['T_degc']:.3f} "
                    f"{r['P_mpa']:.4f} {r['h_kj_kg']:.3f} "
                    f"{r['stream']}\n")

    for stem, out in (("ts_loop", "ts_path"), ("ts_branch", "ts_branch")):
        rows = load("selected_design", stem)
        with open(OUT / f"{out}.dat", "w") as f:
            f.write("s T name\n")
            for r in rows:
                label = r["label"] if r["label"] != "" else "~"
                f.write(f"{r['s_kj_kgk']:.5f} {r['T_degc']:.3f} "
                        f"{label}\n")
    print(f"ts_recompression written ({len(states)} states, "
          f"from results/selected_design)")

    # ------------------------------------------------------------------
    # Everything below is a *translation* of saved study output into the
    # whitespace-delimited form pgfplots reads. Nothing here solves a
    # cycle. That is the whole point: the figures and the recommendation
    # now read the same files, so they cannot describe different designs.
    # ------------------------------------------------------------------

    def _dat(path, header, rows, fields):
        """Write one plot table, skipping rows with a missing value."""
        n = 0
        with open(path, "w") as f:
            f.write(header + "\n")
            for r in rows:
                vals = [r[k] for k in fields]
                if any(v == "" or v is None for v in vals):
                    continue
                f.write(" ".join(f"{v:g}" if isinstance(v, float) else str(v)
                                 for v in vals) + "\n")
                n += 1
        return n

    # --- efficiency vs maximum pressure -------------------------------
    pres = load("parameter_sweeps", "pressure_sweep")
    n = _dat(OUT / "eta_vs_rp.dat", "P_high rp eta_recup eta_recomp", pres,
             ["P_high_mpa", "pressure_ratio",
              "eta_recuperated_pct", "eta_recompression_pct"])
    print(f"eta_vs_rp written ({n} points, from results/parameter_sweeps)")

    # --- efficiency vs split fraction ---------------------------------
    spl = load("parameter_sweeps", "split_fraction_sweep")
    n = _dat(OUT / "eta_vs_x.dat", "x eta_recomp eta_partial", spl,
             ["split", "eta_recompression_pct", "eta_partial_cooling_pct"])
    print(f"eta_vs_x written ({n} points, from results/parameter_sweeps)")

    # --- Pareto -------------------------------------------------------
    # One file per verdict: pgfplots cannot filter rows on a text column
    # without preamble trickery, and four small files beat one clever
    # style. The verdicts come from the study, not from a second
    # classification written here -- that duplication is what previously
    # let the figure and the table disagree.
    cands = load("multi_objective", "candidates")
    cols = ["eta_th_pct", "mass_t", "cost_proxy_musd", "T_margin_k",
            "mwe_per_t"]
    head = "eta mass cost margin mwe_per_t"
    counts = {}
    for verdict in ("infeasible", "dominated", "front", "knee"):
        group = [r for r in cands if r["verdict"] == verdict]
        counts[verdict] = _dat(OUT / f"pareto_{verdict}.dat", head,
                               group, cols)
    _dat(OUT / "pareto.dat", head + " status", cands, cols + ["verdict"])
    print("pareto written (" + ", ".join(f"{k} {v}" for k, v in
                                         counts.items())
          + ", from results/multi_objective)")


if __name__ == "__main__":
    sys.exit(main())
