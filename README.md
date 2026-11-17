# sCO₂ Brayton cycle study for a 100 MWth SMR (ME 306)

This project sizes a supercritical-CO₂ Brayton power cycle for a 100 MWth small modular reactor. It sweeps six layouts (simple, recuperated, recompression, intercooled, recompression with intercooling, partial cooling) over compressor-inlet pressure and temperature, turbine-inlet temperature, intermediate pressures and recompression split. Each point is solved with the block-based solver in `cycles/` (CoolProp properties, pinch-sized recuperators and water-cooled coolers), then checked against the brief's constraints. Efficiency and heat-exchanger conductance are converted into hardware mass, cost and lifetime payout. The feasible designs are ranked by Pareto front, knee point and TOPSIS, and the best ones are written out as state tables and T-s diagrams. Settings are in `config.py`, sweep ranges are in `grids.py`, and the design rationale is in [PLAN.md](PLAN.md).

**Report:** [Full_Report.pdf](Full_Report.pdf).

**Result:** the selected design is layout 6 (partial cooling) at 20 MPa. The main compressor runs at 7.9 MPa and 33.5 °C, the exhaust is at 3.7 MPa, and the recompression split is x = 0.38. It reaches 38.7 % thermal efficiency with 69.2 t of hardware, for a payout of $172.4M over 10 years. Under the literal reading of the 7.7 MPa limit, which applies it to every compressor inlet, the selection is layout 3 (recompression) at 32.5 °C with x = 0.46.

**Extended studies:** nine sensitivity studies (S1–S9) are in [`core/studies/`](core/studies/), with their results and an overview in [`out/studies/README.md`](out/studies/README.md).

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

- **`main`** contains the completed refinement: the sweep was refined around the winners until it converged after round 4 (see `out/convergence.md`). Layout 1 is left out of the ranking; a second, strict ranking (`data/results_econ_strict.csv`) applies 7.7 MPa to every compressor inlet.
- **tag `rebuild`** is the submitted state: <https://github.com/scp15156402/SMR_sCO2_Optimiser/tree/rebuild>.
- **tag `extended-v1`** is the refined study: the merge of `wager` into `main`.
- **branch `wager`** (last commit tagged `wager-final`) is where the refinement was run; kept for its history.
- **`old-project` (branch and tag)** is unchanged: the previous version of this project, as it was before the rebuild.
