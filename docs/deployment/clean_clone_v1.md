# Clean-clone reproduction V1

Prerequisites are Git, Python 3.11+, DVC Google Drive authorization, and Docker Desktop when container checks are required.

```powershell
git clone https://github.com/Eclipse-XS/FMCG-Sales-Intelligence.git
Set-Location FMCG-Sales-Intelligence
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e . --no-deps
.venv\Scripts\python.exe -c "import fmcg_sales_intelligence"
.venv\Scripts\dvc.exe pull
.venv\Scripts\dvc.exe pull data\processed\forecasting\forecasting_v1.parquet.dvc data\processed\stockout\stockout_v1.parquet.dvc data\processed\segmentation\segmentation_v1.parquet.dvc data\processed\anomaly\anomaly_v1.parquet.dvc data\processed\basket\basket_v1.parquet.dvc data\processed\promotion_daily\promotion_daily_v1.parquet.dvc data\processed\promotion_performance\promotion_performance_v1.parquet.dvc
.venv\Scripts\dvc.exe status
.venv\Scripts\python.exe -m pytest -q
docker compose up -d postgres grafana prometheus
.venv\Scripts\python.exe scripts\verify_grafana_and_queries.py
```

Then copy `.env.example` to `.env` and use `docker compose up -d --build` from the repository root. Access the 11 analytical dashboards at `http://localhost:3001` and verify API `/health` and `/ready` at `http://localhost:8000`.

This procedure was proven from the actual GitHub repository and Google Drive DVC remote on 2026-09-19. The explicit pointer pull is required because these processed datasets are standalone DVC outputs and also pipeline dependencies. Do not copy artifacts or the original DVC cache into a clean clone; that would invalidate the proof. OAuth client configuration must remain in ignored `.dvc/config.local`.
