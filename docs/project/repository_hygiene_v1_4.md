# Repository hygiene V1.4

The release audit inspected tracked, untracked and ignored content; obsolete V1.3 roots; exact duplicate hashes; unusually large tracked files; caches; runtime state; secrets; and DVC ownership.

Removed locally:

- Python bytecode and `__pycache__` directories;
- pytest and Ruff caches;
- frontend `dist` and TypeScript build state;
- dbt logs and target output;
- generated EDA run cache;
- package egg-info;
- cache-only obsolete `scripts` and `src/modeling` directories.

No obsolete tracked source/configuration copy or exact tracked duplicate was found. No compatibility shim exists because the serialization audit proved it unnecessary. Large tracked files are documentation metadata, ERD assets, and referenced analytical figures; none is a misplaced model, Parquet dataset, DuckDB database, or runtime volume.

Intentionally retained locally but ignored: `.venv`, `node_modules`, `.env`, `.dvc/config.local`, DVC cache, DVC-restored datasets/warehouse, canonical artifacts, IDE metadata, and live Docker volumes. These are required development/runtime state rather than release content.

No ignore-rule change was required. Existing `.gitignore` and `.dockerignore` already exclude the audited recurring junk without hiding source files.
