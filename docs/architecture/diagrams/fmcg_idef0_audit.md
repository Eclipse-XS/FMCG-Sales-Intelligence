# Функціональна модель FMCG Sales Intelligence: семантичний аудит

Основний документ: [fmcg_idef0.drawio](fmcg_idef0.drawio). Стан репозиторію: `296347d`, перевірено 2026-09-22. Межі моделі: реалізована локальна V1.x, включно з науковим циклом, збереженням результатів і їх використанням. Точка зору: розробник-аналітик. Мета: пояснити функціональні залежності для звіту з практики. Це не схема сервісів, не розклад виконання і не модель майбутнього production deployment.

Усі зміни стосуються документації. Код застосунку, datasets, canonical artifacts, моделі, DVC/MLflow state і runtime configuration не змінювалися. Попередню архітектурну діаграму не перегенеровано.

## Сторінки й обрана декомпозиція

| Сторінка | Зміст | Preview |
|---|---|---|
| A-0 — Контекстна діаграма | Одна функція A0: «Обробляти FMCG-дані, формувати аналітичні результати та надавати їх користувачам» | [SVG](previews/idef0_a_minus_0.svg), [PNG](previews/idef0_a_minus_0.png) |
| A0 — Декомпозиція FMCG Sales Intelligence | A1 інтегрувати, перевіряти й зберігати дані; A2 формувати аналітичні набори; A3 виконувати ML та аналітичну обробку даних; A4 версіонувати дані й реєструвати артефакти; A5 надавати прогнози та результати | [SVG](previews/idef0_a0.svg), [PNG](previews/idef0_a0.png) |
| A2 — Формування аналітичних наборів даних | A2.1 копіювання operational facts; A2.2 перетворення й тестування вітрин; A2.3 побудова ознак, цілей і наборів; A2.4 перевірки якості | [SVG](previews/idef0_a2.svg), [PNG](previews/idef0_a2.png) |
| A3 — ML та аналітична обробка даних | A3.1 прогнозування й класифікація ризику; A3.2 survival; A3.3 сегментація й кандидати в аномалії; A3.4 асоціації й описовий промоаналіз; A3.5 збереження результатів за задачами | [SVG](previews/idef0_a3.svg), [PNG](previews/idef0_a3.png) |

A2 обрано через власну логіку перенесення operational facts, dbt transformations, часових ознак/цілей, різних гранулярностей і незалежних перевірок якості. A3 обрано через сім реалізованих наукових ядер із різними методами й межами застосування. A1 агрегує підготовку та operational persistence, тому декомпозиція A2 не дублює ingestion.

## ICOM на межі системи

| Код | Значення |
|---|---|
| I1 | Операційні та довідкові FMCG-дані: продажі, запаси, замовлення, поставки, товари/SKU, магазини, регіони, ціни, промоакції; публічні reference/donor datasets; згенеровані інтегровані дані |
| I2 | Запити та параметри отримання аналітичних результатів. Для prediction endpoints цей агрегат включає готові ознаки з payload; API перевіряє їх наявність |
| C1 | Контракти даних і правила якості |
| C2 | Методика ML та аналітичної обробки: frozen methodology, modeling/evaluation parameters, межі застосування |
| C3 | Доменні правила та правила виконання: domain/runtime configuration, правила реєстрації артефактів |
| O1 | Збережені canonical models, наукові/аналітичні outputs і метрики семи ядер |
| O2 | Відповіді API/інтерфейсу: прогнози, ризики, доступні офлайн-результати, KPI; experimental frozen cluster membership |
| O3 | Ідентифікатори версій даних/артефактів і метадані canonical runs |
| O4 | Звіти перевірок якості сформованих наборів |
| M1 | Сховища й засоби підготовки даних: PostgreSQL, DuckDB/dbt, Python/Polars, Great Expectations |
| M2 | Модулі ML та аналітики: scientific/inference modules, ML/statistical libraries, serialization |
| M3 | Засоби відтворюваності: DVC, MLflow, remote synchronization |
| M4 | Програмна інфраструктура та інтерфейси: FastAPI, Grafana Dashboards, Docker Compose, Prometheus |

