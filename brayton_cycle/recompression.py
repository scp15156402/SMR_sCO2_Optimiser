"""Recompression Brayton cycle.

Fixes the recuperator pinch.  Near the critical point the high-pressure cold
stream has a much larger specific heat than the low-pressure hot stream, so
with equal mass flows their capacity rates are badly mismatched and the
curves touch inside the exchanger.  Sending a fraction x of the flow around
the precooler and compressing it warm reduces the cold-side flow in the
low-temperature recuperator until the capacity rates match.

The price is that the recompressor works on warm, less dense fluid, so it
costs more per kilogram than the main compressor.  That trade gives x an
interior optimum, typically near 0.3.

Cyclic: the LTR needs its hot inlet from the HTR, which needs the mixer,
which needs the LTR.  The solver tears s8 and iterates.
"""
from cycles import Flowsheet, Node

recompression = Flowsheet("recompression", [
    Node("MC",    "compressor",     {"in": "s1"},  {"out": "s2"}),
    Node("LTR",   "heat_exchanger", {"cold_in": "s2", "hot_in": "s8"},
                                    {"cold_out": "s3", "hot_out": "s9"}),
    Node("SPLIT", "splitter",       {"in": "s9"},  {"out": ["s9a", "s9b"]}),
    Node("PC",    "cooler",         {"in": "s9a"}, {"out": "s1"}),
    Node("RC",    "compressor",     {"in": "s9b"}, {"out": "s10"}),
    Node("MIX",   "mixer",          {"in": ["s3", "s10"]}, {"out": "s4"}),
    Node("HTR",   "heat_exchanger", {"cold_in": "s4", "hot_in": "s7"},
                                    {"cold_out": "s5", "hot_out": "s8"}),
    Node("HEATER","heater",         {"in": "s5"},  {"out": "s6"}),
    Node("TURB",  "turbine",        {"in": "s6"},  {"out": "s7"}),
])
