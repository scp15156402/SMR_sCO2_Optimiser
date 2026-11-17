# S1: cooler pinch 3 K and 8 K

Every design in data/inputs.csv re-solved with the CO2-water cooler pinch set to 3 K and 8 K (baseline 5 K); M0 recalibrated on the most efficient feasible layout 2 design at T_turb 500 C for each pinch, so the reference stays at 60 t. Economics and both rankings rerun (layout 1 unranked; strict = every compressor inlet >= 7.7 MPa). The cooler pinch does not change the cycle (the cooler outlet is fixed at T_in), only the cooler UA, mass and water flow.

| case | attempted | feasible | infeasible |
|---|---|---|---|
| 5 K (baseline) | 2656 | 2561 | 95 |
| 3 K | 2656 | 2561 | 95 |
| 8 K | 2656 | 1992 | 664 |

At 8 K, 569 solver-converged points do not reach the pinch (T_in - 25 C water < 8 K; the solver stops at its most-water limit and reports a smaller pinch with water flows of order 10^4 kg/s). They are counted as infeasible and listed in pinch8_unreachable.csv.

## M0 and reference design

| case | reference | eta | UA_recup kW/K | UA_cooler kW/K | M0 t |
|---|---|---|---|---|---|
| 5 K (baseline) | L2_Ph200_Pl077_T340_Tt500 | 0.33306 | 1865.6 | 6510.8 | 39.059 |
| 3 K | L2_Ph200_Pl077_T340_Tt500 | 0.33306 | 1865.6 | 9506.3 | 31.570 |
| 8 K | L2_Ph200_Pl077_T340_Tt500 | 0.33306 | 1865.6 | 4148.9 | 44.964 |

## Named designs

| design | case | cooler UA kW/K | cooler mass t | total mass t | eta | payout M$ | water kg/s | cooler pinch K |
|---|---|---|---|---|---|---|---|---|
| Reference | 5 K (baseline) | 6511 | 16.28 | 60.00 | 0.33306 | 148.201 | 364 | 5.00 |
| Reference | 3 K | 9506 | 23.77 | 60.00 | 0.33306 | 148.201 | 307 | 3.00 |
| Reference | 8 K | 4149 | 10.37 | 60.00 | 0.33306 | 148.201 | 599 | 8.00 |
| Main TOPSIS #1 | 5 K (baseline) | 7490 | 18.73 | 69.17 | 0.38719 | 172.430 | 625 | 5.00 |
| Main TOPSIS #1 | 3 K | 10113 | 25.28 | 68.24 | 0.38719 | 172.663 | 494 | 3.00 |
| Main TOPSIS #1 | 8 K | 5297 | 13.24 | 69.59 | 0.38719 | 172.325 | 1389 | 8.00 |
| Strict TOPSIS #1 | 5 K (baseline) | 6287 | 15.72 | 70.84 | 0.39744 | 177.035 | 1019 | 5.00 |
| Strict TOPSIS #1 | 3 K | 8836 | 22.09 | 69.73 | 0.39744 | 177.314 | 698 | 3.00 |
| Strict TOPSIS #1 | 8 K | infeasible |  |  |  |  |  |  |
| Strict knee | 5 K (baseline) | 5794 | 14.49 | 70.37 | 0.39342 | 175.182 | 614 | 5.00 |
| Strict knee | 3 K | 8328 | 20.82 | 69.21 | 0.39342 | 175.471 | 459 | 3.00 |
| Strict knee | 8 K | 3519 | 8.80 | 70.58 | 0.39342 | 175.128 | 4622 | 8.00 |
| Highest payout | 5 K (baseline) | 7249 | 18.12 | 78.24 | 0.42302 | 187.721 | 1346 | 5.00 |
| Highest payout | 3 K | 10163 | 25.41 | 78.04 | 0.42302 | 187.772 | 904 | 3.00 |
| Highest payout | 8 K | infeasible |  |  |  |  |  |  |
| Submitted design | 5 K (baseline) | 5960 | 14.90 | 71.52 | 0.40167 | 178.942 | 638 | 5.00 |
| Submitted design | 3 K | 8579 | 21.45 | 70.57 | 0.40167 | 179.177 | 477 | 3.00 |
| Submitted design | 8 K | 3613 | 9.03 | 71.55 | 0.40167 | 178.932 | 4821 | 8.00 |

