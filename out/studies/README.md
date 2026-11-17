# Extended studies (branch curiostudy)

Baseline: main at 96d7df2. The main ranking leaves out layout 1. The strict ranking also requires every compressor inlet to be at or above 7.7 MPa, which removes all of layout 6. Baseline winners:

- Main ranking: knee L6_Ph200_T335_Tt500_Pm079_Pe036_x038, TOPSIS #1 L6_Ph200_T335_Tt500_Pm079_Pe037_x038.
- Strict ranking: knee L3_Ph200_Pl077_T330_Tt500_x043, TOPSIS #1 L3_Ph200_Pl077_T325_Tt500_x046.

Every study has its own folder holding summary.md, the CSVs and the plots, and every sweep can resume from where it stopped. data/results_*.csv were never overwritten.

**S1, cooler pinch 3 K and 8 K (s1_cooler_pinch/).** All 2656 designs were re-solved with the CO2-water cooler pinch at 3 K and at 8 K, and M0 was recalibrated each time. The reference stays L2_Ph200_Pl077_T340_Tt500, and M0 becomes 31.6 t at 3 K and 45.0 t at 8 K (39.1 t at 5 K). The pinch changes only the cooler UA, mass and water flow, not the cycle.

At 8 K, every design with T_in 32.0 or 32.5 C fails. The water enters at 25 C, so the widest approach those designs allow is 7 or 7.5 K. The solver converged on these points anyway, reporting the smaller pinch and water flows near 3×10^4 kg/s. A filter now records the 569 points as infeasible (pinch8_unreachable.csv). Two named designs drop out at 8 K: Highest payout and Strict TOPSIS #1.

- **Main ranking:** at 3 K, the knee is unchanged and TOPSIS #1 moves to layout 3 (L3_Ph200_Pl077_T325_Tt500_x047). At 8 K, both move within layout 6 to L6_Ph200_T330_Tt500_Pm077_Pe045_x030.
- **Strict ranking:** layout 3 stays, with T_in moving between 32.5 and 33 C and x between 0.42 and 0.47. Strict TOPSIS #1 is L3_Ph200_Pl077_T325_Tt500_x047 at 3 K and L3_Ph200_Pl077_T330_Tt500_x042 at 8 K.

An 8 K pinch also pushes the winners' water flow from about 600 kg/s to about 4,000 kg/s. The recommendation holds under the strict reading. Under the main reading it holds at 8 K and becomes a near-tie between layouts 3 and 6 at 3 K.

**S2, compressor-inlet temperature drift (s2_tin_drift/).** The six named designs were held at their design recuperator UA, pressures and split while T_in moved from 32 to 36 C in 0.25 K steps. The coolers could not be frozen at a UA because the cooler model accepts only a pinch spec. They keep the 5 K pinch, and the summary reports the UA they would need instead. The frozen model reproduces each design's efficiency to within 0.00002.

Mean efficiency slopes:

- Reference (layout 2): −0.16 percentage points per K.
- Main TOPSIS #1 (layout 6): −0.25 points per K, almost flat up to 34 C.
- Layout 3 designs: between −1.0 and −1.4 points per K. Most of the drop happens between 32.5 and 33.5 C, where the compressor-inlet density falls from about 550 to about 365 kg/m3 as T_in crosses the pseudo-critical line.

The two curves meet at 33.75 C (0.3870 each), and above that the layout 6 design is more efficient than the submitted layout 3 design. Limitations: this is a sensitivity estimate, not true off-design. Efficiencies are fixed, there are no turbomachinery maps, and pressures and split are not adjusted.

The ranking itself doesn't change, but this is the strongest qualitative argument for the main reading. If the cooler cannot hold T_in near 32.5 C, the layout 3 designs lose most of their efficiency advantage. The strict reading is unaffected because it excludes layout 6.

**S3, pressure drops of 1 % and 2 % per exchanger side (s3_pressure_drop/).** All 2656 designs were re-solved with a fractional pressure drop on both recuperator sides, every cooler and the heater. M0 is held at the baseline 39.059 t, and the baseline reference L2_Ph200_Pl077_T340_Tt500 (re-solved at each dp) is used for payback.

