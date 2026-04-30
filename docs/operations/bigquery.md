# BigQuery status

Runtime status: **configured, not executed**. No project ID or service-account credentials were supplied. `dbt/profiles.yml` includes a BigQuery target and `infrastructure/airbyte/postgres_to_bigquery.json` defines the intended raw landing streams.

Before execution: enable BigQuery API; create a least-privilege service account with dataset/table create and job-user permissions; set `BIGQUERY_PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS` outside the repository; create `fmcg_raw` and `fmcg_analytics` in EU. Partition facts by business date and cluster by store/SKU where appropriate. Avoid unrestricted `SELECT *` and use incremental watermark predicates.
