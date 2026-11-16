"""R4: what each layout's heat sink costs.

Thermal efficiency says nothing about the cooling system, and the four
layouts differ in it more than they differ in anything else visible.  One
has a single precooler on full flow; recompression has one on reduced flow;
the intercooled and partial cooling layouts reject heat twice, at different
pressures and different flows.

This run puts every cooler of every layout side by side, with its water
demand, its approach and its conductance -- and, where a circuit pressure
drop has been stated, what pumping it costs.

    python -m project.studies.cooling
"""
from __future__ import annotations

import sys

from ._io import save
from cycles import CoolantFlow, CoolantRise, Pinch, solve
from cycles.units import K
from project.cases import (baseline_watercooled, intercooled_watercooled,
                           partial_cooling_watercooled,
                           recompression_watercooled)
from project.cases.pdf_baseline import pdf_baseline
from project.cases.pdf_watercooled import CIRCUIT, FLOW_REF_10K, WATER

PINCH = Pinch(K(5))

LAYOUTS = [
    ("recuperated",     baseline_watercooled,        {"RECUP": PINCH}),
    ("recompression",   recompression_watercooled,   {"LTR": PINCH, "HTR": PINCH}),
    ("partial cooling", partial_cooling_watercooled, {"LTR": PINCH, "HTR": PINCH}),
    ("intercooled",     intercooled_watercooled,     {}),
]


def coolers(r):
    return {b: e for b, e in r.blocks.items()
            if e["kind"] == "cooler" and "coolant_flow" in e}


per_cooler = []


def per_layout():
    print("every cooler, 10 K water rise from 25 degC, 5 K recuperator pinch\n")
    print(f"  {'layout':<16}{'cooler':<8}{'duty':>9}{'water':>9}{'pinch':>8}"
          f"{'UA':>9}{'pump':>8}")
    print(f"  {'':<16}{'':<8}{'[MW]':>9}{'[kg/s]':>9}{'[K]':>8}"
          f"{'[kW/K]':>9}{'[kW]':>8}")
    rows = []
    for name, case, specs in LAYOUTS:
        c = case.with_(params={k: dict(spec=v) for k, v in specs.items()}) \
            if specs else case
        r = solve(c)
        if not r.ok:
            print(f"  {name:<16} FLAGGED {r.flags}")
            continue
        m, cs = r.metrics, coolers(r)
        tot_w = tot_ua = 0.0
        for i, (bid, e) in enumerate(sorted(cs.items())):
            w = e["coolant_flow"] * m["mdot"]
            ua = e["coolant_UA_per_flow"] * m["mdot"] / 1e3
            tot_w += w
            tot_ua += ua
            print(f"  {name if i == 0 else '':<16}{bid:<8}"
                  f"{e['q_total']*m['mdot']/1e6:9.1f}{w:9.0f}"
                  f"{e['coolant_pinch']:8.2f}{ua:9.0f}"
                  f"{e.get('pump_w_total', 0.0)*m['mdot']/1e3:8.0f}")
        if len(cs) > 1:
            print(f"  {'':<16}{'total':<8}{'':>9}{tot_w:9.0f}{'':>8}"
                  f"{tot_ua:9.0f}")
        rows.append((name, m["eta_th"] * 100, m["UA_total"] / 1e3, tot_ua))
        for bid, e in sorted(cs.items()):
            per_cooler.append({
                "layout": name,
                "cooler": bid,
                "duty_mw": round(e["q_total"] * m["mdot"] / 1e6, 4),
                "water_kg_s": round(e["coolant_flow"] * m["mdot"], 3),
                "coolant_pinch_k": round(e["coolant_pinch"], 4),
                "coolant_ua_kw_k": round(
                    e["coolant_UA_per_flow"] * m["mdot"] / 1e3, 2),
                # A cooler with no pump circuit configured has no pump
                # work -- which is not the same claim as zero pump work,
                # and must not be written as a number.
                "pump_kw": (round(e["pump_w_total"] * m["mdot"] / 1e3, 3)
                            if "pump_w_total" in e else ""),
            })
    return rows


