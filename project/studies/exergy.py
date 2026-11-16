"""Where each layout destroys its work potential.

Thermal efficiency says how much of the reactor's heat became work. It does
not say where the rest went, because energy is conserved: a first-law
balance can report a loss without naming a culprit. Exergy is not conserved,
so destruction can be attributed to a component, and the ranking is usually
not what the efficiency table suggests.

This run reports it for all four layouts, and sweeps the recompression split
fraction to show which irreversibility each design move trades against
which.

    python -m project.studies.exergy
"""
from __future__ import annotations

import sys

from ._io import save
from cycles import Effectiveness, Pinch, solve
from cycles.units import K
from project.cases import (baseline_watercooled, intercooled_watercooled,
                           partial_cooling_watercooled,
                           recompression_watercooled)

PINCH = Pinch(K(5))

LAYOUTS = [
    ("recuperated",     baseline_watercooled,        {"RECUP": PINCH}),
    ("recompression",   recompression_watercooled,   {"LTR": PINCH, "HTR": PINCH}),
    ("partial cooling", partial_cooling_watercooled, {"LTR": PINCH, "HTR": PINCH}),
    ("intercooled",     intercooled_watercooled,     {}),
]


def pinched(case, specs):
    return case.with_(params={k: dict(spec=v) for k, v in specs.items()}) \
        if specs else case


def component_rows():
    """One row per component per layout, for saving.

    Computed from the same solved results the printed tables use. A
    component whose destruction cannot be computed is written with an
    empty value and its reason, never as a zero -- a missing number and a
    zero mean very different things here, and the heater is exactly the
    case where confusing them would flatter the model.
    """
    rows = []
    for name, case, specs in LAYOUTS:
        r = solve(pinched(case, specs))
        if not r.ok:
            continue
        ex, m = r.exergy, r.metrics
        for bid, c in ex["components"].items():
            computable = c["E_D"] is not None
            rows.append({
                "layout": name,
                "block": bid,
                "kind": c["kind"],
                "exergy_destroyed_mw": round(c["E_D"] / 1e6, 5)
                                       if computable else "",
                "fraction_pct": round(ex["fractions"][bid], 3)
                                if computable and ex["fractions"] else "",
                "specific_kj_kg": round(c["E_D"] / m["mdot"] / 1e3, 4)
                                  if computable else "",
                "reason_unavailable": "" if computable else c["reason"],
            })
    return rows


def balance_rows():
    """The exergy balance per layout, with its residual."""
    rows = []
    for name, case, specs in LAYOUTS:
        r = solve(pinched(case, specs))
        if not r.ok:
            continue
        ex = r.exergy
        rows.append({
            "layout": name,
            "eta_th_pct": round(r.metrics["eta_th"] * 100, 4),
            "supplied_mw": round(ex["Ex_supplied"] / 1e6, 5),
            "to_work_mw": round(ex["Ex_to_work"] / 1e6, 5),
            "destroyed_known_mw": round(ex["E_D_known"] / 1e6, 5),
            "shed_mw": round(ex["Ex_shed"] / 1e6, 5),
            "residual": (f"{ex['balance_residual']:.3e}"
                         if ex["balance_residual"] is not None else ""),
            "complete": "yes" if ex["complete"] else "no",
            "incomplete_reason": "" if ex["complete"] else ex["balance_reason"],
        })
    return rows


def per_component():
    print("exergy destruction by component, 100 MWth, 5 K recuperator pinch\n")
    for name, case, specs in LAYOUTS:
        r = solve(pinched(case, specs))
        if not r.ok:
            print(f"  {name}: FLAGGED {r.flags}\n")
            continue
        ex, m = r.exergy, r.metrics
        print(f"  {name}   eta_th {m['eta_th']*100:.3f} %   "
              f"destroyed {ex['E_D_known']/1e6:.2f} MW"
              f"{'' if ex['complete'] else '  (incomplete)'}")
        rows = sorted(ex["components"].items(),
                      key=lambda kv: -(kv[1]["E_D"] if kv[1]["E_D"] is not None
                                       else -1))
        for bid, c in rows:
            if c["E_D"] is None:
                print(f"      {bid:<8}{c['kind']:<16}{'--':>9}"
                      f"   {c['reason']}")
            else:
                frac = ex["fractions"][bid] if ex["fractions"] else float("nan")
                spec = c["E_D"] / m["mdot"] / 1e3
                print(f"      {bid:<8}{c['kind']:<16}"
                      f"{c['E_D']/1e6:8.3f} MW{frac:7.1f} %"
                      f"{spec:8.2f} kJ/kg")
        res = ex["balance_residual"]
        if res is not None:
            print(f"      balance: supplied {ex['Ex_supplied']/1e6:.2f} = "
                  f"work {ex['Ex_to_work']/1e6:.2f} + destroyed "
                  f"{ex['E_D_known']/1e6:.2f} + shed {ex['Ex_shed']/1e6:.2f} MW"
                  f"   (residual {res:.1e})")
        else:
            print(f"      balance: not closable -- {ex['balance_reason']}")
        print()


