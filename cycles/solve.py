"""solve(case) -> Result.

The orchestrator.  It runs the four passes in order and never contains
layout-specific logic:

    1  pressure  every stream pressure, from anchors and invertible relations
    2  flow      every stream's share of the total mass flow
    3  ordering  evaluation order, and which stream to tear if there is a loop
    4  tear      iterate the loop to a fixed point (skipped when acyclic)

then scales to the requested plant size, runs the checks, and packs a Result.
"""
from __future__ import annotations

from .blocks import fixed_outlets, get, multi_in, multi_out
from .numerics.roots import ConvergenceError
from .passes import flow as flow_pass
from .passes import ordering, tear
from .passes import pressure as pressure_pass
from .physics import exergy as exergy_mod
from .properties import make_props
from .result import Result
from .specs import MassFlow, ThermalPower
from .stream import Stream

ADIABATIC = {"compressor", "turbine"}


def _port_ids(node, port):
    v = node.inlets.get(port, node.outlets.get(port))
    return v if isinstance(v, (list, tuple)) else [v]


def _initial_tear_guess(case, props, P, tears):
    """A domain-informed starting point: a quarter of the way up the cycle's
    temperature span.  Successive substitution is forgiving, but a guess in
    the wrong phase region is not."""
    p = props(case.fluid)
    T_lo = min(st["T"] for st in case.boundary.values())
    heater_T = [prm["T_out"] for bid, prm in case.params.items()
                if get(case.layout.node(bid).type).TYPE == "heater" and "T_out" in prm]
    T_hi = max(heater_T) if heater_T else T_lo * 2.0
    T_guess = T_lo + 0.25 * (T_hi - T_lo)
    return {sid: p.h_pt(P[sid], T_guess) for sid in tears}


