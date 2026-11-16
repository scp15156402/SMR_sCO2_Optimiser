"""R3/R4: the one-variable sweeps, saved.

Two questions the brief asks directly:

  * how does efficiency vary with maximum pressure (and so with pressure
    ratio, since the compressor inlet is held at 7.7 MPa)?
  * how does it vary with the recompression split fraction?

These were previously computed twice -- once here in spirit, and once
inside the plotting script on a *different* grid (pressure 14-20 against
the trade-off's 16-20; split 0.10-0.45 against 0.20-0.35).  The two
agreed only because both happened to call the same solver on the same
cases; nothing enforced it.  Now the sweep is computed once, saved, and
the figures read the file.

The grids here are deliberately finer than the trade-off's.  That is not
an inconsistency: a sweep exists to show the *shape* of a curve and wants
many points, while the trade-off evaluates full candidate designs and
wants few.  They answer different questions, and both now say so in their
own manifest.

    python -m project.studies.sweeps
"""
from __future__ import annotations

import sys

from cycles import Pinch, solve
from cycles.units import K, MPa, degC
from project.cases import (baseline_watercooled, partial_cooling_watercooled,
                           recompression_watercooled)

from ._io import save

PINCH = Pinch(K(5))

# Maximum pressure, in MPa. The lower end is below anything the trade-off
# considers, on purpose: the point of the curve is to show that efficiency
# is still climbing when it meets the 20 MPa limit, and that is only
# visible with room to the left.
P_HIGH = (14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0)
P_INLET = 7.7

# Split fraction. Wider than the trade-off's grid so the interior optimum
# in recompression and the still-climbing partial cooling curve are both
# resolved.
SPLITS = tuple(i / 100 for i in range(10, 50, 5))


def pressure_sweep():
    """Efficiency against maximum pressure, recuperated and recompression."""
    rows = []
    for P_hi in P_HIGH:
        a = solve(baseline_watercooled.with_(
            params={"RECUP": dict(spec=PINCH),
                    "COMP": dict(P_out=MPa(P_hi))}))
        b = solve(recompression_watercooled.with_(
            params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                    "MC": dict(P_out=MPa(P_hi)),
                    "RC": dict(P_out=MPa(P_hi))}))
        rows.append({
            "P_high_mpa": P_hi,
            "pressure_ratio": round(P_hi / P_INLET, 4),
            "eta_recuperated_pct": round(a.metrics["eta_th"] * 100, 4)
                                   if a.ok else "",
            "eta_recompression_pct": round(b.metrics["eta_th"] * 100, 4)
                                     if b.ok else "",
        })
    return rows


def split_sweep():
    """Efficiency against split fraction, recompression and partial cooling."""
    rows = []
    for x in SPLITS:
        a = solve(recompression_watercooled.with_(
            params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                    "SPLIT": dict(x=x)}))
        b = solve(partial_cooling_watercooled.with_(
            params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH),
                    "SPLIT": dict(x=x)}))
        rows.append({
            "split": round(x, 3),
            "eta_recompression_pct": round(a.metrics["eta_th"] * 100, 4)
                                     if a.ok else "",
            "eta_partial_cooling_pct": round(b.metrics["eta_th"] * 100, 4)
                                       if b.ok else "",
        })
    return rows


def _best(rows, key, xkey):
    vals = [(r[key], r[xkey]) for r in rows if r[key] != ""]
    return max(vals) if vals else (None, None)


def main() -> int:
    print("R3/R4 parameter sweeps\n")

    print("1. maximum pressure, compressor inlet fixed at "
          f"{P_INLET} MPa")
    pres = pressure_sweep()
    print(f"   {'P_high':>8}{'rp':>7}{'recuperated':>14}"
          f"{'recompression':>16}")
    for r in pres:
        print(f"   {r['P_high_mpa']:8.1f}{r['pressure_ratio']:7.2f}"
              f"{r['eta_recuperated_pct']:14.3f}"
              f"{r['eta_recompression_pct']:16.3f}")
    for lbl, k in (("recuperated", "eta_recuperated_pct"),
                   ("recompression", "eta_recompression_pct")):
        e, P = _best(pres, k, "P_high_mpa")
        print(f"   best {lbl:<14} {e:.3f} % at {P:.0f} MPa"
              + ("   <- at the limit, still rising"
                 if P == max(P_HIGH) else ""))

    print("\n2. split fraction, 20 MPa")
    spl = split_sweep()
    print(f"   {'x':>6}{'recompression':>16}{'partial cooling':>18}")
    for r in spl:
        pc = r["eta_partial_cooling_pct"]
        print(f"   {r['split']:6.2f}{r['eta_recompression_pct']:16.3f}"
              + (f"{pc:18.3f}" if pc != "" else f"{'did not solve':>18}"))
    for lbl, k in (("recompression", "eta_recompression_pct"),
                   ("partial cooling", "eta_partial_cooling_pct")):
        e, x = _best(spl, k, "split")
        if e is None:
            continue
        interior = min(SPLITS) < x < max(SPLITS)
        print(f"   best {lbl:<16} {e:.3f} % at x = {x:.2f}"
              + ("   <- interior optimum" if interior
                 else "   <- at the edge of the grid"))

    save(
        "parameter_sweeps",
        {"pressure_sweep": pres, "split_fraction_sweep": spl},
        purpose="R3/R4: efficiency against maximum pressure and against "
                "recompression split fraction.",
        script="project/studies/sweeps.py",
        command="python -m project.studies.sweeps",
        inputs={"P_high_mpa": list(P_HIGH), "P_inlet_mpa": P_INLET,
                "splits": [round(x, 3) for x in SPLITS],
                "recuperator_pinch_k": 5.0},
        notes=["Grids are finer than the trade-off study's on purpose: a "
               "sweep shows the shape of a curve, a trade-off evaluates "
               "candidate designs.",
               "An empty efficiency means that point did not solve; it is "
               "recorded rather than dropped."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
