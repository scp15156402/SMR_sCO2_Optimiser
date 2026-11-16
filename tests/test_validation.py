"""The external-validation suite, as assertions.

These wrap the two validators rather than reimplementing them, for a
reason: their printed tables are the source of Appendix B, so they must
keep printing.  `pytest` gives you the pass/fail gate; running the module
directly gives you the table.

    pytest tests/test_validation.py -v        # the gate
    python -m tests.validate_literature       # the table

The distinction these preserve (see the master document's chapter on
validation):

  * `validate_literature` is **validation** -- the solver against somebody
    else's published numbers (Dostal's state table and machines, Kim's
    whole recompression cycle including the location of its optimum).
  * `validate_exergy` is **verification** -- internal consistency of the
    second-law layer against balances it must satisfy by construction.
    Passing it says the arithmetic is right, not that the model is.
"""
from __future__ import annotations

from tests import validate_exergy, validate_literature


def test_literature_validation():
    """9 checks against Dostal (2004) and Kim (2018). External reference."""
    assert validate_literature.main() == 0


def test_exergy_verification():
    """16 internal consistency checks. NOT external validation."""
    assert validate_exergy.main() == 0
