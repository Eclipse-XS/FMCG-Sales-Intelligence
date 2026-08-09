# DFD FMCG Sales Intelligence — модель та перевірка

Основний документ: [fmcg_dfd.drawio](fmcg_dfd.drawio). Стан локального репозиторію: `296347d`, refinement перевірено 2026-09-23. Це окрема документація інформаційних потоків; попередні System Architecture та IDEF0 не замінено. Application code, дані, моделі, DVC/MLflow state і runtime не змінювалися.

## Сторінки та нотація

| Вкладка | Зміст | PNG | SVG |
|---|---|---|---|
| Context | Процес 0, дві зовнішні сутності, три потоки | [PNG](previews/dfd_context.png) | [SVG](previews/dfd_context.svg) |
| Level 1 | П'ять процесів, вісім логічних сховищ; batch, BI, science, registration та optional replay | [PNG](previews/dfd_level_1.png) | [SVG](previews/dfd_level_1.svg) |
| Level 2 — Data Preparation | П'ять підпроцесів 2.0 | [PNG](previews/dfd_level_2_data.png) | [SVG](previews/dfd_level_2_data.svg) |
| Level 2 — ML & Analytics | Сім незалежних підпроцесів 3.0 | [PNG](previews/dfd_level_2_ml.png) | [SVG](previews/dfd_level_2_ml.svg) |

Gane–Sarson: сутність — прямокутник; процес — заокруглений прямокутник із відділеним номером; сховище — відкритий праворуч прямокутник з відсіком D-ідентифікатора; потік — спрямована підписана стрілка. Символи складено з нативних редагованих mxGraph-елементів. Повторення D3/D4/D5 на деталізації означає те саме сховище, не копію даних. Пунктир на Level 1 позначає опціональні **потоки даних**, а не керування або IDEF0 Control.

Межа системи охоплює підготовку даних, локальний replay, наукові розрахунки, реєстрацію результатів та product API/dashboard. E1 — зовнішні джерела FMCG/retail-даних; E2 — бізнес-користувач/аналітик. Публічні donor/reference datasets агреговано в E1. Генерація синтетичних даних — частина 1.0, а не вигадане зовнішнє джерело. Агрегований вхід E2 названо «Параметри прогнозування та аналітичних запитів» однаково на Context та Level 1. Для prediction API ці параметри включають `rows` із готовими ознаками: `product/serving/inference.py` перевіряє required features; побудова training datasets усередині pipeline не означає автоматичного отримання inference features із фільтрів.

## Логічні сховища

| ID | Інформація | Відповідність реалізації |
|---|---|---|
| D1 | Початкові та інтегровані дані | Raw/downloaded джерела, donor calibration, generated CSV; це агрегований файловий шар |
| D2 | Операційні FMCG-дані | PostgreSQL `fmcg`: факти продажів, попиту, запасів, замовлень, доставок; довідники, ціни, промо |
| D3 | Аналітичне сховище | DuckDB raw/staging/intermediate/analytics, dbt models; файлові raw Parquet snapshots належать цій же логічній репліці |
| D4 | Набори для аналітичних задач | Processed Parquet, dataset metadata, збережені stockout episodes; aliases не утворюють нових scientific cores |
| D5 | Канонічні ML/аналітичні артефакти та результати | `artifacts/canonical/`: frozen models, predictions/scores, clusters, rules, promo summaries, metrics/manifests |
| D6 | Метадані експериментів, запусків і версій артефактів | MLflow canonical runs, identities, model versions/aliases; логічно відокремлено від D5 |
| D7 | Звіти якості наборів | JSON/Markdown результатів Great Expectations; процес 2.5 не переписує D4 |
| D8 | Черга replay-подій; Kafka | Збережені replay messages у Kafka topic `sales.events`; ledger та DLQ не входять до цього сховища |

Не кожен файл/службовий лог представлено окремим сховищем. Статичні алгоритмічні конфігурації та контракти є частиною специфікації процесів; їх не перетворено на IDEF0-стрілки. DVC reproduction/remote transfer, observability, orchestration і template-only інтеграції поза обраною логічною деталізацією.

