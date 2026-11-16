"""helpers/builders.py: point ID -> cycles.Case.

Every number comes from config.py or from the ID itself; none is typed here.
Pressure drops are zero (config.PRESSURE_DROP), so no dp parameters are set.
"""
from cycles import Case, CoolantPinch, Effectiveness, ThermalPower
from cycles.units import K, MPa, MW, degC

import config
from brayton_cycle import recuperated
from helpers.ids import parse_id, physical

# Fixed role names -> block ids, so every layout fills the same CSV columns.
# cooler_1 is always the cooler feeding the main compressor.
ROLES = {
    2: {"recup_1": "RECUP", "cooler_1": "COOLER"},
}


def _cooler(T_out, coolant):
    """Cooler parameters. coolant=False: no water side (cycle-only, fast)."""
    p = dict(T_out=T_out)
    if coolant:
        p.update(coolant_fluid="Water",
                 coolant_T_in=degC(config.T_WATER_IN_C),
                 coolant=CoolantPinch(K(config.COOLER_PINCH_K)))
    return p


def _recuperated(id_, ph, coolant):
    """Layout 2: simple recuperated (brayton_cycle/recuperated.py)."""
    T_in = degC(ph["T_in_C"])
    return Case(
        name=id_,
        fluid="CO2",
        layout=recuperated,
        size=ThermalPower(MW(config.Q_THERMAL_MW)),
        boundary={"s1": {"T": T_in, "P": MPa(ph["P_low_MPa"])}},
        params={
            "COMP":   dict(eta=config.ETA_COMPRESSOR, P_out=MPa(ph["P_high_MPa"])),
            "RECUP":  dict(spec=Effectiveness(config.RECUP_EFFECTIVENESS)),
            "HEATER": dict(T_out=degC(ph["T_turb_C"])),
            "TURB":   dict(eta=config.ETA_TURBINE),
            "COOLER": _cooler(T_in, coolant),
        },
    )


BUILDERS = {2: _recuperated}


def build(id_, coolant=True):
    """Case for one point ID. Layouts without a builder raise NotImplementedError."""
    parsed = parse_id(id_)
    layout = parsed["layout"]
    if layout not in BUILDERS:
        raise NotImplementedError(f"layout {layout}: not built yet")
    return BUILDERS[layout](id_, physical(parsed), coolant)
