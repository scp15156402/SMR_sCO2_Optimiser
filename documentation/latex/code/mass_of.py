def mass_of(result, model: MassModel = MassModel()) -> Mass:
    m = result.metrics
    recup_ua = m["UA_total"] / 1e3                       # kW/K
    cooler_ua = sum(e["coolant_UA_per_flow"] for e in result.blocks.values()
                    if e["kind"] == "cooler"
                    and "coolant_UA_per_flow" in e) * m["mdot"] / 1e3

    extra_compressors = sum(1 for e in result.blocks.values()
                            if e["kind"] == "compressor") - 1
    machines = model.other_t + max(extra_compressors, 0) * model.recompressor_t

    recup_t = recup_ua * model.kg_per_ua / 1000.0
    cooler_t = cooler_ua * model.kg_per_ua / 1000.0
    total = recup_t + cooler_t + machines
    W = m["W_net"] / 1e6                                 # MWe

    return Mass(
        recuperators_t=recup_t,
        coolers_t=cooler_t,
        machines_t=machines,
        total_t=total,
        volume_m3=total / model.density_t_per_m3,
        mwe_per_t=W / total if total else float("nan"),
        mwe_per_m3=W / (total / model.density_t_per_m3) if total else float("nan"),
    )