## Kafka після refinement

D8 представляє тільки «Черга replay-подій» із технологічним підписом Kafka. Три пунктирні optional flows збережено: D2 → 1.0 «Продажі для replay (опціонально)»; 1.0 → D8 «Опубліковані replay-події»; D8 → 1.0 «Потік FMCG-подій (опціонально; Kafka)». Процес 1.0 агрегує producer і consumer. Producer читає внутрішні `fmcg.sales`, тому нової зовнішньої сутності на Context немає.

Consumer фактично зберігає прийняті події у `streaming.event_ledger` / `streaming.sales_replay`, використовує `ON CONFLICT(event_id) DO NOTHING`, а некоректні повідомлення пише у `streaming.dead_letters` та `sales.dlq`. Це окремі persistent records, **не вміст D8**. Їх дозволено не деталізувати на цьому Level 1; ingestion Level 2 не замовлено. D9 не додано. Ця абстракція не означає запис replay у канонічні `fmcg` facts. Спрощення локальної replay-гілки не змінює Context або межі 2.0/3.0. Звичайний batch-шлях незалежний від Kafka; Kafka UI відсутній.

Джерела: `pipelines/streaming/produce_replay.py`, `consume_replay.py`, `init_streaming.py`, `docs/project/runtime_platform_validation_v1_2.md`. Runtime для refinement не запускався.

## Реєстрація артефактів: межі узагальнення

4.0 тепер «Реєструвати аналітичні артефакти та метадані», D6 — «Метадані експериментів, запусків і версій артефактів». D6 є логічним metadata store, а не заявою про спільну фізичну базу DVC і MLflow. У цій моделі він відображає дані, які фактично читає/пише MLflow importer: сім canonical runs, content identities (`task:v1:hash`), manifest/version tags, run metadata; формальні registered model versions створюються лише для forecasting і stockout classification. Для інших задач немає вигаданого універсального artifact-version registry. DVC state/remote не додано до D6 окремими потоками.

4.0 не копіює всі scientific outputs: importer читає метрики, маніфести, selected configuration/method evidence, хешує model або manifest і завантажує model bundles лише для двох registered models. Підпис «Метрики, маніфести та аналітичні артефакти» агрегує цей підтримуваний набір. D5 → 5.0 уточнено як «Підтримувані ML-артефакти та аналітичні результати»; survival залишається offline.

## Процеси та перевірка достатності входів

У таблиці наведено перевірку інформаційного змісту, а не лише кількості стрілок. Збережені вхідні набори й артефакти можуть існувати до конкретного запуску. DFD не стверджує, що кожен запуск будує всі stores з нуля.

