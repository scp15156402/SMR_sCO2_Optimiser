# S3: pressure drops (1 % and 2 % per exchanger side)

Every design in data/inputs.csv re-solved with a fractional pressure loss dp on both recuperator sides, every cooler (CO2 side) and the heater. The ID pressures stay the compressor inlet and outlet pressures, so the turbine sees a smaller expansion ratio; the recompressor discharges at the LTR cold-outlet pressure and the layout 6 pre-compressor at P_mid / (1 - dp). Rankings: main and strict, layout 1 unranked.

**M0 is held at the baseline 39.059 t at every dp level, with the baseline reference L2_Ph200_Pl077_T340_Tt500 (re-solved at each dp) for payback.** Recalibrating would pick a different, high-UA layout 2 reference and drop M0 to about 20 t; that changes every mass (and payout) by the same constant, which leaves the Pareto front and the knee unchanged but moves TOPSIS, whose vector normalisation is not shift-invariant.

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
| dp 1 % | L2_Ph200_Pl077_T340_Tt500 | 0.32133 | 1906.4 | 6635.9 | 39.059 |
| dp 2 % | L2_Ph200_Pl077_T340_Tt500 | 0.30894 | 1949.7 | 6768.2 | 39.059 |

## Named designs

| design | case | cooler UA kW/K | cooler mass t | total mass t | eta | payout M$ | water kg/s | cooler pinch K |
|---|---|---|---|---|---|---|---|---|
| Reference | dp 0 (baseline) | 6511 | 16.28 | 60.00 | 0.33306 | 148.201 |  | 5.00 |
| Reference | dp 1 % | 6636 | 16.59 | 60.41 | 0.32133 | 142.348 | 365 | 5.00 |
| Reference | dp 2 % | 6768 | 16.92 | 60.85 | 0.30894 | 136.166 | 367 | 5.00 |
| Main TOPSIS #1 | dp 0 (baseline) | 7490 | 18.73 | 69.17 | 0.38719 | 172.430 |  | 5.00 |
| Main TOPSIS #1 | dp 1 % | 7534 | 18.84 | 69.32 | 0.37230 | 165.094 | 617 | 5.00 |
| Main TOPSIS #1 | dp 2 % | 7591 | 18.98 | 69.51 | 0.35670 | 157.403 | 609 | 5.00 |
| Strict TOPSIS #1 | dp 0 (baseline) | 6287 | 15.72 | 70.84 | 0.39744 | 177.035 |  | 5.00 |
| Strict TOPSIS #1 | dp 1 % | 6511 | 16.28 | 72.01 | 0.37914 | 167.775 | 1015 | 5.00 |
| Strict TOPSIS #1 | dp 2 % | 6757 | 16.89 | 73.30 | 0.35890 | 157.533 | 1014 | 5.00 |
| Strict knee | dp 0 (baseline) | 5794 | 14.49 | 70.37 | 0.39342 | 175.182 |  | 5.00 |
| Strict knee | dp 1 % | 6009 | 15.02 | 71.55 | 0.37429 | 165.511 | 621 | 5.00 |
| Strict knee | dp 2 % | 6248 | 15.62 | 72.88 | 0.35309 | 154.794 | 630 | 5.00 |
| Highest payout | dp 0 (baseline) | 7249 | 18.12 | 78.24 | 0.42302 | 187.721 |  | 5.00 |
| Highest payout | dp 1 % | 7499 | 18.75 | 79.74 | 0.40582 | 178.917 | 1322 | 5.00 |
| Highest payout | dp 2 % | 7774 | 19.43 | 81.40 | 0.38684 | 169.203 | 1304 | 5.00 |
| Submitted design | dp 0 (baseline) | 5960 | 14.90 | 71.52 | 0.40167 | 178.942 |  | 5.00 |
| Submitted design | dp 1 % | 6180 | 15.45 | 72.76 | 0.38279 | 169.379 | 645 | 5.00 |
| Submitted design | dp 2 % | 6423 | 16.06 | 74.14 | 0.36188 | 158.787 | 653 | 5.00 |

## Best design per layout (main ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| dp 0 (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| dp 0 (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| dp 0 (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| dp 0 (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| dp 0 (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| dp 0 (baseline) | 6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 76.61 | 184.582 |
| dp 1 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14471 | 48.69 | 58.735 |
| dp 1 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.32148 | 60.04 | 142.514 |
| dp 1 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.40582 | 79.74 | 178.917 |
| dp 1 % | 4 | L4_Ph200_Pl085_T320_Tt500_Pm140 | 0.34920 | 85.52 | 149.728 |
| dp 1 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.40654 | 82.65 | 178.541 |
| dp 1 % | 6 | L6_Ph200_T320_Tt500_Pm077_Pe054_x045 | 0.40158 | 77.64 | 177.365 |
| dp 2 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14116 | 48.69 | 56.999 |
| dp 2 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.30941 | 60.46 | 136.494 |
| dp 2 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.38684 | 81.40 | 169.203 |
| dp 2 % | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.32859 | 80.73 | 140.829 |
| dp 2 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.38980 | 88.59 | 168.854 |
| dp 2 % | 6 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | 0.38589 | 78.36 | 169.496 |

