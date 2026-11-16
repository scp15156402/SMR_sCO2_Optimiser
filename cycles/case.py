"""One run, fully specified.

A Case is frozen data.  `with_()` returns a modified copy and never mutates,
because an optimiser calls it tens of thousands of times on what would
otherwise be a shared dict -- the kind of bug that produces a plausible but
wrong Pareto front.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field, fields, replace
from typing import Mapping

from .flowsheet import Flowsheet
from .physics.exergy import Environment
from .specs import SIZE_SPECS


@dataclass(frozen=True)
class Numerics:
    nodes: int = 100          # heat-exchanger profile resolution
    tol: float = 1e-8         # tear convergence, relative
    max_iter: int = 200
    relax: float = 1.0        # tear under-relaxation
    energy_tol: float = 1e-3  # fraction of q_in allowed in the closure check


@dataclass(frozen=True)
class Case:
    name: str
    fluid: str
    layout: Flowsheet
    size: object                          # ThermalPower | NetPower | MassFlow
    boundary: Mapping[str, dict]          # stream id -> {"T":..., "P":...}
    params: Mapping[str, dict]            # block id -> parameters
    pressures: Mapping[str, float] = field(default_factory=dict)
    backend: str = "coolprop"
    numerics: Numerics = field(default_factory=Numerics)
    # the dead state the exergy diagnostics are measured against; it changes
    # every exergy number and nothing else, so it belongs here rather than
    # buried as a constant
    environment: Environment = field(default_factory=Environment)
    notes: str = ""

    def __post_init__(self):
        if not isinstance(self.size, SIZE_SPECS):
            raise TypeError(
                f"case {self.name!r}: size must be one of "
                f"{[c.__name__ for c in SIZE_SPECS]}, got {type(self.size).__name__}"
            )
        if not self.boundary:
            raise ValueError(
                f"case {self.name!r}: needs at least one boundary stream "
                f"(a stream with both T and P given) to anchor the loop"
            )
        known = self.layout.streams()
        for sid in list(self.boundary) + list(self.pressures):
            if sid not in known:
                raise ValueError(
                    f"case {self.name!r}: stream {sid!r} is not in layout "
                    f"{self.layout.name!r}"
                )
        for bid in self.params:
            self.layout.node(bid)     # raises if unknown

    def with_(self, **kw) -> "Case":
        """Copy with overrides.  `params`, `boundary` and `pressures` merge
        per key; `numerics` and `environment` accept a partial dict."""
        merged = {}
        for key in ("params", "boundary", "pressures"):
            if key in kw:
                base = copy.deepcopy(dict(getattr(self, key)))
                for k, v in kw.pop(key).items():
                    if isinstance(v, dict) and isinstance(base.get(k), dict):
                        base[k] = {**base[k], **v}
                    else:
                        base[k] = v
                merged[key] = base

        # numerics and environment are frozen dataclasses, not mappings, so
        # a plain replace() would substitute a raw dict for the object and
        # the failure would surface much later as
        # "'dict' object has no attribute 'max_iter'" from inside the tear
        # loop -- an error that says nothing about the real mistake.
        # Accepting a partial dict here means `with_(numerics={"tol": 1e-9})`
        # overrides one field and keeps the rest, which is what every caller
        # expects and what `params` already does.
        for key in ("numerics", "environment"):
            if key in kw and isinstance(kw[key], dict):
                current = getattr(self, key)
                unknown = set(kw[key]) - {f.name for f in fields(current)}
                if unknown:
                    raise ValueError(
                        f"unknown {key} field(s) {sorted(unknown)}; "
                        f"valid: {sorted(f.name for f in fields(current))}")
                merged[key] = replace(current, **kw.pop(key))

        return replace(self, **merged, **kw)
