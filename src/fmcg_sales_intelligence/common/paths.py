from __future__ import annotations

import hashlib
import os
from pathlib import Path


PROJECT_ROOT = Path(os.getenv("FSI_PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def relative_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