Контракти/якість, методику та правила виконання показано трьома окремими controls. Технології агреговано в чотири логічні mechanisms. Коди I/C/O/M збережено в XML metadata та validation JSON, але прибрано з видимих підписів. Ресурси й правила розгалужуються лише до функцій, які їх використовують.

Стрілки входять зліва / зверху / знизу та виходять справа відповідно до [нотації IDEF0 NIST FIPS 183](https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub183.pdf). Dotted numbering A2.1 / A3.1 та верхнє ліве розміщення ідентифікаторів прийнято за університетськими зразками користувача. Вузол на контекстній сторінці A-0 зберігає ідентифікатор A0, який декомпозується на наступній сторінці.

## Аудит кожної функції

У таблиці C і M розкривають відповідні правила й ресурси. Дані не названо механізмами; технології не названо керуванням.

| Функція | I — що обробляється | C — що визначає виконання | O — що утворюється | M — чим виконується |
|---|---|---|---|---|
| A0 | I1, I2 | C1–C3 | O1–O4 | M1–M4 |
| A1 | Вихідні, донорські й синтетичні дані | Mapping/domain definitions, canonical contracts, referential/data validation rules | Операційні факти та довідники | Python ingestion/generation/adapters/validation; PostgreSQL |
| A2 | Операційні факти та довідники | Grain/key/time contracts, SQL transformations, quality rules, правила виконання | Processed task datasets; warehouse marts; quality report | Python, PostgreSQL, DuckDB, dbt, Polars, Great Expectations |
| A3 | Task-specific datasets | Config/modeling, frozen methodology, splits, thresholds, evaluation criteria, правила складу артефактів | Canonical models, results, diagnostics, metrics | Python scientific modules, статистичні/ML-бібліотеки, серіалізація, файлове сховище |
| A4 | Processed datasets та canonical artifacts | Stage dependencies, version ownership, canonical identity, registry/alias rules | Версії, manifests/pointers, метадані canonical runs | DVC, Google Drive remote, MLflow importer/registry |
| A5 | Запити/ознаки/фільтри; warehouse marts; persisted artifact files | Request schemas, frozen feature contracts, serving limitations, domain labels, правила доступних capabilities | Прогнози, risk scores, KPI, аналітичні відповіді | FastAPI, Pydantic, Grafana (11 dashboards-as-code), локальні loaders/read services; телеметрія Prometheus/Grafana |
| A2.1 | Операційні факти та довідники | Перелік таблиць, схема й правила extraction | Raw replica у DuckDB/Parquet | Python, psycopg, PostgreSQL, DuckDB, Polars |
| A2.2 | Raw replica | dbt SQL models, uniqueness/relationship/boundary tests | Analytical marts для A2.3 і BI | DuckDB, dbt |
| A2.3 | Analytical marts | Task contracts, час доступності features, horizons/targets, grain | Записані processed datasets | Python, Polars, DuckDB queries, Parquet writer |
| A2.4 | Уже записані datasets | Expectations: columns, nulls, compound keys, nonnegative ranges | Звіт якості, включно з PASS/FAIL | Great Expectations, Python |
| A3.1 | Forecasting / stockout datasets | Часові розбиття, заборона витоку target, параметри й task metrics | Прогнози/ризики, fitted state, evaluation metrics | Forecasting/stockout modules, CatBoost, scikit-learn |
| A3.2 | Stockout/event-time dataset | Censoring/horizon semantics, Cox specification, diagnostics | Survival estimates, fitted state, дослідницькі diagnostics | Survival module, lifelines |
| A3.3 | Segmentation/anomaly datasets | Features/scaling, k=3, stability checks, detection thresholds | Exploratory clusters, candidate scores, fitted state, diagnostics | Segmentation/anomaly modules, KMeans, Isolation Forest, baseline calculations |
| A3.4 | Basket та promotion datasets | Support/confidence/lift, temporal stability, PRE/DURING/POST windows | Association rules, descriptive comparisons, metrics | Basket/promotion modules, mlxtend, pandas/statistical computations |
| A3.5 | Оцінені результати й fitted state відповідних задач | Canonical paths, serializer/output conventions, resolved configs, manifest/metric contracts | Canonical files: models where applicable, tables, metrics, manifests | Код збереження всередині кожного task module; joblib, Parquet/CSV/JSON/YAML, filesystem |

