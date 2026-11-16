"""Rebuild the theory document.

Regenerates the plot data from the solver, re-extracts the code excerpts
from the source, compiles the LaTeX, and copies the PDF one level up so it
sits beside the markdown files.

The excerpts are pulled out of the real files, never retyped, so a code
change followed by a rebuild shows the change rather than a stale listing.

    python documentation/latex/build.py            # data + compile
    python documentation/latex/build.py --no-data  # compile only

Needs a LaTeX distribution with latexmk, pgfplots, tcolorbox and tikz
(TeX Live or MiKTeX both have them).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEX = "theory_and_implementation.tex"
PDF = "theory_and_implementation.pdf"


def run(cmd, cwd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def main(argv) -> int:
    if "--no-data" not in argv:
        print("regenerating plot data from the solver...")
        if run([sys.executable, "-m", "tools.make_figures"], ROOT):
            print("could not regenerate plot data; using what is there")
        print("re-extracting code excerpts from the source...")
        if run([sys.executable, "-m", "tools.make_code_snippets"], ROOT):
            print("could not re-extract code; using what is there")

    if shutil.which("latexmk") is None:
        print("latexmk not found -- install TeX Live or MiKTeX")
        return 1

    if run(["latexmk", "-pdf", "-interaction=nonstopmode",
            "-halt-on-error", TEX], HERE):
        print("compile failed; see theory_and_implementation.log")
        return 1

    shutil.copy(HERE / PDF, HERE.parent / PDF)
    print(f"\nwritten: {HERE.parent / PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
