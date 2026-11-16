"""S2: compressor-inlet temperature drift with the exchangers frozen (off-design proxy).

    python -m core.studies.s2_tin_drift

For each named design: recuperators held at their design absolute UA (UAperFlow
iterated on mass flow), pressures and split fixed, Q_th fixed at 100 MW, T_in
from 32.0 to 36.0 C in 0.25 K steps. The solver's cooler has only a pinch spec
(CoolantPinch) and its CO2 outlet is pinned at T_in, so coolers cannot be frozen
at a UA: they keep the 5 K pinch spec and the cooler UA they would need is
reported instead.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402

from core.studies.common import (COLUMNS, NAMED, STUDIES, fnum, sweep, table, task,  # noqa: E402
                                 write_summary)
from helpers.builders import ROLES                                       # noqa: E402
from helpers.ids import parse_id                                         # noqa: E402

NAME = "s2_tin_drift"
FOLDER = STUDIES / NAME
T_INS = [32.0 + 0.25 * k for k in range(17)]
COLS = COLUMNS + ["flags"]


def design_ua():
    """{name: (ID, {block id: absolute UA in W/K} of the recuperators, design row)}."""
    ok, bad = sweep([task(f"design:{i}", i) for i in NAMED.values()], FOLDER, "design")
    if bad:
        raise RuntimeError(f"design points did not solve: {bad}")
    rows = {r["ID"]: r for r in ok}
    out = {}
    for nm, id_ in NAMED.items():
        r, roles = rows[id_], ROLES[parse_id(id_)["layout"]]
        out[nm] = (id_, {roles[k]: float(r[f"UA_{k}"]) * 1e3 for k in ("recup_1", "recup_2")
                         if k in roles and r[f"UA_{k}"] != ""}, r)
    return out


def main():
    tasks, designs = [], design_ua()
    for nm, (id_, ua, _) in designs.items():
        tasks += [task(f"{nm}|{t:.2f}", id_, overrides={"T_in_C": t}, freeze=ua) for t in T_INS]
    ok, bad = sweep(tasks, FOLDER, "drift", columns=COLS)
    by = {}
    for r in ok:
        nm, t = r["key"].split("|")
        by.setdefault(nm, {})[float(t)] = r

    md = ["# S2: compressor-inlet temperature drift (off-design proxy)", "",
          "For each named design the recuperators are frozen at their design absolute UA "
          "(UAperFlow, iterated until the mass flow settles), pressures and split are fixed, "
          "heat input stays 100 MWth, and T_in is moved from 32.0 to 36.0 C in 0.25 K steps "
          "(both coolers deliver T_in).", "",
          "**Cooler:** the solver's cooler accepts only a pinch spec and its CO2 outlet is "
          "pinned at T_in, so the coolers could not be frozen at a UA. They keep the 5 K pinch "
          "spec (so the cooler pinch is 5 K by construction) and the cooler UA they *would* "
          "need is reported instead.", "",
          "**Limitations:** fixed isentropic efficiencies, no compressor or turbine maps, fixed "
          "pressures and split, no control action. This is a sensitivity estimate, not a true "
          "off-design calculation. Points whose recuperator pinch falls below 5 K are kept and "
          "flagged.", ""]
    if bad:
        md += ["**Failed points:**", "", table(["key", "reason"], [[b["key"], b["reason"]] for b in bad]), ""]

    fig_all, ax_all = plt.subplots(figsize=(7, 5), dpi=200)
    for nm, (id_, ua, d) in designs.items():
        pts = by.get(nm, {})
        t_des = float(d["T_in_C"])
        rows = []
        for t in sorted(pts):
            r = pts[t]
            rows.append([f"{t:.2f}", f"{float(r['eta']):.5f}", f"{float(r['W_net_MW']):.2f}",
                         fnum(r["pinch_recup_1"], ".2f"), fnum(r["pinch_recup_2"], ".2f"),
                         fnum(r["pinch_cooler_1"], ".2f"),
                         f"{sum(float(r[k] or 0) for k in ('UA_cooler_1', 'UA_cooler_2')):.0f}",
                         f"{float(r['rho_comp_in']):.1f}", r.get("flags", "") or "-"])
        md += [f"## {nm}: {id_} (design T_in {t_des:g} C; recuperator UA "
               + ", ".join(f"{b} {v / 1e3:.0f} kW/K" for b, v in ua.items()) + ")", "",
               table(["T_in C", "eta", "W_net MW", "pinch recup_1 K", "pinch recup_2 K",
                      "cooler pinch K", "cooler UA needed kW/K", "rho comp in kg/m3", "flags"], rows), ""]
        if pts:
            ts = sorted(pts)
            e0 = float(pts[ts[0]]["eta"])
            e_des = min(pts.items(), key=lambda kv: abs(kv[0] - t_des))[1]
            md += [f"eta {e0:.4f} at {ts[0]:g} C -> {float(pts[ts[-1]]['eta']):.4f} at {ts[-1]:g} C; "
                   f"mean slope {(float(pts[ts[-1]]['eta']) - e0) / (ts[-1] - ts[0]) * 100:.2f} "
                   f"percentage points per K. Design-point eta (frozen model) {float(e_des['eta']):.5f} "
                   f"vs design solve {float(d['eta']):.5f}.", ""]
            fig, axs = plt.subplots(2, 2, figsize=(9, 6.5), dpi=200)
            x = ts
            axs[0, 0].plot(x, [float(pts[t]["eta"]) for t in x], "o-", ms=3)
            axs[0, 0].set_ylabel("eta")
            axs[0, 1].plot(x, [float(pts[t]["W_net_MW"]) for t in x], "o-", ms=3)
            axs[0, 1].set_ylabel("W_net (MW)")
            for k, lab in (("pinch_recup_1", "recup_1"), ("pinch_recup_2", "recup_2"),
                           ("pinch_cooler_1", "cooler_1")):
                ys = [pts[t][k] for t in x]
                if all(y != "" for y in ys):
                    axs[1, 0].plot(x, [float(y) for y in ys], "o-", ms=3, label=lab)
            axs[1, 0].axhline(5, color="#999", lw=0.8, ls="--")
            axs[1, 0].set_ylabel("pinch (K)")
            axs[1, 0].legend(fontsize=7, frameon=False)
            axs[1, 1].plot(x, [float(pts[t]["rho_comp_in"]) for t in x], "o-", ms=3)
            axs[1, 1].set_ylabel("compressor inlet density (kg/m3)")
            for a in axs.flat:
                a.set_xlabel("T_in (C)")
                a.axvline(t_des, color="#bbb", lw=0.8)
                a.grid(color="#e6e6e6", lw=0.6)
                a.tick_params(labelsize=8)
            fig.suptitle(f"{nm}: {id_} (frozen recuperator UA)", fontsize=9)
            fig.tight_layout()
            fig.savefig(FOLDER / f"drift_{id_}.png", bbox_inches="tight")
            plt.close(fig)
            ax_all.plot(x, [float(pts[t]["eta"]) for t in x], "o-", ms=3, label=f"{nm} ({id_})")
    ax_all.set_xlabel("Compressor inlet temperature T_in (C)")
    ax_all.set_ylabel("Thermal efficiency")
    ax_all.grid(color="#e6e6e6", lw=0.6)
    for s in ("top", "right"):
        ax_all.spines[s].set_visible(False)
    ax_all.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    fig_all.tight_layout()
    fig_all.savefig(FOLDER / "eta_vs_T_in_all.png", bbox_inches="tight")
    plt.close(fig_all)
    md += ["Plots: drift_<ID>.png per design, eta_vs_T_in_all.png combined.", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
