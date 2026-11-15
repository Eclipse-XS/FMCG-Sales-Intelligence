from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..common.paths import sha256_file


def main():
    parser = argparse.ArgumentParser(description="Approve reviewed local canonical artifacts for executable deserialization")
    parser.add_argument("root", type=Path)
    parser.add_argument("--approve-reviewed-python-artifacts", action="store_true", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    approvals = {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(root.glob("*/models/*.joblib"))}
    if not approvals:
        parser.error("No artifacts found")
    (root / "trusted-artifacts.json").write_text(json.dumps(approvals, indent=2), encoding="utf-8")
    print(json.dumps({"approved": len(approvals), "root": str(root)}))


if __name__ == "__main__":
    main()