def solve(case) -> Result:
    layout = case.layout
    num = case.numerics
    flags = []

    fluids = {case.fluid}
    for prm in case.params.values():
        if "coolant_fluid" in prm:
            fluids.add(prm["coolant_fluid"])
    props = make_props(sorted(fluids), case.backend)

    # --- passes 1 and 2 ---------------------------------------------------
    try:
        P = pressure_pass.resolve(case)
        F = flow_pass.resolve(case)
    except Exception as exc:
        return Result(case=case, ok=False, flags=[f"{type(exc).__name__}: {exc}"])

    # --- seeded streams ---------------------------------------------------
    # Two kinds of state are known before any block runs: the boundary stream
    # the case pins, and any outlet a block fixes from its own parameters (a
    # heater told its outlet temperature).  Seeding the second kind is what
    # lets the expansion branch start before the recuperator network closes.
    pf = props(case.fluid)
    boundary = {}
    for sid, state in case.boundary.items():
        boundary[sid] = Stream(case.fluid, P[sid],
                               pf.h_pt(P[sid], state["T"]), F[sid])

    for node in layout.nodes:
        mod = get(node.type)
        for port, state in fixed_outlets(mod, case.params.get(node.id, {})).items():
            for sid in _port_ids(node, port):
                boundary.setdefault(
                    sid, Stream(case.fluid, P[sid],
                                pf.h_pt(P[sid], state["T"]), F[sid]))

    # --- pass 3 -----------------------------------------------------------
    sched = ordering.build(layout, boundary)

    # --- one sweep through the blocks -------------------------------------
    # `diagnostics` is off while the tear loop converges: profiles, pinches
    # and UA cost a hundred property calls per exchanger and nobody reads
    # them until the loop has settled.  The final sweep turns them on.
    hints = {}

    def evaluate_once(guess, diagnostics=False):
        streams = dict(boundary)
        for sid, h in guess.items():
            streams[sid] = Stream(case.fluid, P[sid], h, F[sid])

        extras, produced = {}, {}
        for bid in sched.order:
            node = layout.node(bid)
            mod = get(node.type)
            params = case.params.get(bid, {})

            inlets = {}
            for port in mod.INLETS:
                ids = _port_ids(node, port)
                vals = [streams[s] for s in ids]
                inlets[port] = vals if port in multi_in(mod) else vals[0]

            P_out = {port: P[_port_ids(node, port)[0]] for port in mod.OUTLETS}

            outs, ex = mod.evaluate(inlets, P_out, params, props,
                                    block_id=bid, diagnostics=diagnostics,
                                    hint=hints.get(bid))
            extras[bid] = ex
            hints[bid] = ex

            for port, val in outs.items():
                ids = _port_ids(node, port)
                vals = val if port in multi_out(mod) else [val]
                for sid, st in zip(ids, vals):
                    if sid in guess:
                        produced[sid] = st.h      # tear: record, do not overwrite
                    else:
                        streams[sid] = st
        return (streams, extras), produced

    # --- pass 4 -----------------------------------------------------------
    guesses = _initial_tear_guess(case, props, P, sched.tears)
    try:
        (streams, _), iters, residual = tear.solve(
            evaluate_once, sched.tears, guesses, num)
        # one more sweep at full resolution, from the converged state, so the
        # Result carries real profiles, pinches and UA values
        final_guess = {sid: streams[sid].h for sid in sched.tears}
        (streams, extras), _ = evaluate_once(final_guess, diagnostics=True)
    except ConvergenceError as exc:
        return Result(case=case, ok=False, flags=[str(exc)],
                      schedule={"order": sched.order, "tears": sched.tears})
    except Exception as exc:
        return Result(case=case, ok=False, flags=[f"{type(exc).__name__}: {exc}"],
                      schedule={"order": sched.order, "tears": sched.tears})

    for ex in extras.values():
        flags.extend(ex.get("flags", []))

    # --- cycle metrics ----------------------------------------------------
    w_t = sum(e["w_total"] for e in extras.values() if e["kind"] == "turbine")
    w_c = sum(e["w_total"] for e in extras.values() if e["kind"] == "compressor")
    q_in = sum(e["q_total"] for e in extras.values() if e["kind"] == "heater")
    q_out = sum(e["q_total"] for e in extras.values() if e["kind"] == "cooler")
    w_net = w_t - w_c

    # Coolant-pump work, summed over every cooler that was given a circuit.
    # It is an auxiliary load rather than cycle work, so it stays out of
    # w_net and out of eta_th -- those remain comparable with any textbook
    # figure -- and is subtracted separately, which is what a plant sees.
    w_pump = sum(e.get("pump_w_total", 0.0) for e in extras.values()
                 if e["kind"] == "cooler")


    if q_in <= 0.0:
        return Result(case=case, ok=False,
                      flags=flags + ["no heat input: q_in <= 0"])

    eta = w_net / q_in
    if isinstance(case.size, ThermalPower):
        mdot = case.size.value / q_in
    elif isinstance(case.size, MassFlow):
        mdot = case.size.value
    else:
        mdot = float("nan")

    # --- margins and heat-exchanger roll-up -------------------------------
    p = pf
    cold = min(streams.values(), key=lambda s: p.T_ph(s.P, s.h))
    T_min = p.T_ph(cold.P, cold.h)
    T_crit, P_crit = p.T_crit, p.P_crit

    hxs = {k: v for k, v in extras.items() if v["kind"] == "heat_exchanger"}
    pinches = [v["pinch"] for v in hxs.values()]
    ua_total = sum(v["UA_per_flow"] for v in hxs.values()
                   if v["UA_per_flow"] == v["UA_per_flow"])

    metrics = {
        "eta_th": eta,
        "eta_net_of_pump": (w_net - w_pump) / q_in,
        "w_turbine": w_t, "w_compressor": w_c, "w_net": w_net,
        "w_pump": w_pump, "w_net_of_pump": w_net - w_pump,
        "q_in": q_in, "q_out": q_out,
        "bwr": w_c / w_t if w_t else float("nan"),
        "mdot": mdot,
        "W_turbine": w_t * mdot, "W_compressor": w_c * mdot,
        "W_net": w_net * mdot, "Q_in": q_in * mdot, "Q_out": q_out * mdot,
        "W_pump": w_pump * mdot, "W_net_of_pump": (w_net - w_pump) * mdot,
        "UA_total": ua_total * mdot, "UA_per_flow_total": ua_total,
        "pinch_min": min(pinches) if pinches else float("nan"),
        "T_min": T_min, "P_min": cold.P,
        "T_crit_margin": T_min - T_crit,
        "P_crit_margin": cold.P - P_crit,
        "P_max": max(P.values()),
        "recuperation_ratio": sum(v["Q"] for v in hxs.values()) / q_in if q_in else 0.0,
    }

    # --- checks -----------------------------------------------------------
    closure = q_in - q_out - w_net
    s_gen = {}
    for bid, e in extras.items():
        node = layout.node(bid)
        if node.type in ADIABATIC:
            a = streams[_port_ids(node, "in")[0]]
            b = streams[_port_ids(node, "out")[0]]
            s_gen[bid] = a.flow * (p.s_ph(b.P, b.h) - p.s_ph(a.P, a.h))
        elif node.type == "heat_exchanger":
            hi = streams[_port_ids(node, "hot_in")[0]]
            ho = streams[_port_ids(node, "hot_out")[0]]
            ci = streams[_port_ids(node, "cold_in")[0]]
            co = streams[_port_ids(node, "cold_out")[0]]
            s_gen[bid] = (hi.flow * (p.s_ph(ho.P, ho.h) - p.s_ph(hi.P, hi.h))
                          + ci.flow * (p.s_ph(co.P, co.h) - p.s_ph(ci.P, ci.h)))

    # --- exergy: a diagnostic layer over the solved cycle -----------------
    # Nothing below feeds back into the solve.  It reads the converged
    # states and says where the work potential went, which the first law
    # cannot: energy is conserved, so eta_th can report a loss without
    # saying which component caused it.
    ex = exergy_mod.analyse(layout, streams, extras, props,
                            case.environment, mdot, case.fluid,
                            W_net=w_net * mdot)
    flags.extend(ex["flags"])
    if abs(ex["loop_entropy_residual"]) > 1e-6:
        flags.append(
            f"working-fluid entropy does not close around the loop "
            f"(residual {ex['loop_entropy_residual']:.3g}); the exergy "
            f"numbers are built on it, so treat them as suspect")

    metrics["E_D_total"] = ex["E_D_total"]
    metrics["E_D_known"] = ex["E_D_known"]
    metrics["exergy_complete"] = ex["complete"]
    metrics["e_D_known"] = ex["E_D_known"] / mdot if mdot else float("nan")

    res = ex.get("balance_residual")
    if res is not None and abs(res) > 1e-6:
        flags.append(
            f"exergy balance does not close: residual {res:.3g} of the "
            f"exergy supplied. Suspect a sign convention or a component "
            f"whose entropy terms are incomplete.")

    checks = {
        "energy_closure": closure,
        "energy_closure_rel": closure / q_in,
        "s_gen": s_gen,
        "tear_residual": residual,
        "tear_iterations": iters,
        "loop_entropy_residual": ex["loop_entropy_residual"],
    }

    if abs(closure / q_in) > num.energy_tol:
        flags.append(f"energy closure off by {closure/q_in*100:.3g}% of q_in")
    for bid, sg in s_gen.items():
        if sg < -1e-6:
            flags.append(f"{bid}: negative entropy generation {sg:.4g} J/kg/K")
    if metrics["T_crit_margin"] < 0 and T_crit == T_crit:
        flags.append(
            f"coldest state is {-metrics['T_crit_margin']:.2f} K below the "
            f"critical temperature")

    return Result(
        case=case,
        ok=not flags,
        flags=flags,
        streams={sid: st.describe(props) for sid, st in streams.items()},
        blocks=extras,
        metrics=metrics,
        exergy=ex,
        checks=checks,
        schedule={"order": sched.order, "tears": sched.tears,
                  "iterations": iters, "residual": residual},
    )
