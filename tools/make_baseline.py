"""Write the regression baseline: every case, its key numbers, as committed.

The baseline is what makes a refactor checkable.  Moving files around
cannot be verified by "it still runs" -- it has to still produce the same
numbers, and that means recording them *before* the move and comparing
after.

Only regenerate this deliberately, when a number has changed for a reason
you can state.  Regenerating it to make a failing test pass defeats the
entire purpose.

    python -m tools.make_baseline
"""
from __future__ import annotations

import json
import pathlib

from cycles import solve
from project.cases import CASES

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "baseline.json"

# What to record. Deliberately few: these are the numbers a refactor must
# not move. Recording every stream would make the file fragile against
# harmless changes.
KEYS = ("eta_th", "w_net", "q_in", "q_out", "bwr", "mdot")


def collect() -> dict:
    out = {}
    for name, case in CASES.items():
        r = solve(case)
        if not r.ok:
            out[name] = {"ok": False, "flags": r.flags}
            continue
        out[name] = {"ok": True,
                     **{k: r.metrics[k] for k in KEYS if k in r.metrics}}
    return out


def main():
    data = collect()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    ok = sum(1 for v in data.values() if v["ok"])
    print(f"written: {OUT}  ({ok}/{len(data)} cases solved)")


if __name__ == "__main__":
    main()
