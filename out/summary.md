# sCO2 Brayton study: summary

Q = 100 MWth, lifetime 10 yr, 70 USD/MWh, 7000 h/yr, 250 USD/kg, TOPSIS weights {'payout': 0.5, 'mass': 0.5}, cooler slices 50 (sweep) / 100 (states), STRICT_INLET_PRESSURE = False.

**Excluded from the ranking:** layout(s) 1 (RANK_EXCLUDE_LAYOUTS). Their rows stay in results_econ.csv with empty pareto/knee/topsis columns; Pareto front, knee and TOPSIS cover the other layouts only.

## 1. Points per layout

| layout | in grid | attempted | feasible | infeasible | reasons |
|---|---|---|---|---|---|
| 1 | 18 | 18 | 9 | 9 | error: 9 |
| 2 | 573 | 573 | 560 | 13 | recup_pinch<5K: 13 |
| 3 | 957 | 957 | 955 | 2 | recup_pinch<5K: 2 |
| 4 | 87 | 87 | 83 | 4 | not_solved: 3, recup_pinch<5K: 1 |
| 5 | 293 | 293 | 232 | 61 | not_solved: 9, recup_pinch<5K: 52 |
| 6 | 728 | 728 | 722 | 6 | recup_pinch<5K: 6 |

## 2. Calibration (layout 2, best feasible eta)

| reference ID | eta | UA_recup_1 kW/K | UA_cooler_1 kW/K | m_recup t | m_cooler t | M0 t (computed) | M0_T in config |
|---|---|---|---|---|---|---|---|
| L2_Ph200_Pl077_T340_Tt500 | 0.333064 | 1865.6 | 6510.8 | 4.664 | 16.277 | 39.059 | 39.059 |

## 3. Best design per layout (by payout)

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 0.2448 | 3851 | 48.69 | 60.45 | 0.3044 |  |  | 5.00 |  |
| L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 0.5518 | 8234 | 59.64 | 148.22 | 0.5582 | 26.81 |  | 5.00 |  |
| L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 0.6988 | 15074 | 78.24 | 187.72 | 0.5406 | 22.12 | 10.42 | 5.00 |  |
| L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 0.5937 | 17295 | 83.80 | 155.15 | 0.4289 | 5.52 |  | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 0.7004 | 15577 | 81.00 | 187.49 | 0.5234 | 22.50 | 9.97 | 5.00 | 5.00 |
| L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 0.6869 | 13819 | 76.61 | 184.58 | 0.5427 | 19.64 | 10.56 | 5.00 | 5.00 |

## 4. Knee of the Pareto front

| column | value |
|---|---|
| ID | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 |
| tags | knee topsis_2 |
| pressure_ratio | 2.5316456 |
| split | 0.38 |
| eta | 0.38544234 |
| UA_recup_1 | 1700.7633 |
| UA_recup_2 | 1611.7968 |
| UA_cooler_1 | 4588.3685 |
| UA_cooler_2 | 2826.7263 |
| UA_total | 10727.655 |
| pinch_recup_1 | 15.774101 |
| pinch_recup_2 | 10.610013 |
| pinch_cooler_1 | 4.9999988 |
| pinch_cooler_2 | 4.9999507 |
| eta_carnot | 0.6033758 |
| eta_second_law | 0.63880975 |
| layout | 6 |
| P_comp_in_min_MPa | 3.6 |
| W_net_MW | 38.544234 |
| mass_t | 68.878137 |
| volume_m3 | 137.75627 |
| mwe_per_t | 0.55960041 |
| hardware_usd | 17219534 |
| electricity_usd_per_yr | 18886675 |
| payout_usd | 1.7164721e+08 |
| M0_used | 39.059 |
| pareto | 1 |
| knee | 1 |
| topsis_score | 0.80927606 |
| topsis_rank | 2 |
| water_flow_kg_s | 620.252 |
| mdot_kg_s | 350.586 |

## 5. Top 5 by TOPSIS

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 0.38719 | 0.6417 | 10844 | 69.17 | 172.43 | 0.5598 | 16.16 | 10.49 | 5.00 | 5.00 |
| L6_Ph200_T335_Tt500_Pm079_Pe036_x038 | 0.38544 | 0.6388 | 10728 | 68.88 | 171.65 | 0.5596 | 15.77 | 10.61 | 5.00 | 5.00 |
| L6_Ph200_T335_Tt500_Pm079_Pe038_x038 | 0.38884 | 0.6444 | 10958 | 69.45 | 173.17 | 0.5598 | 16.54 | 10.38 | 5.00 | 5.00 |
| L6_Ph200_T335_Tt500_Pm079_Pe037_x037 | 0.38587 | 0.6395 | 10764 | 68.97 | 171.84 | 0.5595 | 16.50 | 10.20 | 5.00 | 5.00 |
| L6_Ph200_T335_Tt500_Pm079_Pe035_x038 | 0.38359 | 0.6357 | 10616 | 68.60 | 170.81 | 0.5592 | 15.37 | 10.73 | 5.00 | 5.00 |

