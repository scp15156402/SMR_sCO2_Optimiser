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