| Процес | Входи → результат; джерело перевірки |
|---|---|
| 0 | Зовнішні набори та параметри/ознаки користувача → прогнози, ризики, KPI, аналітика; декомпозиція Level 1 |
| 1.0 Інтегрувати та перевіряти FMCG-дані | Donor/reference files + calibration → інтегровані записи D2, збережені набори D1; наявні продажі → опубліковані replay-події D8; читання D8 → consumer processing, із деталями журналу поза canvas. `pipelines/ingestion`, `harmonization`, `generation`, `validation`, `persistence/load_data.py`, `streaming` |
| 2.0 Формувати аналітичні набори | D2 та збережені шари D3 → D3/D4; читання сформованих D4 → D7. Деталізація 2.1–2.5 |
| 3.0 Виконувати ML та аналітичну обробку | Task datasets та stockout episodes D4 → моделі/результати/метрики D5. Деталізація 3.1–3.7 |
| 4.0 Реєструвати аналітичні артефакти та метадані | Метрики, manifest identities, моделі D5 та наявні MLflow записи D6 → identities/versions D6. `tracking/mlflow_tracker.py`: importer не навчає моделі, читає існуючі runs/versions для повторного використання |
| 5.0 Надавати прогнози та аналітичні результати | Готові ознаки/параметри E2 + serving subset D5 + BI marts D3 → відповідь E2. `product/serving`, `product/analytics`, `product/api`, dashboard. Survival залишається offline; не всі артефакти D5 є API outputs |
| 2.1 Отримувати операційні факти та довідники | D2 → raw replication D3; `pipelines/warehouse/extract_operational.py` |
| 2.2 Узгоджувати аналітичну структуру даних | Raw replica D3 → staging/enriched facts/dimensions D3; `platform/dbt/models/staging`, `intermediate`, dimension/fact models |
| 2.3 Формувати аналітичні вітрини | Узгоджені факти/виміри та raw промоумови D3 → KPI/promo/order/inventory marts D3; `platform/dbt/models/marts`. 2.2 і 2.3 — логічний поділ одного dbt build, не дві вигадані служби |
| 2.4 Будувати ознаки, цілі та набори задач | Facts/dimensions/marts, raw price/promotion conditions D3 → processed datasets D4; `pipelines/datasets/build_all.py` |
| 2.5 Перевіряти якість сформованих наборів | Уже записані Parquet D4 → результати GE D7; `pipelines/quality/validate_datasets.py` |
| 3.1 Прогнозувати обсяг продажів | Історичні ознаки та відомі training targets → CatBoost model, прогноз реалізованих одиниць наступних 7 днів, метрики; `science/forecasting` |
| 3.2 Оцінювати ризик дефіциту | Stockout features/targets + episodes → classifier, risk scores, metrics; `science/stockout` |
| 3.3 Оцінювати час до дефіциту (офлайн) | Stockout features, episodes, event/censoring data → survival model/estimates/metrics; `science/survival` |
| 3.4 Групувати магазини | Агреговані характеристики → KMeans bundle, дослідницькі clusters, diagnostics; `science/segmentation` |
| 3.5 Виявляти аномальні спостереження | Post-event observations + historical baselines → IsolationForest bundle, scores/candidates, diagnostics; `science/anomaly` |
| 3.6 Виявляти асоціації товарів у кошиках | Basket/order item records → frequent itemsets/rules та support/confidence/lift; `science/basket` |
| 3.7 Порівнювати показники промоперіодів | Daily promotion data + exposure/performance sets → descriptive period comparisons/metrics; `science/promotion` |

Шляхи `pipelines/`, `science/`, `product/`, `tracking/` тут відносні до `src/fmcg_sales_intelligence/`.

### Важлива межа відтворюваності D4

`dvc.yaml` і stockout/survival code читають готовий `data/processed/stockout/stockout_episodes.parquet`. `pipelines/refinement/run_refinement.py` обчислює episodes із raw inventory, але записує їх у каталог refinement reports. Поточний `build_all.py` не публікує цей файл до D4. Тому DFD показує **читання наявних episodes** у 3.2/3.3 і не приписує їх автоматичну публікацію процесу 2.4. Це обмеження існуючого build path, а не підстава вигадувати новий процес або змінювати код.

## Баланс рівнів

Перевірка порівнює трійки `(напрям, логічна сутність/сховище, атом інформації)`, а не буквальну однаковість скорочених підписів. Груповий потік може розкладатися на конкретні datasets/результати. Повторений store та використання одного dataset кількома cores не створюють нової межі.

| Перехід | Результат |
|---|---|
| Context → Level 1 | E1 source datasets → 1.0; E2 parameters/features → 5.0; 5.0 results → E2. Ті самі три потоки та підписи |
| 2.0 → 2.1–2.5 | Входи D2 facts; D3 raw/transformed/marts; D4 datasets для GE. Виходи D3 raw/transformed/marts, D4 task datasets, D7 quality results. Множини точно збігаються |
| 3.0 → 3.1–3.7 | D4: forecasting, stockout, episodes, segmentation, anomaly, basket, promotion. D5: сім типів результатів. Множини точно збігаються |

## Результати QA

