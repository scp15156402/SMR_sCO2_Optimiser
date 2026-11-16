"""core/solve_points.py: data/inputs.csv -> data/results_raw.csv + data/infeasible.csv.

    python -m core.solve_points [--grid NAME] [--ids ID ...] [--limit N] [--workers N]

Resumable: every ID already in either output file is skipped. Parallel: a
multiprocessing pool solves, only the main process writes, one row per
finished point, flushed immediately, so Ctrl+C leaves both files intact.
"""
import argparse
import csv
import multiprocessing as mp
import os
import signal
import time
from collections import Counter
from pathlib import Path

import config
from helpers.checks import COLUMNS as RAW_COLUMNS
from helpers.checks import evaluate
from helpers.ids import parse_id

DATA = Path(__file__).resolve().parents[1] / "data"
INPUTS = DATA / "inputs.csv"
RAW = DATA / "results_raw.csv"
INFEASIBLE = DATA / "infeasible.csv"
INF_COLUMNS = ["ID", "layout", "reason"]
PROGRESS_EVERY = 50


def _work(id_):
    return id_, *evaluate(id_)


def _ignore_sigint():
    """Workers ignore Ctrl+C; the main process handles it and stops the pool."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _repair(path, columns):
    """Drop an incomplete last line; check the header. Return IDs already present."""
    if not path.exists():
        return set()
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        cut = data.rfind(b"\n") + 1
        print(f"{path.name}: dropping incomplete last line ({len(data) - cut} bytes)")
        with open(path, "r+b") as fh:
            fh.truncate(cut)
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return set()
    if rows[0] != columns:
        raise SystemExit(f"{path}: header {rows[0]} does not match {columns}")
    return {r[0] for r in rows[1:] if r}


def _open(path, columns):
    new = not path.exists() or path.stat().st_size == 0
    fh = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(fh, lineterminator="\n")
    if new:
        w.writerow(columns)
        fh.flush()
    return fh, w


def _reason_key(reason):
    """Category of one reason, for the summary: text before ' (' or ':'."""
    return reason.split(" (")[0].split(":")[0]


def _fmt_s(s):
    s = int(s)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grid", help="only IDs from this grid")
    ap.add_argument("--ids", nargs="+", help="only these IDs (must be in inputs.csv)")
    ap.add_argument("--limit", type=int, help="solve at most N new points this run")
    ap.add_argument("--workers", type=int, default=config.SWEEP_WORKERS)
    ap.add_argument("--deadline", help="HH:MM local time: stop cleanly then, as on Ctrl+C")
    args = ap.parse_args(argv)
    deadline = None
    if args.deadline:
        hh, mm = map(int, args.deadline.split(":"))
        now = time.localtime()
        deadline = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, hh, mm, 0, 0, 0, -1))
        if time.time() >= deadline:
            print(f"deadline {args.deadline} already passed; nothing run")
            return

    with open(INPUTS, newline="", encoding="utf-8") as fh:
        inputs = list(csv.DictReader(fh))
    known = {r["ID"] for r in inputs}
    todo = [r["ID"] for r in inputs if args.grid is None or r["grid"] == args.grid]
    if args.ids:
        missing = [i for i in args.ids if i not in known]
        if missing:
            raise SystemExit(f"not in inputs.csv: {missing}")
        wanted = set(args.ids)
        todo = [i for i in todo if i in wanted]

    done = _repair(RAW, RAW_COLUMNS) | _repair(INFEASIBLE, INF_COLUMNS)
    todo = [i for i in todo if i not in done]
    if args.limit is not None:
        todo = todo[:args.limit]
    total = len(todo)
    workers = max(1, min(args.workers, total))
    print(f"{total} new points to solve ({len(done)} already done), "
          f"workers {workers}, CPUs {os.cpu_count()}")
    if not total:
        return

    raw_fh, raw_w = _open(RAW, RAW_COLUMNS)
    inf_fh, inf_w = _open(INFEASIBLE, INF_COLUMNS)
    n_feas = n_inf = 0
    reasons = Counter()
    t0 = time.perf_counter()
    interrupted = False
    pool = mp.Pool(workers, initializer=_ignore_sigint)
    try:
        it = pool.imap_unordered(_work, todo, chunksize=1)
        while True:
            if deadline is not None and time.time() >= deadline:
                print(f"\ndeadline {args.deadline} reached")
                raise KeyboardInterrupt
            try:
                id_, status, payload = it.next(timeout=2)
            except mp.TimeoutError:
                continue
            except StopIteration:
                break
            if status == "feasible":
                raw_w.writerow([payload[c] for c in RAW_COLUMNS])
                raw_fh.flush()
                n_feas += 1
            else:
                inf_w.writerow([id_, parse_id(id_)["layout"], payload])
                inf_fh.flush()
                n_inf += 1
                for part in payload.split("; "):
                    reasons[_reason_key(part)] += 1
            n = n_feas + n_inf
            if n % PROGRESS_EVERY == 0 or n == total:
                el = time.perf_counter() - t0
                left = el / n * (total - n)
                print(f"  {n}/{total}  feasible {n_feas}  infeasible {n_inf}  "
                      f"elapsed {_fmt_s(el)}  left ~{_fmt_s(left)}", flush=True)
        pool.close()
    except KeyboardInterrupt:
        interrupted = True
        print("\ninterrupted: stopping workers; files are intact")
        pool.terminate()
    finally:
        pool.join()
        raw_fh.close()
        inf_fh.close()

    wall = time.perf_counter() - t0
    n = n_feas + n_inf
    print(f"\n{'interrupted' if interrupted else 'done'}: attempted {n}, "
          f"feasible {n_feas}, infeasible {n_inf}")
    for k, v in sorted(reasons.items()):
        print(f"  {k}: {v}")
    print(f"wall {wall:.1f} s, {n / wall if wall else 0:.2f} points/s")
    label = args.grid or ("ids" if args.ids else "all")
    log_run(label + (" (interrupted)" if interrupted else ""), workers, n, n_feas, n_inf, wall)


SWEEP_LOG = DATA / "sweep_log.csv"


def log_run(label, workers, n, n_feas, n_inf, wall):
    """Append one line per run to data/sweep_log.csv (read by core.summary)."""
    new = not SWEEP_LOG.exists()
    with open(SWEEP_LOG, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if new:
            w.writerow(["run", "workers", "attempted", "feasible", "infeasible",
                        "wall_s", "points_per_s"])
        w.writerow([label, workers, n, n_feas, n_inf, f"{wall:.1f}",
                    f"{n / wall if wall else 0:.3f}"])


if __name__ == "__main__":
    main()