## Parent–child balancing

Змістовні data/output flows попередньої моделі збережено. Старий агрегат `rules` уточнено як `data_rules`, `method`, `execution`; старий агрегат `resources` — як `data_tools`, `ml_tools`, `lifecycle_tools`, `product_tools`. Це уточнення способу подання ICOM, а не нові бізнесові функції. Коди локальні до сторінки; рівність перевіряється за semantic flow і роллю.

| Parent / boundary | Child distribution |
|---|---|
| A-0 I1, I2 | A0: I1 → A1; I2 → A5 |
| A-0 C1: data rules | A0: A1, A2, A5 |
| A-0 C2: methodology | A0: A3, A5 |
| A-0 C3: execution/domain rules | A0: A1, A2, A4, A5 |
| A-0 M1: data tools | A0: A1, A2, A5 |
| A-0 M2: ML/analytics modules | A0: A3, A5 |
| A-0 M3: reproducibility | A0: A4 |
| A-0 M4: product infrastructure | A0: A5 |
| A-0 O1 / O2 / O3 / O4 | A0: A3 / A5 / A4 / A2 відповідно |
| A0/A2 operational facts | A2:I1 → A2.1 |
| A0/A2 data rules, execution | A2:C1, C2 → A2.1–A2.4 |
| A0/A2 data tools | A2:M1 → A2.1–A2.4 |
| A0/A2 processed datasets | A2:O1 із A2.3; окрема гілка до A2.4 |
| A0/A2 marts | A2:O2 із A2.2; окрема гілка до A2.3 |
| A0/A2 quality report | A2:O3 із A2.4; на A0 це O4 |
| A0/A3 datasets | A3:I1 → незалежні A3.1–A3.4 |
| A0/A3 methodology, ML modules | A3:C1, M1 → A3.1–A3.5 |
| A0/A3 canonical artifacts | A3:O1 із A3.5 |

[Validation JSON](fmcg_idef0_validation.json) містить точні ICOM sets для кожного вузла, boundary mapping і результати імпорту. Автоматично перевірено A-0→A0, A0/A2→A2 і A0/A3→A3. Непояснених boundary inputs/outputs або тунельованих стрілок не додано.

## Факти репозиторію та усунуті неоднозначності

