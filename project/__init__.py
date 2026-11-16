"""The ME 306 sCO2 project.

Everything here is a *user* of the `cycles` solver, which is treated as a
black box: give it a Case, get back a Result.  Nothing in this folder
reaches inside the solver, and nothing in the solver knows this folder
exists.
"""
