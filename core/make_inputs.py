"""core/make_inputs.py: grids.py -> data/inputs.csv.

    python -m core.make_inputs [grid names...]    (no names = every grid)

Every axis value is checked against the brief (config.py); a violation is an
error, not a skip. Combinations that are not a physical pressure ordering are
dropped and counted. The file is rebuilt from scratch on every run.
"""
import argparse
import csv
import itertools
from pathlib import Path

import config
import grids
from helpers.ids import AXIS_TO_FIELD, FIELDS, make_id, parse_id, physical

OUT = Path(__file__).resolve().parents[1] / "data" / "inputs.csv"
COLUMNS = ["ID", "grid", "layout", "P_high_MPa", "P_low_MPa", "P_mid_MPa",
           "P_exh_MPa", "T_in_C", "T_turb_C", "split"]
FORMATS = {"P_high_MPa": ".1f", "P_low_MPa": ".1f", "P_mid_MPa": ".1f",
           "P_exh_MPa": ".1f", "T_in_C": ".1f", "T_turb_C": ".0f", "split": ".2f"}


def expand(name, axis, spec):
    """(start, stop, step) inclusive of stop, or an explicit list."""
    if isinstance(spec, tuple):
        start, stop, step = spec
        if step <= 0 or (stop - start) % step:
            raise ValueError(f"grid {name}: axis {axis} {spec} does not land on stop")
        return list(range(start, stop + 1, step))
    return list(spec)


def check_axis(name, layout, axis, values):
    """Raise if any value on this axis breaks a constraint of the brief."""
    limits = {
        "P_high": lambda v: v <= round(config.P_MAX_MPA * 10),
        "T_turb": lambda v: v <= round(config.T_TURBINE_MAX_C),
        "T_in":   lambda v: v >= round(config.T_INLET_MIN_C * 10),
        "split":  lambda v: round(config.SPLIT_MIN * 100) < v <= round(config.SPLIT_MAX * 100),
    }
    if layout in (1, 2, 3, 4, 5):
        limits["P_low"] = lambda v: v >= round(config.P_INLET_MIN_MPA * 10)
    if layout == 6:
        limits["P_mid"] = lambda v: v >= round(config.P_INLET_MIN_MPA * 10)
    ok = limits.get(axis)
    if ok is None:
        return
    for v in values:
        if not isinstance(v, int) or isinstance(v, bool):
            raise ValueError(f"grid {name}: axis {axis} value {v!r} is not an int")
        if not ok(v):
            raise ValueError(f"grid {name}: axis {axis} value {v} breaks the brief")


def ordered(layout, f):
    """Physical pressure ordering; False means drop the combination."""
    if layout in (4, 5):
        return f["Pl"] < f["Pm"] < f["Ph"]
    if layout == 6:
        return f["Pe"] < f["Pm"] < f["Ph"]
    return True


def grid_points(name, spec):
    """Yield field dicts for one grid; return the number dropped."""
    layout = spec["layout"]
    axes = {k: v for k, v in spec.items() if k != "layout"}
    unknown = [a for a in axes if a not in AXIS_TO_FIELD]
    if unknown:
        raise ValueError(f"grid {name}: unknown axes {unknown}")
    fields = sorted(AXIS_TO_FIELD[a] for a in axes)
    if fields != sorted(FIELDS[layout]):
        raise ValueError(f"grid {name}: layout {layout} needs {FIELDS[layout]}, got {fields}")
    values = {}
    for axis, s in axes.items():
        values[axis] = expand(name, axis, s)
        check_axis(name, layout, axis, values[axis])
    names = list(values)
    kept, dropped = [], 0
    for combo in itertools.product(*(values[a] for a in names)):
        f = {AXIS_TO_FIELD[a]: v for a, v in zip(names, combo)}
        if ordered(layout, f):
            kept.append(f)
        else:
            dropped += 1
    return layout, kept, dropped


def build(names):
    rows = {}
    for name in names:
        layout, points, dropped = grid_points(name, grids.GRIDS[name])
        print(f"{name}: {len(points)} points ({dropped} dropped for pressure ordering)")
        for f in points:
            pid = make_id(layout, **f)
            if pid in rows:
                continue
            phys = physical(parse_id(pid))
            row = {"ID": pid, "grid": name, "layout": layout}
            for key, fmt in FORMATS.items():
                row[key] = "" if phys[key] is None else format(phys[key], fmt)
            rows[pid] = row
    return [rows[k] for k in sorted(rows)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("grids", nargs="*", help="grid names (default: all)")
    args = ap.parse_args(argv)
    names = args.grids or list(grids.GRIDS)
    missing = [n for n in names if n not in grids.GRIDS]
    if missing:
        ap.error(f"unknown grids {missing}; known: {list(grids.GRIDS)}")
    rows = build(names)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"total {len(rows)} -> {OUT.relative_to(OUT.parents[1])}")


if __name__ == "__main__":
    main()
