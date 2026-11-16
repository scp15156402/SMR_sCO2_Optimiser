# Usage guide

How to install, run and extend the solver.

---

## Install

Python 3.10 or newer (the code uses `X | Y` type unions).

```bash
pip install CoolProp
```

That is the only dependency. Run everything from the folder that contains
`cycles/` and `project/`.

---

## Where things are

```
cycles/                 the solver. Knows nothing about CO2 or Brayton.
  stream.py             Stream(fluid, P, h, flow) -- frozen
  specs.py              what a run fixes: HX, coolant and size specs
  case.py               Case + Numerics, frozen, with_() for variants
  flowsheet.py          Flowsheet + Node, validated at import
  solve.py              orchestration and cycle metrics
  result.py             Result, summary(), state_table(), blocks_of()
  blocks/               one file per block type + a registry
  physics/              the equations: isentropic, exchanger limits,
                        profile, sizing, coolant, hydraulics, mixing
  passes/               pressure -> flow -> ordering -> tear
  properties/           CoolProp and ideal-gas backends behind one Protocol
  numerics/             root finders

brayton_cycle/          the five Brayton topologies. Wiring only --
                        not one number appears in this directory.

project/                this project. Uses the layers above as given.
  cases/                a layout plus every number it needs
  assessment/           mass, cost, metrics, Pareto -- the brief's
                        assumptions, deliberately outside cycles/
  studies/              the engineering studies. Each computes once,
                        prints a summary and saves to results/.
    _io.py              save()/load() plus the run manifest

tests/                  pytest. `pytest` from the root runs all 41.
tools/                  document generators: figures, code excerpts,
                        the architecture map. No engineering here.
results/                what the studies produced. Never hand-edited;
                        regenerate by re-running the study.

documentation/
  theory_and_implementation.pdf   everything: Part I the explanation,
                                  Part II the report. Read this first
  usage.md                        this file
  architecture.md                 generated map: tree + every module's API
  project_tracker.md              live status at the head, append-only log
  latex/                          source, build.py, extracted code, plot data
```

`architecture.md` is **generated**, never hand-edited — a tree typed by
hand is wrong the first time a file is added, and a wrong map is worse
than none because it gets believed. Every signature, constant and
docstring line in it is read out of the source with `ast`; the layout and
case tables are read by importing the packages, because a layout is built
by running code and its wiring is not visible in the syntax tree. The only
hand-written part is the one-line note per directory, which lives in
`PURPOSE` at the top of `tools/make_architecture.py`.

Re-run it after adding or removing a module:

```bash
python -m tools.make_architecture
```

Rebuild the theory document with `python documentation/latex/build.py`.
It re-extracts the code excerpts from source first, so they cannot drift.

---

## Run something

```bash
pytest                                    # all 32 checks, including the formula sheet
python -m project.studies.run_cases           # solve every case, full state tables
python -m project.studies.run_cases pdf_baseline
python -m project.studies.check_nodes         # heat-exchanger grid convergence
python -m project.studies.compare_layouts     # all four layouts at equal pinch
python -m project.studies.precooler           # precooler size against water temperature rise
python -m project.studies.cooling             # every cooler of every layout, plus totals
python -m project.studies.exergy              # where each component destroys work potential
python -m project.studies.validate_exergy     # 16 checks on the exergy calculations
python -m project.studies.validate_literature # 9 checks against Dostal and Kim
python -m project.studies.tradeoff            # R5: sweep, filter, Pareto, knee point
python -m tools.make_figures        # plot data for the theory document
python -m tools.make_code_snippets  # code excerpts for the theory document
python -m tools.make_architecture   # regenerate documentation/architecture.md
```

Start with the three validators. `validate_air` proves the algebra against
a closed form, `validate_exergy` the second-law layer, and
`validate_literature` the CO2 properties and a whole cycle against
published work. If any does not print PASS, something is broken before any
result is worth reading.

---

## Solve a case from Python

