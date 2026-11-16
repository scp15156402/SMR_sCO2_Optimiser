"""Generate every numerical table in the documents from saved results.

Before this existed, the reference tables were typed by hand from a
terminal. That is the one remaining way a wrong number can reach a page:
the solver is tested, the studies are saved, the figures read the saved
files -- and then a human retypes a column and nobody notices.

Each table below names the study it reads and the columns it takes.
Nothing here computes anything; if a number is wrong, the study that
produced it is wrong, which is the property worth having.

Output goes to `documentation/latex/tables/*.tex`, one `tabular` per
file, included with \\input{}. They carry no caption and no float
wrapper, so the document controls placement and wording while this
controls the numbers.

    python -m tools.make_tables
"""
from __future__ import annotations

import pathlib
import sys

from project.studies._io import load

OUT = pathlib.Path(__file__).resolve().parents[1] / "documentation" / "latex" \
    / "tables"


# Three different things a cell can be, which must not look alike:
#   a number            -> formatted
#   NOT_APPLICABLE      -> an em dash. The quantity does not exist here
#                          (a pinch has no total; a cooler with no pump
#                          circuit has no pump work). Writing 0 would be
#                          a false claim.
#   "" (empty string)   -> genuinely blank, used for a repeated row label
#                          that would be noise if printed again.
NOT_APPLICABLE = object()


# Characters that are ordinary in a CSV and special in LaTeX. Study
# output carries identifiers like eta_th and energy_tol straight from the
# source, so escaping has to happen here rather than being left to
# whoever writes the table into a document.
_TEX = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def escape(text: str) -> str:
    """Make a data string safe in LaTeX text mode.

    Deliberately not applied to values this module writes itself --
    \\emph{total} is markup, not data -- so it is called only on strings
    that came out of a CSV.
    """
    if text.startswith("\\"):          # markup this module produced
        return text
    return "".join(_TEX.get(c, c) for c in text)


def fmt(v, spec):
    if v is NOT_APPLICABLE or v is None:
        return "---"
    if v == "":
        return ""
    if spec is None:
        return escape(str(v))
    return f"{v:{spec}}"


def table(path, align, header, rows, cols, specs, rules=()):
    """Write one booktabs tabular.

    rules -- row indices (0-based) after which to draw a \\midrule, for
    tables with groups in them."""
    lines = [f"\\begin{{tabular}}{{@{{}}{align}@{{}}}}", "\\toprule"]
    lines += [" & ".join(header) + r" \\", "\\midrule"]
    for i, r in enumerate(rows):
        cells = [fmt(r.get(c, NOT_APPLICABLE), s)
                 for c, s in zip(cols, specs)]
        lines.append(" & ".join(cells) + r" \\")
        if i in rules:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    path.write_text("\n".join(lines))
    return len(rows)


def layout_comparison():
    rows = load("layout_comparison", "layouts")
    return table(
        OUT / "layout_comparison.tex", "lrrrrr",
        ["Layout", r"$\eta_{th}$ [\%]", r"$W_{net}$ [MW$_e$]", "BWR",
         r"Recup.\ $UA$", r"Cooler $UA$"],
        rows,
        ["layout", "eta_th_pct", "W_net_mwe", "back_work_ratio",
         "recuperator_ua_kw_k", "cooler_ua_kw_k"],
        [None, ".3f", ".2f", ".4f", ".0f", ".0f"])


def total_conductance():
    rows = load("layout_comparison", "layouts")
    return table(
        OUT / "total_conductance.tex", "lrrrrr",
        ["Layout", r"$\eta_{th}$ [\%]", "Recup.", "Coolers", "Total",
         r"$\times$ base"],
        rows,
        ["layout", "eta_th_pct", "recuperator_ua_kw_k", "cooler_ua_kw_k",
         "total_ua_kw_k", "ua_ratio_vs_recuperated"],
        [None, ".3f", ".0f", ".0f", ".0f", ".2f"])


