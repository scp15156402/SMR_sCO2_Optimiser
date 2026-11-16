"""What a solved cycle would weigh, from the brief's own figures.

The brief gives one conversion and three fixed items:

    PCHE recuperator    ~2.5 kg per kW/K of UA
    recompressor        ~1.5 t added
    precooler           "scales with heat rejected per MWe"
    baseline PCS        ~60 t and ~120 m3, of which the recuperator is ~10 t

Two readings had to be made, and both are stated rather than buried.

**The precooler.** The brief is vague where it is precise about the
recuperator.  Since both are printed-circuit exchangers doing the same job
in the same technology, the same 2.5 kg per kW/K is applied to the
precooler's UA.  That is a reading, not a quotation, and it matters: the
precooler is the larger exchanger, so it carries more mass than the
recuperator in every layout.

**Volume.** The brief gives a baseline volume (120 m3) and a baseline mass
(60 t) but no volume-per-UA.  Their ratio is 0.5 t/m3, so mass is converted
to volume at that density throughout.  Crude, and it means volume carries no
information mass does not -- which is worth knowing before anyone reads a
MWe/m3 figure as independent evidence.

A sanity check worth noting: the brief assumes a ~10 t baseline recuperator,
and 2.5 kg/(kW/K) applied to this solver's independently computed 3967 kW/K
gives 9.9 t.  The two agree without being made to.
"""
from __future__ import annotations

from dataclasses import dataclass

KG_PER_UA = 2.5            # kg per kW/K, brief
RECOMPRESSOR_T = 1.5       # t, brief
BASELINE_PCS_T = 60.0      # t, brief
BASELINE_RECUP_T = 10.0    # t, brief ("~25% of 10 t baseline")
BASELINE_VOLUME_M3 = 120.0 # m3, brief

# Everything that is not an exchanger: turbine, generator, main compressor,
# piping, structure.  The brief gives no breakdown, so it is taken as the
# baseline PCS mass less its recuperator, and held constant across layouts.
# That is conservative for recompression (which adds a machine, counted
# separately) and silent about turbine size changing with flow.
OTHER_T = BASELINE_PCS_T - BASELINE_RECUP_T

DENSITY_T_PER_M3 = BASELINE_PCS_T / BASELINE_VOLUME_M3


@dataclass(frozen=True)
class MassModel:
    kg_per_ua: float = KG_PER_UA
    recompressor_t: float = RECOMPRESSOR_T
    other_t: float = OTHER_T
    density_t_per_m3: float = DENSITY_T_PER_M3


@dataclass(frozen=True)
class Mass:
    recuperators_t: float
    coolers_t: float
    machines_t: float
    total_t: float
    volume_m3: float
    mwe_per_t: float
    mwe_per_m3: float


def mass_of(result, model: MassModel = MassModel()) -> Mass:
    """Mass and volume of one solved cycle.

    Exchanger mass comes from conductance the solver computed; machine mass
    is the brief's fixed allowance plus 1.5 t for each compressor beyond the
    first, since the baseline's single compressor is already inside
    `other_t`.
    """
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