1. **Donor data ≠ direct corporate ingestion.** Public/reference datasets використовуються для profiling/calibration; operational loader читає generated canonical CSV. A1 агрегує різні наявні способи підготовки; не заявляє єдиного автоматичного onboarding для довільної компанії. Джерела: `pipelines/ingestion/`, `harmonization/calibrate_donors.py`, `generation/generate_dev_data.py`, `persistence/load_data.py`, `product/adapters.py`, `docs/data_sources.md`.
2. **Warehouse ≠ processed datasets.** A2.1 створює raw replica, A2.2 будує marts, A2.3 — task-specific Parquet. Вітрини також надходять прямо до A5 для KPI. Джерела: `pipelines/warehouse/extract_operational.py`, `platform/dbt/`, `pipelines/datasets/build_all.py`, `product/analytics/bi_service.py`.
3. **Quality report ≠ model input або training gate.** GE читає вже записані набори й пише JSON/Markdown report; science modules звіт не читають. Тому A2.4 виробляє окремий quality output, а datasets виходять із A2.3. O4 піднято до контексту для збереження балансу. Ненульовий exit code quality CLI може зупинити його orchestration caller, але окремого загального механізму допуску training немає. Джерела: `pipelines/quality/validate_datasets.py`, `pipelines/orchestration/run_local.py`, Airflow DAG definition.
4. **Сім ядер ≠ сім однакових predictors.** A3.1 об'єднує forecasting і stockout classification; A3.2 — survival; A3.3 — segmentation і anomaly; A3.4 — basket і promotion. Кожна гілка включає власне оцінювання. Basket/promotion не змушено проходити fitted-model training. Джерела: `science/cli.py`, сім відповідних scientific packages, `config/modeling/`, `dvc.yaml`, scientific tests.
5. **A3.5 — функціональне узагальнення, не вигаданий сервіс.** Запис canonical files реалізований у кожному task module. Об'єднання стрілок означає пакет різних типів результатів, а не ансамбль, загальний training loop або синхронний barrier. `manifest.json`, `metrics.json`, outputs і serialized state підтверджені у task implementations.
6. **Науковий цикл ≠ request path.** A3 описує реалізований цикл отримання frozen V1 outputs; діаграма не наказує повторювати training для кожного запиту. A5 читає збережені результати й fitted state, A4 виконує lifecycle work окремо. Джерела: `product/serving/registry.py`, `inference.py`, `product/analytics/read_service.py`, `tracking/mlflow_tracker.py`, runtime docs.
7. **Artifacts як Input до A5.** Вхід означає persisted files, що завантажуються/десеріалізуються й використовуються для формування відповіді. Software loaders та inference services — Mechanisms. Це свідомо обрана межа функції; байти артефактів не ототожнено з бібліотекою або training control.
8. **Запит як Input.** Видимий підпис I2 скорочено до «Запити та параметри отримання аналітичних результатів». `_validate_rows` у `product/serving/inference.py` фактично вимагає готові features для prediction requests. Вони залишаються частиною агрегованого payload; діаграма не стверджує, що API автоматично будує всі features із сирих даних. Схеми допустимого запиту та заборона future/outcome fields — відповідне керування. Параметри фільтра визначають конкретний результат, але на цьому рівні не винесені в окремий контрольний потік.
9. **DVC ≠ MLflow.** A4 функціонально об'єднує versioning і registration, але механізми різні: DVC owns stage dependencies/datasets/canonical outputs/metrics та remote synchronization; MLflow importer переносить уже збережені canonical evidence, metadata й serving aliases, без training. Джерела: `.dvc/config`, `dvc.yaml`, `tracking/mlflow_tracker.py`, clean-clone/runtime evidence.
10. **Segment assignment.** Supervised classifier залишається `DEFERRED_NOT_JUSTIFIED_V1`; experimental membership використовує frozen scaler/KMeans і належить A5. Це не восьме scientific core. Джерела: `product/serving/segment_membership.py`, `tests/integration/test_segment_membership.py`, `docs/project/current_status.md`.
11. **Supporting resources не керують scientific meaning.** Kafka — optional replay до ізольованої `streaming` schema, не джерело canonical facts; Airflow має визначений batch DAG і підтверджений лише bounded evidence smoke; Prometheus/Grafana — допоміжна телеметрія. Вони належать до ресурсів і пояснень у цій документації; довгі infrastructure annotations прибрано з полотна. Вони не є обов’язковими бізнесовими функціями або controls. Джерела: streaming consumer, `platform/airflow/dags/`, `platform/observability/`, `docker-compose.yml`, `docs/project/runtime_platform_validation_v1_2.md`.
12. **Maintained status має пріоритет.** Історичний modeling checkpoint містить застарілі твердження про remote/runtime. Для актуального стану використано README, `current_status.md`, V1.2 runtime evidence та код. Airbyte/BigQuery templates не включено як виконані функції.

