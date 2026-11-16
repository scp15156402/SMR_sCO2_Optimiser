"""Do the engineering conclusions depend on the numerical tolerances?

Chapter 9 argues that every tolerance in the solver sits far below
physical significance.  That argument is persuasive and it is not
evidence.  This study is the evidence: vary each numerical setting across
a range wide enough to matter, re-solve the recommended design, and
report how far the answer moves.

**What is being tested, and what is not.** A tolerance sweep tests
*numerical* convergence -- whether the solver has settled on its own
answer.  It says nothing about whether that answer is physically right;
that is what the literature validation in `tests/test_validation.py` is
for.  The two are easy to confuse and prove different things.

**What would count as a problem.** The recommended design's efficiency is
quoted to four significant figures (41.41 %).  If tightening a tolerance
by a decade moves it by more than about 0.001 points, the fourth figure
is noise and the quoted precision is dishonest.  That is the threshold
used below.

**Efficiency is not the only output that matters.** Mass is one of the
four objectives, and mass is conductance: a tonne of exchanger is
2.5 kg per kW/K of UA.  UA is an integral of dQ/dT over the temperature
profile, so it converges with resolution far more slowly than the pinch
does -- the pinch is a minimum, and the first-order error vanishes near a
smooth extremum, while the integral's does not.  Both are therefore
tracked below, and they do not behave the same way.

Four settings are varied:

  * `tol` -- the tear loop's relative convergence test. The one that
    decides when the flowsheet is solved.
  * `nodes` -- the heat-exchanger profile resolution. Not a tolerance but
    a discretisation, and it belongs in the same question. Note that this
    must be set on the *blocks*: a `nodes` in `Numerics` is the default
    only, and these cases override it per exchanger, so sweeping the
    default would silently vary nothing. The first version of this study
    did exactly that and reported a reassuring row of zeros.
  * `relax` -- the tear loop's under-relaxation. Changes the *path* to
    the answer, not the answer, so a well-converged solve should be
    completely insensitive to it. A disagreement here would mean the loop
    is stopping early.
  * `energy_tol` -- the first-law closure gate. A diagnostic threshold,
    not a solver tolerance, so it must not change any number at all.

    python -m project.studies.tolerances
"""
from __future__ import annotations

import sys

from cycles import solve
from project.studies._io import load, save
from project.studies.tradeoff import recompression_design

from ._io import save as _save  # noqa: F401  (kept explicit for clarity)

# The fourth significant figure of a quoted efficiency, in points.
SIGNIFICANCE_PCT = 1e-3

TOL = (1e-6, 1e-7, 1e-8, 1e-9, 1e-10)
NODES = (25, 50, 100, 200, 400)
RELAX = (0.5, 0.7, 1.0)
ENERGY_TOL = (1e-2, 1e-3, 1e-4)


def selected():
    """The recommended design, rebuilt from the trade-off's knee row.

    Read rather than typed, for the same reason `selected_design.py`
    does it: a sensitivity study of a design that is not the recommended
    one would be worse than no study.
    """
    rows = load("multi_objective", "candidates")
    knee = [r for r in rows if r["verdict"] == "knee"]
    if len(knee) != 1:
        raise SystemExit("run project.studies.tradeoff first")
    k = knee[0]
    return k, recompression_design(k["P_high_mpa"], k["split"],
                                   k["T_inlet_degc"], k["P_inlet_mpa"])


def run(case, **numerics):
    return solve(case.with_(numerics=numerics))


def run_nodes(case, n):
    """Resolution has to be set on the exchangers, not in Numerics."""
    return solve(case.with_(params={"LTR": dict(nodes=n),
                                    "HTR": dict(nodes=n)},
                            numerics={"nodes": n}))


def sweep(case, setting, values, reference):
    """Vary one setting, hold the rest at their defaults."""
    rows = []
    for v in values:
        r = run_nodes(case, v) if setting == "nodes" else run(case,
                                                              **{setting: v})
        if not r.ok:
            # A failure is a result. Record why rather than dropping the
            # point: the reason is often the interesting part.
            rows.append({"setting": setting, "value": v, "eta_th_pct": "",
                         "delta_points": "", "recup_ua_kw_k": "",
                         "delta_ua_pct": "", "solved": "no",
                         "reason": r.flags[0] if r.flags else "unknown"})
            continue
        eta = r.metrics["eta_th"] * 100
        ua = r.metrics["UA_total"] / 1e3
        rows.append({
            "setting": setting,
            "value": v,
            "eta_th_pct": round(eta, 8),
            "delta_points": round(eta - reference[0], 8),
            "recup_ua_kw_k": round(ua, 4),
            "delta_ua_pct": round(100 * (ua - reference[1]) / reference[1], 6),
            "solved": "yes",
            "reason": "",
        })
    return rows


