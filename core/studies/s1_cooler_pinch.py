"""S1: cooler pinch 3 K and 8 K (baseline 5 K), full re-solve of data/inputs.csv.

    python -m core.studies.s1_cooler_pinch [--limit N]

Writes out/studies/s1_cooler_pinch/: pinch{3,8}.csv (+ _infeasible), econ_*.csv,
pareto_*.png, summary.md. Resumable.
"""
import argparse
import csv

import config
from core.studies.common import (NAMED, STUDIES, as_strings, baseline, calibrate, design_text,
                                 econ, fnum, pareto_png, read_csv, sweep, table, task, winners,
                                 write_summary, DATA)
from helpers.ids import parse_id

NAME = "s1_cooler_pinch"
FOLDER = STUDIES / NAME
PINCHES = (3.0, 8.0)


def write_econ(rows, path):
    from core.economics import COLUMNS
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in sorted(as_strings(rows), key=lambda r: r["ID"]):
            w.writerow([r[c] for c in COLUMNS])


def describe(sets):
    """Markdown blocks comparing several (label, raw, ref, m0, main, strict) sets."""
    md = []
    md += ["## M0 and reference design", "",
           table(["case", "reference", "eta", "UA_recup kW/K", "UA_cooler kW/K", "M0 t"],
                 [[s["label"], s["ref"]["ID"], fnum(s["ref"]["eta"], ".5f"),
                   fnum(s["ref"]["UA_recup_1"], ".1f"), fnum(s["ref"]["UA_cooler_1"], ".1f"),
                   f"{s['m0']:.3f}"] for s in sets]), ""]
    rows = []
    for nm, id_ in NAMED.items():
        for s in sets:
            r = next((r for r in s["main"] if r["ID"] == id_), None)
            if r is None:
                rows.append([nm, s["label"], "infeasible", "", "", "", "", "", ""])
                continue
            ua_c = sum(float(r[k] or 0) for k in ("UA_cooler_1", "UA_cooler_2"))
            rows.append([nm, s["label"], f"{ua_c:.0f}", f"{config.COOLER_KG_PER_KW_K * ua_c / 1000:.2f}",
                         f"{r['mass_t']:.2f}", f"{float(r['eta']):.5f}",
                         f"{r['payout_usd'] / 1e6:.3f}", fnum(r.get("water_flow_kg_s", ""), ".0f"),
                         fnum(r.get("pinch_cooler_1", ""), ".2f")])
    md += ["## Named designs", "",
           table(["design", "case", "cooler UA kW/K", "cooler mass t", "total mass t", "eta",
                  "payout M$", "water kg/s", "cooler pinch K"], rows), ""]
    for which in ("main", "strict"):
        md += [f"## Best design per layout ({which} ranking set)", ""]
        rows = []
        for s in sets:
            for L, b in winners(s[which])["best"].items():
                rows.append([s["label"], L, b["ID"], f"{float(b['eta']):.5f}", f"{b['mass_t']:.2f}",
                             f"{b['payout_usd'] / 1e6:.3f}"])
        md += [table(["case", "layout", "ID", "eta", "mass t", "payout M$"], rows), ""]
    md += ["## Rankings", ""]
    rows = []
    for which in ("main", "strict"):
        for s in sets:
            w = winners(s[which])
            rows.append([which, s["label"], w["front"],
                         f"{w['knee']['ID']} ({design_text(w['knee']['ID'])})",
                         f"{w['topsis']['ID']} ({design_text(w['topsis']['ID'])})",
                         fnum(w["knee"].get("water_flow_kg_s", ""), ".0f"),
                         fnum(w["topsis"].get("water_flow_kg_s", ""), ".0f")])
    md += [table(["ranking", "case", "front size", "knee", "TOPSIS #1", "knee water kg/s",
                  "TOPSIS water kg/s"], rows), ""]
    return md


def changes(base, s):
    """Sentences: does the winning layout / T_in / split / P_exh change against base?"""
    out = []
    for which in ("main", "strict"):
        for role in ("knee", "topsis"):
            a, b = winners(base[which])[role]["ID"], winners(s[which])[role]["ID"]
            if a == b:
                out.append(f"- {which} {role}: unchanged ({a}).")
                continue
            pa, pb = parse_id(a), parse_id(b)
            diff = [nm for f, nm in (("layout", "layout"), ("T", "T_in"), ("x", "split"),
                                     ("Pe", "P_exh"), ("Pm", "P_mid"), ("Pl", "P_low"))
                    if pa.get(f) != pb.get(f)]
            out.append(f"- {which} {role}: {a} -> {b} (changes: {', '.join(diff)}).")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    args = ap.parse_args(argv)
    ids = [r["ID"] for r in read_csv(DATA / "inputs.csv")][:args.limit]

    raw0, ref0, m00 = baseline()
    main0, strict0 = econ(raw0, m00, ref0["ID"])
    # baseline water flow is not stored in data/: re-solve the designs we report on
    show = set(NAMED.values())
    for rows in (main0, strict0):
        w = winners(rows)
        show |= {w["knee"]["ID"], w["topsis"]["ID"]}
    ok5, _ = sweep([task(i, i) for i in sorted(show)], FOLDER, "pinch5_reported")
    water = {r["ID"]: r["water_flow_kg_s"] for r in ok5}
    for r in main0 + strict0:
        if r["ID"] in water:
            r["water_flow_kg_s"] = water[r["ID"]]
    sets = [dict(label="5 K (baseline)", raw=raw0, ref=ref0, m0=m00, main=main0, strict=strict0,
                 n_bad=len(read_csv(DATA / "infeasible.csv")))]
    for pinch in PINCHES:
        stem = f"pinch{pinch:g}"
        ok, bad = sweep([task(i, i, opts={"COOLER_PINCH_K": pinch}) for i in ids], FOLDER, stem)
        ref, m0 = calibrate(ok)
        main, strict = econ(ok, m0, ref["ID"])
        write_econ(main, FOLDER / f"econ_{stem}.csv")
        write_econ(strict, FOLDER / f"econ_{stem}_strict.csv")
        pareto_png(main, FOLDER, f"pareto_{stem}.png")
        pareto_png(strict, FOLDER, f"pareto_{stem}_strict.png")
        sets.append(dict(label=f"{pinch:g} K", raw=ok, ref=ref, m0=m0, main=main, strict=strict,
                         n_bad=len(bad)))
    config.M0_T, config.M0_REF_ID = m00, ref0["ID"]

    md = ["# S1: cooler pinch 3 K and 8 K", "",
          "Every design in data/inputs.csv re-solved with the CO2-water cooler pinch set to 3 K "
          "and 8 K (baseline 5 K); M0 recalibrated on the most efficient feasible layout 2 "
          "design at T_turb 500 C for each pinch, so the reference stays at 60 t. Economics and "
          "both rankings rerun (layout 1 unranked; strict = every compressor inlet >= 7.7 MPa). "
          "The cooler pinch does not change the cycle (the cooler outlet is fixed at T_in), "
          "only the cooler UA, mass and water flow.", "",
          table(["case", "attempted", "feasible", "infeasible"],
                [[s["label"], len(s["raw"]) + s["n_bad"], len(s["raw"]), s["n_bad"]] for s in sets]),
          ""]
    md += describe(sets)
    md += ["## Does the winner change? (against 5 K)", ""]
    for s in sets[1:]:
        md += [f"**{s['label']}**", ""] + changes(sets[0], s) + [""]
    md += ["Plots: " + ", ".join(f"pareto_pinch{p:g}.png, pareto_pinch{p:g}_strict.png"
                                 for p in PINCHES) + ".", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
