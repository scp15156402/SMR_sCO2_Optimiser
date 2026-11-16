"""Pareto, knee and TOPSIS on a small hand-made table."""
import math

import pytest

from helpers.ranking import knee, pareto, ranks, topsis

#            A     B     C     D     E
PAYOUT = [100.0, 90.0, 80.0, 70.0, 85.0]
MASS   = [ 10.0,  6.0,  5.0,  5.0,  7.0]
# A: best payout. B, C: trade-offs. D: dominated by C (same mass, less payout).
# E: dominated by B (less payout, more mass).


def test_pareto():
    assert pareto(PAYOUT, MASS) == [True, True, True, False, False]


def test_pareto_ties_both_kept():
    assert pareto([5.0, 5.0], [1.0, 1.0]) == [True, True]


def test_knee():
    # front A(100,10) B(90,6) C(80,5): scaled payout 1, .5, 0; mass 1, .2, 0
    # distances to (1, 0): A 1.0, B hypot(.5,.2)=0.539, C 1.0 -> B
    front = pareto(PAYOUT, MASS)
    assert knee(PAYOUT, MASS, front) == 1


def test_topsis_by_hand():
    w = {"payout": 0.5, "mass": 0.5}
    s = topsis([100.0, 50.0], [10.0, 5.0], w)
    # normalised: payout 100/sqrt(12500)=.8944, 50/..=.4472; mass same numbers
    # weighted: p=[.4472,.2236] m=[.4472,.2236]; best p .4472, m .2236
    # point 0: d+ = .2236, d- = .2236 -> .5 ; point 1: same by symmetry
    assert s == pytest.approx([0.5, 0.5])
    s = topsis([100.0, 50.0, 100.0], [10.0, 5.0, 5.0], w)
    assert s[2] == pytest.approx(1.0)            # best on both: ideal point
    assert ranks(s)[2] == 1


def test_topsis_dominated_scores_lower():
    s = topsis(PAYOUT, MASS, {"payout": 0.5, "mass": 0.5})
    assert s[2] > s[3] and s[1] > s[4]
    assert all(0.0 <= x <= 1.0 for x in s) and not any(math.isnan(x) for x in s)
