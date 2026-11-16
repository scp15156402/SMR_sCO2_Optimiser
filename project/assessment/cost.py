"""The brief's cost proxy: hardware against the energy it earns.

Two numbers do all the work:

    installed hardware   ~US$250 per kg
    electricity          ~US$70 per MWh, over ~7000 h/yr

The brief calls this a *proxy* and it is right to.  It has no fuel cost, no
O&M, no financing, no discounting and no civil works, so the absolute
dollars mean very little.  What it is good for is the comparison the project
actually asks: does the extra hardware of a better layout earn its keep
against the extra electricity it makes?

Two ways of saying the same thing are reported, because they answer
different questions:

  * **Annualised cost** puts hardware and energy on one axis so designs can
    be ranked.  Hardware is a one-off and electricity is per year, so the
    two cannot be added without a lifetime; `LIFETIME_YEARS` makes that
    assumption explicit rather than hiding it inside a formula.
  * **Payback** against a reference design needs no lifetime at all, which
    makes it the more honest of the two. It is what the brief's own worked
    example computes.
"""
from __future__ import annotations

from dataclasses import dataclass

USD_PER_KG = 250.0         # installed hardware, brief
USD_PER_MWH = 70.0         # electricity value, brief
HOURS_PER_YEAR = 7000.0    # brief

# Not in the brief.  Needed only to put a one-off hardware cost and a
# recurring energy value on the same axis; stated here so a reader can
# change it and see what moves.
LIFETIME_YEARS = 30.0


@dataclass(frozen=True)
class CostModel:
    usd_per_kg: float = USD_PER_KG
    usd_per_mwh: float = USD_PER_MWH
    hours_per_year: float = HOURS_PER_YEAR
    lifetime_years: float = LIFETIME_YEARS


@dataclass(frozen=True)
class Cost:
    hardware_musd: float          # one-off
    annual_energy_musd: float     # per year, at full output
    annualised_musd: float        # hardware/lifetime - energy value
    cost_proxy_musd: float        # the MOO objective; lower is better


def cost_of(result, mass, model: CostModel = CostModel()) -> Cost:
    """Hardware cost and energy value for one solved cycle."""
    W = result.metrics["W_net"] / 1e6                     # MWe
    hardware = mass.total_t * 1000.0 * model.usd_per_kg / 1e6
    annual_energy = (W * model.hours_per_year
                     * model.usd_per_mwh / 1e6)
    annualised = hardware / model.lifetime_years - annual_energy
    return Cost(
        hardware_musd=hardware,
        annual_energy_musd=annual_energy,
        annualised_musd=annualised,
        # Objective 3: hardware plus the heat-input penalty, as US$/yr.
        # Lower is better, so a design that earns more electricity for the
        # same hardware scores lower.
        cost_proxy_musd=annualised,
    )


def payback_years(candidate_mass, candidate_cost,
                  base_mass, base_cost) -> float:
    """Years for a design's extra hardware to be repaid by its extra output.

    The brief's own worked example, steps 4 to 8.  Needs no lifetime
    assumption, which is why it is the figure to quote.  Negative means the
    design is both heavier and worse -- it never pays back.
    """
    extra_hardware = candidate_cost.hardware_musd - base_cost.hardware_musd
    extra_value = (candidate_cost.annual_energy_musd
                   - base_cost.annual_energy_musd)
    if extra_value <= 0:
        return float("inf")
    return extra_hardware / extra_value
