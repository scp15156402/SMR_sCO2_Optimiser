"""core/calibrate.py: M0 from the best-efficiency feasible layout-2 point at T_turb = 500 C.

    python -m core.calibrate            print only
    python -m core.calibrate --write    also write M0_T and M0_REF_ID into config.py section D
"""
import argparse
import csv
import re
from pathlib import Path

import config
from helpers.ids import parse_id

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "results_raw.csv"
CONFIG = ROOT / "config.py"


def layout2_rows():
    with open(RAW, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if parse_id(r["ID"])["layout"] == 2
                and parse_id(r["ID"])["Tt"] == round(config.T_TURBINE_MAX_C)]
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


def write_config(c):
    """Replace M0_T, M0_REF_ID and the reference comment in config.py section D."""
    text = CONFIG.read_text(encoding="utf-8")
    new = re.sub(r"^M0_T\s*=\s*[-\d.]+", f"M0_T      = {c['M0_t']:.3f}", text, count=1, flags=re.M)
    new = re.sub(r'^M0_REF_ID\s*=\s*"[^"]*"', f'M0_REF_ID = "{c["ID"]}"', new, count=1, flags=re.M)
    new = re.sub(r"^# reference: eta .*$",
                 f"# reference: eta {c['eta']:.8f}, UA_recup_1 {c['UA_recup_1']:.2f} kW/K, "
                 f"UA_cooler_1 {c['UA_cooler_1']:.2f} kW/K (50 cooler slices)",
                 new, count=1, flags=re.M)
    CONFIG.write_text(new, encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="update config.py section D")
    args = ap.parse_args(argv)
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
    if args.write:
        old = (config.M0_REF_ID, config.M0_T)
        write_config(c)
        print(f"\nconfig.py: M0_REF_ID {old[0]} -> {c['ID']}, M0_T {old[1]} -> {c['M0_t']:.3f}")


if __name__ == "__main__":
    main()
