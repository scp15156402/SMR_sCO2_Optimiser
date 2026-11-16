"""Extract the code excerpts that appear in the theory document.

The excerpts in documentation/ are pulled straight out of the source here,
not retyped, so they cannot drift from what the solver actually does. Run
this before rebuilding the PDF (build.py does it for you).

    python -m tools.make_code_snippets

Writes to documentation/latex/code/.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "documentation" / "latex" / "code"

# name -> (source file, [function or class names to pull])
FUNCTIONS = {
    "isentropic":     ("cycles/physics/isentropic.py",
                       ["isentropic_outlet_h", "compress", "expand"]),
    "duty_limits":    ("cycles/physics/hx_limits.py", ["duty_limits"]),
    "sat_guard":      ("cycles/physics/hx_limits.py", ["limiting_enthalpy"]),
    "hx_profile":     ("cycles/physics/hx_profile.py", ["build"]),
    "ua_sizing":      ("cycles/physics/hx_sizing.py", ["lmtd", "ua_from_profile"]),
    "relation":       ("cycles/blocks/base.py", ["Relation", "drop_relation"]),
    "flow_rules":     ("cycles/blocks/base.py", ["Identity", "Scale", "Sum"]),
    "compressor":     ("cycles/blocks/compressor.py",
                       ["pressure_rules", "flow_rule", "evaluate"]),
    "fixed_outlets":  ("cycles/blocks/heater.py", ["fixed_outlets"]),
    "exergy_specific": ("cycles/physics/exergy.py",
                       ["Environment", "dead_state", "specific"]),
    "exergy_balance": ("cycles/physics/exergy.py", ["_entropy_balance"]),
    "coolant_specs":  ("cycles/specs.py",
                       ["CoolantFlow", "CoolantOutlet", "CoolantRise",
                        "CoolantPinch"]),
    "coolant_size":   ("cycles/physics/coolant.py", ["size"]),
    "circuit_models": ("cycles/physics/hydraulics.py",
                       ["NoPumping", "FixedDrop", "QuadraticDrop",
                        "pressure_drop", "pump_work"]),
    "tear_loop":      ("cycles/passes/tear.py", ["solve"]),
    "ordering":       ("cycles/passes/ordering.py", ["build"]),
    "stream":         ("cycles/stream.py", ["Stream"]),
    "mass_of":        ("project/assessment/mass.py", ["mass_of"]),
    "payback":        ("project/assessment/cost.py", ["payback_years"]),
    "inlets":         ("project/assessment/metrics.py", ["compressor_inlets"]),
    "feasible":       ("project/assessment/moo.py", ["feasible"]),
    "dominance":      ("project/assessment/moo.py",
                       ["_dominates", "pareto_front"]),
    "knee":           ("project/assessment/moo.py", ["knee"]),
    "bisect":         ("cycles/numerics/roots.py", ["bisect"]),
    "solve_monotone": ("cycles/numerics/roots.py", ["solve_monotone"]),
    "secant":         ("cycles/numerics/roots.py", ["secant"]),
    "subst":          ("cycles/numerics/roots.py",
                       ["successive_substitution"]),
    "hx_seek":        ("cycles/blocks/heat_exchanger.py", ["_seek"]),
    "tear_guess":     ("cycles/solve.py", ["_initial_tear_guess"]),
}

# name -> (source file, start marker, end marker)  for fragments of a function
FRAGMENTS = {
    "hx_spec": ("cycles/blocks/heat_exchanger.py",
                "    # --- resolve effectiveness", "    profile = prof("),
    "pressure_propagate": ("cycles/passes/pressure.py",
                           "    # --- propagate both ways", "    missing ="),
    "metrics": ("cycles/solve.py",
                "    # --- cycle metrics", "    if q_in <= 0.0:"),
}

# whole files that are short enough and are themselves the point
WHOLE = {
    "layout_recompression": "brayton_cycle/recompression.py",
    "case_baseline":        "project/cases/pdf_baseline.py",
}


def strip_docstring(src: str) -> str:
    """Drop the leading docstring: the surrounding prose already says it."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    node = tree.body[0] if tree.body else None
    doc = ast.get_docstring(node) if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None
    if not doc:
        return src
    lines = src.splitlines()
    body_start = node.body[0].end_lineno          # 1-indexed, inclusive
    head = lines[:node.body[0].lineno - 1]
    return "\n".join(head + lines[body_start:])


def pull_functions(path: pathlib.Path, names, keep_doc=False) -> str:
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    chunks = []
    for name in names:
        node = next((n for n in tree.body
                     if getattr(n, "name", None) == name), None)
        if node is None:
            raise KeyError(f"{path}: no top-level {name!r}")
        start = min([node.lineno] + [d.lineno for d in
                                     getattr(node, "decorator_list", [])]) - 1
        chunk = "\n".join(lines[start:node.end_lineno])
        chunks.append(chunk if keep_doc else strip_docstring(chunk))
    return "\n\n".join(chunks).rstrip() + "\n"


def pull_fragment(path: pathlib.Path, start: str, end: str) -> str:
    src = path.read_text()
    i = src.index(start)
    j = src.index(end, i)
    return textwrap.dedent(src[i:j]).rstrip() + "\n"


def pull_whole(path: pathlib.Path) -> str:
    """Whole file, minus the module docstring and __future__ import."""
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    skip = 0
    if (tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)):
        skip = tree.body[0].end_lineno
    out = [l for l in lines[skip:]
           if not l.startswith("from __future__")]
    return "\n".join(out).strip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0

    for name, (rel, funcs) in FUNCTIONS.items():
        (OUT / f"{name}.py").write_text(pull_functions(ROOT / rel, funcs))
        n += 1
    for name, (rel, a, b) in FRAGMENTS.items():
        (OUT / f"{name}.py").write_text(pull_fragment(ROOT / rel, a, b))
        n += 1
    for name, rel in WHOLE.items():
        (OUT / f"{name}.py").write_text(pull_whole(ROOT / rel))
        n += 1

    print(f"{n} snippets written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
