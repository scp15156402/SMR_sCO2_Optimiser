# S8: layout 1 with pressurised cooling water

Layout 1 (simple, no recuperator) sends turbine exhaust at several hundred C straight to the cooler. At the solver's default 6 bar the water side reaches saturation and CoolProp raises, so 9 of 18 grid points fail. Here the water pressure is raised for layout 1 only. The brief asked for 20 bar, then 50 bar; neither was enough, so the ladder continued until every point solved. The water pressure changes only the water side (cooler UA, water flow), not the cycle: eta is unchanged.

| water pressure bar | feasible | failed | failure reasons |
|---|---|---|---|
| 20 | 13 | 5 | error: ValueError: Saturation pressure [2e+06 Pa] correspond |
| 50 | 15 | 3 | error: ValueError: Saturation pressure [5e+06 Pa] correspond |
| 100 | 18 | 0 | - |

**Lowest pressure that solves all 18: 100 bar.**

## Layout 1 results at 100 bar (baseline M0 = 39.059 t, N = 10)

| ID | eta | UA_recup | UA_cooler kW/K | mass t | payout M$ | water kg/s | solved at 6 bar | mass at 6 bar t |
|---|---|---|---|---|---|---|---|---|
| L1_Ph200_Pl077_T360_Tt500 | 0.14904 | - | 3818 | 48.61 | 60.879 | 107 | no (failed at 6 bar) | - |
| L1_Ph200_Pl077_T320_Tt500 | 0.14820 | - | 3851 | 48.69 | 60.447 | 636 | yes | 48.69 |
| L1_Ph200_Pl077_T400_Tt500 | 0.14689 | - | 4875 | 51.25 | 59.162 | 76 | no (failed at 6 bar) | - |
| L1_Ph180_Pl077_T360_Tt500 | 0.13437 | - | 3797 | 48.55 | 53.701 | 106 | no (failed at 6 bar) | - |
| L1_Ph180_Pl077_T320_Tt500 | 0.13367 | - | 3831 | 48.64 | 53.340 | 630 | yes | 48.64 |
| L1_Ph200_Pl087_T400_Tt500 | 0.13211 | - | 3905 | 48.82 | 52.531 | 117 | no (failed at 6 bar) | - |
| L1_Ph180_Pl077_T400_Tt500 | 0.13242 | - | 4842 | 51.16 | 52.094 | 75 | no (failed at 6 bar) | - |
| L1_Ph200_Pl087_T360_Tt500 | 0.13024 | - | 3904 | 48.82 | 51.612 | 227 | yes | 48.82 |
| L1_Ph200_Pl087_T320_Tt500 | 0.12800 | - | 4275 | 49.75 | 50.282 | 291 | yes | 49.75 |
| L1_Ph160_Pl077_T360_Tt500 | 0.11739 | - | 3783 | 48.52 | 45.390 | 104 | no (failed at 6 bar) | - |
| L1_Ph180_Pl087_T400_Tt500 | 0.11699 | - | 3862 | 48.71 | 45.149 | 116 | no (failed at 6 bar) | - |
| L1_Ph160_Pl077_T320_Tt500 | 0.11687 | - | 3816 | 48.60 | 45.116 | 623 | yes | 48.60 |
| L1_Ph180_Pl087_T360_Tt500 | 0.11536 | - | 3877 | 48.75 | 44.338 | 226 | yes | 48.75 |
| L1_Ph160_Pl077_T400_Tt500 | 0.11568 | - | 4819 | 51.11 | 43.906 | 74 | no (failed at 6 bar) | - |
| L1_Ph180_Pl087_T320_Tt500 | 0.11336 | - | 4253 | 49.69 | 43.124 | 289 | yes | 49.69 |
| L1_Ph160_Pl087_T400_Tt500 | 0.09951 | - | 3828 | 48.63 | 36.601 | 115 | no (failed at 6 bar) | - |
| L1_Ph160_Pl087_T360_Tt500 | 0.09815 | - | 3858 | 48.70 | 35.919 | 224 | yes | 48.71 |
| L1_Ph160_Pl087_T320_Tt500 | 0.09645 | - | 4242 | 49.66 | 34.843 | 287 | yes | 49.66 |

## Does any conclusion change?

Best layout 1 design: L1_Ph200_Pl077_T360_Tt500, eta 0.1490, payout 60.88 M$, against the worst-ranked layout's best (layout 2, L2_Ph200_Pl077_T335_Tt500: 148.22 M$) and the main TOPSIS #1 (L6_Ph200_T335_Tt500_Pm079_Pe037_x038: 172.43 M$). Layout 1 stays excluded from the ranking; the recovered points do not approach the other layouts.

