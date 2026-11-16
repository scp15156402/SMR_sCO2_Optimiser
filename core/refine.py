"""core/refine.py: refine the sweep in rounds until more points tell us nothing new.

    python -m core.refine [--max-rounds 6] [--minutes 90]

Each round: append grids to grids.py, make_inputs, solve_points (8 workers),
economics, export_states, plots, summary, out/convergence.md, commit, push.

Round 1 grids are fixed (ROUND1). Later rounds are built around each of
layouts 2, 3, 5, 6's best-payout and best-TOPSIS designs:
  * on a grid edge that is not a hard constraint -> extend past it (2 steps);
  * otherwise halve the local step around it, down to the ID resolution
    (pressure 0.1 MPa, T_in 0.5 C, split 0.01);
  * an axis whose winner sits on a hard constraint (or a pressure-ordering
    limit) is not refined: the constraint pins it.
Stops when, against the previous round, best payout per layout moves < 0.05 %,
TOPSIS #1 payout and mass (with and without layout 1) move < 0.1 %, and no
winner sits on a non-constraint edge; or after max rounds / minutes.
"""
import argparse
import csv
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "out"
STATE = DATA / "refine_rounds.json"
REFINED_LAYOUTS = (2, 3, 5, 6)

ROUND1 = {
    "W1_L3": dict(layout=3, P_high=[200], P_low=(77, 85, 2), T_in=(320, 360, 5),
                  split=(30, 48, 1), T_turb=[500]),
    "W1_L6": dict(layout=6, P_high=[200], P_mid=(77, 85, 4), P_exh=(40, 65, 5),
                  T_in=(320, 360, 10), split=(30, 50, 5), T_turb=[500]),
    "W1_L5": dict(layout=5, P_high=[200], P_low=[77, 80], T_in=(320, 340, 10),
                  split=(30, 42, 2), P_mid=(90, 110, 10), T_turb=[500]),
    "W1_L2": dict(layout=2, P_high=[200], P_low=(77, 82, 1), T_in=(320, 360, 5),
                  T_turb=[500]),
    "W1_L4": dict(layout=4, P_high=[200], P_low=(77, 85, 4), T_in=(320, 340, 10),
                  P_mid=(100, 160, 20), T_turb=[500]),
}

FIELD_AXIS = {"Ph": "P_high", "Pl": "P_low", "T": "T_in", "Tt": "T_turb",
              "Pm": "P_mid", "Pe": "P_exh", "x": "split"}
MIN_STEP = {"Ph": 1, "Pl": 1, "Pm": 1, "Pe": 1, "T": 5, "x": 1}
DEFAULT_STEP = {"Ph": 10, "Pl": 5, "Pm": 10, "Pe": 5, "T": 10, "x": 5}


