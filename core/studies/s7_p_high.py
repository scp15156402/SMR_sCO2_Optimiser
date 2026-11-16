"""S7: P_high from 14 to 20 MPa in 0.25 MPa steps for each named design.

    python -m core.studies.s7_p_high

Other variables fixed; design-point re-solve (effectiveness 0.90, cooler pinch
5 K). Payout uses the baseline M0. Is eta / payout still rising at 20 MPa?
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402

import config                                                            # noqa: E402
from core.economics import compute                                       # noqa: E402
from core.studies.common import (NAMED, STUDIES, baseline, sweep, table, task,  # noqa: E402
                                 write_summary)

NAME = "s7_p_high"
FOLDER = STUDIES / NAME
P_HIGHS = [14.0 + 0.25 * k for k in range(25)]


def main():
    _, ref, m0 = baseline()
    config.M0_T = m0
    ok, bad = sweep([task(f"{nm}|{p:.2f}", i, overrides={"P_high_MPa": p})
                     for nm, i in NAMED.items() for p in P_HIGHS], FOLDER, "p_high")
    econ = {r["key"]: r for r in compute(ok)}       # payout at the baseline M0
    by = {}
    for k, r in econ.items():
        nm, p = k.split("|")
        by.setdefault(nm, {})[float(p)] = r
    fails = {b["key"]: b["reason"] for b in bad}

    md = ["# S7: P_high from 14 to 20 MPa", "",
          "Each named design re-solved with P_high from 14 to 20 MPa in 0.25 MPa steps, every "
          "other variable fixed (design-point solve: effectiveness 0.90, cooler pinch 5 K). "
          f"Payout at the baseline M0 = {m0:.3f} t, N = 10. Slopes near the limit are the "
          "one-sided differences over the last 0.5 MPa (19.5 -> 20 MPa).", ""]
    summ = []
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200)
    for nm, id_ in NAMED.items():
        p = by.get(nm, {})
        rows = []
        for ph in P_HIGHS:
            r = p.get(ph)
            if r is None:
                rows.append([f"{ph:.2f}", "infeasible", fails.get(f"{nm}|{ph:.2f}", "?"), "", ""])
            else:
                rows.append([f"{ph:.2f}", f"{float(r['eta']):.5f}", f"{r['mass_t']:.2f}",
                             f"{r['payout_usd'] / 1e6:.3f}", f"{float(r['UA_total']):.0f}"])
        md += [f"## {nm}: {id_}", "",
               table(["P_high MPa", "eta", "mass t", "payout M$", "UA_total kW/K"], rows), ""]
        if 20.0 in p and 19.5 in p:
            de = (float(p[20.0]["eta"]) - float(p[19.5]["eta"])) / 0.5
            dp = (p[20.0]["payout_usd"] - p[19.5]["payout_usd"]) / 0.5
            best = max(p.values(), key=lambda r: r["payout_usd"])
            summ.append([nm, id_, f"{de * 100:+.3f}", f"{dp / 1e6:+.3f}",
                         "yes" if de > 0 else "no", "yes" if dp > 0 else "no",
                         f"{float(best['P_high_MPa']):.2f}"])
        ps = sorted(p)
        axs[0].plot(ps, [float(p[x]["eta"]) for x in ps], "o-", ms=2.5, label=nm)
        axs[1].plot(ps, [p[x]["payout_usd"] / 1e6 for x in ps], "o-", ms=2.5, label=nm)
    for a, lab in zip(axs, ("Thermal efficiency", "10-year payout (M$)")):
        a.set_xlabel("P_high (MPa)")
        a.set_ylabel(lab)
        a.grid(color="#e6e6e6", lw=0.6)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    axs[1].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FOLDER / "p_high_sweep.png", bbox_inches="tight")
    plt.close(fig)
    md[4:4] = ["## Near the 20 MPa limit", "",
               table(["design", "ID", "d eta / dP near 20 MPa (pp per MPa)",
                      "d payout / dP near 20 MPa (M$ per MPa)", "eta still rising", "payout still rising",
                      "P_high of max payout MPa"], summ), ""]
    md += ["Plot: p_high_sweep.png.", ""]
    write_summary(FOLDER, md)


if __name__ == "__main__":
    main()
