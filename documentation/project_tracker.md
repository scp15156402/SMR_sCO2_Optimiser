# Project tracker

Two parts, with different rules.

**Current status**, immediately below, is rewritten every session to reflect
where things actually stand. It is the only part that gets edited.

**The log**, everything after it, is append-only. Never rewrite history,
including entries about work that was later reverted -- the reasoning that
led to a dead end is the most useful thing in here, and deleting it means
re-walking it. Times are IST.

---

# Current status

*Last updated 2026-11-09, 19:40.*

Statuses: **NOT STARTED** / **IN PROGRESS** / **COMPLETE** (built and
runs) / **VERIFIED** (evidence exists and is named) / **BLOCKED**.
Nothing is marked VERIFIED without evidence recorded in
`documentation/registers.md`.

## The recommendation

**Recompression, 20 MPa, x = 0.25, 35 degC compressor inlet.**

| | |
|---|---|
| thermal efficiency | 41.41 % |
| second-law efficiency | 0.684 |
| PCS mass / volume | 87.0 t / 174 m3 |
| specific power | 0.476 MWe/t |
| inlet margin | 4.02 K, 0.32 MPa above critical |
| recuperator pinch | 5.00 K |
| payback vs best feasible recuperated | 2.3 yr |

43 candidates, 36 feasible under the strict inlet reading, 5
non-dominated. Verified unchanged at 25, 100 and 400-node exchanger
resolution.

## Software

| Item | Status | Evidence |
|---|---|---|
| `cycles/` generic solver | **VERIFIED** | air-standard closed form 4.6e-16; no project import; live code free of CO2 |
| `brayton_cycle/` 5 layouts | **VERIFIED** | all solve; wiring only, no numbers |
| `project/cases/` 17 cases | **VERIFIED** | regression baseline committed |
| `project/assessment/` | **COMPLETE** | mass, cost, metrics, MOO. Models themselves unvalidated by nature |
| `project/studies/` 9 + 3 diagnostics | **VERIFIED** | all execute; 9 save with manifests |
| `tools/` 5 generators | **VERIFIED** | figures, tables, registers, architecture, consistency |
| `tests/` 41 checks | **VERIFIED** | all pass |
| `results/` | **COMPLETE** | 9 studies, CSV + manifest each |

## Studies

| Study | Status | Note |
|---|---|---|
| Layout comparison | **VERIFIED** | four layouts at common 5 K pinch |
| Parameter sweeps | **VERIFIED** | pressure and split |
| Partial cooling exhaust pressure | **VERIFIED** | 6.0 MPa interior optimum; 2 points fail physically |
| Intercooling intermediate pressure | **VERIFIED** | monotone to the no-intercooler limit |
| Cooling | **VERIFIED** | pinch floor reproduces T_out - T_water exactly |
| Exergy | **TESTED** | 16 checks; no external reference |
| Multi-objective | **VERIFIED** | 43 candidates, filter returns its rejects |
| Selected design | **VERIFIED** | rebuilt from the knee row; efficiency reproduced |
| Tolerance sensitivity | **VERIFIED** | 9.6e-6 points; knee stable across resolutions |

## Documentation

| Item | Status | Note |
|---|---|---|
| `theory_and_implementation.pdf` | **COMPLETE** | 96 pp, 0 undefined refs, worked numbers restored with provenance |
| `reports/final_report.pdf` | **COMPLETE** | 16 pp, 0 undefined refs, all tables generated |
| Document split | **COMPLETE** | `migration_table.md` is the plan of record |
| Appendix A | **VERIFIED** | generated; every hand-typed row compared |
| `README.md` | **COMPLETE** | current |
| `architecture.md` | **COMPLETE** | generated |
| `usage.md` | **COMPLETE** | master sequence added |
| `registers.md` | **COMPLETE** | generated: study, validation, traceability |
| Decision record | **COMPLETE** | the log below; deliberately not duplicated |
| Numerical consistency | **VERIFIED** | 29 claims checked; prose scanned |

## Validation, honestly

Externally **validated**: solver numerics (closed form), CO2 properties
(Dostal), whole cycle (Kim 2018, including his optimum found
independently in two directions).

**Verified**: energy closure, discretisation, numerical settings,
document numbers.

**Tested**: exergy, case regression, table generation.

**Unvalidated**: mass, cost, design selection. These are the brief's
illustrative coefficients applied consistently, and nothing external
exists to check them against. **The recommendation rests partly on
them**, and both documents say so.

## Open

| Item | Status | Owner |
|---|---|---|
| 7.7 MPa inlet reading: literal or by intent? | **BLOCKED** | course staff. Changes the recommendation: the literal reading excludes the partial-cooling family on a pressure limit, not on performance |
| Joint sweep of partial cooling exhaust pressure and split | NOT STARTED | optional; one-at-a-time sweeps done |
| Off-design and part-load | NOT STARTED | out of scope; stated as a limitation |
| Git history | NOT STARTED | no repository has ever existed; manifests carry a source fingerprint instead |

## Not modelled

Off-design and part-load; turbomachinery mass scaling with flow;
heat-source boundary temperature (so exergy totals exclude the heater);
geometry-derived pressure drops; operating-point-dependent component
efficiencies; fuel, O&M, financing and civil works in the cost proxy.

# Log

## 2026-10-31

### 16:34 -- Project brief introduced
Shared the ME 306 problem statement (sCO2 Brayton for a compact SMR).
Walked through what the project is: optimise a power-conversion cycle using
pressure ratio, regeneration and intercooling, then recommend one
configuration justified on performance, cost, environment and safety.

### 16:45 -- Prior work established
Shared the ME 623 Joule-Thomson cryocooler report (Zhang & Dang
reproduction). **Decided** to reuse its machinery as the mental model:
enthalpy-based heat exchanger effectiveness with warm-end/cold-end limits,
internal pinch checks, CoolProp properties, parametric sweeps.

### 16:49 -- Formula sheet mapped
Shared the Brayton formula sheet. **Agreed** what carries over (work and
efficiency definitions, isentropic efficiency) and what does not (the `pr`
column and cold-air relations, both invalid near the critical point).

### 16:54-17:21 -- Working style corrected (three rounds)
Explicit feedback from the user, each applied immediately:
1. **Teach from the origin and discuss** -- the goal is to learn and
   contribute, not to receive finished output.
2. **Do not quiz.** Pose "why" questions as hooks but answer them in the
   same reply; time is short.
3. **Calibrate to his level.** He has the real-fluid background; skip the
   basics, keep important-but-simple points to a line.

All three were saved to a skill so they persist across sessions.

### 17:21-17:54 -- Mathematical breakdown
Built the layered model: properties -> components -> cycle closure ->
recuperator internals -> plant sizing -> evaluation -> optimisation.
**Decided** the compression and expansion branches are independent because
the turbine inlet temperature is fixed, so a recuperated cycle solves in one
explicit pass. (This later became a 33x speedup in code.)

### 17:38 -- Two kinds of input named
**Agreed** the distinction: *specification parameters* (the requirement:
power, temperature caps, efficiencies) versus *design variables* (what the
optimiser turns). Objective identified as eta_th, the analogue of q_C in the
JT project.

### 17:43-17:49 -- Two-model structure agreed
**Decided:** Model 1 is pure thermodynamics; Model 2 multiplies its physical
outputs (UA, powers, duties) by cost coefficients. The link is strictly
one-way -- a cost coefficient can never change a state. Also established
that maximising efficiency alone has no finite answer without physical
limits, because UA diverges as effectiveness approaches 1.

### 19:02 -- Turbine staging and Rankine analogies
**Decided against** reheat: small gain for sCO2 (the turbine pressure ratio
is low), and it needs a second high-temperature reactor pass. Clarified why
Brayton needs no turbine bleed: its exhaust is hotter than the compressor
discharge, so the whole stream can recuperate directly.

### 19:19-20:13 -- Recuperator theory in full
Derived `UA = integral dQ/dT` from `dQ = U dT dA`, showed the LMTD as its
constant-cp special case, and established the pinch as the consequence of
capacity-rate mismatch. **Agreed** that epsilon, pinch and UA are three
descriptions of one exchanger, and that **UA is the only physical one** --
which is why cost models must read UA, not epsilon.

### 20:06-20:09 -- Pressure drops
**Decided** to keep heat leaks neglected (the cycle moves hundreds of MW,
unlike the JT cooler) but to model pressure drops as parameters, because the
sCO2 pressure ratio is small so losses bite hard, and because pressure drop
is the hidden price of compactness.

---

## 2026-11-01

### 08:10-08:16 -- UA with variable cp, and what sets mdot
**Decided** the segment-LMTD sum over equal-duty nodes. **Agreed** mdot is
an output at design (`mdot = Q_th / q_in`), unlike the JT cooler where the
choked orifice forced it.

### 08:27-08:32 -- Architecture turn
User asked for blocks as composable functions. **Decided** on a block
library plus data-defined layouts. Established that Rankine and Brayton are
the same blocks, and that the `(P, h)` state choice is what makes that true.
**Decided** to design for Rankine but not build it -- add the throttle block
(trivial), defer two-phase specifics.

**Rule agreed:** if making something general costs under an hour and needs
no new validation, do it; otherwise leave a hook.

### 08:42-08:51 -- Literature reviewed
Read Dostal (MIT 2004), Chen (2023), Kim (2018), Wu (2020) in full.
**Key finding:** each paper fixes a *different* set of inputs for identical
physics -- Dostal effectiveness or volume, Kim effectiveness or pinch, Wu
UA, the brief effectiveness with a pinch constraint. **This decided the
architecture**: "what is fixed" had to be a runtime choice.

Also found: partial cooling is in the brief's scope; the brief's 5 K pinch
is a given constraint, not something to derive.

### 08:56-09:00 -- Two-stage split agreed
**Decided:** `cycles/` is the solver, everything else uses it as a black
box. One-way dependency.

### 11:22-11:45 -- Configuration format, three rounds
1. Proposed YAML layouts and cases.
2. User preferred JSON.
3. **User rejected both** -- a config DSL means writing a parser, a schema
   validator and a unit grammar, all of which Python already does better.
   **Decided:** Python data structures throughout, with `MPa(20)`-style unit
   helpers and `case.with_()` for variants.

Also **decided** the folder shape: one file per block, proper package
structure, no compaction. An earlier proposal to collapse the solver into
four files was rejected as unmaintainable.

### 11:45 -- Scope renamed
**Decided** the project is a *cycle block solver*; sCO2 is one case. Nothing
in `cycles/` may mention CO2 or Brayton.

### 12:06-13:58 -- First build
Built and committed 54 files to
`G:\My Drive\...\ME 306 - Adv Thermo\Project\Programming`.

Delivered: properties (CoolProp + ideal gas), 8 blocks, 6 physics helpers,
4 passes, Result, 4 layouts, 6 cases, 4 run scripts.

