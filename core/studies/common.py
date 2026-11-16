"""core/studies/common.py: shared machinery for the extended studies.

* solve_task: one design under modified settings (cooler pinch, pressure drop,
  coolant pressure, physical overrides such as T_in / T_turb / P_high, and
  optionally recuperators frozen at a fixed absolute UA). Same feasibility
  checks as helpers/checks.py.
* sweep: resumable parallel run of many tasks through core.solve_points'
  scheduler (per-point timeout, stall detection), one CSV row per finished task.
* economics, rankings, calibration and Pareto plots for a set of raw rows.

Studies write only to out/studies/<name>/.
"""
import csv
import math
from pathlib import Path

import config
from helpers.builders import BUILDERS, ROLES
from helpers.checks import COLUMNS as RAW_COLUMNS
from helpers.checks import TOL, _stage1_reasons
from helpers.ids import parse_id, physical

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
STUDIES = ROOT / "out" / "studies"

NAMED = {
    "Reference": "L2_Ph200_Pl077_T340_Tt500",
    "Main TOPSIS #1": "L6_Ph200_T335_Tt500_Pm079_Pe037_x038",
    "Strict TOPSIS #1": "L3_Ph200_Pl077_T325_Tt500_x046",
    "Strict knee": "L3_Ph200_Pl077_T330_Tt500_x043",
    "Highest payout": "L3_Ph200_Pl077_T320_Tt500_x036",
    "Submitted design": "L3_Ph200_Pl077_T330_Tt500_x040",
}

BASE = dict(COOLER_PINCH_K=config.COOLER_PINCH_K, PRESSURE_DROP=config.PRESSURE_DROP,
            COOLANT_P_PA=config.COOLANT_P_PA)
EXTRA_COLUMNS = ["key", "mdot_kg_s", "W_net_MW", "water_flow_kg_s", "T_turb_C", "T_in_C",
                 "P_high_MPa", "rho_comp_in", "cooler_pinch_set_K"]
COLUMNS = RAW_COLUMNS + EXTRA_COLUMNS
FAIL_COLUMNS = ["key", "ID", "reason"]


# ------------------------------------------------------------------ solve --
def _apply(opts):
    for k, v in BASE.items():
        setattr(config, k, v)
    for k, v in opts.items():
        setattr(config, k, v)


def _case(base_id, ph, coolant, freeze=None, mdot=None):
    from cycles import UAperFlow
    L = parse_id(base_id)["layout"]
    nodes = config.COOLER_NODES if coolant is True else coolant
    case = BUILDERS[L](base_id, ph, nodes)
    if freeze:
        case = case.with_(params={b: {"spec": UAperFlow(ua / mdot)} for b, ua in freeze.items()})
    return case


def _row(key, base_id, ph, r):
    from CoolProp.CoolProp import PropsSI
    L = parse_id(base_id)["layout"]
    roles, m = ROLES[L], r.metrics
    mdot = m["mdot"]
    ua, pinch = {}, {}
    for role in ("recup_1", "recup_2"):
        b = r.blocks.get(roles.get(role))
        ua[role] = b["UA_per_flow"] * mdot / 1e3 if b else None
        pinch[role] = b["pinch"] if b else None
    for role in ("cooler_1", "cooler_2"):
        b = r.blocks.get(roles.get(role))
        ua[role] = b["coolant_UA_per_flow"] * mdot / 1e3 if b else None
        pinch[role] = b["coolant_pinch"] if b else None
    P_base = ph["P_mid_MPa"] if L == 6 else ph["P_low_MPa"]
    eta = m["eta_th"]
    eta_c = 1 - (ph["T_in_C"] + 273.15) / (ph["T_turb_C"] + 273.15)
    water = sum(b.get("coolant_flow", 0.0) for b in r.blocks.values()
                if b.get("kind") == "cooler") * mdot
    s1 = r.streams["s1"]
    row = {"ID": base_id, "pressure_ratio": ph["P_high_MPa"] / P_base, "split": ph["split"],
           "eta": eta, "UA_recup_1": ua["recup_1"], "UA_recup_2": ua["recup_2"],
           "UA_cooler_1": ua["cooler_1"], "UA_cooler_2": ua["cooler_2"],
           "UA_total": sum(v for v in ua.values() if v is not None),
           "pinch_recup_1": pinch["recup_1"], "pinch_recup_2": pinch["recup_2"],
           "pinch_cooler_1": pinch["cooler_1"], "pinch_cooler_2": pinch["cooler_2"],
           "eta_carnot": eta_c, "eta_second_law": eta / eta_c,
           "key": key, "mdot_kg_s": mdot, "W_net_MW": m["W_net"] / 1e6,
           "water_flow_kg_s": water, "T_turb_C": ph["T_turb_C"], "T_in_C": ph["T_in_C"],
           "P_high_MPa": ph["P_high_MPa"],
           "rho_comp_in": PropsSI("D", "P", s1["P"], "T", s1["T"], "CO2"),
           "cooler_pinch_set_K": config.COOLER_PINCH_K}
    return {k: ("" if v is None else (v if isinstance(v, str) else format(v, ".8g")))
            for k, v in row.items()}


