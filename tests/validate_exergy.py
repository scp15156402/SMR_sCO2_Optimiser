"""Checks on the exergy layer, in the spirit of validate_air.

Exergy destruction is easy to get subtly wrong -- a sign convention, a flow
fraction left unscaled, a reference state that drifts -- and wrong in a way
that still looks plausible, because the numbers come out positive and
roughly the right size. So each check below is chosen to fail loudly for a
specific mistake rather than to confirm the code runs.

    python -m tests.validate_exergy
"""
from __future__ import annotations

import sys

from cycles import Case, CoolantRise, Effectiveness, Pinch, ThermalPower, solve
from cycles.physics import exergy as X
from cycles.properties import make_props
from cycles.units import K, MPa, MW, degC
from project.cases import pdf_baseline, recompression_watercooled
from brayton_cycle import recuperated

TOL = {
    "zero": 1e-9,        # exact-by-construction quantities, relative to scale
    "ideal": 1e-6,       # reversible machines, relative to their own work
    "closure": 1e-6,     # balance residuals, relative to exergy supplied
    "scaling": 1e-12,    # linearity in mdot, relative
}

results = []


def check(name, passed, detail=""):
    results.append((name, passed, detail))
    print(f"  {'PASS' if passed else 'FAIL'}  {name:<46} {detail}")
    return passed


def machine_case(eta_c, eta_t):
    return pdf_baseline.with_(
        name=f"m_{eta_c}_{eta_t}",
        params={"COMP": dict(eta=eta_c), "TURB": dict(eta=eta_t)})


def main() -> int:
    props = make_props([pdf_baseline.fluid, "Water"], pdf_baseline.backend)
    env = pdf_baseline.environment
    co2 = props("CO2")

    print("reference environment and stream exergy\n")

    # 1. the dead state has zero exergy, by definition
    e0 = X.specific(co2, env, env.P0, co2.h_pt(env.P0, env.T0))
    check("exergy at the reference state is zero", abs(e0) < 1e-6,
          f"{e0:.3e} J/kg")

    # 2. an independently evaluated state
    P, T = MPa(20), degC(500)
    h = co2.h_pt(P, T)
    s = co2.s_pt(P, T)
    h0, s0 = co2.h_pt(env.P0, env.T0), co2.s_pt(env.P0, env.T0)
    hand = (h - h0) - env.T0 * (s - s0)
    check("stream exergy matches a hand calculation",
          abs(X.specific(co2, env, P, h) - hand) < 1e-6,
          f"{hand/1e3:.2f} kJ/kg at 20 MPa, 500 degC")

    # 3/5. reversible machines destroy nothing
    r = solve(machine_case(1.0, 1.0))
    ex = r.exergy["components"]
    wc = abs(r.blocks["COMP"]["w_total"] * r.metrics["mdot"])
    wt = abs(r.blocks["TURB"]["w_total"] * r.metrics["mdot"])
    check("ideal compressor destroys nothing",
          abs(ex["COMP"]["E_D"]) < TOL["ideal"] * wc,
          f"{ex['COMP']['E_D']:.3e} W against {wc/1e6:.1f} MW of work")
    check("ideal turbine destroys nothing",
          abs(ex["TURB"]["E_D"]) < TOL["ideal"] * wt,
          f"{ex['TURB']['E_D']:.3e} W against {wt/1e6:.1f} MW of work")

    # 4/6. real machines destroy something, and never less than nothing
    r = solve(machine_case(0.89, 0.90))
    ex = r.exergy["components"]
    check("real compressor destroys a positive amount",
          ex["COMP"]["E_D"] > 0, f"{ex['COMP']['E_D']/1e6:.3f} MW")
    check("real turbine destroys a positive amount",
          ex["TURB"]["E_D"] > 0, f"{ex['TURB']['E_D']/1e6:.3f} MW")

    print("\nmulti-stream components\n")

    # 7/8/9. exchanger, splitter, mixer
    rc = solve(recompression_watercooled.with_(
        params={"LTR": dict(spec=Pinch(K(5))), "HTR": dict(spec=Pinch(K(5)))}))
    ex = rc.exergy["components"]
    check("recuperators destroy a positive amount",
          ex["LTR"]["E_D"] > 0 and ex["HTR"]["E_D"] > 0,
          f"LTR {ex['LTR']['E_D']/1e6:.3f}, HTR {ex['HTR']['E_D']/1e6:.3f} MW")
    biggest = max(c["E_D"] for c in ex.values() if c["E_D"] is not None)
    check("ideal splitter destroys nothing",
          abs(ex["SPLIT"]["E_D"]) < TOL["zero"] * biggest,
          f"{ex['SPLIT']['E_D']:.3e} W")
    check("mixer destroys a positive amount",
          ex["MIX"]["E_D"] > 0,
          f"{ex['MIX']['E_D']/1e6:.3f} MW from mixing unequal states")

    print("\nscaling, closure and completeness\n")

    # 10. linearity in plant size
    half = recompression_watercooled.with_(
        name="half", size=ThermalPower(MW(50)),
        params={"LTR": dict(spec=Pinch(K(5))), "HTR": dict(spec=Pinch(K(5)))})
    rh = solve(half)
    ratio = rh.metrics["E_D_known"] / rc.metrics["E_D_known"]
    check("destruction scales linearly with plant size",
          abs(ratio - 0.5) < TOL["scaling"],
          f"half-size plant gives {ratio:.12f} of the destruction")

    # entropy of the working fluid must return to where it started
    check("working-fluid entropy closes around the loop",
          abs(rc.checks["loop_entropy_residual"]) < 1e-9,
          f"residual {rc.checks['loop_entropy_residual']:.2e}")

    # 11. the overall balance, over a boundary that is actually defined
    res = rc.exergy["balance_residual"]
    check("overall exergy balance closes",
          res is not None and abs(res) < TOL["closure"],
          f"residual {res:.2e} of exergy supplied" if res is not None
          else rc.exergy["balance_reason"])

    # incompleteness is reported, not hidden
    bare = solve(pdf_baseline)
    check("missing boundary data is reported, not guessed",
          bare.metrics["E_D_total"] is None
          and set(bare.exergy["incomplete"]) == {"HEATER", "COOLER"},
          f"incomplete: {bare.exergy['incomplete']}")
    check("a modelled coolant makes the cooler computable",
          rc.exergy["incomplete"] == ["HEATER"],
          f"incomplete: {rc.exergy['incomplete']}")

    print("\nregression: the first-law results must not have moved\n")

    # 12. nothing above may have changed an existing number
    for name, case, eta, ua in (
        ("recuperated", pdf_baseline.with_(params={"RECUP": dict(spec=Pinch(K(5)))}),
         36.541, 3967),
        ("recompression", rc.case, 42.248, 9936),
    ):
        r = solve(case)
        de = abs(r.metrics["eta_th"] * 100 - eta)
        du = abs(r.metrics["UA_total"] / 1e3 - ua)
        check(f"{name} eta and UA unchanged", de < 5e-4 and du < 1.0,
              f"eta {r.metrics['eta_th']*100:.3f} %, UA {r.metrics['UA_total']/1e3:.0f} kW/K")

    bad = [n for n, ok, _ in results if not ok]
    print(f"\n  {len(results) - len(bad)}/{len(results)} passed", end="")
    print("  ->  PASS" if not bad else f"  ->  FAIL: {bad}")
    print(f"\n  tolerances: {TOL}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
