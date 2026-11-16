"""core/export_states.py: data/results_econ.csv -> data/states.csv + data/shortlist.csv.

    python -m core.export_states [--workers N]

Tags the knee, top-N lists and the best design per layout, re-solves every
tagged ID with 100 cooler slices, and writes every stream state.
"""
import argparse
import csv
import multiprocessing as mp
from pathlib import Path

import config
from core.economics import COLUMNS as ECON_COLUMNS
from cycles import solve
from helpers.builders import build

DATA = Path(__file__).resolve().parents[1] / "data"
ECON = DATA / "results_econ.csv"
STATES = DATA / "states.csv"
SHORTLIST = DATA / "shortlist.csv"
STATE_COLUMNS = ["ID", "tags", "stream", "P_MPa", "T_C", "h_kJ_kg", "s_kJ_kgK", "flow"]
SHORT_COLUMNS = ["ID", "tags"] + ECON_COLUMNS[1:] + ["water_flow_kg_s", "mdot_kg_s"]


def tag_rows(rows, n=None):
    """{ID: [tags]} for the knee, top-N lists and best per layout."""
    n = n or config.N_TOP
    tags = {}

    def add(id_, t):
        tags.setdefault(id_, []).append(t)

    f = lambda r, k: float(r[k])
    for r in rows:
        if r["knee"] == "1":
            add(r["ID"], "knee")
    for k, r in enumerate(sorted(rows, key=lambda r: int(r["topsis_rank"]))[:n], 1):
        add(r["ID"], f"topsis_{k}")
    for k, r in enumerate(sorted(rows, key=lambda r: -f(r, "eta"))[:n], 1):
        add(r["ID"], f"eta_{k}")
    for k, r in enumerate(sorted(rows, key=lambda r: f(r, "mass_t"))[:n], 1):
        add(r["ID"], f"mass_{k}")
    for k, r in enumerate(sorted(rows, key=lambda r: -f(r, "payout_usd"))[:n], 1):
        add(r["ID"], f"payout_{k}")
    for L in sorted({r["layout"] for r in rows}, key=int):
        best = max((r for r in rows if r["layout"] == L), key=lambda r: f(r, "payout_usd"))
        add(best["ID"], f"best_L{L}")
    return tags


def _solve(id_):
    r = solve(build(id_, cooler_nodes=100))
    streams = {sid: dict(P=s["P"], T=s["T"], h=s["h"], s=s["s"], flow=s["flow"])
               for sid, s in r.streams.items()}
    mdot = r.metrics.get("mdot", float("nan"))
    water = sum(b.get("coolant_flow", 0.0) for b in r.blocks.values()
                if b.get("kind") == "cooler") * mdot
    return id_, r.ok, list(r.flags), streams, mdot, water


def _skey(sid):
    """s1 < s2 < ... < s11 < s11a < s11b."""
    num = "".join(ch for ch in sid[1:] if ch.isdigit())
    return (int(num) if num else 0, sid)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=config.SWEEP_WORKERS)
    args = ap.parse_args(argv)
    with open(ECON, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    by_id = {r["ID"]: r for r in rows}
    tags = tag_rows(rows)
    ids = sorted(tags)
    print(f"{len(ids)} tagged designs; re-solving with 100 cooler slices")
    with mp.Pool(max(1, min(args.workers, len(ids)))) as pool:
        results = sorted(pool.imap_unordered(_solve, ids))

    with open(STATES, "w", newline="", encoding="utf-8") as fs, \
            open(SHORTLIST, "w", newline="", encoding="utf-8") as fl:
        ws = csv.writer(fs, lineterminator="\n")
        wl = csv.writer(fl, lineterminator="\n")
        ws.writerow(STATE_COLUMNS)
        wl.writerow(SHORT_COLUMNS)
        for id_, ok, flags, streams, mdot, water in results:
            t = " ".join(tags[id_])
            if not ok:
                print(f"  WARNING {id_}: re-solve not ok: {flags}")
            for sid in sorted(streams, key=_skey):
                s = streams[sid]
                ws.writerow([id_, t, sid, f"{s['P']/1e6:.6g}", f"{s['T']-273.15:.6g}",
                             f"{s['h']/1e3:.6g}", f"{s['s']/1e3:.6g}", f"{s['flow']:.6g}"])
            r = by_id[id_]
            wl.writerow([id_, t] + [r[c] for c in ECON_COLUMNS[1:]]
                        + [f"{water:.6g}", f"{mdot:.6g}"])
    print(f"-> {STATES.name}, {SHORTLIST.name}")


if __name__ == "__main__":
    main()