def solve_task(task):
    """task = (key, base_id, overrides, opts, freeze):
         overrides: tuple of (physical key, value), e.g. (("T_in_C", 33.0),)
         opts:      tuple of (config attribute, value) for this solve
         freeze:    tuple of (block id, absolute UA in W/K) -> recuperators held at
                    that UA (fixed-point on mdot), or () for the normal specs.
    Returns (task, "feasible", row) or (task, "infeasible", reason). Never raises."""
    from cycles import solve
    key, base_id, overrides, opts, freeze = task
    try:
        _apply(dict(opts))
        ph = {**physical(parse_id(base_id)), **dict(overrides)}
        freeze = dict(freeze)
        mdot = None
        if freeze:   # absolute UA fixed: iterate UA/mdot until mdot settles
            mdot = solve(_case(base_id, ph, None)).metrics["mdot"]
            for _ in range(30):
                r1 = solve(_case(base_id, ph, None, freeze, mdot))
                if not r1.ok:
                    break
                new = r1.metrics["mdot"]
                done = abs(new - mdot) <= 1e-6 * mdot
                mdot = new
                if done:
                    break
            else:
                return task, "infeasible", "not_solved: frozen-UA mass flow did not settle"
        case1 = _case(base_id, ph, None, freeze, mdot)
        r1 = solve(case1)
        if not r1.ok:
            return task, "infeasible", f"not_solved: {'; '.join(map(str, r1.flags))}"
        reasons = _stage1_reasons(case1, r1)
        if reasons and not freeze:
            return task, "infeasible", "; ".join(reasons)
        r2 = solve(_case(base_id, ph, True, freeze, mdot))
        if not r2.ok:
            return task, "infeasible", f"not_solved: {'; '.join(map(str, r2.flags))}"
        row = _row(key, base_id, ph, r2)
        if freeze:   # off-design proxy: report, do not filter
            row["key"] = key
            row["flags"] = "; ".join(reasons)
        return task, "feasible", row
    except Exception as exc:                        # a sweep must survive any point
        return task, "infeasible", f"error: {type(exc).__name__}: {exc}"


def task(key, base_id, overrides=None, opts=None, freeze=None):
    return (key, base_id, tuple(sorted((overrides or {}).items())),
            tuple(sorted((opts or {}).items())), tuple(sorted((freeze or {}).items())))


