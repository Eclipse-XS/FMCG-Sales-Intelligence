# Repository structure

- `src/fmcg_sales_intelligence/`: installable generic product boundary: contracts, profiles, serving, API, analytics, tracking and CLI.
- `src/modeling/`: frozen V1 experiment implementations retained at stable DVC paths.
- `src/{datasets,quality,warehouse,database,streaming}/`: executed data-platform applications.
- `contracts/`: versioned canonical business contracts.
- `config/domains/`: replaceable source mappings and presentation metadata; never imported by the generic core.
- `config/modeling/`: frozen scientific configuration.
- `data/processed/`: DVC-owned task datasets; `data/warehouse/`: local DuckDB runtime state.
- `artifacts/canonical/`: DVC-owned frozen scientific outputs; `artifacts/project/`: compact Git metadata.
- `platform/dbt/`: staging, intermediate, dimensional/fact and mart transformations.
- `src/fmcg_sales_intelligence/product/analytics/`: publication layer that reads frozen scientific artifacts and writes presentation tables to PostgreSQL for Grafana.
- `infrastructure/`: Docker images, Prometheus, Grafana and connector templates.
- `platform/airflow/dags/`: Airflow discovery path retained deliberately.
- `tests/`: scientific, contract, API and integration regression tests.
- `docs/` and `artifacts/reports/`: maintained guidance versus generated analytical evidence.

