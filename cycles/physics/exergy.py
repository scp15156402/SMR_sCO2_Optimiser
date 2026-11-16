"""Exergy: how much of the work potential each component destroys.

Energy is conserved, so a first-law balance can never say where a cycle
*loses*.  Every joule that goes in comes out somewhere, and the efficiency
tells you the ratio without telling you which component spent it.  Exergy is
the part of an energy flow that could in principle be turned into work
against a reference environment, and unlike energy it is not conserved: it
is destroyed wherever something irreversible happens.  Summing that
destruction per component gives a ranked list of where the losses actually
are, which is information `eta_th` does not contain.

This is a diagnostic layer.  It reads a solved cycle and changes nothing
about it: no equation here feeds back into the solve, and no result above
moves because this module exists.

What is reused rather than rebuilt
-----------------------------------
The solver already computes an entropy balance per block for the adiabatic
components and the heat exchangers, as a sign check on the second law.  For
an adiabatic component with no heat crossing its boundary, exergy
destruction is exactly

    E_D = T0 * S_gen

so this module extends that same balance to the remaining block types rather
than writing a parallel implementation.  The entropy function, the property
backend and the normalised-flow convention are all the existing ones.

What cannot be computed, and why it is not guessed
---------------------------------------------------
Exergy destruction needs the temperature at which heat crosses a component's
boundary.  For the heater, this project has no heat-source model at all --
the block is told an outlet temperature and reports a duty, with no reactor
side, no primary loop and no boundary temperature.  So heater destruction is
reported as *unavailable*, not estimated, and the total is reported as
incomplete whenever it is.  Assuming the CO2 outlet temperature is the
source temperature would understate the destruction badly and silently.

The cooler is the opposite case and shows why the distinction matters.  When
a coolant side has been specified, the coolant's inlet and outlet states are
known, so the cooler's destruction *can* be computed properly: the CO2 and
the coolant together form an adiabatic exchanger and the balance closes.
When no coolant was specified, it cannot, and it is marked unavailable too.

Physical flow exergy only.  Chemical exergy is not included, which is
correct here because the working fluid's composition never changes: every
chemical term would cancel in every balance.  Kinetic and potential terms
are left out for the same reason they are left out of the energy balances.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

T0_DEFAULT = 298.15          # K, 25 degC
P0_DEFAULT = 101325.0        # Pa, one atmosphere

# Below this, a negative destruction is floating-point noise rather than a
# modelling error.  Expressed as a fraction of the largest destruction in
# the cycle, so it scales with the problem.
NEGATIVE_TOL = 1e-6


@dataclass(frozen=True)
class Environment:
    """The dead state everything is measured against.

    Exergy is always relative to an environment: it is the work obtainable
    by bringing a stream reversibly into equilibrium with it.  Change the
    environment and every number here changes, which is why it is a case
    input rather than a constant buried in the code.
    """
    T0: float = T0_DEFAULT
    P0: float = P0_DEFAULT


@lru_cache(maxsize=None)
def dead_state(backend, T0: float, P0: float):
    """(h0, s0) at the reference environment, cached.

    The dead state depends only on the fluid and the environment, so it is
    the same for every stream of a given fluid in a given case.  Computing
    it per call cost two property lookups for every exergy evaluated, which
    is most of the module's property traffic for no information.
    """
    return backend.h_pt(P0, T0), backend.s_pt(P0, T0)


def specific(backend, env: Environment, P: float, h: float,
             s: float | None = None) -> float:
    """Physical flow exergy, J/kg.

        e_x = (h - h0) - T0 (s - s0)

    Pass `s` if the caller already has it; every state in a solved Result
    does, so the property backend is not asked twice.
    """
    h0, s0 = dead_state(backend, env.T0, env.P0)
    if s is None:
        s = backend.s_ph(P, h)
    return (h - h0) - env.T0 * (s - s0)


def _s(props, stream):
    return props(stream.fluid).s_ph(stream.P, stream.h)


def _entropy_balance(node, streams, props):
    """Net entropy leaving a block with its streams, per unit cycle flow.

    Sign convention: outlets positive, inlets negative, so a positive value
    is entropy produced or brought in with heat.  For an adiabatic block
    this *is* the entropy generated.
    """
    out = sum(s.flow * _s(props, s)
              for s in (streams[i] for ids in node.outlets.values()
                        for i in (ids if isinstance(ids, (list, tuple)) else [ids])))
    inn = sum(s.flow * _s(props, s)
              for s in (streams[i] for ids in node.inlets.values()
                        for i in (ids if isinstance(ids, (list, tuple)) else [ids])))
    return out - inn


def analyse(layout, streams, blocks, props, env: Environment, mdot: float,
            fluid: str, W_net: float = 0.0) -> dict:
    """Component-resolved exergy destruction for a solved cycle.

    `streams` and `blocks` are the solver's own; `mdot` is the plant's total
    mass flow, used only to scale normalised results at the end.  Nothing
    here is fed back into the solve.
    """
    pf = props(fluid)
    comps, incomplete, flags = {}, [], []

    for bid, extra in blocks.items():
        node = layout.node(bid)
        kind = node.type
        entry = {"kind": kind, "complete": True, "reason": None}

        if kind == "heater":
            a, b = _in_out(node, streams)
            gain = mdot * a.flow * (
                specific(pf, env, b.P, b.h) - specific(pf, env, a.P, a.h))
            T_b = extra.get("T_source")
            if T_b is None:
                # No heat-source model exists, so the boundary temperature
                # at which exergy enters is unknown.  Report what the CO2
                # side gained -- a lower bound on what the source had to
                # supply -- and refuse to name a destruction.  The user can
                # state a boundary temperature (`T_source` on the block) and
                # this becomes computable; the solver will use a stated
                # temperature but will not invent one.
                entry.update(
                    s_gen=None, E_D=None, complete=False,
                    reason="no heat-source boundary temperature; state one "
                           "with T_source on the heater to make this "
                           "computable",
                    Ex_gain=gain)
                incomplete.append(bid)
            else:
                # Exergy in with the heat, minus exergy gained by the CO2.
                # T_source is the temperature of the boundary the heat
                # crosses, not the CO2 outlet temperature.
                Q = extra["q_total"] * mdot
                entry.update(
                    s_gen=None,
                    E_D=(1.0 - env.T0 / T_b) * Q - gain,
                    T_source=T_b, Ex_gain=gain)

        elif kind == "cooler":
            a, b = _in_out(node, streams)
            ds_cycle = a.flow * (_s(props, b) - _s(props, a))
            if "coolant_flow" in extra:
                # The coolant side is modelled, so CO2 plus coolant is an
                # adiabatic pair and the balance closes honestly.
                pc = props(extra["coolant_fluid"])
                P_c = extra["coolant_P"]
                h_cold_in = pc.h_pt(P_c, extra["coolant_T_in"])
                h_cold_out = pc.h_pt(P_c, extra["coolant_T_out"])
                ds_coolant = extra["coolant_flow"] * (
                    pc.s_ph(P_c, h_cold_out) - pc.s_ph(P_c, h_cold_in))
                entry.update(s_gen=ds_cycle + ds_coolant)
            else:
                entry.update(
                    s_gen=None, E_D=None, complete=False,
                    reason="no coolant side specified, so the rejection "
                           "boundary temperature is unknown",
                    Ex_shed=-mdot * a.flow * (
                        specific(pf, env, b.P, b.h)
                        - specific(pf, env, a.P, a.h)))
                incomplete.append(bid)

        else:
            # compressor, turbine, heat_exchanger, mixer, splitter
            # are all adiabatic with no external heat, so the entropy
            # balance over their own streams is the generation.
            entry.update(s_gen=_entropy_balance(node, streams, props))

        if entry.get("s_gen") is not None:
            entry["E_D"] = env.T0 * entry["s_gen"] * mdot
        comps[bid] = entry

    # --- negative destruction is a real error, not something to clip -----
    biggest = max((c["E_D"] for c in comps.values()
                   if c.get("E_D") is not None), default=0.0)
    for bid, c in comps.items():
        ED = c.get("E_D")
        if ED is not None and ED < -NEGATIVE_TOL * max(biggest, 1.0):
            flags.append(
                f"{bid}: exergy destruction is negative ({ED/1e3:.3g} kW); "
                f"that is a second-law violation, so suspect a sign "
                f"convention, a bad converged state, or a modelling error")

    known = {b: c["E_D"] for b, c in comps.items() if c.get("E_D") is not None}
    complete = not incomplete
    total = sum(known.values()) if known else 0.0

    # --- closure: the CO2 loop's entropy must return to where it started --
    # Summed over every block, the working fluid's entropy changes telescope
    # around the loop and must cancel exactly.  That is checkable even
    # though the overall exergy balance is not, and it validates the entropy
    # field the destructions are built from.
    loop = 0.0
    for bid in blocks:
        node = layout.node(bid)
        loop += _entropy_balance(node, streams, props)
    scale = sum(abs(c["s_gen"]) for c in comps.values()
                if c.get("s_gen") is not None) or 1.0

    # per-stream exergy, so the state table can show where it sits as well
    # as where it goes.  Absolute values in W, scaled to the plant.
    per_stream = {}
    for sid, st in streams.items():
        bk = props(st.fluid)
        e = specific(bk, env, st.P, st.h)
        per_stream[sid] = {"e_x": e, "Ex": e * st.flow * mdot}

    out = {
        "environment": {"T0": env.T0, "P0": env.P0},
        "streams": per_stream,
        "components": comps,
        "by_kind": _by_kind(comps),
        "E_D_known": total,
        "E_D_total": total if complete else None,
        "complete": complete,
        "incomplete": incomplete,
        "loop_entropy_residual": loop / scale,
        "flags": flags,
    }
    out["fractions"] = ({b: 100.0 * e / total for b, e in known.items()}
                        if total > 0 else None)
    out["specific"] = {b: e / mdot for b, e in known.items()} if mdot else {}
    out.update(_balance(comps, blocks, props, env, mdot, W_net, total))
    return out


def _balance(comps, blocks, props, env, mdot, W_net, destroyed) -> dict:
    """Close the exergy books over a boundary that is actually defined.

    The reactor is outside the model, so a balance drawn around the whole
    plant cannot close: the exergy entering with the heat source is unknown.
    Draw the boundary at the *CO2 side of the heater* instead and it closes
    exactly, because every term is then something the solver computed:

        exergy the CO2 gains in the heater
          = net shaft work out
          + exergy destroyed in the components
          + exergy carried away by the coolant

    That last term is exergy *shed*, not destroyed: warm cooling water still
    has work potential relative to the environment, it is simply thrown away
    rather than wrecked. Confusing the two is the usual way these balances
    are got wrong.

    Returns a residual relative to the exergy input, or None with a reason
    when a term is missing.
    """
    heaters = [c for c in comps.values() if c["kind"] == "heater"]
    if len(heaters) != 1 or heaters[0].get("Ex_gain") is None:
        return {"balance_residual": None,
                "balance_reason": "needs exactly one heater with a known "
                                  "CO2-side exergy gain"}

    shed = 0.0
    for bid, c in comps.items():
        if c["kind"] != "cooler":
            continue
        extra = blocks[bid]
        if "coolant_flow" not in extra:
            return {"balance_residual": None,
                    "balance_reason": f"cooler {bid!r} has no coolant side, "
                                      f"so the exergy it sheds is unknown"}
        pc = props(extra["coolant_fluid"])
        P_c = extra["coolant_P"]
        h_i = pc.h_pt(P_c, extra["coolant_T_in"])
        h_o = pc.h_pt(P_c, extra["coolant_T_out"])
        shed += extra["coolant_flow"] * mdot * (
            specific(pc, env, P_c, h_o) - specific(pc, env, P_c, h_i))

    supplied = heaters[0]["Ex_gain"]
    residual = supplied - W_net - destroyed - shed
    return {
        "balance_residual": residual / supplied if supplied else None,
        "balance_reason": None,
        "Ex_supplied": supplied,
        "Ex_shed": shed,
        "Ex_to_work": W_net,
    }


def _in_out(node, streams):
    a = streams[_first(node.inlets["in"])]
    b = streams[_first(node.outlets["out"])]
    return a, b


def _first(v):
    return v[0] if isinstance(v, (list, tuple)) else v


def _by_kind(comps):
    """Aggregate by block type. A kind with any unavailable member is None,
    because a partial sum presented as a category total would mislead."""
    agg, broken = {}, set()
    for c in comps.values():
        if c.get("E_D") is None:
            broken.add(c["kind"])
        else:
            agg[c["kind"]] = agg.get(c["kind"], 0.0) + c["E_D"]
    for k in broken:
        agg[k] = None
    return agg
