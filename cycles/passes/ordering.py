"""Pass 3: decide what order to evaluate the blocks in, and where to tear.

A block is ready when every one of its inlet streams is known.  Only two
blocks have more than one inlet -- the heat exchanger and the mixer -- so
those are the only possible sources of a loop.

Simple and recuperated layouts come out acyclic and evaluate in one pass.
Recompression and partial cooling come out cyclic; the pass then nominates a
tear stream and the tear loop closes it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Schedule:
    order: tuple        # block ids, in evaluation order
    tears: tuple        # stream ids guessed before the first pass


def build(layout, known_streams) -> Schedule:
    known = set(known_streams)
    order, tears = [], []
    remaining = list(layout.nodes)

    while remaining:
        ready = [n for n in remaining if all(s in known for s in n.inlet_streams())]

        if not ready:
            # Everything left is blocked by a loop. Tear the stream that frees
            # the most blocks; ties go to the hot inlet of a heat exchanger,
            # which is the physically natural tear in a recuperator network.
            blocked_inputs = {}
            for n in remaining:
                for s in n.inlet_streams():
                    if s not in known:
                        blocked_inputs.setdefault(s, []).append(n)

            def rank(item):
                sid, nodes = item
                hot = any(
                    nd.type == "heat_exchanger" and nd.inlets.get("hot_in") == sid
                    for nd in nodes
                )
                return (-len(nodes), not hot, sid)

            tear = sorted(blocked_inputs.items(), key=rank)[0][0]
            tears.append(tear)
            known.add(tear)
            continue

        for n in ready:
            order.append(n.id)
            known.update(n.outlet_streams())
            remaining.remove(n)

    return Schedule(tuple(order), tuple(tears))
