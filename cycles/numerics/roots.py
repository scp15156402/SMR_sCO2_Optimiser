"""One-dimensional solvers.

Deliberately small and bracketed.  Newton is not offered: the heat-exchanger
pinch can jump between an end and the interior of the exchanger as
effectiveness changes, which leaves the target function continuous but
kinked.  Bracketed methods do not care; derivative methods do.
"""
from __future__ import annotations


class ConvergenceError(RuntimeError):
    pass


def bisect(f, lo, hi, tol=1e-10, max_iter=200):
    """Smallest-assumption root finder: needs only a sign change on [lo, hi]."""
    flo, fhi = f(lo), f(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if flo * fhi > 0.0:
        raise ConvergenceError(
            f"no sign change on [{lo:g}, {hi:g}]: f(lo)={flo:g}, f(hi)={fhi:g}"
        )
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if fmid == 0.0 or (hi - lo) < tol * max(1.0, abs(mid)):
            return mid
        if flo * fmid < 0.0:
            hi, fhi = mid, fmid
        else:
            lo, flo = mid, fmid
    raise ConvergenceError(f"bisect hit {max_iter} iterations on [{lo:g}, {hi:g}]")


def solve_monotone(f, target, lo, hi, tol=1e-10, max_iter=200, clamp=True):
    """Find x with f(x) = target, where f is monotone on [lo, hi].

    With clamp=True a target outside the achievable range returns the nearest
    endpoint instead of raising.  That matters in a sweep: a design asking for
    a pinch the exchanger cannot deliver should come back flagged, not crash
    ten thousand other points.
    """
    flo, fhi = f(lo) - target, f(hi) - target
    if flo * fhi > 0.0:
        if not clamp:
            raise ConvergenceError(
                f"target {target:g} outside achievable range "
                f"[{flo + target:g}, {fhi + target:g}]"
            )
        return lo if abs(flo) < abs(fhi) else hi
    return bisect(lambda x: f(x) - target, lo, hi, tol=tol, max_iter=max_iter)


def secant(f, target, x0, lo, hi, tol=1e-10, max_iter=40, step=1e-4):
    """Find x with f(x) = target, starting from a good guess x0.

    Used where a previous answer is available and the function is smooth and
    monotone -- a heat exchanger's pinch against its effectiveness, re-solved
    every tear iteration while the hot inlet drifts slightly.  From a warm
    start this converges in a handful of evaluations, against roughly thirty
    for bisection at the same tolerance.

    Every iterate is clamped into [lo, hi], and the whole thing falls back to
    bisection if the secant stalls or leaves the bracket.
    """
    x0 = min(max(x0, lo), hi)
    x1 = min(max(x0 + step * (hi - lo), lo), hi)
    if x1 == x0:
        x1 = min(max(x0 - step * (hi - lo), lo), hi)

    f0 = f(x0) - target
    if abs(f0) < tol:
        return x0
    f1 = f(x1) - target

    for _ in range(max_iter):
        if abs(f1) < tol:
            return x1
        denom = f1 - f0
        if denom == 0.0:
            break
        x2 = x1 - f1 * (x1 - x0) / denom
        if not (lo <= x2 <= hi):
            break
        if abs(x2 - x1) < tol * max(1.0, abs(x2)):
            return x2
        x0, f0, x1, f1 = x1, f1, x2, f(x2) - target

    return solve_monotone(f, target, lo, hi, tol=tol, max_iter=200)
