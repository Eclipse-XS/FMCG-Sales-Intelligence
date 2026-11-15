from pathlib import Path
from fmcg_sales_intelligence.product.analytics.publish_scientific_results import CORES


def test_canonical_artifacts_exist_on_disk():
    artifact_root = Path("artifacts/canonical")
    for core, files in CORES.items():
        core_dir = artifact_root / core
        assert core_dir.exists(), f"Core directory missing: {core_dir}"
        for key, rel_path in files.items():
            file_path = core_dir / rel_path
            assert file_path.exists(), f"Artifact file missing for {core}/{key}: {file_path}"
