"""S4: separate cost per kg for exchangers (c_hx) and the rest (c_tm).

    python -m core.studies.s4_cost_split

hardware = c_hx * m_hx + c_tm * (M0 + added-compressor mass), with m_hx the
recuperator + cooler mass. c_hx is set so the reference design costs what it
does at 250 USD/kg (60 t -> 15 M$) for each ratio k = c_tm / c_hx. Baseline
results only (data/results_raw.csv), no re-solve. Mass, and so the mass axis
of the rankings, is unchanged; only payout moves.
"""
import config
from core.economics import rank, strict_ok
from core.studies.common import (NAMED, STUDIES, baseline, design_text, econ, pareto_png, table,
                                 winners, write_summary)

NAME = "s4_cost_split"
FOLDER = STUDIES / NAME
RATIOS = (0.5, 1.0, 2.0, 4.0, 8.0)


def m_hx(r):
    ua_r = sum(float(r[k] or 0) for k in ("UA_recup_1", "UA_recup_2"))
    ua_c = sum(float(r[k] or 0) for k in ("UA_cooler_1", "UA_cooler_2"))
    return config.KG_PER_KW_K * ua_r / 1000 + config.COOLER_KG_PER_KW_K * ua_c / 1000


def recost(rows, k, ref_row):
    """In place: hardware and payout with c_tm = k * c_hx, reference cost held."""
    ref_cost = config.USD_PER_KG * 1000 * ref_row["mass_t"]
    m_ref_hx = m_hx(ref_row)
    c_hx = ref_cost / (1000 * (m_ref_hx + k * (ref_row["mass_t"] - m_ref_hx)))
    c_tm = k * c_hx
    N = config.LIFETIME_YEARS
    for r in rows:
        hx = m_hx(r)
        r["hardware_usd"] = 1000 * (c_hx * hx + c_tm * (r["mass_t"] - hx))
        r["payout_usd"] = N * r["electricity_usd_per_yr"] - r["hardware_usd"]
    return c_hx, c_tm


def main():
    raw, ref, m0 = baseline()
    out_rows, md_rank, md_top = [], [], []
    for k in RATIOS:
        main_rows, _ = econ(raw, m0, ref["ID"])
        ref_row = next(r for r in main_rows if r["ID"] == ref["ID"])
        c_hx, c_tm = recost(main_rows, k, ref_row)
        rank(main_rows)
        strict_rows = rank([dict(r) for r in main_rows if strict_ok(r["ID"])])
        for which, rows in (("main", main_rows), ("strict", strict_rows)):
            w = winners(rows)
            md_rank.append([f"{k:g}", f"{c_hx:.1f}", f"{c_tm:.1f}", which,
                            f"{w['knee']['ID']} ({design_text(w['knee']['ID'])})",
                            f"{w['topsis']['ID']} ({design_text(w['topsis']['ID'])})", w["front"]])
            top = sorted([r for r in rows if r["topsis_rank"] != ""],
                         key=lambda r: -r["payout_usd"])[:5]
            for i, r in enumerate(top, 1):
                md_top.append([f"{k:g}", which, i, r["ID"], f"{r['mass_t']:.2f}",
                               f"{r['payout_usd'] / 1e6:.3f}"])
        for nm, id_ in NAMED.items():
            r = next(r for r in main_rows if r["ID"] == id_)
            out_rows.append([f"{k:g}", nm, id_, f"{r['hardware_usd'] / 1e6:.3f}",
                             f"{r['payout_usd'] / 1e6:.3f}"])
        if k in (0.5, 8.0):
            pareto_png(main_rows, FOLDER, f"pareto_ratio{k:g}.png", f"10-year payout, c_tm/c_hx = {k:g} (M$)")
            pareto_png(strict_rows, FOLDER, f"pareto_ratio{k:g}_strict.png", f"10-year payout, c_tm/c_hx = {k:g} (M$)")

    md = ["# S4: separate cost per kg (exchangers vs the rest)", "",
          "Hardware cost = c_hx x (recuperator + cooler mass) + c_tm x (M0 + added-compressor "
          "mass). For each ratio c_tm / c_hx, c_hx is chosen so the reference design "
          f"({ref['ID']}, 60 t) costs exactly what it does at 250 USD/kg (15 M$). Baseline "
          "results, N = 10, no re-solve. Mass is unchanged, so only the payout axis moves. "
          "Ratio 1 is the baseline.", "",
          "## Knee and TOPSIS #1", "",
          table(["c_tm/c_hx", "c_hx USD/kg", "c_tm USD/kg", "ranking", "knee", "TOPSIS #1",
                 "front size"], md_rank), "",
          "## Top 5 by payout (ranked layouts)", "",
          table(["c_tm/c_hx", "ranking", "#", "ID", "mass t", "payout M$"], md_top), "",
          "## Named designs", "",
          table(["c_tm/c_hx", "design", "ID", "hardware M$", "payout M$"], out_rows), "",
          "Plots: pareto_ratio0.5(_strict).png and pareto_ratio8(_strict).png (the extremes; "
          "the y axis is the recosted 10-year payout).", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
