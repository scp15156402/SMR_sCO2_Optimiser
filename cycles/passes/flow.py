"""Pass 2: resolve the mass-flow fraction carried by every stream.

Needed before evaluation because the loop's boundary stream may not carry the
full flow -- in a recompression cycle the precooler outlet carries only
(1 - x) of it.

Flows are propagated structurally from an arbitrary seed and then normalised
so the largest is 1.0.  In every closed cycle the main line (through the
turbine) is the largest, so "fraction of total cycle flow" comes out right
without the layout having to nominate a reference stream.
"""
from __future__ import annotations

from ..blocks import get
from ..blocks.base import Identity, Scale, Sum


class FlowError(RuntimeError):
    pass


def _ids(node, port):
    v = node.inlets.get(port, node.outlets.get(port))
    return v if isinstance(v, (list, tuple)) else [v]


def resolve(case) -> dict:
    layout = case.layout
    rules = []
    for node in layout.nodes:
        mod = get(node.type)
        rules.append((node, mod.flow_rule(case.params.get(node.id, {}))))

    f = {next(iter(sorted(layout.streams()))): 1.0}     # arbitrary seed

    for _ in range(2 * len(layout.streams()) + 4):
        changed = False
        for node, rule in rules:
            if isinstance(rule, Identity):
                for a_port, b_port in rule.pairs:
                    a, b = _ids(node, a_port)[0], _ids(node, b_port)[0]
                    if a in f and b not in f:
                        f[b] = f[a]; changed = True
                    elif b in f and a not in f:
                        f[a] = f[b]; changed = True

            elif isinstance(rule, Scale):
                src = _ids(node, rule.inlet)[0]
                outs = _ids(node, rule.outlets[0][0])
                if src in f:
                    for _port, idx, frac in rule.outlets:
                        if outs[idx] not in f:
                            f[outs[idx]] = f[src] * frac; changed = True
                else:
                    for _port, idx, frac in rule.outlets:
                        if outs[idx] in f and frac > 0:
                            f[src] = f[outs[idx]] / frac; changed = True; break

            elif isinstance(rule, Sum):
                ins = _ids(node, rule.inlet)
                out = _ids(node, rule.outlet)[0]
                if all(i in f for i in ins) and out not in f:
                    f[out] = sum(f[i] for i in ins); changed = True
                elif out in f and sum(i not in f for i in ins) == 1:
                    unknown = next(i for i in ins if i not in f)
                    f[unknown] = f[out] - sum(f[i] for i in ins if i in f)
                    changed = True
        if not changed:
            break

    missing = sorted(layout.streams() - set(f))
    if missing:
        raise FlowError(f"case {case.name!r}: flow undetermined for {missing}")

    peak = max(f.values())
    if peak <= 0.0:
        raise FlowError(f"case {case.name!r}: no positive flow anywhere")
    f = {k: v / peak for k, v in f.items()}

    bad = {k: v for k, v in f.items() if v < -1e-12}
    if bad:
        raise FlowError(
            f"case {case.name!r}: negative flow on {sorted(bad)} "
            f"- check the split fraction"
        )
    return f
