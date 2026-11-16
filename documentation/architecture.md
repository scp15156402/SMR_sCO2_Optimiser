# Architecture

**Generated** by `python -m tools.make_architecture`.
Do not edit by hand -- regenerate it. Every signature, constant
and docstring line below is read out of the source, so this file
is wrong only if the source changed and nobody re-ran the script.

The directory notes are the one hand-written part, and they live
in `PURPOSE` at the top of that script.

---

## The tree

```text
Programming/
|-- cycles/
|   |-- blocks/
|   |   |-- __init__.py                         The block library.
|   |   |-- base.py                             The contract every block keeps.
|   |   |-- compressor.py                       Compressor (and pump -- same equations, the fluid decides which it ...
|   |   |-- cooler.py                           Heat rejection to a sink.
|   |   |-- heat_exchanger.py                   Counterflow heat exchanger -- the only block that iterates.
|   |   |-- heater.py                           Heat addition from the source.
|   |   |-- mixer.py                            Merge streams at the same pressure.
|   |   |-- splitter.py                         Split one stream into two at the same state.
|   |   |-- throttle.py                         Isenthalpic expansion through a restriction.
|   |   `-- turbine.py                          Turbine.
|   |-- numerics/
|   |   |-- __init__.py                         Small numerical kernels shared by blocks and passes.
|   |   `-- roots.py                            One-dimensional solvers.
|   |-- passes/
|   |   |-- __init__.py                         Solver passes: pressure, flow, ordering, tear.
|   |   |-- flow.py                             Pass 2: resolve the mass-flow fraction carried by every stream.
|   |   |-- ordering.py                         Pass 3: decide what order to evaluate the blocks in, and where to t...
|   |   |-- pressure.py                         Pass 1: resolve every stream pressure, before any enthalpy exists.
|   |   `-- tear.py                             Pass 4: close the loop.
|   |-- physics/
|   |   |-- __init__.py                         Physics shared by more than one block.
|   |   |-- coolant.py                          Sizing a cycle stream against an external coolant supply.
|   |   |-- exergy.py                           Exergy: how much of the work potential each component destroys.
|   |   |-- hx_limits.py                        The two enthalpy limits on a counterflow exchanger.
|   |   |-- hx_profile.py                       Temperature profile through a counterflow exchanger, and the pinch.
|   |   |-- hx_sizing.py                        Conductance UA from a temperature profile.
|   |   |-- hydraulics.py                       Coolant-side pressure drop, and the pump work it implies.
|   |   |-- isentropic.py                       Isentropic reference state and the efficiency step.
|   |   |-- mixing.py                           Adiabatic merge of two or more streams at the same pressure.
|   |   `-- pressure_drop.py                    Fractional pressure loss, and its inverse.
|   |-- properties/
|   |   |-- __init__.py                         Property backends and the resolver blocks use.
|   |   |-- base.py                             What every property backend must provide.
|   |   |-- coolprop.py                         Real-fluid backend (Helmholtz equations of state via CoolProp).
|   |   `-- idealgas.py                         Ideal-gas backend, for validation.
|   |-- README.md                               5 kB
|   |-- __init__.py                             cycles -- a block-based solver for closed thermodynamic power cycles.
|   |-- case.py                                 One run, fully specified.
|   |-- flowsheet.py                            A layout is a list of blocks and the streams between them.
|   |-- result.py                               What a solved cycle hands back.
|   |-- solve.py                                solve(case) -> Result.
|   |-- specs.py                                Specifications: the small tagged values that say *what a run fixes*.
|   |-- stream.py                               The one object every block speaks.
|   `-- units.py                                Unit helpers.
|-- brayton_cycle/
|   |-- __init__.py                             Brayton-cycle configurations, built from the generic solver.
|   |-- intercooled.py                          Intercooled, recuperated Brayton cycle (two compression stages).
|   |-- partial_cooling.py                      Partial cooling cycle (Angelino).
|   |-- recompression.py                        Recompression Brayton cycle.
|   |-- recuperated.py                          Recuperated Brayton cycle -- the project brief's baseline layout.
|   `-- simple.py                               Simple Brayton cycle: compress, heat, expand, reject.
|-- project/
|   |-- assessment/
|   |   |-- __init__.py                         Turning a solved cycle into the four things the brief asks you to d...
|   |   |-- cost.py                             The brief's cost proxy: hardware against the energy it earns.
|   |   |-- mass.py                             What a solved cycle would weigh, from the brief's own figures.
|   |   |-- metrics.py                          Plant-level figures the brief asks R5 for, and one it asks only to ...
|   |   `-- moo.py                              The multi-objective step: filter, then find the frontier, then choose.
|   |-- cases/
|   |   |-- __init__.py                         Run definitions: a layout plus every number it needs.
|   |   |-- air_brayton_ideal.py                Validation: air-standard Brayton cycle, ideal gas.
|   |   |-- literature.py                       Published cases, reproduced to check the solver against someone els...
|   |   |-- pdf_baseline.py                     ME 306 project brief -- baseline simple recuperated sCO2 cycle.
|   |   |-- pdf_intercooled.py                  Intercooling the compression, which the brief lists as an option.
|   |   |-- pdf_partial_cooling.py              ME 306 project brief -- partial cooling layout.
|   |   |-- pdf_recompression.py                ME 306 project brief -- recompression layout.
|   |   `-- pdf_watercooled.py                  Every layout's heat sink, sized against a real cooling-water supply.
|   |-- studies/
|   |   |-- __init__.py
|   |   |-- _io.py                              Saving a study's results, and recording where they came from.
|   |   |-- check_nodes.py                      Grid-convergence check for the heat-exchanger discretisation.
|   |   |-- compare_layouts.py                  Compare layouts on a fair basis.
|   |   |-- cooling.py                          R4: what each layout's heat sink costs.
|   |   |-- exergy.py                           Where each layout destroys its work potential.
|   |   |-- intercooling.py                     Intercooling's free pressure level.
|   |   |-- partial_cooling.py                  Partial cooling's third pressure level, swept at last.
|   |   |-- precooler.py                        R4: what the heat sink actually costs.
|   |   |-- run_cases.py                        Solve every case and print the state table and the key numbers.
|   |   |-- selected_design.py                  The recommended design, solved once, with its full state table saved.
|   |   |-- sweeps.py                           R3/R4: the one-variable sweeps, saved.
|   |   |-- tolerances.py                       Do the engineering conclusions depend on the numerical tolerances?
|   |   `-- tradeoff.py                         R5: the multi-objective step, and the recommendation it leads to.
|   |-- README.md                               3 kB
|   `-- __init__.py                             The ME 306 sCO2 project.
|-- tests/
|   |-- __init__.py
|   |-- baseline.json                           4 kB
|   |-- conftest.py                             Make the repository importable when pytest is run from anywhere.
|   |-- test_regression.py                      Every case must still construct, still solve, and still give the same
|   |-- test_solver.py                          Solver checks that need no project knowledge at all.
|   |-- test_tables.py                          Regression tests for the generated tables.
|   |-- test_validation.py                      The external-validation suite, as assertions.
|   |-- validate_exergy.py                      Checks on the exergy layer, in the spirit of validate_air.
|   `-- validate_literature.py                  Check the solver against somebody else's published numbers.
|-- tools/
|   |-- __init__.py
|   |-- check_consistency.py                    Check every number asserted in the documents against saved results.
|   |-- make_architecture.py                    Generate documentation/architecture.md: the file tree, annotated.
|   |-- make_baseline.py                        Write the regression baseline: every case, its key numbers, as comm...
|   |-- make_code_snippets.py                   Extract the code excerpts that appear in the theory document.
|   |-- make_figures.py                         Regenerate the data behind the figures in the theory document.
|   |-- make_registers.py                       Generate the study, validation and traceability registers.
|   `-- make_tables.py                          Generate every numerical table in the documents from saved results.
|-- results/
|   |-- cooling/
|   |   |-- manifest.json                       2 kB
|   |   |-- per_cooler.csv                      408 B
|   |   `-- water_sweep.csv                     465 B
|   |-- exergy/
|   |   |-- balance.csv                         394 B
|   |   |-- by_component.csv                    2 kB
|   |   `-- manifest.json                       2 kB
|   |-- intercooling/
|   |   |-- manifest.json                       2 kB
|   |   `-- pressure_sweep.csv                  588 B
|   |-- layout_comparison/
|   |   |-- layouts.csv                         536 B
|   |   `-- manifest.json                       2 kB
|   |-- multi_objective/
|   |   |-- candidates.csv                      8 kB
|   |   |-- manifest.json                       3 kB
|   |   `-- pareto_front.csv                    1 kB
|   |-- parameter_sweeps/
|   |   |-- manifest.json                       1 kB
|   |   |-- pressure_sweep.csv                  269 B
|   |   `-- split_fraction_sweep.csv            224 B
|   |-- partial_cooling/
|   |   |-- manifest.json                       2 kB
|   |   |-- pressure_sweep.csv                  502 B
|   |   `-- split_sweep.csv                     506 B
|   |-- selected_design/
|   |   |-- manifest.json                       2 kB
|   |   |-- performance.csv                     270 B
|   |   |-- state_points.csv                    520 B
|   |   |-- ts_branch.csv                       85 B
|   |   `-- ts_loop.csv                         219 B
|   |-- tolerance_sensitivity/
|   |   |-- knee_stability.csv                  243 B
|   |   |-- manifest.json                       3 kB
|   |   |-- mass_propagation.csv                293 B
|   |   `-- sweep.csv                           1 kB
|   `-- README.md                               4 kB
|-- documentation/
|   |-- latex/
|   |   |-- code/
|   |   |   |-- bisect.py                       656 B
|   |   |   |-- case_baseline.py                1 kB
|   |   |   |-- circuit_models.py               886 B
|   |   |   |-- compressor.py                   1 kB
|   |   |   |-- coolant_size.py                 3 kB
|   |   |   |-- coolant_specs.py                246 B
|   |   |   |-- dominance.py                    535 B
|   |   |   |-- duty_limits.py                  486 B
|   |   |   |-- exergy_balance.py               444 B
|   |   |   |-- exergy_specific.py              470 B
|   |   |   |-- feasible.py                     2 kB
|   |   |   |-- fixed_outlets.py                114 B
|   |   |   |-- flow_rules.py                   274 B
|   |   |   |-- hx_profile.py                   718 B
|   |   |   |-- hx_seek.py                      185 B
|   |   |   |-- hx_spec.py                      1 kB
|   |   |   |-- inlets.py                       363 B
|   |   |   |-- isentropic.py                   301 B
|   |   |   |-- knee.py                         679 B
|   |   |   |-- layout_recompression.py         862 B
|   |   |   |-- mass_of.py                      1 kB
|   |   |   |-- metrics.py                      782 B
|   |   |   |-- ordering.py                     1 kB
|   |   |   |-- payback.py                      373 B
|   |   |   |-- pressure_propagate.py           363 B
|   |   |   |-- relation.py                     346 B
|   |   |   |-- sat_guard.py                    290 B
|   |   |   |-- secant.py                       740 B
|   |   |   |-- solve_monotone.py               465 B
|   |   |   |-- stream.py                       654 B
|   |   |   |-- subst.py                        376 B
|   |   |   |-- tear_guess.py                   438 B
|   |   |   |-- tear_loop.py                    719 B
|   |   |   `-- ua_sizing.py                    594 B
|   |   |-- data/
|   |   |   |-- cp_co2.dat                      3 kB
|   |   |   |-- eta_vs_rp.dat                   210 B
|   |   |   |-- eta_vs_x.dat                    188 B
|   |   |   |-- exergy_by_layout.dat            324 B
|   |   |   |-- exergy_vs_x.dat                 1 kB
|   |   |   |-- pareto.dat                      2 kB
|   |   |   |-- pareto_dominated.dat            1 kB
|   |   |   |-- pareto_front.dat                177 B
|   |   |   |-- pareto_infeasible.dat           290 B
|   |   |   |-- pareto_knee.dat                 68 B
|   |   |   |-- precooler_profile.dat           3 kB
|   |   |   |-- recup_profile.dat               3 kB
|   |   |   |-- ts_branch.dat                   66 B
|   |   |   |-- ts_path.dat                     204 B
|   |   |   |-- ts_recompression.dat            430 B
|   |   |   `-- ua_vs_eps.dat                   813 B
|   |   |-- diagrams/
|   |   |   |-- intercooled.tex                 1 kB
|   |   |   |-- partialcooling.tex              3 kB
|   |   |   |-- pipeline.tex                    1 kB
|   |   |   |-- recompression.tex               2 kB
|   |   |   |-- recuperated.tex                 1 kB
|   |   |   `-- simple.tex                      522 B
|   |   |-- tables/
|   |   |   |-- coolers.tex                     555 B
|   |   |   |-- exergy_balance.tex              346 B
|   |   |   |-- exergy_components.tex           437 B
|   |   |   |-- intercooling.tex                574 B
|   |   |   |-- layout_comparison.tex           386 B
|   |   |   |-- pareto_front.tex                515 B
|   |   |   |-- partial_cooling.tex             380 B
|   |   |   |-- performance.tex                 432 B
|   |   |   |-- state_points.tex                750 B
|   |   |   |-- tolerances.tex                  881 B
|   |   |   |-- total_conductance.tex           365 B
|   |   |   `-- water_sweep.tex                 486 B
|   |   |-- build.py                            Rebuild the theory document.
|   |   |-- theory_and_implementation.pdf       925 kB
|   |   `-- theory_and_implementation.tex       222 kB
|   |-- SMR_sCO2_Brayton_Problem_Statement.pdf  319 kB
|   |-- architecture.md                         59 kB
|   |-- migration_table.md                      4 kB
|   |-- project_tracker.md                      89 kB
|   |-- registers.md                            18 kB
|   |-- theory_and_implementation.pdf           925 kB
|   `-- usage.md                                24 kB
```

## Registered layouts

Block id and type, in topological order. This is the whole of
what a layout file contains -- no numbers.

```text
simple           COMP[compressor]  HEATER[heater]  TURB[turbine]  COOLER[cooler]
recuperated      COMP[compressor]  RECUP[heat_exchanger]  HEATER[heater]  TURB[turbine]  COOLER[cooler]
recompression    MC[compressor]  LTR[heat_exchanger]  SPLIT[splitter]  PC[cooler]  RC[compressor]  MIX[mixer]  HTR[heat_exchanger]  HEATER[heater]  TURB[turbine]
intercooled      LPC[compressor]  IC[cooler]  HPC[compressor]  RECUP[heat_exchanger]  HEATER[heater]  TURB[turbine]  PC[cooler]
partial_cooling  TURB[turbine]  HTR[heat_exchanger]  LTR[heat_exchanger]  PC1[cooler]  PCOMP[compressor]  SPLIT[splitter]  PC2[cooler]  MC[compressor]  RC[compressor]  MIX[mixer]  HEATER[heater]
```

## Registered cases (17)

Importable by name from `project.cases`. Note that
`air_brayton_real` means real *machines* (eta < 1), not a
real fluid -- hence the ideal-gas backend.

```text
case                         layout           fluid      backend
pdf_baseline                 recuperated      CO2        coolprop
pdf_baseline_dp              recuperated      CO2        coolprop
pdf_recompression            recompression    CO2        coolprop
pdf_recompression_pinch      recompression    CO2        coolprop
pdf_partial_cooling          partial_cooling  CO2        coolprop
pdf_intercooled              intercooled      CO2        coolprop
pdf_intercooled_geometric    intercooled      CO2        coolprop
baseline_watercooled         recuperated      CO2        coolprop
baseline_watercooled_pinch   recuperated      CO2        coolprop
baseline_watercooled_flow    recuperated      CO2        coolprop
baseline_pumped              recuperated      CO2        coolprop
recompression_watercooled    recompression    CO2        coolprop
intercooled_watercooled      intercooled      CO2        coolprop
partial_cooling_watercooled  partial_cooling  CO2        coolprop
air_brayton_ideal            simple           AirIdeal   idealgas
air_brayton_real             simple           AirIdeal   idealgas
kim_2018                     recompression    CO2        coolprop
```

Everything below is the same tree with each module's API
spelled out.


## `cycles/`

The solver. Generic: knows nothing about CO2, Brayton, or this project. Could run an ammonia Rankine cycle unchanged.

- **`README.md`** &mdash; 4,618 bytes

### `__init__.py` (36 lines)

> cycles -- a block-based solver for closed thermodynamic power cycles.

- *(no module-level definitions)*

### `case.py` (98 lines)

> One run, fully specified.

- `@dataclass Numerics`
  - `nodes: int = 100`
  - `tol: float = 1e-08`
  - `max_iter: int = 200`
  - `relax: float = 1.0`
  - `energy_tol: float = 0.001`
- `@dataclass Case`
  - `name: str`
  - `fluid: str`
  - `layout: Flowsheet`
  - `size: object`
  - `boundary: Mapping[str, dict]`
  - `params: Mapping[str, dict]`
  - `pressures: Mapping[str, float] = field(default_factory=dict)`
  - `backend: str = 'coolprop'`
  - `numerics: Numerics = field(default_factory=Numer...`
  - `environment: Environment = field(default_factory=Envir...`
  - `notes: str = ''`
  - `__post_init__(self)`
  - `with_(self, **kw)` &mdash; Copy with overrides.  `params`, `boundary` and `pressures` merge

### `flowsheet.py` (129 lines)

> A layout is a list of blocks and the streams between them.

- `@dataclass Node` &mdash; One block instance, wired.
  - `id: str`
  - `type: str`
  - `inlets: Mapping[str, object]`
  - `outlets: Mapping[str, object]`
  - `inlet_streams(self)`
  - `outlet_streams(self)`
- `_flatten(values)`
- `@dataclass Flowsheet`
  - `name: str`
  - `nodes: tuple`
  - `__post_init__(self)`
  - `node(self, node_id)`
  - `streams(self)`
  - `producer(self, stream)`
  - `consumers(self, stream)`
  - `validate(self)` &mdash; Catch wiring mistakes at import, not halfway through a sweep.

### `result.py` (74 lines)

> What a solved cycle hands back.

- `@dataclass Result`
  - `case: object`
  - `ok: bool`
  - `flags: list = field(default_factory=list)`
  - `streams: dict = field(default_factory=dict)`
  - `blocks: dict = field(default_factory=dict)`
  - `metrics: dict = field(default_factory=dict)`
  - `checks: dict = field(default_factory=dict)`
  - `schedule: dict = field(default_factory=dict)`
  - `exergy: dict = field(default_factory=dict)`
  - `__getitem__(self, key)`
  - `blocks_of(self, kind)`
  - `summary(self)`
  - `state_table(self)` &mdash; Every stream, with its exergy alongside its enthalpy.

### `solve.py` (281 lines)

> solve(case) -> Result.

- `ADIABATIC = {'compressor', 'turbine', 'throttle'}`

- `_port_ids(node, port)`
- `_initial_tear_guess(case, props, P, tears)` &mdash; A domain-informed starting point: a quarter of the way up the cycle's
- `solve(case)`

### `specs.py` (104 lines)

> Specifications: the small tagged values that say *what a run fixes*.

- `HX_SPECS = (Effectiveness, Pinch, UAperFlow)`
- `COOLANT_SPECS = (CoolantFlow, CoolantOutlet, CoolantRise,...`
- `SIZE_SPECS = (ThermalPower, NetPower, MassFlow)`

- `@dataclass Effectiveness` &mdash; Q = value * min(Q_hot_limit, Q_cold_limit).  Explicit, no loop.
  - `value: float`
- `@dataclass Pinch` &mdash; Minimum temperature difference anywhere in the exchanger, in K.
  - `value: float`
- `@dataclass UAperFlow` &mdash; Conductance per unit total cycle mass flow, in W/K per (kg/s).
  - `value: float`
- `@dataclass CoolantFlow` &mdash; Coolant mass flow per unit total cycle flow, given directly.
  - `value: float`
- `@dataclass CoolantOutlet` &mdash; Coolant leaves at this temperature, in K.
  - `value: float`
- `@dataclass CoolantRise` &mdash; Coolant warms by this much, in K.
  - `value: float`
- `@dataclass CoolantPinch` &mdash; Minimum approach between the cycle stream and the coolant, in K.
  - `value: float`
- `@dataclass ThermalPower` &mdash; Total heat into the cycle, in W.  mdot = Q_th / q_in.
  - `value: float`
- `@dataclass NetPower` &mdash; Net shaft power, in W.  mdot = W_net / w_net.
  - `value: float`
- `@dataclass MassFlow` &mdash; Total cycle mass flow, in kg/s, given directly.
  - `value: float`

### `stream.py` (38 lines)

> The one object every block speaks.

- `@dataclass Stream`
  - `fluid: str`
  - `P: float`
  - `h: float`
  - `flow: float = 1.0`
  - `with_(self, **kw)`
  - `describe(self, props)` &mdash; Full state, for reporting.  Needs a property backend.

### `units.py` (41 lines)

> Unit helpers.

- `Pa(x)`
- `kPa(x)`
- `MPa(x)`
- `bar(x)`
- `K(x)`
- `degC(x)`
- `J(x)`
- `kJ(x)`
- `MJ(x)`
- `W(x)`
- `kW(x)`
- `MW(x)`
- `W_per_K(x)`
- `kW_per_K(x)`
- `MW_per_K(x)`
- `to_degC(T)`
- `to_MPa(P)`
- `to_kPa(P)`
- `to_kJ(h)`
- `to_MW(P)`
- `to_kW_per_K(ua)`

## `cycles/blocks/`

One file per block type, plus a registry. Every block answers the same four questions, so the solver never branches on type.


### `__init__.py` (50 lines)

> The block library.

- `_MODULES = (compressor, turbine, heat_exchanger, coo...`
- `REGISTRY = {m.TYPE: m for m in _MODULES}`

- `get(block_type)`
- `multi_in(module)`
- `multi_out(module)`
- `fixed_outlets(module, params)` &mdash; Outlet states a block pins from its parameters alone. Usually none.

### `base.py` (86 lines)

> The contract every block keeps.

- `@dataclass Relation` &mdash; Pressure link between two ports, usable in either direction.
  - `src: str`
  - `dst: str`
  - `forward: Callable[[float], float]`
  - `backward: Callable[[float], float]`
- `identity_relation(src, dst)`
- `ratio_relation(src, dst, ratio)`
- `drop_relation(src, dst, delta)`
- `@dataclass Identity` &mdash; Flow passes straight through, port to port.
  - `pairs: tuple`
- `@dataclass Scale` &mdash; One inlet divided among outlets by fixed fractions.
  - `inlet: str`
  - `outlets: tuple`
- `@dataclass Sum` &mdash; Several inlets merged into one outlet.
  - `inlet: str`
  - `outlet: str`
- `require(params, key, block_id='?')`

### `compressor.py` (52 lines)

> Compressor (and pump -- same equations, the fluid decides which it is).

- `TYPE = 'compressor'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`

- `pressure_rules(params)` &mdash; Either the outlet pressure is pinned, or a ratio links the ports.
- `flow_rule(params)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `cooler.py` (109 lines)

> Heat rejection to a sink.

- `TYPE = 'cooler'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `fixed_outlets(params)` &mdash; The outlet state is pinned by `T_out`, independent of what comes in.
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `heat_exchanger.py` (162 lines)

> Counterflow heat exchanger -- the only block that iterates.

- `TYPE = 'heat_exchanger'`
- `INLETS = ('hot_in', 'cold_in')`
- `OUTLETS = ('hot_out', 'cold_out')`

- `pressure_rules(params)`
- `flow_rule(params)`
- `_seek(f, target, warm, tol=1e-09)` &mdash; Solve for the effectiveness that hits `target`.
- `_profile_for(eps, props, hot_in, cold_in, P_out, q_max, nodes, P_hot_in, P_cold_in)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)` &mdash; `diagnostics=False` is used inside the tear loop.

### `heater.py` (75 lines)

> Heat addition from the source.

- `TYPE = 'heater'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `fixed_outlets(params)` &mdash; The outlet state is pinned by `T_out`, independent of what comes in.
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `mixer.py` (59 lines)

> Merge streams at the same pressure.

- `TYPE = 'mixer'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`
- `MULTI_IN = ('in',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `splitter.py` (39 lines)

> Split one stream into two at the same state.

- `TYPE = 'splitter'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`
- `MULTI_OUT = ('out',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `throttle.py` (40 lines)

> Isenthalpic expansion through a restriction.

- `TYPE = 'throttle'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

### `turbine.py` (49 lines)

> Turbine.

- `TYPE = 'turbine'`
- `INLETS = ('in',)`
- `OUTLETS = ('out',)`

- `pressure_rules(params)`
- `flow_rule(params)`
- `evaluate(inlets, P_out, params, props, block_id='?', diagnostics=True, hint=None)`

## `cycles/numerics/`

Root finders. Deliberately small and dumb.


### `__init__.py` (6 lines)

> Small numerical kernels shared by blocks and passes.

- *(no module-level definitions)*

### `roots.py` (114 lines)

> One-dimensional solvers.

- `ConvergenceError(RuntimeError)`
- `bisect(f, lo, hi, tol=1e-10, max_iter=200)` &mdash; Smallest-assumption root finder: needs only a sign change on [lo, hi].
- `solve_monotone(f, target, lo, hi, tol=1e-10, max_iter=200, clamp=True)` &mdash; Find x with f(x) = target, where f is monotone on [lo, hi].
- `successive_substitution(g, x0, tol=1e-08, max_iter=200, relax=1.0)` &mdash; Solve x = g(x).
- `secant(f, target, x0, lo, hi, tol=1e-10, max_iter=40, step=0.0001)` &mdash; Find x with f(x) = target, starting from a good guess x0.

## `cycles/passes/`

The four solver passes, in the order they run: pressure -> flow -> ordering -> tear.


### `__init__.py` (8 lines)

> Solver passes: pressure, flow, ordering, tear.

- *(no module-level definitions)*

### `flow.py` (86 lines)

> Pass 2: resolve the mass-flow fraction carried by every stream.

- `FlowError(RuntimeError)`
- `_ids(node, port)`
- `resolve(case)`

### `ordering.py` (62 lines)

> Pass 3: decide what order to evaluate the blocks in, and where to tear.

- `@dataclass Schedule`
  - `order: tuple`
  - `tears: tuple`
  - `@property is_explicit(self)`
- `build(layout, known_streams)`

### `pressure.py` (100 lines)

> Pass 1: resolve every stream pressure, before any enthalpy exists.

- `PressureError(RuntimeError)`
- `_port_streams(node, port)` &mdash; Map a port name to its stream id(s).
- `resolve(case)` &mdash; Return {stream_id: pressure}. Raises if under- or over-determined.

### `tear.py` (52 lines)

> Pass 4: close the loop.

- `solve(evaluate_once, tears, guesses, numerics)` &mdash; Iterate `evaluate_once(guess_map) -> (state, produced_map)` to a fixed point.

## `cycles/physics/`

Equations shared by more than one block. No block owns these, so none of them imports a block.


### `__init__.py` (9 lines)

> Physics shared by more than one block.

- *(no module-level definitions)*

### `coolant.py` (131 lines)

> Sizing a cycle stream against an external coolant supply.

- `@dataclass CoolantSide` &mdash; Everything the coolant side of one cooler turned out to need.
  - `fluid: str`
  - `flow: float`
  - `T_in: float`
  - `T_out: float`
  - `P: float`
  - `pinch: float`
  - `pinch_at: float`
  - `UA_per_flow: float`
  - `dP: float`
  - `pump_w: float`
  - `profile: object`
  - `flags: tuple`
- `size(hot_in, hot_out, duty, spec, props, *, fluid, T_in, P, circuit=None, pump_eta=0.8, nodes=100, block_id='?')` &mdash; Size one cooler against its coolant supply.

### `exergy.py` (346 lines)

> Exergy: how much of the work potential each component destroys.

- `T0_DEFAULT = 298.15`
- `P0_DEFAULT = 101325.0`
- `NEGATIVE_TOL = 1e-06`

- `@dataclass Environment` &mdash; The dead state everything is measured against.
  - `T0: float = T0_DEFAULT`
  - `P0: float = P0_DEFAULT`
- `dead_state(backend, T0, P0)` &mdash; (h0, s0) at the reference environment, cached.
- `specific(backend, env, P, h, s=None)` &mdash; Physical flow exergy, J/kg.
- `_s(props, stream)`
- `_entropy_balance(node, streams, props)` &mdash; Net entropy leaving a block with its streams, per unit cycle flow.
- `analyse(layout, streams, blocks, props, env, mdot, fluid, W_net=0.0)` &mdash; Component-resolved exergy destruction for a solved cycle.
- `_balance(comps, blocks, props, env, mdot, W_net, destroyed)` &mdash; Close the exergy books over a boundary that is actually defined.
- `_in_out(node, streams)`
- `_first(v)`
- `_by_kind(comps)` &mdash; Aggregate by block type. A kind with any unavailable member is None,
- `stream_table(streams, props, env, mdot)` &mdash; Specific exergy and exergy flow for every stream.

### `hx_limits.py` (75 lines)

> The two enthalpy limits on a counterflow exchanger.

- `SAT_TOL = 0.001`

- `limiting_enthalpy(backend, P, T, direction)` &mdash; Enthalpy at (P, T), resolved when that point lies on a saturation line.
- `duty_limits(props, hot_in, cold_in, P_hot_out, P_cold_out)` &mdash; Return (Q_hot_limited, Q_cold_limited), both in W per kg/s of total flow.
- `max_duty(props, hot_in, cold_in, P_hot_out, P_cold_out)` &mdash; Q_max = min of the two limits, with which one bound.

### `hx_profile.py` (65 lines)

> Temperature profile through a counterflow exchanger, and the pinch.

- `@dataclass Profile`
  - `x: tuple`
  - `T_hot: tuple`
  - `T_cold: tuple`
  - `dT: tuple`
  - `Q: float`
  - `@property pinch(self)`
  - `@property pinch_at(self)`
- `_lerp(a, b, t)`
- `build(props, hot_in, cold_in, hot_out_h, Q, P_hot_in, P_hot_out, P_cold_in, P_cold_out, nodes=100)` &mdash; Walk the exchanger from the cold end in `nodes` equal-duty steps.

### `hx_sizing.py` (39 lines)

> Conductance UA from a temperature profile.

- `lmtd(dT1, dT2)` &mdash; Log-mean of two end differences; falls back to the mean when equal.
- `ua_from_profile(profile)` &mdash; Sum the segment conductances. NaN if the profile has a temperature cross.

### `hydraulics.py` (97 lines)

> Coolant-side pressure drop, and the pump work it implies.

- `CIRCUIT_MODELS = (NoPumping, FixedDrop, QuadraticDrop)`

- `@dataclass NoPumping` &mdash; No circuit modelled.  The default, and an honest one.
- `@dataclass FixedDrop` &mdash; A stated loss in Pa, the same whatever the flow.
  - `dP: float`
- `@dataclass QuadraticDrop` &mdash; dP = dP_ref * (mdot / flow_ref)^2, anchored at a point you know.
  - `dP_ref: float`
  - `flow_ref: float`
- `pressure_drop(model, flow)` &mdash; Pressure drop in Pa for a coolant flow, in normalised units.
- `pump_work(flow, dP, rho, eta)` &mdash; w = v dP / eta for an incompressible coolant, times its flow.

### `isentropic.py` (24 lines)

> Isentropic reference state and the efficiency step.

- `isentropic_outlet_h(backend, P_out, s_in)` &mdash; h_s: enthalpy at the outlet pressure on the inlet isentrope.
- `compress(h_in, h_s, eta)` &mdash; Real compression: the gap to the isentropic state is widened by 1/eta.
- `expand(h_in, h_s, eta)` &mdash; Real expansion: only eta of the isentropic drop is recovered.

### `mixing.py` (21 lines)

> Adiabatic merge of two or more streams at the same pressure.

- `mix(streams)` &mdash; Flow-weighted enthalpy; flows add.  Returns (h, flow).
- `pressure_mismatch(streams)` &mdash; Largest relative pressure difference between the inlets.

### `pressure_drop.py` (18 lines)

> Fractional pressure loss, and its inverse.

- `drop(P_in, delta)` &mdash; Downstream pressure after losing a fraction `delta`.
- `undrop(P_out, delta)` &mdash; Upstream pressure that would produce `P_out` after the same loss.

## `cycles/properties/`

Property backends behind one Protocol. Swapping CoolProp for ideal gas is a string in a Case.


### `__init__.py` (29 lines)

> Property backends and the resolver blocks use.

- `make_backend(fluid, backend='coolprop')` &mdash; One fluid -> one backend instance.
- `make_props(fluids, backend='coolprop')` &mdash; Build the resolver a solve() call hands to every block.

### `base.py` (58 lines)

> What every property backend must provide.

- `Backend(Protocol)`
  - `fluid: str`
  - `name: str`
  - `h_pt(self, P, T)`
  - `s_pt(self, P, T)`
  - `T_ph(self, P, h)`
  - `s_ph(self, P, h)`
  - `h_ps(self, P, s)`
  - `rho_ph(self, P, h)`
  - `cp_ph(self, P, h)`
  - `@property T_crit(self)`
  - `@property P_crit(self)`
- `Props` &mdash; Resolves a fluid name to its backend.
  - `__init__(self, backends)`
  - `__call__(self, fluid)`
  - `fluids(self)`

### `coolprop.py` (45 lines)

> Real-fluid backend (Helmholtz equations of state via CoolProp).

- `CoolPropBackend`
  - `__init__(self, fluid)`
  - `h_pt(self, P, T)`
  - `s_pt(self, P, T)`
  - `T_ph(self, P, h)`
  - `s_ph(self, P, h)`
  - `h_ps(self, P, s)`
  - `rho_ph(self, P, h)`
  - `cp_ph(self, P, h)`
  - `@property T_crit(self)`
  - `@property P_crit(self)`
  - `has_saturation(self, P)` &mdash; Is there a two-phase dome at this pressure?
  - `T_sat(self, P)`
  - `h_sat(self, P, q)` &mdash; Saturated enthalpy: q=0 is liquid, q=1 is vapour.

### `idealgas.py` (74 lines)

> Ideal-gas backend, for validation.

- `T_REF = 298.15`
- `P_REF = 101325.0`
- `GASES = {'AirIdeal': (287.0, 1005.0), 'CO2Ideal':...`

- `IdealGasBackend`
  - `__init__(self, fluid, R=None, cp=None)`
  - `h_pt(self, P, T)`
  - `s_pt(self, P, T)`
  - `T_ph(self, P, h)`
  - `s_ph(self, P, h)`
  - `h_ps(self, P, s)`
  - `rho_ph(self, P, h)`
  - `cp_ph(self, P, h)`
  - `@property T_crit(self)`
  - `@property P_crit(self)`
  - `has_saturation(self, P)` &mdash; An ideal gas never condenses, so (P, T) is always unambiguous.
  - `T_sat(self, P)`
  - `h_sat(self, P, q)`

## `brayton_cycle/`

Layer 2. The five Brayton configurations, as wiring only -- which block feeds which. Not one number appears in this directory; numbers live in a case.


### `__init__.py` (21 lines)

> Brayton-cycle configurations, built from the generic solver.

- `LAYOUTS = {'simple': simple, 'recuperated': recuper...`

### `intercooled.py` (23 lines)

> Intercooled, recuperated Brayton cycle (two compression stages).

- *(no module-level definitions)*

### `partial_cooling.py` (52 lines)

> Partial cooling cycle (Angelino).

- *(no module-level definitions)*

### `recompression.py` (31 lines)

> Recompression Brayton cycle.

- *(no module-level definitions)*

### `recuperated.py` (21 lines)

> Recuperated Brayton cycle -- the project brief's baseline layout.

- *(no module-level definitions)*

### `simple.py` (15 lines)

> Simple Brayton cycle: compress, heat, expand, reject.

- *(no module-level definitions)*

## `project/`

Layer 3. The SMR assignment. Imports cycles and brayton_cycle as black boxes and never reaches into them.

- **`README.md`** &mdash; 3,327 bytes

### `__init__.py` (7 lines)

> The ME 306 sCO2 project.

- *(no module-level definitions)*

## `project/assessment/`

Mass, cost, margins, Pareto. Every figure in here came from the brief rather than from physics, which is exactly why it is outside cycles/.


### `__init__.py` (27 lines)

> Turning a solved cycle into the four things the brief asks you to defend.

- *(no module-level definitions)*

### `cost.py` (86 lines)

> The brief's cost proxy: hardware against the energy it earns.

- `USD_PER_KG = 250.0`
- `USD_PER_MWH = 70.0`
- `HOURS_PER_YEAR = 7000.0`
- `LIFETIME_YEARS = 30.0`

- `@dataclass CostModel`
  - `usd_per_kg: float = USD_PER_KG`
  - `usd_per_mwh: float = USD_PER_MWH`
  - `hours_per_year: float = HOURS_PER_YEAR`
  - `lifetime_years: float = LIFETIME_YEARS`
- `@dataclass Cost`
  - `hardware_musd: float`
  - `annual_energy_musd: float`
  - `annualised_musd: float`
  - `cost_proxy_musd: float`
- `cost_of(result, mass, model=CostModel())` &mdash; Hardware cost and energy value for one solved cycle.
- `payback_years(candidate_mass, candidate_cost, base_mass, base_cost)` &mdash; Years for a design's extra hardware to be repaid by its extra output.

### `mass.py` (99 lines)

> What a solved cycle would weigh, from the brief's own figures.

- `KG_PER_UA = 2.5`
- `RECOMPRESSOR_T = 1.5`
- `BASELINE_PCS_T = 60.0`
- `BASELINE_RECUP_T = 10.0`
- `BASELINE_VOLUME_M3 = 120.0`
- `OTHER_T = BASELINE_PCS_T - BASELINE_RECUP_T`
- `DENSITY_T_PER_M3 = BASELINE_PCS_T / BASELINE_VOLUME_M3`

- `@dataclass MassModel`
  - `kg_per_ua: float = KG_PER_UA`
  - `recompressor_t: float = RECOMPRESSOR_T`
  - `other_t: float = OTHER_T`
  - `density_t_per_m3: float = DENSITY_T_PER_M3`
- `@dataclass Mass`
  - `recuperators_t: float`
  - `coolers_t: float`
  - `machines_t: float`
  - `total_t: float`
  - `volume_m3: float`
  - `mwe_per_t: float`
  - `mwe_per_m3: float`
- `mass_of(result, model=MassModel())` &mdash; Mass and volume of one solved cycle.

### `metrics.py` (103 lines)

> Plant-level figures the brief asks R5 for, and one it asks only to report.

- `T_SOURCE_K = 773.0`
- `T_SINK_K = 305.0`

- `second_law_efficiency(result, T_source=T_SOURCE_K, T_sink=T_SINK_K)` &mdash; eta_th / eta_Carnot.
- `@dataclass Assessment` &mdash; Everything needed to place one design on the trade-off.
  - `name: str`
  - `eta_th: float`
  - `eta_second_law: float`
  - `W_net_mwe: float`
  - `heat_per_mwe: float`
  - `mass: Mass`
  - `cost: Cost`
  - `pinch_min_k: float`
  - `T_margin_k: float`
  - `P_margin_mpa: float`
  - `T_inlet_min_c: float`
  - `P_inlet_min_mpa: float`
  - `P_max_mpa: float`
  - `T_turbine_c: float`
  - `split: float`
- `compressor_inlets(result)` &mdash; (T degC, P MPa) at the inlet of every compressor in the layout.
- `assess(name, result, split=0.0, mass_model=MassModel(), cost_model=CostModel())` &mdash; Reduce a solved cycle to the handful of numbers a decision needs.

### `moo.py` (163 lines)

> The multi-objective step: filter, then find the frontier, then choose.

- `CONSTRAINTS = {'T1_min_c': 32.0, 'P1_min_mpa': 7.7, 'pi...`
- `TOL = 1e-06`
- `OBJECTIVES = (('efficiency', lambda a: a.eta_th, 'max'...`

- `@dataclass Candidate` &mdash; One assessed design, plus why it was or was not allowed.
  - `assessment: object`
  - `ok: bool`
  - `violations: tuple`
- `feasible(assessments, constraints=None)` &mdash; Tag every design with whether it satisfies the brief's constraints.
- `_dominates(a, b, objectives)` &mdash; True if a is at least as good as b everywhere and better somewhere.
- `pareto_front(assessments, objectives=OBJECTIVES)` &mdash; The designs nothing else beats outright.
- `knee(front, objectives=OBJECTIVES)` &mdash; Pick one design: the point closest to the unattainable ideal.

## `project/cases/`

A layout plus every number it needs. Numbers live here and nowhere else.


### `__init__.py` (34 lines)

> Run definitions: a layout plus every number it needs.

- `CASES = {c.name: c for c in (pdf_baseline, pdf_ba...`

### `air_brayton_ideal.py` (46 lines)

> Validation: air-standard Brayton cycle, ideal gas.

- `RP = 10.0`
- `P1 = kPa(100)`

### `literature.py` (74 lines)

> Published cases, reproduced to check the solver against someone else's.

- `KIM_ETA_TURBINE = 0.9`
- `KIM_ETA_COMPRESSOR = 0.85`
- `KIM_EFFECTIVENESS = 0.95`
- `KIM_T_COMP_IN = degC(32)`
- `KIM_P_LOW = MPa(7.4)`
- `KIM_T_TURB_IN = degC(550)`
- `KIM_RP = 2.6`
- `KIM_P_HIGH = MPa(19.24)`
- `KIM_SPLIT = 0.307`
- `KIM_ETA_REPORTED = 0.4467`

- `kim_case(x=KIM_SPLIT, P_high=KIM_P_HIGH, eps=KIM_EFFECTIVENESS, name='kim_2018')`

### `pdf_baseline.py` (49 lines)

> ME 306 project brief -- baseline simple recuperated sCO2 cycle.

- *(no module-level definitions)*

### `pdf_intercooled.py` (61 lines)

> Intercooling the compression, which the brief lists as an option.

- `P_GEOMETRIC = math.sqrt(P_LOW * P_HIGH)`

- `intercooled_case(P_mid, spec=None, T_ic=degC(32), name=None)` &mdash; Brief conditions, two-stage compression with an intercooler.

### `pdf_partial_cooling.py` (50 lines)

> ME 306 project brief -- partial cooling layout.

- `P_LOW = MPa(6.0)`
- `P_MID = MPa(7.7)`
- `P_HIGH = MPa(20.0)`

### `pdf_recompression.py` (45 lines)

> ME 306 project brief -- recompression layout.

- *(no module-level definitions)*

### `pdf_watercooled.py` (108 lines)

> Every layout's heat sink, sized against a real cooling-water supply.

- `WATER = dict(coolant_fluid='Water', coolant_T_in=...`
- `FLOW_REF_10K = 4.714`
- `CIRCUIT = dict(circuit=QuadraticDrop(dP_ref=100000....`
- `TEN_K = dict(WATER, coolant=CoolantRise(K(10)))`
- `TEN_K_PUMPED = dict(TEN_K, **CIRCUIT)`

## `project/studies/`

Engineering studies. Each computes once, returns structured results, and saves them under results/. Run one with python -m project.studies.<name>.


### `__init__.py` (0 lines)

- *(no module-level definitions)*

### `_io.py` (143 lines)

> Saving a study's results, and recording where they came from.

- `ROOT = pathlib.Path(__file__).resolve().parents[2]`
- `RESULTS = ROOT / 'results'`
- `SOURCE_DIRS = ('cycles', 'brayton_cycle', 'project')`

- `source_fingerprint()` &mdash; Hash every source file that could affect a result.
- `_versions()`
- `save(study, tables, *, purpose, command, script, notes=None, inputs=None)` &mdash; Write one study's results to `results/<study>/`.
- `load(study, stem)` &mdash; Read a saved table back. Numeric-looking fields become floats.

### `check_nodes.py` (45 lines)

> Grid-convergence check for the heat-exchanger discretisation.

- `GATE = 0.001`

- `sweep(case, hx_ids, label)`
- `main()`

### `compare_layouts.py` (132 lines)

> Compare layouts on a fair basis.

- `PINCH = Pinch(K(5))`

- `main()`

### `cooling.py` (195 lines)

> R4: what each layout's heat sink costs.

- `PINCH = Pinch(K(5))`
- `LAYOUTS = [('recuperated', baseline_watercooled, {'...`

- `coolers(r)`
- `per_layout()`
- `totals(rows)` &mdash; The number the recuperator-only comparison gets wrong.
- `water_sweep()` &mdash; How much the baseline precooler shrinks as water is added.
- `main()`

### `exergy.py` (234 lines)

> Where each layout destroys its work potential.

- `PINCH = Pinch(K(5))`
- `LAYOUTS = [('recuperated', baseline_watercooled, {'...`

- `pinched(case, specs)`
- `component_rows()` &mdash; One row per component per layout, for saving.
- `balance_rows()` &mdash; The exergy balance per layout, with its residual.
- `per_component()`
- `side_by_side()` &mdash; The same numbers as a comparison, which is what a report wants.
- `_sweep(label, spec, note)`
- `split_sweep()` &mdash; Which irreversibility does raising x trade against which?
- `main()`

### `intercooling.py` (183 lines)

> Intercooling's free pressure level.

- `PINCH = Pinch(K(5))`
- `P_MID = (7.9, 8.2, 8.5, 9.0, 10.0, 11.0, round(P_...`

- `main()`

### `partial_cooling.py` (187 lines)

> Partial cooling's third pressure level, swept at last.

- `PINCH = Pinch(K(5))`
- `P_LOW = (5.0, 5.5, 6.0, 6.5, 7.0, 7.4, 7.6)`
- `P_INLET_LIMIT = 7.7`
- `SPLITS = (0.2, 0.25, 0.3, 0.35, 0.4)`

- `design(P_lo, x)` &mdash; One partial-cooling case: exhaust pressure and split fraction.
- `row(P_lo, x, r)`
- `main()`

### `precooler.py` (65 lines)

> R4: what the heat sink actually costs.

- `line(name, case)`
- `main()`

### `run_cases.py` (51 lines)

> Solve every case and print the state table and the key numbers.

- `report(name)`
- `main(argv)`

### `selected_design.py` (177 lines)

> The recommended design, solved once, with its full state table saved.

- `ETA_TOL_PCT = 0.0001`

- `selected_row()` &mdash; The knee-point row, as the trade-off study labelled it.
- `rebuild(row)` &mdash; Reconstruct the selected case from its recorded parameters.
- `main()`

### `sweeps.py` (153 lines)

> R3/R4: the one-variable sweeps, saved.

- `PINCH = Pinch(K(5))`
- `P_HIGH = (14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0)`
- `P_INLET = 7.7`
- `SPLITS = tuple((i / 100 for i in range(10, 50, 5)))`

- `pressure_sweep()` &mdash; Efficiency against maximum pressure, recuperated and recompression.
- `split_sweep()` &mdash; Efficiency against split fraction, recompression and partial cooling.
- `_best(rows, key, xkey)`
- `main()`

### `tolerances.py` (325 lines)

> Do the engineering conclusions depend on the numerical tolerances?

- `SIGNIFICANCE_PCT = 0.001`
- `TOL = (1e-06, 1e-07, 1e-08, 1e-09, 1e-10)`
- `NODES = (25, 50, 100, 200, 400)`
- `RELAX = (0.5, 0.7, 1.0)`
- `ENERGY_TOL = (0.01, 0.001, 0.0001)`

- `selected()` &mdash; The recommended design, rebuilt from the trade-off's knee row.
- `run(case, **numerics)`
- `run_nodes(case, n)` &mdash; Resolution has to be set on the exchangers, not in Numerics.
- `sweep(case, setting, values, reference)` &mdash; Vary one setting, hold the rest at their defaults.
- `mass_propagation(case)` &mdash; Does the UA variation reach the plant mass?
- `knee_stability()` &mdash; Re-run the whole optimisation at both resolution extremes.
- `main()`

### `tradeoff.py` (293 lines)

> R5: the multi-objective step, and the recommendation it leads to.

- `PINCH = Pinch(K(5))`
- `P_LOW = MPa(7.7)`
- `P_HIGH = (16.0, 18.0, 19.0, 20.0)`
- `INLETS = ((32.0, 7.7), (33.0, 7.7), (35.0, 7.7), (...`
- `SPLITS = (0.2, 0.25, 0.3, 0.35)`
- `PC_SPLITS = (0.25, 0.3, 0.35)`
- `RECOMP_P_HIGH = (18.0, 20.0)`
- `RECOMP_INLETS = ((32.0, 7.7), (35.0, 7.7))`

- `_at(case, nodes)` &mdash; Apply a resolution override to every heat exchanger in a case.
- `recompression_name(P_hi, x, T1)` &mdash; The name a recompression candidate carries, in one place.
- `recompression_design(P_hi, x, T1, P1)` &mdash; Build one recompression candidate.
- `_inlet(case, T_c, P_mpa, cooler)`
- `candidates(nodes=None)` &mdash; Sweep the decision variables the brief lists, layout by layout.
- `rows(tagged, front, pick)` &mdash; One row per candidate, with its verdict.
- `main()`

## `tests/`

pytest suite: solver checks, exergy checks, literature validation, and a regression baseline over every case.


### `__init__.py` (0 lines)

- *(no module-level definitions)*
- **`baseline.json`** &mdash; 4,075 bytes

### `conftest.py` (7 lines)

> Make the repository importable when pytest is run from anywhere.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`

### `test_regression.py` (58 lines)

> Every case must still construct, still solve, and still give the same

- `BASELINE = json.loads((pathlib.Path(__file__).parent...`
- `TOL = 1e-09`

- `test_every_case_is_in_the_baseline()` &mdash; A new case without a baseline entry is an untested case.
- `test_baseline_has_no_orphans()` &mdash; A baseline entry with no case means something was deleted.
- `test_case_reproduces_baseline(name)`

### `test_solver.py` (123 lines)

> Solver checks that need no project knowledge at all.

- `RP = 10.0`
- `P1 = kPa(100)`

- `air_case(eta_c=1.0, eta_t=1.0, name='air')` &mdash; Air-standard Brayton cycle, ideal gas, built without the project.
- `ideal()`
- `closed_form()` &mdash; The air-standard result from a first course in thermodynamics.
- `test_matches_closed_form(ideal, key)` &mdash; Ideal air cycle must reproduce the analytical answer exactly.
- `test_real_machines_lower_efficiency()` &mdash; Isentropic efficiencies below 1 must reduce eta, not raise it.
- `test_energy_closes(ideal)` &mdash; First law over the whole cycle: q_in - q_out - w_net = 0.
- `test_entropy_returns_to_start(ideal)` &mdash; A closed loop must return its working fluid to the same state.
- `test_grid_convergence(nodes)` &mdash; Heat-exchanger discretisation must not move the answer.
- `test_grid_convergence_spread()` &mdash; The spread across node counts must be below 0.1 % relative.

### `test_tables.py` (204 lines)

> Regression tests for the generated tables.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `TABLES = ROOT / 'documentation' / 'latex' / 'tables'`

- `tables()` &mdash; Regenerate the tables, then read them back as text.
- `body(text)` &mdash; The data rows: between \midrule and \bottomrule, one per line.
- `test_net_power_is_plant_output_not_specific_work()` &mdash; W_net must be tens of MW, not tenths.
- `test_net_power_agrees_with_efficiency()` &mdash; W_net / Q_in must equal eta_th. The arithmetic has to close.
- `test_first_law_closes_in_the_selected_design()` &mdash; Q_in = W_net + Q_out, from the saved performance table.
- `test_absent_pump_circuit_is_a_dash_not_a_zero(tables)` &mdash; A total row with no pumped cooler must print ---, never 0.
- `test_dash_and_zero_are_distinguishable(tables)` &mdash; Somewhere in the tables both must appear, and mean different things.
- `test_repeated_layout_label_is_blank_not_dashed(tables)` &mdash; A continuation row says nothing, which is not the same as ---.
- `test_cooler_totals_are_the_sum_of_their_group(tables)` &mdash; Every total row must equal the rows above it.
- `test_tables_match_their_saved_source(tables)` &mdash; Spot-check each table against the CSV it claims to read.
- `test_every_table_has_data(tables)` &mdash; Every table the generator declares must exist and carry rows.

### `test_validation.py` (33 lines)

> The external-validation suite, as assertions.

- `test_literature_validation()` &mdash; 9 checks against Dostal (2004) and Kim (2018). External reference.
- `test_exergy_verification()` &mdash; 16 internal consistency checks. NOT external validation.

### `validate_exergy.py` (159 lines)

> Checks on the exergy layer, in the spirit of validate_air.

- `TOL = {'zero': 1e-09, 'ideal': 1e-06, 'closure'...`

- `check(name, passed, detail='')`
- `machine_case(eta_c, eta_t)`
- `main()`

### `validate_literature.py` (158 lines)

> Check the solver against somebody else's published numbers.

- `DOSTAL_STATES = [('1', 7692.31, 32.0, 306.67, 1.3478), ('...`
- `H_TOL = 0.0005`
- `S_TOL = 0.005`
- `W_TOL = 0.05`
- `ETA_TOL = 0.002`

- `check(name, ok, detail)`
- `properties()`
- `machines()`
- `whole_cycle()`
- `main()`

## `tools/`

Document generators. They read the repository and the saved results; they never solve anything themselves.


### `__init__.py` (0 lines)

- *(no module-level definitions)*

### `check_consistency.py` (246 lines)

> Check every number asserted in the documents against saved results.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `DOCS = {'report': ROOT / 'reports' / 'final_repo...`

- `rows_by(study, stem, key)`
- `checks()` &mdash; Every check: (description, computed value, tolerance, format).
- `prose_scan()` &mdash; Flag any document number that no saved result supports.
- `main()`

### `make_architecture.py` (324 lines)

> Generate documentation/architecture.md: the file tree, annotated.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `OUT = ROOT / 'documentation' / 'architecture.md'`
- `TREE = ('cycles', 'brayton_cycle', 'project', 't...`
- `SKIP_DIRS = {'__pycache__', '.git'}`
- `SKIP_FILES = {'desktop.ini'}`
- `SKIP_SUFFIX = {'.aux', '.fdb_latexmk', '.fls', '.log', ...`
- `NO_PARSE = ('documentation/latex/code',)`
- `PURPOSE = {'cycles': 'The solver. Generic: knows no...`

- `signature(fn)` &mdash; Render a def's arguments the way the source writes them.
- `summary(node)` &mdash; First line of the docstring, which is where the point always is.
- `clip(text, n)`
- `api(path)` &mdash; Every public name a module defines, with its signature.
- `walk(base)` &mdash; Directories depth-first, each with its files, both sorted.
- `one_liner(path)` &mdash; A few words on what a file is, for the tree at the top.
- `tree(base, prefix='')` &mdash; The classic box-drawing tree, files annotated.
- `registry()` &mdash; Layouts and cases as they actually register at import.
- `render()`
- `main()`

### `make_baseline.py` (51 lines)

> Write the regression baseline: every case, its key numbers, as committed.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `OUT = ROOT / 'tests' / 'baseline.json'`
- `KEYS = ('eta_th', 'w_net', 'q_in', 'q_out', 'bwr...`

- `collect()`
- `main()`

### `make_code_snippets.py` (154 lines)

> Extract the code excerpts that appear in the theory document.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `OUT = ROOT / 'documentation' / 'latex' / 'code'`
- `FUNCTIONS = {'isentropic': ('cycles/physics/isentropi...`
- `FRAGMENTS = {'hx_spec': ('cycles/blocks/heat_exchange...`
- `WHOLE = {'layout_recompression': 'brayton_cycle/r...`

- `strip_docstring(src)` &mdash; Drop the leading docstring: the surrounding prose already says it.
- `pull_functions(path, names, keep_doc=False)`
- `pull_fragment(path, start, end)`
- `pull_whole(path)` &mdash; Whole file, minus the module docstring and __future__ import.
- `main()`

### `make_figures.py` (227 lines)

> Regenerate the data behind the figures in the theory document.

- `OUT = pathlib.Path(__file__).resolve().parents[...`

- `_dump_profile(path, profile, q_total)` &mdash; A heat exchanger temperature profile, x rescaled to absolute duty.
- `main()`
- `deliverable_plots(OUT)` &mdash; Translate saved study output into pgfplots tables.

### `make_registers.py` (266 lines)

> Generate the study, validation and traceability registers.

- `ROOT = pathlib.Path(__file__).resolve().parents[1]`
- `RESULTS = ROOT / 'results'`
- `OUT = ROOT / 'documentation' / 'registers.md'`
- `CONSUMED_BY = {'layout_comparison': ('Report §3, Tables...`
- `STATUS = {'layout_comparison': ('VERIFIED', 'all f...`
- `VALIDATION = [('Solver numerics', 'VALIDATED', 'Air-st...`
- `TRACEABILITY = [('Obj 1: maximise thermal efficiency', '...`

- `manifests()`
- `main()`

### `make_tables.py` (303 lines)

> Generate every numerical table in the documents from saved results.

- `OUT = pathlib.Path(__file__).resolve().parents[...`
- `NOT_APPLICABLE = object()`
- `_TEX = {'\\': '\\textbackslash{}', '&': '\\&', '...`
- `TABLES = {'layout_comparison': layout_comparison, ...`

- `escape(text)` &mdash; Make a data string safe in LaTeX text mode.
- `fmt(v, spec)`
- `table(path, align, header, rows, cols, specs, rules=())` &mdash; Write one booktabs tabular.
- `layout_comparison()`
- `total_conductance()`
- `coolers()`
- `water_sweep()`
- `intercooling()`
- `partial_cooling()`
- `state_points()` &mdash; Appendix A's centrepiece: the recommended cycle, state by state.
- `performance()`
- `pareto_front()`
- `exergy_components()` &mdash; Destruction by component for one layout, for the teaching chapter.
- `exergy_balance()`
- `tolerance_sensitivity()`
- `main()`

## `results/`

Saved study outputs. One directory per study, each with a manifest naming the script and command that wrote it.

- **`README.md`** &mdash; 4,458 bytes

## `results/cooling/`

- **`manifest.json`** &mdash; 1,584 bytes
- **`per_cooler.csv`** &mdash; 408 bytes
- **`water_sweep.csv`** &mdash; 465 bytes

## `results/exergy/`

- **`balance.csv`** &mdash; 394 bytes
- **`by_component.csv`** &mdash; 2,040 bytes
- **`manifest.json`** &mdash; 1,555 bytes

## `results/intercooling/`

- **`manifest.json`** &mdash; 1,956 bytes
- **`pressure_sweep.csv`** &mdash; 588 bytes

## `results/layout_comparison/`

- **`layouts.csv`** &mdash; 536 bytes
- **`manifest.json`** &mdash; 1,539 bytes

## `results/multi_objective/`

- **`candidates.csv`** &mdash; 8,699 bytes
- **`manifest.json`** &mdash; 2,874 bytes
- **`pareto_front.csv`** &mdash; 1,241 bytes

## `results/parameter_sweeps/`

- **`manifest.json`** &mdash; 1,438 bytes
- **`pressure_sweep.csv`** &mdash; 269 bytes
- **`split_fraction_sweep.csv`** &mdash; 224 bytes

## `results/partial_cooling/`

- **`manifest.json`** &mdash; 2,074 bytes
- **`pressure_sweep.csv`** &mdash; 502 bytes
- **`split_sweep.csv`** &mdash; 506 bytes

## `results/selected_design/`

- **`manifest.json`** &mdash; 1,703 bytes
- **`performance.csv`** &mdash; 270 bytes
- **`state_points.csv`** &mdash; 520 bytes
- **`ts_branch.csv`** &mdash; 85 bytes
- **`ts_loop.csv`** &mdash; 219 bytes

## `results/tolerance_sensitivity/`

- **`knee_stability.csv`** &mdash; 243 bytes
- **`manifest.json`** &mdash; 2,789 bytes
- **`mass_propagation.csv`** &mdash; 293 bytes
- **`sweep.csv`** &mdash; 1,032 bytes

## `documentation/`

The explanation, and the machinery that keeps it honest.

- **`SMR_sCO2_Brayton_Problem_Statement.pdf`** &mdash; 326,735 bytes
- **`architecture.md`** &mdash; 60,605 bytes
- **`migration_table.md`** &mdash; 4,528 bytes
- **`project_tracker.md`** &mdash; 91,400 bytes
- **`registers.md`** &mdash; 18,852 bytes
- **`theory_and_implementation.pdf`** &mdash; 947,192 bytes
- **`usage.md`** &mdash; 24,903 bytes

## `documentation/latex/`

Source of the theory document.


### `build.py` (58 lines)

> Rebuild the theory document.

- `HERE = Path(__file__).resolve().parent`
- `ROOT = HERE.parents[1]`
- `TEX = 'theory_and_implementation.tex'`
- `PDF = 'theory_and_implementation.pdf'`

- `run(cmd, cwd)`
- `main(argv)`
- **`theory_and_implementation.pdf`** &mdash; 947,192 bytes
- **`theory_and_implementation.tex`** &mdash; 227,373 bytes

## `documentation/latex/code/`

Code excerpts, extracted from the real source by make_code_snippets. Never hand-edited, so they cannot drift.

- **`bisect.py`** &mdash; 656 bytes
- **`case_baseline.py`** &mdash; 1,028 bytes
- **`circuit_models.py`** &mdash; 886 bytes
- **`compressor.py`** &mdash; 1,079 bytes
- **`coolant_size.py`** &mdash; 3,075 bytes
- **`coolant_specs.py`** &mdash; 246 bytes
- **`dominance.py`** &mdash; 535 bytes
- **`duty_limits.py`** &mdash; 486 bytes
- **`exergy_balance.py`** &mdash; 444 bytes
- **`exergy_specific.py`** &mdash; 470 bytes
- **`feasible.py`** &mdash; 2,012 bytes
- **`fixed_outlets.py`** &mdash; 114 bytes
- **`flow_rules.py`** &mdash; 274 bytes
- **`hx_profile.py`** &mdash; 718 bytes
- **`hx_seek.py`** &mdash; 185 bytes
- **`hx_spec.py`** &mdash; 1,373 bytes
- **`inlets.py`** &mdash; 363 bytes
- **`isentropic.py`** &mdash; 301 bytes
- **`knee.py`** &mdash; 679 bytes
- **`layout_recompression.py`** &mdash; 862 bytes
- **`mass_of.py`** &mdash; 1,079 bytes
- **`metrics.py`** &mdash; 782 bytes
- **`ordering.py`** &mdash; 1,322 bytes
- **`payback.py`** &mdash; 373 bytes
- **`pressure_propagate.py`** &mdash; 363 bytes
- **`relation.py`** &mdash; 346 bytes
- **`sat_guard.py`** &mdash; 290 bytes
- **`secant.py`** &mdash; 740 bytes
- **`solve_monotone.py`** &mdash; 465 bytes
- **`stream.py`** &mdash; 654 bytes
- **`subst.py`** &mdash; 376 bytes
- **`tear_guess.py`** &mdash; 438 bytes
- **`tear_loop.py`** &mdash; 719 bytes
- **`ua_sizing.py`** &mdash; 594 bytes

## `documentation/latex/data/`

Plot data, regenerated by make_figures. pgfplots reads these directly, so a rebuild always plots the current solver.

- **`cp_co2.dat`** &mdash; 3,224 bytes
- **`eta_vs_rp.dat`** &mdash; 210 bytes
- **`eta_vs_x.dat`** &mdash; 188 bytes
- **`exergy_by_layout.dat`** &mdash; 324 bytes
- **`exergy_vs_x.dat`** &mdash; 1,268 bytes
- **`pareto.dat`** &mdash; 2,025 bytes
- **`pareto_dominated.dat`** &mdash; 1,160 bytes
- **`pareto_front.dat`** &mdash; 177 bytes
- **`pareto_infeasible.dat`** &mdash; 290 bytes
- **`pareto_knee.dat`** &mdash; 68 bytes
- **`precooler_profile.dat`** &mdash; 3,236 bytes
- **`recup_profile.dat`** &mdash; 3,531 bytes
- **`ts_branch.dat`** &mdash; 66 bytes
- **`ts_path.dat`** &mdash; 204 bytes
- **`ts_recompression.dat`** &mdash; 430 bytes
- **`ua_vs_eps.dat`** &mdash; 813 bytes

## `documentation/latex/diagrams/`

- **`intercooled.tex`** &mdash; 1,262 bytes
- **`partialcooling.tex`** &mdash; 2,800 bytes
- **`pipeline.tex`** &mdash; 1,108 bytes
- **`recompression.tex`** &mdash; 2,045 bytes
- **`recuperated.tex`** &mdash; 1,028 bytes
- **`simple.tex`** &mdash; 522 bytes

## `documentation/latex/tables/`

- **`coolers.tex`** &mdash; 555 bytes
- **`exergy_balance.tex`** &mdash; 346 bytes
- **`exergy_components.tex`** &mdash; 437 bytes
- **`intercooling.tex`** &mdash; 574 bytes
- **`layout_comparison.tex`** &mdash; 386 bytes
- **`pareto_front.tex`** &mdash; 515 bytes
- **`partial_cooling.tex`** &mdash; 380 bytes
- **`performance.tex`** &mdash; 432 bytes
- **`state_points.tex`** &mdash; 750 bytes
- **`tolerances.tex`** &mdash; 881 bytes
- **`total_conductance.tex`** &mdash; 365 bytes
- **`water_sweep.tex`** &mdash; 486 bytes
