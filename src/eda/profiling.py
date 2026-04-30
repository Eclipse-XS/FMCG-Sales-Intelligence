from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
import polars as pl
from .errors import DatasetNotFoundError, UnsupportedDatasetError
from .models import DatasetIdentity

def load_dataset(path: Path) -> pl.DataFrame:
    if not path.exists(): raise DatasetNotFoundError(f"Dataset does not exist: {path}")
    if path.suffix.lower() != ".parquet": raise UnsupportedDatasetError(f"Only Parquet is supported: {path}")
    return pl.read_parquet(path)

def fingerprint(path: Path, logical_name: str, frame: pl.DataFrame | None = None) -> DatasetIdentity:
    frame = frame if frame is not None else load_dataset(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): digest.update(block)
    schema = {c: str(t) for c, t in zip(frame.columns, frame.dtypes)}
    schema_hash = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
    return DatasetIdentity(logical_name, str(path.resolve()), path.stat().st_size, digest.hexdigest(), schema_hash, frame.height, schema)

def profile(frame: pl.DataFrame, keys: list[str] | None = None, date_column: str | None = None, top_n: int = 15) -> dict[str, Any]:
    rows = frame.height
    numeric = [c for c, t in zip(frame.columns, frame.dtypes) if t.is_numeric()]
    categorical = [c for c, t in zip(frame.columns, frame.dtypes) if t in (pl.String, pl.Boolean, pl.Categorical)]
    result: dict[str, Any] = {
        "row_count": rows, "column_count": frame.width,
        "schema": {c: str(t) for c, t in zip(frame.columns, frame.dtypes)},
        "missingness": {c: {"null_count": frame[c].null_count(), "null_rate": frame[c].null_count()/rows if rows else 0} for c in frame.columns},
        "cardinality": {c: frame[c].n_unique() for c in frame.columns},
        "full_duplicate_rows": int(frame.is_duplicated().sum()),
        "business_key_duplicates": int(frame.select(keys).is_duplicated().sum()) if keys else None,
        "numeric": {}, "categorical": {},
    }
    for c in numeric:
        s = frame[c].cast(pl.Float64, strict=False).drop_nulls()
        result["numeric"][c] = ({"count": 0} if not len(s) else {
            "count": len(s), "mean": float(s.mean()), "std": float(s.std()) if len(s)>1 else 0.0,
            "min": float(s.min()), "p25": float(s.quantile(.25)), "median": float(s.median()),
            "p75": float(s.quantile(.75)), "p95": float(s.quantile(.95)), "max": float(s.max()),
            "skew": float(s.skew()) if len(s)>2 else None,
        })
    for c in categorical:
        result["categorical"][c] = frame.group_by(c).len().sort("len", descending=True).head(top_n).to_dicts()
    if date_column and date_column in frame.columns:
        dates = frame[date_column].drop_nulls()
        result["temporal"] = {"column": date_column, "min": str(dates.min()), "max": str(dates.max()), "unique_dates": dates.n_unique()}
    return result
