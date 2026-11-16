def build(props, hot_in, cold_in, hot_out_h, Q, P_hot_in, P_hot_out,
          P_cold_in, P_cold_out, nodes=100) -> Profile:
    ph = props(hot_in.fluid)
    pc = props(cold_in.fluid)
    f_hot, f_cold = hot_in.flow, cold_in.flow

    xs, Th, Tc, dT = [], [], [], []
    for j in range(nodes + 1):
        x = j / nodes
        h_c = cold_in.h + x * Q / f_cold
        h_h = hot_out_h + x * Q / f_hot
        P_c = _lerp(P_cold_in, P_cold_out, x)
        P_h = _lerp(P_hot_out, P_hot_in, x)
        t_h = ph.T_ph(P_h, h_h)
        t_c = pc.T_ph(P_c, h_c)
        xs.append(x)
        Th.append(t_h)
        Tc.append(t_c)
        dT.append(t_h - t_c)

    return Profile(tuple(xs), tuple(Th), tuple(Tc), tuple(dT), Q)
