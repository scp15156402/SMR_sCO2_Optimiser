"""core/economics.py: data/results_raw.csv -> data/results_econ.csv (+ _strict).

    python -m core.economics

mass, cost, payout (PLAN.md formulas), Pareto flag, knee and TOPSIS.
Layouts in config.RANK_EXCLUDE_LAYOUTS keep their rows but are left out of the
ranking (pareto/knee/topsis columns empty). results_econ_strict.csv repeats the
ranking with every design whose lowest compressor inlet pressure is below
config.P_INLET_MIN_MPA removed (all of layout 6 as built).
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
ECON_STRICT = DATA / "results_econ_strict.csv"
RANK_COLUMNS = ("pareto", "knee", "topsis_score", "topsis_rank")
EXTRA = ["layout", "P_comp_in_min_MPa", "W_net_MW", "mass_t", "volume_m3", "mwe_per_t", "hardware_usd",
         "electricity_usd_per_yr", "payout_usd", "M0_used", "pareto", "knee",
         "topsis_score", "topsis_rank"]
COLUMNS = RAW_COLUMNS + EXTRA


def _f(v):
    return float(v) if v not in ("", None) else 0.0


def comp_inlet_min_MPa(id_):
    """Lowest compressor inlet pressure (no pressure drops): P_exh for layout 6
    (pre-compressor), P_low for every other layout."""
    p = parse_id(id_)
    return (p["Pe"] if p["layout"] == 6 else p["Pl"]) / 10


def strict_ok(id_):
    return comp_inlet_min_MPa(id_) >= config.P_INLET_MIN_MPA - 1e-9


def rank(rows):
    """Pareto, knee and TOPSIS over the rows that are not in an excluded layout;
    the excluded rows get empty rank columns. In place."""
    sel = [r for r in rows if r["layout"] not in config.RANK_EXCLUDE_LAYOUTS]
    for r in rows:
        r.update({c: "" for c in RANK_COLUMNS})
    if not sel:
        return rows
    pay = [r["payout_usd"] for r in sel]
    mass = [r["mass_t"] for r in sel]
    front = pareto(pay, mass)
    k = knee(pay, mass, front)
    score = topsis(pay, mass, config.TOPSIS_WEIGHTS)
    rk = ranks(score)
    for i, r in enumerate(sel):
        r.update(pareto=int(front[i]), knee=int(i == k),
                 topsis_score=score[i], topsis_rank=rk[i])
    return rows


def compute(raw_rows, lifetime_years=None, strict=False):
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
        out.append({**r, "layout": layout, "P_comp_in_min_MPa": comp_inlet_min_MPa(r["ID"]),
                    "W_net_MW": w_mw, "mass_t": mass,
                    "volume_m3": mass / config.DENSITY_T_PER_M3,
                    "mwe_per_t": w_mw / mass, "hardware_usd": hw,
                    "electricity_usd_per_yr": elec, "payout_usd": N * elec - hw,
                    "M0_used": config.M0_T})
    if strict:
        out = [r for r in out if strict_ok(r["ID"])]
    return rank(out)


def _fmt(v):
    if isinstance(v, float):
        return format(v, ".8g")
    return str(v)


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in sorted(rows, key=lambda r: r["ID"]):
            w.writerow([_fmt(r[c]) for c in COLUMNS])


def describe(rows):
    kn = next(r for r in rows if r["knee"] == 1)
    t1 = next(r for r in rows if r["topsis_rank"] == 1)
    ranked = sum(r["pareto"] != "" for r in rows)
    return (f"{len(rows)} rows ({ranked} ranked); Pareto front "
            f"{sum(r['pareto'] == 1 for r in rows)}; knee {kn['ID']}; TOPSIS #1 {t1['ID']}")


def main():
    with open(RAW, newline="", encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))
    main_rows, strict_rows = compute(raw), compute(raw, strict=True)
    write(ECON, main_rows)
    write(ECON_STRICT, strict_rows)
    print(f"excluded from ranking: layouts {config.RANK_EXCLUDE_LAYOUTS}")
    print(f"main   -> {ECON.name}: {describe(main_rows)}")
    print(f"strict -> {ECON_STRICT.name}: {describe(strict_rows)} "
          f"({len(main_rows) - len(strict_rows)} designs with a compressor inlet "
          f"< {config.P_INLET_MIN_MPA} MPa removed)")


if __name__ == "__main__":
    main()
