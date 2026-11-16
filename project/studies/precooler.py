"""R4: what the heat sink actually costs.

The brief asks for cooling-water duty and precooler size.  Both depend on a
fact that is easy to miss: near the critical point CO2's specific heat peaks,
so most of the precooler's heat is rejected within a few degrees of the
compressor inlet temperature.  The temperature difference against the water
is therefore small over most of the exchanger, and the conductance needed is
large -- often larger than the recuperator's.

    python -m project.studies.precooler
"""
from __future__ import annotations

import sys

from cycles import solve
from cycles.units import K, degC
from project.cases import baseline_watercooled, recompression_watercooled


def line(name, case):
    r = solve(case)
    if not r.ok:
        print(f"  {name:<16} FLAGGED {r.flags}")
        return
    m, e = r.metrics, None
    for bid, ex in r.blocks.items():
        if ex["kind"] == "cooler" and "coolant_flow" in ex:
            e = ex
            break
    rec = sum(x["UA_per_flow"] for x in r.blocks.values()
              if x["kind"] == "heat_exchanger") * m["mdot"]
    print(f"  {name:<16}{m['eta_th']*100:8.2f}{e['q_total']*m['mdot']/1e6:10.2f}"
          f"{e['coolant_flow']*m['mdot']:11.0f}{e['coolant_pinch']:9.2f}"
          f"{e['coolant_pinch_at']:7.2f}"
          f"{e['coolant_UA_per_flow']*m['mdot']/1e3:11.0f}{rec/1e3:11.0f}")


def main() -> int:
    print("precooler sized against 25 degC cooling water, 10 K rise\n")
    print(f"  {'layout':<16}{'eta':>8}{'duty':>10}{'water':>11}{'pinch':>9}"
          f"{'at x':>7}{'PC UA':>11}{'recup UA':>11}")
    print(f"  {'':<16}{'[%]':>8}{'[MW]':>10}{'[kg/s]':>11}{'[K]':>9}"
          f"{'':>7}{'[kW/K]':>11}{'[kW/K]':>11}")
    line("recuperated", baseline_watercooled)
    line("recompression", recompression_watercooled)

    print("\n  The pinch sits inside the exchanger, not at an end: that is the")
    print("  CO2 specific-heat peak near the critical point flattening the hot")
    print("  curve.  It is the same mechanism that pinches the recuperator, and")
    print("  the reason the precooler cannot be sized from end states alone.")

    print("\n  sensitivity to the allowed water temperature rise:")
    print(f"    {'dT [K]':>8}{'water [kg/s]':>15}{'PC UA [kW/K]':>15}{'pinch [K]':>12}")
    for dT in (5, 10, 15, 20):
        r = solve(baseline_watercooled.with_(
            params={"COOLER": dict(coolant_dT=K(dT))}))
        e = r.blocks["COOLER"]; md = r.metrics["mdot"]
        print(f"    {dT:8d}{e['coolant_flow']*md:15.0f}"
              f"{e['coolant_UA_per_flow']*md/1e3:15.0f}{e['coolant_pinch']:12.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
