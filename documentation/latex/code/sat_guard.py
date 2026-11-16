def limiting_enthalpy(backend, P: float, T: float, direction: str) -> float:
    if backend.has_saturation(P):
        t_sat = backend.T_sat(P)
        if abs(T - t_sat) <= SAT_TOL:
            return backend.h_sat(P, 0.0 if direction == "cooled_to" else 1.0)
    return backend.h_pt(P, T)
