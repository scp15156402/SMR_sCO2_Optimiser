# sCO₂ Brayton cycle for a compact SMR — ME 306

A thermodynamic flowsheet solver, five Brayton configurations built on
it, and the SMR optimisation study the solver was written for.

**The recommendation:** a recompression cycle at 20 MPa, split fraction
0.25, 35 °C compressor inlet — 41.41 % thermal efficiency, 0.684
second-law, 87.0 t of power-conversion hardware, 4.02 K of margin above
the critical point, 2.3-year payback against the best feasible
recuperated design. The full case is in `reports/final_report.pdf`.

## Two documents

| | |
|---|---|
| **`reports/final_report.pdf`** (18 pp) | The engineering investigation. What was asked, what was found, what is recommended and why. Start here. |
| **`documentation/theory_and_implementation.pdf`** (126 pp) | Everything, in one document. Part I is the manual -- theory, governing equations, numerical methods, software architecture, every study's workflow, how to reproduce it. Part II is the report above, compiled from the same source file, so the two can never disagree. If you only keep one file, keep this one. |

The split is deliberate: the report answers the assignment, the manual
explains the machine. Neither repeats the other.

## Three layers

| Directory | The question it answers |
|---|---|
| `cycles/` | How do I model and solve a thermodynamic system? |
| `brayton_cycle/` | How do I build each Brayton configuration from that? |
| `project/` | How do I apply those to the SMR sCO₂ problem? |

`cycles/` knows nothing about CO₂, Brayton cycles or this assignment —
verified by stripping comments and searching live code, and by
reproducing the air-standard closed form with an ideal-gas backend to
4.6 × 10⁻¹⁶. It would run a Rankine plant unchanged.

Around them: `tests/` (41 checks), `tools/` (figure, table, register and
consistency generators), `results/` (what the studies produced).

## Install

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install CoolProp pytest
pytest                                              # expect 41 passed
```

Building the documents additionally needs a TeX distribution with
`latexmk`, `pgfplots` and `siunitx`.

## Run

```bash
# the nine studies, in dependency order
python -m project.studies.compare_layouts    # the four configurations
python -m project.studies.sweeps             # pressure and split
python -m project.studies.partial_cooling    # its third pressure level
python -m project.studies.intercooling       # its free pressure level
python -m project.studies.cooling            # coolers and water
python -m project.studies.exergy             # second-law accounting
python -m project.studies.tradeoff           # candidates, front, knee
python -m project.studies.selected_design    # needs tradeoff
python -m project.studies.tolerances         # needs tradeoff

# everything downstream reads what those saved
python -m tools.make_figures         # -> documentation/latex/data/
python -m tools.make_tables          # -> documentation/latex/tables/
python -m tools.make_registers       # -> documentation/registers.md
python -m tools.make_architecture    # -> documentation/architecture.md
python -m tools.check_consistency    # document claims vs saved results

python documentation/latex/build.py  # the manual
python reports/build.py              # the report
```

Each study writes to `results/<study>/` with a `manifest.json`
recording the command, the grids swept, the environment and a SHA-256
fingerprint of the source that produced it. `results/README.md` maps
study → command → output.

**Nothing downstream re-solves.** Figures and tables read saved
results; if a study has not been run they fail with the command to run.
That is deliberate — silently re-solving is what once let a figure and
a recommendation describe different cycles.

## What was found

- **Compare layouts on total conductance, not recuperators.**
  Recompression makes the precooler *smaller*; counting recuperators
  alone overstates its hardware cost by three-quarters (2.51× against
  1.42×).
- **The compressor-inlet optimum is not at the critical point.** 32 →
  35 °C makes compression ~60 % more expensive per kg and efficiency
  still rises, because the warmer inlet eases the capacity-rate
  mismatch. It buys margin too — the one place two objectives stop
  competing.
- **Intercooling does not pay in sCO₂.** It reduces compressor work as
  intended and still loses at every intermediate pressure, because the
  heat it dumps is heat the recuperator would have recovered. The best
  intercooler here is no intercooler.
- **The pressure optimum is the constraint.** Both layouts are still
  improving at 20 MPa.
- **The front is the finding; the point on it is a choice.**

## Verification status

| | |
|---|---|
| Solver numerics, CO₂ properties, whole cycle | **Validated** — closed form, Dostal, Kim (2018) including his optimum |
| Energy closure, discretisation, numerical settings | **Verified** |
| Exergy, case regression, table generation | **Tested** — no external reference for exergy |
| Mass, cost, design selection | **Unvalidated** — the brief's illustrative coefficients |

The recommendation rests partly on that last row. `documentation/registers.md`
has the full matrix and what each piece of evidence does *not* show.

## Known limitations

Off-design and part-load are not modelled; every efficiency is a
design-point number. Exergy totals exclude the heater, which has no
boundary temperature in the model. Turbomachinery mass is constant
across layouts. Pressure drops are stated, not derived from geometry.

**One open question is not technical:** the brief's "compressor inlet ≥
7.7 MPa" admits two readings, and they select different layouts. The
literal reading is used throughout and the consequence is stated — the
entire partial-cooling family is excluded on a pressure limit rather
than on performance. This should be settled with the course staff.

## Map

| | |
|---|---|
| `documentation/architecture.md` | generated: the tree plus every module's API |
| `documentation/registers.md` | generated: study, validation and traceability registers |
| `documentation/usage.md` | operational manual, exact commands |
| `documentation/project_tracker.md` | status at the head, append-only development log |
| `documentation/migration_table.md` | how the two documents were split |
| `results/README.md` | which study produced which file |
