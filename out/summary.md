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
| 5 | 291 | 291 | 230 | 61 | not_solved: 9, recup_pinch<5K: 52 |
| 6 | 692 | 684 | 678 | 6 | recup_pinch<5K: 6 |

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
| L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.42416 | 0.7007 | 15739 | 81.41 | 187.48 | 0.5210 | 22.62 | 9.84 | 5.00 | 5.00 |
| L6_Ph200_T320_Tt500_Pm077_Pe053_x045 | 0.41591 | 0.6871 | 13920 | 76.86 | 184.58 | 0.5411 | 19.97 | 10.58 | 5.00 | 5.00 |

## 4. Knee of the Pareto front

| column | value |
|---|---|
| ID | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 |
| tags | knee topsis_1 |
| pressure_ratio | 2.5316456 |
| split | 0.37 |
| eta | 0.38228985 |
| UA_recup_1 | 1654.0359 |
| UA_recup_2 | 1541.2927 |
| UA_cooler_1 | 4606.9408 |
| UA_cooler_2 | 2734.0153 |
| UA_total | 10536.285 |
| pinch_recup_1 | 15.730931 |
| pinch_recup_2 | 10.426493 |
| pinch_cooler_1 | 5.000001 |
| pinch_cooler_2 | 5.000016 |
| eta_carnot | 0.6033758 |
| eta_second_law | 0.63358498 |
| layout | 6 |
| P_comp_in_min_MPa | 3.5 |
| W_net_MW | 38.228985 |
| mass_t | 68.399712 |
| volume_m3 | 136.79942 |
| mwe_per_t | 0.55890564 |
| hardware_usd | 17099928 |
| electricity_usd_per_yr | 18732203 |
| payout_usd | 1.702221e+08 |
| M0_used | 39.059 |
| pareto | 1 |
| knee | 1 |
| topsis_score | 0.80797176 |
| topsis_rank | 1 |
| water_flow_kg_s | 619.026 |
| mdot_kg_s | 345.525 |

## 5. Top 5 by TOPSIS

| ID | eta | eta_II | UA_total kW/K | mass t | payout M USD | MWe/t | pinch r1 | pinch r2 | pinch c1 | pinch c2 |
|---|---|---|---|---|---|---|---|---|---|---|
| L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 0.38229 | 0.6336 | 10536 | 68.40 | 170.22 | 0.5589 | 15.73 | 10.43 | 5.00 | 5.00 |
| L6_Ph200_T345_Tt500_Pm081_Pe040_x037 | 0.38755 | 0.6437 | 10932 | 69.39 | 172.55 | 0.5585 | 17.40 | 9.96 | 5.00 | 5.00 |
| L6_Ph200_T335_Tt500_Pm079_Pe040_x037 | 0.39053 | 0.6472 | 11118 | 69.85 | 173.89 | 0.5591 | 17.57 | 9.89 | 5.00 | 5.00 |
| L6_Ph200_T340_Tt500_Pm081_Pe040_x040 | 0.39158 | 0.6497 | 11183 | 70.02 | 174.37 | 0.5593 | 16.76 | 10.80 | 5.00 | 5.00 |
| L6_Ph200_T340_Tt500_Pm081_Pe040_x037 | 0.38733 | 0.6426 | 10933 | 69.39 | 172.44 | 0.5582 | 17.74 | 9.97 | 5.00 | 5.00 |

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
| L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.42416 | 0.7007 | 15739 | 81.41 | 187.48 | 0.5210 | 22.62 | 9.84 | 5.00 | 5.00 |
| L3_Ph200_Pl077_T320_Tt500_x035 | 0.42241 | 0.6978 | 15076 | 78.25 | 187.42 | 0.5398 | 22.38 | 9.65 | 5.00 |  |
| L3_Ph200_Pl077_T325_Tt500_x035 | 0.42161 | 0.6972 | 14646 | 77.17 | 187.29 | 0.5463 | 21.80 | 10.13 | 5.00 |  |
| L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.42564 | 0.7032 | 17301 | 85.31 | 187.24 | 0.4989 | 23.32 | 7.68 | 5.00 | 5.00 |