## Best design per layout (main ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| 5 K (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 5 K (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| 5 K (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 5 K (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| 5 K (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| 5 K (baseline) | 6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 76.61 | 184.582 |
| 3 K | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 44.72 | 61.437 |
| 3 K | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.47 | 148.262 |
| 3 K | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.04 | 187.772 |
| 3 K | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 85.52 | 154.718 |
| 3 K | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 80.97 | 187.501 |
| 3 K | 6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 78.70 | 184.059 |
| 8 K | 1 | L1_Ph200_Pl087_T360_Tt500 | 0.13024 | 52.19 | 50.768 |
| 8 K | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.56 | 148.238 |
| 8 K | 3 | L3_Ph200_Pl079_T330_Tt500_x035 | 0.42066 | 79.50 | 186.250 |
| 8 K | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.34429 | 73.39 | 150.356 |
| 8 K | 5 | L5_Ph200_Pl077_T330_Tt500_Pm090_x036 | 0.42122 | 82.21 | 185.849 |
| 8 K | 6 | L6_Ph200_T330_Tt500_Pm081_Pe055_x045 | 0.41226 | 74.93 | 183.276 |

## Best design per layout (strict ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| 5 K (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 5 K (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| 5 K (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 5 K (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| 5 K (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| 3 K | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 44.72 | 61.437 |
| 3 K | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.47 | 148.262 |
| 3 K | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.04 | 187.772 |
| 3 K | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 85.52 | 154.718 |
| 3 K | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 80.97 | 187.501 |
| 8 K | 1 | L1_Ph200_Pl087_T360_Tt500 | 0.13024 | 52.19 | 50.768 |
| 8 K | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.56 | 148.238 |
| 8 K | 3 | L3_Ph200_Pl079_T330_Tt500_x035 | 0.42066 | 79.50 | 186.250 |
| 8 K | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.34429 | 73.39 | 150.356 |
| 8 K | 5 | L5_Ph200_Pl077_T330_Tt500_Pm090_x036 | 0.42122 | 82.21 | 185.849 |

## Rankings

| ranking | case | front size | knee | TOPSIS #1 | knee water kg/s | TOPSIS water kg/s |
|---|---|---|---|---|---|---|
| main | 5 K (baseline) | 60 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 620 | 625 |
| main | 3 K | 64 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L3_Ph200_Pl077_T325_Tt500_x047 (layout 3, T_in 32.5 C, x 0.47) | 490 | 689 |
| main | 8 K | 26 | L6_Ph200_T330_Tt500_Pm077_Pe045_x030 (layout 6, T_in 33 C, x 0.30, P_exh 4.5 MPa) | L6_Ph200_T330_Tt500_Pm077_Pe045_x030 (layout 6, T_in 33 C, x 0.30, P_exh 4.5 MPa) | 3869 | 3869 |
| strict | 5 K (baseline) | 37 | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 614 | 1019 |
| strict | 3 K | 35 | L3_Ph200_Pl077_T325_Tt500_x047 (layout 3, T_in 32.5 C, x 0.47) | L3_Ph200_Pl077_T325_Tt500_x047 (layout 3, T_in 32.5 C, x 0.47) | 689 | 689 |
| strict | 8 K | 22 | L3_Ph200_Pl077_T330_Tt500_x042 (layout 3, T_in 33 C, x 0.42) | L3_Ph200_Pl077_T330_Tt500_x042 (layout 3, T_in 33 C, x 0.42) | 4688 | 4688 |

## Does the winner change? (against 5 K)

**3 K**

- main knee: unchanged (L6_Ph200_T335_Tt500_Pm079_Pe036_x038).
- main topsis: L6_Ph200_T335_Tt500_Pm079_Pe037_x038 -> L3_Ph200_Pl077_T325_Tt500_x047 (changes: layout, T_in, split, P_exh, P_mid, P_low).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T325_Tt500_x047 (changes: T_in, split).
- strict topsis: L3_Ph200_Pl077_T325_Tt500_x046 -> L3_Ph200_Pl077_T325_Tt500_x047 (changes: split).

**8 K**

- main knee: L6_Ph200_T335_Tt500_Pm079_Pe036_x038 -> L6_Ph200_T330_Tt500_Pm077_Pe045_x030 (changes: T_in, split, P_exh, P_mid).
- main topsis: L6_Ph200_T335_Tt500_Pm079_Pe037_x038 -> L6_Ph200_T330_Tt500_Pm077_Pe045_x030 (changes: T_in, split, P_exh, P_mid).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T330_Tt500_x042 (changes: split).
- strict topsis: L3_Ph200_Pl077_T325_Tt500_x046 -> L3_Ph200_Pl077_T330_Tt500_x042 (changes: T_in, split).

Plots: pareto_pinch3.png, pareto_pinch3_strict.png, pareto_pinch8.png, pareto_pinch8_strict.png.

