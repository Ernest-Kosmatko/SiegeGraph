"""Content-addressed evidence storage: files are copied alongside the
project database and hashed so a report can prove nothing was altered
after capture."""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


def evidence_dir(project_path: Path) -> Path:
    d = project_path.parent / f"{project_path.stem}.evidence"
    d.mkdir(exist_ok=True)
    return d


def ingest_file(project_path: Path, source: Path) -> tuple[Path, str]:
    """Copy `source` into the project's evidence store, return (new_path, sha256)."""
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    dest = evidence_dir(project_path) / f"{digest[:16]}_{source.name}"
    shutil.copy2(source, dest)
    return dest, digest
