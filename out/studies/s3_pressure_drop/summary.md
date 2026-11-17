# S3: pressure drops (1 % and 2 % per exchanger side)

Every design in data/inputs.csv re-solved with a fractional pressure loss dp on both recuperator sides, every cooler (CO2 side) and the heater. The ID pressures stay the compressor inlet and outlet pressures, so the turbine sees a smaller expansion ratio; the recompressor discharges at the LTR cold-outlet pressure and the layout 6 pre-compressor at P_mid / (1 - dp). M0 recalibrated at each level. Rankings: main and strict, layout 1 unranked.

## Efficiency loss per layout

Best eta per layout (baseline -> with dp), its loss in percentage points, and the median loss over the designs feasible at that dp (same ID in both).

| case | layout | best eta | best loss pp | median loss pp | best design | feasible |
|---|---|---|---|---|---|---|
| dp 1 % | 1 | 0.14820 -> 0.14471 | 0.35 | 0.35 | L1_Ph200_Pl077_T320_Tt500 | 9 |
| dp 1 % | 2 | 0.33306 -> 0.32261 | 1.05 | 1.32 | L2_Ph200_Pl097_T320_Tt500 | 559 |
| dp 1 % | 3 | 0.42302 -> 0.40582 | 1.72 | 1.93 | L3_Ph200_Pl077_T320_Tt500_x036 | 953 |
| dp 1 % | 4 | 0.35938 -> 0.34920 | 1.02 | 1.04 | L4_Ph200_Pl085_T320_Tt500_Pm140 | 81 |
| dp 1 % | 5 | 0.42578 -> 0.40915 | 1.66 | 1.79 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 229 |
| dp 1 % | 6 | 0.41595 -> 0.40159 | 1.44 | 1.53 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | 728 |
| dp 2 % | 1 | 0.14820 -> 0.14116 | 0.70 | 0.71 | L1_Ph200_Pl077_T320_Tt500 | 9 |
| dp 2 % | 2 | 0.33306 -> 0.31166 | 2.14 | 2.74 | L2_Ph200_Pl097_T320_Tt500 | 559 |
| dp 2 % | 3 | 0.42302 -> 0.38684 | 3.62 | 4.07 | L3_Ph200_Pl077_T320_Tt500_x036 | 952 |
| dp 2 % | 4 | 0.35938 -> 0.32859 | 3.08 | 2.17 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 80 |
| dp 2 % | 5 | 0.42578 -> 0.39064 | 3.51 | 3.77 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 224 |
| dp 2 % | 6 | 0.41595 -> 0.38601 | 2.99 | 3.17 | L6_Ph200_T320_Tt500_Pm077_Pe057_x045 | 728 |

## Feasible counts

| case | layout | attempted | feasible | infeasible |
|---|---|---|---|---|
| dp 0 (baseline) | 1 | 18 | 9 | 9 |
| dp 0 (baseline) | 2 | 573 | 560 | 13 |
| dp 0 (baseline) | 3 | 957 | 955 | 2 |
| dp 0 (baseline) | 4 | 87 | 83 | 4 |
| dp 0 (baseline) | 5 | 293 | 232 | 61 |
| dp 0 (baseline) | 6 | 728 | 722 | 6 |
| dp 1 % | 1 | 18 | 9 | 9 |
| dp 1 % | 2 | 573 | 559 | 14 |
| dp 1 % | 3 | 957 | 953 | 4 |
| dp 1 % | 4 | 87 | 81 | 6 |
| dp 1 % | 5 | 293 | 229 | 64 |
| dp 1 % | 6 | 728 | 728 | 0 |
| dp 2 % | 1 | 18 | 9 | 9 |
| dp 2 % | 2 | 573 | 559 | 14 |
| dp 2 % | 3 | 957 | 952 | 5 |
| dp 2 % | 4 | 87 | 80 | 7 |
| dp 2 % | 5 | 293 | 224 | 69 |
| dp 2 % | 6 | 728 | 728 | 0 |

