"""Generate the study, validation and traceability registers.

Three registers, one generated file. They are generated rather than
written because two of the three are already recorded elsewhere in
machine-readable form -- the study register in the run manifests, the
traceability chain in the manifests plus a mapping kept here -- and a
hand-maintained copy of a machine-readable fact goes stale.

The validation register is the exception: what a piece of evidence
*demonstrates* is a judgement, so it lives in VALIDATION below and is
the only hand-written part.

The decision record is deliberately not here. Decisions, with their
reasoning, are in `documentation/project_tracker.md`, which is an
append-only log written as the work happened. Copying them into a
second file would duplicate without adding anything.

    python -m tools.make_registers
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "documentation" / "registers.md"

# Which document sections consume each study. Not derivable: it is a
# statement about two documents, and no file records it.
CONSUMED_BY = {
    "layout_comparison":     ("Report §3, Tables 1-2", "Tech §9.3"),
    "parameter_sweeps":      ("Report §6.1-6.2, Figs 3-4", "Tech §9.4"),
    "partial_cooling":       ("Report §3.4, Table 6", "Tech §9.5"),
    "intercooling":          ("Report §3.3, Table 5", "Tech §9.6"),
    "cooling":               ("Report §4.3, Tables 7-8", "Tech §9.7"),
    "exergy":                ("Report §5, Table 9", "Tech §9.8"),
    "multi_objective":       ("Report §6.4, Figs 5-6, Table 10",
                              "Tech §9.9"),
    "selected_design":       ("Report §7, Table 11, Fig 7, App A.1",
                              "Tech §9.10"),
    "tolerance_sensitivity": ("Report §8.2, App A.2", "Tech §9.11"),
}

# What each study's verification status rests on. A status without
# evidence is an opinion.
STATUS = {
    "layout_comparison":     ("VERIFIED", "all four layouts converge; "
                              "energy closes to 2e-14"),
    "parameter_sweeps":      ("VERIFIED", "every point a converged solve; "
                              "non-solving points recorded"),
    "partial_cooling":       ("VERIFIED", "interior optimum found; two "
                              "non-solving points explained physically"),
    "intercooling":          ("VERIFIED", "monotone to the no-intercooler "
                              "limit, which is the recuperated baseline"),
    "cooling":               ("VERIFIED", "pinch floor reproduces "
                              "T_CO2,out - T_water,in exactly"),
    "exergy":                ("TESTED", "balance closes to ~1e-9 of exergy "
                              "supplied; 16 checks in tests/"),
    "multi_objective":       ("VERIFIED", "dominance and knee tested; the "
                              "*selection* is unvalidated by nature"),
    "selected_design":       ("VERIFIED", "rebuilt design reproduces the "
                              "recorded efficiency; first law closes"),
    "tolerance_sensitivity": ("VERIFIED", "9.6e-6 points across all "
                              "settings; same knee at 25/100/400 nodes"),
}

VALIDATION = [
    ("Solver numerics", "VALIDATED", "Air-standard Brayton vs the closed "
     "form, 4.6e-16", "tests/test_solver.py",
     "The block equations, passes and tear are right. Says nothing about "
     "CO2."),
    ("CO2 properties", "VALIDATED", "Dostal's state table, 0.002 % on "
     "enthalpy", "tests/test_validation.py",
     "The equation of state as used here, at these states. Three entropy "
     "disagreements were traced to errors in his table."),
    ("Whole cycle", "VALIDATED", "Kim (2018): 44.669 % vs 44.670 %, and "
     "his optimum found independently in two directions",
     "tests/test_validation.py",
     "The strongest evidence here. Matching an optimum means the model's "
     "derivatives are right, not just one value."),
    ("Energy closure", "VERIFIED", "First law closes to 2e-14 of q_in",
     "tests/test_solver.py", "Arithmetic, not physics."),
    ("Discretisation", "VERIFIED", "UA converges; 100 nodes within "
     "0.003 % of 400", "project/studies/tolerances.py",
     "Efficiency and UA converge at different rates; only UA moves."),
    ("Exergy", "TESTED", "16 internal checks; balance closes to ~1e-9",
     "tests/test_validation.py",
     "Self-consistency. No external reference was available, so this is "
     "not validation."),
    ("Case regression", "TESTED", "All 17 cases solve against a committed "
     "baseline", "tests/test_regression.py",
     "Catches regressions. Cannot catch a model that was always wrong."),
    ("Table generation", "TESTED", "9 checks, one per defect found while "
     "writing the generator", "tests/test_tables.py",
     "Includes the specific-work conversion and the ---/blank/zero "
     "distinction."),
    ("Document numbers", "VERIFIED", "29 load-bearing claims checked "
     "against results/", "tools/check_consistency.py",
     "Plus a scan for efficiency figures with no saved source."),
    ("Mass model", "UNVALIDATED", "2.5 kg per kW/K, the brief's "
     "assumption", "project/assessment/mass.py",
     "Applied consistently and sensitivity-checked. Nothing external "
     "exists to test it against."),
    ("Cost model", "UNVALIDATED", "US$250/kg, US$70/MWh, the brief's "
     "proxy", "project/assessment/cost.py",
     "No fuel, O&M, financing, discounting or civil works."),
    ("Design selection", "UNVALIDATED", "Knee rule, equal weights",
     "project/assessment/moo.py",
     "The rule is implemented correctly and tested. That its output is "
     "the right engineering choice is not something a test establishes."),
]

# Requirement -> implementation -> study -> where it is answered.
TRACEABILITY = [
    ("Obj 1: maximise thermal efficiency", "cycles/solve.py metrics",
     "parameter_sweeps, multi_objective", "Report §6"),
    ("Obj 2: minimise PCS mass and volume",
     "project/assessment/mass.py", "multi_objective", "Report §6.4, §7"),
    ("Obj 3: minimise cost proxy", "project/assessment/cost.py",
     "multi_objective", "Report §7.2"),
    ("Obj 4: maximise inlet margin",
     "project/assessment/metrics.py compressor_inlets",
     "multi_objective", "Report §6.3, §7"),
    ("Reported: second-law efficiency",
     "project/assessment/metrics.py", "exergy, selected_design",
     "Report §5"),
    ("Constraint: inlet >= 32 degC, >= 7.7 MPa",
     "project/assessment/moo.py CONSTRAINTS", "multi_objective",
     "Report §6.4, §8.3"),
    ("Constraint: recuperator pinch >= 5 K", "cycles/specs.py Pinch",
     "all", "Report §2.2"),
    ("Constraint: P <= 20 MPa", "project/assessment/moo.py",
     "parameter_sweeps", "Report §6.1"),
    ("Constraint: turbine inlet <= 500 degC", "project/cases/",
     "all", "Report §1"),
    ("Constraint: split <= 0.5", "project/assessment/moo.py",
     "multi_objective", "Report §6.2"),
    ("Deliverable: T-s diagram of chosen cycle",
     "project/studies/selected_design.py", "selected_design",
     "Report Fig 7"),
    ("Deliverable: efficiency vs pressure ratio",
     "project/studies/sweeps.py", "parameter_sweeps", "Report Fig 3"),
    ("Deliverable: efficiency vs split fraction",
     "project/studies/sweeps.py", "parameter_sweeps", "Report Fig 4"),
    ("Deliverable: Pareto plots",
     "project/assessment/moo.py", "multi_objective", "Report Figs 5-6"),
    ("Deliverable: feasible set after filtering",
     "project/assessment/moo.py feasible", "multi_objective",
     "Report §6.4"),
    ("Deliverable: final justification", "--", "multi_objective",
     "Report §7"),
    ("R1 turbine", "cycles/blocks/turbine.py", "layout_comparison",
     "Report §4.1"),
    ("R2 compressors", "cycles/blocks/compressor.py",
     "parameter_sweeps, intercooling", "Report §4.1, §6.3"),
    ("R3 recuperators", "cycles/physics/hx_*.py", "layout_comparison",
     "Report §4.2"),
    ("R4 precooler and heat rejection", "cycles/physics/coolant.py",
     "cooling, partial_cooling", "Report §4.3, §3.4"),
    ("R5 integration and compactness",
     "project/assessment/", "multi_objective", "Report §6-7"),
]


def manifests():
    out = {}
    for m in sorted(RESULTS.rglob("manifest.json")):
        d = json.loads(m.read_text())
        out[d["study"]] = d
    return out


def main() -> int:
    man = manifests()
    if not man:
        print("no manifests found -- run the studies first")
        return 1

    L = ["# Registers", "",
         "Generated by `python -m tools.make_registers`. The study and",
         "traceability registers are read from the run manifests; the",
         "validation register's judgements are hand-written in that",
         "script. Do not edit this file.", "",
         "The decision record is **not** here: decisions and their",
         "reasoning are in `project_tracker.md`, written as the work",
         "happened. A second copy would duplicate without adding.", "",
         "---", "", "## 1. Study register", ""]

    fps = {d["source_fingerprint"]["sha256"] for d in man.values()}
    L += [f"{len(man)} studies. Source fingerprints: "
          + ("**all identical** — every result came from one source "
             "state." if len(fps) == 1 else
             f"**{len(fps)} distinct** — results were produced at "
             f"different source states and are not a single snapshot."),
          ""]

    for name, d in sorted(man.items()):
        status, evidence = STATUS.get(name, ("UNKNOWN", "--"))
        report, tech = CONSUMED_BY.get(name, ("--", "--"))
        fp = d["source_fingerprint"]
        L += [f"### {name}", "",
              f"- **Purpose** — {d['purpose']}",
              f"- **Entry point** — `{d['script']}`",
              f"- **Command** — `{d['command']}`",
              f"- **Inputs** — " + ", ".join(
                  f"`{k}`={v}" for k, v in list(d["inputs"].items())[:6]),
              f"- **Outputs** — " + ", ".join(
                  f"`results/{name}/{o['file']}` ({o['rows']} rows)"
                  for o in d["outputs"]),
              f"- **Manifest** — `results/{name}/manifest.json`, written "
              f"{d['written_utc']}",
              f"- **Source fingerprint** — `{fp['sha256'][:16]}` "
              f"over {fp['files']} files",
              f"- **Consumed by** — {report}; {tech}",
              f"- **Status** — **{status}**: {evidence}", ""]
        if d.get("notes"):
            L += ["  Caveats recorded with the result:", ""]
            L += [f"  - {n}" for n in d["notes"]] + [""]

    L += ["---", "", "## 2. Validation register", "",
          "*Validated* means agreement with an independent reference.",
          "*Tested* means an automated check passes. *Verified* means the",
          "arithmetic is right. *Unvalidated* means implemented with",
          "nothing external to check against — a statement of what is",
          "known, not a criticism.", "",
          "| What | Status | Evidence | Where | What it does *not* show |",
          "|---|---|---|---|---|"]
    for what, status, ev, where, limit in VALIDATION:
        L.append(f"| {what} | **{status}** | {ev} | `{where}` | {limit} |")

    L += ["", "---", "", "## 3. Traceability matrix", "",
          "Every requirement in the problem statement, from its model to",
          "the section that answers it.", "",
          "| Requirement | Implementation | Study | Answered in |",
          "|---|---|---|---|"]
    for req, impl, study, where in TRACEABILITY:
        L.append(f"| {req} | `{impl}` | {study} | {where} |")

    L += ["", "---", "", "## 4. Known limitations", "",
          "Carried from the validation register and the studies' own",
          "recorded caveats.", "",
          "- Mass, cost, payback and the selection rest on the brief's",
          "  illustrative coefficients. Efficiency and margin do not.",
          "- Exergy totals exclude the heater, which has no boundary",
          "  temperature in the model. Layouts stay comparable; absolute",
          "  totals are partial.",
          "- Every efficiency is a design-point number. Off-design and",
          "  part-load are not modelled.",
          "- Turbomachinery mass is held constant across layouts.",
          "- Pressure drops are stated, not derived from geometry.",
          "- The 7.7 MPa inlet constraint admits two readings and they",
          "  select different layouts. The literal reading is used.",
          "- Partial cooling was swept one variable at a time, not",
          "  jointly over exhaust pressure and split fraction.", ""]

    OUT.write_text("\n".join(L) + "\n")
    print(f"written: {OUT}  ({len(L)} lines, {len(man)} studies, "
          f"{len(VALIDATION)} validation rows, "
          f"{len(TRACEABILITY)} requirements)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
