# Refinement convergence (branch wager)

Main ranking excludes layout 1 (RANK_EXCLUDE_LAYOUTS). Strict ranking also removes every design with a compressor inlet below 7.7 MPa (all of layout 6). Tracked winners: best payout in layouts 2, 3, 5, 6; TOPSIS #1 and knee (main); TOPSIS #1 (strict).

Stop when, against the previous round: best payout per layout (2, 3, 5, 6) moves < 0.05 %; TOPSIS #1 payout and mass (main and strict) move < 0.1 %; no tracked winner on a free (non-constraint) grid edge. Otherwise stop at the round or time limit.

**Caps used in this run:** none (effectively uncapped: --max-rounds 1000, --minutes 1e+06; no solve deadline)

## Rounds

| round | points added | total feasible | M0 used t (reference) | best payout L2 / L3 / L5 / L6 (M$) | TOPSIS #1 main | knee main | TOPSIS #1 strict | payout < 0.05 % | TOPSIS < 0.1 % | no free edge | wall min |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 (start of this run) | 0 | 2515 | 39.059 (L2_Ph200_Pl077_T340_Tt500) | 148.217 / 187.721 / 187.485 / 184.581 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 (170.222 M$, 68.40 t) | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 (170.222 M$, 68.40 t) | L3_Ph200_Pl077_T325_Tt500_x046 (177.035 M$, 70.84 t) | no | no | no | 0.0 |
| 3 | 44 | 2559 | 39.059 (L2_Ph200_Pl077_T340_Tt500) | 148.217 / 187.721 / 187.493 / 184.582 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (172.430 M$, 69.17 t) | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 (172.430 M$, 69.17 t) | L3_Ph200_Pl077_T325_Tt500_x046 (177.035 M$, 70.84 t) | yes | no | yes | 1.7 |

## Best payout design per layout

| round | layout | ID | eta | mass t | payout M$ |
|---|---|---|---|---|---|
| 2 | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 2 | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| 2 | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 2 | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| 2 | 5 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | 0.42416 | 81.41 | 187.485 |
| 2 | 6 | L6_Ph200_T320_Tt500_Pm077_Pe053_x045 | 0.41591 | 76.86 | 184.581 |
| 3 | 1 | L1_Ph200_Pl077_T320_Tt500 | 0.14820 | 48.69 | 60.447 |
| 3 | 2 | L2_Ph200_Pl077_T335_Tt500 | 0.33292 | 59.64 | 148.217 |
| 3 | 3 | L3_Ph200_Pl077_T320_Tt500_x036 | 0.42302 | 78.24 | 187.721 |
| 3 | 4 | L4_Ph200_Pl081_T320_Tt500_Pm160 | 0.35938 | 83.80 | 155.149 |
| 3 | 5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.42397 | 81.00 | 187.493 |
| 3 | 6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.41578 | 76.61 | 184.582 |

## Tracked winners on a free grid edge (after each round)

| round | ID | free edges |
|---|---|---|
| 2 | L2_Ph200_Pl077_T335_Tt500 | - |
| 2 | L3_Ph200_Pl077_T320_Tt500_x036 | - |
| 2 | L3_Ph200_Pl077_T325_Tt500_x046 | - |
| 2 | L5_Ph200_Pl077_T320_Tt500_Pm080_x036 | Pm- |
| 2 | L6_Ph200_T320_Tt500_Pm077_Pe053_x045 | - |
| 2 | L6_Ph200_T335_Tt500_Pm079_Pe035_x037 | - |
| 3 | L2_Ph200_Pl077_T335_Tt500 | - |
| 3 | L3_Ph200_Pl077_T320_Tt500_x036 | - |
| 3 | L3_Ph200_Pl077_T325_Tt500_x046 | - |
| 3 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | - |
| 3 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | - |
| 3 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | - |

## Earlier rounds (layout 1 still ranked, no strict ranking)

| round | points added | total feasible | TOPSIS #1 (with L1) | knee (with L1) |
|---|---|---|---|---|
| 0 | 0 | 969 | L3_Ph200_Pl077_T330_Tt500_x040 (178.942 M$, 71.52 t) | L2_Ph200_Pl077_T340_Tt500 |
| 1 | 1455 | 2413 | L6_Ph200_T340_Tt500_Pm081_Pe040_x035 (171.158 M$, 69.05 t) | L2_Ph200_Pl077_T335_Tt500 |
| 2 | 102 | 2515 | L6_Ph200_T335_Tt500_Pm079_Pe035_x035 (169.046 M$, 68.04 t) | L2_Ph200_Pl077_T335_Tt500 |

## Verdict

(continuing)
