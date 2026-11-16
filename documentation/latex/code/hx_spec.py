# --- resolve effectiveness from whichever spec was given ----------------
if q_max == 0.0:
    eps = 0.0
elif isinstance(spec, Effectiveness):
    eps = spec.value
elif isinstance(spec, Pinch):
    # pinch falls as effectiveness rises -> monotone decreasing
    eps = _seek(lambda e: prof(e).pinch, spec.value, warm)
elif isinstance(spec, UAperFlow):
    def ua_of(e):
        ua = hx_sizing.ua_from_profile(prof(e))
        return ua if ua == ua else 1e30      # NaN -> treat as unreachable
    eps = _seek(ua_of, spec.value, warm)
else:
    raise TypeError(
        f"block {block_id!r}: spec must be Effectiveness, Pinch or "
        f"UAperFlow, got {type(spec).__name__}"
    )

Q = eps * q_max
h_hot_out = hot_in.h - Q / hot_in.flow if hot_in.flow else hot_in.h
h_cold_out = cold_in.h + Q / cold_in.flow if cold_in.flow else cold_in.h

hot_out = Stream(hot_in.fluid, P_out["hot_out"], h_hot_out, hot_in.flow)
cold_out = Stream(cold_in.fluid, P_out["cold_out"], h_cold_out, cold_in.flow)

extras = {
    "kind": "heat_exchanger",
    "Q": Q,                                   # W per kg/s of total flow
    "Q_max": q_max,
    "binding_limit": binding,
    "effectiveness": eps,
    "shortfall": (1.0 - eps) * q_max,         # loss indicator: heat not recovered
    "flags": flags,
}

if not diagnostics:
    return {"hot_out": hot_out, "cold_out": cold_out}, extras
