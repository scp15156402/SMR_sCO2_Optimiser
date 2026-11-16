"""What a solved cycle hands back.

This is the only object Stage 2 ever sees.  Everything a study, a cost model
or a plot could need is already in here, so nothing downstream has to reach
back into the solver or re-run it.

Failures are flags, not exceptions.  A sweep of ten thousand points must keep
going when one of them asks for a pinch the exchanger cannot deliver.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Result:
    case: object                      # the Case that produced this
    ok: bool                          # solved and passed every check
    flags: list = field(default_factory=list)

    streams: dict = field(default_factory=dict)   # id -> P,T,h,s,rho,flow
    blocks: dict = field(default_factory=dict)    # id -> that block's extras
    metrics: dict = field(default_factory=dict)   # cycle-level numbers
    checks: dict = field(default_factory=dict)    # closure, pinch, entropy
    schedule: dict = field(default_factory=dict)  # order, tears, iterations
    exergy: dict = field(default_factory=dict)    # component-resolved E_D

    # --- convenience ------------------------------------------------------
    def __getitem__(self, key):
        return self.metrics[key]
