"""core/economics.py: data/results_raw.csv -> data/results_econ.csv.

    python -m core.economics

mass, cost, payout (PLAN.md formulas), Pareto flag, knee and TOPSIS.
Refuses to run until config.M0_T has been calibrated.
"""
import csv
from pathlib import Path

import config
from helpers.checks import COLUMNS as RAW_COLUMNS
from helpers.ids import parse_id
from helpers.ranking import knee, pareto, ranks, topsis

DATA = Path(__file__).resolve().parents[1] / "data"
RAW = DATA / "results_raw.csv"
ECON = DATA / "results_econ.csv"
EXTRA = ["layout", "W_net_MW", "mass_t", "volume_m3", "mwe_per_t", "hardware_usd",
         "electricity_usd_per_yr", "payout_usd", "M0_used", "pareto", "knee",
         "topsis_score", "topsis_rank"]
COLUMNS = RAW_COLUMNS + EXTRA


def _f(v):
    return float(v) if v not in ("", None) else 0.0


def compute(raw_rows, lifetime_years=None):
    """Raw rows (dicts of strings) -> econ rows (dicts of numbers/strings)."""
    if config.M0_T is None:
        raise SystemExit("config.M0_T is None: run python -m core.calibrate and "
                         "enter M0_T in config.py section D first")
    N = config.LIFETIME_YEARS if lifetime_years is None else lifetime_years
    out = []
    for r in raw_rows:
        layout = parse_id(r["ID"])["layout"]
        eta = float(r["eta"])
        ua_recup = _f(r["UA_recup_1"]) + _f(r["UA_recup_2"])
        ua_cool = _f(r["UA_cooler_1"]) + _f(r["UA_cooler_2"])
        mass = (config.KG_PER_KW_K * ua_recup / 1000
                + config.COOLER_KG_PER_KW_K * ua_cool / 1000
                + config.M0_T
                + config.EXTRA_COMPRESSOR_T * config.EXTRA_COMPRESSORS[layout])
        w_mw = eta * config.Q_THERMAL_MW
        elec = w_mw * config.HOURS_PER_YEAR * config.USD_PER_MWH
        hw = config.USD_PER_KG * 1000 * mass
        out.append({**r, "layout": layout, "W_net_MW": w_mw, "mass_t": mass,
                    "volume_m3": mass / config.DENSITY_T_PER_M3,
                    "mwe_per_t": w_mw / mass, "hardware_usd": hw,
                    "electricity_usd_per_yr": elec, "payout_usd": N * elec - hw,
                    "M0_used": config.M0_T})
    pay = [r["payout_usd"] for r in out]
    mass = [r["mass_t"] for r in out]
    front = pareto(pay, mass)
    k = knee(pay, mass, front)
    score = topsis(pay, mass, config.TOPSIS_WEIGHTS)
    rank = ranks(score)
    for i, r in enumerate(out):
        r.update(pareto=int(front[i]), knee=int(i == k),
                 topsis_score=score[i], topsis_rank=rank[i])
    return out


def _fmt(v):
    if isinstance(v, float):
        return format(v, ".8g")
    return str(v)


def main():
    with open(RAW, newline="", encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))
    rows = sorted(compute(raw), key=lambda r: r["ID"])
    with open(ECON, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([_fmt(r[c]) for c in COLUMNS])
    kn = next(r for r in rows if r["knee"])
    print(f"{len(rows)} rows -> {ECON.name}; Pareto front {sum(r['pareto'] for r in rows)}; "
          f"knee {kn['ID']}; TOPSIS #1 {next(r['ID'] for r in rows if r['topsis_rank'] == 1)}")


if __name__ == "__main__":
    main()
