# Repository migration V1

| Old path | New path | Reason |
|---|---|---|
| No installable product package | `src/fmcg_sales_intelligence/` | Stable generic product boundary without disturbing frozen DVC dependencies |
| Implicit database schema as contract | `config/contracts/registry_v1.yaml` | Versioned machine-readable external contracts |
| Company meaning mixed into project narrative | `config/domains/*` | Replaceable mappings and presentation metadata |
| No serving home | `src/fmcg_sales_intelligence/serving/` and `api/` | Frozen inference separated from HTTP transport |
| No frontend | `apps/dashboard/` | Versioned API-driven business visualization |
| Ad-hoc tool state | `artifacts/project/technology_registry_v1.json` | Evidence-based lifecycle registry |

Deliberately not moved: `src/modeling`, modeling configs, DVC outputs, reports, root `platform/airflow/dags/`, and dbt models. Moving these would create DVC lineage or Airflow-discovery risk without product value. No files were deleted. Legacy modules remain active training/data-pipeline implementations, not abandoned duplicates.

