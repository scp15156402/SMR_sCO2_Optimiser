"""The recommended design, solved once, with its full state table saved.

Why this study exists at all:

The brief asks for a T-s diagram of the chosen cycle. The obvious way to
produce one is to write down the chosen cycle's parameters in the
plotting script and solve it there.  That is exactly what was done
before, and it broke: the plot was built from the *default* recompression
case (32 degC inlet, default split) while its caption claimed to show the
recommended design (35 degC, x = 0.25, 20 MPa).  The two drifted apart
silently, and the error was caught by looking at a rendered page rather
than by reading code.

This study removes the possibility.  It reads the knee point out of
`results/multi_objective/candidates.csv` -- the row the trade-off study
itself labelled -- and rebuilds that case through
`tradeoff.recompression_design()`, the same factory the sweep used.  The
chosen design is therefore defined in exactly one place, and the figure
cannot describe a different cycle from the recommendation.

It then checks that the efficiency it gets back matches the one recorded
in the CSV.  If the two disagree, something changed between the two runs
and the study fails loudly rather than quietly saving a mismatched
diagram.

    python -m project.studies.selected_design

Requires `python -m project.studies.tradeoff` to have been run first.
"""
from __future__ import annotations

import sys

from cycles import solve
from cycles.units import to_degC, to_MPa

from ._io import load, save
from .tradeoff import recompression_design

# How closely the rebuilt case must reproduce the recorded efficiency.
#
# This is a reproducibility check, not a physical tolerance, so the limit
# is set by how precisely the CSV stores the number rather than by the
# solver.  eta_th_pct is written to four decimal places, so two identical
# runs can differ by up to 5e-5 percentage points purely from rounding.
# 1e-4 sits just above that floor: tight enough that any real change in
# the model trips it, loose enough that storage precision does not.
#
# Set tighter and this check fails on a correct run, which is worse than
# not having it -- a guard that cries wolf gets deleted.
ETA_TOL_PCT = 1e-4


def selected_row():
    """The knee-point row, as the trade-off study labelled it."""
    rows = load("multi_objective", "candidates")
    knees = [r for r in rows if r["verdict"] == "knee"]
    if len(knees) != 1:
        raise SystemExit(
            f"expected exactly one row with verdict 'knee', found "
            f"{len(knees)}. Re-run: python -m project.studies.tradeoff")
    return knees[0]


def rebuild(row):
    """Reconstruct the selected case from its recorded parameters."""
    if not row["name"].startswith("recompression"):
        raise SystemExit(
            f"the selected design is {row['name']!r}, which this study "
            f"does not know how to rebuild. Only recompression designs "
            f"have a factory; add one for the new layout.")
    return recompression_design(row["P_high_mpa"], row["split"],
                                row["T_inlet_degc"], row["P_inlet_mpa"])


def main() -> int:
    row = selected_row()
    print(f"selected design: {row['name']}")
    print(f"  from results/multi_objective/candidates.csv "
          f"(verdict 'knee')\n")

    r = solve(rebuild(row))
    if not r.ok:
        print("the rebuilt case did not solve:")
        for f in r.flags:
            print("   ", f)
        return 1

    eta = r.metrics["eta_th"] * 100
    drift = abs(eta - row["eta_th_pct"])
    print(f"  recorded eta  {row['eta_th_pct']:.4f} %")
    print(f"  rebuilt  eta  {eta:.4f} %   (drift {drift:.2e})")
    if drift > ETA_TOL_PCT:
        print("\nMISMATCH: the rebuilt case does not reproduce the recorded")
        print("efficiency. The sweep and this study are no longer running")
        print("the same code or the same inputs. Re-run tradeoff first.")
        return 1
    print("  reproduced\n")

    # --- the state table, which is what the T-s diagram is drawn from ---
    states = []
    for sid in sorted(r.streams, key=lambda s: (len(s), s)):
        st = r.streams[sid]
        states.append({
            "stream": sid,
            "P_mpa": round(to_MPa(st["P"]), 5),
            "T_degc": round(to_degC(st["T"]), 4),
            "h_kj_kg": round(st["h"] / 1e3, 4),
            "s_kj_kgk": round(st["s"] / 1e3, 6),
            "flow_kg_s": round(st["flow"], 5),
        })

    # The loop in visiting order, which no sort gives you, plus the branch
    # that skips the precooler. Drawing a cycle needs the order; labelling
    # it needs the names; so both are saved.
    LOOP = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s1"]
    BRANCH = ["s9", "s10", "s4"]
    seen = set()

    def path(ids):
        out = []
        for sid in ids:
            st = r.streams[sid]
            out.append({
                "label": "" if sid in seen else sid.lstrip("s"),
                "s_kj_kgk": round(st["s"] / 1e3, 6),
                "T_degc": round(to_degC(st["T"]), 4),
            })
            seen.add(sid)
        return out

    loop, branch = path(LOOP), path(BRANCH)

    mdot = r.metrics["mdot"]
    perf = [{
        "quantity": k, "value": v, "unit": u
    } for k, v, u in [
        ("eta_th", round(eta, 4), "%"),
        ("eta_second_law", row["eta_second_law"], "-"),
        # Specific quantities in J/kg; multiply by mass flow for plant
        # totals. The metrics dict is per-kilogram throughout.
        ("W_net", round(r.metrics["w_net"] * mdot / 1e6, 4), "MW"),
        ("Q_in", round(r.metrics["q_in"] * mdot / 1e6, 4), "MW"),
        ("Q_out", round(r.metrics["q_out"] * mdot / 1e6, 4), "MW"),
        ("mass_flow", round(mdot, 3), "kg/s"),
        ("mass_total", row["mass_t"], "t"),
        ("volume", row["volume_m3"], "m3"),
        ("specific_power", row["mwe_per_t"], "MWe/t"),
        ("T_margin", row["T_margin_k"], "K"),
        ("P_margin", row["P_margin_mpa"], "MPa"),
        ("recuperator_pinch", row["pinch_k"], "K"),
    ]]

    save(
        "selected_design",
        {"state_points": states, "performance": perf,
         "ts_loop": loop, "ts_branch": branch},
        purpose="Solve the knee-point design identified by the trade-off "
                "study and save its state table, so the T-s diagram and "
                "the recommendation cannot describe different cycles.",
        script="project/studies/selected_design.py",
        command="python -m project.studies.selected_design",
        inputs={"name": row["name"], "P_high_mpa": row["P_high_mpa"],
                "split": row["split"], "T_inlet_degc": row["T_inlet_degc"],
                "P_inlet_mpa": row["P_inlet_mpa"],
                "source": "results/multi_objective/candidates.csv"},
        notes=[f"Rebuilt efficiency reproduced the recorded value to "
               f"{drift:.2e} percentage points.",
               "ts_loop is the main circuit in visiting order; ts_branch "
               "is the recompression branch. Repeated states carry a "
               "blank label so no number is drawn twice."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