```python
from cycles import solve
from project.cases import pdf_baseline

r = solve(pdf_baseline)

print(r.ok)                        # False if anything was flagged
print(r.flags)                     # why, if so
print(r.summary())                 # the headline numbers
print(r.state_table())             # every stream

r.metrics["eta_th"]                # 0.3272
r.metrics["UA_total"]              # W/K
r.blocks["RECUP"]["pinch"]         # K
r.blocks["RECUP"]["profile"].dT    # the whole temperature-difference array
```

### What is in a Result

| Field | Contents |
|---|---|
| `ok` | solved and passed every check |
| `flags` | list of problems; empty when `ok` |
| `streams` | per stream: P, T, h, s, rho, flow |
| `blocks` | per block: its extras (work, duty, epsilon, pinch, UA, profile) |
| `metrics` | cycle level: eta_th, eta_net_of_pump, w_net, w_pump, BWR, mdot, UA_total, pinch_min, margins, E_D_known, E_D_total, exergy_complete |
| `exergy` | component-resolved destruction, per-stream exergy, balance residual |
| `checks` | energy closure, entropy generation per block, tear residual |
| `schedule` | evaluation order, tear streams, iterations |
| `case` | the Case that produced it |

`result.blocks_of("heat_exchanger")` filters by block kind.

---

## Make a variant of a case

Cases are frozen. `with_()` returns a modified **copy**, deep-merging
`params` and `boundary` per key.

```python
from cycles import Pinch, Effectiveness
from cycles.units import MPa, degC, K

hotter   = pdf_baseline.with_(name="hot",  params={"HEATER": dict(T_out=degC(600))})
tighter  = pdf_baseline.with_(name="tight", params={"RECUP": dict(spec=Pinch(K(5)))})
lower_rp = pdf_baseline.with_(name="low_rp", params={"COMP": dict(P_out=MPa(15))})
```

Never mutate a case in place. An optimiser calling `with_()` ten thousand
times on a shared mutable dict is the classic source of a plausible but
wrong Pareto front.

---

## Write a new case

```python
from cycles import Case, Effectiveness, ThermalPower
from cycles.units import MPa, MW, degC
from brayton_cycle import recuperated

my_case = Case(
    name="my_case",
    notes="what this run is for and where the numbers came from",
    fluid="CO2",
    layout=recuperated,
    size=ThermalPower(MW(100)),

    # a boundary stream gives both T and P -- it anchors the loop
    boundary={"s1": {"T": degC(32), "P": MPa(7.7)}},

    params={
        "COMP":   dict(eta=0.89, P_out=MPa(20)),
        "RECUP":  dict(spec=Effectiveness(0.90), nodes=100),
        "HEATER": dict(T_out=degC(500)),
        "TURB":   dict(eta=0.90),
        "COOLER": dict(T_out=degC(32)),
    },
)
```

Every number is SI internally; the unit helpers convert at the point of use.

### Size specifications

```python
ThermalPower(MW(100))    # fixed reactor duty -- mdot = Q_th / q_in
NetPower(MW(40))         # fixed electrical output
MassFlow(400.0)          # kg/s given directly
```

### Heat exchanger specifications

```python
Effectiveness(0.90)      # explicit, fastest
Pinch(K(5))              # solved for; the brief's constraint as a target
UAperFlow(8000.0)        # W/K per kg/s; multiply by mdot to compare with a paper
```

Give one; the other two come back as outputs.

### Optional block parameters

| Block | Parameter | Meaning |
|---|---|---|
| compressor, turbine | `P_out` or `ratio` | pins the outlet pressure |
| heat_exchanger | `dp_hot`, `dp_cold` | fractional pressure loss per side |
| heat_exchanger | `nodes` | profile resolution, default 100 |
| cooler, heater | `dp` | fractional pressure loss |
| cooler | `coolant_fluid`, `coolant_T_in` | turn on the coolant side |
| cooler | `coolant` | which coolant spec (below) |
| cooler | `coolant_P` | coolant operating pressure, Pa, default 6e5 |
| cooler | `circuit` | pressure-drop model (below), default `NoPumping()` |
| cooler | `pump_eta` | pump efficiency, default 0.80 |
| splitter | `x` | fraction to the second outlet |

