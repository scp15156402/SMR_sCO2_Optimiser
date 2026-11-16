def feasible(assessments, constraints=None) -> list:
    c = dict(CONSTRAINTS, **(constraints or {}))
    out = []
    for a in assessments:
        bad = []
        # The brief: "Compressor inlet >= 32 degC and >= 7.7 MPa (safe
        # distance from two-phase region)".  Two readings are possible and
        # they disagree for partial cooling, whose pre-compressor sits at an
        # intermediate pressure below 7.7 MPa:
        #
        #   strict   every compressor inlet meets both limits
        #   intent   every compressor inlet is clear of the two-phase
        #            region, which above the critical temperature it is at
        #            any pressure
        #
        # `strict_inlet_pressure` selects between them, defaulting to the
        # literal reading.  Flip it and partial cooling becomes admissible.
        if a.T_inlet_min_c < c["T1_min_c"] - TOL:
            bad.append(f"compressor inlet {a.T_inlet_min_c:.2f} degC "
                       f"< {c['T1_min_c']} degC")
        if c.get("strict_inlet_pressure", True):
            if a.P_inlet_min_mpa < c["P1_min_mpa"] - TOL:
                bad.append(f"compressor inlet {a.P_inlet_min_mpa:.2f} MPa "
                           f"< {c['P1_min_mpa']} MPa")
        elif a.T_margin_k < -TOL:
            bad.append(f"compressor inlet {-a.T_margin_k:.2f} K below "
                       f"the critical temperature")
        if a.pinch_min_k < c["pinch_min_k"] - TOL:
            bad.append(f"pinch {a.pinch_min_k:.2f} K < {c['pinch_min_k']} K")
        if a.P_max_mpa > c["P_max_mpa"] + TOL:
            bad.append(f"max pressure {a.P_max_mpa:.2f} > {c['P_max_mpa']} MPa")
        if a.T_turbine_c > c["T_turbine_max_c"] + TOL:
            bad.append(f"turbine inlet {a.T_turbine_c:.1f} > {c['T_turbine_max_c']} degC")
        if a.split > c["split_max"] + TOL:
            bad.append(f"split {a.split:.3f} > {c['split_max']}")
        out.append(Candidate(assessment=a, ok=not bad, violations=tuple(bad)))
    return out
