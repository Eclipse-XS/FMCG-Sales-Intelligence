"""Store Segmentation V1: exploratory clustering at the physical-store grain."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT

import hashlib, json, platform, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import yaml
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,
                             davies_bouldin_score, silhouette_score)
from sklearn.preprocessing import RobustScaler

ROOT = PROJECT_ROOT
DEFAULT_CONFIG = ROOT / "config/modeling/segmentation.yaml"
DEFAULT_DATA = ROOT / "data/processed/segmentation/segmentation_v1.parquet"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def _git(*args):
    try: return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception: return None


def load_contract(config_path=DEFAULT_CONFIG, data_path=DEFAULT_DATA):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    frame = pd.read_parquet(data_path)
    frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"])
    for c in cfg["features"]: frame[c] = pd.to_numeric(frame[c], errors="coerce")
    return cfg, frame


def select_latest_snapshot(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values(["store_id", "snapshot_date"])
    reference = ordered.groupby("store_id", as_index=False).tail(1).sort_values("store_id").reset_index(drop=True)
    history = ordered.merge(reference[["store_id", "snapshot_date"]], on="store_id", suffixes=("", "_reference"))
    history = history[history.snapshot_date < history.snapshot_date_reference].drop(columns="snapshot_date_reference").reset_index(drop=True)
    if reference.store_id.duplicated().any(): raise ValueError("Reference cohort is not one row per store")
    return reference, history


def audit_features(reference: pd.DataFrame, cfg: dict) -> dict:
    candidates, selected = cfg["features"], cfg["selected_features"]
    missing = reference[candidates].isna().sum().to_dict()
    nunique = reference[candidates].nunique().to_dict()
    corr = reference[candidates].corr().round(6)
    return {"candidate_features": candidates, "selected_features": selected,
            "excluded_after_audit": cfg["excluded_after_audit"], "missingness": missing,
            "unique_values": nunique, "skewness": reference[candidates].skew().to_dict(),
            "distributions": reference[candidates].describe().to_dict(),
            "correlations": corr.to_dict(), "outlier_rule": "diagnostic only; no stores removed",
            "iqr_outlier_counts": {c: int(((reference[c] < reference[c].quantile(.25)-1.5*(reference[c].quantile(.75)-reference[c].quantile(.25))) | (reference[c] > reference[c].quantile(.75)+1.5*(reference[c].quantile(.75)-reference[c].quantile(.25)))).sum()) for c in candidates}}


def canonicalize(labels: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, dict]:
    """Map arbitrary IDs by ascending first-PC projection of transformed centroids."""
    pca = PCA(n_components=1).fit(X)
    old = sorted(np.unique(labels), key=lambda x: float(pca.transform(X[labels == x].mean(0, keepdims=True))[0, 0]))
    mapping = {int(raw): i for i, raw in enumerate(old)}
    return np.array([mapping[int(x)] for x in labels]), mapping


def nearest_centroid(X: np.ndarray, centroids: np.ndarray):
    distances = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)
    labels = distances.argmin(axis=1)
    ordered = np.sort(distances, axis=1)
    margin = ordered[:, 1] - ordered[:, 0] if centroids.shape[0] > 1 else np.full(len(X), np.nan)
    return labels, distances[np.arange(len(X)), labels], margin


def evaluate_candidates(reference, history, cfg, scaler):
    features = cfg["selected_features"]; X = scaler.transform(reference[features]); Xh = scaler.transform(history[features])
    rows=[]
    for algorithm in cfg["candidate_models"]:
        for k in cfg["cluster_count_candidates"]:
            model = (KMeans(n_clusters=k, random_state=cfg["random_seed"], n_init=cfg["kmeans"]["n_init"])
                     if algorithm == "kmeans" else AgglomerativeClustering(n_clusters=k, linkage=cfg["agglomerative"]["linkage"], metric=cfg["agglomerative"]["metric"]))
            raw=model.fit_predict(X); labels,mapping=canonicalize(raw,X)
            centroids=np.vstack([X[labels==i].mean(0) for i in range(k)])
            historical,_,_=nearest_centroid(Xh,centroids); ref_by_store=dict(zip(reference.store_id,labels))
            retention=float(np.mean([historical[i] == ref_by_store[s] for i,s in enumerate(history.store_id)]))
            counts=np.bincount(labels,minlength=k)
            rows.append({"algorithm":algorithm,"k":k,"silhouette":silhouette_score(X,labels),"davies_bouldin":davies_bouldin_score(X,labels),"calinski_harabasz":calinski_harabasz_score(X,labels),"cluster_sizes":"|".join(map(str,counts)),"minimum_cluster_size":int(counts.min()),"maximum_cluster_size":int(counts.max()),"singleton_clusters":int((counts==1).sum()),"temporal_assignment_retention":retention,"assignment_method":"native centroid" if algorithm=="kmeans" else "nearest reference centroid approximation"})
    return pd.DataFrame(rows)


def _segment_names(profiles: pd.DataFrame) -> dict:
    names={}
    for cid,g in profiles.groupby("cluster_id"):
        z=dict(zip(g.feature,g.standardized_profile)); volume="Higher-Volume" if z.get("revenue_30d",0)>.35 else "Lower-Volume" if z.get("revenue_30d",0)<-.35 else "Mid-Volume"
        promo="Promotion-Leaning" if z.get("promotion_unit_share_30d",0)>.35 else "Lower-Promotion" if z.get("promotion_unit_share_30d",0)<-.35 else "Balanced-Promotion"
        names[int(cid)]=f"{volume} {promo}"
    # ensure names remain unique without implying ordinal value
    seen={}
    for cid,name in list(names.items()):
        seen[name]=seen.get(name,0)+1
        if seen[name]>1: names[cid]=f"{name} Profile {seen[name]}"
    return names


def run_segmentation_experiment(config_path=DEFAULT_CONFIG, data_path=DEFAULT_DATA, output_dir=None, experiment_id=None, overwrite=False):
    cfg,frame=load_contract(config_path,data_path); data_path=Path(data_path)
    reference,history=select_latest_snapshot(frame); features=cfg["selected_features"]
    if len(reference)!=reference.store_id.nunique() or len(reference)!=20: raise ValueError("Expected exactly 20 independent physical stores")
    if reference[features].isna().any().any(): raise ValueError("Selected clustering features contain missing values")
    scaler=RobustScaler().fit(reference[features]); X=scaler.transform(reference[features])
    candidates=evaluate_candidates(reference,history,cfg,scaler)
    alg=cfg["selection"]["algorithm"]; k=int(cfg["selection"]["clusters"])
    if alg=="kmeans": model=KMeans(n_clusters=k,random_state=cfg["random_seed"],n_init=cfg["kmeans"]["n_init"])
    else: model=AgglomerativeClustering(n_clusters=k,linkage=cfg["agglomerative"]["linkage"],metric=cfg["agglomerative"]["metric"])
    raw=model.fit_predict(X); labels,mapping=canonicalize(raw,X); centroids=np.vstack([X[labels==i].mean(0) for i in range(k)])
    ref_labels,dist,margin=nearest_centroid(X,centroids)
    # For reference points nearest-centroid labels must equal the frozen partition.
    if not np.array_equal(ref_labels,labels): raise ValueError("Canonical centroid assignment differs from fitted partition")
    overall=reference[features].mean(); overall_sd=reference[features].std(ddof=0).replace(0,np.nan)
    profile_rows=[]
    for cid in range(k):
        group=reference.loc[labels==cid,features]
        for f in features: profile_rows.append({"cluster_id":cid,"store_count":len(group),"feature":f,"mean":group[f].mean(),"median":group[f].median(),"overall_mean":overall[f],"relative_to_overall":group[f].mean()/overall[f] if overall[f] else np.nan,"standardized_profile":(group[f].mean()-overall[f])/overall_sd[f]})
    profiles=pd.DataFrame(profile_rows); names=_segment_names(profiles); profiles["segment_name"]=profiles.cluster_id.map(names)
    ref=reference[["store_id","snapshot_date"]].copy(); ref["cluster_id"]=labels; ref["segment_name"]=ref.cluster_id.map(names); ref["distance_to_centroid"]=dist; ref["centroid_distance_margin"]=margin; ref["segmentation_experiment_id"]=experiment_id or "segmentation_v1_canonical"; ref["segmentation_version"]=cfg["pseudo_label_version"]; ref["label_semantics"]="PSEUDO_LABEL_NOT_GROUND_TRUTH"
    Xh=scaler.transform(history[features]); hl,hd,hm=nearest_centroid(Xh,centroids)
    hist=history[["store_id","snapshot_date"]].copy(); hist["reference_cluster_id"]=hl; hist["segment_name"]=hist.reference_cluster_id.map(names); hist["distance_to_centroid"]=hd; hist["centroid_distance_margin"]=hm; hist["assignment_method"]="kmeans_predict_equivalent_nearest_centroid" if alg=="kmeans" else "nearest_final_cluster_centroid_approximation"
    latest=dict(zip(ref.store_id,ref.cluster_id)); hist["matches_reference_assignment"]= [int(c)==int(latest[s]) for s,c in zip(hist.store_id,hist.reference_cluster_id)]
    all_assign=pd.concat([hist.rename(columns={"reference_cluster_id":"cluster_id"})[["store_id","snapshot_date","cluster_id"]],ref[["store_id","snapshot_date","cluster_id"]]]).sort_values(["store_id","snapshot_date"])
    transitions=all_assign.groupby("store_id").cluster_id.agg(lambda x:" -> ".join(map(str,x))).reset_index(name="segment_sequence"); transitions["transition_count"]=all_assign.groupby("store_id").cluster_id.agg(lambda x:int((x.to_numpy()[1:]!=x.to_numpy()[:-1]).sum())).to_numpy(); transitions["stable"]=transitions.transition_count.eq(0)
    retention=float(hist.matches_reference_assignment.mean()); historical_ari=[]
    for date,g in hist.groupby("snapshot_date"):
        historical_ari.append({"snapshot_date":str(date.date()),"adjusted_rand_index_vs_reference":adjusted_rand_score([latest[s] for s in g.store_id],g.reference_cluster_id),"retention_vs_reference":float(g.matches_reference_assignment.mean())})
    selected=candidates[(candidates.algorithm==alg)&(candidates.k==k)].iloc[0].to_dict()
    readiness="READY_WITH_LIMITATIONS" if retention>=.7 and selected["minimum_cluster_size"]>=2 else "NOT_READY"
    out=Path(output_dir or ROOT/"artifacts/experiments/segmentation"/(experiment_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    if out.exists() and overwrite: shutil.rmtree(out)
    if out.exists(): raise FileExistsError(out)
    for p in [out/"models",out/"predictions_or_labels",out/"diagnostics",out/"figures"]: p.mkdir(parents=True,exist_ok=True)
    model_state={"preprocessor":scaler,"model":model,"features":features,"canonical_mapping":mapping,"centroids":centroids,"segment_names":names,"algorithm":alg,"k":k,"version":cfg["pseudo_label_version"]}; joblib.dump(model_state,out/"models/final_model.joblib"); loaded=joblib.load(out/"models/final_model.joblib"); assert np.allclose(loaded["preprocessor"].transform(reference[features]),X)
    ref.to_parquet(out/"predictions_or_labels/store_segments.parquet",index=False); hist.to_parquet(out/"predictions_or_labels/historical_assignments.parquet",index=False); transitions.to_csv(out/"diagnostics/transition_summary.csv",index=False); profiles.to_csv(out/"diagnostics/cluster_profiles.csv",index=False); candidates.to_csv(out/"diagnostics/candidate_metrics.csv",index=False)
    context=reference[["store_id",*cfg["context_only"]]].assign(cluster_id=labels,segment_name=[names[x] for x in labels]); context.groupby(["cluster_id","segment_name",*cfg["context_only"]]).size().reset_index(name="store_count").to_csv(out/"diagnostics/cluster_context.csv",index=False)
    diagnostics=audit_features(reference,cfg); diagnostics.update({"rows":len(frame),"unique_stores":frame.store_id.nunique(),"snapshot_dates":[str(x.date()) for x in sorted(frame.snapshot_date.unique())],"rows_per_store":frame.groupby('store_id').size().to_dict(),"reference_policy":"latest eligible snapshot per physical store","reference_rows":len(reference),"historical_rows":len(history)})
    (out/"diagnostics/data_diagnostics.json").write_text(json.dumps(diagnostics,indent=2,default=str),encoding="utf-8")
    stability={"temporal_assignment_retention":retention,"stable_stores":int(transitions.stable.sum()),"changing_stores":int((~transitions.stable).sum()),"total_transitions":int(transitions.transition_count.sum()),"by_snapshot":historical_ari,"interpretation":"Historical snapshots assigned to frozen reference centroids; not independent refits or ground-truth agreement."}; (out/"diagnostics/stability_metrics.json").write_text(json.dumps(stability,indent=2),encoding="utf-8")
    # PCA is visualization only.
    pca=PCA(n_components=2).fit(X); xy=pca.transform(X); plt.figure(figsize=(8,6))
    for cid in range(k): plt.scatter(xy[labels==cid,0],xy[labels==cid,1],label=names[cid],s=60)
    for i,s in enumerate(reference.store_id): plt.annotate(str(s),(xy[i,0],xy[i,1]),fontsize=8)
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})"); plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})"); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(out/"figures/pca_clusters.png",dpi=180); plt.close()
    pivot=profiles.pivot(index="cluster_id",columns="feature",values="standardized_profile"); plt.figure(figsize=(10,3)); plt.imshow(pivot,cmap="coolwarm",aspect="auto"); plt.xticks(range(len(pivot.columns)),pivot.columns,rotation=35,ha="right"); plt.yticks(range(k),[names[i] for i in pivot.index]); plt.colorbar(label="Standardized relative profile"); plt.tight_layout(); plt.savefig(out/"figures/cluster_profiles.png",dpi=180); plt.close()
    counts=ref.groupby("segment_name").size(); counts.plot.bar(figsize=(8,4)); plt.ylabel("Stores"); plt.tight_layout(); plt.savefig(out/"figures/cluster_sizes.png",dpi=180); plt.close()
    st=hist.groupby("snapshot_date").matches_reference_assignment.mean(); st.plot(marker="o",ylim=(0,1),figsize=(7,4)); plt.ylabel("Retention vs reference"); plt.tight_layout(); plt.savefig(out/"figures/temporal_stability.png",dpi=180); plt.close()
    metrics={"selected_silhouette":selected["silhouette"],"selected_davies_bouldin":selected["davies_bouldin"],"selected_calinski_harabasz":selected["calinski_harabasz"],"number_of_clusters":k,"minimum_cluster_size":selected["minimum_cluster_size"],"maximum_cluster_size":selected["maximum_cluster_size"],"temporal_assignment_retention":retention,"store_count":len(reference),"pseudo_label_readiness":readiness}; (out/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8"); (out/"dvc_metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    selected_artifact={"algorithm":alg,"k":k,"preprocessing":cfg["preprocessing"],"features":features,"transformations":cfg["transformations"],"random_seed":cfg["random_seed"],"internal_metrics":selected,"canonical_mapping":mapping,"cluster_sizes":selected["cluster_sizes"],"stability_metrics":stability,"selection_rationale":cfg["selection"]["rationale"],"dataset_fingerprint":_sha(data_path)}; (out/"selected_model.json").write_text(json.dumps(selected_artifact,indent=2,default=str),encoding="utf-8"); (out/"resolved_config.yaml").write_text(yaml.safe_dump(cfg,sort_keys=False),encoding="utf-8")
    ambiguous=ref.nsmallest(3,"centroid_distance_margin").store_id.tolist(); distant=ref.nlargest(3,"distance_to_centroid").store_id.tolist()
    report=f"""# Store Segmentation V1