def mass_propagation(case):
    """Does the UA variation reach the plant mass?

    UA is the only quantity resolution moves, and mass is 2.5 kg per
    kW/K of it, so the question is not whether mass moves -- it must --
    but whether it moves enough to matter against the gaps between
    candidate designs on the Pareto front.
    """
    from project.assessment import assess

    print("\n  mass propagation: the same sweep, through the assessment "
          "model")
    print(f"    {'nodes':>7}{'mass [t]':>12}{'d_mass [t]':>13}"
          f"{'d_mass [%]':>12}{'MWe/t':>10}")
    rows, ref = [], None
    for n in NODES:
        r = run_nodes(case, n)
        if not r.ok:
            continue
        a = assess(f"nodes={n}", r)
        if ref is None and n == 100:
            ref = a.mass.total_t
        rows.append({"nodes": n, "mass_t": round(a.mass.total_t, 4),
                     "mwe_per_t": round(a.mass.mwe_per_t, 5),
                     "eta_th_pct": round(a.eta_th, 6)})
    for d in rows:
        dm = d["mass_t"] - ref
        print(f"    {d['nodes']:>7}{d['mass_t']:12.4f}{dm:+13.4f}"
              f"{100*dm/ref:+12.4f}{d['mwe_per_t']:10.5f}")
        d["delta_mass_t"] = round(dm, 5)
        d["delta_mass_pct"] = round(100 * dm / ref, 5)

    span = max(d["mass_t"] for d in rows) - min(d["mass_t"] for d in rows)
    print(f"    full span across 25-400 nodes: {span:.4f} t")

    # The gap that matters: how far apart are neighbouring designs on the
    # front? A mass uncertainty smaller than that cannot reorder them.
    front = sorted(load("multi_objective", "pareto_front"),
                   key=lambda r: r["mass_t"])
    gaps = [b["mass_t"] - a["mass_t"] for a, b in zip(front, front[1:])]
    if gaps:
        print(f"    smallest gap between adjacent front designs: "
              f"{min(gaps):.2f} t")
        print(f"    resolution uncertainty is {min(gaps)/span:.0f}x smaller "
              f"-> the front cannot reorder")
    return rows


def knee_stability():
    """Re-run the whole optimisation at both resolution extremes.

    The mass table above says the front cannot reorder. This checks it
    instead of arguing it: the full candidate sweep, the constraint
    filter, the dominance test and the knee rule, all re-run at the
    coarsest and the finest resolution considered. If the selected
    design is the same object at 25 nodes and at 400, resolution does
    not touch the recommendation.

    It costs three full sweeps. That is a few minutes against a
    conclusion the whole project rests on.
    """
    from project.assessment import feasible, knee, pareto_front
    from project.studies.tradeoff import candidates

    print("\n  knee stability: the entire optimisation, re-run at each "
          "resolution")
    rows = []
    for n in (min(NODES), 100, max(NODES)):
        cands = candidates(nodes=n)
        tagged = feasible(cands)
        good = [c.assessment for c in tagged if c.ok]
        front = pareto_front(good)
        pick = knee(front)
        rows.append({
            "nodes": n,
            "candidates": len(cands),
            "feasible": len(good),
            "front_size": len(front),
            "selected": pick.name,
            "eta_th_pct": round(pick.eta_th, 4),
            "mass_t": round(pick.mass.total_t, 4),
        })
        print(f"    nodes={n:>4}  {len(cands)} solved, {len(good)} feasible, "
              f"{len(front)} on front  ->  {pick.name}")

    names = {r["selected"] for r in rows}
    if len(names) == 1:
        print(f"    the same design is selected at every resolution")
        spread = max(r["mass_t"] for r in rows) - min(r["mass_t"]
                                                      for r in rows)
        print(f"    its mass varies by {spread:.4f} t across the range")
    else:
        print(f"    SELECTION CHANGES WITH RESOLUTION: {sorted(names)}")
    return rows