- Entity → Store direct flow: **none** (також немає зворотних Store → Entity).
- Store → Store direct flow: **none**.
- Entity → Entity direct flow: **none**.
- Black holes: **none** — кожен процес має output.
- Miracles: **none в межах моделі** — кожен процес має input; походження outputs перевірено за таблицею вище.
- Gray holes: **none в межах моделі** — необхідні datasets, episodes, готові serving features та frozen models явно присутні. Висновок ґрунтується на читанні реалізації, а не лише на XML.
- Unlabelled meaningful flows: **none** — 49 підписаних потоків на чотирьох сторінках.
- Parent-child balancing violations: **none** — три порівняння пройшли.
- XML: **PASS**; 407 унікальних cells; усі parent/source/target references коректні.
- Геометрія: ортогональні маршрути; немає стрілок через сторонні вузли чи текстові прямокутники, накладень зовнішніх підписів і вузлів; виміряно ширину та висоту тексту Arial.
- Реальний імпорт збереженого XML у **mxGraph 4.2.2: PASS** для кожної сторінки, кількість імпортованих cells збігається з XML. Це не твердження про інтерактивний GUI-тест diagrams.net.
- Створено чотири native SVG і чотири PNG 4200 × 2800 через mxGraph та headless Chrome. Усі PNG оглянуто візуально; виправлено лінії символів stores, перетини тексту й маршрути на Level 1 та Data Preparation.
- Макет landscape, чорно-білий, базовий текст 23 px на полотні 2100 px: приблизно 9 pt за ширини A4 без полів. Для звіту бажано SVG на повну доступну ширину landscape-сторінки.

Машинний звіт із точними множинами балансування та SHA-256 фінального XML: [fmcg_dfd_validation.json](fmcg_dfd_validation.json).

## Точкові зміни та збережені рішення

Повний перелік старих і нових підписів: [fmcg_dfd_refinement.md](fmcg_dfd_refinement.md).

- Чотири pages, процеси 0, 1.0–5.0, 2.1–2.5 та 3.1–3.7 збережено. Gane–Sarson та дві downstream-гілки D3/D5 → 5.0 збережено.
- D1 залишено як реальний файловий шар; термін «вихідні» замінено на «початкові». Calibration справді читається під час генерації даних.
- D3 Data Preparation скорочено із семи до чотирьох copies без нових stores або store-to-store edges. Входи 2.4 агреговано: «Факти, виміри, вітрини, ціни та промоумови». Множина boundary atoms незмінна.
- Дві довгі engineering notes на Data Preparation прибрано. Уточнення D3 говорить про аналітичні **структури**, а не ML-моделі.
- D4/D5 на ML page залишено по сім повторів; назва D5 узгоджена на всіх сторінках. Survival має позначку «офлайн». Exploratory clusters, anomaly candidates, association rules та descriptive promotion results не отримали сильніших claims.
- GE читає вже опубліковані набори і пише quality reports D7. Окремий BI шлях збережено; MLflow не стоїть у request path.
- Запропоноване спрощення не інтерпретовано як автоматичний feature lookup в API або model-version registry для всіх cores. Відповідні обмеження реалізації наведено вище.

Джерела актуальності: `README.md`, `docs/project/current_status.md`, `docs/project/runtime_platform_validation_v1_2.md`, maintained architecture docs, `docs/data_sources.md`, зазначені source modules, dbt SQL, `dvc.yaml`, contract/domain/modeling configs і API/dashboard read paths. Історичний modeling checkpoint не використано для заперечення пізнішої runtime validation.

## Відтворення документації

```powershell
.venv/Scripts/python.exe docs/architecture/diagrams/build_dfd.py
.venv/Scripts/python.exe docs/architecture/diagrams/render_dfd_mxgraph.py --mxgraph-js "$env:TEMP/fmcg-idef0-render/node_modules/mxgraph/javascript/dist/build.js"
```

Другий скрипт приймає будь-який локальний шлях до `mxgraph/javascript/dist/build.js`; у цій сесії використано вже наявний тимчасовий mxGraph tooling. Chrome запускається з тимчасовим профілем. Залежності застосунку не змінюються. Генератор — джерело початкового макета; ручні зміни `.drawio` будуть перезаписані повторним запуском генератора. Для експорту ручних змін достатньо другого скрипта.
