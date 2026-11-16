def pressure_rules(params):
    if "P_out" in params:
        return [], {"out": params["P_out"]}
    if "ratio" in params:
        return [ratio_relation("in", "out", params["ratio"])], {}
    return [], {}          # outlet pressure comes from elsewhere in the sheet

def flow_rule(params):
    from .base import Identity
    return Identity((("in", "out"),))

def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    st = inlets["in"]
    eta = require(params, "eta", block_id)
    p = props(st.fluid)

    s_in = p.s_ph(st.P, st.h)
    h_s = isentropic_outlet_h(p, P_out["out"], s_in)
    h = compress(st.h, h_s, eta)

    out = Stream(st.fluid, P_out["out"], h, st.flow)
    w = h - st.h
    return {"out": out}, {
        "kind": "compressor",
        "w": w,                       # J/kg of this stream
        "w_isentropic": h_s - st.h,
        "w_total": w * st.flow,       # J per kg of total cycle flow
        "w_lost": w - (h_s - st.h),   # loss indicator: real minus ideal
        "ratio": P_out["out"] / st.P,
    }
