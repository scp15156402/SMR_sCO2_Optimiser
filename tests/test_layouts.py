"""Smoke test per layout: one mid-grid point, first-law closure, plausible eta."""
import pytest

from cycles import solve
from helpers.builders import build
from helpers.checks import evaluate

MID = {
    1: "L1_Ph180_Pl077_T360_Tt500",
    3: "L3_Ph180_Pl077_T360_Tt500_x030",
    4: "L4_Ph180_Pl077_T360_Tt500_Pm120",
    5: "L5_Ph200_Pl077_T360_Tt500_Pm120_x030",
    6: "L6_Ph200_T360_Tt500_Pm082_Pe065_x030",
}
# Layout 1 has no recuperator: all turbine-exhaust heat is rejected, and its
# efficiency at these conditions is about 0.13 (hand-checked by the energy
# balance below), so its lower bound is 0.10 rather than 0.15.
ETA_LO = {1: 0.10}


LAYOUT1_KNOWN_FAILURE = (
    "layout 1 has no recuperator, so the cooler receives turbine exhaust at "
    "several hundred degC; the CoolantPinch search tries water outlets up to "
    "that temperature, reaches saturation at the default 6 bar coolant "
    "pressure (159 degC) and CoolProp raises. 9 of 18 L1 points fail this way. "
    "Fixing it needs a coolant-pressure decision or a cycles/ change.")


@pytest.mark.parametrize("layout", [
    pytest.param(1, marks=pytest.mark.xfail(strict=True, reason=LAYOUT1_KNOWN_FAILURE)),
    3, 4, 5, 6])
def test_layout_smoke(layout):
    _check(layout, MID[layout])


def test_layout1_at_a_solvable_point():
    """Same checks for layout 1 at a point whose cooler water stays below boiling."""
    _check(1, "L1_Ph200_Pl077_T320_Tt500")


def _check(layout, id_):
    status, payload = evaluate(id_)
    if status == "infeasible":
        assert not payload.startswith(("error", "not_solved")), payload
    r = solve(build(id_))
    assert r.ok, r.flags
    q_heater = sum(b["q_total"] for b in r.blocks.values() if b.get("kind") == "heater")
    q_cool = sum(b["q_total"] for b in r.blocks.values() if b.get("kind") == "cooler")
    w_net = r.metrics["w_net"]
    assert w_net == pytest.approx(q_heater - q_cool, rel=1e-6)
    assert ETA_LO.get(layout, 0.15) < r.metrics["eta_th"] < 0.55

