"""S6: turbine inlet temperature 400 to 500 C (10 C steps), other variables fixed.

    python -m core.studies.s6_t_turb

Designs: the best-payout design of each of layouts 2 to 6 (baseline) and every
named design. Design-point re-solve at each T_turb (recuperator effectiveness
0.90, cooler pinch 5 K), same feasibility checks.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402

from core.studies.common import (NAMED, STUDIES, baseline, econ, sweep, table, task,  # noqa: E402
                                 winners, write_summary)

NAME = "s6_t_turb"
FOLDER = STUDIES / NAME
T_TURBS = list(range(400, 501, 10))


def designs():
    raw, ref, m0 = baseline()
    main, _ = econ(raw, m0, ref["ID"])
    pairs = [(f"Best payout L{L}", b["ID"]) for L, b in winners(main)["best"].items() if L != 1]
    labels = {}                      # one entry per ID; a design named twice gets both labels
    for nm, id_ in pairs + list(NAMED.items()):
        labels.setdefault(id_, []).append(nm)
    return {id_: " / ".join(nms) for id_, nms in labels.items()}


def main():
    ds = designs()
    ok, bad = sweep([task(f"{i}|{t}", i, overrides={"T_turb_C": float(t)})
                     for i in ds for t in T_TURBS], FOLDER, "t_turb")
    by = {}
    for r in ok:
        i, t = r["key"].split("|")
        by.setdefault(i, {})[int(t)] = r
    fails = {}
    for b in bad:
        i, t = b["key"].split("|")
        fails.setdefault(i, {})[int(t)] = b["reason"]

    head = ["T_turb C"] + [f"{lab}<br>{i}" for i, lab in ds.items()]
    rows = []
    for t in T_TURBS:
        cells = [t]
        for i in ds:
            if t in by.get(i, {}):
                cells.append(f"{float(by[i][t]['eta']):.5f}")
            else:
                cells.append(f"infeasible ({fails.get(i, {}).get(t, '?')})")
        rows.append(cells)
    slope = []
    for i, lab in ds.items():
        p = by.get(i, {})
        if 400 in p and 500 in p:
            e4, e5 = float(p[400]["eta"]), float(p[500]["eta"])
            slope.append([lab, i, f"{e4:.5f}", f"{e5:.5f}", f"{(e5 - e4) / 100 * 1000:.3f}",
                          f"{float(p[400]['eta_second_law']):.4f}", f"{float(p[500]['eta_second_law']):.4f}"])

    fig, ax = plt.subplots(figsize=(7, 5), dpi=200)
    for i, lab in ds.items():
        p = by.get(i, {})
        ts = sorted(p)
        ax.plot(ts, [float(p[t]["eta"]) for t in ts], "o-", ms=3, label=f"{lab} ({i})")
    ax.set_xlabel("Turbine inlet temperature (C)")
    ax.set_ylabel("Thermal efficiency")
    ax.grid(color="#e6e6e6", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    fig.tight_layout()
    fig.savefig(FOLDER / "eta_vs_T_turb.png", bbox_inches="tight")
    plt.close(fig)

    md = ["# S6: turbine inlet temperature 400 to 500 C", "",
          "Each design re-solved at T_turb = 400 to 500 C in 10 C steps with every other "
          "variable fixed (pressures, T_in, split; recuperator effectiveness 0.90 and cooler "
          "pinch 5 K, i.e. a re-design at each temperature, not off-design). Designs: best "
          "payout of layouts 2 to 6 and the named designs.", "",
          "## eta against T_turb", "", table(head, rows), "",
          "## Change from 400 to 500 C", "",
          table(["design", "ID", "eta 400 C", "eta 500 C", "d eta per 10 C (pp)",
                 "eta_II 400 C", "eta_II 500 C"], slope), "",
          "Plot: eta_vs_T_turb.png.", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