def side_by_side():
    """The same numbers as a comparison, which is what a report wants."""
    print("\ndestruction by component kind [MW]\n")
    kinds = ("turbine", "compressor", "heat_exchanger", "mixer", "cooler")
    print(f"  {'layout':<17}" + "".join(f"{k[:9]:>11}" for k in kinds)
          + f"{'known':>9}{'eta':>8}")
    for name, case, specs in LAYOUTS:
        r = solve(pinched(case, specs))
        if not r.ok:
            continue
        bk = r.exergy["by_kind"]
        cells = "".join(
            f"{bk[k]/1e6:11.3f}" if bk.get(k) is not None else f"{'--':>11}"
            for k in kinds)
        print(f"  {name:<17}{cells}{r.exergy['E_D_known']/1e6:9.2f}"
              f"{r.metrics['eta_th']*100:8.3f}")
    print("\n  'known' excludes the heater, which has no heat-source model,")
    print("  so it is a partial sum in every row and is never presented as")
    print("  a total. The rows are still comparable: the same term is")
    print("  missing from each.")


def _sweep(label, spec, note):
    print(f"\n{label}\n")
    print(f"  {'x':>5}{'eta_th':>9}{'UA tot':>9}{'compressors':>13}"
          f"{'recups':>9}{'mixer':>8}{'known':>8}")
    print(f"  {'':>5}{'[%]':>9}{'[kW/K]':>9}{'[MW]':>13}"
          f"{'[MW]':>9}{'[MW]':>8}{'[MW]':>8}")
    best = None
    for x in (0.20, 0.25, 0.30, 0.33, 0.36, 0.40, 0.45):
        c = recompression_watercooled.with_(
            name=f"x{x}",
            params={"LTR": dict(spec=spec), "HTR": dict(spec=spec),
                    "SPLIT": dict(x=x)})
        r = solve(c)
        if not r.ok:
            print(f"  {x:5.2f}  FLAGGED {r.flags[:1]}")
            continue
        bk, m = r.exergy["by_kind"], r.metrics
        if best is None or m["eta_th"] > best[1]:
            best = (x, m["eta_th"])
        print(f"  {x:5.2f}{m['eta_th']*100:9.3f}{m['UA_total']/1e3:9.0f}"
              f"{bk['compressor']/1e6:13.3f}{bk['heat_exchanger']/1e6:9.3f}"
              f"{bk['mixer']/1e6:8.3f}{r.exergy['E_D_known']/1e6:8.2f}")
    if best:
        print(f"  best efficiency at x = {best[0]:.2f}")
    print(note)


def split_sweep():
    """Which irreversibility does raising x trade against which?"""
    print("\n\nrecompression split fraction")
    print("\n  Raising x sends more flow through the warm recompressor and")
    print("  less up the recuperator's cold side. Watch the compressor and")
    print("  recuperator columns move in opposite directions: that is the")
    print("  trade, made visible as two irreversibilities rather than as one")
    print("  efficiency number.")

    _sweep("at a fixed 5 K pinch -- the exchanger is allowed to grow",
           PINCH,
           "\n  No optimum appears, because a fixed pinch lets UA rise"
           "\n  without limit: efficiency climbs and destruction falls all"
           "\n  the way, paid for with exchanger. Note the mixer column"
           "\n  reaching ~0 near x = 0.40 -- that is the two mixing streams"
           "\n  arriving at the same state, which is what capacity-rate"
           "\n  matching means, seen directly.")

    _sweep("at a fixed 0.90 effectiveness -- the exchanger is held",
           Effectiveness(0.90),
           "\n  Now the exchanger cannot grow to absorb the change, and an"
           "\n  optimum appears. This is the honest sweep: the first one"
           "\n  measures how much hardware you are willing to buy."
           "\n\n  Lower destruction does not automatically mean higher"
           "\n  efficiency. Compare the two tables at the same x before"
           "\n  concluding anything from a destruction number alone.")


def main() -> int:
    per_component()
    side_by_side()
    split_sweep()

    save(
        "exergy",
        {"by_component": component_rows(), "balance": balance_rows()},
        purpose="Second-law accounting: where the available work is "
                "destroyed, by component and by layout.",
        script="project/studies/exergy.py",
        command="python -m project.studies.exergy",
        inputs={"recuperator_pinch_k": 5.0, "T0_k": 298.15, "P0_pa": 101325},
        notes=["The heater's destruction is not computable: the model has "
               "no heat-source boundary temperature. Those rows carry an "
               "empty value and a reason, never a zero.",
               "Every total that excludes the heater is labelled "
               "incomplete rather than presented as a total.",
               "Supply T_source to the heater and the number becomes "
               "computable; at 650 degC the heater would be the largest "
               "irreversibility in the cycle."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
