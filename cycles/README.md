# cycles

A block-based solver for closed thermodynamic power cycles.

Nothing here knows what a Brayton cycle is, or that CO2 exists. A cycle is a
list of blocks and the streams between them; a run is a `Case` giving the
numbers. sCO2, air-standard Brayton, Rankine and a Joule-Thomson cryocooler
are all layouts, not code.

## The cascade

Each layer uses only the layers below it.

```
solve.py         runs the passes, packs the Result
passes/          pressure, flow, ordering, tear
blocks/          the eight component functions
physics/         isentropic, pressure drop, HX limits, profile, UA, mixing
properties/      CoolProp, ideal gas, (tables)     numerics/  bisect, secant
```

`physics/` exists because of one rule: anything used by more than one caller
earns its own file. `hx_profile.py` is the clearest case — the solver needs
it for the pinch, and the plotting layer will need the same array for a T-Q
diagram.

## The stream

```python
Stream(fluid, P, h, flow)
```

Pressure, specific enthalpy, and the fraction of total cycle mass flow.
Temperature, entropy and density are derived, never stored.

`(P, h)` is chosen over `(P, T)` deliberately: inside a saturation dome `P`
and `T` are not independent, so `(P, T)` cannot identify a state. That one
choice is what lets this solver run Rankine cycles later without touching a
single block.

## The block contract

Every block module exports five things:

```python
TYPE                         # the name a layout file uses
INLETS / OUTLETS             # port names; MULTI_* ports carry a list
pressure_rules(params)       # -> (relations, anchors)   runs before enthalpies
flow_rule(params)            # -> Identity | Scale | Sum  runs before enthalpies
evaluate(inlets, P_out, params, props, ...) -> (outlets, extras)
```

and may optionally export `fixed_outlets(params)` for an outlet whose state
is pinned by a parameter rather than by its inlet.

Pressure and flow are declared separately from `evaluate` because both are
resolved across the whole flowsheet before any enthalpy exists. Relations are
invertible because a closed cycle needs them to be: the turbine outlet
pressure in a recuperated layout is only reachable by walking *backwards*
from the compressor inlet through the hot-side losses.

Adding a block is: write the module, import it in `blocks/__init__.py`, add
it to the list. Nothing else changes.

## The four passes

| pass | what it does |
|---|---|
| `pressure` | every stream pressure, from anchors and invertible relations. Three pressure levels (partial cooling) need no special case. |
| `flow` | every stream's share of the total mass flow. Needed before evaluation because the boundary stream may not carry all of it. |
| `ordering` | evaluation order by readiness; nominates a tear stream if the graph has a loop. |
| `tear` | successive substitution to a fixed point. Skipped entirely when the layout is acyclic. |

Simple and recuperated layouts come out acyclic and solve in one pass.
Recompression tears one stream and settles in about thirty.

## Specifications

A heat exchanger takes exactly one of these, and reports the other two:

```python
Effectiveness(0.90)   # explicit
Pinch(K(5))           # secant on effectiveness
UAperFlow(ua)         # secant on effectiveness
```

Plant size takes one of `ThermalPower` or `MassFlow`.

Which specification you give decides which loop the solver runs. That is the
whole reason the solver is built this way: Dostal fixes effectiveness or
exchanger volume, Kim fixes effectiveness or pinch, Wu fixes UA, the brief
fixes effectiveness with a pinch constraint. Same physics, four conventions.

## Performance notes

Two things keep a sweep tractable, both in `solve.py`:

- **`diagnostics=False` during the tear.** Profiles, pinches and UA cost a
  hundred property calls per exchanger and nobody reads them until the loop
  has settled. One final sweep at full resolution produces them.
- **Warm-started secant.** With a pinch or UA spec the effectiveness barely
  moves between tear iterations, so each one restarts from the last answer.
  Bisection at the same tolerance needs roughly thirty evaluations; the
  secant needs a handful.

Together these took the pinch-specified recompression case from 23 s to 5 s,
with identical results. A plain effectiveness run is 0.36 s.

## Failure handling

The solver raises almost nothing. An infeasible pinch, a temperature cross, a
non-converged tear or a negative entropy generation becomes an entry in
`result.flags` and `result.ok` goes False. A sweep of ten thousand points
must survive the bad ones.
