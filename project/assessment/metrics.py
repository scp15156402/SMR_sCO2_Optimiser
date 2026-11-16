"""Plant-level figures the brief asks R5 for, and one it asks only to report.

Everything here is a few lines over quantities the solver already produced.
It lives in `project/` because the source and sink temperatures that define
Carnot efficiency are this problem's boundary conditions, not physics.
"""
from __future__ import annotations

from dataclasses import dataclass

from .cost import Cost, CostModel, cost_of
from .mass import Mass, MassModel, mass_of

# The brief's own second-law check: Carnot between source and sink.
# 773 K is the 500 degC turbine inlet; 305 K is roughly the 32 degC
# compressor inlet.  Both are the brief's numbers, used so the figure is
# comparable with its worked example.
T_SOURCE_K = 773.0
T_SINK_K = 305.0


def second_law_efficiency(result, T_source=T_SOURCE_K, T_sink=T_SINK_K):
    """eta_th / eta_Carnot.

    The brief is explicit that this is *reported, not optimized*, and it is
    worth seeing why: Carnot here is a constant (0.605), so dividing by it
    reorders nothing. It rescales efficiency onto "how much of what was
    thermodynamically available did we actually get", which is a fairer
    thing to quote than a bare percentage, and useless as an objective.
    """
    return result.metrics["eta_th"] / (1.0 - T_sink / T_source)


@dataclass(frozen=True)
class Assessment:
    """Everything needed to place one design on the trade-off."""
    name: str
    eta_th: float                 # %
    eta_second_law: float
    W_net_mwe: float
    heat_per_mwe: float           # MWth per MWe
    mass: Mass
    cost: Cost
    pinch_min_k: float
    T_margin_k: float             # worst compressor inlet, above T_crit
    P_margin_mpa: float           # worst compressor inlet, above P_crit
    T_inlet_min_c: float          # coldest compressor inlet
    P_inlet_min_mpa: float        # lowest-pressure compressor inlet
    P_max_mpa: float
    T_turbine_c: float
    split: float


def compressor_inlets(result):
    """(T degC, P MPa) at the inlet of every compressor in the layout.

    The brief's margin constraint is about *compressor* inlets, because
    that is where liquid would do damage. Measuring it at whatever stream
    happens to be coldest gives a different and sometimes wrong answer: in
    the partial cooling layout the coldest stream sits at the intermediate
    pressure, which is below the critical pressure but nowhere near the
    two-phase region because it is well above the critical temperature.
    """
    out = []
    for bid, e in result.blocks.items():
        if e["kind"] != "compressor":
            continue
        node = result.case.layout.node(bid)
        sid = node.inlets["in"]
        st = result.streams[sid if isinstance(sid, str) else sid[0]]
        out.append((bid, st["T"] - 273.15, st["P"] / 1e6))
    return out


def assess(name, result, split=0.0,
           mass_model=MassModel(), cost_model=CostModel()) -> Assessment:
    """Reduce a solved cycle to the handful of numbers a decision needs."""
    m = result.metrics
    mass = mass_of(result, mass_model)

    # critical point of the working fluid, from the backend the solve used
    inlets = compressor_inlets(result)
    T_crit_c, P_crit_mpa = 30.9782, 7.3773        # CO2
    T_marg = min((T - T_crit_c for _, T, _ in inlets), default=float("nan"))
    P_marg = min((P - P_crit_mpa for _, _, P in inlets), default=float("nan"))

    return Assessment(
        name=name,
        eta_th=m["eta_th"] * 100.0,
        eta_second_law=second_law_efficiency(result),
        W_net_mwe=m["W_net"] / 1e6,
        heat_per_mwe=m["Q_in"] / m["W_net"],
        mass=mass,
        cost=cost_of(result, mass, cost_model),
        pinch_min_k=m["pinch_min"],
        T_margin_k=T_marg,
        P_margin_mpa=P_marg,
        T_inlet_min_c=min((T for _, T, _ in inlets), default=float("nan")),
        P_inlet_min_mpa=min((P for _, _, P in inlets), default=float("nan")),
        P_max_mpa=m["P_max"] / 1e6,
        T_turbine_c=max(s["T"] for s in result.streams.values()) - 273.15,
        split=split,
    )
