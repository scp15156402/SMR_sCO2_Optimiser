def successive_substitution(g, x0, tol=1e-8, max_iter=200, relax=1.0):
    x = x0
    for i in range(1, max_iter + 1):
        xn = g(x)
        res = abs(xn - x)
        x = x + relax * (xn - x)
        if res < tol * max(1.0, abs(x)):
            return x, i, res
    raise ConvergenceError(
        f"tear did not converge in {max_iter} iterations; residual {res:g}"
    )
