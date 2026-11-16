"""The multi-objective step: filter, then find the frontier, then choose.

The brief sets four objectives that disagree:

    1. maximise thermal efficiency
    2. minimise PCS mass and volume
    3. minimise the cost proxy
    4. maximise the compressor-inlet margin above the critical point

Because they disagree there is no single best design, and that is the point
of the exercise rather than a difficulty with it.  What exists instead is a
*frontier*: the designs for which you cannot improve one objective without
giving up another.  Everything behind the frontier is strictly worse than
something on it and can be discarded without an argument.

Three steps, in order:

    feasible()      throw away designs that break a constraint
    pareto_front()  throw away designs something else beats outright
    knee()          pick one, and be explicit about the rule used
"""
from __future__ import annotations

from dataclasses import dataclass

# The brief's constraint list, verbatim in intent.
CONSTRAINTS = {
    "T1_min_c": 32.0,        # compressor inlet, safe distance from two-phase
    "P1_min_mpa": 7.7,       # same
    "pinch_min_k": 5.0,      # recuperator minimum approach
    "P_max_mpa": 20.0,       # maximum cycle pressure
    "T_turbine_max_c": 500.0,  # material limit
    "split_max": 0.5,        # split fraction between 0 and 0.5
    "strict_inlet_pressure": True,   # see feasible() for what this decides
}

TOL = 1e-6                   # so a design exactly on a limit is admitted


@dataclass(frozen=True)
class Candidate:
    """One assessed design, plus why it was or was not allowed."""
    assessment: object
    ok: bool
    violations: tuple


def feasible(assessments, constraints=None) -> list:
    """Tag every design with whether it satisfies the brief's constraints.

    Returns all of them, tagged, rather than only the survivors: the brief
    asks for "the feasible set after constraint filtering" as a deliverable,
    and showing what was excluded and why is most of that deliverable's
    value.  A filter whose rejects are invisible cannot be checked.
    """
    c = dict(CONSTRAINTS, **(constraints or {}))
    out = []
    for a in assessments:
        bad = []
        # The brief: "Compressor inlet >= 32 degC and >= 7.7 MPa (safe
        # distance from two-phase region)".  Two readings are possible and
        # they disagree for partial cooling, whose pre-compressor sits at an
        # intermediate pressure below 7.7 MPa:
        #
        #   strict   every compressor inlet meets both limits
        #   intent   every compressor inlet is clear of the two-phase
        #            region, which above the critical temperature it is at
        #            any pressure
        #
        # `strict_inlet_pressure` selects between them, defaulting to the
        # literal reading.  Flip it and partial cooling becomes admissible.
        if a.T_inlet_min_c < c["T1_min_c"] - TOL:
            bad.append(f"compressor inlet {a.T_inlet_min_c:.2f} degC "
                       f"< {c['T1_min_c']} degC")
        if c.get("strict_inlet_pressure", True):
            if a.P_inlet_min_mpa < c["P1_min_mpa"] - TOL:
                bad.append(f"compressor inlet {a.P_inlet_min_mpa:.2f} MPa "
                           f"< {c['P1_min_mpa']} MPa")
        elif a.T_margin_k < -TOL:
            bad.append(f"compressor inlet {-a.T_margin_k:.2f} K below "
                       f"the critical temperature")
        if a.pinch_min_k < c["pinch_min_k"] - TOL:
            bad.append(f"pinch {a.pinch_min_k:.2f} K < {c['pinch_min_k']} K")
        if a.P_max_mpa > c["P_max_mpa"] + TOL:
            bad.append(f"max pressure {a.P_max_mpa:.2f} > {c['P_max_mpa']} MPa")
        if a.T_turbine_c > c["T_turbine_max_c"] + TOL:
            bad.append(f"turbine inlet {a.T_turbine_c:.1f} > {c['T_turbine_max_c']} degC")
        if a.split > c["split_max"] + TOL:
            bad.append(f"split {a.split:.3f} > {c['split_max']}")
        out.append(Candidate(assessment=a, ok=not bad, violations=tuple(bad)))
    return out


# Each objective as (name, getter, "max" or "min").
OBJECTIVES = (
    ("efficiency", lambda a: a.eta_th, "max"),
    ("mass", lambda a: a.mass.total_t, "min"),
    ("cost proxy", lambda a: a.cost.cost_proxy_musd, "min"),
    ("margin", lambda a: a.T_margin_k, "max"),
)


def _dominates(a, b, objectives) -> bool:
    """True if a is at least as good as b everywhere and better somewhere."""
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
    """The designs nothing else beats outright.

    A design is dominated when some other design is at least as good on
    every objective and strictly better on one: there is then no reason
    anyone would choose it, whatever their priorities.  What survives is the
    set where the priorities actually matter.
    """
    return [a for a in assessments
            if not any(_dominates(b, a, objectives)
                       for b in assessments if b is not a)]


def knee(front, objectives=OBJECTIVES):
    """Pick one design: the point closest to the unattainable ideal.

    Normalise each objective onto 0-1 across the front, build the corner
    where every objective takes its best value -- a point no real design
    reaches -- and take whichever design sits nearest it.

    This is one rule among several and it is not neutral: it weights every
    objective equally, which is a judgement nobody asked for. The brief
    allows "a weighted-sum or knee point choice", so it is admissible, but
    the honest way to report it is as a starting point for an argument
    rather than as an answer the mathematics produced.
    """
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