## 5. Top 5 by efficiency

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 0.42578 | 0.7034 | 18680 | 88.76 | 186.44 | 0.4797 | 23.72 | 6.10 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.42564 | 0.7032 | 17301 | 85.31 | 187.24 | 0.4989 | 23.32 | 7.68 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm110_x034 | 0.42468 | 0.7016 | 19137 | 89.90 | 185.62 | 0.4724 | 23.91 | 5.87 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm100_x035 | 0.42453 | 0.7013 | 17763 | 86.47 | 186.40 | 0.4910 | 23.62 | 7.42 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.42416 | 0.7007 | 15739 | 81.41 | 187.48 | 0.5210 | 22.62 | 9.84 | 5.00 | 5.00 |

## 5. Top 5 by lowest mass

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L1_Ph160_Pl077_T320_Tt500 | 0.11687 | 0.1931 | 3816 | 48.60 | 45.12 | 0.2405 |  |  | 5.00 |  |
| L1_Ph180_Pl077_T320_Tt500 | 0.13367 | 0.2208 | 3831 | 48.64 | 53.34 | 0.2748 |  |  | 5.00 |  |
| L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 0.2448 | 3851 | 48.69 | 60.45 | 0.3044 |  |  | 5.00 |  |
| L1_Ph160_Pl087_T360_Tt500 | 0.09815 | 0.1636 | 3859 | 48.71 | 35.92 | 0.2015 |  |  | 5.00 |  |
| L1_Ph180_Pl087_T360_Tt500 | 0.11536 | 0.1922 | 3877 | 48.75 | 44.34 | 0.2366 |  |  | 5.00 |  |

## 5. Top 5 by payout

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 0.6988 | 15074 | 78.24 | 187.72 | 0.5406 | 22.12 | 10.42 | 5.00 |  |
| L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 0.7004 | 15577 | 81.00 | 187.49 | 0.5234 | 22.50 | 9.97 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.42416 | 0.7007 | 15739 | 81.41 | 187.48 | 0.5210 | 22.62 | 9.84 | 5.00 | 5.00 |
| L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 0.42364 | 0.6999 | 15368 | 80.48 | 187.46 | 0.5264 | 22.35 | 10.14 | 5.00 | 5.00 |
| L3_Ph200_Pl077_T320_Tt500_x035 | 0.42241 | 0.6978 | 15076 | 78.25 | 187.42 | 0.5398 | 22.38 | 9.65 | 5.00 |  |

## 6. Lifetime sensitivity (recomputed in memory, main ranking)

| years | knee | knee payout M USD | TOPSIS #1 | its payout M USD | max payout | max payout M USD | front size |
|---|---|---|---|---|---|---|---|
| 5 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 | 77.21 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 77.57 | L3_Ph200_Pl077_T320_Tt500_x036 | 84.08 | 55 |
| 10 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 | 171.65 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 172.43 | L3_Ph200_Pl077_T320_Tt500_x036 | 187.72 | 60 |
| 20 | L3_Ph200_Pl077_T325_Tt500_x044 | 376.97 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 362.15 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 395.80 | 68 |

## 6b. Strict ranking: every compressor inlet >= 7.7 MPa (data/results_econ_strict.csv)

722 designs with a compressor inlet below 7.7 MPa removed (layouts left with no designs: 6); layouts [1] also unranked. The main ranking (results_econ.csv) is unchanged.

Knee: **L3_Ph200_Pl077_T330_Tt500_x043**; TOPSIS #1: **L3_Ph200_Pl077_T325_Tt500_x046**.

### Pareto front

