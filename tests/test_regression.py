"""Every case must still construct, still solve, and still give the same
numbers as the committed baseline.

This is the test that makes a refactor safe.  "It still runs" is not
evidence; "it produces the same numbers it produced before the move" is.
The baseline lives in `tests/baseline.json` and is written by
`python -m tools.make_baseline`.

Tolerance is 1e-9 relative -- far tighter than anything physical, because
a pure refactor should change *nothing*.  A failure here means either a
real behavioural change (investigate it) or a deliberate one (state the
reason, then regenerate the baseline).  Never regenerate the baseline to
silence a failure.

    pytest tests/test_regression.py -q
"""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from cycles import solve
from project.cases import CASES

BASELINE = json.loads(
    (pathlib.Path(__file__).parent / "baseline.json").read_text())
TOL = 1e-9


def test_every_case_is_in_the_baseline():
    """A new case without a baseline entry is an untested case."""
    missing = set(CASES) - set(BASELINE)
    assert not missing, f"no baseline for: {sorted(missing)}"


def test_baseline_has_no_orphans():
    """A baseline entry with no case means something was deleted."""
    orphans = set(BASELINE) - set(CASES)
    assert not orphans, f"baseline references missing cases: {sorted(orphans)}"


@pytest.mark.parametrize("name", sorted(CASES))
def test_case_reproduces_baseline(name):
    want = BASELINE[name]
    r = solve(CASES[name])
    assert r.ok == want["ok"], f"{name}: ok changed; flags={r.flags}"
    if not want["ok"]:
        return
    for key, expected in want.items():
        if key in ("ok", "flags"):
            continue
        got = r.metrics[key]
        assert math.isclose(got, expected, rel_tol=TOL), (
            f"{name}.{key}: {got!r} != baseline {expected!r} "
            f"(relative change {abs(got - expected) / abs(expected):.3e})")
