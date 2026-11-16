"""The two enthalpy limits on a counterflow exchanger.

Written in enthalpy, not temperature, because the two streams' specific heats
differ strongly in an sCO2 recuperator.  Which limit binds is therefore a
*result* of the calculation, not something you can assume from the geometry.

  warm-end limit : the cold stream cannot leave hotter than the hot stream enters
  cold-end limit : the hot stream cannot leave colder than the cold stream enters

Both are returned per unit *total cycle* mass flow, so the caller never has to
remember which side carries which fraction.
"""
from __future__ import annotations

# how close to the saturation temperature counts as being on it, in kelvin
SAT_TOL = 1e-3


def limiting_enthalpy(backend, P: float, T: float, direction: str) -> float:
    """Enthalpy at (P, T), resolved when that point lies on a saturation line.

    Inside a two-phase dome P and T are *not* independent: every quality from
    0 to 1 shares one temperature, so a plain h(P, T) lookup is ambiguous.

    The duty limits are not really asking for "the" enthalpy there, though.
    They are asking for the extreme enthalpy that still satisfies a
    temperature constraint, and that *is* well defined:

        direction="cooled_to"   the stream may not end up colder than T.
                                Below the saturated-liquid enthalpy it would
                                be subcooled and colder than T_sat, so the
                                smallest admissible enthalpy is h_f.

        direction="heated_to"   the stream may not end up hotter than T.
                                Above the saturated-vapour enthalpy it would
                                be superheated and hotter than T_sat, so the
                                largest admissible enthalpy is h_g.

    Away from the dome -- which is every state in an sCO2 cycle -- this is
    just h(P, T) and costs one extra comparison.
    """
    if backend.has_saturation(P):
        t_sat = backend.T_sat(P)
        if abs(T - t_sat) <= SAT_TOL:
            return backend.h_sat(P, 0.0 if direction == "cooled_to" else 1.0)
    return backend.h_pt(P, T)


def duty_limits(props, hot_in, cold_in, P_hot_out, P_cold_out):
    """Return (Q_hot_limited, Q_cold_limited), both in W per kg/s of total flow.

    Q_hot_limited  -- hot stream cooled all the way to the cold inlet temperature
    Q_cold_limited -- cold stream heated all the way to the hot inlet temperature
    """
    ph = props(hot_in.fluid)
    pc = props(cold_in.fluid)

    T_hot_in = ph.T_ph(hot_in.P, hot_in.h)
    T_cold_in = pc.T_ph(cold_in.P, cold_in.h)

    h_hot_min = limiting_enthalpy(ph, P_hot_out, T_cold_in, "cooled_to")
    h_cold_max = limiting_enthalpy(pc, P_cold_out, T_hot_in, "heated_to")

    q_hot = hot_in.h - h_hot_min
    q_cold = h_cold_max - cold_in.h

    return hot_in.flow * q_hot, cold_in.flow * q_cold


def max_duty(props, hot_in, cold_in, P_hot_out, P_cold_out):
    """Q_max = min of the two limits, with which one bound."""
    q_h, q_c = duty_limits(props, hot_in, cold_in, P_hot_out, P_cold_out)
    if q_h <= q_c:
        return q_h, "hot"
    return q_c, "cold"
