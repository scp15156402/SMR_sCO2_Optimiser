"""Physics checks: layout 2 reference points, first-law hand checks, literature.

A. Reference values for the layout 2 builder, computed independently with this
   solver. A change here means the builder or the solver changed.
B. First-law checks a person can redo by hand from the stream enthalpies.
C. Literature, ported from the old project's tests/validate_literature.py
   (tag old-project), same reference numbers and tolerances.
"""
import pytest

import config
from brayton_cycle import recompression
from cycles import Case, Effectiveness, ThermalPower, solve
from cycles.physics.isentropic import compress, expand
from cycles.properties import make_backend
from cycles.units import MPa, MW, degC
from helpers.builders import build

# ---------------------------------------------------------------- A ---------
REF_1 = "L2_Ph200_Pl077_T320_Tt500"
REFERENCE = {
    REF_1: dict(eta=0.3271985, recup_pinch=25.1415, recup_UA=1669.53,
                cooler_UA=7692.51, water_pinch=5.000),
    "L2_Ph200_Pl077_T360_Tt500": dict(eta=0.3319068, recup_pinch=26.6125,
                                      recup_UA=2015.35, cooler_UA=7125.21),
}
ETA_REL, PINCH_ABS, UA_REL = 1e-4, 0.01, 1e-3

_solved = {}


def solved(id_):
    if id_ not in _solved:
        _solved[id_] = solve(build(id_))
    return _solved[id_]


@pytest.mark.parametrize("id_", sorted(REFERENCE))
def test_reference_point(id_):
    ref = REFERENCE[id_]
    r = solved(id_)
    assert r.ok and not r.flags, r.flags
    m, cooler = r.metrics, r.blocks["COOLER"]
    assert m["eta_th"] == pytest.approx(ref["eta"], rel=ETA_REL)
    assert r.blocks["RECUP"]["pinch"] == pytest.approx(ref["recup_pinch"], abs=PINCH_ABS)
    assert m["UA_total"] / 1e3 == pytest.approx(ref["recup_UA"], rel=UA_REL)
    assert cooler["coolant_UA_per_flow"] * m["mdot"] / 1e3 == pytest.approx(
        ref["cooler_UA"], rel=UA_REL)
    if "water_pinch" in ref:
        assert cooler["coolant_pinch"] == pytest.approx(ref["water_pinch"], abs=PINCH_ABS)


# ---------------------------------------------------------------- B ---------
# Streams of brayton_cycle/recuperated.py:
#   s1 -COMP-> s2 -RECUP cold-> s3 -HEATER-> s4 -TURB-> s5 -RECUP hot-> s6 -COOLER-> s1
@pytest.fixture(scope="module")
def ref1():
    r = solved(REF_1)
    assert r.ok, r.flags
    return r


def _H(r, sid):
    """Enthalpy flow per kg of total cycle flow, J/kg."""
    s = r.streams[sid]
    return s["h"] * s["flow"]


def test_heater_duty(ref1):
    q = _H(ref1, "s4") - _H(ref1, "s3")
    assert ref1.metrics["mdot"] * q == pytest.approx(MW(config.Q_THERMAL_MW), rel=1e-6)


def test_eta_from_enthalpies(ref1):
    w_t = _H(ref1, "s4") - _H(ref1, "s5")
    w_c = _H(ref1, "s2") - _H(ref1, "s1")
    q_in = _H(ref1, "s4") - _H(ref1, "s3")
    assert (w_t - w_c) / q_in == pytest.approx(ref1.metrics["eta_th"], rel=1e-9)


def test_recuperator_balance(ref1):
    hot = _H(ref1, "s5") - _H(ref1, "s6")
    cold = _H(ref1, "s3") - _H(ref1, "s2")
    assert hot == pytest.approx(cold, rel=1e-9)


def test_boundary_conditions(ref1):
    assert ref1.streams["s1"]["T"] == pytest.approx(degC(32.0))     # cooler outlet = T_in
    assert ref1.streams["s4"]["T"] == pytest.approx(degC(500.0))    # turbine inlet = T_turb
    assert ref1.streams["s2"]["P"] == pytest.approx(MPa(20.0))      # compressor outlet = P_high


# ---------------------------------------------------------------- C ---------
# Dostal, MIT-ANP-TR-100 (2004), Table 10.2: basic design state points,
# conservative turbomachinery.  (point, P kPa, T degC, h kJ/kg, s kJ/kg/K)
DOSTAL_STATES = [
    ("1", 7692.31,  32.00,  306.67, 1.3478),
    ("2", 20000.00, 61.10,  327.26, 1.3546),
    ("3", 19988.68, 157.99, 536.10, 1.9099),
    ("4", 19957.95, 396.54, 846.36, 2.4908),
    ("5", 19827.95, 550.00, 1035.25, 2.7429),
    ("6", 7901.16,  440.29, 914.45, 2.7619),
    ("7", 7814.21,  168.34, 604.19, 2.2189),
    ("8", 7704.58,  69.59,  478.64, 1.9026),
]
H_TOL = 5e-4      # relative; enthalpy is what every block balance uses
S_TOL = 5e-3      # relative; looser: Dostal's printed h, T and s are not
                  # mutually consistent at three points (the table, not the backend)
