def bisect(f, lo, hi, tol=1e-10, max_iter=200):
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
