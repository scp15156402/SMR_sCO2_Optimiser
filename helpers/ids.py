"""helpers/ids.py: point IDs, built from and parsed back to grid-unit integers.

ID format (PLAN.md): L{layout}_Ph{P_high}_Pl{P_low}_T{T_in}_Tt{T_turb}[_Pm..][_Pe..][_x..]
Integer units: pressure 0.1 MPa, T_in 0.1 degC, T_turb 1 degC, split 0.01.
"""
import re

# Fields carried by each layout's ID, in ID order.
FIELDS = {
    1: ("Ph", "Pl", "T", "Tt"),
    2: ("Ph", "Pl", "T", "Tt"),
    3: ("Ph", "Pl", "T", "Tt", "x"),
    4: ("Ph", "Pl", "T", "Tt", "Pm"),
    5: ("Ph", "Pl", "T", "Tt", "Pm", "x"),
    6: ("Ph", "T", "Tt", "Pm", "Pe", "x"),   # no Pl: main compressor inlet is P_mid
}

# grids.py axis name -> ID field.
AXIS_TO_FIELD = {
    "P_high": "Ph", "P_low": "Pl", "T_in": "T", "T_turb": "Tt",
    "P_mid": "Pm", "P_exh": "Pe", "split": "x",
}

# ID field -> (physical key, divisor).
_PHYSICAL = {
    "Ph": ("P_high_MPa", 10),
    "Pl": ("P_low_MPa", 10),
    "Pm": ("P_mid_MPa", 10),
    "Pe": ("P_exh_MPa", 10),
    "T":  ("T_in_C", 10),
    "Tt": ("T_turb_C", 1),
    "x":  ("split", 100),
}


def make_id(layout, **fields):
    """Build the ID string. Values are non-negative ints in grids.py units."""
    if layout not in FIELDS:
        raise ValueError(f"unknown layout {layout!r}")
    expected = FIELDS[layout]
    missing = [f for f in expected if f not in fields]
    extra = [f for f in fields if f not in expected]
    if missing or extra:
        raise ValueError(f"layout {layout}: missing {missing}, extra {extra}")
    parts = [f"L{layout}"]
    for f in expected:
        v = fields[f]
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise ValueError(f"layout {layout}: field {f} must be a non-negative int, got {v!r}")
        parts.append(f"{f}{v:03d}")
    return "_".join(parts)


def parse_id(id_):
    """Parse an ID back to {"layout": int, <field>: int, ...}."""
    if not isinstance(id_, str):
        raise ValueError(f"ID must be a string, got {id_!r}")
    parts = id_.split("_")
    m = re.fullmatch(r"L(\d)", parts[0])
    if not m or int(m.group(1)) not in FIELDS:
        raise ValueError(f"malformed ID {id_!r}: bad layout prefix")
    layout = int(m.group(1))
    expected = FIELDS[layout]
    if len(parts) - 1 != len(expected):
        raise ValueError(f"malformed ID {id_!r}: expected fields {expected}")
    out = {"layout": layout}
    for f, part in zip(expected, parts[1:]):
        m = re.fullmatch(rf"{f}(\d{{3,}})", part)
        if not m:
            raise ValueError(f"malformed ID {id_!r}: expected field {f}, got {part!r}")
        out[f] = int(m.group(1))
    if make_id(layout, **{f: out[f] for f in expected}) != id_:
        raise ValueError(f"malformed ID {id_!r}: not in canonical form")
    return out


def physical(parsed):
    """Convert parse_id output to real units. Keys not on the layout are None."""
    out = {key: None for key, _ in _PHYSICAL.values()}
    for f in FIELDS[parsed["layout"]]:
        key, div = _PHYSICAL[f]
        out[key] = parsed[f] / div
    return out
