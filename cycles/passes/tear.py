"""Pass 4: close the loop.

The recuperator network of a recompression cycle is circular -- the
low-temperature recuperator needs its hot inlet, which the high-temperature
recuperator produces, which needs the mixer, which needs the
low-temperature recuperator.  One guessed enthalpy breaks it.

Plain successive substitution, deliberately.  The map is contractive here
(guess the tear enthalpy too high and it comes back lower) and settles in
roughly thirty passes.  Secant acceleration was tried and removed: on this
map it is unreliable near the critical point, and the safeguarded version
needed *more* passes than the plain one.  The per-pass cost is the thing
worth optimising, and that is handled by skipping diagnostics while
iterating -- see `diagnostics` in solve.py.

A bracketed root find is not used because the bracket would have to be
guessed, and a bad bracket fails louder than a slow iteration.
"""
from __future__ import annotations

from ..numerics.roots import ConvergenceError


def solve(evaluate_once, tears, guesses, numerics):
    """Iterate `evaluate_once(guess_map) -> (state, produced_map)` to a fixed point.

    Returns (state, iterations, residual).  Raises ConvergenceError if the
    loop will not settle; the caller turns that into a flag rather than a
    crash, so one bad point never kills a sweep.
    """
    if not tears:
        state, _ = evaluate_once({})
        return state, 0, 0.0

    x = dict(guesses)
    residual = float("inf")

    for i in range(1, numerics.max_iter + 1):
        state, g = evaluate_once(x)

        residual = max(
            abs(g[s] - x[s]) / max(abs(x[s]), abs(g[s]), 1.0) for s in tears
        )
        if residual < numerics.tol:
            return state, i, residual

        x = {s: x[s] + numerics.relax * (g[s] - x[s]) for s in tears}

    raise ConvergenceError(
        f"tear streams {list(tears)} did not converge in {numerics.max_iter} "
        f"iterations; residual {residual:.3g}. Try a smaller numerics.relax."
    )