## Best design per layout (strict ranking set)

| case | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| dp 0 (baseline) | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| dp 0 (baseline) | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| dp 0 (baseline) | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| dp 0 (baseline) | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| dp 0 (baseline) | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| dp 1 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14471 | 48.69 | 58.735 |
| dp 1 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.32148 | 60.04 | 142.514 |
| dp 1 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.40582 | 79.74 | 178.917 |
| dp 1 % | 4 | L4_Ph200_Pl085_T320_Tt500_Pm140 | 0.34920 | 85.52 | 149.728 |
| dp 1 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.40654 | 82.65 | 178.541 |
| dp 2 % | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14116 | 48.69 | 56.999 |
| dp 2 % | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.30941 | 60.46 | 136.494 |
| dp 2 % | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.38684 | 81.40 | 169.203 |
| dp 2 % | 4 | L4_Ph200_Pl081_T330_Tt500_Pm160 | 0.32859 | 80.73 | 140.829 |
| dp 2 % | 5 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 0.38980 | 88.59 | 168.854 |

## Rankings

| ranking | case | front size | knee | TOPSIS #1 | knee water kg/s | TOPSIS water kg/s |
|---|---|---|---|---|---|---|
| main | dp 0 (baseline) | 60 | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) |  |  |
| main | dp 1 % | 54 | L6_Ph200_T335_Tt500_Pm079_Pe038_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.8 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 621 | 617 |
| main | dp 2 % | 43 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 609 | 609 |
| strict | dp 0 (baseline) | 37 | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) |  |  |
| strict | dp 1 % | 37 | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 1015 | 1015 |
| strict | dp 2 % | 37 | L3_Ph200_Pl077_T325_Tt500_x045 (layout 3, T_in 32.5 C, x 0.45) | L3_Ph200_Pl077_T325_Tt500_x045 (layout 3, T_in 32.5 C, x 0.45) | 1025 | 1025 |

## Incremental payback against the reference (L2_Ph200_Pl077_T340_Tt500, same dp)

| case | design | ID | extra cost M$ | extra value M$/yr | payout M$ | simple payback yr | payback r=8% yr |
|---|---|---|---|---|---|---|---|
| dp 0 (baseline) | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 2.292 | 2.652 | 172.430 | 0.86 | 0.93 |
| dp 0 (baseline) | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 2.710 | 3.154 | 177.035 | 0.86 | 0.93 |
| dp 0 (baseline) | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 2.592 | 2.957 | 175.182 | 0.88 | 0.94 |
| dp 0 (baseline) | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 4.561 | 4.408 | 187.721 | 1.03 | 1.12 |
| dp 0 (baseline) | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 2.879 | 3.362 | 178.942 | 0.86 | 0.92 |
| dp 1 % | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 2.227 | 2.497 | 165.094 | 0.89 | 0.96 |
| dp 1 % | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 2.899 | 2.833 | 167.775 | 1.02 | 1.11 |
| dp 1 % | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 2.785 | 2.595 | 165.511 | 1.07 | 1.17 |
| dp 1 % | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 4.832 | 4.140 | 178.917 | 1.17 | 1.27 |
| dp 1 % | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 3.085 | 3.012 | 169.379 | 1.02 | 1.11 |
| dp 2 % | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 2.165 | 2.340 | 157.403 | 0.93 | 1.00 |
| dp 2 % | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 3.113 | 2.448 | 157.533 | 1.27 | 1.39 |
| dp 2 % | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 3.006 | 2.163 | 154.794 | 1.39 | 1.53 |
| dp 2 % | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 5.136 | 3.817 | 169.203 | 1.35 | 1.48 |
| dp 2 % | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 3.321 | 2.594 | 158.787 | 1.28 | 1.40 |

## Do the rankings change? (against dp 0)

**dp 1 %**

- main knee: L6_Ph200_T335_Tt500_Pm079_Pe036_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe038_x038 (changes: P_exh).
- main topsis: unchanged (L6_Ph200_T335_Tt500_Pm079_Pe037_x038).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T325_Tt500_x046 (changes: T_in, split).
- strict topsis: unchanged (L3_Ph200_Pl077_T325_Tt500_x046).

**dp 2 %**

- main knee: L6_Ph200_T335_Tt500_Pm079_Pe036_x038 -> L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (changes: P_exh).
- main topsis: unchanged (L6_Ph200_T335_Tt500_Pm079_Pe037_x038).
- strict knee: L3_Ph200_Pl077_T330_Tt500_x043 -> L3_Ph200_Pl077_T325_Tt500_x045 (changes: T_in, split).
- strict topsis: L3_Ph200_Pl077_T325_Tt500_x046 -> L3_Ph200_Pl077_T325_Tt500_x045 (changes: split).

Plots: pareto_dp1pct.png, pareto_dp1pct_strict.png, pareto_dp2pct.png, pareto_dp2pct_strict.png.