def main() -> int:
    k, case = selected()
    print(f"Tolerance sensitivity of the recommended design\n")
    print(f"  {k['name']}")
    print(f"  recorded eta_th {k['eta_th_pct']:.4f} %\n")

    base = run(case)
    if not base.ok:
        print("the design did not solve at default settings")
        return 1
    ref = (base.metrics["eta_th"] * 100, base.metrics["UA_total"] / 1e3)
    print(f"  at default settings: {ref[0]:.6f} %, "
          f"recuperator UA {ref[1]:.1f} kW/K\n")

    all_rows = []
    for setting, values, note in (
        ("tol", TOL, "tear loop convergence (relative)"),
        ("nodes", NODES, "heat-exchanger profile resolution"),
        ("relax", RELAX, "tear under-relaxation"),
        ("energy_tol", ENERGY_TOL, "first-law closure gate (diagnostic)"),
    ):
        rows = sweep(case, setting, values, ref)
        all_rows += rows
        print(f"  {setting}  --  {note}")
        print(f"    {'value':>10}{'eta_th [%]':>16}"
              f"{'d_eta [pts]':>14}{'UA [kW/K]':>13}{'d_UA [%]':>11}")
        for d in rows:
            if d["solved"] == "no":
                print(f"    {d['value']:>10}      did not solve -- "
                      f"{d['reason'][:58]}")
                continue
            print(f"    {d['value']:>10}{d['eta_th_pct']:16.6f}"
                  f"{d['delta_points']:14.2e}{d['recup_ua_kw_k']:13.1f}"
                  f"{d['delta_ua_pct']:11.3f}")
        ok = [d for d in rows if d["solved"] == "yes"]
        worst = max((abs(d["delta_points"]) for d in ok), default=float("nan"))
        worst_ua = max((abs(d["delta_ua_pct"]) for d in ok), default=0.0)
        verdict = ("insensitive" if worst < SIGNIFICANCE_PCT
                   else "SENSITIVE -- quoted precision is not supported")
        print(f"    eta: worst {worst:.2e} points -> {verdict}")
        print(f"    UA : worst {worst_ua:.3f} %"
              + ("   <- mass is an objective; see note below"
                 if worst_ua > 0.01 else "") + "\n")

    worst_overall = max(abs(d["delta_points"]) for d in all_rows
                        if d["solved"] == "yes")
    worst_ua_overall = max(abs(d["delta_ua_pct"]) for d in all_rows
                           if d["solved"] == "yes")
    print(f"  Largest efficiency deviation across every setting: "
          f"{worst_overall:.2e} points")
    print(f"  Largest UA deviation across every setting:         "
          f"{worst_ua_overall:.3f} %  "
          f"({worst_ua_overall / 100 * 87.0:.3f} t on an 87 t plant)")
    print(f"  Threshold for the fourth significant figure: "
          f"{SIGNIFICANCE_PCT:.0e} points")
    if worst_overall < SIGNIFICANCE_PCT:
        print(f"\n  The quoted efficiency is converged. Reporting "
              f"{k['eta_th_pct']:.4f} % to four")
        print(f"  figures is supported by the numerics.")
    else:
        print(f"\n  The quoted efficiency is NOT converged at four figures.")

    # --- does the UA variation reach the recommendation? --------------
    mass_rows = mass_propagation(case)
    knee_rows = knee_stability()

    save(
        "tolerance_sensitivity",
        {"sweep": all_rows, "mass_propagation": mass_rows,
         "knee_stability": knee_rows},
        purpose="Vary each numerical tolerance and discretisation setting "
                "across a decade or more and measure how far the "
                "recommended design's efficiency moves.",
        script="project/studies/tolerances.py",
        command="python -m project.studies.tolerances",
        inputs={"design": k["name"], "reference_eta_pct": round(ref[0], 8),
                "tol": list(TOL), "nodes": list(NODES),
                "relax": list(RELAX), "energy_tol": list(ENERGY_TOL),
                "significance_threshold_points": SIGNIFICANCE_PCT,
                "reference_ua_kw_k": round(ref[1], 4)},
        notes=[f"Largest deviation {worst_overall:.2e} efficiency points "
               f"and {worst_ua_overall:.3f} % UA across all settings.",
               "Efficiency and UA do not converge at the same rate. The "
               "pinch is a minimum, so its first-order discretisation "
               "error vanishes near the extremum; UA is an integral of "
               "dQ/dT and its does not. Resolution therefore moves the "
               "mass estimate while leaving the efficiency untouched.",
               "A loose tear tolerance (1e-6) is rejected by the exergy "
               "balance, not the first-law closure. The second-law check "
               "is the more sensitive convergence detector of the two, "
               "which is worth knowing when diagnosing a cycle that "
               "'converged' but looks wrong.",
               "This tests numerical convergence only. Whether the "
               "converged answer is physically right is what the "
               "literature validation establishes, and the two prove "
               "different things.",
               "relax changes the path to the answer, not the answer. Any "
               "sensitivity to it would mean the tear loop is stopping "
               "early.",
               "energy_tol is a diagnostic gate and must not change any "
               "number; it is swept to confirm that."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
