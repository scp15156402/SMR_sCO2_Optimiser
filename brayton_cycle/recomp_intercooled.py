"""Recompression Brayton cycle with an intercooled main compressor (layout 5).

The recompression layout with its main compressor split into two stages and
an intercooler between them. The recompressor still takes its fraction x of
the LTR hot outlet straight to high pressure, bypassing the precooler.

Cyclic like recompression: the solver tears one stream and iterates.
"""
from cycles import Flowsheet, Node

recomp_intercooled = Flowsheet("recomp_intercooled", [
    Node("LPC",    "compressor",     {"in": "s1"},  {"out": "s2"}),
    Node("IC",     "cooler",         {"in": "s2"},  {"out": "s3"}),
    Node("HPC",    "compressor",     {"in": "s3"},  {"out": "s4"}),
    Node("LTR",    "heat_exchanger", {"cold_in": "s4", "hot_in": "s10"},
                                     {"cold_out": "s5", "hot_out": "s11"}),
    Node("SPLIT",  "splitter",       {"in": "s11"}, {"out": ["s11a", "s11b"]}),
    Node("PC",     "cooler",         {"in": "s11a"}, {"out": "s1"}),
    Node("RC",     "compressor",     {"in": "s11b"}, {"out": "s12"}),
    Node("MIX",    "mixer",          {"in": ["s5", "s12"]}, {"out": "s6"}),
    Node("HTR",    "heat_exchanger", {"cold_in": "s6", "hot_in": "s9"},
                                     {"cold_out": "s7", "hot_out": "s10"}),
    Node("HEATER", "heater",         {"in": "s7"},  {"out": "s8"}),
    Node("TURB",   "turbine",        {"in": "s8"},  {"out": "s9"}),
])
