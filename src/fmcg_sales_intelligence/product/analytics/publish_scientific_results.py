import os
import json
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Target Schema
SCHEMA = "ml_results"

# Core to Artifacts Mapping
CORES = {
    "forecasting_v1": {
        "metrics": "metrics.json",
        "predictions": "predictions/test_predictions.parquet",
    },
    "stockout_classification_v1": {
        "metrics": "metrics.json",
        "predictions": "predictions/test_predictions.parquet",
    },
    "stockout_survival_v1": {
        "metrics": "metrics.json",
        "predictions": "predictions/test_predictions.parquet",
        "coefficients": "diagnostics/final_coefficients.csv",
    },
    "segmentation_v1": {
        "metrics": "metrics.json",
        "assignments": "predictions_or_labels/historical_assignments.parquet",
        "profiles": "diagnostics/cluster_profiles.csv",
        "sizes": "diagnostics/cluster_context.csv",
        "candidates": "diagnostics/candidate_metrics.csv",
    },
    "anomaly_v1": {
        "metrics": "metrics.json",
        "candidates": "predictions_or_scores/review_candidates.csv",
    },
    "basket_v1": {
        "metrics": "metrics.json",
        "rules": "outputs/top_rules.csv",
        "all_rules": "outputs/association_rules.parquet",
    },
    "promotion_v1": {
        "metrics": "metrics.json",
        "summary": "outputs/promotion_summary.parquet",
        "exposure": "outputs/exposure_metrics.parquet",
    }
}

def create_engine_from_env():
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "fmcg")
    password = os.environ.get("POSTGRES_PASSWORD", "change_me")
    db = os.environ.get("POSTGRES_DB", "fmcg")
    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

def safe_read(filepath):
    if not filepath.exists():
        logging.warning(f"File not found: {filepath}")
        return None
    if filepath.suffix == '.parquet':
        df = pd.read_parquet(filepath)
    elif filepath.suffix == '.csv':
        df = pd.read_csv(filepath)
    elif filepath.suffix == '.json':
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported extension: {filepath.suffix}")
    
    # Replace non-finite with None (SQL NULL)
    df.replace([np.inf, -np.inf, np.nan], None, inplace=True)
    return df

def publish_core(core_name, files, engine, artifact_root):
    base_dir = artifact_root / core_name
    if not base_dir.exists():
        logging.error(f"Core directory missing: {base_dir}")
        return

    manifest = []
    
    with engine.begin() as conn:
        for file_key, relative_path in files.items():
            filepath = base_dir / relative_path
            data = safe_read(filepath)
            if data is None:
                continue
                
            table_name = f"{core_name}_{file_key}"
            
            if isinstance(data, dict):
                # Flatten single-row metrics JSON
                df = pd.DataFrame([data])
                df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
                df.to_sql(table_name, conn, schema=SCHEMA, if_exists="replace", index=False)
                row_count = 1
            else:
                df = data
                df.to_sql(table_name, conn, schema=SCHEMA, if_exists="replace", index=False)
                row_count = len(df)
                
            manifest.append({
                "core": core_name,
                "table_name": table_name,
                "source_file": relative_path,
                "row_count": row_count
            })
            logging.info(f"Published {core_name}/{file_key} -> {SCHEMA}.{table_name} ({row_count} rows)")
            
    return manifest

def main():
    artifact_root = Path(os.environ.get("FSI_ARTIFACT_ROOT", "artifacts/canonical"))
    engine = create_engine_from_env()
    
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};"))
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA}.publication_manifest;"))
        
    full_manifest = []
    
    for core_name, files in CORES.items():
        logging.info(f"Publishing {core_name}...")
        manifest = publish_core(core_name, files, engine, artifact_root)
        if manifest:
            full_manifest.extend(manifest)
            
    if full_manifest:
        df_manifest = pd.DataFrame(full_manifest)
        df_manifest["published_at"] = pd.Timestamp.now("UTC")
        with engine.begin() as conn:
            df_manifest.to_sql("publication_manifest", conn, schema=SCHEMA, if_exists="replace", index=False)
        logging.info(f"Published manifest with {len(full_manifest)} records.")
        
if __name__ == "__main__":
    main()