Шляхи `product/`, `pipelines/`, `science/`, `tracking/` відносні до `src/fmcg_sales_intelligence/`.

## Візуальне уточнення за університетськими зразками

- Збережено один наявний `.drawio` із тими самими чотирма рівнями/сторінками і 15 функціями. Семантику data/results flows не перебудовано.
- Прибрано великі заголовки, службові примітки, пояснення routing, legend та переліки бібліотек із полотна. Назви сторінок залишилися в Draw.io tabs.
- Біле полотно, білі прямокутники, тонкі чорні стрілки, звичайний Arial без великих bold заголовків. Ідентифікатори зверху ліворуч; назви функцій центровані.
- A-0: один центральний блок, два агреговані inputs, три controls, чотири outputs, чотири mechanisms. На controls/mechanisms підписи розривають лінію білим проміжком, як у references. I1 включає synthetic/donor data; I2 перейменовано без втрати feature payload semantics.
- A0, A2, A3 мають каскадне компонування. A3 перейменовано на «Виконувати ML та аналітичну обробку даних». A2.1–A2.4 і A3.1–A3.5 використовують dotted numbering.
- Grouping A2/A3 не змінено: A3.1 predictive; A3.2 survival; A3.3 exploratory structure/deviation analysis; A3.4 association/descriptive campaign analysis; A3.5 persisted outputs. A3.3/A3.4 не означають спільний estimator або training pipeline.
- Свідомі відмінності від references: незалежні scientific branches на A3; прямі warehouse/artifact inputs до A5; відсутність вигаданого обов’язкового A4→A5 runtime step; окремий quality output, оскільки science modules не споживають validation report. На A2 один релевантний data mechanism; на A3 один ML mechanism — баланс із parent збережено. На A-0 mechanisms чотири.

## Технічна й візуальна перевірка

```powershell
.venv/Scripts/python.exe docs/architecture/diagrams/build_idef0.py
.venv/Scripts/python.exe docs/architecture/diagrams/render_idef0_mxgraph.py --mxgraph-js "$env:TEMP\fmcg-idef0-render\node_modules\mxgraph\javascript\dist\build.js"
```

Другий крок вимагає наявний mxGraph 4.2.2 (`javascript/dist/build.js`) і Chrome. Для цього уточнення mxGraph встановлено лише в тимчасовий tooling-каталог, не в application dependencies. Рендерер запускає браузер без GUI з окремим тимчасовим профілем і не використовує користувацькі browser credentials.

- Valid XML; 4 pages; 15 function boxes; 262 unique cell IDs; parent/source/target references і finite geometry перевірено.
- Для кожного вузла є I, C, O, M. Автоматично перевірено боки входження, напрямки останніх сегментів і вихід справа.
- Три parent–child typed-flow balances пройдено; назви й піднабори правил/ресурсів перевірено семантично.
- Orthogonal routes; відсутні overlapping function boxes та connectors через function boxes. Текст уміщується. Підписи на стрілках мають білий проміжок; інші підписи не перетинають ліній.
- **Імпорт mxGraph пройдено для всіх 4 сторінок:** A-0 — 31 cell, A0 — 97, A2 — 66, A3 — 68. Кількість імпортованих cells дорівнює кількості у відповідному XML.
- SVG експортовано з mxGraph; PNG 3680 × 2320 отримано через headless Chrome. У SVG немає image objects, vendor assets або raster flattening. Ці previews замінили попередні previews локального примітивного експортера.
- Усі чотири фінальні previews оглянуто візуально й порівняно з наданими зразками. Повний UI diagrams.net інтерактивно не відкривався; перевірено імпорт його формату через mxGraph codec.

Основний документ залишається fully editable: окремі functions, labels, connectors. Генератор перезапише ручні правки до IDEF0 artifacts при повторному запуску; після build можна повторити native render. Джерельний `.drawio` fingerprint і machine-readable перевірки записано у validation JSON. Попередня System Architecture Diagram не змінена.
