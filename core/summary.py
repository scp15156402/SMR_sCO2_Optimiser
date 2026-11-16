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
          f"STRICT_INLET_PRESSURE = {config.STRICT_INLET_PRESSURE}.", ""]

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
        top = sorted(econ, key=lambda r: float(r[key]), reverse=rev)[:N]
        md += [f"## 5. Top {N} by {title}", "", _table(brief_head, [row_brief(r) for r in top]), ""]

    # 6. lifetime sensitivity
    sens = []
    for yrs in (5, 10, 20):
        e = compute(raw, lifetime_years=yrs)
        k = next(r for r in e if r["knee"])
        t = next(r for r in e if r["topsis_rank"] == 1)
        p = max(e, key=lambda r: r["payout_usd"])
        sens.append([yrs, k["ID"], f"{k['payout_usd']/1e6:.2f}", t["ID"], f"{t['payout_usd']/1e6:.2f}",
                     p["ID"], f"{p['payout_usd']/1e6:.2f}", sum(r["pareto"] for r in e)])
    md += ["## 6. Lifetime sensitivity (recomputed in memory)", "",
           _table(["years", "knee", "knee payout M USD", "TOPSIS #1", "its payout M USD",
                   "max payout", "max payout M USD", "front size"], sens), ""]

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