def coolers():
    rows = load("cooling", "per_cooler")
    # Blank the repeated layout name so a group reads as a group, and add
    # a total line wherever a layout has more than one cooler -- the
    # total is what the layout comparison actually uses, so leaving the
    # reader to add the column up would be a gap.
    by_layout = {}
    for r in rows:
        by_layout.setdefault(r["layout"], []).append(r)
    out = []
    for name, group in by_layout.items():
        for i, r in enumerate(group):
            d = dict(r)
            d["layout"] = name if i == 0 else ""
            out.append(d)
        if len(group) > 1:
            pumps = [g["pump_kw"] for g in group if g["pump_kw"] != ""]
            out.append({
                "layout": "", "cooler": r"\emph{total}", # A total duty is not what this table is for, and a total
                # pinch is not a quantity at all. Neither is zero.
                "duty_mw": NOT_APPLICABLE,
                "water_kg_s": sum(g["water_kg_s"] for g in group),
                "coolant_pinch_k": NOT_APPLICABLE,
                "coolant_ua_kw_k": sum(g["coolant_ua_kw_k"] for g in group),
                "pump_kw": sum(pumps) if pumps else NOT_APPLICABLE,
            })
    return table(
        OUT / "coolers.tex", "llrrrrr",
        ["Layout", "Cooler", "Duty [MW]", "Water [kg/s]", "Pinch [K]",
         r"$UA$", "Pump [kW]"],
        out,
        ["layout", "cooler", "duty_mw", "water_kg_s", "coolant_pinch_k",
         "coolant_ua_kw_k", "pump_kw"],
        [None, None, ".1f", ".0f", ".2f", ".0f", ".0f"])


def water_sweep():
    rows = load("cooling", "water_sweep")
    return table(
        OUT / "water_sweep.tex", "rrrrrrr",
        ["Water [kg/s]", r"$T_{w,out}$ [\si{\celsius}]", "Pinch [K]",
         "at $x$", r"$UA$", "Pump [kW]", r"$\eta_{net}$ [\%]"],
        rows,
        ["water_kg_s", "water_T_out_degc", "coolant_pinch_k", "pinch_at_x",
         "coolant_ua_kw_k", "pump_kw", "eta_net_of_pump_pct"],
        [".0f", ".1f", ".2f", ".2f", ".0f", ".0f", ".3f"])


def intercooling():
    rows = load("intercooling", "pressure_sweep")
    return table(
        OUT / "intercooling.tex", "rrrrr",
        [r"$P_{mid}$ [MPa]", r"$\eta_{th}$ [\%]", "BWR", r"Recup.\ $UA$",
         r"vs base [pts]"],
        rows,
        ["P_mid_mpa", "eta_th_pct", "back_work_ratio", "recup_ua_kw_k",
         "delta_eta_points"],
        [".2f", ".3f", ".4f", ".0f", "+.3f"])


def partial_cooling():
    rows = load("partial_cooling", "pressure_sweep")
    return table(
        OUT / "partial_cooling.tex", "rrrrrl",
        [r"$P_{low}$ [MPa]", r"$\eta_{th}$ [\%]", "BWR", "Mass [t]",
         r"$P_{in,min}$ [MPa]", "Strict?"],
        rows,
        ["P_low_mpa", "eta_th_pct", "back_work_ratio", "mass_t",
         "P_inlet_min_mpa", "feasible_strict"],
        [".1f", ".3f", ".4f", ".1f", ".2f", None])


def state_points():
    """Appendix A's centrepiece: the recommended cycle, state by state."""
    rows = load("selected_design", "state_points")
    return table(
        OUT / "state_points.tex", "lrrrrr",
        ["Stream", "$P$ [MPa]", r"$T$ [\si{\celsius}]",
         "$h$ [kJ/kg]", r"$s$ [kJ/kg\,K]", r"$\dot m$ [kg/s]"],
        rows,
        ["stream", "P_mpa", "T_degc", "h_kj_kg", "s_kj_kgk", "flow_kg_s"],
        [None, ".3f", ".2f", ".2f", ".4f", ".2f"])


