"""Build the final report.

Regenerates the tables and plot data from the saved study results, then
compiles. Nothing here solves a cycle: every number in the report comes
from `results/`, written by a study in `project/studies/`.

    python reports/build.py             # tables + data + compile
    python reports/build.py --no-data   # compile only
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEX = "final_report.tex"
PDF = "final_report.pdf"


def run(cmd, cwd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def main(argv) -> int:
    if "--no-data" not in argv:
        print("regenerating tables from saved study results...")
        if run([sys.executable, "-m", "tools.make_tables"], ROOT):
            print("could not regenerate tables -- run the studies first")
            return 1
        print("regenerating plot data...")
        if run([sys.executable, "-m", "tools.make_figures"], ROOT):
            print("could not regenerate plot data -- run the studies first")
            return 1

    if shutil.which("latexmk") is None:
        print("latexmk not found -- install TeX Live or MiKTeX")
        return 1
    if run(["latexmk", "-pdf", "-interaction=nonstopmode",
            "-halt-on-error", TEX], HERE):
        print("compile failed; see final_report.log")
        return 1
    print(f"\nwritten: {HERE / PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
