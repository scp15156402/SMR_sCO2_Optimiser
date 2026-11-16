"""Recuperated Brayton cycle -- the project brief's baseline layout.

Turbine exhaust preheats the compressor discharge before the reactor sees it.
This is the Brayton equivalent of a regenerative feedwater heater, and in an
sCO2 cycle the recuperator moves more heat than the reactor supplies, which
is why it dominates size and cost.

Acyclic: the compression and expansion branches are independent (the turbine
inlet temperature is fixed), so the solver evaluates this in a single pass
with no tear.
"""
from cycles import Flowsheet, Node

recuperated = Flowsheet("recuperated", [
    Node("COMP",   "compressor",     {"in": "s1"},  {"out": "s2"}),
    Node("RECUP",  "heat_exchanger", {"cold_in": "s2", "hot_in": "s5"},
                                     {"cold_out": "s3", "hot_out": "s6"}),
    Node("HEATER", "heater",         {"in": "s3"},  {"out": "s4"}),
    Node("TURB",   "turbine",        {"in": "s4"},  {"out": "s5"}),
    Node("COOLER", "cooler",         {"in": "s6"},  {"out": "s1"}),
])
