# Refinement convergence (branch wager)

Stop when, against the previous round: best payout per layout moves < 0.05 %; TOPSIS #1 payout and mass (with and without layout 1) move < 0.1 %; no layout 2/3/5/6 winner (best payout or best TOPSIS) on a non-constraint grid edge. Round 0 is the state inherited from branch rebuild.

## Rounds

| round | points added | total feasible | TOPSIS #1 (with L1) | TOPSIS #1 (no L1) | knee (with L1) | knee (no L1) | payout < 0.05 % | TOPSIS < 0.1 % | no free edge | wall min |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 969 | L3_Ph200_Pl077_T330_Tt500_x040 (178.94 M$, 71.52 t) | L3_Ph200_Pl077_T330_Tt500_x040 (178.94 M$, 71.52 t) | L2_Ph200_Pl077_T340_Tt500 | L3_Ph200_Pl077_T330_Tt500_x040 | no | no | no | 0.0 |
| 1 | 1455 | 2413 | L6_Ph200_T340_Tt500_Pm081_Pe040_x035 (171.16 M$, 69.05 t) | L6_Ph200_T340_Tt500_Pm081_Pe040_x040 (174.37 M$, 70.02 t) | L2_Ph200_Pl077_T335_Tt500 | L6_Ph200_T340_Tt500_Pm081_Pe040_x040 | no | no | no | 80.8 |

## Best payout design per layout

| round | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| 0 | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 0 | 2 | L2_Ph200_Pl077_T340_Tt500 | 0.33306 | 60.00 | 148.201 |
| 0 | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 0 | 4 | L4_Ph200_Pl082_T320_Tt500_Pm140 | 0.34084 | 75.54 | 148.129 |
| 0 | 5 | L5_Ph200_Pl077_T320_Tt500_Pm100_x035 | 0.42453 | 86.47 | 186.404 |
| 0 | 6 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | 0.41591 | 77.33 | 184.463 |
| 1 | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 1 | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| 1 | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 1 | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| 1 | 5 | L5_Ph200_Pl077_T320_Tt500_Pm090_x036 | 0.42402 | 83.46 | 186.904 |
| 1 | 6 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | 0.41591 | 77.33 | 184.463 |

## Winners on a non-constraint grid edge (after each round)

| round | ID | free edges |
|---|---|---|
| 0 | L2_Ph200_Pl077_T340_Tt500 | - |
| 0 | L3_Ph200_Pl077_T330_Tt500_x040 | x+ |
| 0 | L3_Ph200_Pl077_T320_Tt500_x036 | - |
| 0 | L5_Ph200_Pl077_T400_Tt500_Pm100_x025 | T+, Pm- |
| 0 | L5_Ph200_Pl077_T320_Tt500_Pm100_x035 | Pm-, x+ |
| 0 | L6_Ph200_T320_Tt500_Pm077_Pe045_x035 | Pe- |
| 0 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | - |
| 1 | L2_Ph200_Pl077_T335_Tt500 | - |
| 1 | L3_Ph200_Pl077_T330_Tt500_x044 | - |
| 1 | L3_Ph200_Pl077_T320_Tt500_x036 | - |
| 1 | L5_Ph200_Pl077_T330_Tt500_Pm090_x042 | Pm-, x+ |
| 1 | L5_Ph200_Pl077_T320_Tt500_Pm090_x036 | Pm- |
| 1 | L6_Ph200_T340_Tt500_Pm081_Pe040_x035 | Pe- |
| 1 | L6_Ph200_T320_Tt500_Pm077_Pe055_x045 | - |

## Verdict

(continuing)
