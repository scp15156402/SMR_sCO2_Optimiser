"""Small numerical kernels shared by blocks and passes."""
from .roots import ConvergenceError, bisect, secant, solve_monotone

__all__ = ["ConvergenceError", "bisect", "secant", "solve_monotone"]
