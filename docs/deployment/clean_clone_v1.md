# Clean-clone reproduction V1

Prerequisites are Git, Python 3.11+, Node/npm, DVC Google Drive authorization, and Docker Desktop when container checks are required.

```powershell
git clone https://github.com/Eclipse-XS/FMCG-Sales-Intelligence.git
Set-Location FMCG-Sales-Intelligence
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e . --no-deps
.venv\Scripts\python.exe -c "import fmcg_sales_intelligence"
.venv\Scripts\dvc.exe pull
.venv\Scripts\dvc.exe status
.venv\Scripts\python.exe -m pytest -q
Set-Location apps/dashboard
npm ci
npm test
npm run build
```

Then copy `.env.example` to `.env` and use `docker compose --profile core up -d --build` from the repository root. Verify `/health`, `/ready`, both inference routes, analytics filters, and offline outputs.

This procedure is documented but not yet proven from GitHub: DVC upload/pull is blocked by interactive OAuth and Git publication is intentionally gated behind successful DVC upload. Do not copy artifacts or the original DVC cache into a clean clone; that would invalidate the proof.
