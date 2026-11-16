"""Property backends and the resolver blocks use."""
from __future__ import annotations

from .base import Backend, Props
from .idealgas import GASES, IdealGasBackend

__all__ = ["Backend", "Props", "IdealGasBackend", "make_backend", "make_props"]


def make_backend(fluid: str, backend: str = "coolprop"):
    """One fluid -> one backend instance."""
    if backend == "coolprop":
        from .coolprop import CoolPropBackend
        return CoolPropBackend(fluid)
    if backend == "idealgas":
        return IdealGasBackend(fluid)
    if backend == "tables":
        raise NotImplementedError(
            "tabular backend not built yet; it is the speed option for large "
            "sweeps and the only route for fluids CoolProp lacks (He-3)"
        )
    raise ValueError(f"unknown backend {backend!r}")


def make_props(fluids, backend: str = "coolprop") -> Props:
    """Build the resolver a solve() call hands to every block."""
    if isinstance(fluids, str):
        fluids = [fluids]
    return Props({f: make_backend(f, backend) for f in fluids})