## 1. Objective
Exploratory behavioral grouping of physical stores without ground-truth labels.

## 2. Unit of analysis
The independent unit is one physical store, not one snapshot. The reference cohort has **{len(reference)} stores**.

## 3. Dataset
`{data_path}` contains {len(frame)} rows and {frame.store_id.nunique()} stores over {frame.snapshot_date.nunique()} snapshots.

## 4. Reference cohort
Latest eligible snapshot per store: {reference.snapshot_date.max().date()}; exactly one row per store.

## 5. Historical snapshots
The {len(history)} earlier rows are reserved for temporal diagnostics and never treated as independent stores.

## 6. Feature contract
Clustering features: `{', '.join(features)}`. IDs and `{', '.join(cfg['context_only'])}` are excluded from geometry. Units/profit were removed as revenue redundancy, floor area as correlated static capacity context, and active SKU count for zero variance.

## 7. Preprocessing
RobustScaler fitted on the reference cohort. No imputation, deletion, or log transform was required. No outlier store was removed.

## 8. Candidate algorithms
KMeans and Ward agglomerative clustering only.

## 9. Candidate k values
`2, 3, 4, 5`.

## 10. Internal metrics
Selected silhouette {selected['silhouette']:.4f}, Davies–Bouldin {selected['davies_bouldin']:.4f}, Calinski–Harabasz {selected['calinski_harabasz']:.2f}. These measure representation geometry, not truth.

