from __future__ import annotations
import json
from pathlib import Path
import polars as pl
import pytest
from fmcg_sales_intelligence.science.eda import EDAResult,run_eda
from fmcg_sales_intelligence.science.eda.comparison import compare_runs
from fmcg_sales_intelligence.science.eda.config import EDAConfig
from fmcg_sales_intelligence.science.eda.errors import IncompatibleRunsError,UnknownTaskError
from fmcg_sales_intelligence.science.eda.models import EDARequest
from fmcg_sales_intelligence.science.eda.profiling import fingerprint,profile
from fmcg_sales_intelligence.science.eda.service import EDAService
from fmcg_sales_intelligence.science.eda.storage import RunStore
from fmcg_sales_intelligence.science.eda.cli import parser

ROOT=Path(__file__).resolve().parents[2]

FORECAST=ROOT/"data/processed/forecasting/forecasting_v1.parquet"

def config(tmp_path:Path)->EDAConfig:
    return EDAConfig(report_root=tmp_path/"reports",default_paths={"forecasting":FORECAST,"stockout":ROOT/"data/processed/stockout/stockout_v1.parquet","segmentation":ROOT/"data/processed/segmentation/segmentation_v1.parquet","anomaly":ROOT/"data/processed/anomaly/anomaly_v1.parquet","basket":ROOT/"data/processed/basket/basket_v1.parquet","promotion":ROOT/"data/processed/promotion_performance/promotion_performance_v1.parquet"})

def test_public_api_structured_result_and_current_forecast_metrics():
    result=run_eda("forecasting",persist=False)
    assert isinstance(result,EDAResult)
    assert result.metrics["prediction_rows"]==86400
    assert result.metrics["complete_target_rows"]==79680
    assert result.metrics["zero_sales_rows"]==51368
    assert result.metrics["inventory_censored_rows"]==242
    json.dumps(result.to_dict())

def test_unknown_task_is_domain_error():
    with pytest.raises(UnknownTaskError):run_eda("nonsense",persist=False)

def test_explicit_dataset_override():
    result=run_eda("forecasting",FORECAST,persist=False)
    assert result.datasets[0].row_count==86400

def test_fingerprint_content_and_schema(tmp_path):
    p=tmp_path/"x.parquet";pl.DataFrame({"a":[1,None],"b":["x","y"]}).write_parquet(p)
    a=fingerprint(p,"x");b=fingerprint(p,"x")
    assert a.content_sha256==b.content_sha256 and a.schema_sha256==b.schema_sha256
    pl.DataFrame({"a":[1,2,3],"b":["x","y","z"]}).write_parquet(p)
    assert fingerprint(p,"x").content_sha256!=a.content_sha256

def test_generic_profile_semantics():
    f=pl.DataFrame({"id":[1,1,2],"date":["2024-01-01","2024-01-01","2024-01-02"],"x":[1.0,None,3.0],"cat":["a","a","b"]}).with_columns(pl.col("date").str.to_date())
    p=profile(f,["id","date"],"date")
    assert p["missingness"]["x"]=={"null_count":1,"null_rate":1/3}
    assert p["cardinality"]["cat"]==2 and p["business_key_duplicates"]==2
    assert p["temporal"]["min"]=="2024-01-01"

def test_run_storage_round_trip_latest_and_unique_ids(tmp_path):
    service=EDAService(config(tmp_path));a=service.run(EDARequest("forecasting"));b=service.run(EDARequest("forecasting"))
    assert a.run_id!=b.run_id
    store=RunStore(tmp_path/"reports");loaded=store.load(a.run_id)
    assert loaded.metrics==a.to_dict()["metrics"] and store.latest("forecasting").run_id==b.run_id
    assert len(store.list("forecasting"))==2
    assert all("C:/Users" not in x.path.replace("\\","/") for x in b.artifacts)

def test_same_data_run_comparison(tmp_path):
    service=EDAService(config(tmp_path));a=service.run(EDARequest("forecasting",persist=False));b=service.run(EDARequest("forecasting",persist=False))
    c=compare_runs(a,b)
    assert c.identical_data and not c.schema["added_columns"]
    assert c.metric_changes["prediction_rows"]["absolute_delta"]==0

def test_comparison_detects_schema_and_metric_change(tmp_path):
    service=EDAService(config(tmp_path));a=service.run(EDARequest("forecasting",persist=False));b=service.run(EDARequest("forecasting",persist=False))
    b.datasets[0].schema["new_column"]="Int64";b.metrics["prediction_rows"]+=1
    c=compare_runs(a,b)
    assert c.schema["added_columns"]==["new_column"]
    assert c.metric_changes["prediction_rows"]["absolute_delta"]==1

def test_incompatible_comparison_rejected():
    with pytest.raises(IncompatibleRunsError):compare_runs(run_eda("forecasting",persist=False),run_eda("stockout",persist=False))

def test_report_generated_from_result(tmp_path):
    result=EDAService(config(tmp_path)).run(EDARequest("forecasting"))
    directory=tmp_path/"reports"/"runs"/result.run_id
    assert (directory/"report.md").exists() and (directory/"metrics.json").exists() and (directory/"manifest.json").exists()
    assert result.run_id in (directory/"report.md").read_text(encoding="utf-8")

def test_cli_contract_parses_required_commands():
    assert parser().parse_args(["run","--task","forecasting"]).command=="run"
    assert parser().parse_args(["list-runs"]).command=="list-runs"
    assert parser().parse_args(["show-run","abc"]).run_id=="abc"
    assert parser().parse_args(["compare","a","b"]).run_b=="b"
