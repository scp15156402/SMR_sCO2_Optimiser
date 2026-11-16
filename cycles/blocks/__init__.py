"""The block library.

Adding a block is: write the module, import it here, add it to the list.
Nothing else in the solver needs to change -- the passes discover everything
they need through the contract in base.py.
"""
from __future__ import annotations

from . import (compressor, cooler, heat_exchanger, heater, mixer, splitter,
               throttle, turbine)

_MODULES = (
    compressor,
    turbine,
    heat_exchanger,
    cooler,
    heater,
    splitter,
    mixer,
    throttle,
)

REGISTRY = {m.TYPE: m for m in _MODULES}


def get(block_type: str):
    try:
        return REGISTRY[block_type]
    except KeyError:
        raise KeyError(
            f"unknown block type {block_type!r}; "
            f"known types: {sorted(REGISTRY)}"
        ) from None


def multi_in(module) -> tuple:
    return getattr(module, "MULTI_IN", ())


def multi_out(module) -> tuple:
    return getattr(module, "MULTI_OUT", ())


def fixed_outlets(module, params) -> dict:
    """Outlet states a block pins from its parameters alone. Usually none."""
    fn = getattr(module, "fixed_outlets", None)
    return fn(params) if fn else {}


__all__ = ["REGISTRY", "get", "multi_in", "multi_out", "fixed_outlets"]
