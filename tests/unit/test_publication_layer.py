import json
from pathlib import Path
import pandas as pd
import pytest

from fmcg_sales_intelligence.product.analytics.publish_scientific_results import (
    CORES,
    safe_read,
    publish_core,
)


def test_cores_definition():
    """Verify all 7 scientific cores are mapped in publication layer."""
    expected_cores = {
        "forecasting_v1",
        "stockout_classification_v1",
        "stockout_survival_v1",
        "segmentation_v1",
        "anomaly_v1",
        "basket_v1",
        "promotion_v1",
    }
    assert set(CORES.keys()) == expected_cores
    for core, file_map in CORES.items():
        assert "metrics" in file_map
        assert len(file_map) >= 2


def test_safe_read_csv(tmp_path: Path):
    test_csv = tmp_path / "test.csv"
    test_csv.write_text("a,b,c\n1,2.5,inf\n-inf,nan,5\n", encoding="utf-8")
    df = safe_read(test_csv)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Verify non-finite values are replaced with None
    assert df.iloc[0, 2] is None or pd.isna(df.iloc[0, 2])
    assert df.iloc[1, 0] is None or pd.isna(df.iloc[1, 0])
    assert df.iloc[1, 1] is None or pd.isna(df.iloc[1, 1])


def test_safe_read_json(tmp_path: Path):
    test_json = tmp_path / "test.json"
    test_json.write_text(json.dumps({"metric_a": 0.95, "nested": {"key": 1}}), encoding="utf-8")
    data = safe_read(test_json)
    assert isinstance(data, dict)
    assert data["metric_a"] == 0.95


def test_safe_read_missing_file(tmp_path: Path):
    missing_file = tmp_path / "does_not_exist.csv"
    assert safe_read(missing_file) is None


def test_safe_read_unsupported_extension(tmp_path: Path):
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported extension"):
        safe_read(bad_file)


def test_canonical_artifacts_exist_on_disk():
    """Verify that canonical artifact files defined in CORES actually exist on disk."""
    artifact_root = Path("artifacts/canonical")
    for core, files in CORES.items():
        core_dir = artifact_root / core
        assert core_dir.exists(), f"Core directory missing: {core_dir}"
        for key, rel_path in files.items():
            file_path = core_dir / rel_path
            assert file_path.exists(), f"Artifact file missing for {core}/{key}: {file_path}"


def test_publish_core_missing_core_returns_none(tmp_path: Path):
    class DummyEngine:
        pass
    result = publish_core("non_existent_core", {}, DummyEngine(), tmp_path)
    assert result is None
