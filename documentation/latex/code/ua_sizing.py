def lmtd(dT1: float, dT2: float) -> float:
    if dT1 <= 0.0 or dT2 <= 0.0:
        return float("nan")
    if abs(dT1 - dT2) < 1e-9 * max(dT1, dT2):
        return 0.5 * (dT1 + dT2)
    return (dT1 - dT2) / math.log(dT1 / dT2)

def ua_from_profile(profile) -> float:
    dT = profile.dT
    n = len(dT) - 1
    if n < 1 or min(dT) <= 0.0:
        return float("nan")
    dQ = profile.Q / n
    total = 0.0
    for j in range(1, n + 1):
        lm = lmtd(dT[j], dT[j - 1])
        if not math.isfinite(lm) or lm <= 0.0:
            return float("nan")
        total += dQ / lm
    return total
