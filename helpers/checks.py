"""helpers/checks.py: one point ID -> feasible row or infeasible reason.

Stage 1 solves the cycle without the coolant side (fast) and applies the
brief's constraints. Stage 2, for feasible points only, re-solves with the
coolant side to get cooler UA and water pinch.
"""
import config
from cycles import solve
from helpers.builders import ROLES, build
from helpers.ids import parse_id, physical

TOL = 1e-6   # a point exactly on a limit passes

COLUMNS = ["ID", "pressure_ratio", "split", "eta",
           "UA_recup_1", "UA_recup_2", "UA_cooler_1", "UA_cooler_2", "UA_total",
           "pinch_recup_1", "pinch_recup_2", "pinch_cooler_1", "pinch_cooler_2",
           "eta_carnot", "eta_second_law"]


def _fmt(v):
    return "" if v is None else format(v, ".8g")


def _compressor_inlets(case):
    """[(block id, inlet stream id, is_main)] for every compressor.
    The main compressor is the one fed by cooler_1."""
    roles = ROLES[parse_id(case.name)["layout"]]
    main_feed = case.layout.node(roles["cooler_1"]).outlet_streams()
    out = []
    for n in case.layout.nodes:
        if n.type == "compressor":
            sid = n.inlet_streams()[0]
            out.append((n.id, sid, sid in main_feed))
    return out


def _stage1_reasons(case, r):
    reasons = []
    hx = [b["pinch"] for b in r.blocks.values() if b.get("kind") == "heat_exchanger"]
    if hx and min(hx) < config.RECUP_PINCH_MIN_K - TOL:
        reasons.append(f"recup_pinch<5K ({min(hx):.4f})")

    T_low = P_low = False
    for _, sid, is_main in _compressor_inlets(case):
        s = r.streams[sid]
        if s["T"] - 273.15 < config.T_INLET_MIN_C - TOL:
            T_low = True
        if (config.STRICT_INLET_PRESSURE or is_main) and \
                s["P"] / 1e6 < config.P_INLET_MIN_MPA - TOL:
            P_low = True
    if T_low:
        reasons.append("T_inlet<32C")
    if P_low:
        reasons.append("P_inlet<7.7MPa")

    if max(s["P"] for s in r.streams.values()) / 1e6 > config.P_MAX_MPA + TOL:
        reasons.append("P_max>20MPa")
    T_turb = [r.streams[n.inlet_streams()[0]]["T"] - 273.15
              for n in case.layout.nodes if n.type == "turbine"]
    if T_turb and max(T_turb) > config.T_TURBINE_MAX_C + TOL:
        reasons.append("T_turbine>500C")
    for n in case.layout.nodes:
        if n.type == "splitter":
            x = case.params[n.id]["x"]
            if not (config.SPLIT_MIN + TOL < x <= config.SPLIT_MAX + TOL):
                reasons.append("split_out_of_range")
    return reasons


def _row(id_, r):
    ph = physical(parse_id(id_))
    layout = parse_id(id_)["layout"]
    roles = ROLES[layout]
    m = r.metrics
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

    P_base = ph["P_mid_MPa"] if layout == 6 else ph["P_low_MPa"]
    eta = m["eta_th"]
    eta_c = 1 - (ph["T_in_C"] + 273.15) / (ph["T_turb_C"] + 273.15)
    row = {
        "ID": id_,
        "pressure_ratio": ph["P_high_MPa"] / P_base,
        "split": ph["split"],
        "eta": eta,
        "UA_recup_1": ua["recup_1"], "UA_recup_2": ua["recup_2"],
        "UA_cooler_1": ua["cooler_1"], "UA_cooler_2": ua["cooler_2"],
        "UA_total": sum(v for v in ua.values() if v is not None),
        "pinch_recup_1": pinch["recup_1"], "pinch_recup_2": pinch["recup_2"],
        "pinch_cooler_1": pinch["cooler_1"], "pinch_cooler_2": pinch["cooler_2"],
        "eta_carnot": eta_c,
        "eta_second_law": eta / eta_c,
    }
    return {k: (v if k == "ID" else _fmt(v)) for k, v in row.items()}


def evaluate(id_):
    """("feasible", row_dict) or ("infeasible", reason_str). Never raises."""
    try:
        case1 = build(id_, coolant=False)
        r1 = solve(case1)
        if not r1.ok:
            return "infeasible", f"not_solved: {'; '.join(map(str, r1.flags))}"
        reasons = _stage1_reasons(case1, r1)
        if reasons:
            return "infeasible", "; ".join(reasons)

        r2 = solve(build(id_, coolant=True))
        if not r2.ok:
            return "infeasible", f"not_solved: {'; '.join(map(str, r2.flags))}"
        e1, e2 = r1.metrics["eta_th"], r2.metrics["eta_th"]
        assert abs(e2 - e1) <= 1e-9 * abs(e1), f"stage 2 eta {e2} != stage 1 eta {e1}"
        return "feasible", _row(id_, r2)
    except Exception as exc:                       # a sweep must survive any point
        return "infeasible", f"error: {type(exc).__name__}: {exc}"
