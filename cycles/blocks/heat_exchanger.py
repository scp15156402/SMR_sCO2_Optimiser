"""Counterflow heat exchanger -- the only block that iterates.

One implementation serves every two-stream exchanger in a cycle: the
recuperator (working fluid both sides), the precooler (working fluid against
cooling water), and the intermediate heat exchanger (working fluid against a
primary coolant).  Only the fluids and the flow fractions differ.

Three ways to say how hard it works, all describing the same hardware:

    Effectiveness(e)  explicit   -- Q = e * Q_max
    Pinch(dT)         1-D solve  -- the smallest temperature difference anywhere
    UAperFlow(ua)     1-D solve  -- the conductance, which is the physical size

Whichever you give, the other two come back as outputs.  Pinch and UA both
move monotonically with effectiveness, so the search is bracketed and safe:
bisection on the first pass, secant from the previous answer afterwards.
"""
from __future__ import annotations

from ..numerics.roots import secant, solve_monotone
from ..physics import hx_limits, hx_profile, hx_sizing
from ..specs import Effectiveness, Pinch, UAperFlow
from ..stream import Stream
from .base import Identity, drop_relation, require

TYPE = "heat_exchanger"
INLETS = ("hot_in", "cold_in")
OUTLETS = ("hot_out", "cold_out")

EPS_LO, EPS_HI = 1e-6, 0.999999


def pressure_rules(params):
    return [
        drop_relation("hot_in", "hot_out", params.get("dp_hot", 0.0)),
        drop_relation("cold_in", "cold_out", params.get("dp_cold", 0.0)),
    ], {}


def flow_rule(params):
    return Identity((("hot_in", "hot_out"), ("cold_in", "cold_out")))


def _seek(f, target, warm, tol=1e-9):
    """Solve for the effectiveness that hits `target`.

    Secant from the previous answer when there is one -- a handful of
    evaluations instead of thirty bisection steps -- and plain bisection on
    the first pass.  The tolerance stays tight either way: a loose inner
    solve puts a floor under the tear loop's residual and stops the outer
    iteration converging at all.
    """
    if warm is None:
        return solve_monotone(f, target, EPS_LO, EPS_HI, tol=tol)
    return secant(f, target, warm, EPS_LO, EPS_HI, tol=tol)


def _profile_for(eps, props, hot_in, cold_in, P_out, q_max, nodes,
                 P_hot_in, P_cold_in):
    Q = eps * q_max
    h_hot_out = hot_in.h - Q / hot_in.flow
    return hx_profile.build(
        props, hot_in, cold_in, h_hot_out, Q,
        P_hot_in=P_hot_in, P_hot_out=P_out["hot_out"],
        P_cold_in=P_cold_in, P_cold_out=P_out["cold_out"],
        nodes=nodes,
    ), Q


def evaluate(inlets, P_out, params, props, block_id="?", diagnostics=True,
             hint=None):
    """`diagnostics=False` is used inside the tear loop.

    While the loop is still converging, only the duty matters -- the
    profile, pinch and UA are outputs nobody reads yet, and they cost a
    hundred property calls each.  With an effectiveness spec they can be
    skipped outright; with a pinch or UA spec the search still needs a
    profile, but a coarse one is enough to place the effectiveness.
    The final pass always runs at full resolution.

    `hint` is this block's own extras from the previous sweep.  With a pinch
    or UA spec the effectiveness barely moves between tear iterations, so the
    bisection is restarted in a narrow window around the last answer instead
    of across the whole range -- the difference between twenty bisection
    steps per exchanger per iteration and about six.
    """
    hot_in, cold_in = inlets["hot_in"], inlets["cold_in"]
    spec = require(params, "spec", block_id)
    nodes = params.get("nodes", 100)
    search_nodes = params.get("search_nodes", max(16, nodes // 5))

    q_max, binding = hx_limits.max_duty(
        props, hot_in, cold_in, P_out["hot_out"], P_out["cold_out"]
    )

    flags = []
    if q_max <= 0.0:
        # Hot stream is not hotter than the cold stream: nothing to recuperate.
        flags.append(f"{block_id}: no temperature overlap, duty forced to zero")
        q_max = 0.0

    warm = hint.get("effectiveness") if hint else None

    def prof(eps, n=None):
        return _profile_for(eps, props, hot_in, cold_in, P_out, q_max,
                            n or search_nodes, hot_in.P, cold_in.P)[0]

    # --- resolve effectiveness from whichever spec was given ----------------
    if q_max == 0.0:
        eps = 0.0
    elif isinstance(spec, Effectiveness):
        eps = spec.value
    elif isinstance(spec, Pinch):
        # pinch falls as effectiveness rises -> monotone decreasing
        eps = _seek(lambda e: prof(e).pinch, spec.value, warm)
    elif isinstance(spec, UAperFlow):
        def ua_of(e):
            ua = hx_sizing.ua_from_profile(prof(e))
            return ua if ua == ua else 1e30      # NaN -> treat as unreachable
        eps = _seek(ua_of, spec.value, warm)
    else:
        raise TypeError(
            f"block {block_id!r}: spec must be Effectiveness, Pinch or "
            f"UAperFlow, got {type(spec).__name__}"
        )

    Q = eps * q_max
    h_hot_out = hot_in.h - Q / hot_in.flow if hot_in.flow else hot_in.h
    h_cold_out = cold_in.h + Q / cold_in.flow if cold_in.flow else cold_in.h

    hot_out = Stream(hot_in.fluid, P_out["hot_out"], h_hot_out, hot_in.flow)
    cold_out = Stream(cold_in.fluid, P_out["cold_out"], h_cold_out, cold_in.flow)

    extras = {
        "kind": "heat_exchanger",
        "Q": Q,                                   # W per kg/s of total flow
        "Q_max": q_max,
        "binding_limit": binding,
        "effectiveness": eps,
        "shortfall": (1.0 - eps) * q_max,         # loss indicator: heat not recovered
        "flags": flags,
    }

    if not diagnostics:
        return {"hot_out": hot_out, "cold_out": cold_out}, extras

    profile = prof(eps, nodes) if q_max > 0.0 else None
    if profile is None:
        extras.update(pinch=float("nan"), pinch_at=float("nan"),
                      UA_per_flow=0.0, profile=None)
        return {"hot_out": hot_out, "cold_out": cold_out}, extras

    if profile.pinch <= 0.0:
        flags.append(f"{block_id}: temperature cross, pinch {profile.pinch:.2f} K")

    extras.update(
        pinch=profile.pinch,
        pinch_at=profile.pinch_at,
        UA_per_flow=hx_sizing.ua_from_profile(profile),
        profile=profile,
    )
    return {"hot_out": hot_out, "cold_out": cold_out}, extras
