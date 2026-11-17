# S6: turbine inlet temperature 400 to 500 C

Each design re-solved at T_turb = 400 to 500 C in 10 C steps with every other variable fixed (pressures, T_in, split; recuperator effectiveness 0.90 and cooler pinch 5 K, i.e. a re-design at each temperature, not off-design). Designs: best payout of layouts 2 to 6 and the named designs.

## eta against T_turb

| T_turb C | Best payout L2<br>L2_Ph200_Pl077_T335_Tt500 | Best payout L3 / Highest payout<br>L3_Ph200_Pl077_T320_Tt500_x036 | Best payout L4<br>L4_Ph200_Pl081_T320_Tt500_Pm160 | Best payout L5<br>L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | Best payout L6<br>L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | Reference<br>L2_Ph200_Pl077_T340_Tt500 | Main TOPSIS #1<br>L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | Strict TOPSIS #1<br>L3_Ph200_Pl077_T325_Tt500_x046 | Strict knee<br>L3_Ph200_Pl077_T330_Tt500_x043 | Submitted design<br>L3_Ph200_Pl077_T330_Tt500_x040 |
|---|---|---|---|---|---|---|---|---|---|---|
| 400 | 0.29734 | 0.37140 | infeasible (recup_pinch<5K (1.0326)) | 0.37298 | 0.35632 | 0.29662 | 0.31803 | 0.35018 | 0.34394 | 0.35249 |
| 410 | 0.30141 | 0.37740 | infeasible (recup_pinch<5K (1.4765)) | 0.37889 | 0.36310 | 0.30081 | 0.32590 | 0.35573 | 0.34977 | 0.35827 |
| 420 | 0.30536 | 0.38321 | infeasible (recup_pinch<5K (1.9162)) | 0.38463 | 0.36969 | 0.30485 | 0.33353 | 0.36107 | 0.35537 | 0.36383 |
| 430 | 0.30918 | 0.38887 | infeasible (recup_pinch<5K (2.3653)) | 0.39021 | 0.37608 | 0.30877 | 0.34093 | 0.36621 | 0.36076 | 0.36918 |
| 440 | 0.31288 | 0.39436 | infeasible (recup_pinch<5K (2.8046)) | 0.39564 | 0.38228 | 0.31256 | 0.34812 | 0.37116 | 0.36595 | 0.37434 |
| 450 | 0.31647 | 0.39971 | infeasible (recup_pinch<5K (3.2640)) | 0.40092 | 0.38831 | 0.31624 | 0.35509 | 0.37594 | 0.37095 | 0.37931 |
| 460 | 0.31995 | 0.40491 | infeasible (recup_pinch<5K (3.7010)) | 0.40606 | 0.39418 | 0.31981 | 0.36187 | 0.38055 | 0.37577 | 0.38410 |
| 470 | 0.32333 | 0.40998 | infeasible (recup_pinch<5K (4.1548)) | 0.41107 | 0.39989 | 0.32327 | 0.36846 | 0.38499 | 0.38042 | 0.38873 |
| 480 | 0.32662 | 0.41487 | infeasible (recup_pinch<5K (4.6112)) | 0.41584 | 0.40545 | 0.32663 | 0.37487 | 0.38929 | 0.38490 | 0.39319 |
| 490 | 0.32981 | 0.41901 | 0.35675 | 0.41997 | 0.41086 | 0.32989 | 0.38111 | 0.39343 | 0.38923 | 0.39751 |
| 500 | 0.33292 | 0.42302 | 0.35938 | 0.42397 | 0.41578 | 0.33306 | 0.38719 | 0.39744 | 0.39342 | 0.40167 |

## Change from 400 to 500 C

| design | ID | eta 400 C | eta 500 C | d eta per 10 C (pp) | eta_II 400 C | eta_II 500 C |
|---|---|---|---|---|---|---|
| Best payout L2 | L2_Ph200_Pl077_T335_Tt500 | 0.29734 | 0.33292 | 0.356 | 0.5461 | 0.5518 |
| Best payout L3 / Highest payout | L3_Ph200_Pl077_T320_Tt500_x036 | 0.37140 | 0.42302 | 0.516 | 0.6794 | 0.6988 |
| Best payout L5 | L5_Ph200_Pl077_T320_Tt500_Pm079_x036 | 0.37298 | 0.42397 | 0.510 | 0.6823 | 0.7004 |
| Best payout L6 | L6_Ph200_T320_Tt500_Pm077_Pe052_x045 | 0.35632 | 0.41578 | 0.595 | 0.6518 | 0.6869 |
| Reference | L2_Ph200_Pl077_T340_Tt500 | 0.29662 | 0.33306 | 0.364 | 0.5456 | 0.5526 |
| Main TOPSIS #1 | L6_Ph200_T335_Tt500_Pm079_Pe037_x038 | 0.31803 | 0.38719 | 0.692 | 0.5841 | 0.6417 |
| Strict TOPSIS #1 | L3_Ph200_Pl077_T325_Tt500_x046 | 0.35018 | 0.39744 | 0.473 | 0.6414 | 0.6573 |
| Strict knee | L3_Ph200_Pl077_T330_Tt500_x043 | 0.34394 | 0.39342 | 0.495 | 0.6309 | 0.6513 |
| Submitted design | L3_Ph200_Pl077_T330_Tt500_x040 | 0.35249 | 0.40167 | 0.492 | 0.6465 | 0.6650 |

Plot: eta_vs_T_turb.png.