| ID | mass t | payout M USD |
|---|---|---|
| L2_Ph200_Pl077_T335_Tt500 | 59.64 | 148.22 |
| L3_Ph200_Pl077_T335_Tt500_x048 | 68.88 | 161.09 |
| L3_Ph200_Pl077_T330_Tt500_x048 | 68.95 | 167.52 |
| L3_Ph200_Pl077_T330_Tt500_x047 | 69.20 | 169.22 |
| L3_Ph200_Pl077_T330_Tt500_x046 | 69.45 | 170.83 |
| L3_Ph200_Pl077_T330_Tt500_x045 | 69.73 | 172.36 |
| L3_Ph200_Pl077_T330_Tt500_x044 | 70.03 | 173.81 |
| L3_Ph200_Pl077_T325_Tt500_x048 | 70.19 | 174.24 |
| L3_Ph200_Pl077_T330_Tt500_x043 | 70.37 | 175.18 |
| L3_Ph200_Pl077_T325_Tt500_x047 | 70.50 | 175.68 |
| L3_Ph200_Pl077_T330_Tt500_x042 | 70.73 | 176.49 |
| L3_Ph200_Pl077_T325_Tt500_x046 | 70.84 | 177.03 |
| L3_Ph200_Pl077_T330_Tt500_x041 | 71.10 | 177.75 |
| L3_Ph200_Pl077_T325_Tt500_x045 | 71.22 | 178.32 |
| L3_Ph200_Pl077_T330_Tt500_x040 | 71.52 | 178.94 |
| L3_Ph200_Pl077_T325_Tt500_x044 | 71.61 | 179.53 |
| L3_Ph200_Pl077_T320_Tt500_x045 | 71.96 | 179.66 |
| L3_Ph200_Pl077_T330_Tt500_x039 | 71.97 | 180.08 |
| L3_Ph200_Pl077_T325_Tt500_x043 | 72.04 | 180.68 |
| L3_Ph200_Pl077_T320_Tt500_x044 | 72.41 | 180.79 |
| L3_Ph200_Pl077_T330_Tt500_x038 | 72.48 | 181.16 |
| L3_Ph200_Pl077_T325_Tt500_x042 | 72.52 | 181.77 |
| L3_Ph200_Pl077_T320_Tt500_x043 | 72.88 | 181.86 |
| L3_Ph200_Pl077_T330_Tt500_x037 | 73.04 | 182.20 |
| L3_Ph200_Pl077_T325_Tt500_x041 | 73.04 | 182.80 |
| L3_Ph200_Pl077_T320_Tt500_x042 | 73.41 | 182.86 |
| L3_Ph200_Pl077_T325_Tt500_x040 | 73.61 | 183.78 |
| L3_Ph200_Pl077_T320_Tt500_x041 | 73.99 | 183.81 |
| L3_Ph200_Pl077_T330_Tt500_x031 | 74.24 | 184.04 |
| L3_Ph200_Pl077_T325_Tt500_x039 | 74.25 | 184.70 |
| L3_Ph200_Pl077_T320_Tt500_x040 | 74.64 | 184.71 |
| L3_Ph200_Pl077_T325_Tt500_x038 | 74.98 | 185.57 |
| L3_Ph200_Pl077_T325_Tt500_x037 | 75.81 | 186.38 |
| L3_Ph200_Pl077_T325_Tt500_x034 | 76.56 | 186.53 |
| L3_Ph200_Pl077_T325_Tt500_x036 | 76.75 | 187.14 |
| L3_Ph200_Pl077_T325_Tt500_x035 | 77.17 | 187.29 |
| L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 187.72 |

### TOPSIS top 10

| rank | ID | score | mass t | payout M USD |
|---|---|---|---|---|
| 1 | L3_Ph200_Pl077_T325_Tt500_x046 | 0.80799 | 70.84 | 177.03 |
| 2 | L3_Ph200_Pl077_T330_Tt500_x042 | 0.80755 | 70.73 | 176.49 |
| 3 | L3_Ph200_Pl077_T325_Tt500_x047 | 0.80750 | 70.50 | 175.68 |
| 4 | L3_Ph200_Pl077_T325_Tt500_x045 | 0.80735 | 71.22 | 178.32 |
| 5 | L3_Ph200_Pl077_T330_Tt500_x043 | 0.80723 | 70.37 | 175.18 |
| 6 | L3_Ph200_Pl077_T330_Tt500_x041 | 0.80699 | 71.10 | 177.75 |
| 7 | L3_Ph200_Pl077_T325_Tt500_x044 | 0.80585 | 71.61 | 179.53 |
| 8 | L3_Ph200_Pl077_T330_Tt500_x044 | 0.80581 | 70.03 | 173.81 |
| 9 | L3_Ph200_Pl077_T325_Tt500_x048 | 0.80572 | 70.19 | 174.24 |
| 10 | L3_Ph200_Pl077_T330_Tt500_x040 | 0.80528 | 71.52 | 178.94 |

