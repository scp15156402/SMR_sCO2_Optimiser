def _dominates(a, b, objectives) -> bool:
    better_anywhere = False
    for _, get, sense in objectives:
        x, y = get(a), get(b)
        if sense == "min":
            x, y = -x, -y
        if x < y - TOL:
            return False
        if x > y + TOL:
            better_anywhere = True
    return better_anywhere

def pareto_front(assessments, objectives=OBJECTIVES) -> list:
    return [a for a in assessments
            if not any(_dominates(b, a, objectives)
                       for b in assessments if b is not a)]
