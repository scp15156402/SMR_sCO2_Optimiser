# sCO₂ Brayton cycle study for a 100 MWth SMR (ME 306)

This project sizes a supercritical-CO₂ Brayton power cycle for a 100 MWth small modular reactor. It sweeps six layouts (simple, recuperated, recompression, intercooled, recompression with intercooling, partial cooling) over compressor-inlet pressure and temperature, turbine-inlet temperature, intermediate pressures and recompression split. Each point is solved with the block-based solver in `cycles/` (CoolProp properties, pinch-sized recuperators and water-cooled coolers), then checked against the brief's constraints. Efficiency and heat-exchanger conductance are converted into hardware mass, cost and lifetime payout. The feasible designs are ranked by Pareto front, knee point and TOPSIS, and the best ones are written out as state tables and T-s diagrams. Settings are in `config.py`, sweep ranges are in `grids.py`, and the design rationale is in [PLAN.md](PLAN.md).

## Running the pipeline

Requires Python with `CoolProp`, `numpy`, `matplotlib` and `pytest`. Run every step from the repository root:

```
python -m core.make_inputs        # expand grids.py into data/inputs.csv (optionally: grid names)
python -m core.solve_points       # solve and check every new point -> data/results_raw.csv, data/infeasible.csv
                                  #   (--grid NAME, --workers N, --limit N, --deadline HH:MM; resumable)
python -m core.calibrate          # print the reference mass M0; enter it as M0_T in config.py
python -m core.economics          # mass, cost, payout, Pareto/knee/TOPSIS -> data/results_econ.csv
python -m core.export_states      # re-solve tagged designs -> data/states.csv, data/shortlist.csv
python -m core.plots              # summary plots and T-s diagrams -> out/
python -m core.summary            # out/summary.md
python -m pytest                  # tests
```

`calibrate` only has to be rerun if the reference point or the mass model changes.

## Branches and tags

- **`old-project` (branch and tag)** holds the previous version of this project, as it was before the rebuild.
- **tag `rebuild`** is the submitted state: <https://github.com/scp15156402/SMR_sCO2_Optimiser/tree/rebuild>.
- **`main`** is that submitted state, plus later maintenance.
- **branch `wager`** holds unfinished sweep-refinement work (`core/refine.py`, `out/convergence.md`). It has not been merged into `main`.
