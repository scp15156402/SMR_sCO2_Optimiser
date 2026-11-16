"""Every layout's heat sink, sized against a real cooling-water supply.

The brief gives cooling water at 25 degC and asks R4 for the cooling-water
duty, calling it a key siting constraint for a small modular reactor.  That
needs each cooler modelled as a two-stream exchanger rather than as a wish
that the CO2 arrives at 32 degC.

It is worth doing for every layout rather than just the baseline, because
the layouts differ in how many coolers they have and in what each one does:

    recuperated     one precooler, full flow
    recompression   one precooler, reduced flow
    intercooled     a precooler and an intercooler
    partial cooling two coolers at different pressures, one reduced flow

Those differences are invisible in thermal efficiency and very visible in
cooling-water demand, which is exactly the sort of thing a compactness
argument has to account for.

Pick one spec per cooler.  All four reduce to a coolant flow:

    CoolantFlow      the flow directly, per kg/s of total cycle flow
    CoolantOutlet    the coolant leaves at this temperature
    CoolantRise      the coolant warms by this much
    CoolantPinch     size the exchanger to this minimum approach

Pumping is optional and never guessed.  Give a circuit model and the solver
reports what that stated pressure drop costs; give none and it reports zero
rather than inventing a figure.
"""
from cycles import (CoolantFlow, CoolantPinch, CoolantRise, Pinch,
                    QuadraticDrop)
from cycles.units import K, MPa, degC

from .pdf_baseline import pdf_baseline
from .pdf_intercooled import pdf_intercooled
from .pdf_partial_cooling import pdf_partial_cooling
from .pdf_recompression import pdf_recompression

# 25 degC supply, circuit at 6 bar.  The block's own default would do, but
# stating it here keeps every water-cooled case reading the same.
WATER = dict(coolant_fluid="Water", coolant_T_in=degC(25), coolant_P=MPa(0.6))

# The water flow a 10 K rise produces on the baseline, per kg/s of cycle
# flow: about 1610 kg/s at 100 MWth.  Used to anchor the circuit model and
# as the middle of a sweep.
FLOW_REF_10K = 4.714

# A stated 100 kPa across the water side at that flow, rising as the square
# of flow.  This is an assumption, declared as one -- see the module
# docstring of cycles/physics/hydraulics.py for why nothing here tries to
# derive it from geometry.
CIRCUIT = dict(circuit=QuadraticDrop(dP_ref=100e3, flow_ref=FLOW_REF_10K),
               pump_eta=0.80)

TEN_K = dict(WATER, coolant=CoolantRise(K(10)))
TEN_K_PUMPED = dict(TEN_K, **CIRCUIT)


# --- one cooler ------------------------------------------------------------
baseline_watercooled = pdf_baseline.with_(
    name="baseline_watercooled",
    notes="brief baseline with the precooler sized against 25 degC water",
    params={"COOLER": TEN_K},
)

baseline_pumped = pdf_baseline.with_(
    name="baseline_pumped",
    notes="baseline, water side plus a stated 100 kPa circuit loss",
    params={"COOLER": TEN_K_PUMPED},
)

baseline_watercooled_flow = pdf_baseline.with_(
    name="baseline_watercooled_flow",
    notes="precooler with the water flow given directly",
    params={"COOLER": dict(WATER, coolant=CoolantFlow(FLOW_REF_10K))},
)

baseline_watercooled_pinch = pdf_baseline.with_(
    name="baseline_watercooled_pinch",
    notes="precooler sized to a 5 K approach against the water",
    params={"RECUP": dict(spec=Pinch(K(5))),
            "COOLER": dict(WATER, coolant=CoolantPinch(K(5)))},
)

recompression_watercooled = pdf_recompression.with_(
    name="recompression_watercooled",
    notes="recompression with the precooler sized against 25 degC water",
    params={"PC": TEN_K_PUMPED},
)


# --- two coolers -----------------------------------------------------------
# The intercooled layout rejects heat twice, and the intercooler does it at a
# higher pressure than the precooler.  Same spec, same block, no new code.
intercooled_watercooled = pdf_intercooled.with_(
    name="intercooled_watercooled",
    notes="intercooled layout, both coolers sized against 25 degC water",
    params={"PC": TEN_K_PUMPED, "IC": TEN_K_PUMPED},
)

# Partial cooling also rejects heat twice, but at three pressure levels and
# with the second cooler carrying only part of the flow.
partial_cooling_watercooled = pdf_partial_cooling.with_(
    name="partial_cooling_watercooled",
    notes="partial cooling, both coolers sized against 25 degC water",
    params={"PC1": TEN_K_PUMPED, "PC2": TEN_K_PUMPED},
)
