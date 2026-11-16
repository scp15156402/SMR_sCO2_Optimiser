"""Simple Brayton cycle: compress, heat, expand, reject.

The baseline with no regeneration.  For sCO2 this performs poorly despite a
low back-work ratio, because the turbine exhaust leaves very hot and all of
that heat is thrown away in the precooler.  That is the argument for the
recuperator, and this layout exists to make it quantitatively.
"""
from cycles import Flowsheet, Node

simple = Flowsheet("simple", [
    Node("COMP",   "compressor", {"in": "s1"}, {"out": "s2"}),
    Node("HEATER", "heater",     {"in": "s2"}, {"out": "s3"}),
    Node("TURB",   "turbine",    {"in": "s3"}, {"out": "s4"}),
    Node("COOLER", "cooler",     {"in": "s4"}, {"out": "s1"}),
])
