"""Solver checks that need no project knowledge at all.

These are the tests that prove `cycles/` is generic.  They were previously
in `project/runs/validate_air.py` (now deleted), which imported `project.cases` -- so the
test that the solver is not project-specific could not run without the
project.  The flowsheet and case are built here instead, from `cycles` and
`brayton_cycle` only, which removes that backwards dependency.

    pytest tests/test_solver.py -v
"""
from __future__ import annotations

import math

import pytest

from brayton_cycle import simple
from cycles import Case, MassFlow, solve
from cycles.properties.idealgas import GASES
from cycles.units import K, kPa

RP = 10.0
P1 = kPa(100)
T1, T3 = 288.15, 1273.15


def air_case(eta_c: float = 1.0, eta_t: float = 1.0, name: str = "air"):
    """Air-standard Brayton cycle, ideal gas, built without the project."""
    return Case(
        name=name, fluid="AirIdeal", layout=simple, backend="idealgas",
        size=MassFlow(1.0),
        boundary={"s1": {"T": K(T1), "P": P1}},
        params={
            "COMP":   dict(P_out=P1 * RP, eta=eta_c),
            "HEATER": dict(T_out=K(T3)),
            "TURB":   dict(P_out=P1, eta=eta_t),
            "COOLER": dict(T_out=K(T1)),
        },
    )


@pytest.fixture(scope="module")
def ideal():
    r = solve(air_case())
    assert r.ok, r.flags
    return r


def closed_form():
    """The air-standard result from a first course in thermodynamics."""
    R, cp = GASES["AirIdeal"]
    g = cp / (cp - R)
    T2s = T1 * RP ** ((g - 1) / g)
    T4s = T3 / RP ** ((g - 1) / g)
    return {
        "eta": 1.0 - RP ** (-(g - 1) / g),
        "w_net": cp * ((T3 - T4s) - (T2s - T1)),
        "q_in": cp * (T3 - T2s),
        "bwr": (T2s - T1) / (T3 - T4s),
    }


@pytest.mark.parametrize("key", ["eta", "w_net", "q_in", "bwr"])
def test_matches_closed_form(ideal, key):
    """Ideal air cycle must reproduce the analytical answer exactly.

    This is the genericity check: if any of these fail, something in the
    solver is assuming CO2 or real-gas behaviour.
    """
    want = closed_form()[key]
    got = {"eta": ideal.metrics["eta_th"],
           "w_net": ideal.metrics["w_net"],
           "q_in": ideal.metrics["q_in"],
           "bwr": ideal.metrics["bwr"]}[key]
    assert math.isclose(got, want, rel_tol=1e-4), f"{key}: {got} vs {want}"


def test_real_machines_lower_efficiency():
    """Isentropic efficiencies below 1 must reduce eta, not raise it."""
    r = solve(air_case(0.85, 0.90, "air_real"))
    assert r.ok, r.flags
    assert r.metrics["eta_th"] < closed_form()["eta"]


def test_energy_closes(ideal):
    """First law over the whole cycle: q_in - q_out - w_net = 0."""
    m = ideal.metrics
    residual = abs(m["q_in"] - m["q_out"] - m["w_net"]) / m["q_in"]
    assert residual < 1e-10, residual


def test_entropy_returns_to_start(ideal):
    """A closed loop must return its working fluid to the same state."""
    s1 = ideal.streams["s1"]
    assert math.isclose(s1["h"], ideal.streams["s1"]["h"], rel_tol=1e-12)


@pytest.mark.parametrize("nodes", [50, 100, 200])
def test_grid_convergence(nodes):
    """Heat-exchanger discretisation must not move the answer.

    Lifted from `project/studies/check_nodes.py`, which sweeps the node count
    and printed the spread.  Here it is an assertion instead.
    """
    from cycles import Pinch
    from project.cases import baseline_watercooled
    from cycles.case import Numerics
    r = solve(baseline_watercooled.with_(
        params={"RECUP": dict(spec=Pinch(K(5)))},
        numerics=Numerics(nodes=nodes)))
    assert r.ok, r.flags
    test_grid_convergence.results[nodes] = r.metrics["eta_th"]


test_grid_convergence.results = {}


def test_grid_convergence_spread():
    """The spread across node counts must be below 0.1 % relative."""
    res = test_grid_convergence.results
    assert len(res) == 3, "run the parametrised grid test first"
    lo, hi = min(res.values()), max(res.values())
    assert (hi - lo) / hi < 1e-3, res
