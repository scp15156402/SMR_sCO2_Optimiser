"""Saving a study's results, and recording where they came from.

Every study in this package calls `save()` exactly once, with the tables
it computed.  That writes a directory under `results/` containing the
numbers as CSV and a `manifest.json` saying what produced them.

Why this exists: a study that prints its results leaves nothing you can
check.  The numbers reach a document only by a human reading a terminal
and typing, and a typo or a stale run is then invisible.  Saving them
means the figure, the table and the report all read the same file, and
you can open that file yourself.

The manifest deliberately records a **source fingerprint** rather than a
Git commit.  There is no repository yet, and inventing a commit hash
would be worse than having none; the fingerprint is a hash of every
source file that could affect the answer, so two runs with the same
fingerprint ran the same code.  When Git exists, add the commit alongside
it -- the fingerprint stays useful because it also catches uncommitted
edits.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import pathlib
import platform
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"

# Directories whose contents can change a number. Documentation and saved
# results cannot, so they are excluded -- otherwise the fingerprint would
# change every time a result was written, which makes it useless.
SOURCE_DIRS = ("cycles", "brayton_cycle", "project")


def source_fingerprint() -> dict:
    """Hash every source file that could affect a result.

    Returns the combined hash and the file count.  Two runs agreeing on
    the hash ran identical code; disagreeing means something changed,
    even if it was never committed.
    """
    h = hashlib.sha256()
    n = 0
    for d in SOURCE_DIRS:
        for p in sorted((ROOT / d).rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            h.update(p.relative_to(ROOT).as_posix().encode())
            h.update(p.read_bytes())
            n += 1
    return {"sha256": h.hexdigest()[:16], "files": n}


def _versions() -> dict:
    out = {"python": sys.version.split()[0], "platform": platform.platform()}
    try:
        import CoolProp
        out["coolprop"] = CoolProp.__version__
    except Exception:                                    # noqa: BLE001
        out["coolprop"] = "unavailable"
    return out


def save(study: str, tables: dict, *, purpose: str, command: str,
         script: str, notes=None, inputs=None) -> pathlib.Path:
    """Write one study's results to `results/<study>/`.

    tables -- {filename_stem: list of dicts}, one CSV each. Every row of a
              table must have the same keys, which is checked here rather
              than producing a ragged file nobody notices.
    """
    out = RESULTS / study
    out.mkdir(parents=True, exist_ok=True)

    written = []
    for stem, rows in tables.items():
        if not rows:
            continue
        keys = list(rows[0])
        for i, row in enumerate(rows):
            if list(row) != keys:
                raise ValueError(
                    f"{study}/{stem}: row {i} has keys {list(row)}, "
                    f"expected {keys}")
        path = out / f"{stem}.csv"
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        written.append({"file": f"{stem}.csv", "rows": len(rows),
                        "columns": keys})

    manifest = {
        "study": study,
        "purpose": purpose,
        "script": script,
        "command": command,
        "written_utc": datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_fingerprint": source_fingerprint(),
        "environment": _versions(),
        "inputs": inputs or {},
        "outputs": written,
        "notes": notes or [],
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")

    rel = out.relative_to(ROOT)
    print(f"\nsaved to {rel}/")
    for w in written:
        print(f"  {w['file']:<28} {w['rows']:>5} rows")
    print(f"  manifest.json                source {manifest['source_fingerprint']['sha256']}")
    return out


def load(study: str, stem: str) -> list:
    """Read a saved table back. Numeric-looking fields become floats.

    This is what the plotting and reporting tools use, so that nothing
    downstream of a study ever re-solves anything.
    """
    path = RESULTS / study / f"{stem}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run the study first:\n"
            f"    python -m project.studies.{study}")
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out = {}
            for k, v in row.items():
                try:
                    out[k] = float(v)
                except (TypeError, ValueError):
                    out[k] = v
            rows.append(out)
    return rows
