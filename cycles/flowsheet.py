"""A layout is a list of blocks and the streams between them.

That is the whole representation.  Simple, recuperated, intercooled,
recompression and partial-cooling are different lists of the same block
types -- no layout-specific code anywhere in the solver.

Streams are never declared; they are whatever the ports mention.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Node:
    """One block instance, wired.

    Port values are a stream id, or a list of stream ids for a port the block
    declares as MULTI_IN / MULTI_OUT (a mixer's inlet, a splitter's outlet).
    """
    id: str
    type: str
    inlets: Mapping[str, object]
    outlets: Mapping[str, object]

    def inlet_streams(self) -> list:
        return _flatten(self.inlets.values())

    def outlet_streams(self) -> list:
        return _flatten(self.outlets.values())


def _flatten(values) -> list:
    out = []
    for v in values:
        if isinstance(v, (list, tuple)):
            out.extend(v)
        else:
            out.append(v)
    return out


@dataclass(frozen=True)
class Flowsheet:
    name: str
    nodes: tuple

    def __post_init__(self):
        object.__setattr__(self, "nodes", tuple(self.nodes))
        self.validate()

    # --- lookups ----------------------------------------------------------
    def node(self, node_id: str) -> Node:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise KeyError(f"no block {node_id!r} in layout {self.name!r}")

    def streams(self) -> set:
        s = set()
        for n in self.nodes:
            s.update(n.inlet_streams())
            s.update(n.outlet_streams())
        return s

    def producer(self, stream: str):
        for n in self.nodes:
            if stream in n.outlet_streams():
                return n
        return None

    def consumers(self, stream: str) -> list:
        return [n for n in self.nodes if stream in n.inlet_streams()]

    # --- checks -----------------------------------------------------------
    def validate(self):
        """Catch wiring mistakes at import, not halfway through a sweep."""
        from .blocks import get, multi_in, multi_out

        ids = [n.id for n in self.nodes]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"layout {self.name!r}: duplicate block ids {sorted(dupes)}")

        for n in self.nodes:
            mod = get(n.type)
            missing_in = set(mod.INLETS) - set(n.inlets)
            missing_out = set(mod.OUTLETS) - set(n.outlets)
            if missing_in or missing_out:
                raise ValueError(
                    f"layout {self.name!r}, block {n.id!r} ({n.type}): "
                    f"unwired ports in={sorted(missing_in)} out={sorted(missing_out)}"
                )
            extra = (set(n.inlets) - set(mod.INLETS)) | (set(n.outlets) - set(mod.OUTLETS))
            if extra:
                raise ValueError(
                    f"layout {self.name!r}, block {n.id!r} ({n.type}): "
                    f"unknown ports {sorted(extra)}"
                )
            for port in mod.INLETS:
                is_list = isinstance(n.inlets[port], (list, tuple))
                if is_list != (port in multi_in(mod)):
                    raise ValueError(
                        f"layout {self.name!r}, block {n.id!r}: inlet port {port!r} "
                        f"{'takes' if port in multi_in(mod) else 'does not take'} a list"
                    )
            for port in mod.OUTLETS:
                is_list = isinstance(n.outlets[port], (list, tuple))
                if is_list != (port in multi_out(mod)):
                    raise ValueError(
                        f"layout {self.name!r}, block {n.id!r}: outlet port {port!r} "
                        f"{'takes' if port in multi_out(mod) else 'does not take'} a list"
                    )

        # every stream has exactly one producer and at least one consumer
        for s in self.streams():
            producers = [n.id for n in self.nodes if s in n.outlet_streams()]
            if len(producers) > 1:
                raise ValueError(
                    f"layout {self.name!r}: stream {s!r} produced by {producers}"
                )
            if not producers:
                raise ValueError(
                    f"layout {self.name!r}: stream {s!r} has no producer "
                    f"- a closed cycle has no loose ends"
                )
            if not self.consumers(s):
                raise ValueError(f"layout {self.name!r}: stream {s!r} goes nowhere")
