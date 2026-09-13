from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import joblib


def load_approved_bundle(artifact: Path, approvals_path: Path):
    """Approval file is operator-owned. Verify the exact bytes being deserialized."""
    if not approvals_path.is_file():
        raise ValueError("Operator artifact approval file is required")
    approvals = json.loads(approvals_path.read_text(encoding="utf-8"))
    payload = artifact.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    key = artifact.resolve().relative_to(approvals_path.parent.resolve()).as_posix()
    if approvals.get(key) != digest:
        raise ValueError("Artifact hash is not approved by the operator")
    return joblib.load(io.BytesIO(payload))
