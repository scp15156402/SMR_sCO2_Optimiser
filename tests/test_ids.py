"""Point IDs: build, parse, convert."""
import pytest

from helpers.ids import make_id, parse_id, physical

EXAMPLES = {
    1: dict(Ph=200, Pl=77, T=320, Tt=500),
    2: dict(Ph=180, Pl=85, T=350, Tt=451),
    3: dict(Ph=200, Pl=77, T=320, Tt=500, x=30),
    4: dict(Ph=200, Pl=77, T=320, Tt=500, Pm=120),
    5: dict(Ph=200, Pl=77, T=320, Tt=500, Pm=120, x=25),
    6: dict(Ph=200, T=320, Tt=500, Pm=80, Pe=40, x=30),
}


@pytest.mark.parametrize("layout", sorted(EXAMPLES))
def test_round_trip(layout):
    fields = EXAMPLES[layout]
    assert parse_id(make_id(layout, **fields)) == {"layout": layout, **fields}


def test_example_string():
    assert make_id(3, Ph=200, Pl=77, T=320, Tt=500, x=30) == "L3_Ph200_Pl077_T320_Tt500_x030"


def test_missing_field():
    with pytest.raises(ValueError):
        make_id(3, Ph=200, Pl=77, T=320, Tt=500)


def test_extra_field():
    with pytest.raises(ValueError):
        make_id(2, Ph=200, Pl=77, T=320, Tt=500, x=30)


def test_non_int_value():
    with pytest.raises(ValueError):
        make_id(2, Ph=20.0, Pl=77, T=320, Tt=500)


@pytest.mark.parametrize("bad", [
    "",
    "L7_Ph200_Pl077_T320_Tt500",          # unknown layout
    "L3_Ph200_Pl077_T320_Tt500",          # missing x
    "L2_Ph200_T320_Pl077_Tt500",          # wrong order
    "L2_Ph200_Pl77_T320_Tt500",           # not zero-padded
    "L2_Ph200_Pl077_T320_Tt500_",         # trailing separator
    "L2_PhABC_Pl077_T320_Tt500",          # non-numeric
])
def test_malformed_id(bad):
    with pytest.raises(ValueError):
        parse_id(bad)


def test_physical_layout3():
    p = physical(parse_id("L3_Ph200_Pl077_T320_Tt500_x030"))
    assert p["P_high_MPa"] == pytest.approx(20.0)
    assert p["P_low_MPa"] == pytest.approx(7.7)
    assert p["T_in_C"] == pytest.approx(32.0)
    assert p["T_turb_C"] == pytest.approx(500.0)
    assert p["split"] == pytest.approx(0.30)
    assert p["P_mid_MPa"] is None
    assert p["P_exh_MPa"] is None
