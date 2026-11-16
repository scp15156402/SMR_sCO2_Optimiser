def size(hot_in, hot_out, duty, spec, props, *, fluid, T_in, P,
         circuit=None, pump_eta=0.80, nodes=100, block_id="?") -> CoolantSide:
    if not isinstance(spec, COOLANT_SPECS):
        raise TypeError(
            f"block {block_id!r}: coolant spec must be one of "
            f"{', '.join(c.__name__ for c in COOLANT_SPECS)}, "
            f"got {type(spec).__name__}")

    pc = props(fluid)
    h_in = pc.h_pt(P, T_in)

    def profile_for(flow):
        """A trial coolant flow fixes its outlet enthalpy by energy balance.

        The coolant-side pressure is held at P across the exchanger.  Unlike
        the cycle side, where a 1-2 % drop moves cp enough to shift the
        pinch, a liquid coolant's enthalpy and density barely move over a
        few hundred kPa, so a pressure profile would change nothing
        thermally.  The drop still costs pump work, which is accounted for
        separately below.
        """
        coolant_in = Stream(fluid, P, h_in, flow)
        return hx_profile.build(
            props, hot_in, coolant_in, hot_out.h, duty,
            P_hot_in=hot_in.P, P_hot_out=hot_out.P,
            P_cold_in=P, P_cold_out=P, nodes=nodes)

    def flow_for_outlet(T_out):
        h_out = pc.h_pt(P, T_out)
        if h_out <= h_in:
            raise ValueError(
                f"block {block_id!r}: coolant outlet {T_out:.2f} K is not "
                f"above its inlet {T_in:.2f} K")
        return duty / (h_out - h_in)

    # --- every spec collapses to a flow ---------------------------------
    if isinstance(spec, CoolantFlow):
        flow = spec.value
    elif isinstance(spec, CoolantOutlet):
        flow = flow_for_outlet(spec.value)
    elif isinstance(spec, CoolantRise):
        flow = flow_for_outlet(T_in + spec.value)
    else:                                            # CoolantPinch
        T_hot_in = props(hot_in.fluid).T_ph(hot_in.P, hot_in.h)
        flow = solve_monotone(
            lambda f: profile_for(f).pinch, spec.value,
            flow_for_outlet(T_hot_in - 0.01),        # least coolant
            flow_for_outlet(T_in + 0.5),             # most coolant
            tol=1e-6)

    if flow <= 0.0:
        raise ValueError(f"block {block_id!r}: coolant flow must be positive")

    prof = profile_for(flow)
    T_out = pc.T_ph(P, h_in + duty / flow)

    flags = []
    if prof.pinch <= 0.0:
        flags.append(f"{block_id}: coolant temperature cross, "
                     f"pinch {prof.pinch:.2f} K")

    dP = hydraulics.pressure_drop(circuit, flow)
    if dP >= P:
        flags.append(f"{block_id}: stated coolant pressure drop "
                     f"{dP/1e3:.0f} kPa is at or above the "
                     f"{P/1e3:.0f} kPa operating pressure")
    rho = pc.rho_ph(P, h_in)

    return CoolantSide(
        fluid=fluid, flow=flow, T_in=T_in, T_out=T_out, P=P,
        pinch=prof.pinch, pinch_at=prof.pinch_at,
        UA_per_flow=hx_sizing.ua_from_profile(prof),
        dP=dP, pump_w=hydraulics.pump_work(flow, dP, rho, pump_eta),
        profile=prof, flags=tuple(flags))
