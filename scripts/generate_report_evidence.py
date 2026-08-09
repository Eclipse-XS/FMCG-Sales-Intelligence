"""Generate report/evidence from the repository's frozen state."""

from __future__ import annotations

import argparse
from pathlib import Path

from fmcg_sales_intelligence.reporting import generate_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-tests", action="store_true", help="Regenerate evidence without executing pytest.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = generate_evidence(root, run_tests=not args.skip_tests)
    print(f"Evidence generated at {output}")


if __name__ == "__main__":
    main()
