import ast
import json
from pathlib import Path


def test_frozen_scientific_registry_values_are_exact():
    cores = {
        x["task"]: x
        for x in json.loads(Path("artifacts/project/modeling_registry_v1.json").read_text())["cores"]
    }
    assert cores["forecasting"]["primary_metric_value"] == 0.3778884755
    assert cores["stockout_classification"]["primary_metric_value"] == 0.2551216857
    assert cores["stockout_survival"]["primary_metric_value"] == 0.7922890233
    assert cores["segmentation"]["primary_metric_value"] == 0.3307169762
    assert cores["anomaly"]["primary_metric_value"] == 0.0241503797
    assert cores["basket"]["primary_metric_value"] == 1262
    assert cores["promotion"]["primary_metric_value"] == 0.0621638304
    assert cores["segment_assignment"]["status"] == "BLOCKED"


def test_serving_source_contains_no_training_calls():
    for path in Path("src/fmcg_sales_intelligence/serving").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        assert not any(n.func.attr in {"fit", "fit_transform"} for n in calls)


def test_technology_registry_has_required_fields():
    data = json.loads(Path("artifacts/project/technology_registry_v1.json").read_text())
    required = {
        "name",
        "category",
        "version",
        "state",
        "purpose",
        "required_for_default_stack",
        "required_for_training",
        "required_for_serving",
        "required_for_offline_analytics",
        "required_for_data_engineering",
        "required_for_observability",
        "required_for_frontend",
        "required_for_ci",
        "runtime_location",
        "configuration_paths",
        "main_source_paths",
        "health_check",
        "validation_command",
        "persistent_state",
        "credentials_required",
        "network_ports",
        "dependencies_on_other_services",
        "consumers",
        "owner_layer",
        "known_limitations",
        "planned_action",
        "evidence",
    }
    assert len(data["technologies"]) >= 25
    assert all(required <= set(item) for item in data["technologies"])


def test_mlflow_importer_has_no_training_and_is_lazy_imported():
    path = Path("src/fmcg_sales_intelligence/tracking/mlflow_tracker.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert not any(n.func.attr in {"fit", "fit_transform"} for n in calls)