### Coolant specifications

Any cooler can be sized against a real supply rather than assumed perfect.
Four ways to say how much coolant, all collapsing to a flow:

```python
from cycles import CoolantFlow, CoolantOutlet, CoolantRise, CoolantPinch

CoolantFlow(4.714)       # kg/s of coolant per kg/s of total cycle flow
CoolantOutlet(degC(35))  # it leaves at this temperature
CoolantRise(K(10))       # it warms by this much
CoolantPinch(K(5))       # size for this minimum approach
```

```python
params={"COOLER": dict(coolant_fluid="Water", coolant_T_in=degC(25),
                       coolant=CoolantRise(K(10)))}
```

Only `CoolantFlow` answers "what do I get for this much coolant?", so it is
the one a sweep varies. The other three demand an outcome and report its
cost.

Outputs land in `r.blocks["COOLER"]`: `coolant_flow`, `coolant_T_out`,
`coolant_pinch`, `coolant_pinch_at`, `coolant_UA_per_flow`,
`coolant_profile`, and `pump_w_total` when a circuit was given.

### Circuit specifications (pump work)

**The solver applies a pressure drop you state; it never manufactures one.**
There is deliberately no geometry-based model: this project computes UA and
not geometry, so a geometry-derived drop would describe an exchanger
unrelated to the one being sized.

```python
from cycles import NoPumping, FixedDrop, QuadraticDrop

NoPumping()                                    # default; reports zero, not a guess
FixedDrop(dP=100e3)                            # Pa, flow-independent
QuadraticDrop(dP_ref=100e3, flow_ref=4.714)    # Pa at that flow, scaling as flow^2
```

Drops are **absolute pascals**, not fractions of the operating pressure:
hydraulic loss is set by dynamic pressure, not by how far above atmosphere
the circuit sits. Use `QuadraticDrop` where you can — pump work then goes as
the *cube* of flow, which is what decides whether a coolant sweep has an
interior optimum.

Pump work is an auxiliary load. It never enters `eta_th`; read
`metrics["eta_net_of_pump"]`, `metrics["w_pump"]` or `metrics["W_pump"]`.

### Numerics

```python
from cycles import Numerics
case.with_(numerics=Numerics(nodes=200, tol=1e-9, relax=0.7))
```

Lower `relax` if a tear loop will not settle.

---

## Write a new layout

A layout is pure wiring. No numbers.

```python
from cycles import Flowsheet, Node

my_layout = Flowsheet("my_layout", [
    Node("COMP",   "compressor",     {"in": "s1"}, {"out": "s2"}),
    Node("RECUP",  "heat_exchanger", {"cold_in": "s2", "hot_in": "s5"},
                                     {"cold_out": "s3", "hot_out": "s6"}),
    Node("HEATER", "heater",         {"in": "s3"}, {"out": "s4"}),
    Node("TURB",   "turbine",        {"in": "s4"}, {"out": "s5"}),
    Node("COOLER", "cooler",         {"in": "s6"}, {"out": "s1"}),
])
```

Rules the validator enforces at import:

- every port of the block type must be wired, and no extras;
- every stream has exactly one producer and at least one consumer (a closed
  cycle has no loose ends);
- a mixer's `in` and a splitter's `out` take a **list**; every other port
  takes a single stream id.

Available block types: `compressor`, `turbine`, `heat_exchanger`, `cooler`,
`heater`, `splitter`, `mixer`, `throttle`.

Layouts already written, in `brayton_cycle/`: `simple`, `recuperated`,
`recompression`, `intercooled`, `partial_cooling`.

### Anchoring pressures

