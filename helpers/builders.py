"""helpers/builders.py: point ID -> cycles.Case.

Every number comes from config.py or from the ID itself; none is typed here.
Pressure drops are zero (config.PRESSURE_DROP), so no dp parameters are set.
Every compressor uses ETA_COMPRESSOR, the turbine ETA_TURBINE, every
recuperator Effectiveness(RECUP_EFFECTIVENESS), the heater T_out = T_turb and
every cooler T_out = T_in with the water side.
"""
from cycles import Case, CoolantPinch, Effectiveness, ThermalPower
from cycles.units import K, MPa, MW, degC

import config
from brayton_cycle import (intercooled, partial_cooling, recomp_intercooled,
                           recompression, recuperated, simple)
from helpers.ids import parse_id, physical

# Fixed role names -> block ids, so every layout fills the same CSV columns.
# cooler_1 is always the cooler feeding the main compressor.
ROLES = {
    1: {"cooler_1": "COOLER"},
    2: {"recup_1": "RECUP", "cooler_1": "COOLER"},
    3: {"recup_1": "HTR", "recup_2": "LTR", "cooler_1": "PC"},
    4: {"recup_1": "RECUP", "cooler_1": "PC", "cooler_2": "IC"},
    5: {"recup_1": "HTR", "recup_2": "LTR", "cooler_1": "PC", "cooler_2": "IC"},
    6: {"recup_1": "HTR", "recup_2": "LTR", "cooler_1": "PC2", "cooler_2": "PC1"},
}


def _cooler(T_out, nodes):
    """Cooler parameters. nodes=None: no water side (cycle-only, fast);
    otherwise the coolant side is sized with this many profile slices."""
    p = dict(T_out=T_out)
    if nodes is not None:
        p.update(coolant_fluid="Water",
                 coolant_T_in=degC(config.T_WATER_IN_C),
                 coolant=CoolantPinch(K(config.COOLER_PINCH_K)),
                 nodes=nodes)
    return p


def _comp(P_out_MPa):
    return dict(eta=config.ETA_COMPRESSOR, P_out=MPa(P_out_MPa))


def _recup():
    return dict(spec=Effectiveness(config.RECUP_EFFECTIVENESS))


def _case(id_, layout, ph, boundary_P_MPa, params, pressures=None):
    return Case(
        name=id_, fluid="CO2", layout=layout,
        size=ThermalPower(MW(config.Q_THERMAL_MW)),
        boundary={"s1": {"T": degC(ph["T_in_C"]), "P": MPa(boundary_P_MPa)}},
        params={**params,
                "HEATER": dict(T_out=degC(ph["T_turb_C"])),
                "TURB":   dict(eta=config.ETA_TURBINE)},
        pressures=pressures or {},
    )


def _simple(id_, ph, n):
    """Layout 1 (brayton_cycle/simple.py)."""
    T = degC(ph["T_in_C"])
    return _case(id_, simple, ph, ph["P_low_MPa"], {
        "COMP":   _comp(ph["P_high_MPa"]),
        "COOLER": _cooler(T, n),
    })


def _recuperated(id_, ph, n):
    """Layout 2 (brayton_cycle/recuperated.py)."""
    T = degC(ph["T_in_C"])
    return _case(id_, recuperated, ph, ph["P_low_MPa"], {
        "COMP":   _comp(ph["P_high_MPa"]),
        "RECUP":  _recup(),
        "COOLER": _cooler(T, n),
    })


def _recompression(id_, ph, n):
    """Layout 3 (brayton_cycle/recompression.py)."""
    T = degC(ph["T_in_C"])
    return _case(id_, recompression, ph, ph["P_low_MPa"], {
        "MC":    _comp(ph["P_high_MPa"]),
        "RC":    _comp(ph["P_high_MPa"]),
        "LTR":   _recup(),
        "HTR":   _recup(),
        "SPLIT": dict(x=ph["split"]),
        "PC":    _cooler(T, n),
    })


def _intercooled(id_, ph, n):
    """Layout 4 (brayton_cycle/intercooled.py)."""
    T = degC(ph["T_in_C"])
    return _case(id_, intercooled, ph, ph["P_low_MPa"], {
        "LPC":   _comp(ph["P_mid_MPa"]),
        "IC":    _cooler(T, n),
        "HPC":   _comp(ph["P_high_MPa"]),
        "RECUP": _recup(),
        "PC":    _cooler(T, n),
    })


def _recomp_intercooled(id_, ph, n):
    """Layout 5 (brayton_cycle/recomp_intercooled.py)."""
    T = degC(ph["T_in_C"])
    return _case(id_, recomp_intercooled, ph, ph["P_low_MPa"], {
        "LPC":   _comp(ph["P_mid_MPa"]),
        "IC":    _cooler(T, n),
        "HPC":   _comp(ph["P_high_MPa"]),
        "RC":    _comp(ph["P_high_MPa"]),
        "LTR":   _recup(),
        "HTR":   _recup(),
        "SPLIT": dict(x=ph["split"]),
        "PC":    _cooler(T, n),
    })


def _partial_cooling(id_, ph, n):
    """Layout 6, Angelino (brayton_cycle/partial_cooling.py).
    Main compressor inlet s1 is at P_mid; turbine exhaust s7 at P_exh."""
    T = degC(ph["T_in_C"])
    return _case(id_, partial_cooling, ph, ph["P_mid_MPa"], {
        "PCOMP": _comp(ph["P_mid_MPa"]),
        "MC":    _comp(ph["P_high_MPa"]),
        "RC":    _comp(ph["P_high_MPa"]),
        "HTR":   _recup(),
        "LTR":   _recup(),
        "SPLIT": dict(x=ph["split"]),
        "PC1":   _cooler(T, n),
        "PC2":   _cooler(T, n),
    }, pressures={"s7": MPa(ph["P_exh_MPa"])})


BUILDERS = {1: _simple, 2: _recuperated, 3: _recompression, 4: _intercooled,
            5: _recomp_intercooled, 6: _partial_cooling}


def build(id_, coolant=True, cooler_nodes=None):
    """Case for one point ID. Layouts without a builder raise NotImplementedError.

    coolant=False: coolers get no coolant parameters. Otherwise every cooler
    uses cooler_nodes (default config.COOLER_NODES) profile slices;
    recuperators keep the solver default of 100.
    """
    parsed = parse_id(id_)
    layout = parsed["layout"]
    if layout not in BUILDERS:
        raise NotImplementedError(f"layout {layout}: not built yet")
    nodes = (cooler_nodes or config.COOLER_NODES) if coolant else None
    return BUILDERS[layout](id_, physical(parsed), nodes)
