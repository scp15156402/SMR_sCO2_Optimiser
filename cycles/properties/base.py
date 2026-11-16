"""What every property backend must provide.

Blocks only ever call these seven functions, so swapping CoolProp for an
ideal gas or a lookup table changes nothing above this file.  That swap is
the solver's genericity test: the same layout must reproduce the textbook
air-standard cycle when the backend is ideal gas.
"""
from __future__ import annotations

from typing import Protocol


class Backend(Protocol):
    fluid: str
    name: str

    # forward
    def h_pt(self, P: float, T: float) -> float: ...
    def s_pt(self, P: float, T: float) -> float: ...

    # inverse -- these replace the air-table pr column
    def T_ph(self, P: float, h: float) -> float: ...
    def s_ph(self, P: float, h: float) -> float: ...
    def h_ps(self, P: float, s: float) -> float: ...

    # auxiliary
    def rho_ph(self, P: float, h: float) -> float: ...
    def cp_ph(self, P: float, h: float) -> float: ...

    # critical point; (nan, nan) for an ideal gas
    @property
    def T_crit(self) -> float: ...
    @property
    def P_crit(self) -> float: ...


class Props:
    """Resolves a fluid name to its backend.

    A cycle may carry more than one fluid (CO2 on one side of a precooler,
    water on the other), so blocks ask `props(stream.fluid)` rather than
    assuming a single working fluid.
    """

    def __init__(self, backends: dict):
        self._backends = dict(backends)

    def __call__(self, fluid: str) -> Backend:
        try:
            return self._backends[fluid]
        except KeyError:
            raise KeyError(
                f"no property backend for fluid {fluid!r}; "
                f"have {sorted(self._backends)}"
            ) from None

    def fluids(self):
        return sorted(self._backends)
