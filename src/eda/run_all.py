from __future__ import annotations
from .service import run_eda

def main() -> None:
    result=run_eda("all")
    print(f"EDA complete: run_id={result.run_id}")


if __name__ == "__main__":
    main()
