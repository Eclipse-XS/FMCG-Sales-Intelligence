# System architecture overview

Модель потоків даних DFD: [редагований документ із 4 сторінками](fmcg_dfd.drawio), [семантика, балансування, Kafka replay та перевірки](fmcg_dfd_audit.md). Gane–Sarson показує рух інформації між процесами, зовнішніми сутностями та сховищами.

Функціональна модель IDEF0: [редагований документ із 4 сторінками](fmcg_idef0.drawio), [семантичний аудит, баланс ICOM і previews](fmcg_idef0_audit.md). Вона доповнює технічну архітектуру нижче.

Основний редагований документ: [fmcg_system_architecture.drawio](fmcg_system_architecture.drawio).
Preview: [SVG](fmcg_system_architecture.svg), [PNG](fmcg_system_architecture.png).

Діаграма описує локальний стан репозиторію на commit `296347d`, перевірений 2026-09-22. Це documentation-only зміна. Наукові результати й application code не змінено; training, DVC reproduction та runtime services не запускалися.

## Архітектурні рішення та джерела

| Рішення | Підтвердження в репозиторії |
|---|---|
| Generic FMCG core; `coca_cola_demo` — змінна demo-конфігурація | `README.md`, `config/domains/`, `product/adapters.py`, `product/contracts/registry.py` |
| Public datasets — донори / reference; основний фактичний load читає generated CSV | `docs/data_sources.md`, `pipelines/harmonization/calibrate_donors.py`, `pipelines/generation/generate_dev_data.py`, `pipelines/persistence/load_data.py` |
| PostgreSQL operational → DuckDB/dbt → processed Parquet | `platform/postgres/schema.sql`, `pipelines/warehouse/extract_operational.py`, `platform/dbt/`, `pipelines/datasets/build_all.py` |
| Перевірки якості розміщені на відповідних рівнях, GE — після dataset build | `pipelines/validation/`, `pipelines/persistence/validate_database.py`, `pipelines/quality/validate_datasets.py` |
| Сім незалежних scientific cores; frozen models, outputs і metrics | `science/cli.py`, сім task packages у `science/`, `config/modeling/`, `dvc.yaml` |
| FastAPI завантажує локальні frozen bundles; аналітичні outputs читаються окремо | `product/serving/registry.py`, `product/analytics/read_service.py`, `product/api/app.py` |
| FastAPI також читає KPI безпосередньо з warehouse | `product/analytics/bi_service.py`, warehouse mount у `docker-compose.yml` |
| Experimental membership використовує frozen KMeans, без retraining | `product/serving/segment_membership.py`, `docs/project/current_status.md` |
| DVC володіє datasets/artifacts/metrics; Google Drive remote налаштований | `dvc.yaml`, `.dvc/config`, `docs/project/clean_clone_reproduction_v1.md` |
| MLflow імпортує canonical runs та serving aliases; не стоїть між artifacts і FastAPI | `tracking/mlflow_tracker.py`, `product/serving/registry.py`, `docker-compose.yml` |
| Kafka consumer пише лише в ізольовану PostgreSQL `streaming` schema | `pipelines/streaming/consume_replay.py`, `init_streaming.py`, `docs/project/runtime_platform_validation_v1_2.md` |
| Airflow: виконаний bounded smoke; batch DAG лише визначений | `platform/airflow/dags/fmcg_runtime_smoke.py`, `fmcg_platform.py`, runtime validation V1.2 |
| Prometheus scrapes API; Grafana має Prometheus та PostgreSQL datasources | `platform/observability/prometheus/prometheus.yml`, `platform/observability/grafana/provisioning/datasources/` |
| Docker Compose охоплює runtime services; Airflow має окремий ephemeral runtime | `docker-compose.yml`, runtime validation V1.2 |

Шляхи `product/`, `pipelines/`, `science/`, `tracking/` у таблиці відносні до `src/fmcg_sales_intelligence/`.

## Уточнення до початкового опису

- Kafka не підключено до canonical ingestion стрілкою, яка могла б означати оновлення `fmcg` facts. Відображено фактичний consumer → isolated replay schema.
- Додано прямий warehouse → FastAPI BI шлях: не всі dashboard results проходять через ML.
- Public datasets показано як донори для генерації; схема не стверджує, що всі зовнішні набори напряму завантажуються в operational schema.
- Airflow dashed control позначає визначений batch DAG. Підтверджене виконання обмежене frozen-evidence smoke check; повний DAG не представлено як виконаний deployment.
- Grafana не зведено лише до Prometheus: додатковий operational PostgreSQL datasource явно зазначено.
- Старий `modeling_checkpoint_v1.md` містить історичні твердження про відсутність remote і runtime validation. Актуальні `current_status.md`, README та V1.2 runtime evidence мають пріоритет для цих питань.
- У maintained Mermaid overview DVC/MLflow стоять у лінійному ланцюгу до API. У новій діаграмі lifecycle відділено від request path відповідно до коду й вимоги завдання.
- Supervised Segment Assignment залишається `DEFERRED_NOT_JUSTIFIED_V1`; він не є восьмим core. Experimental frozen membership зазначено лише в serving. Airbyte / BigQuery templates не показано як реалізовані системи.

## Перевірка та відтворення

```powershell
.venv/Scripts/python.exe docs/architecture/diagrams/build_overview.py
```

`build_overview.py` створює стандартний uncompressed `mxfile` / `mxGraphModel`, потім читає збережений XML для preview. Кожен компонент, підпис і connector редагується; підписи прив'язані до батьківських блоків для спільного переміщення.

Перевірено: valid XML; 94 унікальні cell IDs; коректні parent/source/target references; finite geometry; 18 orthogonal connectors; відсутність накладання великих блоків і перетинів unrelated boxes; ширина й висота всіх підписів у Arial. Preview оглянуто візуально; виправлено перетин підпису BI зі стрілкою та зайвий підпис біля DVC. Кольори кодують джерела, дані, ML, product та infrastructure.

SVG та PNG 3520 × 2200 створено локальним експортером простих XML shapes, а не застосунком diagrams.net. Інтерактивне відкриття в diagrams.net не виконувалося. Основним артефактом залишається `.drawio`; preview не вбудовано замість editable elements. Для звіту краще використовувати SVG на повну ширину landscape-сторінки.
