import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = json.loads((ROOT / "artifacts/project/modeling_registry_v1.json").read_text(encoding="utf-8"))


def test_registry_contains_every_planned_core():
    tasks = {core["task"] for core in REGISTRY["cores"]}
    assert tasks == {"forecasting", "stockout_classification", "stockout_survival", "segmentation", "segment_assignment", "anomaly", "basket", "promotion"}


def test_segment_assignment_remains_blocked_without_fake_stage():
    core = next(core for core in REGISTRY["cores"] if core["task"] == "segment_assignment")
    assert core["status"] == "BLOCKED"
    assert not core["implemented"] and core["dvc_stage"] is None and core["canonical_artifact_path"] is None


def test_implemented_cores_have_artifacts_stages_and_valid_modes():
    modes = set(REGISTRY["execution_mode_taxonomy"])
    for core in REGISTRY["cores"]:
        assert core["recommended_execution_mode"] in modes
        if core["implemented"]:
            assert core["canonical_artifact_path"] and (ROOT / core["canonical_artifact_path"]).is_dir()
            assert core["dvc_stage"]


def test_registry_avoids_fake_production_and_causal_claims():
    serialized = json.dumps(REGISTRY).lower()
    assert "production_ready" not in serialized
    assert "causal_uplift" not in serialized
    assert all(core["status"] in {"READY", "READY_WITH_LIMITATIONS", "NOT_READY", "BLOCKED", "NOT_IMPLEMENTED"} for core in REGISTRY["cores"])
