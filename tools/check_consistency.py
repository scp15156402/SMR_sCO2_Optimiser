"""Check every number asserted in the documents against saved results.

Figures and tables are generated, so they cannot drift. Prose cannot be
generated, and prose is where a number gets stale: a sentence written
when the sweep said 41.38 % stays written after the sweep says 41.41 %.

This checks the claims that are load-bearing -- the ones a reader would
use to judge the recommendation -- against `results/`. It is not a
spell-checker for every digit in 110 pages; it is a guard on the
numbers that would embarrass the project if they were wrong.

Each check states the claim in words, computes it from saved data, and
compares. A failure prints both values and the file to look in.

    python -m tools.check_consistency
"""
from __future__ import annotations

import pathlib
import re
import sys

from project.studies._io import load

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = {
    "report": ROOT / "reports" / "final_report.tex",
    "technical": ROOT / "documentation" / "latex"
                 / "theory_and_implementation.tex",
}


def rows_by(study, stem, key):
    return {r[key]: r for r in load(study, stem)}


def checks():
    """Every check: (description, computed value, tolerance, format)."""
    cands = load("multi_objective", "candidates")
    knee = next(r for r in cands if r["verdict"] == "knee")
    front = load("multi_objective", "pareto_front")
    layouts = rows_by("layout_comparison", "layouts", "layout")
    perf = {r["quantity"]: r["value"]
            for r in load("selected_design", "performance")}

    recup_front = min((r for r in front if r["name"].startswith("recup")),
                      key=lambda r: r["mass_t"])
    best_eta = max(front, key=lambda r: r["eta_th_pct"])

    # the brief's coefficients
    USD_KG, USD_MWH, HOURS = 250, 70, 7000

    d_eta = knee["eta_th_pct"] - recup_front["eta_th_pct"]
    d_mass = knee["mass_t"] - recup_front["mass_t"]
    hardware = d_mass * 1000 * USD_KG / 1e6
    annual = d_eta / 100 * 100 * USD_MWH * HOURS / 1e6
    out = [
        ("selected efficiency", knee["eta_th_pct"], 41.41, 0.005, ".2f"),
        ("selected mass", knee["mass_t"], 87.0, 0.05, ".1f"),
        ("selected margin", knee["T_margin_k"], 4.02, 0.005, ".2f"),
        ("selected specific power", knee["mwe_per_t"], 0.476, 0.0005, ".3f"),
        ("second-law efficiency", perf["eta_second_law"], 0.684, 0.0005,
         ".3f"),
        ("recompression minus recuperated, points",
         layouts["recompression"]["eta_th_pct"]
         - layouts["recuperated"]["eta_th_pct"], 5.71, 0.005, ".2f"),
        ("selected minus best feasible recuperated, points",
         d_eta, 4.06, 0.005, ".2f"),
        ("extra mass over that baseline, t", d_mass, 18.5, 0.05, ".1f"),
        ("extra hardware cost, US$M", hardware, 4.6, 0.05, ".1f"),
        ("extra annual energy value, US$M/yr", annual, 1.99, 0.005, ".2f"),
        ("payback, years", hardware / annual, 2.3, 0.05, ".1f"),
        ("best front design beats selected by, points",
         best_eta["eta_th_pct"] - knee["eta_th_pct"], 1.4, 0.05, ".1f"),
        ("and is heavier by, t",
         best_eta["mass_t"] - knee["mass_t"], 17, 0.5, ".0f"),
        ("recuperated-only conductance ratio",
         layouts["recompression"]["recuperator_ua_kw_k"]
         / layouts["recuperated"]["recuperator_ua_kw_k"], 2.51, 0.005, ".2f"),
        ("total conductance ratio",
         layouts["recompression"]["ua_ratio_vs_recuperated"], 1.42, 0.005,
         ".2f"),
        ("partial cooling total conductance ratio",
         layouts["partial cooling"]["ua_ratio_vs_recuperated"], 1.07, 0.005,
         ".2f"),
        ("first law closes on the selected design, MW",
         perf["Q_in"] - perf["W_net"] - perf["Q_out"], 0.0, 1e-3, ".2e"),
        ("candidates", len(cands), 43, 0, "d"),
        ("feasible", sum(1 for r in cands if r["verdict"] != "infeasible"),
         36, 0, "d"),
        ("rejected", sum(1 for r in cands if r["verdict"] == "infeasible"),
         7, 0, "d"),
        ("on the front", len(front), 5, 0, "d"),
    ]

    ic = load("intercooling", "pressure_sweep")
    best_ic = max(ic, key=lambda r: r["eta_th_pct"])
    gm = next(r for r in ic if r["is_geometric_mean"] == "yes")
    out += [
        ("intercooling: geometric mean below best, points",
         best_ic["eta_th_pct"] - gm["eta_th_pct"], 0.23, 0.005, ".2f"),
        ("intercooling: best is at the lowest pressure swept",
         best_ic["P_mid_mpa"], min(r["P_mid_mpa"] for r in ic), 0, ".2f"),
    ]

    pc = load("partial_cooling", "pressure_sweep")
    best_pc = max(pc, key=lambda r: r["eta_th_pct"])
    out += [
        ("partial cooling: best exhaust pressure, MPa",
         best_pc["P_low_mpa"], 6.0, 0.001, ".1f"),
        ("partial cooling: solvable pressures meeting 7.7 MPa",
         sum(1 for r in pc if r["feasible_strict"] == "yes"), 0, 0, "d"),
    ]

    # Figures quoted in the technical document's teaching chapters.
    # These were hand-typed once, from an older run, and three of them
    # were wrong. They are checked now rather than trusted.
    ex = [r for r in load("exergy", "by_component")
          if r["layout"] == "recompression"
          and r["exergy_destroyed_mw"] != ""]
    out += [
        ("teaching: recuperated back-work ratio",
         layouts["recuperated"]["back_work_ratio"], 0.1764, 5e-5, ".4f"),
        ("teaching: intercooled back-work ratio",
         layouts["intercooled"]["back_work_ratio"], 0.1595, 5e-5, ".4f"),
        ("teaching: intercooling efficiency penalty, points",
         layouts["intercooled"]["eta_th_pct"]
         - layouts["recuperated"]["eta_th_pct"], -0.30, 0.005, ".2f"),
        ("teaching: intercooled recuperator ratio",
         layouts["intercooled"]["recuperator_ua_kw_k"]
         / layouts["recuperated"]["recuperator_ua_kw_k"], 1.23, 0.005,
         ".2f"),
        ("teaching: recompression precooler is smaller, kW/K",
         layouts["recompression"]["cooler_ua_kw_k"], 7662, 1.0, ".0f"),
        ("teaching: baseline precooler, kW/K",
         layouts["recuperated"]["cooler_ua_kw_k"], 8419, 1.0, ".0f"),
        ("teaching: compressors destroy, MW",
         sum(r["exergy_destroyed_mw"] for r in ex
             if r["kind"] == "compressor"), 1.34, 0.005, ".2f"),
        ("teaching: HTR share of destruction, %",
         next(r["fraction_pct"] for r in ex if r["block"] == "HTR"),
         45.3, 0.05, ".1f"),
    ]

    tol = [r for r in load("tolerance_sensitivity", "sweep")
           if r["solved"] == "yes"]
    out += [
        ("largest efficiency deviation, points",
         max(abs(r["delta_points"]) for r in tol), 9.6e-6, 1e-7, ".1e"),
        ("largest UA deviation, %",
         max(abs(r["delta_ua_pct"]) for r in tol), 0.041, 5e-4, ".3f"),
    ]
    mp = load("tolerance_sensitivity", "mass_propagation")
    span = max(r["mass_t"] for r in mp) - min(r["mass_t"] for r in mp)
    fr = sorted(front, key=lambda r: r["mass_t"])
    gap = min(b["mass_t"] - a["mass_t"] for a, b in zip(fr, fr[1:]))
    out += [
        ("mass span across 25-400 nodes, t", span, 0.0124, 5e-4, ".4f"),
        ("smallest gap between front designs, t", gap, 4.91, 0.005, ".2f"),
    ]
    ks = load("tolerance_sensitivity", "knee_stability")
    out.append(("distinct designs selected across resolutions",
                len({r["selected"] for r in ks}), 1, 0, "d"))
    return out


