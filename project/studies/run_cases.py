"""Solve every case and print the state table and the key numbers.

    python -m project.studies.run_cases                # all of them
    python -m project.studies.run_cases pdf_baseline   # just one
"""
from __future__ import annotations

import sys

from cycles import solve
from project.cases import CASES


def report(name: str) -> None:
    result = solve(CASES[name])
    print("=" * 72)
    print(result.summary())
    print()
    print(result.state_table())

    hxs = result.blocks_of("heat_exchanger")
    if hxs:
        print("\n  exchanger   eps      pinch [K]  at x    binds   UA [kW/K]")
        for bid, e in hxs.items():
            ua = e["UA_per_flow"] * result.metrics["mdot"] / 1e3
            print(f"  {bid:<10} {e['effectiveness']:.4f}  {e['pinch']:8.3f}  "
                  f"{e['pinch_at']:5.2f}  {e['binding_limit']:>6}  {ua:9.1f}")

    m = result.metrics
    print(f"\n  heat input per MWe   {1/m['eta_th']:.3f} MWth/MWe")
    print(f"  heat rejected        {m['Q_out']/1e6:.2f} MW "
          f"({m['q_out']/m['w_net']:.2f} per unit net work)")
    print(f"  recuperation ratio   {m['recuperation_ratio']:.2f}  "
          f"(exchanger duty / reactor duty)")
    print(f"  energy closure       {result.checks['energy_closure_rel']:.2e} of q_in")
    print()


def main(argv) -> int:
    names = argv[1:] or list(CASES)
    unknown = [n for n in names if n not in CASES]
    if unknown:
        print(f"unknown case(s) {unknown}; known: {sorted(CASES)}")
        return 1
    for n in names:
        report(n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