Every stream pressure must be derivable from the anchors you give. The usual
pattern is: the boundary stream's `P`, plus `P_out` on the compressor. The
turbine outlet is then found by walking **backwards** from the compressor
inlet through the hot-side losses -- you do not specify it.

A layout with more than two pressure levels (partial cooling) needs one more
anchor, supplied through `pressures={"s7": MPa(6.0)}` on the Case.

If you under-specify you get a clear error naming the unresolved streams; if
you over-specify you get one naming the conflicting relation.

---

## Write a new block

Five exports, in `cycles/blocks/your_block.py`:

```python
TYPE = "your_block"
INLETS = ("in",)
OUTLETS = ("out",)

def pressure_rules(params):
    """(relations, anchors) -- runs before any enthalpy exists."""
    return [], {}

def flow_rule(params):
    from .base import Identity
    return Identity((("in", "out"),))

def evaluate(inlets, P_out, params, props, block_id="?",
             diagnostics=True, hint=None):
    st = inlets["in"]
    p = props(st.fluid)
    ...
    return {"out": new_stream}, {"kind": "your_block", ...}
```

Then import it in `cycles/blocks/__init__.py` and add it to `_MODULES`.
Nothing else changes.

Optional sixth export, `fixed_outlets(params)`, for an outlet whose state is
pinned by a parameter rather than by its inlet -- it can remove a whole tear
loop. The heater and cooler use it.

The `extras` dict must contain `kind`; `solve()` sums cycle metrics by it.
Use `w_total` for work and `q_total` for heat, both already multiplied by
the stream's flow fraction.

---

## Assessment: mass, cost and the trade-off

`project/assessment/` turns a solved cycle into the four things the brief
asks you to defend. It reads a `Result` and never reaches back into it, and
every number in it is an assumption from the brief rather than physics —
which is exactly why it lives in `project/` and not in `cycles/`.

```python
from cycles import solve, Pinch
from cycles.units import K
from project.assessment import assess, feasible, pareto_front, knee
from project.cases import recompression_watercooled

r = solve(recompression_watercooled.with_(
        params={"LTR": dict(spec=Pinch(K(5))), "HTR": dict(spec=Pinch(K(5)))}))
a = assess("recompression", r, split=0.30)

a.eta_th                 # %
a.eta_second_law         # eta_th / Carnot(773 K, 305 K)
a.mass.total_t           # t, from UA at 2.5 kg per kW/K
a.mass.volume_m3         # m3, at the brief's implied 0.5 t/m3
a.mass.mwe_per_t         # compactness
a.cost.hardware_musd     # one-off, at $250/kg
a.cost.annual_energy_musd  # per year, at $70/MWh over 7000 h
a.cost.cost_proxy_musd   # the MOO objective; lower is better
a.T_margin_k             # worst compressor inlet, above critical
```

Then the multi-objective step:

```python
tagged = feasible([a1, a2, a3])          # against the brief's constraints
good   = [c.assessment for c in tagged if c.ok]
front  = pareto_front(good)              # non-dominated designs
pick   = knee(front)                     # one choice, equally weighted
```

`feasible()` returns **every** design tagged, not just the survivors, with
the reason each was rejected — the brief asks for the feasible set after
filtering, and a filter whose rejects are invisible cannot be checked.

### The one constraint that is ambiguous

The brief says *"Compressor inlet ≥ 32 °C and ≥ 7.7 MPa (safe distance from
two-phase region)"*. Partial cooling's pre-compressor sits at 6.00 MPa and
32 °C — below the pressure limit, but well clear of the two-phase region
because it is above the critical temperature. The two readings disagree:

```python
feasible(cands)                                      # strict: rejects partial cooling
feasible(cands, {"strict_inlet_pressure": False})    # intent: admits it
```

Default is strict. It changes the answer, so settle it before quoting a
recommendation.

### The deliverable plots

`make_figures` writes plain whitespace-delimited tables to
`documentation/latex/data/`, which the theory document reads directly with
pgfplots. Nothing is rendered to an image, so a rebuild always plots the
current solver rather than a picture of an old one.

