"""Compare layouts on a fair basis.

Comparing layouts at the same *effectiveness* is not fair: their exchangers
see different inlet states, so the same effectiveness means different
hardware.  Comparing them at the same *pinch* is fair -- both sides are then
using equally aggressive exchangers -- and the brief fixes that pinch at 5 K.

    python -m project.studies.compare_layouts
"""
from __future__ import annotations

import sys

from cycles import Pinch, solve
from cycles.units import K
from project.cases import (baseline_watercooled, intercooled_watercooled,
                           partial_cooling_watercooled,
                           recompression_watercooled)

from ._io import save

PINCH = Pinch(K(5))


def main() -> int:
    # the water-cooled variants, so the coolers are sized and their
    # conductance and exergy destruction are real rather than missing
    runs = [
        ("recuperated", baseline_watercooled.with_(
            params={"RECUP": dict(spec=PINCH)})),
        ("recompression", recompression_watercooled.with_(
            params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH)})),
        ("partial cooling", partial_cooling_watercooled.with_(
            params={"LTR": dict(spec=PINCH), "HTR": dict(spec=PINCH)})),
        ("intercooled", intercooled_watercooled),
    ]

    print(f"all layouts sized to a 5 K minimum pinch, 100 MWth, "
          f"500 degC turbine inlet\n")
    print(f"  {'layout':<17}{'eta_th':>9}{'W_net':>9}{'BWR':>8}"
          f"{'recup':>9}{'cooler':>9}{'UA tot':>9}{'E_D':>9}")
    print(f"  {'':<17}{'[%]':>9}{'[MWe]':>9}{'':>8}"
          f"{'[kW/K]':>9}{'[kW/K]':>9}{'[kW/K]':>9}{'[MW]':>9}")

    rows = []
    for name, case in runs:
        r = solve(case)
        if not r.ok:
            print(f"  {name:<17} FLAGGED: {r.flags}")
            continue
        m = r.metrics
        cool = sum(e["coolant_UA_per_flow"] for e in r.blocks.values()
                   if e["kind"] == "cooler"
                   and "coolant_UA_per_flow" in e) * m["mdot"] / 1e3
        rows.append((name, m, cool))
        print(f"  {name:<17}{m['eta_th']*100:9.3f}{m['W_net']/1e6:9.3f}"
              f"{m['bwr']:8.4f}{m['UA_total']/1e3:9.0f}{cool:9.0f}"
              f"{m['UA_total']/1e3+cool:9.0f}{m['E_D_known']/1e6:9.2f}")

    if len(rows) >= 2:
        base, base_cool = rows[0][1], rows[0][2]
        print("\n  E_D excludes the heater: no heat-source boundary")
        print("  temperature exists in the model, so the total is")
        print("  incomplete and labelled as such. Every other component,")
        print("  coolers included, is accounted for.")
        print()
        for name, m, cool in rows[1:]:
            d_eta = (m["eta_th"] - base["eta_th"]) * 100
            d_ua = ((m["UA_total"]/1e3 + cool)
                    / (base["UA_total"]/1e3 + base_cool))
            print(f"  {name:<17} {d_eta:+6.2f} efficiency points for "
                  f"{d_ua:.2f}x the TOTAL conductance")
        print("\n  Those ratios are the trade-off the brief asks you to")
        print("  defend, and they count recuperators AND coolers. Counting")
        print("  recuperators alone would say 2.51x for recompression; it")
        print("  makes the precooler smaller, so the honest figure is lower.")
        print("  Run project.studies.cooling for the cooler-by-cooler split.")
        print("\n  Partial cooling also has a free low-pressure level that has")
        print("  not been optimised here -- sweep it before ruling the layout out.")
        print("\n  Intercooling is the one that loses outright: it does cut the")
        print("  back-work ratio, but sCO2 compression is already cheap, so the")
        print("  saving is small, and the heat dumped in the intercooler is heat")
        print("  the recuperator could have recovered and the reactor must now")
        print("  resupply. Worse efficiency AND more exchanger.")

    base, base_cool = rows[0][1], rows[0][2]
    table = []
    for name, m, cool in rows:
        ua_tot = m["UA_total"] / 1e3 + cool
        table.append({
            "layout": name,
            "eta_th_pct": round(m["eta_th"] * 100, 4),
            # w_net is SPECIFIC work in J/kg, not plant output. Multiply
            # by the mass flow or you report 0.1 MW for a 36 MW plant --
            # which this line did until the generated table was compared
            # against the hand-typed one.
            "W_net_mwe": round(m["w_net"] * m["mdot"] / 1e6, 4),
            "back_work_ratio": round(m["bwr"], 5),
            "mdot_kg_s": round(m["mdot"], 4),
            "recuperator_ua_kw_k": round(m["UA_total"] / 1e3, 2),
            "cooler_ua_kw_k": round(cool, 2),
            "total_ua_kw_k": round(ua_tot, 2),
            "exergy_destroyed_mw": round(m["E_D_known"] / 1e6, 4),
            "delta_eta_points": round((m["eta_th"] - base["eta_th"]) * 100, 4),
            "ua_ratio_vs_recuperated": round(
                ua_tot / (base["UA_total"] / 1e3 + base_cool), 4),
        })

    save(
        "layout_comparison",
        {"layouts": table},
        purpose="R1/R2: the four Brayton configurations at a common 5 K "
                "recuperator pinch, 100 MWth and 500 degC turbine inlet.",
        script="project/studies/compare_layouts.py",
        command="python -m project.studies.compare_layouts",
        inputs={"recuperator_pinch_k": 5.0, "thermal_power_mw": 100.0,
                "turbine_inlet_degc": 500.0, "cooling": "water-cooled"},
        notes=["ua_ratio_vs_recuperated counts recuperators AND coolers. "
               "Counting recuperators alone gives 2.51x for recompression; "
               "it makes the precooler smaller, so the honest figure is "
               "lower.",
               "exergy_destroyed_mw excludes the heater: the model has no "
               "heat-source boundary temperature, so the total is "
               "incomplete and labelled as such.",
               "Partial cooling's low-pressure level is fixed at 6 MPa and "
               "has not been optimised; its efficiency here is provisional."],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