def totals(rows):
    """The number the recuperator-only comparison gets wrong."""
    print("\n\ntotal exchanger conductance, recuperators AND coolers\n")
    print(f"  {'layout':<17}{'eta_th':>8}{'recup':>9}{'coolers':>9}"
          f"{'total':>9}{'vs base':>9}{'pts/x':>8}")
    print(f"  {'':<17}{'[%]':>8}{'[kW/K]':>9}{'[kW/K]':>9}"
          f"{'[kW/K]':>9}{'ratio':>9}{'':>8}")
    e0 = rows[0][1]
    t0 = rows[0][2] + rows[0][3]
    for name, eta, rec, cool in rows:
        tot = rec + cool
        ratio = tot / t0
        gain = eta - e0
        pr = f"{gain/(ratio-1):8.2f}" if ratio > 1.001 else f"{'--':>8}"
        print(f"  {name:<17}{eta:8.3f}{rec:9.0f}{cool:9.0f}"
              f"{tot:9.0f}{ratio:9.2f}{pr}")
    print("\n  Compare those ratios with the recuperator-only ones in")
    print("  compare_layouts: recompression looks like 2.51x the hardware")
    print("  there and 1.42x here. The difference is the precooler, which")
    print("  is the largest exchanger in the plant and which recompression")
    print("  makes SMALLER -- it rejects less heat per MW and does it from")
    print("  reduced flow. Judging compactness on recuperators alone")
    print("  overstates what the flow-splitting layouts cost by a lot.")
    return 0


water_rows = []


def water_sweep():
    """How much the baseline precooler shrinks as water is added."""
    print("\n\nbaseline precooler, water flow swept directly\n")
    print(f"  {'water':>8}{'T_out':>8}{'pinch':>8}{'at x':>7}{'UA':>9}"
          f"{'pump':>8}{'eta_net':>9}")
    print(f"  {'kg/s':>8}{'degC':>8}{'K':>8}{'':>7}{'kW/K':>9}"
          f"{'kW':>8}{'%':>9}")
    for f_w in (2.5, 3.5, 4.714, 6.5, 8.0, 10.0, 13.0):
        c = pdf_baseline.with_(
            name=f"pc_{f_w:.2f}",
            params={"COOLER": dict(WATER, **CIRCUIT,
                                   coolant=CoolantFlow(f_w))})
        r = solve(c)
        if not r.ok:
            print(f"  {f_w:8.2f}  FLAGGED {r.flags}")
            continue
        m = r.metrics
        e = next(iter(coolers(r).values()))
        print(f"  {e['coolant_flow']*m['mdot']:8.0f}"
              f"{e['coolant_T_out']-273.15:8.1f}{e['coolant_pinch']:8.2f}"
              f"{e['coolant_pinch_at']:7.2f}"
              f"{e['coolant_UA_per_flow']*m['mdot']/1e3:9.0f}"
              f"{m['W_pump']/1e3:8.0f}{m['eta_net_of_pump']*100:9.3f}")
        water_rows.append({
            "water_kg_s": round(e["coolant_flow"] * m["mdot"], 2),
            "water_T_out_degc": round(e["coolant_T_out"] - 273.15, 3),
            "coolant_pinch_k": round(e["coolant_pinch"], 4),
            "pinch_at_x": round(e["coolant_pinch_at"], 4),
            "coolant_ua_kw_k": round(
                e["coolant_UA_per_flow"] * m["mdot"] / 1e3, 2),
            "pump_kw": round(m["W_pump"] / 1e3, 3),
            "eta_th_pct": round(m["eta_th"] * 100, 4),
            "eta_net_of_pump_pct": round(m["eta_net_of_pump"] * 100, 4),
        })
    print("\n  The pinch leaves the interior and sticks at 7.00 K once the")
    print("  water is plentiful: that is the 32 degC CO2 outlet minus the")
    print("  25 degC water inlet, and no flow can open it further.")
    print("\n  eta_th is 32.720 % in every row. Only eta_net_of_pump moves,")
    print("  and it moves the wrong way, because pump work is a cost with")
    print("  no efficiency benefit to trade against. The exchanger is what")
    print("  pushes back, and it is hardware, invisible to efficiency.")
    return 0


def main() -> int:
    rows = per_layout()
    totals(rows)
    water_sweep()
    save(
        "cooling",
        {"per_cooler": per_cooler, "water_sweep": water_rows},
        purpose="Size every cooler in every layout against 25 degC water, "
                "and sweep the baseline precooler's water flow.",
        script="project/studies/cooling.py",
        command="python -m project.studies.cooling",
        inputs={"water_inlet_degc": 25.0, "water_rise_k": 10.0,
                "recuperator_pinch_k": 5.0},
        notes=["The precooler pinch sticks at 7.00 K once water is "
               "plentiful: that is the 32 degC CO2 outlet minus the "
               "25 degC water inlet, and no flow can open it further.",
               "eta_th does not move across the water sweep; only "
               "eta_net_of_pump does, and it falls, because pump work is "
               "a cost with no efficiency benefit to trade against.",
               "Pressure drops are stated, never derived: this project "
               "computes UA and not geometry."],
    )
    print("\n  Pressure drops are stated, never derived: this project")
    print("  computes UA and not geometry, so a geometry-based drop would")
    print("  describe an exchanger unrelated to the one being sized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
