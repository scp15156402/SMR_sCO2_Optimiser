# S4: separate cost per kg (exchangers vs the rest)

Hardware cost = c_hx x (recuperator + cooler mass) + c_tm x (M0 + added-compressor mass). For each ratio c_tm / c_hx, c_hx is chosen so the reference design (L2_Ph200_Pl077_T340_Tt500, 60 t) costs exactly what it does at 250 USD/kg (15 M$). Baseline results, N = 10, no re-solve. Mass is unchanged, so only the payout axis moves. Ratio 1 is the baseline.

## Knee and TOPSIS #1

| c_tm/c_hx | c_hx USD/kg | c_tm USD/kg | ranking | knee | TOPSIS #1 | front size |
|---|---|---|---|---|---|---|
| 0.5 | 370.6 | 185.3 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | 59 |
| 0.5 | 370.6 | 185.3 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 35 |
| 1 | 250.0 | 250.0 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 60 |
| 1 | 250.0 | 250.0 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 37 |
| 2 | 151.4 | 302.9 | main | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe038_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.8 MPa) | 63 |
| 2 | 151.4 | 302.9 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 39 |
| 4 | 84.7 | 338.6 | main | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 65 |
| 4 | 84.7 | 338.6 | strict | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 41 |
| 8 | 45.0 | 359.9 | main | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 66 |
| 8 | 45.0 | 359.9 | strict | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x045 (layout 3, T_in 32.5 C, x 0.45) | 42 |

## Top 5 by payout (ranked layouts)

| c_tm/c_hx | ranking | # | ID | mass t | payout M$ |
|---|---|---|---|---|---|
| 0.5 | main | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 185.798 |
| 0.5 | main | 2 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 185.549 |
| 0.5 | main | 3 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 185.515 |
| 0.5 | main | 4 | L3_Ph200_Pl077_T325_Tt500_x035 | 77.17 | 185.499 |
| 0.5 | main | 5 | L3_Ph200_Pl077_T320_Tt500_x035 | 78.25 | 185.498 |
| 0.5 | strict | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 185.798 |
| 0.5 | strict | 2 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 185.549 |
| 0.5 | strict | 3 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 185.515 |
| 0.5 | strict | 4 | L3_Ph200_Pl077_T325_Tt500_x035 | 77.17 | 185.499 |
| 0.5 | strict | 5 | L3_Ph200_Pl077_T320_Tt500_x035 | 78.25 | 185.498 |
| 1 | main | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 187.721 |
| 1 | main | 2 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 187.493 |
| 1 | main | 3 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 187.485 |
| 1 | main | 4 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 187.464 |
| 1 | main | 5 | L3_Ph200_Pl077_T320_Tt500_x035 | 78.25 | 187.421 |
| 1 | strict | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 187.721 |
| 1 | strict | 2 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 187.493 |
| 1 | strict | 3 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 187.485 |
| 1 | strict | 4 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 187.464 |
| 1 | strict | 5 | L3_Ph200_Pl077_T320_Tt500_x035 | 78.25 | 187.421 |
| 2 | main | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 189.292 |
| 2 | main | 2 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 189.279 |
| 2 | main | 3 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 189.141 |
| 2 | main | 4 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 189.109 |
| 2 | main | 5 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 189.029 |
| 2 | strict | 1 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 189.292 |
| 2 | strict | 2 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 189.279 |
| 2 | strict | 3 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 189.141 |
| 2 | strict | 4 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 189.109 |
| 2 | strict | 5 | L5_Ph200_Pl077_T320_Tt500_Pm078_x036 | 80.48 | 189.029 |
| 4 | main | 1 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 190.661 |
| 4 | main | 2 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 88.76 | 190.437 |
| 4 | main | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 190.357 |
| 4 | main | 4 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 190.262 |
| 4 | main | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 190.204 |
| 4 | strict | 1 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 190.661 |
| 4 | strict | 2 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 88.76 | 190.437 |
| 4 | strict | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 190.357 |
| 4 | strict | 4 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 190.262 |
| 4 | strict | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 81.00 | 190.204 |
| 8 | main | 1 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 191.482 |
| 8 | main | 2 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 88.76 | 191.395 |
| 8 | main | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 190.989 |
| 8 | main | 4 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 190.929 |
| 8 | main | 5 | L5_Ph200_Pl077_T320_Tt500_Pm100_x035 | 86.47 | 190.885 |
| 8 | strict | 1 | L5_Ph200_Pl077_T320_Tt500_Pm090_x035 | 85.31 | 191.482 |
| 8 | strict | 2 | L5_Ph200_Pl077_T320_Tt500_Pm100_x034 | 88.76 | 191.395 |
| 8 | strict | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 78.24 | 190.989 |
| 8 | strict | 4 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 81.41 | 190.929 |
| 8 | strict | 5 | L5_Ph200_Pl077_T320_Tt500_Pm100_x035 | 86.47 | 190.885 |

## Named designs

| c_tm/c_hx | design | ID | hardware M$ | payout M$ |
|---|---|---|---|---|
| 0.5 | Reference | L2_Ph200_Pl077_T340_Tt500 | 15.000 | 148.201 |
| 0.5 | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 17.843 | 171.880 |
| 0.5 | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 18.740 | 176.005 |
| 0.5 | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 18.565 | 174.209 |
| 0.5 | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 21.484 | 185.798 |
| 0.5 | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 18.990 | 177.831 |
| 1 | Reference | L2_Ph200_Pl077_T340_Tt500 | 15.000 | 148.201 |
| 1 | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 17.292 | 172.430 |
| 1 | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 17.710 | 177.035 |
| 1 | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 17.592 | 175.182 |
| 1 | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 19.561 | 187.721 |
| 1 | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 17.879 | 178.942 |
| 2 | Reference | L2_Ph200_Pl077_T340_Tt500 | 15.000 | 148.201 |
| 2 | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 16.843 | 172.880 |
| 2 | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 16.869 | 177.877 |
| 2 | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 16.797 | 175.977 |
| 2 | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 17.990 | 189.292 |
| 2 | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 16.971 | 179.850 |
| 4 | Reference | L2_Ph200_Pl077_T340_Tt500 | 15.000 | 148.201 |
| 4 | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 16.538 | 173.185 |
| 4 | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 16.299 | 178.447 |
| 4 | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 16.259 | 176.515 |
| 4 | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 16.926 | 190.357 |
| 4 | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 16.356 | 180.465 |
| 8 | Reference | L2_Ph200_Pl077_T340_Tt500 | 15.000 | 148.201 |
| 8 | Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 16.357 | 173.366 |
| 8 | Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 15.960 | 178.785 |
| 8 | Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 15.939 | 176.835 |
| 8 | Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 16.293 | 190.989 |
| 8 | Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 15.990 | 180.830 |

Plots: pareto_ratio0.5(_strict).png and pareto_ratio8(_strict).png (the extremes; the y axis is the recosted 10-year payout).