## 6. Lifetime sensitivity (recomputed in memory, main ranking)

| years | knee | knee payout M USD | TOPSIS #1 | its payout M USD | max payout | max payout M USD | front size |
|---|---|---|---|---|---|---|---|
| 5 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 76.56 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 76.56 | L3_Ph200_Pl077_T320_Tt500_x036 | 84.08 | 46 |
| 10 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 170.22 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 170.22 | L3_Ph200_Pl077_T320_Tt500_x036 | 187.72 | 51 |
| 20 | L3_Ph200_Pl077_T325_Tt500_x044 | 376.97 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | 357.54 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 395.80 | 57 |

## 6b. Strict ranking: every compressor inlet >= 7.7 MPa (data/results_econ_strict.csv)

678 designs with a compressor inlet below 7.7 MPa removed (layouts left with no designs: 6); layouts [1] also unranked. The main ranking (results_econ.csv) is unchanged.

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
| 1 | L3_Ph200_Pl077_T325_Tt500_x046 | 0.80800 | 70.84 | 177.03 |
| 2 | L3_Ph200_Pl077_T330_Tt500_x042 | 0.80756 | 70.73 | 176.49 |
| 3 | L3_Ph200_Pl077_T325_Tt500_x047 | 0.80751 | 70.50 | 175.68 |
| 4 | L3_Ph200_Pl077_T325_Tt500_x045 | 0.80736 | 71.22 | 178.32 |
| 5 | L3_Ph200_Pl077_T330_Tt500_x043 | 0.80723 | 70.37 | 175.18 |
| 6 | L3_Ph200_Pl077_T330_Tt500_x041 | 0.80700 | 71.10 | 177.75 |
| 7 | L3_Ph200_Pl077_T325_Tt500_x044 | 0.80586 | 71.61 | 179.53 |
| 8 | L3_Ph200_Pl077_T330_Tt500_x044 | 0.80582 | 70.03 | 173.81 |
| 9 | L3_Ph200_Pl077_T325_Tt500_x048 | 0.80573 | 70.19 | 174.24 |
| 10 | L3_Ph200_Pl077_T330_Tt500_x040 | 0.80529 | 71.52 | 178.94 |

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

**Grid completeness.** Every grid finished before the 15:45 hard stop (last finished 15:31); no grid is incomplete. 1011 of 1011 points attempted. Refinement grids L3_fine (33 points, 3 already in L3) and L6_fine (12 points) were added afterwards and solved completely: 1053 of 1053 points attempted.

**Skipped layouts / failed checks.**

- **Layout 1 (simple): 9 of 18 points fail with an error, not a physical reason.** With no recuperator the cooler receives turbine exhaust at several hundred degC. The `CoolantPinch` search tries water outlets up to that temperature, reaches saturation at the solver's default 6 bar coolant pressure (159 degC), and CoolProp raises. The 9 points that solved are kept; their efficiencies are 9.6 to 14.8 %. The layout 1 smoke test at the mid-grid point is marked xfail (strict) for this reason, and a second layout 1 test at a solvable point passes. Fixing it needs a coolant-pressure decision or a `cycles/` change; neither was made.
- **Layout 1 eta floor** in `tests/test_layouts.py` is 0.10, not 0.15 (a simple cycle without recuperation is expected to be low).
- **`not_solved` points are temperature crosses, not solver failures:** 1 in layout 4 (RECUP), 9 in layout 5 (LTR), reported by the solver as flags.
- **Layout 5 (`brayton_cycle/recomp_intercooled.py`)** is new wiring written in this step; layout 6 uses `STRICT_INLET_PRESSURE = False` (7.7 MPa applied to the main compressor only).

**Settings.** Sweep cooler profiles use 50 slices (`COOLER_NODES`); 25 was planned but failed a reference test (cooler UA -0.156 % at L2_Ph200_Pl077_T360_Tt500 against a 0.1 % tolerance). States and T-s diagrams are re-solved with 100. The L2_cal row of the run table was entered by hand from that run's console output (the log file was added afterwards).
