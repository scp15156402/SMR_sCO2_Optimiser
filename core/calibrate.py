"""core/calibrate.py: print M0 from the best-efficiency feasible layout-2 point.

    python -m core.calibrate

Prints only; the user pastes M0_T and M0_REF_ID into config.py section D.
"""
import csv
from pathlib import Path

import config
from helpers.ids import parse_id

RAW = Path(__file__).resolve().parents[1] / "data" / "results_raw.csv"


def layout2_rows():
    with open(RAW, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if parse_id(r["ID"])["layout"] == 2]
    if not rows:
        raise SystemExit("no feasible layout-2 rows in results_raw.csv")
    return sorted(rows, key=lambda r: float(r["eta"]), reverse=True)


def calibration():
    """Reference row and the M0 it implies, as a dict."""
    ref = layout2_rows()[0]
    ua_r, ua_c = float(ref["UA_recup_1"]), float(ref["UA_cooler_1"])
    m_recup = config.KG_PER_KW_K * ua_r / 1000
    m_cooler = config.COOLER_KG_PER_KW_K * ua_c / 1000
    return dict(ID=ref["ID"], eta=float(ref["eta"]), UA_recup_1=ua_r, UA_cooler_1=ua_c,
                m_recup_t=m_recup, m_cooler_t=m_cooler,
                M0_t=config.BASELINE_MASS_T - m_recup - m_cooler)


def main():
    c = calibration()
    print(f"reference ID   {c['ID']}")
    print(f"eta            {c['eta']:.8f}")
    print(f"UA_recup_1     {c['UA_recup_1']:.2f} kW/K   -> m_recup  {c['m_recup_t']:.3f} t")
    print(f"UA_cooler_1    {c['UA_cooler_1']:.2f} kW/K   -> m_cooler {c['m_cooler_t']:.3f} t")
    print(f"M0 = {config.BASELINE_MASS_T} - {c['m_recup_t']:.3f} - {c['m_cooler_t']:.3f} "
          f"= {c['M0_t']:.3f} t")
    print("\ntop 10 layout-2 rows by eta")
    print(f"  {'ID':<28} {'eta':>10} {'UA_total':>10} {'pinch_recup_1':>14}")
    for r in layout2_rows()[:10]:
        print(f"  {r['ID']:<28} {float(r['eta']):10.6f} {float(r['UA_total']):10.1f} "
              f"{float(r['pinch_recup_1']):14.3f}")


if __name__ == "__main__":
    main()