## M0 and reference design

| case | reference | eta | UA_recup kW/K | UA_cooler kW/K | M0 t |
|---|---|---|---|---|---|
| dp 0 (baseline) | L2_Ph200_Pl077_T340_Tt500 | 0.33306 | 1865.6 | 6510.8 | 39.059 |
| dp 1 % | L2_Ph200_Pl097_T320_Tt500 | 0.32261 | 5415.0 | 10403.9 | 20.453 |
| dp 2 % | L2_Ph200_Pl097_T320_Tt500 | 0.31166 | 5893.8 | 10646.7 | 18.649 |

## Named designs

| design | case | cooler UA kW/K | cooler mass t | total mass t | eta | payout M$ | water kg/s | cooler pinch K |
|---|---|---|---|---|---|---|---|---|
| Reference | dp 0 (baseline) | 6511 | 16.28 | 60.00 | 0.33306 | 148.201 |  | 5.00 |
| Reference | dp 1 % | 6636 | 16.59 | 41.81 | 0.32133 | 146.999 | 365 | 5.00 |
| Reference | dp 2 % | 6768 | 16.92 | 40.44 | 0.30894 | 141.269 | 367 | 5.00 |
| Main TOPSIS #1 | dp 0 (baseline) | 7490 | 18.73 | 69.17 | 0.38719 | 172.430 |  | 5.00 |
| Main TOPSIS #1 | dp 1 % | 7534 | 18.84 | 50.72 | 0.37230 | 169.746 | 617 | 5.00 |
| Main TOPSIS #1 | dp 2 % | 7591 | 18.98 | 49.10 | 0.35670 | 162.506 | 609 | 5.00 |
| Strict TOPSIS #1 | dp 0 (baseline) | 6287 | 15.72 | 70.84 | 0.39744 | 177.035 |  | 5.00 |
| Strict TOPSIS #1 | dp 1 % | 6511 | 16.28 | 53.40 | 0.37914 | 172.426 | 1015 | 5.00 |
| Strict TOPSIS #1 | dp 2 % | 6757 | 16.89 | 52.89 | 0.35890 | 162.636 | 1014 | 5.00 |
| Strict knee | dp 0 (baseline) | 5794 | 14.49 | 70.37 | 0.39342 | 175.182 |  | 5.00 |
| Strict knee | dp 1 % | 6009 | 15.02 | 52.95 | 0.37429 | 170.163 | 621 | 5.00 |
| Strict knee | dp 2 % | 6248 | 15.62 | 52.47 | 0.35309 | 159.897 | 630 | 5.00 |
| Highest payout | dp 0 (baseline) | 7249 | 18.12 | 78.24 | 0.42302 | 187.721 |  | 5.00 |
| Highest payout | dp 1 % | 7499 | 18.75 | 61.14 | 0.40582 | 183.569 | 1322 | 5.00 |
| Highest payout | dp 2 % | 7774 | 19.43 | 60.99 | 0.38684 | 174.306 | 1304 | 5.00 |
| Submitted design | dp 0 (baseline) | 5960 | 14.90 | 71.52 | 0.40167 | 178.942 |  | 5.00 |
| Submitted design | dp 1 % | 6180 | 15.45 | 54.15 | 0.38279 | 174.031 | 645 | 5.00 |
| Submitted design | dp 2 % | 6423 | 16.06 | 53.73 | 0.36188 | 163.890 | 653 | 5.00 |

