def _seek(f, target, warm, tol=1e-9):
    if warm is None:
        return solve_monotone(f, target, EPS_LO, EPS_HI, tol=tol)
    return secant(f, target, warm, EPS_LO, EPS_HI, tol=tol)
