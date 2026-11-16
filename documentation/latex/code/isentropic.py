def isentropic_outlet_h(backend, P_out: float, s_in: float) -> float:
    return backend.h_ps(P_out, s_in)

def compress(h_in: float, h_s: float, eta: float) -> float:
    return h_in + (h_s - h_in) / eta

def expand(h_in: float, h_s: float, eta: float) -> float:
    return h_in - eta * (h_in - h_s)
