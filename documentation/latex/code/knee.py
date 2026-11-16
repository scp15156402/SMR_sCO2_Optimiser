def knee(front, objectives=OBJECTIVES):
    if not front:
        return None
    if len(front) == 1:
        return front[0]

    ranges = []
    for name, get, sense in objectives:
        vals = [get(a) for a in front]
        lo, hi = min(vals), max(vals)
        ranges.append((get, sense, lo, hi if hi > lo else lo + 1.0))

    def distance(a):
        d = 0.0
        for get, sense, lo, hi in ranges:
            u = (get(a) - lo) / (hi - lo)          # 0 worst .. 1 best, if max
            if sense == "min":
                u = 1.0 - u
            d += (1.0 - u) ** 2                    # shortfall from the ideal
        return d

    return min(front, key=distance)
