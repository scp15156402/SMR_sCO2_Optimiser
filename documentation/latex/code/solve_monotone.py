def solve_monotone(f, target, lo, hi, tol=1e-10, max_iter=200, clamp=True):
    flo, fhi = f(lo) - target, f(hi) - target
    if flo * fhi > 0.0:
        if not clamp:
            raise ConvergenceError(
                f"target {target:g} outside achievable range "
                f"[{flo + target:g}, {fhi + target:g}]"
            )
        return lo if abs(flo) < abs(fhi) else hi
    return bisect(lambda x: f(x) - target, lo, hi, tol=tol, max_iter=max_iter)
