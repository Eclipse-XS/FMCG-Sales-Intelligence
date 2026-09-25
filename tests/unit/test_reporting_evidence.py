from pathlib import Path

from fmcg_sales_intelligence.reporting.evidence import _dataset_summary, _metric_rows


ROOT = Path(__file__).resolve().parents[2]


def test_metric_rows_preserve_nested_canonical_values() -> None:
    rows = _metric_rows({"test": {"wape": 0.25}, "selected": "model"})
    assert rows == [{"metric": "test.wape", "value": 0.25}, {"metric": "selected", "value": "model"}]


def test_dataset_summary_reads_materialized_metadata() -> None:
    rows = _dataset_summary(ROOT)
    names = {row["Dataset"] for row in rows}
    assert "forecasting_v1" in names
    assert "stockout_v1" in names
    assert all(row["Rows"] > 0 and row["Columns"] > 0 for row in rows)
