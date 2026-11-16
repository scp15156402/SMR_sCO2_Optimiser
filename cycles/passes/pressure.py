"""Pass 1: resolve every stream pressure, before any enthalpy exists.

Possible because each block declares its pressure link as an *invertible*
relation.  Propagation then runs in both directions from the anchors, which
is what a closed cycle needs: the turbine outlet pressure in a recuperated
layout is only reachable by walking backwards from the compressor inlet
through the hot-side losses.

A layout with three pressure levels (partial cooling, where the turbine
exhausts below the main compressor inlet) needs no special handling -- the
anchors and relations simply resolve to three values.
"""
from __future__ import annotations

from ..blocks import get


class PressureError(RuntimeError):
    pass


def _port_streams(node, port):
    """Map a port name to its stream id(s)."""
    if port in node.inlets:
        v = node.inlets[port]
    elif port in node.outlets:
        v = node.outlets[port]
    else:
        raise PressureError(f"block {node.id!r} has no port {port!r}")
    return v if isinstance(v, (list, tuple)) else [v]


def resolve(case) -> dict:
    """Return {stream_id: pressure}. Raises if under- or over-determined."""
    layout = case.layout
    P = {}

    # --- anchors ----------------------------------------------------------
    for sid, state in case.boundary.items():
        if "P" not in state:
            raise PressureError(
                f"boundary stream {sid!r} needs a pressure as well as a temperature"
            )
        P[sid] = state["P"]
    P.update(case.pressures)

    edges = []     # (stream_a, stream_b, forward, backward)
    for node in layout.nodes:
        mod = get(node.type)
        params = case.params.get(node.id, {})
        relations, anchors = mod.pressure_rules(params)

        for port, value in anchors.items():
            for sid in _port_streams(node, port):
                if sid in P and abs(P[sid] - value) > 1e-6 * max(P[sid], value):
                    raise PressureError(
                        f"stream {sid!r} anchored twice with different pressures: "
                        f"{P[sid]:.6g} and {value:.6g} (block {node.id!r})"
                    )
                P[sid] = value

        for rel in relations:
            for a in _port_streams(node, rel.src):
                for b in _port_streams(node, rel.dst):
                    edges.append((a, b, rel.forward, rel.backward))

    # --- propagate both ways until nothing changes ------------------------
    for _ in range(len(layout.streams()) + 2):
        changed = False
        for a, b, fwd, bwd in edges:
            if a in P and b not in P:
                P[b] = fwd(P[a]); changed = True
            elif b in P and a not in P:
                P[a] = bwd(P[b]); changed = True
        if not changed:
            break

    missing = sorted(layout.streams() - set(P))
    if missing:
        raise PressureError(
            f"case {case.name!r}: pressure undetermined for {missing}. "
            f"Add a pressure anchor (a block P_out, a ratio, or an entry in "
            f"case.pressures)."
        )

    # --- consistency: every relation must hold ----------------------------
    worst, worst_at = 0.0, None
    for a, b, fwd, _ in edges:
        want, got = fwd(P[a]), P[b]
        err = abs(want - got) / max(abs(want), 1.0)
        if err > worst:
            worst, worst_at = err, (a, b)
    if worst > 1e-6:
        raise PressureError(
            f"case {case.name!r}: pressure network is over-determined; "
            f"relation {worst_at[0]} -> {worst_at[1]} is off by {worst*100:.3g}%. "
            f"Remove one anchor."
        )

    return P