**Validation passed:** ideal-gas air Brayton against the formula sheet to
4.6e-16; energy closure 2e-14; node convergence 5.9e-5.

**Three performance decisions made during the build:**
- Added `fixed_outlets` to the heater (the "expansion branch is
  independent" insight from 17:21, made explicit in code). Dropped
  recompression from two tears to one: **11.6 s -> 0.35 s**.
- Skipped diagnostics during the tear loop.
- Warm-started secant for pinch/UA specs: **23 s -> 5.0 s**.

**One approach tried and rejected:** Wegstein acceleration on the tear.
Oscillated and stalled at residual 1.7e-4; the safeguarded version took 64
iterations against 29 for plain substitution. Removed, with the reason
written into `tear.py` so it is not re-attempted.

**One trap recorded:** nested tolerances must be ordered -- loosening the
inner heat exchanger tolerance stopped the outer tear converging at all.

### 15:36 -- Scope gap caught by the user
User challenged the claim that partial cooling, the water-side precooler and
the intermediate heat exchanger were all out of scope. **Re-read the brief:
the user was right on two of three.**

- Partial cooling: **required** (listed technique; R4 must decide on it).
- Water-side precooler: **required** (R4 sizes it against the 25 degC
  supply and reports cooling-water duty).
- Intermediate heat exchanger: correctly out of scope ("take the
  reactor-side heater as given", R1).

**Both gaps closed the same session.**

- Partial cooling cost **zero new solver code** -- 11 blocks, 14 streams,
  three pressure levels, pure wiring. First real confirmation that the
  architecture holds.
- The cooler gained an optional coolant side reusing the recuperator's
  limit, profile and sizing functions.

**Results that changed the picture.** At equal 5 K pinch, against the
recuperated baseline: recompression +5.71 points for 2.51x the conductance;
partial cooling +3.73 points for only **1.35x**. Partial cooling is more
UA-efficient, and its low-pressure level is still unoptimised -- so R4's
decision is live, not foregone.

**The precooler result is the more striking one.** 1610 kg/s of cooling
water for 32.7 MWe, and a precooler of 7191 kW/K against the recuperator's
1670 -- over four times larger. The pinch against the water sits *inside*
the exchanger (x = 0.32), caused by the same CO2 cp peak that pinches the
recuperator.

### 21:19 -- Documentation rules added
User added two standing rules:
1. **Always explain code logic and caveats when coding.** Building without
   discussion makes work pile up and loses the thread.
2. **Every substantial project gets a `documentation/` folder**: theory,
   caveats/choices/limitations, a usage README, and this tracker.

Both saved to the skill. This folder created in response.

---

### 21:30 -- Documentation restructured
User corrected the shape of the documentation:

- **Theory and caveats belong in one file**, because understanding the
  theory is what makes the caveats make sense. The two markdown files were
  merged.
- **That file should be LaTeX**, which allows far more descriptive
  presentation and is easier to read. The other two stay markdown.
- **It should include block diagrams** and schematics of layouts that the
  discussion keeps referring to.
- **Structure:** `documentation/latex/` holds the source; the compiled PDF
  sits outside it, beside `usage.md` and this tracker.
- **Keep it updated** as the project evolves.

Done. `theory_and_implementation.pdf`, 31 pages, 13 chapters, theory and
implementation interleaved with every caveat in a boxed environment stating
the choice and what it costs.

Five figures, all built from **solver output rather than sketches**:

| Figure | Shows |
|---|---|
| cp of CO2 along both recuperator isobars | the capacity-rate mismatch that causes the pinch |
| recuperated cycle block diagram | TikZ |
| recuperator T-Q profile | the real baseline profile at eps = 0.90 |
| UA and efficiency against effectiveness | the cost divergence, on twin axes |
| recompression and partial cooling block diagrams | TikZ, three pressure levels marked |
| precooler T-Q against cooling water | the internal pinch at x = 0.32 |

`project/runs/make_figures.py` regenerates the plot data, so a model change
followed by `make` shows real differences rather than stale pictures.

**Two build problems worth recording.** `microtype` font expansion needs a
scalable font, which the default CM bitmap fonts are not -- fixed with
`lmodern`. And both flow-splitting diagrams were cramped around the mixer on
the first attempt; redrawn with the cold and hot rows separated and the
split/mix nodes given clear space.

### 22:34 -- Code added to the theory document
User: the implementation sections do not make sense without the code, and
seeing the code alongside the equations makes both the physics and the
coding clearer. Requested in a chalk-green colour.

Added a `\codefile` environment (chalk green, RGB 47/102/78, with the source
path as a boxed title tab) and **14 code excerpts** placed directly beside
the equations they implement. Examples of the pairing:

| Equation | Listing beside it |
|---|---|
| $\eta_c$, $\eta_t$ definitions | `physics/isentropic.py` -- three lines, two blocks |
| $Q_{hot}$, $Q_{cold}$ limits | `physics/hx_limits.py` |
| $h_c(x)$, $h_h(x)$ node discretisation | `physics/hx_profile.py`, the loop itself |
| $UA = \int dQ/\Delta T$ | `physics/hx_sizing.py` |
| the three HX specifications | the dispatch in `heat_exchanger.py` |
| invertible pressure relations | `blocks/base.py` + the propagation loop |
| successive substitution | `passes/tear.py`, all eighteen lines |

**The excerpts are extracted from the source, never retyped.**
`project/runs/make_code_snippets.py` pulls named functions out with `ast`
(dropping their docstrings, since the surrounding prose already says it) and
slices fragments by marker strings. `build.py` runs it before compiling, so
a code change followed by a rebuild shows the change rather than a stale
listing.

Result: 38 pages, zero overfull lines.

Also replaced the `Makefile` with `build.py`: extensionless files are
blocked by the file-transfer tools, and `make` is not standard on Windows.

---

## 2026-11-03

### 14:17 -- Two-phase ambiguity in the duty limits: proposal, measurement, fix
User proposed adding temperature to the stream state, `(fluid, P, h, flow)
+ T`, to resolve the `h(P, T)` ambiguity flagged in the duty-limit caveat,
noting it would match the traditional way of writing a state table and
should be cheap.

**It does not fix that caveat, and it is not cheap.** Both were checked
rather than argued.

*Why it cannot fix it.* The ambiguous state is a **hypothetical one
belonging to no stream in the flowsheet** -- "what enthalpy *would* the hot
stream have if cooled to `T_cold_in`". The cold inlet's own temperature was
never in doubt: `T(P,h)` is single-valued in that direction. No field stored
on a `Stream` can answer a question about a state that does not exist.

*Why it costs.* Instrumented the backend and the `Stream` constructor:

| case | streams created | T_ph calls outside the profile loop | net |
|---|---|---|---|
| recuperated | 15 | 21 | -6 calls (small win) |
| recompression | 393 | 265 | **+128 calls** (19% more T_ph work) |

The tear loop builds and discards streams every iteration, and most are
never asked for a temperature. A lazy cache would be neutral but needs the
property backend on the stream, which makes `Stream` heavier and no longer
plain serialisable data. And the reporting benefit the idea was after
already exists: every stream in a `Result` carries P, T, h, s, rho and
flow, and `state_table()` prints them.

**The actual fix** is to stop asking the wrong question. The limits are not
after "the" enthalpy at (P, T) but the *extreme* enthalpy still satisfying a
temperature constraint, which is unambiguous even inside a dome:

- "cooled to T", so T_out >= T: below h_f the stream is subcooled and
  colder than T_sat, so the smallest admissible enthalpy is **h_f**.
- "heated to T", so T_out <= T: above h_g it is superheated and hotter than
  T_sat, so the largest admissible enthalpy is **h_g**.

Added `limiting_enthalpy()` in `physics/hx_limits.py`, plus
`has_saturation`, `T_sat` and `h_sat` on the backend interface (the ideal
gas raises, since it never condenses).

**Verified against water at 10 kPa**, a condenser pressure: a plain lookup
there has 2392 kJ/kg of candidate answers; the guard returns h_f = 191.8 for
"cooled to" and h_g = 2583.9 for "heated to", and is bit-identical to a
plain lookup 20 K either side of saturation.

**Every sCO2 number in the project is unchanged to the last digit**, because
`has_saturation` is False above the critical pressure so the guard never
even reaches its comparison. Timings unchanged. Air validation still
4.6e-16.

*What is still open.* Wherever a **user** specifies an outlet temperature --
a heater's `T_out`, a cooler's `T_out`, a boundary stream's `T` -- the same
ambiguity exists and no guard can fix it, because a condenser told "leave at
45.81 degC and 10 kPa" genuinely has not been told what state to leave in.
A Rankine condenser needs a *quality* specification, not a temperature. That
is one more option on an existing block, still unbuilt.

---

## 2026-11-03, 17:30 — Documentation rewritten as explanation, not as a list

*Why.* Feedback, and the strongest so far: *"I very much hate the way you
have written the documentation, cause nothing is being explained, its just
listed."* That was correct. The previous `theory_and_implementation.tex`
stated facts in sequence and left the reader to supply every connection
between them. Someone who already knew the material could recognise it;
nobody could learn it from the document, which is the only reason the
document exists.

*What changed in how I work.* Added a section to the `learn-first-engineering`
skill, placed above the existing rules because it is the one most often
broken:

> **Explain, never just list.** Write connected prose that builds an
> argument. A bullet list is a table of contents for an explanation, not the
> explanation. Test before sending: could a reader reconstruct the idea from
> what is written, or only recognise it?

*What changed in the document.* `theory_and_implementation.tex` rewritten
end to end, 39 pages to 43. The structure is similar; nearly every paragraph
is not. Specifically:

- **Every chapter now argues to its result rather than announcing it.**
  Chapter 2 does not state that CO2 has a low back-work ratio, it compares
  $v_1\Delta P$ against the solver's answer (0.4 % for sCO2, 2.8x too large
  for air) and lets the 498x specific-volume ratio explain why.
- **The capacity-rate idea is now taught before recompression needs it**,
  because recompression is incomprehensible without it and the old version
  assumed it.
- **Caveats explain their own consequence.** The sub-critical low-pressure
  side caveat now says *why* 6 MPa is safe (above 31 degC there is no
  saturation line at any pressure), then says what would make it unsafe and
  that nothing checks for it.
- **The two failed optimisations are written up as findings**, with the
  diagnosis, because the general lesson -- in nested iterations the inner
  tolerance must be tighter than the outer, and speed comes from better
  guesses not looser convergence -- cost two days and should not be relearnt.
- **The validation chapter now distinguishes what each check establishes.**
  The 4.6e-16 air result proves the algebra, and proves nothing about CO2.
  Said explicitly, because the opposite reading is the easy mistake.
- **"What is not modelled" is grouped by consequence** -- would change the
  answer / would change the number / known-small -- rather than listed flat.
  Cooling-water pumping power sits at the top with the note that it shifts
  the optimum pressure ratio, so any optimum reported here is wrong in a
  known direction.

*State.* Builds clean: 43 pages, zero overfull boxes, no undefined
references. All 18 code listings, 4 TikZ block diagrams, 3 pgfplots figures
and every caveat box preserved.

*Housekeeping closed.* `theory.md` and `caveats_and_limitations.md` have
been removed from the drive; the LaTeX document is now the only theory
document, as intended.

---

## 2026-11-03, 18:10 — Rewritten again, this time as a teaching document

*What happened.* Siddhant gave up on my 43-page rewrite partway through
Chapter 5 and went to ChatGPT, which explained the three heat-exchanger
specification modes successfully. He sent the transcript back with the
comment: *"When I say explain, I mean something like this. You just spend
too much effort in computing real figures and values and your theory
document, although complete, makes it very difficult to read."*

*The diagnosis, which was not what I assumed.* My previous correction had
been "stop listing, write prose". That was the wrong axis. The ChatGPT
explanation is **more** listy than my first draft — numbered steps,
comparison tables. The real difference:

- **I wrote conclusions; it wrote a path.** My entire treatment of the
  three modes was: *"effectiveness, pinch and UA each move monotonically
  with the others. Fix any one and the remaining two are determined."* True,
  and useless to anyone who doesn't already know it.
- **It ran the loop out loud.** Guess 0.70 → pinch 35 K → too low → guess
  0.85 → 12 K → bracketed. That is what made it land.
- **Its numbers were invented and round.** 500 and 350 kJ/kg, obviously
  fake, chosen so the `min()` is visible at a glance. Mine were real and
  verified — 601.7 kg/m3, Z = 0.222 — and every one of them *stops the
  reader*, because 5 significant figures signal "a result to check" rather
  than "a step to follow".

*Second clarification from him, which decided the structure.* **"We aren't
making a project report. We are making a theory documentation... it is just
so as after say 3 years I revisit this project I read the document and
revise everything."** That killed the two-document split I had proposed.
There is no grader; validation and timings are a regression reference, not
the point.

*The chapter template, taken from his own sentence* ("after that the
implementation and probably the code will become interesting cause now I
would know what's going on"):

> why the thing exists → how it works, built from the physical object →
> the numerical procedure walked out loud with invented numbers →
> the use cases → **then** the code → short caveats → what to remember

*Process.* Rewrote Chapter 5 alone first and sent it as a sample rather
than redoing 43 pages on a guess. He scored it 9.8/10 ("those 0.2 are cause
its looks AI, but you are an AI so fair enough"), so the rest followed that
shape.

*Result.* 43 pages to 55, with no new content — the growth is entirely
decompression. Specific changes:

- **Every real computed figure moved to Appendix A.** The teaching chapters
  now run on invented round numbers that stay consistent across the whole
  document: pressure span 12 MPa, w_c = 24, w_t = 144, w_net = 120 kJ/kg,
  BWR = 0.17; recuperator Q_h,lim = 500, Q_c,lim = 600, Q_max = 500.
- **Worked procedures everywhere.** The pinch-mode search, the tear loop
  (500 → 540 → 552 → 555.6, each gap 30 % of the last, so the contraction
  is *visible* rather than asserted), the three-slice UA integration where
  the pinched slice eats 43 % of the hardware for 33 % of the duty.
- **Capacity rate is now taught before recompression needs it**, with the
  balanced/unbalanced worked comparison. That was the biggest structural
  hole: recompression is unintelligible without it.
- **Code moved to the end of each chapter**, after the hand calculation it
  implements.
- **"What to remember" list closing every chapter** — 5 or 6 lines. This is
  the revision surface: read those, and if one doesn't ring a bell you know
  which section to reopen.
- Appendix B (validation) now states what each check establishes and,
  explicitly, that the 4.6e-16 air result proves the algebra and proves
  nothing about CO2.

*New standing rule, agreed:* **numbers that teach should be invented and
round; numbers that are real belong where results live.** Mixing them makes
the real ones look decorative and the teaching ones look unreliable. Plots
are the exception — a cp curve teaches *shape*, so real data is fine there.

*State.* Builds clean: 55 pages, zero overfull boxes, zero undefined
references. All code listings, 5 TikZ diagrams and 3 pgfplots figures kept.

---

## 2026-11-03, 18:40 — Partial cooling block diagram was wrong

*Caught by Siddhant*, who asked whether the figure was correct. It was not.

*The error.* The drawn figure ran the mixer straight into the heater. The
actual layout is `MIX -> s4 -> HTR cold_in`, `HTR cold_out -> s5 -> HEATER`,
so the mixer feeds the **cold side of the high-temperature recuperator**
first. As drawn, the HTR had a hot side and no cold side: the picture showed
a cycle with no high-temperature recuperation at all, which is strictly
worse than the one the numbers came from.

*Why it happened, which is the part worth remembering.* To keep the figure
legible I had collapsed `MC -> LTR cold -> MIX` into a single arrow
labelled "2 -> LTR cold", and said so in the caption. Once the cold path
stopped being drawn as a path, losing a whole exchanger side on it became
invisible. **An abbreviation in a schematic removes the very redundancy that
would have caught the mistake.** Draw every stream or don't draw the figure.

*Fix.* Redrawn with both recuperators showing both sides, all 14 streams
routed and numbered, using the same skeleton as the recompression figure so
the two can be compared directly. Verified stream by stream against
`project/layouts/partial_cooling.py`. New caption points at the one real
difference between the layouts (cool, pre-compress, then split) instead of
apologising for an abbreviation.

*Also checked:* `recompression.py` against Figure 6.1 — all 10 streams
correct, no equivalent error. Two stream labels nudged where they sat on
top of the recompressor riser in both figures.

*Numbers unaffected.* The solver always had the correct topology; only the
drawing was wrong. 56 pages, builds clean.

---

## 2026-11-03, 18:55 — Partial cooling: diagram right, attribution wrong

*Siddhant's challenge:* the partial cooling figure "is partial cooling +
recompression combined", and for a section that says Dostal found partial
cooling beats recompression, we should show just partial cooling.

*Checked against Dostal §5.3 (the PDF, not memory).* The challenge is
understandable and the literature is against it. Dostal, describing
Angelino's partial cooling cycle: *"only a fraction of the working fluid is
compressed in the low temperature (main) compressor... The rest is
compressed in the recompression compressor"*, and *"After leaving the
pre-compressing compressor the working fluid is split into two streams."*
He gives our own capacity-rate reason for it: the reduced flow on the HP
side of the LTR equalises the heat capacities so the pinch does not occur.

**The split IS partial cooling.** The name misleads: "partial" describes
the *flow* (only part of it is cooled to minimum temperature), not the
cooling arrangement. Further confirmation the layout file came from
Dostal's figure: he writes "the first part of the heat is rejected at much
lower temperatures (9 to 10) than the main portion (11 to 1)", and
`partial_cooling.py` has exactly `s9 -> PC1 -> s10` and `s11a -> PC2 -> s1`.

*But the challenge found a real error anyway, in the text.* I had written
"Dostal found partial cooling beats recompression below about 20 MPa and
loses above it." What Dostal actually reports (§5.6) is that recompression
is best around 20 MPa and at lower pressures the best is **partial cooling
with improved regeneration** -- a further variant with a *third* recuperator
carrying three streams and both precoolers merged into one three-stream
unit. I had attributed a more complex layout's result to the simpler one we
model. The *reason* Dostal gives (turbine exhaust pressure decoupled from
compressor inlet pressure) does carry over; the magnitude does not.

*Changes.*
- Figure kept as drawn -- it is correct and matches Angelino/Dostal.
- New §6.3.2 "The name is misleading, so read it carefully", with a table
  placing all five layouts by pressure levels / flow split / recuperators.
  Recompression and partial cooling differ in **exactly one column**, the
  number of pressure levels, which is why the low-pressure level is the only
  thing worth sweeping to tell them apart.
- Noted that the layout he was imagining -- three pressure levels, no split
  -- is a real cycle, the **pre-compression** cycle, but a different machine:
  its compressor sits between the recuperators with no cooler before it, so
  it works by raising T and cp mid-regeneration. Not implemented.
- New §6.3.4 stating what Dostal actually found, plus a caveat that nothing
  in Appendix A tests Angelino's crossover: that would need the third
  recuperator, a three-stream exchanger model the solver lacks, and a sweep
  over turbine inlet pressure.

57 pages, builds clean.

---

## 2026-11-03, 19:50 — Coolant side made a design variable; pumping power added

*From Siddhant's ChatGPT discussion of chapters 6 and 7.* Two requests:
make the coolant side accept a water flow directly rather than only a
temperature, and add cooling-water pumping power. Both done, with one
correction to the proposed physics.

### The correction: water-side dP must be absolute, not fractional

The suggested model was `dP = dp_w * P_water,in` -- the same fractional
convention the CO2 side uses. That is wrong for water, and wrong in a way
that would have quietly ruined the optimisation built on top of it.

A heat exchanger's hydraulic loss is set by dynamic pressure (rho V^2 / 2)
and geometry. It does not scale with the absolute operating pressure. Two
consequences of getting this wrong:

- **Magnitude.** 2 % of 2 bar is 4 kPa. A real water-side drop is 50-200
  kPa, so pumping power would have come out ~50x too small -- the
  discussion's own worked example gave "0.04 bar", which should have been
  the tell.
- **Direction, which is worse.** It hands an optimiser a lever that does
  not exist: lower the circuit's operating pressure and pumping power
  appears to fall. Pushed far enough it recommends running the cooling
  circuit near vacuum.

So `coolant_dP` is in **pascals**, and `coolant_P` (operating pressure) is
a separate input. They are separate physical quantities and conflating
them is the easy mistake.

### Second correction: the drop must scale with flow

A *fixed* dP makes pump work linear in flow. Darcy-Weisbach at roughly
constant friction factor gives dP ~ mdot^2, hence **W_pump ~ mdot^3**.
Cubic, not linear. The discussion recommended implementing a fixed
fractional drop but then illustrated the trade with a curve rising as
roughly mdot^2.5 -- the recommendation and the illustration contradicted
each other, and only the latter was right.

Implemented both: `coolant_dP` alone is constant, `coolant_dP` +
`coolant_dP_at` scales quadratically anchored at a reference flow. At 2732
kg/s the two models differ by a factor of ~3 (365 kW vs 1052 kW).

### The finding that came out of it

Sweeping water flow with pump work counted gives a result worth having:
**net-of-pump efficiency rises monotonically as water flow falls.** There
is no efficiency optimum. Pump work appears in efficiency; the exchanger
does not. Conductance is hardware and hardware is invisible to a first-law
efficiency.

An optimum only exists once conductance is priced, J = eta_net - lambda*UA,
and the best flow moves from 1024 to 1878 kg/s as lambda goes 2e-5 -> 5e-4.
At lambda = 2e-4 it lands on 1610 kg/s, which is the 10 K water rise the
chapter already recommended on entirely different grounds.

This is the same lesson as the layout comparison, reached from a different
direction, and it is now stated in both places.

### Third counter, on chapter 6

The discussion concluded "if you sweep for maximum efficiency you won't
prefer partial cooling". **Not established.** Partial cooling's
low-pressure level is fixed at an arbitrary 6 MPa and has never been
swept -- and it is that layout's *only* extra degree of freedom. Comparing
a tuned recompression against an untuned partial cooling and concluding
recompression is more efficient is not a result. The conductance comparison
is sound; the efficiency comparison is provisional. Said so in a caveat.

### Code

- `cycles/blocks/cooler.py`: new `coolant_flow` spec alongside T_out / dT /
  pinch, all four now reducing to a flow; `_water_pressure_drop()`;
  water-side inlet and outlet pressures passed into the profile (previously
  both were P_c, i.e. zero drop); pump work reported as `pump_w_total`.
- `cycles/solve.py`: `w_pump`, `W_pump`, `eta_net_of_pump`,
  `w_net_of_pump`. Pump work is kept *out* of `w_net` and `eta_th` so those
  stay comparable with textbook figures.
- `project/cases/pdf_watercooled.py`: `PUMPED` circuit at 6 bar (the old
  2 bar default is too low once 100 kPa of loss is modelled), plus
  `baseline_pumped` and `baseline_pumped_flow`.
- `project/runs/precooler_pump.py`: the sweep, run both ways, with the
  priced objective.

*Regression:* air validation still 4.61e-16; the three layout figures
(36.541 / 42.248 / 40.275 %) unchanged; baseline water flow still
1609.7 kg/s and pinch 5.50 K.

### Document

Chapter 6 gains §6.4 "Choosing between them, and why the rule matters more
than the answer": what recompression leaves undone (no control over where
heat is rejected), the two optimisation objectives, J = eta - lambda*UA,
and the caveat above. Chapter 7 gains §7.3 "What the water costs to move"
with the absolute-vs-fractional argument, the cubic scaling, both sweeps,
and the priced-objective table. Appendix A gains the pump sweep. 61 pages.

---

## 2026-11-03, 21:00 — Coolant hydraulics made pluggable

*Request:* one model selector for the water-side pressure drop, with four
models (fixed, quadratic, Darcy-Weisbach, custom), all returning Pa, and the
precooler never learning which produced it. Built. Three counters.

### Counter 1 (architecture): dataclasses, not a class hierarchy

The suggestion was a `CoolantHydraulics` base class with `pressure_drop()`
overridden per model. That would be the only class hierarchy in the project.
Everything here is either a module of plain functions (blocks) or an inert
frozen dataclass dispatched by type (`Effectiveness`, `Pinch`, `UAperFlow`).
Built the hydraulic models the same way, in
`cycles/physics/hydraulics.py`. Same extensibility, no new idiom.

### Counter 2 (physics): Darcy-Weisbach needs geometry we do not have

Chapter 9 is explicit that UA is computed and U is not, so the exchanger has
**no geometry anywhere in this program**. Giving `DarcyWeisbach` a channel
diameter and count invents a geometry for the *hydraulic* calculation that
the *thermal* calculation knows nothing about. The two can contradict each
other silently -- you can specify a channel count that could not deliver the
UA reported in the same table.

Mitigated, not solved: the solver flags a channel velocity outside
0.3-6 m/s. Documented as "the pressure drop of *a* exchanger with this
geometry", never "*the* exchanger whose UA is in the same table".

### Counter 3 (honesty): the friction factor breaks at the transition

64/Re below Re=2300, Haaland above, and the two do not meet. The sweep
crosses that step between 1024 and 1195 kg/s, where dP more than doubles for
a 17 % rise in flow. That is an artefact of stitching two correlations
together, not physics. Water channels in a compact exchanger sit right in
that band -- the baseline geometry gives Re = 3214 -- so it is not a remote
corner case. Runs with 2000 < Re < 4000 are now flagged.

Also noted: `CustomDrop` takes a callable, so a case using one cannot be
written into a results table or compared across sessions. Worth having,
worth labelling.

### Architectural consequence: hydraulics moved out of the block

A pressure drop needs *absolute* flow in kg/s. Absolute flows need mdot,
which needs q_in, which needs every block evaluated. So hydraulics cannot
run inside the cooler and now run in `solve.py` after the solve, where mdot
exists. The block reports the water flow as a fraction plus density and
viscosity; the solver does the rest.

Consequence owned in the document: the water-side pressure is held constant
when the *thermal* profile is built, unlike the CO2 side. Liquid water's h
and rho barely move over a few hundred kPa, so the profile is unchanged to
~1e-6, whereas on the CO2 side the same drop shifts cp and moves the pinch.

### The result worth having

Same cycle, same flow (1610 kg/s), three models: 202 kW, 202 kW, 58 kW. A
round-number assumption and a geometry calculation disagree by a factor of
four. All three have the same *shape* (rising faster than flow), which is
why the conclusions survive the choice of model even though the magnitudes
do not.

### Changed

- `cycles/physics/hydraulics.py` (new): FixedDrop, QuadraticDrop,
  DarcyWeisbach, CustomDrop, `friction_factor` (Haaland + laminar),
  `pressure_drop`, `pump_power`.
- `cycles/properties/`: `mu_ph` added to the Backend protocol and CoolProp;
  the ideal gas raises, as it does for saturation.
- `cycles/blocks/cooler.py`: hydraulics removed; reports coolant rho, mu and
  the chosen model instead.
- `cycles/solve.py`: post-solve hydraulics, velocity and Reynolds flags.
- `cycles/__init__.py`: the four models exported alongside the HX specs.
- `project/cases/pdf_watercooled.py`: PUMPED / PUMPED_FIXED /
  PUMPED_GEOMETRY and three cases. Pump efficiency now 0.80.
- `project/runs/precooler_pump.py`: sweeps all three models.

*Regression:* air validation 4.61e-16; layouts 36.541 / 42.248 / 40.275 %;
baseline water 1609.7 kg/s, pinch 5.50 K. 63 pages, builds clean.

---

## 2026-11-03, 21:10 — Pumping power removed; mdot vs UA kept  [reverts 21:00]

*Siddhant's call:* "let's just model mdot vs UA. Let the user define mdot.
Let's skip the pump part completely, too much ambiguity and effort and adds
pointless complexity."

Right call, and the reason is the one that came out of building it: an
honest dP needs the exchanger's channel geometry, and this project never
computes geometry. A Darcy-Weisbach number would have been using a geometry
with no connection to the UA printed beside it, with nothing to catch the
contradiction. A plausible number is worse than no number, because it gets
quoted.

### Removed

- `cycles/physics/hydraulics.py` (FixedDrop, QuadraticDrop, DarcyWeisbach,
  CustomDrop, friction_factor, pressure_drop, pump_power)
- `mu_ph` from the Backend protocol and CoolProp; the Backend is back to
  seven functions, as its docstring says
- the post-solve hydraulics pass in `solve.py`, plus `w_pump`, `W_pump`,
  `eta_net_of_pump`, `w_net_of_pump`
- `coolant_rho`, `coolant_mu`, `hydraulics`, `pump_eta` from the cooler's
  extras
- the pumped cases and `project/runs/precooler_pump.py`
- document section 7.3 on pumping, plus the DW-geometry, Re-transition and
  custom-correlation caveats

### Kept

`coolant_flow` as a fourth spec. It is what makes the sweep possible --
the other three specs each answer "what water do I need to achieve this?",
only the flow spec answers "what do I get for this much water?". New
`project/runs/precooler_sweep.py`.

### What the sweep found, which justified keeping it

Sweeping water flow at the baseline turns up something the temperature-rise
table hid. The pinch sits **inside** the exchanger, around x = 0.3, and
widens as water is added -- until about 3400 kg/s, where it jumps to x = 0
and sticks at **exactly 7.00 K**. That is 32 degC CO2 outlet minus 25 degC
water inlet: the gap between the two terminal temperatures. Past that point
more water buys nothing at all, because the approach is capped by where the
streams start and finish rather than by the flow.

So the usable band has a hard edge above (~3000 kg/s, no further benefit)
and a practical one below (~1000 kg/s, pinch too tight to build).

Also stated explicitly, because the opposite is the natural assumption:
**water flow does not change eta_th.** It is 32.720 % in every row. The
cycle is solved to a CO2 outlet temperature the case fixed, so the water
side decides what the heat sink costs, not what the cycle makes. The link
back to efficiency runs the other way -- if the water could not reach
32 degC at any sane size, the compressor inlet would have to rise, and
*that* would cost efficiency.

The pumping caveat in chapter 7 now says why it is absent rather than
promising it later, and chapter 12 matches.

*One orphan caught on review.* Chapter 6's J = eta - lambda*UA passage
ended with "Chapter 7 runs exactly this argument on a smaller problem",
which stopped being true the moment the lambda table was deleted. Reworded:
chapter 7 now shows the same asymmetry in a *starker* form -- water flow
changes exchanger size by a factor of two and changes efficiency not at
all, so efficiency cannot pick a water flow even in principle. Also noted
that the layout-level lambda sweep has not been run and is R4's job.

*Regression:* air 4.61e-16; layouts 36.541 / 42.248 / 40.275 %; baseline
water 1609.7 kg/s, pinch 5.50 K; the dT table unchanged. 59 pages, clean.

---

## 2026-11-03, 22:00 — Intercooling tested, and it loses

*Siddhant:* "one thing which we didnt cover was intercooling for
compressors. Should we? Also it would have the same UA vs mdot caveat,
right?"

Yes to both, and the first one turned into a useful negative result.

### The result

Sized to the same 5 K pinch as everything else:

| layout | eta_th | BWR | sum UA | vs baseline |
|---|---|---|---|---|
| recuperated | 36.541 % | 0.1764 | 3967 | -- |
| **intercooled** | **36.244 %** | 0.1595 | 4873 | **-0.30 pts, 1.23x UA** |
| recompression | 42.248 % | 0.2676 | 9936 | +5.71 pts, 2.51x UA |
| partial cooling | 40.275 % | 0.2750 | 5356 | +3.73 pts, 1.35x UA |

Intercooling is the only layout that goes **backwards**. A quarter more
exchanger for less efficiency than doing nothing. Swept over intermediate
pressure 10-18 MPa; best point is the lowest one tried and still loses.
12.41 MPa (the ideal-gas geometric mean) is not the optimum here.

### Why, and it is the point of the whole project

Two effects, and they do not cancel.

**The saving is real but small.** BWR does fall, 0.176 -> 0.160, so the
compressor genuinely is cheaper. But a gas turbine spends ~50 % of turbine
output on compression and this cycle spends ~18 %, because near-critical CO2
is nearly incompressible. Cutting an already-small number by a tenth leaves
you ~2 % of turbine output better off.

**The loss is bigger.** The intercooler rejects 24-57 kJ/kg at a temperature
*above the compressor inlet* -- heat the recuperator could have recovered.
It leaves the cycle and the reactor must resupply it. q_in rises 292.8 ->
~300 kJ/kg, and a rising denominator beats a rising numerator.

So: **intercooling helps a cycle whose compression is expensive, and the
entire premise of sCO2 is that its compression is cheap.** The feature that
makes the cycle worth building is the feature that makes this improvement
pointless. Good sentence for the report.

### Answer to the second question: yes, same caveat, and it is the dull half

The intercooler is specified by its CO2 outlet temperature exactly like the
precooler, so everything in 7.3 applies unchanged: water flow trades against
intercooler UA with zero effect on efficiency.

Its outlet temperature is not really free either -- lower is always better
for compression work, so you take it as low as the 25 degC cooling water
allows, which is the same 32 degC the precooler sits at. **The only
genuinely free variable intercooling adds is the intermediate pressure**,
which is a cycle variable, and the sweep is over exactly that.

### Changed

- `project/cases/pdf_intercooled.py` (new): `intercooled_case()` factory,
  `pdf_intercooled` (10 MPa, 5 K pinch) and `pdf_intercooled_geometric`.
  Registered in `project/cases/__init__.py`, as was the previously
  unregistered `baseline_watercooled_flow`.
- `project/runs/compare_layouts.py`: fourth row plus the explanation.
- Document: new section 6.4 "Intercooling, and why it loses", with the
  mechanism, the caveat about intercooling *with* recompression (untested),
  and the water-side caveat above. Layout family table gains a row.
  Appendix A gains the comparison row and the P_mid sweep. The open question
  "is intercooling in scope?" is now answered and replaced with the narrower
  one about combining it with recompression.

*Note on the API:* my first attempt built the case with
`pdf_baseline.with_(layout=intercooled, ...)` and the Case validator caught
it -- `with_` deep-merges, so the baseline's COMP block came along into a
layout that has no COMP, and it raised at construction rather than
producing a wrong answer. The frozen-dataclass-with-validation choice from
chapter 10 paying for itself.

*Regression:* all 6 runs OK; 13 registered cases all solve; air 4.61e-16;
other three layouts unchanged. 60 pages, builds clean.

---

## 2026-11-03, 22:25 — Architecture pass: coolant unified, pump work restored, document restructured

*Siddhant:* add intercooling and its implementation, make the recuperator
and water-flow machinery genuinely reusable, bring back pump work "since it
is being used so many times", keep block-reusability, and "see if you want
to change the folder structure or the documentation structure, cause else it
will be difficult to make any big changes from now on."

### What was actually wrong

Only one structural defect, and it was not the folder layout. The coolant
side lived as a private function inside `cooler.py` and reimplemented a
*second* spec system (`coolant_T_out` / `coolant_dT` / `coolant_pinch` /
`coolant_flow`) paralleling the exchanger's Effectiveness / Pinch /
UAperFlow. Two spec systems for one physics. That is what would have hurt,
and partial cooling already had two coolers.

The second signal was the document: I had put intercooling in "Splitting the
flow", which it does not do. Chapter boundaries were tangling components
with layouts.

The folders themselves are fine. `cycles/{blocks,physics,passes,properties,
numerics}` + `project/{layouts,cases,runs}` handles everything added so far
without strain, so no churn there.

### Code

- `cycles/specs.py`: `CoolantFlow`, `CoolantOutlet`, `CoolantRise`,
  `CoolantPinch` as frozen specs beside the HX ones. Same idiom, same
  collapse-to-one-primitive pattern.
- `cycles/physics/coolant.py` (new): the sizing, *below* the blocks because
  every cooler wants it. Reuses hx_profile and hx_sizing unchanged.
- `cycles/blocks/cooler.py`: now thin. Calls `coolant.size()` when a spec is
  present.
- `cycles/physics/hydraulics.py` (restored, trimmed): `NoPumping`,
  `FixedDrop`, `QuadraticDrop`. **DarcyWeisbach deliberately not restored.**
- `cycles/solve.py`: pump work summed across all coolers as an auxiliary
  load; `eta_net_of_pump`. It stays out of `eta_th`.
- `project/cases/pdf_watercooled.py`: rewritten. Cooled cases for all four
  layouts, including both coolers of partial cooling and of the intercooled
  layout.
- `project/runs/cooling.py` (new, replaces precooler_sweep): every cooler of
  every layout, the totals table, and the water sweep.

### The principle that settled the pump question

**The solver applies a pressure drop you state; it never manufactures one.**

My earlier reason for cutting pump work was right about DarcyWeisbach and
too broad. A geometry-based drop is dishonest *here* because this project
computes UA and never computes geometry, so the geometry fed to it has no
connection to the UA reported beside it. A stated drop in pascals is not
dishonest -- it is an assumption, declared. Fixed and quadratic come back;
geometry stays out. Written into the module docstring so it does not get
re-litigated.

### The finding, and it is the biggest of the project so far

Counting coolers reverses the hardware comparison.

| layout | eta_th | recup | coolers | total | vs base |
|---|---|---|---|---|---|
| recuperated | 36.541 % | 3967 | 8419 | 12386 | 1.00 |
| intercooled | 36.244 % | 4873 | 10758 | 15632 | 1.26 |
| recompression | 42.248 % | 9936 | 7662 | 17598 | **1.42** |
| partial cooling | 40.275 % | 5356 | 7909 | 13266 | **1.07** |

Recuperator-only, recompression is 2.51x the baseline hardware. **With
coolers counted it is 1.42x.** Partial cooling falls from 1.35x to 1.07x --
seven percent more exchanger for nearly four efficiency points.

Why: **recompression makes the precooler smaller.** It rejects less heat per
MW (Q_rej/W_net 1.37 vs 1.74) and the precooler carries only the unsplit
fraction. It needs the *least* cooling water of the four layouts, which the
efficiency table gives no hint of.

So every compactness statement made from recuperator conductance alone
overstates what the flow-splitting layouts cost, by roughly a factor of two.
That now appears in chapter 7, the appendix, and as a cross-reference from
compare_layouts.

Intercooling loses a second time here: most cooling conductance of the four,
on top of the worst efficiency.

### Document restructure

Chapters 6 and 7 swapped and rewritten:

- **Ch 6 "Rejecting heat"** (was "The precooler"): all coolers as one
  component class. Adds the four coolant specs, the cooler-block design and
  why the sizing sits below the blocks, the stated-not-derived principle,
  the circuit models, and the per-layout cooling table.
- **Ch 7 "The layouts"** (was "Splitting the flow"): capacity rate,
  recompression, partial cooling, intercooling, and choosing between them --
  now including the total-conductance correction.

Order is now physics -> components -> layouts -> solving -> results, and
"How to read this" says so. Appendix A reorganised to match. 66 pages,
builds clean, no undefined references.

*Regression:* all 7 runs OK; 16 registered cases all solve; air 4.61e-16;
layout efficiencies unchanged.


---

## 2026-11-03, 22:30 — Tracker given a live head

*Siddhant:* "just to make sure, you keeping track of the project_tracker.md,
right?"

Yes -- 13 entries, nothing lost, including the entries for work later
reverted. But checking turned up two real defects.

**The living sections were stranded.** "Open decisions" and "Next up" sat at
line 193 of 1004, written on 2026-11-01 and never updated, because every
session since appended *below* them. Anyone reading to the end saw the
history and never saw the stale status 800 lines up -- which still listed
intercooling as an open question after it had been answered, and knew
nothing about the cooling work or the total-conductance finding.

Fixed by splitting the file in two, with the contract stated at the top:

- **Current status** at the head, rewritten every session. The only part
  that gets edited.
- **Log** below, append-only, including dead ends. The reasoning that led
  somewhere wrong is the most useful thing in the file; deleting it means
  re-walking it.

**Timestamps had drifted into nonsense.** Today's entries ran "(later)",
"(later still)", "(evening)", "(night)", "(late)", "(late, reverted)", then
"(night)" and "(late)" *again* -- so the ordering was ambiguous by
inspection. Replaced with clock times. The 21:10 entry is now marked
"[reverts 21:00]" so the pair reads as what it was.

Content of the log entries is untouched; only the headings changed, which
makes the history more accurate rather than less.

*Rule for next time:* the status block gets rewritten at the end of every
session that changes what is true, not just when something is finished.

---

## 2026-11-03, 22:40 — usage.md brought current; the rule that let it drift strengthened

*Siddhant:* "I made you add in the skill that you update the documentation
folder files after every change, right... If there is no such rule, then
make one and follow it everytime next"

The rule existed and was too weak. It said *"create a documentation/ folder
and keep it current as the project grows"* -- a disposition, not a
checklist, with no trigger. So the two files I happened to be thinking about
stayed current and the third drifted for two days.

### What was stale in usage.md

Written 2026-11-01 and untouched since. It still:

- listed `precooler_sweep`, deleted hours earlier, and omitted `cooling`,
  `make_figures` and `make_code_snippets`
- said "all three layouts" when there are four
- documented the cooler as taking `coolant_T_out` / `coolant_dT` /
  `coolant_pinch` -- replaced by `coolant=CoolantRise(...)` spec objects
- knew nothing of the circuit models, pump work, `eta_net_of_pump`,
  `coolant_P` or `pump_eta`
- had no entry for the two new flags
- carried timings from before the coolant work

### What it now has

- a **repository map**, since none existed and the folder question came up
- every run script, including the documentation builders
- the four coolant specs with the "only CoolantFlow answers what a sweep
  asks" distinction
- the three circuit models, with the stated-never-derived principle quoted
  where someone configuring a case will actually read it
- both new flags and their fixes
- fresh timings with tear counts and iterations, plus the note that a
  coolant side costs ~0.1 s per cooler and runs only on the final pass

**Every code example in it was executed before saving.** All four coolant
specs, all three circuit models, every documented `r.blocks[...]` and
`r.metrics[...]` key asserted present. A README whose snippets no longer run
is worse than none, because it is trusted.

### Rule strengthened

The skill now has a **closing checklist to run after every change**, naming
all three files, because the failure was never intent -- it was that
"keep it current" has no moment at which it fires:

1. Theory document: does a chapter, caveat or appendix now say something
   false? Rebuild; check clean.
2. Usage README: did a script, option, spec, default or message change or
   get deleted? Re-run the examples.
3. Tracker: append a log entry *and* rewrite the status head.

Plus: deleting a section is the highest-risk edit, so check what
cross-referenced it. (That is the orphan caught at 22:30 generalised.)
And the tracker's two-part structure and clock-time rule are now written
into the skill rather than living only in this file.

usage.md: 8919 -> 13684 bytes.


---

## 2026-11-04, 08:05 — Exergy analysis: reviewed, gaps closed, documented

*Siddhant supplied a detailed 12-section spec* and asked for it implemented
throughout, with a chapter if one fits.

### Provenance, stated because it matters

A substantial exergy implementation **already existed in my container**
when I started -- `cycles/physics/exergy.py` plus edits to `solve.py`,
`case.py`, `result.py`, and new `runs/exergy.py` and
`runs/validate_exergy.py` -- all timestamped after my last commit the
previous night, and **not on the G: drive**. I did not write it and do not
know where it came from. I told Siddhant immediately and treated it as
unreviewed: checked against the spec line by line rather than trusted.

It turned out to be good. 16/16 of its own validation passed, including the
overall balance closing to 3.9e-8, and `eta_th` was bit-identical
(0.3271985366727382). But it had gaps against the spec.

### Gaps found and closed

| Spec | Gap | Fix |
|---|---|---|
| 3 | per-stream exergy not exposed | `exergy["streams"]`, and a column in `state_table()` |
| 3.2 | `specific()` recomputed h0,s0 on every call | `dead_state()` with `lru_cache` |
| 4.5 | heater always unavailable, no way to supply the boundary | optional `T_source` on the heater block |
| 7 | four-layout comparison had no cooler UA and no exergy | `compare_layouts` now carries both |
| 11 | no documentation at all | chapter 10, plus usage.md |

`Environment` was also not exported from `cycles` -- caught only because I
executed the usage.md examples rather than writing them from memory. That
is the second time that habit has paid this week.

### The T_source finding, which is the strongest thing here

The heater cannot be computed because the project has no heat-source model.
The spec was right to forbid substituting the CO2 outlet temperature. State
a source temperature and you see why:

| stated T_source | heater E_D | total |
|---|---|---|
| none | unavailable | incomplete (20.07 known) |
| 550 degC | 9.88 MW | 29.96 MW |
| 650 degC | 13.80 MW | 33.88 MW |

At 650 degC **the heater is the largest single irreversibility in the
plant**, bigger than the recuperator. So the component the model cannot
compute is quite possibly the worst one, and reporting zero for it would
have inverted the chapter's conclusion. 100 K of source temperature is 4 MW
of destruction -- which is exactly why it is not quietly defaulted.

Same rule as the circuit pressure drops: **stated, never invented.**

### The result worth having

| layout | eta_th | recuperators | turbine | coolers | total* |
|---|---|---|---|---|---|
| recuperated | 36.541 % | 12.29 | 2.23 | 2.00 | 17.29 |
| intercooled | 36.244 % | 13.12 | 2.17 | 1.34 | 17.34 |
| recompression | 42.248 % | 6.99 | 2.90 | 1.82 | 13.45 |
| partial cooling | 40.275 % | 7.09 | 2.92 | 1.97 | 13.75 |

*excluding the heater. MW.

**The recuperator is the biggest irreversibility in every layout** --
45-76 % of the accounted total, four to six times the turbine, from a
component with no moving parts. And it is the capacity-rate mismatch of
chapter 7 seen a second way: a temperature difference is what generates
entropy in an exchanger, and the mismatch is what makes it large where the
duty is.

So recompression cutting recuperator destruction 12.3 -> 7.0 MW *explains*
the efficiency ranking that chapter 7 derived from capacity rates. Two
independent routes to the same conclusion. Its compressors and turbine
destroy more; the recuperator saving swamps both.

Intercooling is the counter-example and consistent with 7.4: the only
layout whose recuperator destruction goes **up**.

### Documentation

New **chapter 10, "Exergy: where the losses actually are"** -- its own
chapter rather than a subtopic, because it needs the dead state, the
entropy tax, the component equations, the boundary problem and the balance
before any of it is usable. Covers every item in spec section 11. Stacked
bar chart from the real converged data. 73 pages.

usage.md gains an exergy section with the metrics, the Environment, the
T_source rule and the three new flags. All examples executed.

*Regression:* 8 runs OK; 16 cases solve; air 4.61e-16; eta_th
bit-identical; layout efficiencies and UA unchanged.


---

## 2026-11-04, 08:20 — Validated against published work. Part 1 closed.

*Siddhant:* "so do what you have to do, and tell me what i have to do"

The thing I had to do was the literature validation I had flagged as the
top priority six times. Done, and it passes.

### Three levels, deliberately

Reproducing one efficiency is weak evidence -- it can be hit by luck or by
tuning. So the checks sit at three separate levels:

**1. Properties alone**, against Dostal Table 10.2. No cycle, no solver,
just h and s at stated P and T. This is the level that catches a
transposed argument or a unit slip, and it is exactly what `validate_air`
cannot reach because air never touches the CO2 property path.

Enthalpy: worst error **0.002 %** over 8 states. Essentially exact.

Entropy: worst **0.388 %**, at three points. Investigated rather than
waved through, and **it is Dostal's table, not us**: recomputing s from his
*own* h gives the same answer as from his *own* T, and both differ from the
s he prints. His h, T and s are not mutually consistent at those three
points. Reported in the appendix rather than hidden, since every block
balance here is an enthalpy balance and those agree.

**2. One machine at a time.** Dostal prints both isentropic and actual
outlets, so the isentropic relation and the efficiency definition can be
checked in isolation:

| | Dostal | ours |
|---|---|---|
| compressor isentropic | 324.99 | 324.99 |
| compressor eta 0.89 | 327.26 | 327.26 |
| turbine isentropic | 901.03 | 901.04 |
| turbine eta 0.90 | 914.45 | 914.46 |

**3. A whole cycle**, Kim (2018) Table 1, recompression.

Definitions checked against ours *first*, because a matching number from
mismatched definitions is worse than no check: his sr sits on the
recompressor branch like our x (his eq. 6); his effectiveness is
enthalpy-based like ours (eq. 4); his LTR carries the same (1-sr) on the
cold-side limit (eq. 5); his cycle work weights each compressor by its own
flow (eq. 8).

| | Kim | ours |
|---|---|---|
| eta at his optimum | 44.67 % | **44.669 %** |
| optimum split ratio | 0.307 | **0.307** |
| optimum pressure ratio | 2.6 | **2.6** |

0.001 percentage points on the efficiency. But the stronger result is the
last two rows: sweeping independently in two directions, the solver puts
the optimum exactly where Kim puts it. One number can be luck; a response
surface agreeing in two directions cannot.

### Files

- `project/cases/literature.py` (new): Kim's case with the
  definition-matching reasoning written into the docstring, plus a
  `kim_case()` factory for sweeping.
- `project/runs/validate_literature.py` (new): the 9 checks.
- Appendix B rewritten: "The check that has not been run" is now "Against
  published work", with the Dostal table-inconsistency finding.
- Every caveat saying the CO2 numbers were unverified has been discharged
  and now points at the new section. Two mentions of "self-consistent"
  remain and both are correct: partial cooling and the intercooled layout
  genuinely have no published comparison.

**Part 1 is now closed.** The solver is built, documented and validated
against an independent author.

*Regression:* 17 cases solve; air 4.61e-16; eta_th bit-identical; 74 pages,
builds clean.

---

## 2026-11-04, 09:00 — The project's actual question, answered

*Siddhant, after asking for the brief to be explained section by section:*
"Proceed... I would like the project files, as in the helpers, etc to be
kept in some other folder so that it doesnt clutter or polute the already
made generic solver."

### Scope correction first

Stages are abandoned. They were introduced to get a reusable framework, but
reuse comes from the `cycles/` vs `project/` boundary, which is already
built and already proven three times. A schedule label does not enforce
anything; a folder boundary does.

New subpackage `project/assessment/`, a fourth kind of thing beside
layouts / cases / runs. It reads a `Result` and never reaches back. Every
number in it (2.5 kg per kW/K, $250/kg, $70/MWh, 60 t) is a brief
assumption, not physics, which is exactly why it cannot live in `cycles/`.

- `mass.py` -- UA to tonnes, volume at the brief's implied 0.5 t/m3
- `cost.py` -- hardware vs energy value, cost proxy, payback
- `metrics.py` -- second-law efficiency, compressor-inlet margins
- `moo.py` -- constraint filter, Pareto front, knee point
- `project/runs/tradeoff.py` -- the R5 run

### Three bugs caught while building, all mine

1. **rp sweep walked through the pressure limit.** 2.6 x 7.7 = 20.02 MPa,
   rejected for exceeding 20 by 0.02. Fixed by sweeping absolute P_high.
2. **Margin measured at the coldest stream, not the compressor inlet.**
   That gave partial cooling a *different* verdict depending on which
   stream happened to be coldest -- admitted at 32 degC, rejected at
   35 degC, for no physical reason. Now measured at every compressor inlet,
   which is what the brief's constraint is actually about.
3. **Payback compared against an arbitrary baseline** rather than the best
   feasible one.

### The ambiguity is now explicit and switchable

The brief: "Compressor inlet >= 32 degC and >= 7.7 MPa (safe distance from
two-phase region)". Partial cooling's pre-compressor sits at **6.00 MPa,
32 degC** -- below the pressure limit, but well above the critical
temperature so nowhere near the dome.

`strict_inlet_pressure=True` (default) rejects the whole partial cooling
family; `False` admits it. **It changes the answer**, so it needs settling
with the course staff. No longer a note in a caveat -- it is a flag in the
filter with both results printed.

### A real finding: the optimum compressor inlet is NOT at the critical point

Sweeping T1 at fixed 5 K pinch:

| T1 | eta | w_comp | q_in | UA |
|---|---|---|---|---|
| 32 C | 36.541 % | 20.5 | 262.2 | 3967 |
| 35 C | **37.355 %** | 33.4 | 222.0 | 4488 |
| 38 C | 37.103 % | 37.9 | 211.5 | 4934 |

Compression gets **63 % more expensive** going 32 -> 35 degC, and
efficiency still *rises*, because the reactor supplies **15 % less heat**:
a warmer cold inlet eases the capacity-rate mismatch, so recuperation
improves. Optimum near 35 degC, then it declines.

Counterintuitive and directly answers R4's "study how compressor inlet
temperature and pressure drive cycle efficiency". It also buys operating
margin for free -- 4.02 K instead of 1.02 K above critical -- which is MOO
objective 4. It costs 13 % more exchanger, which is why it sits on the
Pareto front rather than dominating.

### The result

43 candidates swept, 36 feasible (strict reading), 5 non-dominated:

| design | eta % | mass t | cost M$/yr | margin K | MWe/t |
|---|---|---|---|---|---|
| recompression 18 MPa x=0.35 35C | 42.82 | 103.7 | -20.12 | 4.02 | 0.413 |
| recompression 20 MPa x=0.30 35C | 42.47 | 95.0 | -20.02 | 4.02 | 0.447 |
| **recompression 20 MPa x=0.25 35C** | **41.41** | **87.0** | **-19.57** | **4.02** | **0.476** |
| recompression 20 MPa x=0.20 35C | 40.45 | 82.1 | -19.13 | 4.02 | 0.493 |
| recuperated 20 MPa 35C | 37.35 | 68.5 | -17.73 | 4.02 | 0.545 |

Knee point: **recompression, 20 MPa, x = 0.25, 35 degC inlet.** 41.41 %,
87.0 t, 0.476 MWe/t, 2.3 year payback against the best feasible baseline.

Stated in the output, because it is true: the knee weights all four
objectives equally, which nobody asked for. It is where the argument
starts.

### Deliverable plot data, all from converged runs

`ts_recompression.dat`, `eta_vs_rp.dat`, `eta_vs_x.dat`, `pareto.dat`
(43 designs tagged infeasible / dominated / front / knee).

### Still to do

The five plots as figures in the document, and the written justification.

## 2026-11-04 (continued)

### 08:45 -- Assessment package committed and verified
Committed `project/assessment/` (mass, cost, metrics, moo), `tradeoff.py`,
`make_figures.py`, both documentation markdown files and four plot data
files -- thirteen files -- then read every one back off the drive and
compared byte counts. All matched. This read-back is now routine after
three separate occasions where `device_commit_files` reported success and
left the old bytes in place.

### 08:50 -- Chapter 11, "Choosing one design"
Written and inserted after the exergy chapter. 632 lines, taking the
document from 74 to 85 pages. Structure: why a multi-objective problem has
no answer -> each objective and the proxy standing in for it -> the
constraint filter and its one ambiguity -> dominance -> the knee rule ->
what the sweep found -> the recommendation -> what would overturn it.

**Decided** to teach dominance with four invented round designs (A-D, 40 %
/100 t and so on) before showing the real 43-point cloud. The real cloud
cannot teach the idea, because in four dimensions you cannot see which
point dominates which.

Five code excerpts pulled from `project/assessment/` by
`make_code_snippets`, as usual: `compressor_inlets`, `feasible`,
`_dominates` + `pareto_front`, `knee`, plus `mass_of` and `payback_years`
registered for later use.

### 08:55 -- The specific-power trap, named
Added as a section of its own. MWe/t is the ratio of two objectives already
on the list, and because exchanger mass grows faster than efficiency, it is
maximised by the *least* efficient design on the front. Plotted twice on
purpose: the frontier slopes up against mass and down against specific
power, and a reader shown only the second would pick the simplest layout.
A derived ratio in an objective list is a double count wearing a disguise.

### 09:00 -- Four defects caught by looking at the rendered pages
Not by reading the source. Worth recording as a method:

1. **The T-s diagram was the wrong cycle.** It was built from the default
   recompression case (32 degC inlet, default split) while the caption said
   "the recommended cycle" (35 degC, x = 0.25, 20 MPa). The plot and the
   recommendation would have disagreed in print. Fixed by constructing the
   design explicitly in `deliverable_plots()`, with a comment saying the
   two must be edited together.
2. **The caption described the wrong leg as the precooler** -- called it a
   "short vertical drop" when it is the long bottom leg. Invisible until
   the figure was next to its own caption.
3. **Deictic references to floating figures.** "Two features of that plot"
   sat on a page where LaTeX had floated the plot elsewhere. Replaced with
   numbered references.
4. **A 2-D projection of a 4-D front looks like a bug.** Dominated crosses
   sit above frontier dots in the eta-mass plot, because those designs lose
   on cost or margin. Said so in the caption rather than leaving a reader
   to decide the code is wrong.

Also: the T-s plot had no state numbers at all, which makes a T-s diagram
nearly useless. Added by emitting a label column from `make_figures`, with
repeated states blanked so no number is printed twice.

### 09:05 -- siunitx
`\year` collides with a TeX primitive and `\USD` does not exist in
siunitx 3. Both were in the first draft and both killed the compile.
Replaced with plain text. Noted here only because the error message
(`Missing number, treated as zero`) points nowhere near the cause.

### 09:10 -- Documentation updated, all three files
Per the standing rule. `usage.md` gained the `assessment/` entry in the
tree and a table of every plot data file with the reason the Pareto data is
split four ways and the T-s data written twice. Tracker head rewritten,
housekeeping list checked against the drive and reduced from four stale
files to one.

**Where this leaves the project:** the analysis is done. The remaining
deliverable is the written justification, and Chapter 11 is its draft.

## 2026-11-06

### 15:50 -- architecture.md, generated rather than written
Asked for a folder tree with the functions in each file. **Decided** to
make it a script (`project.runs.make_architecture`) rather than a document,
because a tree typed by hand is wrong the first time a file is added, and a
wrong map is worse than no map -- it gets believed. Same reasoning that
already governs the extracted code snippets and the plot data: the
documentation folder should contain as little hand-maintained derived
content as possible.

Structure read three ways, for three reasons:

- **`ast`** for signatures, classes, dataclass fields and module-level
  constants. Parsing beats importing here: it cannot run anything, so a
  module with a side effect or a missing dependency still maps.
- **Importing** for the layout wiring and the case registry, because a
  layout is *built by running code* -- `LAYOUTS` and `CASES` do not exist
  in the syntax tree. If the import fails the section says so rather than
  vanishing.
- **Hand-written**, in a `PURPOSE` dict, for the one thing no parser can
  infer: why a directory exists. That is the only prose in the output.

Two things the first version got wrong, both caught by running it:

1. **It died on `documentation/latex/code/`.** Those files are *fragments*
   snipped out mid-class by `make_code_snippets`, so they do not parse as
   modules. Excluded by path, plus a `SyntaxError` guard so one bad file
   reports itself instead of costing the whole map.
2. **`air_brayton_real` looked like a bug** in the case table -- "real"
   paired with the ideal-gas backend. It is not: "real" means real
   *machines* (eta < 1), not a real fluid. Added a `backend` column and a
   note, because a map that invites a wrong conclusion has failed at the
   one job it has.

Output: 1234 lines. Tree with a one-line note per file, the layout and case
registries, then every module's full API.

### 17:05 -- Phase 4 started: Chapter 9, "The numerical methods"

Three long direction documents today settled the architecture. Both of my
standing objections withdrawn, one of them because I was wrong on a point
of fact and said so: I had argued Chapter 5 could not sit in Part I
because it carries 11 project-specific numbers. That conflates two rules.
The constraint that `cycles/` must not know about CO2 is a constraint on
the *code*; the *document* may teach the recuperator with sCO2 numbers,
and a worked example with real values teaches better than an abstract
one. The objection evaporated.

The genuine obstacle that remains is narrower: Chapter 8 motivates
tearing with recompression's loop, and recompression is Part II. Fix
agreed -- split at the seam, generic recycle in Part I, recompression
walkthrough in Part II. That is better than the current single chapter,
not a compromise.

Wrote Chapter 9 (438 lines, document 85 -> 93 pages). It fills the
largest documented gap: `roots.py` has four methods and the document
named two of them once each, never named `solve_monotone`,
`successive_substitution` or `ConvergenceError`, and said nothing at all
about what happens when convergence fails.

**The organising idea** is that there are only five kinds of problem in
the whole solver -- direct evaluation, property inversion, scalar
root-find, fixed point, scheduling -- and knowing which one you are
looking at tells you what it costs and how it can fail. Three
consequences fall out of that table: the expensive kinds are rare (a
recuperated cycle has no cycle-level search at all); property inversion
is everywhere and invisible, which makes carrying (P,h) a *numerical*
decision as much as a thermodynamic one; and there is exactly one true
fixed point in the program.

**Three things the chapter says that were only ever in code comments:**

- *Why Newton is deliberately absent.* The pinch can migrate from an end
  of the exchanger into the interior as effectiveness rises. The function
  stays continuous but its slope does not -- it has a kink. Bracketed
  methods do not care; derivative methods do. Smoothness of a
  thermodynamic function is a physical question, not a free assumption.
- *Why `clamp=True` is an engineering decision, not a numerical one.* A
  design asking for a pinch the exchanger cannot deliver returns the
  nearest endpoint flagged, rather than raising, because one impossible
  point must not kill a 10,000-point sweep. Same philosophy as
  `Result(ok=False)`.
- *Why the inner tolerance must be tighter than the outer.* If the
  exchanger resolves itself only to 1e-6, feeding it identical input
  twice returns answers differing by 1e-6, and the tear loop cannot tell
  that noise from real change. Its residual acquires a floor it can never
  get below, and a perfectly healthy cycle reports non-convergence. The
  fix is an ordering, not a number. This also explains why Wegstein
  failed: the inner loop's finite tolerance puts a discontinuity into the
  outer map and the extrapolation reads it as signal.

**Honest about what is not derived.** Three of the five tolerances are
conventional choices that proved adequate; only the exchanger's 1e-9 is
derived (one decade below the outer loop). Said so rather than inventing
a justification, and flagged the tolerance-sensitivity sweep as
outstanding.

Two labels added to existing sections (`sec:tearloop`, `sec:explicit`) so
the new chapter can reference them. Six code excerpts registered and
extracted. `usage.md` needed no change -- the snippet registry it does not
document is the only thing that moved.

**Blocked on the user for Phase 1:** Git does not exist and the G: drive
cannot be reached from a shell, so version control has to be set up on
Windows. PowerShell instructions given. No file moves until that lands,
per his own instruction.

### 23:10 -- Execution provenance: studies now save, figures now read

The user's objection, in his words: results were being incorporated into
documentation "without establishing an inspectable and reproducible
connection to the actual project source code and saved outputs." He is
right, and the precise shape of it was worth establishing rather than
conceding in general terms.

**What was actually true.** Chapter 12's five figures were plotted by
pgfplots from eight `.dat` files that physically existed, written by
`make_figures.py`, a permanent script. So the figures were traceable.
What was not: `tradeoff.py` printed and saved nothing, so the 31
hand-typed rows of Chapter 12 -- including the entire recommendation
table -- had no file behind them. They came out of a terminal and went
into LaTeX through me. Appendix A's 21 rows likewise.

**A near-miss worth recording.** Early in this work I ran a migration
command that copied `project/runs/*` over the already-migrated
`tools/` and `tests/`, silently reverting them, and then deleted
`project/runs/`. I noticed because directories contained files I had not
just created, stopped rather than guessing, and restored from the backup
zip taken minutes earlier. **The lesson is the one the user has been
making: establish state before acting on it.** The backup existed only
because his instruction said to make one.

**What now exists.**

`project/studies/_io.py` -- `save()` writes a study's tables as CSV plus
a `manifest.json` recording purpose, script, command, environment, the
grids actually swept, and a **source fingerprint**: a SHA-256 over every
`.py` in `cycles/`, `brayton_cycle/` and `project/`. Two runs agreeing on
that hash ran identical code. Deliberately not a fake commit hash -- there
is no repository yet, and when there is, the commit goes *alongside* the
fingerprint, which stays useful because it also catches uncommitted edits.

Five studies now save: `layout_comparison`, `parameter_sweeps`, `exergy`,
`multi_objective`, `selected_design`. 17 files under `results/`, plus a
README mapping study -> command -> output.

**The duplicate sweep is gone.** `make_figures` no longer solves anything.
It reads the CSVs and translates them into pgfplots tables. The pressure
and split sweeps moved into `project/studies/sweeps.py`, computed once.

**The drift is now structurally impossible.** `selected_design.py` reads
the knee row from `multi_objective/candidates.csv` -- the row the
trade-off study itself labelled -- and rebuilds that case through
`recompression_design()`, the same factory the sweep used. It then checks
the efficiency it gets back against the recorded one and fails loudly on
disagreement. The chosen design is defined in exactly one place.

That guard fired on its first run, on my own bug: I had set the tolerance
to 1e-6 while the CSV stores eta to four decimals, so two identical runs
can differ by 5e-5 from rounding alone. Raised to 1e-4 with the reasoning
written down -- a guard that cries wolf gets deleted, which is worse than
no guard.

**Verified:** 32 tests pass; document rebuilds at 93 pages with zero
undefined references; the Pareto figure and the recommendation table both
render from the same CSV; the knee row in `candidates.csv` matches the
printed table to every digit.

**Still to do, and not claimed as done:** the two-document split (§4 of
his direction) -- project results out of the technical document and into
a separate final report. Appendix A still hand-typed. `precooler_sweep.py`
and the now-obsolete `project/layouts/` and `project/runs/` still on the
drive: the shell cannot reach G:, so the user must delete those three.

## 2026-11-07

### Milestone 1 -- Phase 4.1 and Phase 3: the engineering gaps and Appendix A

Not committed to the drive piecemeal. The user asked for one complete
verified version rather than a stream of file corrections, so everything
below stays in the working copy until the Phase 6 release package.

**Partial cooling's third pressure level, swept at last.**
`project/studies/partial_cooling.py`. The turbine exhaust had been fixed
at 6.0 MPa for no better reason than that it is a round number, which
made every partial-cooling comparison provisional.

Result: **6.0 MPa was already the optimum** -- an interior one, 5.0 ->
6.0 -> 7.0 rises then falls. Luck, but now demonstrated rather than
assumed. Two points (7.4, 7.6 MPa) do not solve, and the reason is
physical rather than numerical: as the exhaust pressure approaches the
main compressor inlet the pre-compressor has almost no work to do, PC2's
duty collapses and the coolant profile crosses. Re-sweeping the split at
the best pressure gives 41.9 % at x = 0.40 against recompression's
44.9 % at the same split, so the layout ranking is unchanged -- but it is
now a swept comparison. **0 of 5 exhaust pressures** put the
pre-compressor inlet at or above 7.7 MPa, so the strict reading rejects
the family at any exhaust pressure, which is a stronger statement than
before.

**Intercooling's free pressure level.** `project/studies/intercooling.py`,
new -- Appendix A contained an intercooler pressure sweep with no study
behind it at all, run ad hoc at some point and never saved.

Two findings worth more than the table. First, **the pressure that
minimises compressor work is not the one that maximises efficiency**:
back-work ratio bottoms out at 10 MPa while efficiency is still
improving at 7.9. The recuperator penalty outruns the compression
saving, and it is the penalty that sets the optimum. Second, efficiency
rises monotonically as the intermediate pressure falls toward the
compressor inlet -- that is, as the intercooler is switched off. **There
is no interior optimum: the best intercooler for this cycle is no
intercooler.** The geometric-mean rule (12.41 MPa), which is an
ideal-gas result, is 0.23 points off the best point swept.

**Tolerance sensitivity.** `project/studies/tolerances.py`. Largest
efficiency deviation across every setting: **9.6e-6 points**, against a
1e-3 threshold for the fourth significant figure. Quoting 41.4097 % is
supported by the numerics.

Three things that came out of it and would not have come out of an
argument:

1. **A loose tear tolerance (1e-6) is rejected by the exergy balance, not
   the first-law closure.** The second-law check is the more sensitive
   convergence detector of the two.
2. **Efficiency and UA do not converge at the same rate.** Resolution
   leaves eta unchanged to 1e-8 while moving UA by 0.041 % between 25 and
   100 nodes. The pinch is a minimum, so its first-order discretisation
   error vanishes near the extremum; UA is an integral of dQ/dT and its
   does not. Since mass is an objective, that is the number that
   mattered, and the first version of the study did not report it.
3. **The first version swept nothing.** It varied `Numerics.nodes`, which
   these cases override per exchanger, and reported a reassuring column
   of zeros. Caught because a 16x resolution change showing exactly zero
   is not believable.

**A solver defect, found and fixed.** `Case.with_()` deep-merged `params`
but replaced `numerics` with a raw dict, so `with_(numerics={"tol": 1e-9})`
failed deep inside the tear loop with `'dict' object has no attribute
'max_iter'` -- an error that says nothing about the real mistake. Now
both `numerics` and `environment` accept a partial dict, and an unknown
field raises at construction naming the valid ones.

**Appendix A automated.** `tools/make_tables.py` generates 11 LaTeX
tables from saved results; `project/studies/cooling.py` now saves the two
tables it was only printing. Every hand-typed row was compared against
its generated replacement.

**The comparison found a real bug -- in the new code, not the old table.**
`W_net` read 0.10 where it should read 36.5 MW: `metrics["w_net"]` is
*specific* work in J/kg and must be multiplied by the mass flow. Two
places, both written last night when saving was added. Fixed; the saved
performance table now closes the first law exactly (41.41 + 58.59 =
100.00 MW). Every other hand-typed value matched its generated
replacement digit for digit.

Also separated three cell meanings that the first generator collapsed
into one: a number, *not applicable* (an em dash -- a pinch has no total,
and a cooler with no circuit has no pump work), and a blank repeated row
label. Writing 0 for "no such quantity" is a false claim.

**Verified:** 32 tests pass. All nine studies execute and save.

**Known, and deliberately deferred to Phase 6:** the manifest
fingerprints no longer agree across studies, because source changed
between runs. That is the mechanism working. Everything will be re-run
from the final source state before the release package is built.

**Next:** Phase 1 and 2 -- split the technical document and write the
final report.

## 2026-11-09

### 19:40 -- Worked numbers restored to the technical document

The user, on reading the split document: *"the theory implementation
without numbers feels difficult to read. Its just that I didnt know
where the numbers were coming from and where were they stored."*

He is right and the correction is mine. His standing rule was never
"no numbers" -- it was that teaching numbers should be concrete, real
computed figures should be traceable, and the reader should always know
which is which. When the completion directive said to move project
results into the report, **I treated every number as a result.** The 11
figures in the recuperator chapter and the comparison tables in the
layout chapter were not results; they were what made those chapters
teachable. Stripping them left prose that asserted conclusions without
showing the evidence for them.

The clinching detail: the intercooling section I deleted contained the
sentence *"'23 % more exchanger' is an argument. Leaving it out is
not."* I wrote that and then did exactly what it warns against.

**The fix is not simply to put them back.** The original complaint --
not knowing where numbers came from -- would return. So:

- A `\from{file}{command}` macro prints a small grey line under every
  computed table naming the saved file and the command that regenerates
  it. Both arguments are `\detokenize`d, because every one of these
  paths contains an underscore and hand-escaping file paths is the same
  transcription problem in another costume.
- A companion `\invented` macro marks the round teaching numbers, so
  the two kinds are never confused.

**Restored:** every layout's heat sink, total conductance, intercooling
(idea, cost, why the saving does not survive, where the pressure should
sit), exergy by component.

**A stale caveat, caught by the restore.** The partial-cooling section
still said the low-pressure level "has not been swept" and that no
conclusion could be drawn until it was. It was swept on 7 November.
Replaced with the result: 6.0 MPa is a genuine interior optimum, the
arbitrary original choice was right by luck, two higher pressures fail
physically, and no solvable exhaust pressure satisfies the strict inlet
limit.

**And the restore caught me doing the very thing being fixed.** I
hand-typed six tables back into the document. The generator already
existed. Replacing them with `\input` of the generated versions showed
three of my transcribed exergy figures were wrong -- MC 0.79 against
0.70, RC 0.73 against 0.64, MIX 0.22 against 0.40 -- copied from an
older run. Two prose figures that depended on them were wrong too
(compressor destruction 1.52 against 1.34 MW; the back-work minimum at
12 against 10 MPa).

Nothing caught this but regenerating. **That is the argument for the
whole pipeline, demonstrated on its author within ten minutes of
writing it.**

`exergy_components` added to the generator (12 tables now). Eight
teaching figures added to `check_consistency` -- **37 claims checked,
all consistent**. `test_every_table_has_data` now checks against the
generator's own registry instead of a hardcoded count.

**Verified:** 41 tests pass; manual 96 pp and report 16 pp, both cold
builds, 0 undefined references; 37 claims consistent; no efficiency
figure in either document lacks a saved source.

---

## 9 November -- one document, and diagrams for the report

**The report now shows the layouts instead of describing them.** Five
block diagrams -- simple, recuperated, recompression, partial cooling,
intercooled -- each with a caption saying what defect in the previous
layout it answers. Two of them already existed inside the manual's TeX;
they were pulled out into `documentation/latex/diagrams/` and
`\input` back, so there is one copy of each drawing and both documents
read it. The intercooled one was drawn twice: the first version routed
the return arrow straight through the HP compressor box, which read as a
connection that does not exist.

A sixth diagram, `pipeline`, was added to the report's methodology. It
draws the path a number takes -- case, solver, assessment, `results/`
with a manifest, generated table, document -- because the report asserts
that nothing was transcribed by hand and that claim is easier to show
than to state.

**The manual absorbed the report.** `reports/report_body.tex` now holds
the report's content and is compiled by two wrappers: the standalone
`final_report.tex`, and Part II of the manual. Neither copies the other.
The body contains no relative paths -- tables, plot data and diagrams are
reached through `\tbl`, `\dat` and `\dgm`, which each wrapper defines for
its own directory -- and the manual shifts the body's sectioning down one
level inside a group so `\section` lands as `\chapter`. Nothing in the
shared file is edited to make that work, which is the point: one copy of
the argument, and it cannot drift.

The manual is now in two parts, with a short page in front of each saying
what it is for and which to read first depending on what you want.

**Verified:** 41 tests pass; 37 claims consistent; manual 126 pp and
report 18 pp, both cold builds, 0 undefined references; the configuration
and pipeline diagrams visually inspected page by page.
