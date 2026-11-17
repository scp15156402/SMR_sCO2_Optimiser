"""core/studies/run_all.py: run S1..S9 in order; commit and push after each.

    python -m core.studies.run_all [names...]

Each study runs as its own process (python -m core.studies.<name>), logging to
out/studies/<name>/run.log. A failure is recorded in that study's summary.md and
the next study starts. Only the study's own script and output folder are staged
(never git add -A, never Documents/).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDIES = ["s1_cooler_pinch", "s2_tin_drift", "s3_pressure_drop", "s4_cost_split",
           "s5_discounting", "s6_t_turb", "s7_p_high", "s8_layout1_water", "s9_tq_profiles"]


def git(*args):
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    for p in Path(ROOT, common).rglob("desktop.ini"):   # Google Drive litter in .git
        p.unlink(missing_ok=True)
    print(f"$ git {' '.join(args)}", flush=True)
    return subprocess.run(["git", *args], cwd=ROOT)


def run(name):
    folder = ROOT / "out" / "studies" / name
    folder.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print(f"\n=== {name} ({time.strftime('%H:%M')}) ===", flush=True)
    with open(folder / "run.log", "w", encoding="utf-8") as log:
        rc = subprocess.run([sys.executable, "-u", "-m", f"core.studies.{name}"], cwd=ROOT,
                            stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"}).returncode
    minutes = (time.time() - t0) / 60
    if rc != 0:
        tail = (folder / "run.log").read_bytes().decode("utf-8", "replace").splitlines()[-25:]
        note = ["", f"## FAILED (exit code {rc}, after {minutes:.1f} min)", "",
                "The study did not complete; the tail of run.log:", "", "```", *tail, "```", ""]
        summary = folder / "summary.md"
        text = summary.read_text(encoding="utf-8") if summary.exists() else f"# {name}\n"
        summary.write_text(text + "\n".join(note), encoding="utf-8", newline="\n")
    print(f"{name}: exit {rc}, {minutes:.1f} min", flush=True)
    git("add", "--", f"core/studies/{name}.py", f"out/studies/{name}")
    git("commit", "-q", "-m", f"Study {name}: {'done' if rc == 0 else 'FAILED, see summary.md'}"
        f" ({minutes:.0f} min)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    git("push", "-q", "origin", "curiostudy")
    return rc


def main(argv=None):
    names = (argv if argv is not None else sys.argv[1:]) or STUDIES
    results = {n: run(n) for n in names}
    print("\n" + "\n".join(f"{n}: {'ok' if rc == 0 else f'FAILED ({rc})'}" for n, rc in results.items()))


if __name__ == "__main__":
    main()
