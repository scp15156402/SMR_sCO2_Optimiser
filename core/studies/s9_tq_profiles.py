"""S9: temperature-duty (T-Q) profiles of every exchanger of the named designs.

    python -m core.studies.s9_tq_profiles

Each named design solved once with 100 slices on every recuperator and cooler.
One figure per exchanger (pinch marked) and one combined figure per design.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402

from cycles import solve                                                 # noqa: E402
from core.studies.common import NAMED, STUDIES, _apply, table, write_summary  # noqa: E402
from helpers.builders import ROLES, build                                # noqa: E402
from helpers.ids import parse_id                                         # noqa: E402

NAME = "s9_tq_profiles"
FOLDER = STUDIES / NAME
NODES = 100


def exchangers(id_, r):
    """[(role, block id, profile, kind)] for every recuperator and cooler."""
    roles = ROLES[parse_id(id_)["layout"]]
    out = []
    for role in ("recup_1", "recup_2", "cooler_1", "cooler_2"):
        bid = roles.get(role)
        if not bid:
            continue
        b = r.blocks[bid]
        prof = b.get("profile") if role.startswith("recup") else b.get("coolant_profile")
        out.append((role, bid, prof, "recuperator" if role.startswith("recup") else "cooler (CO2 / water)"))
    return out


def draw(ax, prof, mdot, title):
    q = [x * prof.Q * mdot / 1e6 for x in prof.x]               # MW from the cold end
    th = [t - 273.15 for t in prof.T_hot]
    tc = [t - 273.15 for t in prof.T_cold]
    ax.plot(q, th, color="#d6452a", lw=1.4, label="hot side")
    ax.plot(q, tc, color="#2a78d6", lw=1.4, label="cold side")
    i = min(range(len(prof.dT)), key=lambda k: prof.dT[k])
    ax.plot([q[i], q[i]], [tc[i], th[i]], color="#222", lw=1)
    ax.annotate(f"pinch {prof.pinch:.2f} K", (q[i], (tc[i] + th[i]) / 2), xytext=(6, 0),
                textcoords="offset points", fontsize=7, va="center")
    ax.set_title(title, fontsize=8)
    ax.set_xlabel("Duty from cold end (MW)", fontsize=8)
    ax.set_ylabel("T (C)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(color="#e6e6e6", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")


def main():
    _apply({})
    FOLDER.mkdir(parents=True, exist_ok=True)
    rows, md_fail = [], []
    for nm, id_ in NAMED.items():
        try:
            r = solve(build(id_, coolant=True, cooler_nodes=NODES))
            if not r.ok:
                raise RuntimeError(f"not solved: {r.flags}")
            mdot = r.metrics["mdot"]
            ex = exchangers(id_, r)
            fig_all, axs = plt.subplots(1, len(ex), figsize=(3.6 * len(ex), 3.4), dpi=200, squeeze=False)
            for k, (role, bid, prof, kind) in enumerate(ex):
                title = f"{bid} ({role}, {kind})"
                fig, ax = plt.subplots(figsize=(5, 3.6), dpi=200)
                draw(ax, prof, mdot, f"{nm}: {id_}\n{title}")
                fig.tight_layout()
                fig.savefig(FOLDER / f"TQ_{id_}_{bid}.png", bbox_inches="tight")
                plt.close(fig)
                draw(axs[0][k], prof, mdot, title)
                rows.append([nm, id_, bid, role, f"{prof.Q * mdot / 1e6:.2f}", f"{prof.pinch:.2f}",
                             f"{prof.pinch_at:.2f}", f"{prof.dT[0]:.2f}", f"{prof.dT[-1]:.2f}"])
            fig_all.suptitle(f"{nm}: {id_}", fontsize=9)
            fig_all.tight_layout()
            fig_all.savefig(FOLDER / f"TQ_{id_}_all.png", bbox_inches="tight")
            plt.close(fig_all)
        except Exception as exc:
            md_fail.append([nm, id_, f"{type(exc).__name__}: {exc}"])

    md = ["# S9: exchanger temperature profiles (T-Q)", "",
          f"Each named design solved with {NODES} slices on every recuperator and cooler "
          "(baseline settings: effectiveness 0.90, cooler pinch 5 K, no pressure drop). Duty is "
          "measured from the cold end (x = 0: cold stream in, hot stream out). Pinch location "
          "x is the fraction of duty from the cold end.", "",
          table(["design", "ID", "exchanger", "role", "duty MW", "pinch K", "pinch at x",
                 "dT cold end K", "dT hot end K"], rows), ""]
    if md_fail:
        md += ["**Failed:**", "", table(["design", "ID", "error"], md_fail), ""]
    md += ["Plots: TQ_<ID>_<exchanger>.png per exchanger, TQ_<ID>_all.png per design.", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
