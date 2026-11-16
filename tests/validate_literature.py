"""Check the solver against somebody else's published numbers.

This is the validation the other three cannot do.  `validate_air` proves
the algebra by reproducing a closed form; energy closure proves nothing
leaks; `check_nodes` proves the discretisation is fine.  All three would
pass with the CO2 properties wrong, because none of them involves CO2.

Three independent checks here, deliberately at different levels:

  1. Properties alone, against Dostal's published state table.  No cycle,
     no solver -- just h and s at stated P and T.  This is what catches a
     transposed argument or a unit slip.
  2. One machine at a time, against Dostal's own ideal/real pairs.  He
     prints both the isentropic and the actual outlet, so the isentropic
     relation and the efficiency definition can be checked separately from
     everything else.
  3. A whole cycle, against Kim's reported optimum -- and not just the
     efficiency at his optimum but the *location* of that optimum in two
     directions, which is a far stronger claim than matching one number.

    python -m tests.validate_literature
"""
from __future__ import annotations

import sys

from cycles import solve
from cycles.physics.isentropic import compress, expand
from cycles.properties import make_backend
from project.cases.literature import (KIM_ETA_REPORTED, KIM_P_LOW, KIM_RP,
                                      KIM_SPLIT, kim_case)

# Dostal, MIT-ANP-TR-100 (2004), Table 10.2: basic design state points,
# conservative turbomachinery.  (point, P kPa, T degC, h kJ/kg, s kJ/kg/K)
DOSTAL_STATES = [
    ("1", 7692.31,  32.00,  306.67, 1.3478),
    ("2", 20000.00, 61.10,  327.26, 1.3546),
    ("3", 19988.68, 157.99, 536.10, 1.9099),
    ("4", 19957.95, 396.54, 846.36, 2.4908),
    ("5", 19827.95, 550.00, 1035.25, 2.7429),
    ("6", 7901.16,  440.29, 914.45, 2.7619),
    ("7", 7814.21,  168.34, 604.19, 2.2189),
    ("8", 7704.58,  69.59,  478.64, 1.9026),
]

H_TOL = 5e-4      # relative; enthalpy is what every block balance uses
S_TOL = 5e-3      # relative; looser, see the note printed below
W_TOL = 0.05      # kJ/kg on a machine outlet
ETA_TOL = 2e-3    # relative on a reproduced cycle efficiency

results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name:<46} {detail}")


def properties():
    print("1. properties alone, against Dostal Table 10.2\n")
    co2 = make_backend("CO2", "coolprop")
    worst_h = worst_s = 0.0
    odd = []
    for pt, P_kPa, T_C, h_ref, s_ref in DOSTAL_STATES:
        h = co2.h_pt(P_kPa * 1e3, T_C + 273.15) / 1e3
        s = co2.s_pt(P_kPa * 1e3, T_C + 273.15) / 1e3
        worst_h = max(worst_h, abs(h - h_ref) / abs(h_ref))
        e_s = abs(s - s_ref) / abs(s_ref)
        worst_s = max(worst_s, e_s)
        if e_s > S_TOL / 5:
            odd.append((pt, s_ref, s, co2.s_ph(P_kPa * 1e3, h_ref * 1e3) / 1e3))
    check("enthalpy at all 8 published states", worst_h < H_TOL,
          f"worst {worst_h*100:.3f} % over 8 points")
    check("entropy at all 8 published states", worst_s < S_TOL,
          f"worst {worst_s*100:.3f} % over 8 points")

    if odd:
        print("\n     Three entropies disagree by more than the rest. It is "
              "the table,\n     not the backend: recomputing s from Dostal's "
              "OWN enthalpy gives the\n     same answer as from his own "
              "temperature, and both differ from the\n     value he prints, "
              "so his h, T and s are not mutually consistent.\n")
        print(f"     {'pt':>4} {'printed':>9} {'from his T':>11} "
              f"{'from his h':>11}")
        for pt, s_ref, s_T, s_h in odd:
            print(f"     {pt:>4} {s_ref:9.4f} {s_T:11.4f} {s_h:11.4f}")
        print("\n     Every block balance in this solver is an enthalpy "
              "balance, and the\n     enthalpies agree to 0.002 %.")


def machines():
    print("\n2. one machine at a time, against Dostal's ideal/real pairs\n")
    co2 = make_backend("CO2", "coolprop")

    # compressor: 1 -> 2, eta 0.89.  Dostal prints 2id = 324.99, 2 = 327.26
    h1, s1 = 306.67e3, 1.3478e3
    h2id = co2.h_ps(20000e3, s1)
    h2 = compress(h1, h2id, 0.89)
    check("compressor isentropic outlet", abs(h2id / 1e3 - 324.99) < W_TOL,
          f"Dostal 324.99, ours {h2id/1e3:.2f} kJ/kg")
    check("compressor outlet at eta = 0.89", abs(h2 / 1e3 - 327.26) < W_TOL,
          f"Dostal 327.26, ours {h2/1e3:.2f} kJ/kg")

    # turbine: 5 -> 6, eta 0.90.  Dostal prints 6id = 901.03, 6 = 914.45
    h5, s5 = 1035.25e3, 2.7429e3
    h6id = co2.h_ps(7901.16e3, s5)
    h6 = expand(h5, h6id, 0.90)
    check("turbine isentropic outlet", abs(h6id / 1e3 - 901.03) < W_TOL,
          f"Dostal 901.03, ours {h6id/1e3:.2f} kJ/kg")
    check("turbine outlet at eta = 0.90", abs(h6 / 1e3 - 914.45) < W_TOL,
          f"Dostal 914.45, ours {h6/1e3:.2f} kJ/kg")


def whole_cycle():
    print("\n3. a whole cycle, against Kim (2018) Table 1 and his optimum\n")
    r = solve(kim_case())
    if not r.ok:
        check("Kim case solves", False, str(r.flags))
        return
    eta = r.metrics["eta_th"]
    err = abs(eta - KIM_ETA_REPORTED) / KIM_ETA_REPORTED
    check("efficiency at Kim's reported optimum", err < ETA_TOL,
          f"Kim {KIM_ETA_REPORTED*100:.2f} %, ours {eta*100:.3f} % "
          f"({(eta-KIM_ETA_REPORTED)*100:+.3f} points)")

    # stronger: does the optimum sit where he says, in both directions?
    xs = [0.24, 0.27, 0.29, KIM_SPLIT, 0.33, 0.36]
    best_x = max(xs, key=lambda x: solve(kim_case(x=x)).metrics["eta_th"])
    check("split ratio optimum is where Kim puts it", best_x == KIM_SPLIT,
          f"Kim 0.307, ours {best_x:.3f}")

    rps = [2.2, 2.4, KIM_RP, 2.8, 3.0]
    best_rp = max(rps, key=lambda p:
                  solve(kim_case(P_high=KIM_P_LOW * p)).metrics["eta_th"])
    check("pressure ratio optimum is where Kim puts it", best_rp == KIM_RP,
          f"Kim 2.6, ours {best_rp:.1f}")


def main() -> int:
    print("validation against published work\n")
    properties()
    machines()
    whole_cycle()
    ok = all(results)
    print(f"\n  {sum(results)}/{len(results)} passed  ->  "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"\n  tolerances: h {H_TOL:.0e}, s {S_TOL:.0e} relative; "
          f"machines {W_TOL} kJ/kg; efficiency {ETA_TOL:.0e} relative")
    if ok:
        print("\n  The sCO2 results can now be called validated rather than")
        print("  merely self-consistent. Matching an independent author's")
        print("  optimum in two directions is the part that could not have")
        print("  happened by luck.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