## 7. Runs, skipped layouts and failed checks

| run | workers | attempted | feasible | infeasible | wall_s | points_per_s |
|---|---|---|---|---|---|---|
| L2_cal | 8 | 525 | 512 | 13 | 1051.3 | 0.499 |
| L3 | 8 | 108 | 106 | 2 | 169.6 | 0.637 |
| L1 | 8 | 18 | 9 | 9 | 28.1 | 0.641 |
| L4 | 8 | 54 | 53 | 1 | 59.0 | 0.916 |
| L6 | 8 | 162 | 156 | 6 | 525.5 | 0.308 |
| L5 | 8 | 144 | 91 | 53 | 255.8 | 0.563 |
| L3_fine | 8 | 30 | 30 | 0 | 138.5 | 0.217 |
| L6_fine | 8 | 12 | 12 | 0 | 134.6 | 0.089 |
| all | 8 | 1455 | 1444 | 11 | 4634.5 | 0.314 |
| all (interrupted) | 8 | 102 | 102 | 0 | 472.8 | 0.216 |
| all | 8 | 44 | 44 | 0 | 41.2 | 1.067 |
| all | 2 | 2 | 2 | 0 | 5.3 | 0.378 |

**Refinement (`core/refine.py`, branch wager).** Starting from the 1053 points of the base and fine grids, four rounds of refinement around the winners added 1455, 102, 44 and 2 points (rounds 1 to 4). Rounds 1 and 2 ran under a 90-minute cap; rounds 3 and 4 ran with no round or time cap and converged after round 4: best payout per layout (2, 3, 5, 6) moved < 0.05 %, TOPSIS #1 payout and mass (main and strict) moved < 0.1 %, and no tracked winner sat on a free grid edge (out/convergence.md). Every grid point was attempted: 2656 attempted, 2561 feasible, 95 infeasible, no timeouts. M0 was checked after every round and never changed: the reference is still L2_Ph200_Pl077_T340_Tt500 (eta 0.33306, M0 39.059 t).

**Rankings.** `RANK_EXCLUDE_LAYOUTS = [1]`: layout 1 keeps its rows but is left out of the Pareto front, knee and TOPSIS, as in the submitted report (layouts 2 to 6). The main ranking (`results_econ.csv`, `STRICT_INLET_PRESSURE = False`) applies 7.7 MPa to the main compressor inlet only. The strict ranking (`results_econ_strict.csv`) also removes every design with any compressor inlet below 7.7 MPa, which removes all of layout 6 (722 designs). Main: TOPSIS #1 L6_Ph200_T335_Tt500_Pm079_Pe037_x038, knee L6_Ph200_T335_Tt500_Pm079_Pe036_x038. Strict: TOPSIS #1 L3_Ph200_Pl077_T325_Tt500_x046, knee L3_Ph200_Pl077_T330_Tt500_x043.

**Skipped layouts / failed checks.**

- **Layout 1 (simple): 9 of 18 points fail with an error, not a physical reason.** With no recuperator the cooler receives turbine exhaust at several hundred degC. The `CoolantPinch` search tries water outlets up to that temperature, reaches saturation at the solver's default 6 bar coolant pressure (159 degC), and CoolProp raises. The 9 points that solved are kept; their efficiencies are 9.6 to 14.8 %. The layout 1 smoke test at the mid-grid point is marked xfail (strict) for this reason, and a second layout 1 test at a solvable point passes. Fixing it needs a coolant-pressure decision or a `cycles/` change; neither was made.
- **Layout 1 eta floor** in `tests/test_layouts.py` is 0.10, not 0.15 (a simple cycle without recuperation is expected to be low).
- **`not_solved` points are temperature crosses, not solver failures:** 3 in layout 4 (RECUP), 9 in layout 5 (LTR), reported by the solver as flags.
- **Layout 5 (`brayton_cycle/recomp_intercooled.py`)** is new wiring written in this step; layout 6 uses `STRICT_INLET_PRESSURE = False` (7.7 MPa applied to the main compressor only).

**Settings.** Sweep cooler profiles use 50 slices (`COOLER_NODES`); 25 was planned but failed a reference test (cooler UA -0.156 % at L2_Ph200_Pl077_T360_Tt500 against a 0.1 % tolerance). States and T-s diagrams are re-solved with 100. The L2_cal row of the run table was entered by hand from that run's console output (the log file was added afterwards).