W_TOL = 0.05      # kJ/kg on a machine outlet
ETA_TOL = 2e-3    # relative on a reproduced cycle efficiency


@pytest.fixture(scope="module")
def co2():
    return make_backend("CO2", "coolprop")


def test_dostal_enthalpy(co2):
    worst = max(abs(co2.h_pt(P * 1e3, T + 273.15) / 1e3 - h) / abs(h)
                for _, P, T, h, _ in DOSTAL_STATES)
    assert worst < H_TOL, worst


def test_dostal_entropy(co2):
    worst = max(abs(co2.s_pt(P * 1e3, T + 273.15) / 1e3 - s) / abs(s)
                for _, P, T, _, s in DOSTAL_STATES)
    assert worst < S_TOL, worst


# Dostal compressor 1 -> 2 at eta 0.89: prints 2id = 324.99, 2 = 327.26 kJ/kg
def test_dostal_compressor_isentropic(co2):
    h2id = co2.h_ps(20000e3, 1.3478e3)
    assert abs(h2id / 1e3 - 324.99) < W_TOL, h2id / 1e3


def test_dostal_compressor_real(co2):
    h2 = compress(306.67e3, co2.h_ps(20000e3, 1.3478e3), 0.89)
    assert abs(h2 / 1e3 - 327.26) < W_TOL, h2 / 1e3


# Dostal turbine 5 -> 6 at eta 0.90: prints 6id = 901.03, 6 = 914.45 kJ/kg
def test_dostal_turbine_isentropic(co2):
    h6id = co2.h_ps(7901.16e3, 2.7429e3)
    assert abs(h6id / 1e3 - 901.03) < W_TOL, h6id / 1e3


def test_dostal_turbine_real(co2):
    h6 = expand(1035.25e3, co2.h_ps(7901.16e3, 2.7429e3), 0.90)
    assert abs(h6 / 1e3 - 914.45) < W_TOL, h6 / 1e3


# Kim et al., Energy 147 (2018) 1216-1226. Table 1 conditions; the
# conclusions give the optimum. Definitions checked against ours in the old
# project/cases/literature.py: split ratio is the fraction sent to the
# recompressor (our x); effectiveness is enthalpy-based q / min(q_max_hot,
# q_max_cold); LTR cold-side limit carries (1-sr); compressor work weighted by
# its own flow. No pressure drops mentioned, so none applied.
KIM_ETA_TURBINE = 0.90
KIM_ETA_COMPRESSOR = 0.85
KIM_EFFECTIVENESS = 0.95
KIM_T_COMP_IN = degC(32)
KIM_P_LOW = MPa(7.4)
KIM_T_TURB_IN = degC(550)
KIM_RP = 2.6                 # reported optimum, conclusion 1
KIM_P_HIGH = MPa(19.24)
KIM_SPLIT = 0.307
KIM_ETA_REPORTED = 0.4467


def kim_case(x=KIM_SPLIT, P_high=KIM_P_HIGH, eps=KIM_EFFECTIVENESS):
    return Case(
        name="kim_2018", fluid="CO2", layout=recompression,
        size=ThermalPower(MW(100)),          # efficiency is size-independent
        boundary={"s1": {"T": KIM_T_COMP_IN, "P": KIM_P_LOW}},
        params={
            "MC":     dict(eta=KIM_ETA_COMPRESSOR, P_out=P_high),
            "RC":     dict(eta=KIM_ETA_COMPRESSOR, P_out=P_high),
            "LTR":    dict(spec=Effectiveness(eps), nodes=100),
            "HTR":    dict(spec=Effectiveness(eps), nodes=100),
            "SPLIT":  dict(x=x),
            "HEATER": dict(T_out=KIM_T_TURB_IN),
            "TURB":   dict(eta=KIM_ETA_TURBINE),
            "PC":     dict(T_out=KIM_T_COMP_IN),
        },
    )


def test_kim_efficiency_at_optimum():
    r = solve(kim_case())
    assert r.ok, r.flags
    err = abs(r.metrics["eta_th"] - KIM_ETA_REPORTED) / KIM_ETA_REPORTED
    assert err < ETA_TOL, r.metrics["eta_th"]


def test_kim_split_optimum():
    xs = [0.24, 0.27, 0.29, KIM_SPLIT, 0.33, 0.36]
    best = max(xs, key=lambda x: solve(kim_case(x=x)).metrics["eta_th"])
    assert best == KIM_SPLIT, best


def test_kim_pressure_ratio_optimum():
    rps = [2.2, 2.4, KIM_RP, 2.8, 3.0]
    best = max(rps, key=lambda p: solve(kim_case(P_high=KIM_P_LOW * p)).metrics["eta_th"])
    assert best == KIM_RP, best
