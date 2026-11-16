"""The feasibility filter on one known point."""
import pytest

import config
import helpers.checks as checks

ID = "L2_Ph200_Pl077_T320_Tt500"


def test_reference_point_feasible():
    status, row = checks.evaluate(ID)
    assert status == "feasible", row
    expected = dict(eta=0.3271985, UA_recup_1=1669.53, UA_cooler_1=7692.51,
                    UA_total=9362.04, pinch_recup_1=25.1415, pinch_cooler_1=5.000,
                    pressure_ratio=2.5974026, eta_carnot=0.6053159)
    tol = dict(eta=dict(rel=1e-4), pinch_recup_1=dict(abs=0.01),
               pinch_cooler_1=dict(abs=0.01), pressure_ratio=dict(rel=1e-7),
               eta_carnot=dict(rel=1e-6))
    for k, v in expected.items():
        assert float(row[k]) == pytest.approx(v, **tol.get(k, dict(rel=1e-3))), k
    for k in ("UA_recup_2", "UA_cooler_2", "pinch_recup_2", "pinch_cooler_2", "split"):
        assert row[k] == "", k
    assert list(row) == checks.COLUMNS


def test_pinch_limit_makes_infeasible_without_stage2(monkeypatch):
    monkeypatch.setattr(config, "RECUP_PINCH_MIN_K", 30.0)
    calls = []
    real_build = checks.build

    def spy(id_, coolant=True):
        calls.append(coolant)
        return real_build(id_, coolant=coolant)

    monkeypatch.setattr(checks, "build", spy)
    status, reason = checks.evaluate(ID)
    assert status == "infeasible"
    assert reason.startswith("recup_pinch<5K"), reason
    assert calls == [False]          # stage 2 (coolant=True) never ran