# ------------------------------------------------------------------ sweep --
def read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sweep(tasks, folder, stem, columns=COLUMNS, workers=None, point_timeout=None, stall=None):
    """Solve every task not already in folder/<stem>.csv or <stem>_infeasible.csv.
    Resumable; returns (feasible rows, infeasible rows) over all tasks."""
    from core import solve_points as sp
    folder.mkdir(parents=True, exist_ok=True)
    ok_path, bad_path = folder / f"{stem}.csv", folder / f"{stem}_infeasible.csv"
    done = sp._repair(ok_path, columns) | sp._repair(bad_path, FAIL_COLUMNS)
    todo = [t for t in tasks if t[0] not in done]
    print(f"[{folder.name}/{stem}] {len(todo)} to solve, {len(tasks) - len(todo)} already done",
          flush=True)
    if todo:
        ok_fh, ok_w = sp._open(ok_path, columns)
        bad_fh, bad_w = sp._open(bad_path, FAIL_COLUMNS)
        n = 0
        try:
            for t, status, payload in sp._run_points(
                    todo, min(workers or config.SWEEP_WORKERS, len(todo)),
                    point_timeout or sp.POINT_TIMEOUT_S, stall or sp.STALL_S, work=solve_task):
                if status == "feasible":
                    ok_w.writerow([payload.get(c, "") for c in columns])
                    ok_fh.flush()
                else:
                    bad_w.writerow([t[0], t[1], payload])
                    bad_fh.flush()
                n += 1
                if n % 100 == 0 or n == len(todo):
                    print(f"  {n}/{len(todo)}", flush=True)
        finally:
            ok_fh.close()
            bad_fh.close()
    keys = {t[0] for t in tasks}
    return ([r for r in read_csv(ok_path) if r["key"] in keys],
            [r for r in read_csv(bad_path) if r["key"] in keys])


# -------------------------------------------------------------- economics --
def calibrate(raw):
    """(reference row, M0) from the most efficient feasible layout-2 design at 500 C."""
    l2 = [r for r in raw if parse_id(r["ID"])["layout"] == 2
          and parse_id(r["ID"])["Tt"] == round(config.T_TURBINE_MAX_C)]
    ref = max(l2, key=lambda r: float(r["eta"]))
    m0 = (config.BASELINE_MASS_T - config.KG_PER_KW_K * float(ref["UA_recup_1"]) / 1000
          - config.COOLER_KG_PER_KW_K * float(ref["UA_cooler_1"]) / 1000)
    return ref, m0


def econ(raw, m0, ref_id=None, lifetime_years=None):
    """(main rows, strict rows) with M0 = m0; config.M0_REF_ID set for the plots."""
    from core.economics import compute
    config.M0_T = m0
    if ref_id:
        config.M0_REF_ID = ref_id
    return compute(raw, lifetime_years), compute(raw, lifetime_years, strict=True)


def winners(rows):
    """knee, TOPSIS #1, best payout per layout, front size."""
    rk = [r for r in rows if r["topsis_rank"] != ""]
    best = {}
    for r in rows:
        L = r["layout"]
        if L not in best or r["payout_usd"] > best[L]["payout_usd"]:
            best[L] = r
    return dict(knee=next(r for r in rk if r["knee"] == 1),
                topsis=next(r for r in rk if r["topsis_rank"] == 1),
                best=dict(sorted(best.items())), front=sum(r["pareto"] == 1 for r in rk))


def as_strings(rows):
    from core.economics import _fmt
    return [{k: _fmt(v) for k, v in r.items()} for r in rows]


def pareto_png(rows, folder, name, ylabel="10-year payout (M$)"):
    """Pareto figure in the core/plots.py style (commit 96d7df2)."""
    from core.plots import pareto_plot
    rel = (folder / name).relative_to(ROOT / "out")
    return pareto_plot(as_strings(rows), str(rel).replace("\\", "/"), ylabel)


def baseline():
    """Baseline (main, strict) econ rows, as numbers, from data/."""
    raw = read_csv(DATA / "results_raw.csv")
    ref, m0 = calibrate(raw)
    return raw, ref, m0


# ---------------------------------------------------------------- report --
def table(head, rows):
    out = ["| " + " | ".join(map(str, head)) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def fnum(v, fmt):
    if v in ("", None):
        return ""
    v = float(v)
    return "" if math.isnan(v) else format(v, fmt)


def design_text(id_):
    p = physical(parse_id(id_))
    s = f"layout {parse_id(id_)['layout']}, T_in {p['T_in_C']:g} C"
    if p["split"] is not None:
        s += f", x {p['split']:.2f}"
    if p["P_exh_MPa"] is not None:
        s += f", P_exh {p['P_exh_MPa']:g} MPa"
    return s


def write_summary(folder, lines):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"-> {(folder / 'summary.md').relative_to(ROOT)}", flush=True)
