from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import RobustScaler

from src.modeling import run_experiment
from src.modeling.segmentation import DEFAULT_CONFIG, audit_features, canonicalize, evaluate_candidates, nearest_centroid, select_latest_snapshot

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/segmentation/segmentation_v1.parquet"

def loaded():
    cfg=yaml.safe_load(DEFAULT_CONFIG.read_text()); f=pd.read_parquet(DATA); f.snapshot_date=pd.to_datetime(f.snapshot_date)
    for c in cfg["features"]: f[c]=pd.to_numeric(f[c])
    return cfg,f

def test_latest_snapshot_and_independent_store_semantics():
    _,f=loaded(); ref,hist=select_latest_snapshot(f)
    assert len(f)==60 and f.store_id.nunique()==20 and len(ref)==20 and not ref.store_id.duplicated().any()
    assert set(ref.snapshot_date.dt.strftime("%Y-%m-%d"))=={"2024-03-30"} and len(hist)==40

def test_feature_contract_excludes_identifiers_context_and_constant():
    cfg,f=loaded(); ref,_=select_latest_snapshot(f); audit=audit_features(ref,cfg)
    assert not set(cfg["selected_features"]) & set(cfg["identifiers"]+cfg["context_only"])
    assert "active_skus_30d" not in cfg["selected_features"] and audit["unique_values"]["active_skus_30d"]==1

def test_missingness_and_robust_scaling():
    cfg,f=loaded(); ref,_=select_latest_snapshot(f); X=RobustScaler().fit_transform(ref[cfg["selected_features"]])
    assert not np.isnan(X).any() and np.allclose(np.median(X,axis=0),0)

def test_all_candidates_metrics_sizes_and_k_range():
    cfg,f=loaded(); ref,hist=select_latest_snapshot(f); sc=RobustScaler().fit(ref[cfg["selected_features"]]); c=evaluate_candidates(ref,hist,cfg,sc)
    assert set(c.algorithm)=={"kmeans","agglomerative_clustering"} and set(c.k)=={2,3,4,5} and len(c)==8
    assert c.silhouette.between(-1,1).all() and (c.davies_bouldin>=0).all() and (c.minimum_cluster_size>=1).all()

def test_deterministic_canonical_labels_and_historical_assignment():
    cfg,f=loaded(); ref,hist=select_latest_snapshot(f); sc=RobustScaler().fit(ref[cfg["selected_features"]]); X=sc.transform(ref[cfg["selected_features"]])
    from sklearn.cluster import KMeans
    a=KMeans(n_clusters=3,random_state=cfg["random_seed"],n_init=50).fit_predict(X); b=KMeans(n_clusters=3,random_state=cfg["random_seed"],n_init=50).fit_predict(X)
    ca,_=canonicalize(a,X); cb,_=canonicalize(b,X); assert np.array_equal(ca,cb)
    cent=np.vstack([X[ca==i].mean(0) for i in range(3)]); h,dist,margin=nearest_centroid(sc.transform(hist[cfg["selected_features"]]),cent)
    assert len(h)==40 and (dist>=0).all() and (margin>=0).all()

def test_public_api_artifacts_pseudo_labels_and_reload(tmp_path):
    result=run_experiment("segmentation",output_dir=tmp_path/"seg",experiment_id="test_seg",overwrite=True)
    out=Path(result["output_dir"]); labels=pd.read_parquet(out/"predictions_or_labels/store_segments.parquet")
    assert len(labels)==20 and labels.store_id.nunique()==20
    assert set(["cluster_id","segment_name","segmentation_version","label_semantics"]).issubset(labels.columns)
    assert set(labels.label_semantics)=={"PSEUDO_LABEL_NOT_GROUND_TRUTH"}
    state=joblib.load(out/"models/final_model.joblib"); assert state["features"] and state["version"]=="segmentation_v1"
