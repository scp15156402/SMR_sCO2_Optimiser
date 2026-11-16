def solve(evaluate_once, tears, guesses, numerics):
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
