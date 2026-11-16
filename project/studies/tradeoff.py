"""R5: the multi-objective step, and the recommendation it leads to.

This is the run the brief's deliverables come from.  It does four things,
in the order the brief sets out:

  1. sweep the decision variables to generate candidate designs
  2. filter out the ones that break a constraint, and say which and why
  3. find the Pareto front among what survives
  4. pick a knee point, and be explicit that the rule is a judgement

Nothing here solves anything.  Every candidate is a solved cycle, read.

    python -m project.studies.tradeoff
"""
from __future__ import annotations

import sys

from cycles import Pinch, solve
from cycles.units import K, MPa, degC
from project.assessment import assess, feasible, knee, pareto_front
from project.assessment.cost import payback_years
from project.cases import (baseline_watercooled, intercooled_watercooled,
                           partial_cooling_watercooled,
                           recompression_watercooled)
from ._io import save

PINCH = Pinch(K(5))
P_LOW = MPa(7.7)


# Maximum pressures to try.  Swept as absolute pressure rather than as a
# ratio, because the binding constraint is "P_max <= 20 MPa": sweeping a
# ratio against a varying inlet pressure walks straight through the limit.
P_HIGH = (16.0, 18.0, 19.0, 20.0)

# Compressor inlet states.  The brief lists this as a decision variable
# (R2) and it is the only one that moves objective 4: pushing the inlet
# further above the critical point buys operating margin and costs
# efficiency, because the fluid is less dense to compress.
INLETS = ((32.0, 7.7), (33.0, 7.7), (35.0, 7.7), (32.0, 8.2), (35.0, 8.5))

# Split fractions. Recompression and partial cooling get different grids
# because partial cooling costs more to solve and its optimum sits higher.
# Hoisted to module level so the saved manifest records the grid that was
# actually swept, rather than a number typed into it separately.
SPLITS = (0.20, 0.25, 0.30, 0.35)
PC_SPLITS = (0.25, 0.30, 0.35)

# Recompression's own sub-grid.
RECOMP_P_HIGH = (18.0, 20.0)
RECOMP_INLETS = ((32.0, 7.7), (35.0, 7.7))


def _at(case, nodes):
    """Apply a resolution override to every heat exchanger in a case."""
    if nodes is None:
        return case
    from cycles.blocks import get
    hx = [n.id for n in case.layout.nodes
          if get(n.type).TYPE == "heat_exchanger"]
    return case.with_(params={b: dict(nodes=nodes) for b in hx},
                      numerics={"nodes": nodes})


def recompression_name(P_hi, x, T1) -> str:
    """The name a recompression candidate carries, in one place.

    The name is the key that links a row of `candidates.csv` back to the
    case that produced it, so it must be generated, never typed.
    """
    return f"recompression {P_hi:.0f}MPa x={x:.2f} {T1:.0f}C"


def recompression_design(P_hi, x, T1, P1):
    """Build one recompression candidate.

    This is the *only* place a recompression case is constructed. The
    sweep below calls it, and so does `selected_design.py` when it
    rebuilds the knee point to draw its T-s diagram. A figure and a
    recommendation can therefore no longer describe different cycles --
    which they did once, before this function existed.
    """
    return _inlet(recompression_watercooled, T1, P1, "PC").with_(
        name=f"recomp_{P_hi}_{x}_{T1}",
        params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                "MC": dict(P_out=MPa(P_hi)),
                "RC": dict(P_out=MPa(P_hi)),
                "SPLIT": dict(x=x)})


def _inlet(case, T_c, P_mpa, cooler):
    return case.with_(
        boundary={"s1": {"T": degC(T_c), "P": MPa(P_mpa)}},
        params={cooler: dict(T_out=degC(T_c))})


