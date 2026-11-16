"""helpers/ranking.py: Pareto front, knee and TOPSIS on (payout max, mass min)."""
import math


def pareto(payout, mass):
    """True where no other point has payout >= and mass <= with one strict."""
    n = len(payout)
    order = sorted(range(n), key=lambda i: (mass[i], -payout[i]))
    flags = [False] * n
    best = -math.inf
    for i in order:                      # increasing mass, then decreasing payout
        if payout[i] > best:
            flags[i] = True
            best = payout[i]
    # equal (mass, payout) duplicates of a front point are also non-dominated
    front = {(mass[i], payout[i]) for i in range(n) if flags[i]}
    return [flags[i] or (mass[i], payout[i]) in front for i in range(n)]


def knee(payout, mass, front):
    """Index of the front point nearest the ideal corner after scaling both
    objectives to 0-1 over the front (payout 1 = best, mass 0 = best)."""
    idx = [i for i in range(len(payout)) if front[i]]
    if not idx:
        return None
    pmin, pmax = min(payout[i] for i in idx), max(payout[i] for i in idx)
    mmin, mmax = min(mass[i] for i in idx), max(mass[i] for i in idx)

    def d(i):
        pn = (payout[i] - pmin) / (pmax - pmin) if pmax > pmin else 1.0
        mn = (mass[i] - mmin) / (mmax - mmin) if mmax > mmin else 0.0
        return math.hypot(1.0 - pn, mn)

    return min(idx, key=d)


def topsis(payout, mass, weights):
    """Closeness score d_minus / (d_plus + d_minus); vector normalisation."""
    def norm(v):
        s = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / s for x in v]

    p = [weights["payout"] * x for x in norm(payout)]
    m = [weights["mass"] * x for x in norm(mass)]
    p_best, p_worst = max(p), min(p)          # benefit
    m_best, m_worst = min(m), max(m)          # cost
    scores = []
    for pi, mi in zip(p, m):
        d_plus = math.hypot(pi - p_best, mi - m_best)
        d_minus = math.hypot(pi - p_worst, mi - m_worst)
        tot = d_plus + d_minus
        scores.append(d_minus / tot if tot else 0.0)
    return scores


def ranks(scores):
    """1 = highest score."""
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    r = [0] * len(scores)
    for k, i in enumerate(order, 1):
        r[i] = k
    return r