```bash
python -m tools.make_figures
```

| file | what it holds |
|---|---|
| `ts_recompression.dat` | every state of the recommended cycle, keyed by name |
| `ts_path.dat` | the same states **in visiting order**, with labels, for drawing the loop |
| `ts_branch.dat` | the recompression branch, likewise |
| `eta_vs_rp.dat` | efficiency against maximum pressure, two layouts |
| `eta_vs_x.dat` | efficiency against split fraction, two layouts |
| `pareto.dat` | all 43 designs with a `status` column |
| `pareto_{front,knee,dominated,infeasible}.dat` | the same, split by status |

The split files exist because pgfplots cannot filter rows on a *text*
column without preamble trickery; four small files beat one clever style.
The T–s cycle needs both an unordered table (for labelling by name) and an
ordered one (for drawing a polyline), because no sort gives you the order
the fluid actually visits states in.

If you change the recommendation, change the case at the top of
`deliverable_plots()` as well — the T–s figure is built from an explicitly
constructed design, not from the knee point, so the two can drift apart if
only one is edited.

---

## Exergy analysis

Every solve carries one. It is a diagnostic layer: it reads the converged
states and changes nothing, so no first-law number moves because of it.

```python
r = solve(case)

r.metrics["E_D_known"]          # W destroyed, over the components that can be computed
r.metrics["E_D_total"]          # the same, or None when accounting is incomplete
r.metrics["exergy_complete"]    # False whenever a boundary temperature is missing

r.exergy["components"]["RECUP"]["E_D"]      # W, per component instance
r.exergy["fractions"]["RECUP"]              # % of the known total
r.exergy["by_kind"]["heat_exchanger"]       # aggregated by block type
r.exergy["streams"]["s6"]["e_x"]            # J/kg of specific flow exergy
r.exergy["incomplete"]                      # which components, and why
r.exergy["balance_residual"]                # relative; ~1e-8 when it closes
```

`state_table()` gains a specific-exergy column.

### The reference environment

```python
from cycles import Environment
from cycles.units import degC

case.with_(environment=Environment(T0=degC(40), P0=101325.0))
```

Defaults are 298.15 K and 101325 Pa. Physical flow exergy only — chemical
exergy is omitted, which is exact here because the working fluid's
composition never changes, so the term cancels from every difference.

### What cannot be computed, and the one way to fix it

The heater has no heat-source model: no reactor, no primary loop, no
boundary temperature. Its destruction is reported as **unavailable** and
the total as **incomplete**. The CO2 outlet temperature is *not* used as a
substitute — heat flows down a temperature difference, and the whole
irreversibility lives in that gap.

**The solver uses a boundary temperature you state, and never invents one**
— the same rule as the circuit pressure drops:

```python
params={"HEATER": dict(T_out=degC(500), T_source=degC(650))}
```

With `T_source` given, heater destruction becomes computable and the total
can be complete.

A cooler is computable whenever it has a coolant side, because the coolant
states are then known. Without one it is unavailable for the same reason as
the heater.

---

## Change the working fluid

```python
case.with_(fluid="Air")                                    # any CoolProp fluid
case.with_(fluid="AirIdeal", backend="idealgas")           # closed-form validation
```

Known ideal gases are in `cycles/properties/idealgas.py`.

---

## When something goes wrong

The solver raises almost nothing -- problems become flags.

```python
r = solve(case)
if not r.ok:
    for f in r.flags:
        print(f)
```