def candidates(nodes=None):
    """Sweep the decision variables the brief lists, layout by layout.

    `nodes` overrides every heat exchanger's profile resolution. It
    exists so the tolerance study can re-run this entire sweep at a
    different resolution and check that the Pareto front and the knee
    point do not move -- a claim that is worth testing rather than
    inferring from the mass arithmetic.
    """
    out = []

    # recuperated: maximum pressure and compressor inlet state
    for P_hi in P_HIGH:
        for T1, P1 in INLETS:
            c = _inlet(baseline_watercooled, T1, P1, "COOLER").with_(
                name=f"recup_{P_hi}_{T1}_{P1}",
                params={"RECUP": dict(spec=PINCH),
                        "COMP": dict(P_out=MPa(P_hi))})
            r = solve(_at(c, nodes))
            if r.ok:
                out.append(assess(
                    f"recuperated {P_hi:.0f}MPa {T1:.0f}C/{P1}", r))

    # recompression: maximum pressure, split fraction, inlet state
    for P_hi in RECOMP_P_HIGH:
        for x in SPLITS:
            for T1, P1 in RECOMP_INLETS:
                r = solve(_at(recompression_design(P_hi, x, T1, P1), nodes))
                if r.ok:
                    out.append(assess(
                        recompression_name(P_hi, x, T1), r, split=x))

    # partial cooling: split fraction and inlet state
    for x in PC_SPLITS:
        for T1, P1 in ((32.0, 7.7), (35.0, 7.7)):
            c = partial_cooling_watercooled.with_(
                name=f"pc_{x}_{T1}",
                boundary={"s1": {"T": degC(T1), "P": MPa(P1)}},
                params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                        "SPLIT": dict(x=x), "PC2": dict(T_out=degC(T1))})
            r = solve(_at(c, nodes))
            if r.ok:
                out.append(assess(
                    f"partial cooling x={x:.2f} {T1:.0f}C", r, split=x))

    r = solve(_at(intercooled_watercooled, nodes))
    if r.ok:
        out.append(assess("intercooled", r))
    return out


def rows(tagged, front, pick):
    """One row per candidate, with its verdict.

    This is the single table everything downstream reads: the printed
    summary below, the CSV on disk, and every figure in the report. There
    is deliberately no second place where a candidate's numbers are
    computed -- that is what let a figure and a recommendation disagree
    once already.
    """
    out = []
    for c in tagged:
        a = c.assessment
        if not c.ok:
            verdict = "infeasible"
        elif a is pick:
            verdict = "knee"
        elif any(a is f for f in front):
            verdict = "front"
        else:
            verdict = "dominated"
        out.append({
            "name": a.name,
            "P_high_mpa": round(a.P_max_mpa, 3),
            "P_inlet_mpa": round(a.P_inlet_min_mpa, 3),
            "T_inlet_degc": round(a.T_inlet_min_c, 2),
            "T_turbine_degc": round(a.T_turbine_c, 1),
            "split": round(a.split, 3) if a.split is not None else "",
            "eta_th_pct": round(a.eta_th, 4),
            "eta_second_law": round(a.eta_second_law, 4),
            "W_net_mwe": round(a.W_net_mwe, 4),
            "heat_per_mwe": round(a.heat_per_mwe, 4),
            "mass_t": round(a.mass.total_t, 3),
            "volume_m3": round(a.mass.volume_m3, 2),
            "mwe_per_t": round(a.mass.mwe_per_t, 4),
            "recuperators_t": round(a.mass.recuperators_t, 3),
            "coolers_t": round(a.mass.coolers_t, 3),
            "machines_t": round(a.mass.machines_t, 3),
            "mwe_per_m3": round(a.mass.mwe_per_m3, 4),
            "hardware_musd": round(a.cost.hardware_musd, 4),
            "annual_energy_musd": round(a.cost.annual_energy_musd, 4),
            "annualised_musd": round(a.cost.annualised_musd, 4),
            "cost_proxy_musd": round(a.cost.cost_proxy_musd, 4),
            "T_margin_k": round(a.T_margin_k, 3),
            "P_margin_mpa": round(a.P_margin_mpa, 4),
            "pinch_k": round(a.pinch_min_k, 3),
            "verdict": verdict,
            "violations": "; ".join(c.violations),
        })
    return out