## Best design per layout (main ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| dp 0 (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| dp 0 (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| dp 0 (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| dp 0 (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| dp 0 (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| dp 0 (baseline) | 6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 76.61 | 184.582 |
| dp 1 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14471 | 30.08 | 63.386 |
| dp 1 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.32148 | 41.43 | 147.165 |
| dp 1 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.40582 | 61.14 | 183.569 |
| dp 1 % | 4 | L4_Ph200_Pl085_T320_Tt500_Pm140 | 0.34920 | 66.91 | 154.379 |
| dp 1 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.40654 | 64.05 | 183.192 |
| dp 1 % | 6 | L6_Ph200_T320_Tt500_Pm077_Pe054_x045 | 0.40158 | 59.04 | 182.017 |
| dp 2 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14116 | 28.28 | 62.101 |
| dp 2 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.30941 | 40.05 | 141.597 |
| dp 2 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.38684 | 60.99 | 174.306 |
| dp 2 % | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.32859 | 60.32 | 145.931 |
| dp 2 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.38980 | 68.18 | 173.957 |
| dp 2 % | 6 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | 0.38589 | 57.95 | 174.598 |

## Best design per layout (strict ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| dp 0 (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| dp 0 (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| dp 0 (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| dp 0 (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| dp 0 (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| dp 1 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14471 | 30.08 | 63.386 |
| dp 1 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.32148 | 41.43 | 147.165 |
| dp 1 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.40582 | 61.14 | 183.569 |
| dp 1 % | 4 | L4_Ph200_Pl085_T320_Tt500_Pm140 | 0.34920 | 66.91 | 154.379 |
| dp 1 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.40654 | 64.05 | 183.192 |
| dp 2 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14116 | 28.28 | 62.101 |
| dp 2 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.30941 | 40.05 | 141.597 |
| dp 2 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.38684 | 60.99 | 174.306 |
| dp 2 % | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.32859 | 60.32 | 145.931 |
| dp 2 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.38980 | 68.18 | 173.957 |

## Rankings

| ranking | case | front size | knee | TOPSIS #1 | knee water kg/s | TOPSIS water kg/s |
|---|---|---|---|---|---|---|
| main | dp 0 (baseline) | 60 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) |  |  |
| main | dp 1 % | 54 | L6_Ph200_T335_Tt500_Pm079_Pe038_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.8 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe033_x036 (layout 6, T_in 33.5 C, x 0.36, P_exh 3.3 MPa) | 621 | 604 |
| main | dp 2 % | 43 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe035_x033 (layout 6, T_in 33.5 C, x 0.33, P_exh 3.5 MPa) | 609 | 615 |
| strict | dp 0 (baseline) | 37 | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) |  |  |
| strict | dp 1 % | 37 | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | L2_Ph200_Pl077_T335_Tt500 (layout 2, T_in 33.5 C) | 1015 | 455 |
| strict | dp 2 % | 37 | L3_Ph200_Pl077_T325_Tt500_x045 (layout 3, T_in 32.5 C, x 0.45) | L2_Ph200_Pl077_T335_Tt500 (layout 2, T_in 33.5 C) | 1025 | 455 |

## Do the rankings change? (against dp 0)

**dp 1 %**

- main knee: L6_Ph200_T335_Tt500_Pm079_Pe036_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe038_x038 (changes: P_exh).
- main topsis: L6_Ph200_T335_Tt500_Pm079_Pe037_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe033_x036 (changes: split, P_exh).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T325_Tt500_x046 (changes: T_in, split).
- strict topsis: L3_Ph200_Pl077_T325_Tt500_x046 -> L2_Ph200_Pl077_T335_Tt500 (changes: layout, T_in, split).

**dp 2 %**

- main knee: L6_Ph200_T335_Tt500_Pm079_Pe036_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (changes: P_exh).
- main topsis: L6_Ph200_T335_Tt500_Pm079_Pe037_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe035_x033 (changes: split, P_exh).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T325_Tt500_x045 (changes: T_in, split).
- strict topsis: L3_Ph200_Pl077_T325_Tt500_x046 -> L2_Ph200_Pl077_T335_Tt500 (changes: layout, T_in, split).

Plots: pareto_dp1pct.png, pareto_dp1pct_strict.png, pareto_dp2pct.png, pareto_dp2pct_strict.png.

