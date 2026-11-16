def payback_years(candidate_mass, candidate_cost,
                  base_mass, base_cost) -> float:
    extra_hardware = candidate_cost.hardware_musd - base_cost.hardware_musd
    extra_value = (candidate_cost.annual_energy_musd
                   - base_cost.annual_energy_musd)
    if extra_value <= 0:
        return float("inf")
    return extra_hardware / extra_value
