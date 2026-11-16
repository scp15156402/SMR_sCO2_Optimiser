"""Brayton-cycle configurations, built from the generic solver.

Each file is pure wiring -- which blocks, and which streams run between them.
No numbers live here; those belong in a case.  A new layout is a new file.
"""
from .intercooled import intercooled
from .partial_cooling import partial_cooling
from .recompression import recompression
from .recuperated import recuperated
from .simple import simple

LAYOUTS = {
    "simple": simple,
    "recuperated": recuperated,
    "recompression": recompression,
    "intercooled": intercooled,
    "partial_cooling": partial_cooling,
}

__all__ = ["simple", "recuperated", "recompression", "intercooled",
           "partial_cooling", "LAYOUTS"]
