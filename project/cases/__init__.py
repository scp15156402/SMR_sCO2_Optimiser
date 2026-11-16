"""Run definitions: a layout plus every number it needs.

Cases are frozen; `case.with_(...)` returns a modified copy.  That is how a
validation case, a sensitivity variant or an optimiser's trial point is
built -- never by editing one in place.
"""
from .air_brayton_ideal import air_brayton_ideal, air_brayton_real
from .pdf_baseline import pdf_baseline, pdf_baseline_dp
from .literature import kim_2018, kim_case
from .pdf_intercooled import (intercooled_case, pdf_intercooled,
                              pdf_intercooled_geometric)
from .pdf_partial_cooling import pdf_partial_cooling
from .pdf_recompression import pdf_recompression, pdf_recompression_pinch
from .pdf_watercooled import (baseline_pumped, baseline_watercooled,
                              baseline_watercooled_flow,
                              baseline_watercooled_pinch,
                              intercooled_watercooled,
                              partial_cooling_watercooled,
                              recompression_watercooled)

CASES = {c.name: c for c in (
    pdf_baseline, pdf_baseline_dp,
    pdf_recompression, pdf_recompression_pinch,
    pdf_partial_cooling,
    pdf_intercooled, pdf_intercooled_geometric,
    baseline_watercooled, baseline_watercooled_pinch,
    baseline_watercooled_flow, baseline_pumped,
    recompression_watercooled, intercooled_watercooled,
    partial_cooling_watercooled,
    air_brayton_ideal, air_brayton_real,
    kim_2018,
)}

__all__ = list(CASES) + ["CASES", "intercooled_case", "kim_case"]
