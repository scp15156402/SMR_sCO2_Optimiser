"""Intercooled, recuperated Brayton cycle (two compression stages).

Cooling between stages cuts compression work, because the second stage then
compresses denser fluid.  Expect a smaller gain here than in an ideal-gas
cycle: sCO2 compression work is already small, so there is less to save.
Intercooling also lowers the recuperator's cold inlet temperature, which
changes the duty limits -- whether the extra hardware pays is a result to
compute, not an assumption.

Adding a third stage is three more lines, not a code change.
"""
from cycles import Flowsheet, Node

intercooled = Flowsheet("intercooled", [
    Node("LPC",    "compressor",     {"in": "s1"},  {"out": "s2"}),
    Node("IC",     "cooler",         {"in": "s2"},  {"out": "s3"}),
    Node("HPC",    "compressor",     {"in": "s3"},  {"out": "s4"}),
    Node("RECUP",  "heat_exchanger", {"cold_in": "s4", "hot_in": "s7"},
                                     {"cold_out": "s5", "hot_out": "s8"}),
    Node("HEATER", "heater",         {"in": "s5"},  {"out": "s6"}),
    Node("TURB",   "turbine",        {"in": "s6"},  {"out": "s7"}),
    Node("PC",     "cooler",         {"in": "s8"},  {"out": "s1"}),
])
