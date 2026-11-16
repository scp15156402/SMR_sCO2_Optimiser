"""core/plots.py: every figure in out/.

    python -m core.plots

Reads data/results_econ.csv and data/states.csv; never re-solves the cycle.
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
import numpy as np                                                  # noqa: E402
from CoolProp.CoolProp import PropsSI                               # noqa: E402

from helpers.builders import build                                  # noqa: E402
from helpers.ids import parse_id, physical                          # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "out"
DPI = 200
NAMES = {1: "1 simple", 2: "2 recuperated", 3: "3 recompression",
         4: "4 recup + intercool", 5: "5 recomp + intercool", 6: "6 Angelino"}
COLORS = {1: "#7f7f7f", 2: "#1f77b4", 3: "#d62728", 4: "#2ca02c", 5: "#9467bd", 6: "#ff7f0e"}
FOLDERS = {"knee": "Knee", "topsis": "Top_N_topsis", "eta": "Top_N_efficiency",
           "mass": "Top_N_mass", "payout": "Top_N_payout", "best": "Best_per_layout"}


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _f(r, k):
    return float(r[k])


def _save(fig, name):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def pareto_plot(rows):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for L in sorted({int(r["layout"]) for r in rows}):
        sel = [r for r in rows if int(r["layout"]) == L]
        ax.scatter([_f(r, "mass_t") for r in sel], [_f(r, "payout_usd") / 1e6 for r in sel],
                   s=12, alpha=0.6, color=COLORS[L], label=NAMES[L])
    front = sorted((r for r in rows if r["pareto"] == "1"), key=lambda r: _f(r, "mass_t"))
    ax.plot([_f(r, "mass_t") for r in front], [_f(r, "payout_usd") / 1e6 for r in front],
            "k-", lw=1.2, label="Pareto front")
    for r in rows:
        if r["knee"] == "1":
            ax.plot(_f(r, "mass_t"), _f(r, "payout_usd") / 1e6, "k*", ms=16,
                    mfc="gold", label=f"knee {r['ID']}")
    ax.set_xlabel("PCS mass [t]")
    ax.set_ylabel("lifetime payout [million USD]")
    ax.set_title("Lifetime payout vs mass, all feasible designs")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    return _save(fig, "pareto_payout_vs_mass.png")


def eta_mass_plot(rows):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for L in sorted({int(r["layout"]) for r in rows}):
        sel = [r for r in rows if int(r["layout"]) == L]
        ax.scatter([_f(r, "mass_t") for r in sel], [_f(r, "eta") * 100 for r in sel],
                   s=12, alpha=0.6, color=COLORS[L], label=NAMES[L])
    ax.set_xlabel("PCS mass [t]")
    ax.set_ylabel("thermal efficiency [%]")
    ax.set_title("Efficiency vs mass, all feasible designs")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    return _save(fig, "eta_vs_mass.png")


def eta_pr_plot(rows):
    sel = [r for r in rows if r["layout"] == "2"]
    lines = defaultdict(list)
    for r in sel:
        ph = physical(parse_id(r["ID"]))
        if ph["T_turb_C"] == 500 and abs(ph["P_low_MPa"] - 7.7) < 1e-9:
            lines[ph["T_in_C"]].append((_f(r, "pressure_ratio"), _f(r, "eta")))
    fig, ax = plt.subplots(figsize=(7, 5))
    for T in sorted(lines):
        pts = sorted(lines[T])
        ax.plot([p for p, _ in pts], [e * 100 for _, e in pts], "o-", ms=4, label=f"T_in {T:g} °C")
    ax.set_xlabel("pressure ratio P_high / P_low")
    ax.set_ylabel("thermal efficiency [%]")
    ax.set_title("Layout 2, T_turb 500 °C, P_low 7.7 MPa")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    return _save(fig, "eta_vs_pressure_ratio.png")


def eta_split_plot(rows):
    sel = []
    for r in rows:
        if r["layout"] == "3":
            ph = physical(parse_id(r["ID"]))
            if abs(ph["P_low_MPa"] - 7.7) < 1e-9:
                sel.append((ph, r))
    if not sel:
        return None
    best_T = max(sel, key=lambda t: _f(t[1], "eta"))[0]["T_in_C"]
    lines = defaultdict(list)
    for ph, r in sel:
        if ph["T_in_C"] == best_T:
            lines[ph["P_high_MPa"]].append((ph["split"], _f(r, "eta")))
    fig, ax = plt.subplots(figsize=(7, 5))
    for P in sorted(lines):
        pts = sorted(lines[P])
        ax.plot([x for x, _ in pts], [e * 100 for _, e in pts], "o-", ms=4, label=f"P_high {P:g} MPa")
    ax.set_xlabel("split fraction x (to recompressor)")
    ax.set_ylabel("thermal efficiency [%]")
    ax.set_title(f"Layout 3, P_low 7.7 MPa, T_in {best_T:g} °C (best), T_turb 500 °C\n"
                 "(feasible points only)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    return _save(fig, "eta_vs_split.png")


_DOME = None


def _dome():
    global _DOME
    if _DOME is None:
        Tc = PropsSI("Tcrit", "CO2")
        T = np.linspace(PropsSI("Ttriple", "CO2") + 0.5, Tc - 0.05, 120)
        sl = [PropsSI("S", "T", t, "Q", 0, "CO2") / 1e3 for t in T]
        sv = [PropsSI("S", "T", t, "Q", 1, "CO2") / 1e3 for t in T]
        _DOME = (np.concatenate([sl, sv[::-1]]), np.concatenate([T, T[::-1]]) - 273.15)
    return _DOME


def _isobar(P, h1, h2, n=40):
    """T-s path at constant pressure between two enthalpies (heat exchange)."""
    hs = np.linspace(h1, h2, n)
    return ([PropsSI("S", "P", P, "H", h, "CO2") / 1e3 for h in hs],
            [PropsSI("T", "P", P, "H", h, "CO2") - 273.15 for h in hs])


def ts_plot(id_, tag, states):
    st = {s["stream"]: s for s in states}
    layout = build(id_, coolant=False).layout
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ds, dT = _dome()
    ax.plot(ds, dT, color="0.6", lw=1, label="CO2 saturation dome")
    for node in layout.nodes:
        ins = [s for s in node.inlet_streams() if s in st]
        outs = [s for s in node.outlet_streams() if s in st]
        for a in ins:
            for b in outs:
                A, B = st[a], st[b]
                Pa, Pb = float(A["P_MPa"]) * 1e6, float(B["P_MPa"]) * 1e6
                ha, hb = float(A["h_kJ_kg"]) * 1e3, float(B["h_kJ_kg"]) * 1e3
                if node.type in ("heater", "cooler", "heat_exchanger") and abs(Pa - Pb) < 1:
                    if node.type == "heat_exchanger" and {a, b} not in (
                            {node.inlets.get("hot_in"), node.outlets.get("hot_out")},
                            {node.inlets.get("cold_in"), node.outlets.get("cold_out")}):
                        continue
                    s_, T_ = _isobar(Pa, ha, hb)
                    color = {"heater": "#d62728", "cooler": "#1f77b4"}.get(node.type, "#2ca02c")
                elif node.type in ("compressor", "turbine"):
                    s_ = [float(A["s_kJ_kgK"]), float(B["s_kJ_kgK"])]
                    T_ = [float(A["T_C"]), float(B["T_C"])]
                    color = "k"
                else:                                   # splitter / mixer: no process line
                    continue
                ax.plot(s_, T_, color=color, lw=1.4)
    for sid, s in st.items():
        x, y = float(s["s_kJ_kgK"]), float(s["T_C"])
        ax.plot(x, y, "o", color="k", ms=3)
        ax.annotate(sid[1:], (x, y), textcoords="offset points", xytext=(4, 3), fontsize=7)
    ax.set_xlabel("s [kJ/(kg K)]")
    ax.set_ylabel("T [°C]")
    ax.set_title(f"{tag}: {id_}")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    folder = FOLDERS[tag.split("_")[0]]
    return _save(fig, f"{folder}/TS_{tag}_{id_}.png")


def main():
    rows = _read(DATA / "results_econ.csv")
    made = [pareto_plot(rows), eta_mass_plot(rows), eta_pr_plot(rows), eta_split_plot(rows)]
    states = defaultdict(list)
    tags = {}
    for s in _read(DATA / "states.csv"):
        states[s["ID"]].append(s)
        tags[s["ID"]] = s["tags"].split()
    n_ts = 0
    for id_, ts in sorted(tags.items()):
        for t in ts:
            ts_plot(id_, t, states[id_])
            n_ts += 1
    print(f"{len([m for m in made if m])} summary plots, {n_ts} T-s diagrams -> {OUT.name}/")


if __name__ == "__main__":
    main()
