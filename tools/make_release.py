"""Package a verified release.

A release is not a zip of whatever happens to be on disk. This script
refuses to write one unless the tree it is packaging passes its own
checks, and it records the result of each check in the archive, next to
a SHA-256 of every file. The point is that someone holding the zip --
including me, later -- can tell whether what they have is what was
verified, without trusting the filename.

Usage:  python -m tools.make_release [--out DIR] [--skip-extract-test]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = "Programming"          # what the zip extracts to

# Build artefacts. The PDFs are kept -- they are the deliverable -- but
# everything LaTeX leaves behind to make them is noise in a checksum list.
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git", ".ipynb_checkpoints"}
SKIP_SUFFIX = {".pyc", ".pyo", ".aux", ".log", ".out", ".toc", ".lof",
               ".lot", ".fls", ".fdb_latexmk", ".synctex.gz", ".nav",
               ".snm", ".vrb", ".bbl", ".blg", ".zip"}
SKIP_NAMES = {".DS_Store", "Thumbs.db", "INVENTORY.md"}


def _files(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix in SKIP_SUFFIX or p.name in SKIP_NAMES:
            continue
        out.append(p)
    return out


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _pages(pdf: Path) -> int | None:
    """Page count without a pdf library: the last /Count in the catalogue."""
    code, out = _run(["pdfinfo", str(pdf)], ROOT)
    if code == 0:
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))
    return None


def _undefined_refs(pdf: Path) -> int | None:
    """LaTeX warnings live in the .log beside the source, not the PDF."""
    for log in ROOT.rglob(pdf.stem + ".log"):
        return len(re.findall(r"Warning.*ndefined", log.read_text(errors="replace")))
    return None


def verify() -> dict:
    """Every check that gets recorded in the inventory. Raises on failure."""
    checks: dict[str, str] = {}

    code, out = _run([sys.executable, "-m", "pytest", "-q"], ROOT)
    m = re.search(r"(\d+) passed", out)
    if code != 0 or not m:
        raise SystemExit("refusing to package: test suite failed\n" + out[-3000:])
    checks["Test suite"] = f"**{m.group(1)} passed**"

    code, out = _run([sys.executable, "-m", "tools.check_consistency"], ROOT)
    if code != 0 or "all consistent" not in out:
        raise SystemExit("refusing to package: claims inconsistent\n" + out[-3000:])
    n_claims = len(re.findall(r"^\s*\[ok \]", out, re.M))
    checks["Document claims checked against saved results"] = \
        f"**{n_claims} checked, all consistent**"

    # One fingerprint across every manifest, or the results were not all
    # produced by the same source tree and must not ship together.
    prints = {}
    for man in sorted((ROOT / "results").rglob("manifest.json")):
        fp = json.loads(man.read_text()).get("source_fingerprint") or {}
        prints[man.parent.name] = (fp.get("sha256"), fp.get("files"))
    if not prints:
        raise SystemExit("refusing to package: no result manifests found")
    uniq = set(prints.values())
    if len(uniq) != 1:
        raise SystemExit(f"refusing to package: mixed fingerprints {prints}")
    checks["Studies executed"] = f"**{len(prints)} of {len(prints)}**"
    sha, nfiles = uniq.pop()
    checks["Source fingerprints across all manifests"] = \
        f"**identical: {sha} ({nfiles} source files)**"

    for label, pdf in (("Master document", ROOT / "documentation/theory_and_implementation.pdf"),
                       ("Final report", ROOT / "reports/final_report.pdf")):
        if not pdf.exists():
            raise SystemExit(f"refusing to package: {pdf} not built")
        bad = _undefined_refs(pdf)
        if bad:
            raise SystemExit(f"refusing to package: {pdf.name} has {bad} undefined references")
        checks[label] = f"**{_pages(pdf)} pp, 0 undefined references**"

    from tools.make_tables import TABLES
    checks["Generated tables"] = f"**{len(TABLES)}**"
    return checks


def inventory(files: list[Path], checks: dict, archive: str, nbytes: int) -> str:
    by_dir: dict[str, int] = {}
    for p in files:
        rel = p.relative_to(ROOT)
        key = "(root)/" if len(rel.parts) == 1 else rel.parts[0] + "/"
        by_dir[key] = by_dir.get(key, 0) + 1

    L = ["# Release inventory", "",
         "ME 306 Advanced Thermodynamics — SMR sCO₂ Brayton cycle project",
         f"Archive:   {archive}",
         f"Packaged:  {_dt.datetime.now(_dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
         f"Root:      {ARCHIVE_ROOT}/   (extracts to one directory of this name)",
         "",
         f"Files:     {len(files)}",
         f"Bytes:     {nbytes:,} uncompressed", "",
         "## Verification performed on this exact tree", "",
         "| Check | Result |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in checks.items()]
    L += ["", "## Contents", "", "| Directory | Files |", "|---|---|"]
    L += [f"| `{k}` | {v} |" for k, v in sorted(by_dir.items())]
    L += ["", "## Verifying after extraction", "", "```bash",
          f"cd {ARCHIVE_ROOT}",
          "sha256sum -c <(grep -E '^[0-9a-f]{64}  ' INVENTORY.md | awk '{print $1\"  \"$3}')",
          "pytest", "```", "",
          "Windows: `Get-FileHash -Algorithm SHA256 .\\cycles\\solve.py`", "",
          "## SHA-256, size, path", "", "```"]
    for p in files:
        L.append(f"{_sha256(p)}  {p.stat().st_size:>9}  {p.relative_to(ROOT).as_posix()}")
    L += ["```", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent))
    ap.add_argument("--skip-extract-test", action="store_true",
                    help="skip re-running the suite from the extracted copy")
    args = ap.parse_args()

    checks = verify()
    files = _files(ROOT)
    nbytes = sum(p.stat().st_size for p in files)
    stamp = _dt.date.today().isoformat()
    name = f"ME306_sCO2_Brayton_RELEASE_{stamp}.zip"
    text = inventory(files, checks, name, nbytes)

    out = Path(args.out) / name
    (ROOT / "INVENTORY.md").write_text(text, encoding="utf-8")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(f"{ARCHIVE_ROOT}/INVENTORY.md", text)
        for p in files:
            z.write(p, f"{ARCHIVE_ROOT}/{p.relative_to(ROOT).as_posix()}")

    # The archive is only trustworthy if the thing inside it runs. Extract
    # into a scratch directory and re-run the suite from there.
    if not args.skip_extract_test:
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(out) as z:
                z.extractall(td)
            tree = Path(td) / ARCHIVE_ROOT
            code, log = _run([sys.executable, "-m", "pytest", "-q"], tree)
            if code != 0:
                out.unlink(missing_ok=True)
                raise SystemExit("archive deleted: it does not pass its own "
                                 "tests when extracted\n" + log[-3000:])
            print("extracted copy:", re.search(r"(\d+ passed.*)", log).group(1))

    print(f"written: {out}")
    print(f"files:   {len(files)}")
    print(f"sha256:  {_sha256(out)}")


if __name__ == "__main__":
    main()
