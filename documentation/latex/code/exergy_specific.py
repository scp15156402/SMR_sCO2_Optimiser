@dataclass(frozen=True)
class Environment:
    T0: float = T0_DEFAULT
    P0: float = P0_DEFAULT

@lru_cache(maxsize=None)
def dead_state(backend, T0: float, P0: float):
    return backend.h_pt(P0, T0), backend.s_pt(P0, T0)

def specific(backend, env: Environment, P: float, h: float,
             s: float | None = None) -> float:
    h0, s0 = dead_state(backend, env.T0, env.P0)
    if s is None:
        s = backend.s_ph(P, h)
    return (h - h0) - env.T0 * (s - s0)
