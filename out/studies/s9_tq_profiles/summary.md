# S9: exchanger temperature profiles (T-Q)

Each named design solved with 100 slices on every recuperator and cooler (baseline settings: effectiveness 0.90, cooler pinch 5 K, no pressure drop). Duty is measured from the cold end (x = 0: cold stream in, hot stream out). Pinch location x is the fraction of duty from the cold end.

| design | ID | exchanger | role | duty MW | pinch K | pinch at x | dT cold end K | dT hot end K |
|---|---|---|---|---|---|---|---|---|
| Reference | L2_Ph200_Pl077_T340_Tt500 | RECUP | recup_1 | 121.63 | 26.80 | 0.00 | 26.80 | 98.93 |
| Reference | L2_Ph200_Pl077_T340_Tt500 | COOLER | cooler_1 | 66.69 | 5.00 | 0.22 | 9.00 | 49.40 |
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | HTR | recup_1 | 53.85 | 16.16 | 0.00 | 16.16 | 47.06 |
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | LTR | recup_2 | 36.53 | 10.49 | 0.00 | 10.49 | 34.16 |
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | PC2 | cooler_1 | 43.69 | 5.00 | 0.31 | 8.50 | 54.27 |
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | PC1 | cooler_2 | 17.59 | 5.00 | 1.00 | 8.50 | 5.00 |
| Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | HTR | recup_1 | 109.56 | 19.73 | 0.00 | 19.73 | 39.89 |
| Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | LTR | recup_2 | 73.83 | 20.21 | 1.00 | 33.69 | 20.21 |
| Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | PC | cooler_1 | 60.26 | 5.00 | 0.29 | 7.50 | 59.98 |
| Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | HTR | recup_1 | 105.11 | 18.49 | 0.00 | 18.49 | 36.04 |
| Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | LTR | recup_2 | 74.92 | 19.36 | 1.00 | 32.31 | 19.36 |
| Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | PC | cooler_1 | 60.66 | 5.00 | 0.23 | 8.00 | 61.89 |
| Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | HTR | recup_1 | 116.98 | 22.12 | 0.00 | 22.12 | 48.97 |
| Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | LTR | recup_2 | 76.25 | 10.42 | 0.00 | 10.42 | 17.69 |
| Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | PC | cooler_1 | 57.70 | 5.00 | 0.37 | 7.00 | 36.07 |
| Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | HTR | recup_1 | 107.51 | 19.14 | 0.00 | 19.14 | 38.02 |
| Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | LTR | recup_2 | 75.38 | 18.57 | 1.00 | 24.86 | 18.57 |
| Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | PC | cooler_1 | 59.83 | 5.00 | 0.24 | 8.00 | 55.63 |

Plots: TQ_<ID>_<exchanger>.png per exchanger, TQ_<ID>_all.png per design.