def run(*args):
    print(f"\n$ {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=True)


def git(*args, check=True):
    print(f"$ git {' '.join(args)}", flush=True)
    return subprocess.run(["git", *args], cwd=ROOT, check=check)


def read(name):
    p = DATA / name
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------ constraints --
def valid(field, v, w, layout):
    """Is value v for `field` allowed, given the winner's other fields w?"""
    import config
    if v <= 0:
        return False
    o = {**w, field: v}
    if field == "Ph":
        return v <= round(config.P_MAX_MPA * 10) and all(
            v > o[k] for k in ("Pl", "Pm", "Pe") if k in o)
    if field == "Pl":
        return (v >= round(config.P_INLET_MIN_MPA * 10) and v < o["Ph"]
                and ("Pm" not in o or v < o["Pm"]))
    if field == "Pm":
        if layout == 6:
            return v >= round(config.P_INLET_MIN_MPA * 10) and o["Pe"] < v < o["Ph"]
        return o["Pl"] < v < o["Ph"]
    if field == "Pe":
        return v < o["Pm"]
    if field == "T":
        return v >= round(config.T_INLET_MIN_C * 10)
    if field == "x":
        return round(config.SPLIT_MIN * 100) < v <= round(config.SPLIT_MAX * 100)
    return False


def lines(input_ids):
    """{(layout, field, other-fields-key): sorted values} over attempted IDs."""
    from helpers.ids import FIELDS, parse_id
    out = {}
    for id_ in input_ids:
        p = parse_id(id_)
        L = p["layout"]
        for f in FIELDS[L]:
            key = (L, f, tuple((g, p[g]) for g in FIELDS[L] if g != f))
            out.setdefault(key, set()).add(p[f])
            out.setdefault((L, f, "all"), set()).add(p[f])
    return out


def analyse(id_, line_map):
    """Per-field: step, on non-constraint edge low/high, and proposed values."""
    from helpers.ids import FIELDS, parse_id
    p = parse_id(id_)
    L = p["layout"]
    w = {f: p[f] for f in FIELDS[L]}
    res = {}
    for f in FIELDS[L]:
        if f == "Tt":
            continue
        # step: nearest neighbour on the exact line, else anywhere in the layout
        line = line_map.get((L, f, tuple((g, w[g]) for g in FIELDS[L] if g != f)), {w[f]})
        span = line_map.get((L, f, "all"), line)
        near = [abs(v - w[f]) for v in line if v != w[f]] or \
               [abs(v - w[f]) for v in span if v != w[f]]
        s = min(near) if near else DEFAULT_STEP[f]
        # edge: the winner is at the end of everything this layout has tried
        lo = [v for v in span if v < w[f]]
        hi = [v for v in span if v > w[f]]
        edge_lo = not lo and valid(f, w[f] - s, w, L)
        edge_hi = not hi and valid(f, w[f] + s, w, L)
        new = {w[f]}
        if edge_lo:
            new |= {v for v in (w[f] - s, w[f] - 2 * s) if valid(f, v, w, L)}
        if edge_hi:
            new |= {v for v in (w[f] + s, w[f] + 2 * s) if valid(f, v, w, L)}
        at_bound = (not hi and not valid(f, w[f] + s, w, L)) or \
                   (not lo and not valid(f, w[f] - s, w, L))
        if not (edge_lo or edge_hi or at_bound):
            m = MIN_STEP[f]
            h = (s // 2) // m * m
            if m <= h < s:
                new |= {v for v in (w[f] - h, w[f] + h) if valid(f, v, w, L)}
        res[f] = dict(step=s, edge_lo=edge_lo, edge_hi=edge_hi, values=sorted(new))
    return L, w, res


def propose(snapshot, input_ids, rnd):
    """Grids for the next round around each layout's winners."""
    lm = lines(input_ids)
    grids = {}
    for L in REFINED_LAYOUTS:
        winners = {snapshot["winners"][str(L)][k] for k in ("payout", "topsis")
                   if snapshot["winners"].get(str(L))}
        for tag, id_ in zip(("a", "b"), sorted(winners)):
            _, w, res = analyse(id_, lm)
            g = dict(layout=L, T_turb=[w["Tt"]])
            for f, r in res.items():
                g[FIELD_AXIS[f]] = r["values"]
            n = 1
            for f, r in res.items():
                n *= len(r["values"])
            if n > 1:
                grids[f"W{rnd}_L{L}{tag}"] = g
    return grids


def append_grids(grids, rnd):
    text = [f"\n# refinement round {rnd} (core/refine.py)", "GRIDS.update({"]
    for name, g in grids.items():
        body = ", ".join(f"{k}={v!r}" for k, v in g.items())
        text.append(f"    {name!r}: dict({body}),")
    text.append("})\n")
    with open(ROOT / "grids.py", "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(text))


# --------------------------------------------------------------- snapshot --
def snapshot():
    import config
    from helpers.ranking import knee, pareto, topsis
    econ = read("results_econ.csv")
    ids = [r["ID"] for r in read("inputs.csv")]
    lm = lines(ids)
    f = float
    best = {}
    for L in sorted({r["layout"] for r in econ}, key=int):
        b = max((r for r in econ if r["layout"] == L), key=lambda r: f(r["payout_usd"]))
        best[L] = dict(ID=b["ID"], eta=f(b["eta"]), mass=f(b["mass_t"]), payout=f(b["payout_usd"]))

    def rank(rows):
        p = [f(r["payout_usd"]) for r in rows]
        m = [f(r["mass_t"]) for r in rows]
        s = topsis(p, m, config.TOPSIS_WEIGHTS)
        t = rows[max(range(len(rows)), key=lambda i: s[i])]
        k = rows[knee(p, m, pareto(p, m))]
        pick = lambda r: dict(ID=r["ID"], eta=f(r["eta"]), mass=f(r["mass_t"]),
                              payout=f(r["payout_usd"]))
        return pick(t), pick(k)

    t_all, k_all = rank(econ)
    t_no1, k_no1 = rank([r for r in econ if r["layout"] != "1"])
    winners, edges = {}, {}
    for L in REFINED_LAYOUTS:
        rows = [r for r in econ if r["layout"] == str(L)]
        if not rows:
            continue
        wp = max(rows, key=lambda r: f(r["payout_usd"]))["ID"]
        wt = max(rows, key=lambda r: f(r["topsis_score"]))["ID"]
        winners[str(L)] = dict(payout=wp, topsis=wt)
        for id_ in {wp, wt}:
            _, _, res = analyse(id_, lm)
            on = [f"{k}{'-' if r['edge_lo'] else '+'}" for k, r in res.items()
                  if r["edge_lo"] or r["edge_hi"]]
            edges[id_] = on
    return dict(feasible=len(econ), attempted=len(read("results_raw.csv")) + len(read("infeasible.csv")),
                best=best, topsis=t_all, topsis_no1=t_no1, knee=k_all, knee_no1=k_no1,
                winners=winners, edges=edges)


def conditions(prev, cur):
    if prev is None:
        return dict(payout=False, topsis=False, edges=not any(cur["edges"].values()))
    rel = lambda a, b: abs(a - b) / abs(b) if b else float("inf")
    c1 = all(rel(cur["best"][L]["payout"], prev["best"][L]["payout"]) < 5e-4
             for L in cur["best"] if L in prev["best"])
    c2 = all(rel(cur[k]["payout"], prev[k]["payout"]) < 1e-3 and
             rel(cur[k]["mass"], prev[k]["mass"]) < 1e-3 for k in ("topsis", "topsis_no1"))
    c3 = not any(cur["edges"].values())
    return dict(payout=c1, topsis=c2, edges=c3)


# ---------------------------------------------------------------- report --
def report(rounds):
    yn = lambda b: "yes" if b else "no"
    md = ["# Refinement convergence (branch wager)", "",
          "Stop when, against the previous round: best payout per layout moves < 0.05 %; "
          "TOPSIS #1 payout and mass (with and without layout 1) move < 0.1 %; "
          "no layout 2/3/5/6 winner (best payout or best TOPSIS) on a non-constraint grid edge. "
          "Round 0 is the state inherited from branch rebuild.", "",
          "## Rounds", "",
          "| round | points added | total feasible | TOPSIS #1 (with L1) | TOPSIS #1 (no L1) | knee (with L1) | knee (no L1) | payout < 0.05 % | TOPSIS < 0.1 % | no free edge | wall min |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rounds:
        s, c = r["snap"], r["cond"]
        cell = lambda d: f"{d['ID']} ({d['payout']/1e6:.2f} M$, {d['mass']:.2f} t)"
        md.append(f"| {r['round']} | {r['added']} | {s['feasible']} | {cell(s['topsis'])} | "
                  f"{cell(s['topsis_no1'])} | {s['knee']['ID']} | {s['knee_no1']['ID']} | "
                  f"{yn(c['payout'])} | {yn(c['topsis'])} | {yn(c['edges'])} | {r['minutes']:.1f} |")
    md += ["", "## Best payout design per layout", "",
           "| round | layout | ID | eta | mass t | payout M$ |", "|---|---|---|---|---|---|"]
    for r in rounds:
        for L, b in r["snap"]["best"].items():
            md.append(f"| {r['round']} | {L} | {b['ID']} | {b['eta']:.5f} | {b['mass']:.2f} | "
                      f"{b['payout']/1e6:.3f} |")
    md += ["", "## Winners on a non-constraint grid edge (after each round)", "",
           "| round | ID | free edges |", "|---|---|---|"]
    for r in rounds:
        for id_, e in r["snap"]["edges"].items():
            md.append(f"| {r['round']} | {id_} | {', '.join(e) if e else '-'} |")
    last = rounds[-1]
    md += ["", "## Verdict", "", last.get("verdict", "(running)"), ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "convergence.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    print("\n".join(md[6:6 + 2 + len(rounds)]), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--minutes", type=float, default=90)
    args = ap.parse_args(argv)
    t0 = time.time()
    end = t0 + args.minutes * 60
    deadline = time.strftime("%H:%M", time.localtime(end))
    print(f"refine: start {time.strftime('%H:%M')}, hard stop {deadline}", flush=True)

    rounds = [dict(round=0, added=0, snap=snapshot(), minutes=0.0)]
    rounds[0]["cond"] = conditions(None, rounds[0]["snap"])
    verdict = None
    for rnd in range(1, args.max_rounds + 1):
        if time.time() >= end:
            verdict = f"Stopped at the {args.minutes:g}-minute limit before round {rnd}; NOT converged."
            break
        prev = rounds[-1]["snap"]
        grids = ROUND1 if rnd == 1 else propose(prev, [r["ID"] for r in read("inputs.csv")], rnd)
        if not grids:
            verdict = f"Round {rnd}: no further refinement possible at ID resolution."
            break
        before = prev["attempted"]
        append_grids(grids, rnd)
        run("core.make_inputs")
        try:
            run("core.solve_points", "--workers", "8", "--deadline", deadline)
        except subprocess.CalledProcessError as e:
            print(f"solve_points failed: {e}", flush=True)
        run("core.economics")
        run("core.export_states")
        run("core.plots")
        run("core.summary")
        snap = snapshot()
        cond = conditions(prev, snap)
        rounds.append(dict(round=rnd, added=snap["attempted"] - before, snap=snap, cond=cond,
                           minutes=(time.time() - t0) / 60))
        timed_out = time.time() >= end
        if all(cond.values()):
            verdict = (f"CONVERGED after round {rnd}: all three stop conditions hold "
                       f"against round {rnd - 1}.")
        elif timed_out:
            verdict = (f"NOT converged: the {args.minutes:g}-minute limit was reached during "
                       f"round {rnd}. Unmet: {', '.join(k for k, v in cond.items() if not v)}.")
        elif rnd == args.max_rounds:
            verdict = (f"NOT converged after {rnd} rounds. Unmet: "
                       f"{', '.join(k for k, v in cond.items() if not v)}.")
        rounds[-1]["verdict"] = verdict or "(continuing)"
        STATE.write_text(json.dumps(rounds, indent=1), encoding="utf-8")
        report(rounds)
        git("add", "-A")
        git("commit", "-q", "-m", f"wager: refinement round {rnd}\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", check=False)
        git("push", "-q", "-u", "origin", "wager", check=False)
        if verdict:
            break
    if verdict and rounds[-1].get("verdict") != verdict:
        rounds[-1]["verdict"] = verdict
        report(rounds)
        git("add", "-A")
        git("commit", "-q", "-m", "wager: convergence verdict\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", check=False)
        git("push", "-q", "-u", "origin", "wager", check=False)
    print(f"\nrefine done: {verdict}", flush=True)


if __name__ == "__main__":
    main()
