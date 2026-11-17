"""S3: pressure drops of 1 % and 2 % on every exchanger side, full re-solve.

    python -m core.studies.s3_pressure_drop

dp is a fraction of the inlet pressure on both recuperator sides, every cooler
(CO2 side) and the heater. ID pressures remain the compressor inlet and outlet
pressures; the recompressor discharges at the LTR cold-outlet pressure and the
layout 6 pre-compressor at P_mid / (1 - dp) (helpers/builders.py). M0 is held
at the baseline value and the reference stays L2_Ph200_Pl077_T340_Tt500 (its
own dp re-solve) at every level. Resumable: cached solves are reused.
"""
import statistics

from core.studies.common import (DATA, NAMED, STUDIES, baseline, econ, pareto_png,
                                 read_csv, sweep, table, task, winners, write_summary)
from core.studies.s5_discounting import payback
from core.studies.s1_cooler_pinch import changes, describe, write_econ
from helpers.ids import parse_id

NAME = "s3_pressure_drop"
FOLDER = STUDIES / NAME
DPS = (0.01, 0.02)


def main():
    ids = [r["ID"] for r in read_csv(DATA / "inputs.csv")]
    raw0, ref0, m00 = baseline()
    main0, strict0 = econ(raw0, m00, ref0["ID"])
    sets = [dict(label="dp 0 (baseline)", raw=raw0, ref=ref0, m0=m00, main=main0, strict=strict0,
                 n_bad=len(read_csv(DATA / "infeasible.csv")), bad=read_csv(DATA / "infeasible.csv"))]
    for dp in DPS:
        stem = f"dp{dp * 100:g}pct"
        ok, bad = sweep([task(i, i, opts={"PRESSURE_DROP": dp}) for i in ids], FOLDER, stem)
        # M0 held at the baseline value: recalibrating moves every mass (and payout) by one
        # constant, which leaves the front and the min-max knee alone but shifts TOPSIS,
        # whose vector normalisation is not shift-invariant.
        ref, m0 = next(r for r in ok if r["ID"] == ref0["ID"]), m00
        main, strict = econ(ok, m0, ref["ID"])
        write_econ(main, FOLDER / f"econ_{stem}.csv")
        write_econ(strict, FOLDER / f"econ_{stem}_strict.csv")
        pareto_png(main, FOLDER, f"pareto_{stem}.png")
        pareto_png(strict, FOLDER, f"pareto_{stem}_strict.png")
        sets.append(dict(label=f"dp {dp * 100:g} %", raw=ok, ref=ref, m0=m0, main=main,
                         strict=strict, n_bad=len(bad), bad=bad))

    L = lambda r: parse_id(r["ID"])["layout"]
    layouts = sorted({L(r) for r in raw0})
    eff = []
    base_eta = {r["ID"]: float(r["eta"]) for r in raw0}
    for s in sets[1:]:
        for k in layouts:
            rows = [r for r in s["raw"] if L(r) == k]
            if not rows:
                eff.append([s["label"], k, "-", "-", "-", "-", 0])
                continue
            best = max(rows, key=lambda r: float(r["eta"]))
            b0 = max((r for r in raw0 if L(r) == k), key=lambda r: float(r["eta"]))
            loss = [base_eta[r["ID"]] - float(r["eta"]) for r in rows if r["ID"] in base_eta]
            eff.append([s["label"], k, f"{float(b0['eta']):.5f} -> {float(best['eta']):.5f}",
                        f"{(float(b0['eta']) - float(best['eta'])) * 100:.2f}",
                        f"{statistics.median(loss) * 100:.2f}" if loss else "-",
                        best["ID"], len(rows)])
    counts = []
    for s in sets:
        for k in layouts:
            n_ok = sum(L(r) == k for r in s["raw"])
            n_bad = sum(int(b["ID"][1]) == k for b in s["bad"])
            counts.append([s["label"], k, n_ok + n_bad, n_ok, n_bad])

    md = ["# S3: pressure drops (1 % and 2 % per exchanger side)", "",
          "Every design in data/inputs.csv re-solved with a fractional pressure loss dp on both "
          "recuperator sides, every cooler (CO2 side) and the heater. The ID pressures stay the "
          "compressor inlet and outlet pressures, so the turbine sees a smaller expansion ratio; "
          "the recompressor discharges at the LTR cold-outlet pressure and the layout 6 "
          "pre-compressor at P_mid / (1 - dp). Rankings: main and strict, layout 1 unranked.", "",
          f"**M0 is held at the baseline {m00:.3f} t at every dp level, with the baseline reference "
          f"{ref0['ID']} (re-solved at each dp) for payback.** Recalibrating would pick a "
          "different, high-UA layout 2 reference and drop M0 to about 20 t; that changes every "
          "mass (and payout) by the same constant, which leaves the Pareto front and the knee "
          "unchanged but moves TOPSIS, whose vector normalisation is not shift-invariant.", "",
          "## Efficiency loss per layout", "",
          "Best eta per layout (baseline -> with dp), its loss in percentage points, and the "
          "median loss over the designs feasible at that dp (same ID in both).", "",
          table(["case", "layout", "best eta", "best loss pp", "median loss pp", "best design", "feasible"], eff), "",
          "## Feasible counts", "", table(["case", "layout", "attempted", "feasible", "infeasible"], counts), ""]
    md += describe(sets)
    pb = []
    for s in sets:
        rows = {r["ID"]: r for r in s["main"]}
        rr = rows[ref0["ID"]]
        for nm, id_ in NAMED.items():
            if nm == "Reference":
                continue
            x = rows.get(id_)
            if x is None:
                pb.append([s["label"], nm, id_, "infeasible", "", "", "", ""])
                continue
            dc = x["hardware_usd"] - rr["hardware_usd"]
            dv = x["electricity_usd_per_yr"] - rr["electricity_usd_per_yr"]
            pb.append([s["label"], nm, id_, f"{dc / 1e6:.3f}", f"{dv / 1e6:.3f}",
                       f"{x['payout_usd'] / 1e6:.3f}"]
                      + [f"{payback(dc, dv, r):.2f}" for r in (0.0, 0.08)])
    md += [f"## Incremental payback against the reference ({ref0['ID']}, same dp)", "",
           table(["case", "design", "ID", "extra cost M$", "extra value M$/yr", "payout M$",
                  "simple payback yr", "payback r=8% yr"], pb), ""]
    md += ["## Do the rankings change? (against dp 0)", ""]
    for s in sets[1:]:
        md += [f"**{s['label']}**", ""] + changes(sets[0], s) + [""]
    md += ["Plots: " + ", ".join(f"pareto_dp{d * 100:g}pct.png, pareto_dp{d * 100:g}pct_strict.png"
                                 for d in DPS) + ".", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
