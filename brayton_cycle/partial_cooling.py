"""Partial cooling cycle (Angelino).

The third flow-splitting layout, and the one the brief asks R4 to weigh
against intercooling.  It differs from recompression in two ways:

  1. The turbine exhausts to a pressure *below* the main compressor inlet.
     A pre-compressor raises it back up.  That makes three pressure levels
     instead of two.
  2. There are two coolers.  The first takes the turbine exhaust down before
     the pre-compressor; the second cools only the fraction that goes to the
     main compressor.

Rejecting the first part of the heat at a lower temperature, and the second
part from only a fraction of the flow, lowers the mean temperature of heat
rejection -- which is what raises efficiency.  Like recompression it also
fixes the pinch, because the low-temperature recuperator's cold side carries
reduced flow.

Dostal found this layout beats recompression below about 20 MPa and loses
above it, so at the brief's 20 MPa ceiling the comparison is genuinely close
and worth computing rather than assuming.

Note what is *not* here: no new block types.  Partial cooling is the same
eight functions wired differently, which is the whole point of the design.
"""
from cycles import Flowsheet, Node

partial_cooling = Flowsheet("partial_cooling", [
    # low-pressure side: turbine exhaust down through both recuperators
    Node("TURB",   "turbine",        {"in": "s6"},  {"out": "s7"}),
    Node("HTR",    "heat_exchanger", {"cold_in": "s4", "hot_in": "s7"},
                                     {"cold_out": "s5", "hot_out": "s8"}),
    Node("LTR",    "heat_exchanger", {"cold_in": "s2", "hot_in": "s8"},
                                     {"cold_out": "s3", "hot_out": "s9"}),

    # first cooler and the pre-compressor: low pressure -> intermediate
    Node("PC1",    "cooler",         {"in": "s9"},  {"out": "s10"}),
    Node("PCOMP",  "compressor",     {"in": "s10"}, {"out": "s11"}),

    # split at the intermediate pressure
    Node("SPLIT",  "splitter",       {"in": "s11"}, {"out": ["s11a", "s11b"]}),

    # main branch: cooled again, then compressed and recuperated
    Node("PC2",    "cooler",         {"in": "s11a"}, {"out": "s1"}),
    Node("MC",     "compressor",     {"in": "s1"},  {"out": "s2"}),

    # recompressed branch: straight to high pressure, bypassing PC2 and the LTR
    Node("RC",     "compressor",     {"in": "s11b"}, {"out": "s12"}),

    Node("MIX",    "mixer",          {"in": ["s3", "s12"]}, {"out": "s4"}),
    Node("HEATER", "heater",         {"in": "s5"},  {"out": "s6"}),
])