| Flag | What it means |
|---|---|
| `temperature cross, pinch -X K` | the exchanger is thermodynamically impossible |
| `no temperature overlap` | hot stream is not hotter than the cold one; duty forced to zero |
| `tear streams [...] did not converge` | lower `numerics.relax`, or the layout is badly torn |
| `pressure undetermined for [...]` | add a pressure anchor |
| `pressure network is over-determined` | remove one anchor |
| `energy closure off by X%` | a real bug; report it |
| `negative entropy generation` | a real bug; report it |
| `coldest state is X K below the critical temperature` | the cycle entered two-phase territory |
| `exergy destruction is negative` | a second-law violation; a sign or convergence error, never clipped away |
| `exergy balance does not close` | a term is missing or mis-signed |
| `working-fluid entropy does not close around the loop` | the entropy field the exergy rests on is suspect |
| `coolant temperature cross, pinch -X K` | not enough coolant for the duty asked |
| `stated coolant pressure drop X kPa is at or above the Y kPa operating pressure` | raise `coolant_P` or lower the drop |

A sweep should filter on `r.ok` rather than assume success.

---

## Performance

| Case | Tears | Iterations | Time |
|---|---|---|---|
| recuperated, effectiveness | 0 | — | 0.10 s |
| recuperated + water + pump | 0 | — | 0.18 s |
| partial cooling, effectiveness | 1 | 19 | 0.33 s |
| partial cooling + two water sides | 1 | 19 | 0.45 s |
| intercooled, pinch | 0 | — | 0.72 s |
| recompression, pinch | 1 | 31 | 4.98 s |

Pinch and UA specs are slower because they solve for effectiveness inside
the tear loop. For large sweeps prefer effectiveness, or reduce `nodes`.

A coolant side costs roughly 0.1 s per cooler: it builds a full profile, but
only once, on the final pass — it is skipped while the tear loop is still
converging, because it cannot change the cycle.

The first CoolProp call in a session takes a few seconds (library warm-up),
so time a loop, not a single solve.

## The master sequence

Everything, from a clean checkout, in dependency order. This is what the
release build runs.

```bash
pytest                                        # 41 checks

python -m project.studies.compare_layouts     # the four configurations
python -m project.studies.sweeps              # pressure and split
python -m project.studies.partial_cooling     # its third pressure level
python -m project.studies.intercooling        # its free pressure level
python -m project.studies.cooling             # coolers and water
python -m project.studies.exergy              # second-law accounting
python -m project.studies.tradeoff            # candidates, front, knee
python -m project.studies.selected_design     # needs tradeoff
python -m project.studies.tolerances          # needs tradeoff

python -m tools.make_figures                  # plot data
python -m tools.make_tables                   # LaTeX tables, incl. Appendix A
python -m tools.make_registers                # study/validation/traceability
python -m tools.make_architecture             # the module map
python -m tools.check_consistency             # claims vs saved results

python documentation/latex/build.py           # the manual
python reports/build.py                       # the report
```

Only two dependencies exist: `selected_design` and `tolerances` both
read the knee row that `tradeoff` writes, and both fail with the command
to run if it is missing. Everything else is independent.

After a full sequence every manifest should carry the **same** source
fingerprint. Differing fingerprints mean the source changed mid-run and
the results are a mixture — which is exactly what the fingerprint is
for.

### The generators

| Command | Writes | Reads |
|---|---|---|
| `tools.make_figures` | `documentation/latex/data/*.dat` | `results/` |
| `tools.make_tables` | `documentation/latex/tables/*.tex` | `results/` |
| `tools.make_registers` | `documentation/registers.md` | the manifests |
| `tools.make_architecture` | `documentation/architecture.md` | the source |
| `tools.check_consistency` | nothing; exits non-zero on a mismatch | `results/` + both `.tex` |

None of them solves a cycle. `check_consistency` verifies 29
load-bearing claims against saved results and then scans both documents
for efficiency figures with no saved source; figures that legitimately
come from outside `results/` — Kim's published value, for instance —
are listed in that script with the reason.

### Building the two documents

```bash
python documentation/latex/build.py          # 94 pp manual
python documentation/latex/build.py --no-data  # skip regeneration
python reports/build.py                      # 16 pp report
```

`reports/build.py` regenerates the tables first, so Appendix A is never
stale: rerun a study, rebuild the report, and the appendix follows.

---
