from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml
from ..engine.data import read_source


class FileAdapter:
    """Declarative CSV/Parquet adapter; complex transforms belong in reviewed code."""

    def __init__(self, mapping_path: str | Path):
        self.mapping = yaml.safe_load(Path(mapping_path).read_text(encoding="utf-8"))

    def normalize(self, contract_id: str, source: str | Path | pd.DataFrame) -> pd.DataFrame:
        frame = read_source(source)
        spec = self.mapping["datasets"][contract_id]
        columns = spec["columns"]
        missing = set(columns) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing mapped source columns: {sorted(missing)}")
        return frame[list(columns)].rename(columns=columns)