- **Efficiency loss** (best design per layout at 1 % / 2 %):
  - Layout 2: 1.05 / 2.14 points.
  - Layout 3: 1.72 / 3.62 points.
  - Layout 5: 1.66 / 3.51 points.
  - Layout 6: 1.44 / 2.99 points.
  - The medians are similar. Layouts with more exchangers in series lose most.
- **Feasible counts** barely move (layout 5: 232 → 229 → 224; layout 6: 722 → 728).
- **Why M0 is fixed:** recalibrating would pick a different, high-UA reference (L2_Ph200_Pl097_T320_Tt500) and drop M0 to 20.5 t and 18.6 t. A uniform mass shift leaves the Pareto front and the min-max knee unchanged, but it moves TOPSIS, whose vector normalisation is not shift-invariant. The first S3 run recalibrated M0, and that alone made strict TOPSIS #1 flip to the layout 2 design L2_Ph200_Pl077_T335_Tt500.
- **Main ranking:** TOPSIS #1 is unchanged at 1 % and 2 % (L6_Ph200_T335_Tt500_Pm079_Pe037_x038). The knee only shifts P_exh by ±0.1 MPa.
- **Strict ranking:** TOPSIS #1 stays in layout 3 at 32.5 C: L3_Ph200_Pl077_T325_Tt500_x046 at 1 % (unchanged) and x045 at 2 %. The knee is the same design at each level.

Neither recommendation changes: both are robust to pressure drops of 1–2 % per exchanger side.

**S4, separate cost per kg for exchangers and the rest (s4_cost_split/).** Exchangers are priced at c_hx and the fixed and turbomachinery mass at c_tm, with c_tm/c_hx = 0.5, 1, 2, 4 and 8. In every case c_hx is set so the reference still costs 15 M$. This uses the baseline results with no re-solve.

- **Main ranking:** stays layout 6 for ratios 0.5 to 2. At ratios 4 and 8, exchangers become cheap and both winners switch to layout 3: knee L3_Ph200_Pl077_T325_Tt500_x044, TOPSIS #1 L3_Ph200_Pl077_T325_Tt500_x046.
- **Strict ranking:** the knee is L3_Ph200_Pl077_T330_Tt500_x043 for ratios up to 2, and becomes L3_Ph200_Pl077_T325_Tt500_x044 at ratios 4 and 8. TOPSIS #1 is L3_Ph200_Pl077_T325_Tt500_x046 at every ratio except 8, where it is x045.
- **Top payout:** L3_Ph200_Pl077_T320_Tt500_x036 is the top-payout design up to ratio 2. Above that, the intercooled layout 5 design L5_Ph200_Pl077_T320_Tt500_Pm090_x035 takes over.

The main recommendation changes only when exchangers cost less than about a quarter as much per kg as the rest of the plant. In that case it converges on the strict answer. The strict reading does not change.

**S5, discounting (s5_discounting/).** Payout was replaced by NPV, with r = 0, 3, 5, 8 and 10 % and N = 10 and 20 years. This uses the baseline results with no re-solve.

- **Main ranking:** TOPSIS #1 is L6_Ph200_T335_Tt500_Pm079_Pe037_x038 in every case. The knee is the layout 6 design except at N = 20 with r = 0–3 %, where it is L3_Ph200_Pl077_T325_Tt500_x044.
- **Strict ranking:** TOPSIS #1 is L3_Ph200_Pl077_T325_Tt500_x046 in every case. The knee is L3_Ph200_Pl077_T330_Tt500_x043, or x044 at N = 20 with low r.
- **Payback against the reference:** every named design pays back in under 1.2 years even at 10 %. Simple payback is 0.86 years for Main TOPSIS #1, Strict TOPSIS #1 and the Submitted design, 0.88 for the Strict knee and 1.03 for Highest payout. Because payback is so short, discounting barely matters.

