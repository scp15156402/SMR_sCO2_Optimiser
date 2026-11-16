"""core/summary.py: out/summary.md from the data files.

    python -m core.summary

Reads inputs, results_raw, infeasible, results_econ, shortlist, sweep_log and
(optionally) data/run_notes.md. Lifetime sensitivity is recomputed in memory.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

import config
from core.calibrate import calibration
from core.economics import compute
from helpers.ids import parse_id

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "out"


def _read(name):
    p = DATA / name
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _g(v, fmt):
    return "" if v in ("", None) else format(float(v), fmt)


def main():
    inputs, raw, inf = _read("inputs.csv"), _read("results_raw.csv"), _read("infeasible.csv")
    econ, short, log = _read("results_econ.csv"), _read("shortlist.csv"), _read("sweep_log.csv")
    L = lambda id_: parse_id(id_)["layout"]
    md = ["# sCO2 Brayton study: summary", "",
          f"Q = {config.Q_THERMAL_MW:g} MWth, lifetime {config.LIFETIME_YEARS} yr, "
          f"{config.USD_PER_MWH:g} USD/MWh, {config.HOURS_PER_YEAR:g} h/yr, "
          f"{config.USD_PER_KG:g} USD/kg, TOPSIS weights {config.TOPSIS_WEIGHTS}, "
          f"cooler slices {config.COOLER_NODES} (sweep) / 100 (states), "
          f"STRICT_INLET_PRESSURE = {config.STRICT_INLET_PRESSURE}.", "",
          f"**Excluded from the ranking:** layout(s) "
          f"{', '.join(map(str, config.RANK_EXCLUDE_LAYOUTS)) or 'none'} "
          f"(RANK_EXCLUDE_LAYOUTS). Their rows stay in results_econ.csv with empty "
          f"pareto/knee/topsis columns; Pareto front, knee and TOPSIS cover the other layouts only.", ""]
    ranked = [r for r in econ if r["topsis_rank"] != ""]

    # 1. per layout
    n_in = Counter(L(r["ID"]) for r in inputs)
    n_f = Counter(L(r["ID"]) for r in raw)
    n_i = Counter(L(r["ID"]) for r in inf)
    reasons = defaultdict(Counter)
    for r in inf:
        for part in r["reason"].split("; "):
            reasons[L(r["ID"])][part.split(" (")[0].split(":")[0]] += 1
    rows = []
    for k in sorted(n_in):
        rs = ", ".join(f"{a}: {b}" for a, b in sorted(reasons[k].items())) or "-"
        rows.append([k, n_in[k], n_f[k] + n_i[k], n_f[k], n_i[k], rs])
    md += ["## 1. Points per layout", "",
           _table(["layout", "in grid", "attempted", "feasible", "infeasible", "reasons"], rows), ""]

    # 2. calibration
    c = calibration()
    md += ["## 2. Calibration (layout 2, best feasible eta)", "",
           _table(["reference ID", "eta", "UA_recup_1 kW/K", "UA_cooler_1 kW/K",
                   "m_recup t", "m_cooler t", "M0 t (computed)", "M0_T in config"],
                  [[c["ID"], f"{c['eta']:.6f}", f"{c['UA_recup_1']:.1f}", f"{c['UA_cooler_1']:.1f}",
                    f"{c['m_recup_t']:.3f}", f"{c['m_cooler_t']:.3f}", f"{c['M0_t']:.3f}",
                    config.M0_T]]), ""]

    def row_brief(r):
        return [r["ID"], _g(r["eta"], ".5f"), _g(r["eta_second_law"], ".4f"),
                _g(r["UA_total"], ".0f"), _g(r["mass_t"], ".2f"),
                _g(float(r["payout_usd"]) / 1e6, ".2f"), _g(r["mwe_per_t"], ".4f"),
                _g(r["pinch_recup_1"], ".2f"), _g(r["pinch_recup_2"], ".2f"),
                _g(r["pinch_cooler_1"], ".2f"), _g(r["pinch_cooler_2"], ".2f")]
    brief_head = ["ID", "eta", "eta_II", "UA_total kW/K", "mass t", "payout M USD",
                  "MWe/t", "pinch r1", "pinch r2", "pinch c1", "pinch c2"]

    # 3. best per layout
    best = []
    for k in sorted({r["layout"] for r in econ}, key=int):
        best.append(max((r for r in econ if r["layout"] == k), key=lambda r: float(r["payout_usd"])))
    md += ["## 3. Best design per layout (by payout)", "",
           _table(brief_head, [row_brief(r) for r in best]), ""]

    # 4. knee
    kn = next((r for r in short if "knee" in r["tags"].split()), None)
    if kn:
        md += ["## 4. Knee of the Pareto front", "",
               _table(["column", "value"], [[k, v] for k, v in kn.items() if v != ""]), ""]

    # 5. top N
    N = config.N_TOP
    for title, key, rev in [("TOPSIS", "topsis_score", True), ("efficiency", "eta", True),
                            ("lowest mass", "mass_t", False), ("payout", "payout_usd", True)]:
        pool = ranked if key == "topsis_score" else econ
        top = sorted(pool, key=lambda r: float(r[key]), reverse=rev)[:N]
        md += [f"## 5. Top {N} by {title}", "", _table(brief_head, [row_brief(r) for r in top]), ""]

    # 6. lifetime sensitivity
    sens = []
    for yrs in (5, 10, 20):
        e = [r for r in compute(raw, lifetime_years=yrs) if r["topsis_rank"] != ""]
        k = next(r for r in e if r["knee"] == 1)
        t = next(r for r in e if r["topsis_rank"] == 1)
        p = max(e, key=lambda r: r["payout_usd"])
        sens.append([yrs, k["ID"], f"{k['payout_usd']/1e6:.2f}", t["ID"], f"{t['payout_usd']/1e6:.2f}",
                     p["ID"], f"{p['payout_usd']/1e6:.2f}", sum(r["pareto"] for r in e)])
    md += ["## 6. Lifetime sensitivity (recomputed in memory, main ranking)", "",
           _table(["years", "knee", "knee payout M USD", "TOPSIS #1", "its payout M USD",
                   "max payout", "max payout M USD", "front size"], sens), ""]

    # 6b. strict reading of the 7.7 MPa limit
    strict = [r for r in _read("results_econ_strict.csv") if r["topsis_rank"] != ""]
    if strict:
        removed = sorted({r["layout"] for r in econ} - {r["layout"] for r in _read("results_econ_strict.csv")})
        front = sorted((r for r in strict if r["pareto"] == "1"), key=lambda r: float(r["mass_t"]))
        kn_s = next(r for r in strict if r["knee"] == "1")
        top_s = sorted(strict, key=lambda r: int(r["topsis_rank"]))[:10]
        md += ["## 6b. Strict ranking: every compressor inlet >= "
               f"{config.P_INLET_MIN_MPA:g} MPa (data/results_econ_strict.csv)", "",
               f"{len(econ) - len(_read('results_econ_strict.csv'))} designs with a compressor inlet below "
               f"{config.P_INLET_MIN_MPA:g} MPa removed (layouts left with no designs: "
               f"{', '.join(removed) or 'none'}); layouts {config.RANK_EXCLUDE_LAYOUTS} also unranked. "
               "The main ranking (results_econ.csv) is unchanged.", "",
               f"Knee: **{kn_s['ID']}**; TOPSIS #1: **{top_s[0]['ID']}**.", "",
               "### Pareto front", "",
               _table(["ID", "mass t", "payout M USD"],
                      [[r["ID"], _g(r["mass_t"], ".2f"), _g(float(r["payout_usd"]) / 1e6, ".2f")]
                       for r in front]), "",
               "### TOPSIS top 10", "",
               _table(["rank", "ID", "score", "mass t", "payout M USD"],
                      [[r["topsis_rank"], r["ID"], _g(r["topsis_score"], ".5f"), _g(r["mass_t"], ".2f"),
                        _g(float(r["payout_usd"]) / 1e6, ".2f")] for r in top_s]), ""]

    # 7. runs and notes
    md += ["## 7. Runs, skipped layouts and failed checks", ""]
    if log:
        md += [_table(list(log[0]), [list(r.values()) for r in log]), ""]
    notes = DATA / "run_notes.md"
    if notes.exists():
        md += [notes.read_text(encoding="utf-8").strip(), ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    print(f"-> out/summary.md ({len(md)} lines)")


if __name__ == "__main__":
    main()