def performance():
    rows = load("selected_design", "performance")
    return table(
        OUT / "performance.tex", "lrl",
        ["Quantity", "Value", "Unit"],
        rows, ["quantity", "value", "unit"], [None, None, None])


def pareto_front():
    rows = load("multi_objective", "pareto_front")
    return table(
        OUT / "pareto_front.tex", "lrrrrr",
        ["Design", r"$\eta_{th}$ [\%]", "Mass [t]", r"MW$_e$/t",
         "Margin [K]", "Cost [M\\$/yr]"],
        rows,
        ["name", "eta_th_pct", "mass_t", "mwe_per_t", "T_margin_k",
         "cost_proxy_musd"],
        [None, ".2f", ".1f", ".3f", ".2f", ".2f"])


def exergy_components():
    """Destruction by component for one layout, for the teaching chapter.

    The balance table is per-layout; this is the breakdown inside one of
    them. Recompression, because that is the recommended configuration
    and the one the chapter argues about.
    """
    rows = [r for r in load("exergy", "by_component")
            if r["layout"] == "recompression"]
    # Computable first, largest first; the unavailable one last, so the
    # reader meets the numbers before the gap in them.
    have = sorted((r for r in rows if r["exergy_destroyed_mw"] != ""),
                  key=lambda r: -r["exergy_destroyed_mw"])
    missing = [r for r in rows if r["exergy_destroyed_mw"] == ""]
    for r in missing:
        r = dict(r)
    out = have + [dict(r, exergy_destroyed_mw=NOT_APPLICABLE,
                       fraction_pct=NOT_APPLICABLE) for r in missing]
    return table(
        OUT / "exergy_components.tex", "llrr",
        ["Block", "Kind", r"$\dot E_D$ [\si{\mega\watt}]",
         r"Share [\si{\percent}]"],
        out, ["block", "kind", "exergy_destroyed_mw", "fraction_pct"],
        [None, None, ".2f", ".1f"])


def exergy_balance():
    rows = load("exergy", "balance")
    return table(
        OUT / "exergy_balance.tex", "lrrrrl",
        ["Layout", "Supplied", "To work", "Destroyed", "Shed", "Complete?"],
        rows,
        ["layout", "supplied_mw", "to_work_mw", "destroyed_known_mw",
         "shed_mw", "complete"],
        [None, ".2f", ".2f", ".2f", ".2f", None])


def tolerance_sensitivity():
    rows = [r for r in load("tolerance_sensitivity", "sweep")
            if r["solved"] == "yes"]
    return table(
        OUT / "tolerances.tex", "llrrr",
        ["Setting", "Value", r"$\eta_{th}$ [\%]", r"$\Delta\eta$ [pts]",
         r"$\Delta UA$ [\%]"],
        rows,
        ["setting", "value", "eta_th_pct", "delta_points", "delta_ua_pct"],
        [None, None, ".6f", ".2e", ".3f"])


TABLES = {
    "layout_comparison": layout_comparison,
    "total_conductance": total_conductance,
    "coolers": coolers,
    "water_sweep": water_sweep,
    "intercooling": intercooling,
    "partial_cooling": partial_cooling,
    "state_points": state_points,
    "performance": performance,
    "pareto_front": pareto_front,
    "exergy_balance": exergy_balance,
    "exergy_components": exergy_components,
    "tolerances": tolerance_sensitivity,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for name, fn in TABLES.items():
        try:
            n = fn()
        except FileNotFoundError as e:
            missing.append((name, str(e).split("\n")[0]))
            continue
        print(f"  {name + '.tex':<28}{n:>4} rows")
    if missing:
        print("\n  could not generate:")
        for name, why in missing:
            print(f"    {name}: {why}")
        return 1
    print(f"\n{len(TABLES)} tables in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
