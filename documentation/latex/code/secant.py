def secant(f, target, x0, lo, hi, tol=1e-10, max_iter=40, step=1e-4):
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
