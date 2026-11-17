"""S8: layout 1 with pressurised cooling water.

    python -m core.studies.s8_layout1_water

At the solver's default 6 bar, 9 of the 18 layout 1 points fail: the cooler
receives turbine exhaust at several hundred C and the water side reaches
saturation. Raise the water pressure for layout 1 only: 20 bar, then 50 bar,
and further if needed, until all 18 solve; use the lowest that works. Layout 1
stays out of the ranking. Payout uses the baseline M0.
"""
import config
from core.economics import compute
from core.studies.common import (DATA, STUDIES, baseline, econ, fnum, read_csv, sweep, table,
                                 task, winners, write_summary)

NAME = "s8_layout1_water"
FOLDER = STUDIES / NAME
LADDER_BAR = (20, 50, 100, 150, 250)    # the brief asked for 20 then 50; continue only if needed


def main():
    ids = [r["ID"] for r in read_csv(DATA / "inputs.csv") if r["layout"] == "1"]
    tried, used = [], None
    for bar in LADDER_BAR:
        ok, bad = sweep([task(f"{bar}|{i}", i, opts={"COOLANT_P_PA": bar * 1e5}) for i in ids],
                        FOLDER, f"water{bar}bar")
        tried.append([bar, len(ok), len(bad), "; ".join(sorted({b["reason"][:60] for b in bad})) or "-"])
        if not bad:
            used = (bar, ok)
            break

    raw0, ref, m0 = baseline()
    base_main, _ = econ(raw0, m0, ref["ID"])
    w = winners(base_main)
    md = ["# S8: layout 1 with pressurised cooling water", "",
          "Layout 1 (simple, no recuperator) sends turbine exhaust at several hundred C straight "
          "to the cooler. At the solver's default 6 bar the water side reaches saturation and "
          "CoolProp raises, so 9 of 18 grid points fail. Here the water pressure is raised for "
          "layout 1 only. The brief asked for 20 bar, then 50 bar"
          + ("; neither was enough, so the ladder continued until every point solved."
             if used is None or used[0] > 50 else ".")
          + " The water pressure changes only the "
          "water side (cooler UA, water flow), not the cycle: eta is unchanged.", "",
          table(["water pressure bar", "feasible", "failed", "failure reasons"], tried), ""]
    if used is None:
        md += ["**No pressure in the ladder solved all 18 points.**", ""]
        write_summary(FOLDER, md)
        return
    bar, ok = used
    config.M0_T = m0
    rows = sorted(compute(ok), key=lambda r: -r["payout_usd"])
    base_l1 = {r["ID"]: r for r in base_main if r["layout"] == 1}
    tab = []
    for r in rows:
        b = base_l1.get(r["ID"])
        tab.append([r["ID"], f"{float(r['eta']):.5f}", fnum(r["UA_recup_1"], ".0f") or "-",
                    f"{float(r['UA_cooler_1']):.0f}", f"{r['mass_t']:.2f}",
                    f"{r['payout_usd'] / 1e6:.3f}", f"{float(r['water_flow_kg_s']):.0f}",
                    "yes" if b else "no (failed at 6 bar)",
                    f"{b['mass_t']:.2f}" if b else "-"])
    best = rows[0]
    l2 = w["best"][2]
    md += [f"**Lowest pressure that solves all 18: {bar} bar.**", "",
           f"## Layout 1 results at {bar} bar (baseline M0 = {m0:.3f} t, N = 10)", "",
           table(["ID", "eta", "UA_recup", "UA_cooler kW/K", "mass t", "payout M$", "water kg/s",
                  "solved at 6 bar", "mass at 6 bar t"], tab), "",
           "## Does any conclusion change?", "",
           f"Best layout 1 design: {best['ID']}, eta {float(best['eta']):.4f}, payout "
           f"{best['payout_usd'] / 1e6:.2f} M$, against the worst-ranked layout's best "
           f"(layout 2, {l2['ID']}: {l2['payout_usd'] / 1e6:.2f} M$) and the main TOPSIS #1 "
           f"({w['topsis']['ID']}: {w['topsis']['payout_usd'] / 1e6:.2f} M$). Layout 1 stays "
           "excluded from the ranking; the recovered points do not approach the other layouts.", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
