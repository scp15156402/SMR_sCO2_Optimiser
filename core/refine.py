"""core/refine.py: refine the sweep in rounds until more points tell us nothing new.

    python -m core.refine [--max-rounds 10] [--minutes 240]

Each round: append grids to grids.py, make_inputs, solve_points (8 workers),
recalibrate M0 if the most efficient layout-2 design changed, economics,
export_states, plots, summary, out/convergence.md, commit, push.

Continues from data/refine_rounds.json. With no saved state, round 1 uses the
fixed ROUND1 grids. Later rounds are built around the tracked winners:
best payout in each of layouts 2, 3, 5, 6; TOPSIS #1 and knee of the main
ranking; TOPSIS #1 of the strict ranking. For each winner and axis:
  * on a grid edge that is not a hard constraint -> extend past it (2 steps);
  * otherwise halve the local step around it, down to the ID resolution
    (pressure 0.1 MPa, T_in 0.5 C, split 0.01);
  * an axis whose winner sits on a hard constraint (or a pressure-ordering
    limit) is not refined: the constraint pins it.
Bounds: the brief's constraints (config.py) plus P_exh >= P_EXH_MIN_MPA, split <= SPLIT_MAX.
Stops when, against the previous round: best payout per layout (2, 3, 5, 6)
moves < 0.05 %; TOPSIS #1 payout and mass (main and strict) move < 0.1 %; no
tracked winner sits on a free grid edge. Otherwise after max rounds / minutes.
"""
import argparse
import csv
import importlib
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
    """Drive drops desktop.ini into .git/, which breaks ref parsing: clear it first."""
    for p in (ROOT / ".git").rglob("desktop.ini"):
        p.unlink(missing_ok=True)
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
        return round(config.P_EXH_MIN_MPA * 10) <= v < o["Pm"]
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
        # A winner exactly on a constraint is pinned on that side; one with room
        # short of a full step is still on a free edge and extends into that room.
        lo = [v for v in span if v < w[f]]
        hi = [v for v in span if v > w[f]]
        m = MIN_STEP[f]
        edge_lo = not lo and valid(f, w[f] - m, w, L)
        edge_hi = not hi and valid(f, w[f] + m, w, L)
        new = {w[f]}
        for on, sign in ((edge_lo, -1), (edge_hi, 1)):
            if not on:
                continue
            ok = [v for v in (w[f] + sign * s, w[f] + 2 * sign * s) if valid(f, v, w, L)]
            if not ok:   # less than one step to the constraint: last allowed value + midpoint
                room = [w[f] + sign * k for k in range(m, s + 1, m) if valid(f, w[f] + sign * k, w, L)]
                far = room[-1]
                mid = w[f] + sign * ((abs(far - w[f]) // 2) // m * m)
                ok = [v for v in (mid, far) if v != w[f]]
            new |= set(ok)
        at_bound = (not hi and not edge_hi) or (not lo and not edge_lo)
        if not (edge_lo or edge_hi or at_bound):
            h =(s // 2) // m * m
            if m <= h < s:
                new |= {v for v in (w[f] - h, w[f] + h) if valid(f, v, w, L)}
        res[f] = dict(step=s, edge_lo=edge_lo, edge_hi=edge_hi, values=sorted(new))
    return L, w, res


def tracked(snap):
    """{label: ID} of every winner the refinement follows."""
    t = {f"payout_L{L}": snap["best"][str(L)]["ID"] for L in REFINED_LAYOUTS
         if str(L) in snap["best"]}
    t.update(topsis=snap["topsis"]["ID"], knee=snap["knee"]["ID"],
             topsis_strict=snap["topsis_strict"]["ID"])
    return t


def propose(snap, input_ids, rnd):
    """Grids for the next round around each tracked winner (one grid per distinct ID)."""
    lm = lines(input_ids)
    grids = {}
    for k, id_ in enumerate(sorted(set(tracked(snap).values()))):
        L, w, res = analyse(id_, lm)
        g = dict(layout=L, T_turb=[w["Tt"]])
        n = 1
        for f, r in res.items():
            g[FIELD_AXIS[f]] = r["values"]
            n *= len(r["values"])
        if n > 1:
            grids[f"W{rnd}_L{L}{'abcdefgh'[k]}"] = g
    return grids


def append_grids(grids, rnd):
    text = [f"\n# refinement round {rnd} (core/refine.py)", "GRIDS.update({"]
    for name, g in grids.items():
        body = ", ".join(f"{k}={v!r}" for k, v in g.items())
        text.append(f"    {name!r}: dict({body}),")
    text.append("})\n")
    with open(ROOT / "grids.py", "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(text))


# ------------------------------------------------------------ calibration --
def recalibrate():
    """If the most efficient feasible layout-2 design (T_turb 500) changed, write the
    new M0 into config.py. Returns a dict describing old and new reference."""
    import config
    from core.calibrate import calibration, write_config
    importlib.reload(config)
    c = calibration()
    rec = dict(old_ID=config.M0_REF_ID, old_M0=config.M0_T, new_ID=c["ID"],
               new_M0=round(c["M0_t"], 3), eta=c["eta"], changed=c["ID"] != config.M0_REF_ID)
    if rec["changed"]:
        write_config(c)
        importlib.reload(config)
        print(f"RECALIBRATED: {rec['old_ID']} (M0 {rec['old_M0']}) -> {rec['new_ID']} "
              f"(eta {c['eta']:.8f}, M0 {rec['new_M0']})", flush=True)
    else:
        print(f"calibration unchanged: {rec['new_ID']} (M0 {rec['old_M0']})", flush=True)
    return rec


# --------------------------------------------------------------- snapshot --
def snapshot():
    import config
    importlib.reload(config)
    econ, strict = read("results_econ.csv"), read("results_econ_strict.csv")
    lm = lines([r["ID"] for r in read("inputs.csv")])
    f = float
    pick = lambda r: dict(ID=r["ID"], eta=f(r["eta"]), mass=f(r["mass_t"]),
                          payout=f(r["payout_usd"]))
    best = {}
    for L in sorted({r["layout"] for r in econ}, key=int):
        best[L] = pick(max((r for r in econ if r["layout"] == L), key=lambda r: f(r["payout_usd"])))
    snap = dict(feasible=len(econ),
                attempted=len(read("results_raw.csv")) + len(read("infeasible.csv")),
                M0=config.M0_T, M0_ref=config.M0_REF_ID, best=best,
                topsis=pick(next(r for r in econ if r["topsis_rank"] == "1")),
                knee=pick(next(r for r in econ if r["knee"] == "1")),
                topsis_strict=pick(next(r for r in strict if r["topsis_rank"] == "1")))
    edges = {}
    for id_ in sorted(set(tracked(snap).values())):
        _, _, res = analyse(id_, lm)
        edges[id_] = [f"{k}{'-' if r['edge_lo'] else '+'}" for k, r in res.items()
                      if r["edge_lo"] or r["edge_hi"]]
    snap["edges"] = edges
    return snap


def conditions(prev, cur):
    c3 = not any(cur["edges"].values())
    if prev is None or "topsis_strict" not in prev:
        return dict(payout=False, topsis=False, edges=c3)
    rel = lambda a, b: abs(a - b) / abs(b) if b else float("inf")
    c1 = all(rel(cur["best"][str(L)]["payout"], prev["best"][str(L)]["payout"]) < 5e-4
             for L in REFINED_LAYOUTS if str(L) in cur["best"] and str(L) in prev["best"])
    c2 = all(rel(cur[k]["payout"], prev[k]["payout"]) < 1e-3 and
             rel(cur[k]["mass"], prev[k]["mass"]) < 1e-3 for k in ("topsis", "topsis_strict"))
    return dict(payout=c1, topsis=c2, edges=c3)


# ---------------------------------------------------------------- report --
def report(rounds, caps=""):
    yn = lambda b: "yes" if b else "no"
    cell = lambda d: f"{d['ID']} ({d['payout']/1e6:.3f} M$, {d['mass']:.2f} t)"
    legacy = [r for r in rounds if "topsis_strict" not in r["snap"]]
    new = [r for r in rounds if "topsis_strict" in r["snap"]]
    md = ["# Refinement convergence (branch wager)", "",
          "Main ranking excludes layout 1 (RANK_EXCLUDE_LAYOUTS). Strict ranking also removes every "
          "design with a compressor inlet below 7.7 MPa (all of layout 6). Tracked winners: best "
          "payout in layouts 2, 3, 5, 6; TOPSIS #1 and knee (main); TOPSIS #1 (strict).", "",
          "Stop when, against the previous round: best payout per layout (2, 3, 5, 6) moves < 0.05 %; "
          "TOPSIS #1 payout and mass (main and strict) move < 0.1 %; no tracked winner on a free "
          "(non-constraint) grid edge. Otherwise stop at the round or time limit.", "",
          f"**Caps used in this run:** {caps or '(not recorded)'}", "",
          "## Rounds", "",
          "| round | points added | total feasible | M0 used t (reference) | best payout L2 / L3 / L5 / L6 (M$) "
          "| TOPSIS #1 main | knee main | TOPSIS #1 strict | payout < 0.05 % | TOPSIS < 0.1 % "
          "| no free edge | wall min |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in new:
        s, c = r["snap"], r["cond"]
        recal = r.get("recal") or {}
        m0 = f"{s['M0']} ({s['M0_ref']})" + (
            f" **recalibrated from {recal['old_M0']} ({recal['old_ID']})**" if recal.get("changed") else "")
        bp = " / ".join(f"{s['best'][str(L)]['payout']/1e6:.3f}" for L in REFINED_LAYOUTS
                        if str(L) in s["best"])
        md.append(f"| {r['round']}{r.get('label', '')} | {r['added']} | {s['feasible']} | {m0} | {bp} | "
                  f"{cell(s['topsis'])} | {cell(s['knee'])} | {cell(s['topsis_strict'])} | "
                  f"{yn(c['payout'])} | {yn(c['topsis'])} | {yn(c['edges'])} | {r['minutes']:.1f} |")
    md += ["", "## Best payout design per layout", "",
           "| round | layout | ID | eta | mass t | payout M$ |", "|---|---|---|---|---|---|"]
    for r in new:
        for L, b in r["snap"]["best"].items():
            md.append(f"| {r['round']} | {L} | {b['ID']} | {b['eta']:.5f} | {b['mass']:.2f} | "
                      f"{b['payout']/1e6:.3f} |")
    md += ["", "## Tracked winners on a free grid edge (after each round)", "",
           "| round | ID | free edges |", "|---|---|---|"]
    for r in new:
        for id_, e in r["snap"]["edges"].items():
            md.append(f"| {r['round']} | {id_} | {', '.join(e) if e else '-'} |")
    if legacy:
        md += ["", "## Earlier rounds (layout 1 still ranked, no strict ranking)", "",
               "| round | points added | total feasible | TOPSIS #1 (with L1) | knee (with L1) |",
               "|---|---|---|---|---|"]
        for r in legacy:
            s = r["snap"]
            md.append(f"| {r['round']} | {r['added']} | {s['feasible']} | {cell(s['topsis'])} | "
                      f"{s['knee']['ID']} |")
    last = rounds[-1]
    md += ["", "## Verdict", "", last.get("verdict", "(running)"), ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "convergence.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    i = md.index("## Rounds")
    print("\n".join(md[i + 2:i + 4 + len(new)]), flush=True)


def commit(msg):
    git("add", "-A")
    git("commit", "-q", "-m", f"{msg}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
        check=False)
    git("push", "-q", "-u", "origin", "wager", check=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-rounds", type=int, default=10)
    ap.add_argument("--minutes", type=float, default=240)
    args = ap.parse_args(argv)
    t0 = time.time()
    end = t0 + args.minutes * 60
    # solve_points takes a same-day HH:MM deadline: only pass one when the end really
    # falls later today; otherwise there is effectively no time cap.
    same_day = time.localtime(end)[:3] == time.localtime(t0)[:3]
    deadline = time.strftime("%H:%M", time.localtime(end)) if same_day else None
    uncapped = deadline is None and args.max_rounds >= 1000
    caps = ("none (effectively uncapped: --max-rounds "
            f"{args.max_rounds}, --minutes {args.minutes:g}; no solve deadline)") if uncapped else (
            f"--max-rounds {args.max_rounds}, --minutes {args.minutes:g}"
            f" (solve deadline {deadline or 'none'})")
    print(f"refine: start {time.strftime('%H:%M')}; caps: {caps}", flush=True)

    rounds = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else []
    base = dict(round=rounds[-1]["round"] if rounds else 0, added=0, snap=snapshot(),
                minutes=0.0, label=" (start of this run)")
    base["cond"] = conditions(None, base["snap"])
    if rounds and "topsis_strict" in rounds[-1]["snap"]:
        base = rounds[-1]                         # resume a run with the current criteria
    else:
        rounds.append(base)
    first = base["round"] + 1
    verdict = None
    for rnd in range(first, first + args.max_rounds):
        if time.time() >= end:
            verdict = (f"NOT converged: stopped at the {args.minutes:g}-minute limit before round "
                       f"{rnd}. Unmet after round {rnd - 1}: "
                       f"{', '.join(k for k, v in rounds[-1]['cond'].items() if not v) or 'none'}.")
            break
        prev = rounds[-1]["snap"]
        grids = ROUND1 if rnd == 1 else propose(prev, [r["ID"] for r in read("inputs.csv")], rnd)
        if not grids:
            verdict = f"Round {rnd}: no further refinement possible at ID resolution."
            break
        before = prev["attempted"]
        append_grids(grids, rnd)
        try:
            run("core.make_inputs")
            run("core.solve_points", "--workers", "8", *(["--deadline", deadline] if deadline else []))
            recal = recalibrate()
            run("core.economics")
            run("core.export_states")
            run("core.plots")
            run("core.summary")
            snap = snapshot()
        except Exception as e:             # a real error (non-zero exit, exception): stop here
            code = getattr(e, "returncode", None)
            what = "STUCK (no point finished for 60 min)" if code == 3 else f"{type(e).__name__}: {e}"
            verdict = f"ERROR in round {rnd}: {what}. Stopped; NOT converged."
            print(verdict, flush=True)
            rounds[-1]["verdict"] = verdict
            STATE.write_text(json.dumps(rounds, indent=1), encoding="utf-8", newline="\n")
            report(rounds, caps)
            commit(f"wager: refinement stopped with an error in round {rnd}")
            raise SystemExit(1)
        cond = conditions(prev, snap)
        rounds.append(dict(round=rnd, added=snap["attempted"] - before, snap=snap, cond=cond,
                           recal=recal, minutes=(time.time() - t0) / 60))
        unmet = ", ".join(k for k, v in cond.items() if not v)
        if all(cond.values()):
            verdict = (f"CONVERGED after round {rnd}: all three stop conditions hold "
                       f"against round {rnd - 1}.")
        elif time.time() >= end:
            verdict = (f"NOT converged: the {args.minutes:g}-minute limit was reached during "
                       f"round {rnd}. Unmet: {unmet}.")
        elif rnd == first + args.max_rounds - 1:
            verdict = f"NOT converged after {args.max_rounds} rounds (round {rnd}). Unmet: {unmet}."
        rounds[-1]["verdict"] = verdict or "(continuing)"
        STATE.write_text(json.dumps(rounds, indent=1), encoding="utf-8", newline="\n")
        report(rounds, caps)
        commit(f"wager: refinement round {rnd}")
        if verdict:
            break
    if verdict and rounds[-1].get("verdict") != verdict:
        rounds[-1]["verdict"] = verdict
        STATE.write_text(json.dumps(rounds, indent=1), encoding="utf-8", newline="\n")
        report(rounds, caps)
        commit("wager: convergence verdict")
    print(f"\nrefine done: {verdict}", flush=True)


if __name__ == "__main__":
    main()
