from __future__ import annotations

import joblib
import polars as pl
import pytest
from fastapi.testclient import TestClient
from sklearn.cluster import KMeans

from fmcg_sales_intelligence.api.app import create_app
from fmcg_sales_intelligence.serving import SegmentMembershipService


ARTIFACT = "artifacts/canonical/segmentation_v1/models/final_model.joblib"
DATA = "data/processed/segmentation/segmentation_v1.parquet"
LABELS = "artifacts/canonical/segmentation_v1/predictions_or_labels/store_segments.parquet"


def reference_row(service: SegmentMembershipService) -> tuple[dict, int]:
    labels = pl.read_parquet(LABELS).sort("store_id")
    store_id = labels[0, "store_id"]
    expected = labels[0, "cluster_id"]
    row = (
        pl.read_parquet(DATA)
        .filter(pl.col("store_id") == store_id)
        .sort("snapshot_date")
        .tail(1)
        .select(service.features)
        .to_dicts()[0]
    )
    return {"store_id": store_id, **{key: float(value) for key, value in row.items()}}, expected


def test_assignment_uses_exact_frozen_contract_without_fit(monkeypatch):
    state = joblib.load(ARTIFACT)
    service = SegmentMembershipService()
    assert service.features == state["features"]
    row, expected = reference_row(service)
    monkeypatch.setattr(KMeans, "fit", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("fit called")))
    first = service.assign([row])[0]
    second = service.assign([row])[0]
    assert first == second
    assert first["cluster_id"] == expected
    assert first["assignment_method"] == "frozen_kmeans_predict"
    assert first["scientific_status"] == "exploratory"
    assert first["taxonomy_stability"] == "limited"
    assert first["review_required"] is True
    assert not ({"probability", "confidence", "score"} & set(first))


def test_assignment_rejects_missing_unknown_and_invalid_features():
    service = SegmentMembershipService()
    row, _ = reference_row(service)
    with pytest.raises(ValueError, match="Missing required"):
        service.assign([{k: v for k, v in row.items() if k != service.features[0]}])
    with pytest.raises(ValueError, match="Unsupported"):
        service.assign([{**row, "brand": "Coca-Cola"}])
    with pytest.raises(ValueError, match="finite number"):
        service.assign([{**row, service.features[0]: float("nan")}])


def test_assignment_endpoint_is_generic_and_explicitly_exploratory():
    service = SegmentMembershipService()
    row, expected = reference_row(service)
    response = TestClient(create_app()).post("/api/v1/analytics/segments/assign", json={"rows": [row]})
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["cluster_id"] == expected
    assert item["label_semantics"] == "PSEUDO_LABEL_NOT_GROUND_TRUTH"
    assert "coca" not in str(item).lower()
