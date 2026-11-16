def _initial_tear_guess(case, props, P, tears):
    p = props(case.fluid)
    T_lo = min(st["T"] for st in case.boundary.values())
    heater_T = [prm["T_out"] for bid, prm in case.params.items()
                if get(case.layout.node(bid).type).TYPE == "heater" and "T_out" in prm]
    T_hi = max(heater_T) if heater_T else T_lo * 2.0
    T_guess = T_lo + 0.25 * (T_hi - T_lo)
    return {sid: p.h_pt(P[sid], T_guess) for sid in tears}