def prose_scan():
    """Flag any document number that no saved result supports.

    Deliberately narrow: it looks only for efficiency-shaped figures in
    the 30-50 % range, which is where this project's claims live.
    """
    allowed = set()
    for study, stem, col in (
        ("multi_objective", "candidates", "eta_th_pct"),
        ("layout_comparison", "layouts", "eta_th_pct"),
        ("parameter_sweeps", "pressure_sweep", "eta_recuperated_pct"),
        ("parameter_sweeps", "pressure_sweep", "eta_recompression_pct"),
        ("parameter_sweeps", "split_fraction_sweep", "eta_recompression_pct"),
        ("parameter_sweeps", "split_fraction_sweep",
         "eta_partial_cooling_pct"),
        ("intercooling", "pressure_sweep", "eta_th_pct"),
        ("partial_cooling", "pressure_sweep", "eta_th_pct"),
        ("partial_cooling", "split_sweep", "eta_th_pct"),
        ("cooling", "water_sweep", "eta_th_pct"),
        ("cooling", "water_sweep", "eta_net_of_pump_pct"),
    ):
        for r in load(study, stem):
            v = r.get(col)
            if isinstance(v, float):
                allowed |= {round(v, 2), round(v, 1), round(v, 3)}

    # Figures that legitimately do not come from results/. Each is listed
    # with the reason, so an exception is a stated decision rather than a
    # silently widened filter.
    EXTERNAL = {
        44.670: "Kim (2018), the published value being validated against",
        44.669: "this solver's reproduction of Kim, from "
                "tests/test_validation.py rather than a study",
        44.67:  "the same, rounded",
        45.3:   "an exergy destruction *share*, not an efficiency -- the "
                "scanner cannot tell percent-of-total from percent-"
                "efficiency by syntax alone",
    }

    findings = []
    for name, path in DOCS.items():
        text = path.read_text()
        for m in re.finditer(r"\\SI\{(\d\d\.\d{1,3})\}\{\\percent\}", text):
            v = float(m.group(1))
            if not 30.0 <= v <= 50.0:
                continue
            if any(abs(v - e) < 0.006 for e in EXTERNAL):
                continue
            if not any(abs(v - a) < 0.006 for a in allowed):
                line = text[:m.start()].count("\n") + 1
                findings.append((name, line, v))
    return findings


def main() -> int:
    print("Checking document claims against saved results\n")
    bad = 0
    for desc, got, want, tol, spec in checks():
        ok = abs(got - want) <= tol
        mark = "ok " if ok else "FAIL"
        print(f"  [{mark}] {desc:<52}{got:>12{spec}}  claimed "
              f"{want:{spec}}")
        bad += not ok

    print("\nScanning prose for efficiency figures with no saved source")
    findings = prose_scan()
    if not findings:
        print("  [ok ] every efficiency figure in both documents traces to "
              "a saved result\n         or to a named external reference")
    for name, line, v in findings:
        print(f"  [FAIL] {name}.tex line {line}: {v} % matches no saved "
              f"result")
    bad += len(findings)

    print(f"\n{'all consistent' if not bad else f'{bad} problem(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
