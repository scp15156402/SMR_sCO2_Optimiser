def duty_limits(props, hot_in, cold_in, P_hot_out, P_cold_out):
    ph = props(hot_in.fluid)
    pc = props(cold_in.fluid)

    T_hot_in = ph.T_ph(hot_in.P, hot_in.h)
    T_cold_in = pc.T_ph(cold_in.P, cold_in.h)

    h_hot_min = limiting_enthalpy(ph, P_hot_out, T_cold_in, "cooled_to")
    h_cold_max = limiting_enthalpy(pc, P_cold_out, T_hot_in, "heated_to")

    q_hot = hot_in.h - h_hot_min
    q_cold = h_cold_max - cold_in.h

    return hot_in.flow * q_hot, cold_in.flow * q_cold
