# PLAN

## Purpose

sCO₂ Brayton cycle study for a 100 MWth SMR. Six layouts:

1. Simple
2. Recuperated
3. Recompression
4. Recuperated + intercooling
5. Recompression + intercooling
6. Angelino (`brayton_cycle/partial_cooling.py`)

Sweep each, compute efficiency and UA, convert to mass, cost and lifetime payout, then rank.

## Tree

| Path | Role |
|---|---|
| `cycles/` | Solver. Do not edit. |
| `brayton_cycle/` | Layout wiring. |
| `config.py` | Every fixed number in the study. |
| `grids.py` | Sweep ranges. |
| `core/make_inputs.py` | `grids.py` → `data/inputs.csv` |
| `core/solve_points.py` | `inputs.csv` → `data/results_raw.csv` + `data/infeasible.csv`; parallel, resumable |
| `core/calibrate.py` | Prints M0 from the best layout-2 point; the user pastes it into `config.py` |
| `core/economics.py` | `results_raw.csv` → `data/results_econ.csv`: mass, cost, payout, Pareto flag, knee, TOPSIS |
| `core/export_states.py` | `results_econ.csv` → `data/states.csv` for top-N lists and the knee |
| `core/plots.py` | Everything in `out/` |
| `helpers/ids.py`, `helpers/builders.py`, `helpers/checks.py`, `helpers/ranking.py` | Shared helpers |
| `tests/test_solver.py`, `tests/test_checks.py` | Tests |

## ID scheme

```
L{layout}_Ph{P_high}_Pl{P_low}_T{T_in}_Tt{T_turb}
```

- plus `_Pm{P_mid}` for layouts 4, 5, 6
- plus `_Pe{P_exh}` for layout 6
- plus `_x{split}` for layouts 3, 5, 6

All values are integers, zero-padded to 3 digits, in the `grids.py` units (pressure 0.1 MPa, T_in 0.1 °C, T_turb 1 °C, split 0.01). Layout 6 has no `Pl` (its main compressor inlet is P_mid).

Example: `L3_Ph200_Pl077_T320_Tt500_x030`

## CSV columns

| File | Columns |
|---|---|
| `inputs.csv` | ID, grid, layout, P_high_MPa, P_low_MPa, P_mid_MPa, P_exh_MPa, T_in_C, T_turb_C, split (blank where not applicable) |
| `results_raw.csv` (feasible points only) | ID, pressure_ratio (main compressor), split, eta, one UA column per exchanger in kW/K, UA_total, one pinch column per exchanger in K, eta_carnot, eta_second_law |
| `infeasible.csv` | ID, layout, reason |
| `results_econ.csv` | all raw columns plus mass_t, hardware_usd, electricity_usd_per_yr, payout_usd, M0_used, pareto, knee, topsis_score, topsis_rank |
| `states.csv` | ID, tags, stream, P, T, h, s, flow |

## Formulas

```
mass_t         = 2.5e-3 * (sum of recuperator and cooler UA in kW/K) + M0_T + 1.5 * EXTRA_COMPRESSORS[layout]
payout_usd     = LIFETIME_YEARS * eta * Q_THERMAL_MW * HOURS_PER_YEAR * USD_PER_MWH - USD_PER_KG * 1000 * mass_t
eta_carnot     = 1 - T_in_K / T_turb_K
eta_second_law = eta / eta_carnot
```

## Rules

- Recuperators use `Effectiveness(0.90)`.
- A point is infeasible if any recuperator pinch < 5 K or any brief constraint is broken.
- Coolers use `CoolantPinch(5 K)` with water at 25 °C.
- Pressure drops are zero.
- P_high is the compressor outlet pressure.

## Step rules

- Work on branch `rebuild`. Do only what the step says. Never edit `cycles/` or `brayton_cycle/` unless told to.
- If git fails with "index file corrupt" or "bad object refs/desktop.ini": delete desktop.ini files under `.git/` only, move `.git/index` aside if needed, run `git reset` (never `--hard`), retry once, and report it.
- End each step with a report: what was done, the check results with actual numbers, git status, and anything unexpected. If a check fails, show the traceback and stop. Do not fix beyond the step.
- Do not commit the step's work. The next step's prompt says when to commit and push it.
