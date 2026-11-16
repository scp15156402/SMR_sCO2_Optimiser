# results/

Every number in the final report comes from a file in here, and every
file in here was written by a script in `project/studies/`.

Nothing in this directory is edited by hand. If a number looks wrong, the
fix is in the study that produced it, followed by re-running the study —
never an edit here.

## How to regenerate everything

```bash
python -m project.studies.compare_layouts    # layout comparison
python -m project.studies.sweeps             # pressure and split sweeps
python -m project.studies.exergy             # second-law accounting
python -m project.studies.tradeoff           # candidates, Pareto, knee
python -m project.studies.selected_design    # the chosen cycle's states
python -m tools.make_figures                 # plot data for the document
```

Order matters in one place: `selected_design` reads the knee row that
`tradeoff` writes, and `make_figures` reads all of them. Run `tradeoff`
before `selected_design`, and both before `make_figures`. Each will tell
you if an input it needs is missing.

## What each study produces

| Study | Command | Outputs |
|---|---|---|
| Layout comparison | `python -m project.studies.compare_layouts` | `layout_comparison/layouts.csv` |
| Parameter sweeps | `python -m project.studies.sweeps` | `parameter_sweeps/pressure_sweep.csv`, `parameter_sweeps/split_fraction_sweep.csv` |
| Exergy | `python -m project.studies.exergy` | `exergy/by_component.csv`, `exergy/balance.csv` |
| Multi-objective | `python -m project.studies.tradeoff` | `multi_objective/candidates.csv`, `multi_objective/pareto_front.csv` |
| Selected design | `python -m project.studies.selected_design` | `selected_design/state_points.csv`, `performance.csv`, `ts_loop.csv`, `ts_branch.csv` |

Studies that print diagnostics and save nothing, because they produce no
result a report would cite: `run_cases`, `check_nodes`, `precooler`,
`cooling`.

## What a manifest records

Every study directory has a `manifest.json` alongside its CSVs:

- **purpose** — what question the study answers
- **script** and **command** — how to reproduce it
- **written_utc** — when
- **source_fingerprint** — a SHA-256 over every `.py` file in `cycles/`,
  `brayton_cycle/` and `project/`. Two runs agreeing on this hash ran
  identical code. There is no Git repository yet, and inventing a commit
  hash would be worse than having none; when Git exists the commit should
  be recorded *alongside* the fingerprint, which stays useful because it
  also catches uncommitted edits.
- **environment** — Python and CoolProp versions
- **inputs** — the actual grids and settings swept, read from the
  constants the study used rather than typed in separately
- **outputs** — each file, its row count and its columns
- **notes** — the caveats that belong with these numbers

## Provenance of the document's figures

`tools/make_figures.py` no longer solves anything. It reads the CSVs
above and writes whitespace-delimited tables into
`documentation/latex/data/`, which pgfplots reads at build time.

| Figure | Reads |
|---|---|
| T–s diagram of the selected cycle | `selected_design/state_points.csv`, `ts_loop.csv`, `ts_branch.csv` |
| Efficiency vs maximum pressure | `parameter_sweeps/pressure_sweep.csv` |
| Efficiency vs split fraction | `parameter_sweeps/split_fraction_sweep.csv` |
| Pareto, both projections | `multi_objective/candidates.csv` |

Figures that illustrate *method* rather than report a project result —
the $c_p$ peak, a recuperator profile, $UA$ against effectiveness — are
still computed inside `make_figures` from a fixed illustrative case. They
are drawings of a concept, not findings, and are labelled as such in the
technical document.

## The one thing this structure is designed to prevent

The pressure and split-fraction sweeps used to be computed twice: once in
`tradeoff.py` and again, on a **different grid**, inside the plotting
script. They agreed only because both happened to call the same solver.
Separately, the T–s diagram was once built from the default recompression
case while its caption claimed to show the recommended design.

Both failures are now structurally impossible. A study computes once and
saves; everything downstream reads the file. `selected_design.py` rebuilds
the chosen cycle from the knee row the trade-off itself labelled, through
the same factory the sweep used, and fails loudly if the efficiency it
gets back disagrees with the one recorded.