Neither recommendation changes, apart from the main knee at long horizons with low discount rates.

**S6, turbine inlet temperature 400 to 500 C (s6_t_turb/).** The best-payout design of layouts 2–6 and the named designs were re-solved at each T_turb with everything else fixed (design-point solve).

- **Efficiency rise per 10 C:**
  - Layout 2: 0.36 points.
  - Layout 3: 0.47–0.52 points.
  - Layout 5: 0.51 points.
  - Layout 6: 0.60 points (best payout) and 0.69 points (Main TOPSIS #1).
- **Layout 4:** the best layout 4 design breaks the 5 K recuperator pinch below 490 C, so it is infeasible there.
- **Order at 400 C:** Highest payout 0.371, Submitted design 0.352, Strict TOPSIS #1 0.350, Strict knee 0.344, Main TOPSIS #1 0.318, Reference 0.297.

Layout 6 depends most on high T_turb. A lower turbine temperature therefore favours the strict, layout 3 answer, while the main answer remains a valid design at every temperature.

**S7, P_high from 14 to 20 MPa (s7_p_high/).** The named designs were re-solved at each P_high in 0.25 MPa steps, with payout at the baseline M0. For every design, efficiency and payout are still rising at 20 MPa, and maximum payout is at the 20 MPa limit.

Slopes over the last 0.5 MPa (efficiency in points per MPa, payout in M$ per MPa):

| Design | Efficiency | Payout |
|---|---|---|
| Reference | +0.52 | +2.68 |
| Highest payout | +0.24 | +1.57 |
| Main TOPSIS #1 | +0.16 | +0.77 |
| Submitted design | +0.08 | +0.63 |
| Strict TOPSIS #1 | +0.07 | +0.61 |
| Strict knee | +0.03 | +0.38 |

The 20 MPa cap is binding, but the marginal gain for the recommended designs is small (under 1 M$ per MPa). The recommendation does not change under either reading.

**S8, layout 1 with pressurised cooling water (s8_layout1_water/).** At the default 6 bar, 9 of the 18 layout 1 points fail because the water side reaches saturation. 20 bar recovers 13 of 18 and 50 bar 15 of 18, so the ladder continued, and 100 bar is the lowest pressure that solves all 18. The water pressure changes only the water side, not the cycle.

The best layout 1 design is L1_Ph200_Pl077_T360_Tt500, with efficiency 0.149 and a payout of 60.9 M$. That is far below layout 2 (148 M$) and Main TOPSIS #1 (172 M$). Layout 1 stays excluded, and neither ranking changes.

**S9, exchanger T-Q profiles (s9_tq_profiles/).** Every exchanger of the named designs was plotted at 100 slices, with the pinch marked. Each cooler meets its 5 K pinch internally, where the CO2 crosses its pseudo-critical region (x = 0.22–0.37 of duty from the cold end). The layout 6 PC1 cooler is the exception: its pinch is at the hot end.

Recuperator pinches:

- Reference: 26.8 K.
- Main TOPSIS #1: HTR 16.2 K, LTR 10.5 K.
- Strict TOPSIS #1: HTR 19.7 K, LTR 20.2 K, with the LTR pinch at its hot end.
- Highest payout: LTR 10.4 K at the cold end.

All recuperator pinches are well above the 5 K limit. This is a diagnostic only, so there is no ranking result.

**Summary across studies.** The strict recommendation stays in layout 3, with T_in 32.5–33 C and x 0.42–0.47, in every study, including S3 with M0 held fixed. (An earlier S3 run that recalibrated M0 flipped strict TOPSIS #1 to layout 2. That was an artefact of the recalibration, now removed.) In S1 at 8 K the 32.5 C designs become infeasible and the winner moves to T_in 33 C. The main recommendation stays in layout 6 except when exchangers are cheap (S4 ratio ≥ 4) or the cooler pinch is 3 K (S1), where it moves to layout 3. S2 cuts the other way: layout 6 holds its efficiency far better if T_in drifts above design.