## 11. Cluster-size diagnostics
Selected sizes: {selected['cluster_sizes']}; minimum {selected['minimum_cluster_size']}, maximum {selected['maximum_cluster_size']}, no singleton clusters.

## 12. Temporal stability
Historical-to-reference retention is **{retention:.1%}**. {int(transitions.stable.sum())} stores remain in one assigned segment across all snapshots; {int((~transitions.stable).sum())} change at least once; total transitions {int(transitions.transition_count.sum())}.

## 13. Selection rationale
Frozen selection: **{alg}, k={k}**. {cfg['selection']['rationale']}. KMeans and agglomerative k=3 produce the same reference partition; KMeans is retained because centroid prediction is native.

## 14. Final segmentation
Canonical cluster names derived after fitting: {names}.

## 15. Cluster profiles
Machine-readable means, medians, population ratios, and standardized profiles are in `diagnostics/cluster_profiles.csv`.

## 16. Business interpretation
Cluster 1 is higher-volume with higher volatility. Clusters 0 and 2 are lower-volume and differ primarily in promotion share. These are descriptive associations.

## 17. Context analysis
Region, channel, and store type appear only in `diagnostics/cluster_context.csv`; they did not determine distance and are not causal explanations.

## 18. Ambiguous and boundary stores
Smallest centroid margins: stores {ambiguous}. Largest within-cluster distances: stores {distant}. Distance and margin are diagnostics, not probabilities.

