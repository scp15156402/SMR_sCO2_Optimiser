# project

The ME 306 sCO2 project. Everything here is a *user* of the `cycles` solver.

```
../brayton_cycle/   topology only — which blocks, wired to which streams
cases/     numbers only — a layout plus every parameter it needs
runs/      scripts that produce output
```

No file in this folder reaches inside the solver, and no file in the solver
knows this one exists.

## Layouts

| file | what it is |
|---|---|
| `simple.py` | compress, heat, expand, reject. The no-regeneration baseline. |
| `recuperated.py` | the brief's baseline. Acyclic — solves in one pass. |
| `recompression.py` | split the flow, two recuperators. Cyclic — one tear. |
| `intercooled.py` | two compression stages with an intercooler. |
| `partial_cooling.py` | three pressure levels, two coolers, pre-compressor. Written with zero new solver code. |

A layout is pure wiring. Adding a third compression stage is three lines;
adding partial cooling is a new file, not a code change.

## Cases

| case | what it is |
|---|---|
| `pdf_baseline` | the brief's table, verbatim, no pressure drops |
| `pdf_baseline_dp` | the same with 1 % per exchanger side |
| `pdf_recompression` | recompression at effectiveness 0.90, split 0.30 |
| `pdf_recompression_pinch` | the same sized to the brief's 5 K pinch |
| `pdf_partial_cooling` | partial cooling, 6 MPa low side, split 0.30 |
| `baseline_watercooled` | precooler sized against 25 degC water, 10 K rise |
| `recompression_watercooled` | the same for the recompression layout |
| `baseline_watercooled_pinch` | precooler sized to a 5 K approach instead |
| `air_brayton_ideal` | ideal-gas validation against the formula sheet |
| `air_brayton_real` | the same with eta_c 0.85, eta_t 0.90 |

Cases are frozen. `case.with_(...)` returns a modified copy — that is how a
variant, a sensitivity run or an optimiser's trial point is built, never by
editing one in place. An optimiser calling `with_` ten thousand times on a
shared mutable dict is the kind of bug that produces a plausible but wrong
Pareto front.

## Runs

```bash
python -m project.studies.run_cases [name]    # full state tables
python -m project.studies.run_cases [name]    # full state tables
python -m project.studies.check_nodes         # grid convergence
python -m project.studies.compare_layouts     # all three layouts at equal pinch
python -m project.studies.precooler           # R4: cooling water and precooler size
```

## What comes next

Stage 2, in brief order:

1. **Metrics** — loss indicators per role, second-law efficiency, net
   efficiency, critical-point margin, cooling-water duty.
2. **Economics** — PCHE mass and volume from UA, turbomachinery mass, the
   cost proxy. All coefficients as parameters.
3. **Sweeps** — eta against pressure ratio, split fraction, effectiveness,
   compressor inlet temperature.
4. **Optimisation** — constraint filter, Pareto front, knee selection, and
   the table of what the chosen design gives up against each role's own
   optimum.
5. **Plots** — T-s, h-s, T-Q with the pinch marked, Pareto fronts.

Still open in the solver: only the intermediate heat exchanger, and the
brief puts that out of scope -- R1 is told to take the reactor-side heater
as given. If it is ever wanted, it is the same `heat_exchanger` block with a
primary coolant on the hot side.