def main() -> int:
    print("R5 multi-objective trade-off\n")
    print("1. candidate designs from the decision-variable sweeps")
    cands = candidates()
    print(f"   {len(cands)} solved\n")

    print("2. constraint filter")
    tagged = feasible(cands)
    good = [c.assessment for c in tagged if c.ok]
    bad = [c for c in tagged if not c.ok]
    print(f"   {len(good)} feasible, {len(bad)} rejected"
          f"   (strict reading of the inlet-pressure limit)")
    for c in bad[:8]:
        print(f"     {c.assessment.name:<30} {'; '.join(c.violations)}")
    if len(bad) > 8:
        print(f"     ... and {len(bad)-8} more")

    lenient = [c.assessment for c in
               feasible(cands, {"strict_inlet_pressure": False}) if c.ok]
    extra = len(lenient) - len(good)
    if extra:
        print(f"\n   Reading the limit as two-phase safety instead of an")
        print(f"   absolute pressure admits {extra} more design(s) -- the")
        print(f"   partial cooling family, whose pre-compressor sits at")
        print(f"   6.00 MPa but 32 degC, well clear of the dome. Worth")
        print(f"   settling with the course staff; it changes the answer.")

    print("\n3. Pareto front over the brief's four objectives")
    front = pareto_front(good)
    print(f"   {len(front)} of {len(good)} are non-dominated\n")
    hdr = (f"   {'design':<28}{'eta':>7}{'mass':>7}{'cost':>8}"
           f"{'margin':>8}{'MWe/t':>8}")
    print(hdr)
    print(f"   {'':<28}{'[%]':>7}{'[t]':>7}{'[M$/y]':>8}{'[K]':>8}{'':>8}")
    for a in sorted(front, key=lambda a: -a.eta_th):
        print(f"   {a.name:<28}{a.eta_th:7.2f}{a.mass.total_t:7.1f}"
              f"{a.cost.cost_proxy_musd:8.2f}{a.T_margin_k:8.2f}"
              f"{a.mass.mwe_per_t:8.3f}")

    print("\n4. knee point")
    pick = knee(front)
    # compare against the best feasible baseline, not an arbitrary one
    recups = [a for a in good if a.name.startswith("recuperated")]
    base = max(recups, key=lambda a: a.eta_th) if recups else good[0]
    print(f"   {pick.name}")
    print(f"     eta {pick.eta_th:.3f} %   second-law {pick.eta_second_law:.3f}")
    print(f"     {pick.W_net_mwe:.2f} MWe   {pick.heat_per_mwe:.3f} MWth/MWe")
    print(f"     {pick.mass.total_t:.1f} t   {pick.mass.volume_m3:.1f} m3   "
          f"{pick.mass.mwe_per_t:.3f} MWe/t   {pick.mass.mwe_per_m3:.3f} MWe/m3")
    print(f"     hardware ${pick.cost.hardware_musd:.1f} M   "
          f"energy ${pick.cost.annual_energy_musd:.2f} M/yr")
    print(f"     margin {pick.T_margin_k:.2f} K / {pick.P_margin_mpa:.3f} MPa "
          f"above critical, pinch {pick.pinch_min_k:.2f} K")
    if pick is not base:
        pb = payback_years(pick.mass, pick.cost, base.mass, base.cost)
        print(f"     vs {base.name}: {pick.eta_th-base.eta_th:+.2f} points, "
              f"{pick.mass.total_t-base.mass.total_t:+.1f} t, "
              f"payback {pb:.1f} yr")

    print("\n   The knee weights all four objectives equally, which nobody")
    print("   asked for. It is a starting point for the argument, not the")
    print("   answer: shift the weights and the pick moves along the front.")

    save(
        "multi_objective",
        {"candidates": rows(tagged, front, pick),
         "pareto_front": rows([c for c in tagged
                               if c.ok and any(c.assessment is f
                                               for f in front)],
                              front, pick)},
        purpose="R5: sweep the decision variables, filter on the brief's "
                "constraints, find the Pareto front, pick a knee point.",
        script="project/studies/tradeoff.py",
        command="python -m project.studies.tradeoff",
        inputs={"P_high_mpa": list(P_HIGH),
                "recompression_P_high_mpa": list(RECOMP_P_HIGH),
                "inlets_degc_mpa": [list(i) for i in INLETS],
                "splits_recompression": list(SPLITS),
                "splits_partial_cooling": list(PC_SPLITS),
                "recuperator_pinch_k": 5.0,
                "strict_inlet_pressure": True},
        notes=["The knee weights all four objectives equally. That is a "
               "rule, not a result: shifting the weights moves the pick "
               "along the front.",
               "strict_inlet_pressure=True reads the brief's 7.7 MPa limit "
               "as applying to every compressor inlet, which rejects the "
               "partial cooling family. The alternative reading admits it "
               "and changes the recommendation."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
