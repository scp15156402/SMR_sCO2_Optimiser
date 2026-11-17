# S5: discounting

Payout replaced by NPV = annual electricity value x sum_{t=1..N} (1+r)^-t - hardware cost (hardware paid at t = 0, value at the end of each year). Baseline results, no re-solve; mass unchanged. r = 0 reproduces the undiscounted payout.

## Knee and TOPSIS #1

| N | r % | ranking | knee | TOPSIS #1 | TOPSIS #1 NPV M$ | front size |
|---|---|---|---|---|---|---|
| 10 | 0 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 172.43 | 60 |
| 10 | 0 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 177.04 | 37 |
| 10 | 3 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 144.55 | 59 |
| 10 | 3 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 148.41 | 36 |
| 10 | 5 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 129.21 | 59 |
| 10 | 5 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 132.67 | 36 |
| 10 | 8 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 110.01 | 58 |
| 10 | 8 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 112.97 | 35 |
| 10 | 10 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 99.28 | 58 |
| 10 | 10 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 101.95 | 35 |
| 20 | 0 | main | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 362.15 | 68 |
| 20 | 0 | strict | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 371.78 | 44 |
| 20 | 3 | main | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 264.97 | 65 |
| 20 | 3 | strict | L3_Ph200_Pl077_T325_Tt500_x044 (layout 3, T_in 32.5 C, x 0.44) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 272.02 | 41 |
| 20 | 5 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 219.14 | 63 |
| 20 | 5 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 224.99 | 39 |
| 20 | 8 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 168.98 | 60 |
| 20 | 8 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 173.49 | 37 |
| 20 | 10 | main | L6_Ph200_T335_Tt500_Pm079_Pe036_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.6 MPa) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (layout 6, T_in 33.5 C, x 0.38, P_exh 3.7 MPa) | 144.23 | 59 |
| 20 | 10 | strict | L3_Ph200_Pl077_T330_Tt500_x043 (layout 3, T_in 33 C, x 0.43) | L3_Ph200_Pl077_T325_Tt500_x046 (layout 3, T_in 32.5 C, x 0.46) | 148.09 | 36 |

## Incremental payback against the reference (L2_Ph200_Pl077_T340_Tt500)

Extra hardware cost and extra annual electricity value against the reference; payback in years, simple (r = 0) and discounted.

| design | ID | extra cost M$ | extra value M$/yr | payback r=0% (yr) | payback r=3% (yr) | payback r=5% (yr) | payback r=8% (yr) | payback r=10% (yr) |
|---|---|---|---|---|---|---|---|---|
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 2.292 | 2.652 | 0.86 | 0.89 | 0.91 | 0.93 | 0.95 |
| Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 2.710 | 3.154 | 0.86 | 0.88 | 0.90 | 0.93 | 0.94 |
| Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 2.592 | 2.957 | 0.88 | 0.90 | 0.92 | 0.94 | 0.96 |
| Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 4.561 | 4.408 | 1.03 | 1.07 | 1.09 | 1.12 | 1.15 |
| Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 2.879 | 3.362 | 0.86 | 0.88 | 0.90 | 0.92 | 0.94 |

Plots: pareto_N10_r8(_strict).png, pareto_N20_r8(_strict).png (y axis is the NPV).

