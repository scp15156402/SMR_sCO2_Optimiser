"""Regression tests for the generated tables.

Every test here corresponds to a defect that actually occurred while
`tools/make_tables.py` was being written. None of them is hypothetical,
and that is the point: a regression test earns its place by naming a
mistake that was made once.

The defects, in the order they were found:

  1. Specific work reported as plant power. `metrics["w_net"]` is J/kg;
     multiplying by mass flow is not optional. The generated table said
     0.10 MW for a 36.5 MW plant.
  2. A cooler with no pump circuit printed as `0`, which claims the pump
     work is zero rather than that there is no pump.
  3. Repeated row labels printed in full, and later collapsed into the
     same em dash used for a missing value -- making "same as above" and
     "no such quantity" look identical.
  4. Multi-cooler layouts had no total row, leaving the reader to add up
     the column that the layout comparison actually uses.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from project.studies._io import load

ROOT = pathlib.Path(__file__).resolve().parents[1]
TABLES = ROOT / "documentation" / "latex" / "tables"


@pytest.fixture(scope="module")
def tables():
    """Regenerate the tables, then read them back as text."""
    r = subprocess.run([sys.executable, "-m", "tools.make_tables"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, f"make_tables failed:\n{r.stdout}\n{r.stderr}"
    return {p.stem: p.read_text() for p in TABLES.glob("*.tex")}


def body(text):
    """The data rows: between \\midrule and \\bottomrule, one per line."""
    rows = []
    inside = False
    for line in text.splitlines():
        if line.startswith("\\midrule"):
            inside = True
            continue
        if line.startswith("\\bottomrule"):
            break
        if inside and line.strip().endswith(r"\\"):
            rows.append([c.strip() for c in
                         line.rstrip("\\ ").split("&")])
    return rows


# --- defect 1: specific work vs plant power --------------------------

def test_net_power_is_plant_output_not_specific_work():
    """W_net must be tens of MW, not tenths.

    The failure mode is silent: 0.0958 MW looks like a plausible number
    until you notice the plant is 100 MWth.
    """
    for r in load("layout_comparison", "layouts"):
        assert 20.0 < r["W_net_mwe"] < 60.0, (
            f"{r['layout']}: W_net {r['W_net_mwe']} MW is not a plant "
            f"output for a 100 MWth reactor -- specific work was probably "
            f"not multiplied by mass flow")


def test_net_power_agrees_with_efficiency():
    """W_net / Q_in must equal eta_th. The arithmetic has to close."""
    for r in load("layout_comparison", "layouts"):
        implied = r["W_net_mwe"] / 100.0 * 100.0
        assert abs(implied - r["eta_th_pct"]) < 0.01, (
            f"{r['layout']}: W_net implies {implied:.3f} % but eta_th is "
            f"{r['eta_th_pct']:.3f} %")


def test_first_law_closes_in_the_selected_design():
    """Q_in = W_net + Q_out, from the saved performance table."""
    perf = {r["quantity"]: r["value"]
            for r in load("selected_design", "performance")}
    residual = perf["Q_in"] - perf["W_net"] - perf["Q_out"]
    assert abs(residual) < 1e-3, (
        f"first law does not close in performance.csv: "
        f"{perf['Q_in']} != {perf['W_net']} + {perf['Q_out']} "
        f"(residual {residual:.2e} MW)")


# --- defect 2: missing circuit is not zero ---------------------------

def test_absent_pump_circuit_is_a_dash_not_a_zero(tables):
    """A total row with no pumped cooler must print ---, never 0."""
    rows = body(tables["coolers"])
    totals = [r for r in rows if "total" in r[1]]
    assert totals, "the coolers table lost its total rows"
    for r in totals:
        # duty and pinch have no meaningful total and must be dashed
        assert r[2] == "---", f"total row has a duty of {r[2]!r}, expected ---"
        assert r[4] == "---", f"total row has a pinch of {r[4]!r}, expected ---"


def test_dash_and_zero_are_distinguishable(tables):
    """Somewhere in the tables both must appear, and mean different things."""
    text = "\n".join(tables.values())
    assert "---" in text, "no em dash anywhere: the distinction was lost"
    rows = body(tables["coolers"])
    numeric = [r for r in rows if r[1] not in ("", r"\emph{total}")]
    assert any(c.replace(".", "").replace("-", "").isdigit()
               for r in numeric for c in r[2:]), \
        "no numeric cells found; the table is not carrying data"


# --- defect 3: blank repeated labels ---------------------------------

def test_repeated_layout_label_is_blank_not_dashed(tables):
    """A continuation row says nothing, which is not the same as ---."""
    rows = body(tables["coolers"])
    continuations = [r for r in rows if r[0] == ""]
    assert continuations, (
        "no continuation rows: either the grouping was lost, or repeated "
        "labels are being printed in full")
    for r in continuations:
        assert r[0] != "---", (
            "a repeated row label was rendered as ---, which means "
            "'not applicable' elsewhere in the same table")


# --- defect 4: totals ------------------------------------------------

def test_cooler_totals_are_the_sum_of_their_group(tables):
    """Every total row must equal the rows above it."""
    rows = body(tables["coolers"])
    group, checked = [], 0
    for r in rows:
        if "total" in r[1]:
            want_water = sum(float(g[3]) for g in group)
            want_ua = sum(float(g[5]) for g in group)
            assert abs(float(r[3]) - want_water) < 1.0, (
                f"water total {r[3]} != {want_water:.0f}")
            assert abs(float(r[5]) - want_ua) < 1.0, (
                f"UA total {r[5]} != {want_ua:.0f}")
            checked += 1
            group = []
        elif r[1] != "":
            if r[0] != "":
                group = []
            group.append(r)
    assert checked >= 2, f"only {checked} total rows checked, expected >= 2"


# --- the tables must come from the saved results ---------------------

def test_tables_match_their_saved_source(tables):
    """Spot-check each table against the CSV it claims to read.

    This is the property the whole generator exists for: if a number can
    drift between the results directory and the page, nothing else in
    this file matters.
    """
    cases = [
        ("layout_comparison", ("layout_comparison", "layouts"),
         "eta_th_pct", 1, ".3f"),
        ("state_points", ("selected_design", "state_points"),
         "T_degc", 2, ".2f"),
        ("pareto_front", ("multi_objective", "pareto_front"),
         "mass_t", 2, ".1f"),
        ("intercooling", ("intercooling", "pressure_sweep"),
         "eta_th_pct", 1, ".3f"),
        ("partial_cooling", ("partial_cooling", "pressure_sweep"),
         "eta_th_pct", 1, ".3f"),
    ]
    for name, (study, stem), column, col_index, spec in cases:
        rows = body(tables[name])
        saved = load(study, stem)
        assert len(rows) >= len(saved), (
            f"{name}.tex has {len(rows)} rows but {study}/{stem}.csv has "
            f"{len(saved)}")
        for printed, source in zip(rows, saved):
            assert printed[col_index] == f"{source[column]:{spec}}", (
                f"{name}.tex row disagrees with {study}/{stem}.csv: "
                f"printed {printed[col_index]!r}, saved "
                f"{source[column]:{spec}!r}")


def test_every_table_has_data(tables):
    """Every table the generator declares must exist and carry rows.

    Checked against the generator's own registry rather than a hardcoded
    count, so adding a table does not break this test while a table that
    silently fails to generate still does.
    """
    from tools.make_tables import TABLES
    missing = set(TABLES) - set(tables)
    assert not missing, f"declared but not generated: {sorted(missing)}"
    for name, text in tables.items():
        assert body(text), f"{name}.tex has no data rows"
        assert r"\toprule" in text and r"\bottomrule" in text, \
            f"{name}.tex is not a complete booktabs tabular"
