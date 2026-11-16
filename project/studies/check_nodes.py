"""Grid-convergence check for the heat-exchanger discretisation.

UA is an integral of dQ/dT, so it depends on how finely the exchanger is cut.
The default of 100 nodes is only defensible if doubling it barely moves the
answer.  Run this whenever the profile or sizing code changes.

    python -m project.studies.check_nodes
"""
from __future__ import annotations

import sys

from cycles import solve
from project.cases import pdf_baseline, pdf_recompression

GATE = 1e-3          # 0.1 % between successive refinements


def sweep(case, hx_ids, label):
    print(f"\n{label}")
    print("   nodes      UA [kW/K]     pinch [K]      change")
    prev, worst = None, 0.0
    for n in (10, 25, 50, 100, 200, 400):
        r = solve(case.with_(params={b: dict(nodes=n) for b in hx_ids}))
        ua = r.metrics["UA_total"] / 1e3
        change = "" if prev is None else f"{abs(ua - prev) / prev:10.2e}"
        if prev is not None:
            worst = max(worst, abs(ua - prev) / prev) if n >= 100 else worst
        print(f"   {n:5d}  {ua:12.3f}  {r.metrics['pinch_min']:11.4f}  {change}")
        prev = ua
    return worst


def main() -> int:
    w1 = sweep(pdf_baseline, ["RECUP"], "recuperated baseline")
    w2 = sweep(pdf_recompression, ["LTR", "HTR"], "recompression")
    worst = max(w1, w2)
    ok = worst < GATE
    print(f"\n  worst change at or beyond 100 nodes: {worst:.2e}  "
          f"->  {'PASS' if ok else 'FAIL'} (gate {GATE:.0e})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
