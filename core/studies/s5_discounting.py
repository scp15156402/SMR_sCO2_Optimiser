"""S5: discounted payout (NPV) instead of the undiscounted lifetime payout.

    python -m core.studies.s5_discounting

NPV = annual electricity value x sum_{t=1..N} 1/(1+r)^t - hardware cost, for
r = 0, 3, 5, 8, 10 % and N = 10, 20. Baseline results, no re-solve. Also the
incremental payback (simple and discounted) of each named design against the
reference (extra hardware cost / extra annual value).
"""
import math

from core.economics import rank, strict_ok
from core.studies.common import (NAMED, STUDIES, baseline, design_text, econ, pareto_png, table,
                                 winners, write_summary)

NAME = "s5_discounting"
FOLDER = STUDIES / NAME
RATES = (0.0, 0.03, 0.05, 0.08, 0.10)
YEARS = (10, 20)


def annuity(r, n):
    return n if r == 0 else (1 - (1 + r) ** -n) / r


def payback(d_cost, d_value, r):
    """Years for the extra annual value to repay the extra cost (inf if never)."""
    if d_cost <= 0:
        return 0.0
    if d_value <= 0:
        return math.inf
    if r == 0:
        return d_cost / d_value
    x = 1 - r * d_cost / d_value
    return math.inf if x <= 0 else -math.log(x) / math.log(1 + r)


def main():
    raw, ref, m0 = baseline()
    base, _ = econ(raw, m0, ref["ID"])
    rk_rows = []
    for n in YEARS:
        for r in RATES:
            rows = [dict(x) for x in base]
            a = annuity(r, n)
            for x in rows:
                x["payout_usd"] = x["electricity_usd_per_yr"] * a - x["hardware_usd"]
            rank(rows)
            strict = rank([dict(x) for x in rows if strict_ok(x["ID"])])
            for which, rs in (("main", rows), ("strict", strict)):
                w = winners(rs)
                rk_rows.append([n, f"{r * 100:g}", which,
                                f"{w['knee']['ID']} ({design_text(w['knee']['ID'])})",
                                f"{w['topsis']['ID']} ({design_text(w['topsis']['ID'])})",
                                f"{w['topsis']['payout_usd'] / 1e6:.2f}", w["front"]])
            if (n, r) in ((10, 0.08), (20, 0.08)):
                pareto_png(rows, FOLDER, f"pareto_N{n}_r{r * 100:g}.png", f"NPV, N = {n}, r = {r * 100:g} % (M$)")
                pareto_png(strict, FOLDER, f"pareto_N{n}_r{r * 100:g}_strict.png", f"NPV, N = {n}, r = {r * 100:g} % (M$)")

    by = {x["ID"]: x for x in base}
    ref_row = by[ref["ID"]]
    pb = []
    for nm, id_ in NAMED.items():
        if id_ == ref["ID"]:
            continue
        x = by[id_]
        dc = x["hardware_usd"] - ref_row["hardware_usd"]
        dv = x["electricity_usd_per_yr"] - ref_row["electricity_usd_per_yr"]
        cells = [nm, id_, f"{dc / 1e6:.3f}", f"{dv / 1e6:.3f}"]
        for r in RATES:
            p = payback(dc, dv, r)
            cells.append("never" if math.isinf(p) else f"{p:.2f}")
        pb.append(cells)

    md = ["# S5: discounting", "",
          "Payout replaced by NPV = annual electricity value x sum_{t=1..N} (1+r)^-t - hardware "
          "cost (hardware paid at t = 0, value at the end of each year). Baseline results, "
          "no re-solve; mass unchanged. r = 0 reproduces the undiscounted payout.", "",
          "## Knee and TOPSIS #1", "",
          table(["N", "r %", "ranking", "knee", "TOPSIS #1", "TOPSIS #1 NPV M$", "front size"], rk_rows), "",
          f"## Incremental payback against the reference ({ref['ID']})", "",
          "Extra hardware cost and extra annual electricity value against the reference; payback "
          "in years, simple (r = 0) and discounted.", "",
          table(["design", "ID", "extra cost M$", "extra value M$/yr"]
                + [f"payback r={r * 100:g}% (yr)" for r in RATES], pb), "",
          "Plots: pareto_N10_r8(_strict).png, pareto_N20_r8(_strict).png (y axis is the NPV).", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