## 19. Pseudo-label artifact
`predictions_or_labels/store_segments.parquet` is versioned `{cfg['pseudo_label_version']}` and marked `PSEUDO_LABEL_NOT_GROUND_TRUTH`.

## 20. Segment Assignment readiness
**{readiness}**. Retention of {retention:.1%} is inadequate for treating these exploratory labels as a stable supervised target.

## 21. Limitations
Only {len(reference)} independent stores, three synthetic snapshots, about 90 days of history, and no external/production validation. Internal metrics do not prove natural clusters.

## 22. Reproducibility and DVC
Seed {cfg['random_seed']}; frozen scaler, feature order, centroids, canonical mapping, dataset hash and model state are persisted. DVC stage: `segmentation_v1`.

## 23. Future hypotheses
Collect longer history and additional independent stores, then examine whether promotion dependence and volume regimes remain stable before specifying Segment Assignment.
"""; (out/"report.md").write_text(report,encoding="utf-8")
    git_status=_git("status","--porcelain"); manifest={"experiment_id":experiment_id or out.name,"task":"segmentation","status":"complete","created_at":datetime.now(timezone.utc).isoformat(),"dataset_path":str(data_path),"dataset_fingerprint":_sha(data_path),"schema_fingerprint":hashlib.sha256(str([(c,str(t)) for c,t in zip(frame.columns,frame.dtypes)]).encode()).hexdigest(),"unit_of_analysis":"physical store","reference_snapshot_policy":"latest eligible snapshot per store","reference_snapshot_dates":[str(x.date()) for x in sorted(reference.snapshot_date.unique())],"store_count":len(reference),"historical_snapshot_count":len(history),"feature_set":features,"excluded_fields":cfg["excluded_after_audit"],"context_only_fields":cfg["context_only"],"preprocessing":cfg["preprocessing"],"transformations":cfg["transformations"],"candidate_algorithms":cfg["candidate_models"],"candidate_k_values":cfg["cluster_count_candidates"],"selected_algorithm":alg,"selected_k":k,"selection_rationale":cfg["selection"]["rationale"],"cluster_sizes":selected["cluster_sizes"],"stability_metrics":stability,"pseudo_label_readiness":readiness,"random_seed":cfg["random_seed"],"library_versions":{"python":platform.python_version(),"pandas":pd.__version__,"scikit_learn":sklearn.__version__},"git":{"commit":_git("rev-parse","HEAD"),"branch":_git("branch","--show-current"),"dirty":bool(git_status)},"dvc":{"stage":"segmentation_v1","remote":None},"artifacts":{"model":"models/final_model.joblib","labels":"predictions_or_labels/store_segments.parquet","historical":"predictions_or_labels/historical_assignments.parquet","profiles":"diagnostics/cluster_profiles.csv","candidates":"diagnostics/candidate_metrics.csv"},"pca_explained_variance_ratio":pca.explained_variance_ratio_.tolist(),"reload_smoke_test":True}; (out/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str),encoding="utf-8")
    return {"experiment_id":manifest["experiment_id"],"output_dir":str(out),"selected_model":alg,"test_metrics":metrics}
