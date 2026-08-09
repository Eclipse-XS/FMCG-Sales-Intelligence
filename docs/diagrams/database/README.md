# FMCG Sales Intelligence: Logical and Physical ERD

Дві окремі редаговані моделі даних, побудовані за репозиторієм 2026-09-23. PostgreSQL не запускався; це аудит DDL у репозиторії, а не новий знімок live database. Реалізацію проєкту не змінено.

## Основні артефакти

| Модель | Native editable source | Векторний preview | Растровий preview |
|---|---|---|---|
| Logical domain model | [fmcg_logical_erd.drawio](fmcg_logical_erd.drawio) | [SVG](fmcg_logical_erd.svg) | [PNG](fmcg_logical_erd.png) |
| Physical PostgreSQL model | [fmcg_physical_erd.drawio](fmcg_physical_erd.drawio) | [SVG](fmcg_physical_erd.svg) | [PNG](fmcg_physical_erd.png) |

Draw.io — джерела діаграм; SVG/PNG експортовані з тих самих mxGraph-моделей. Таблиці, тексти та зв’язки є окремими редагованими об’єктами. Немає вставленого зображення замість моделі чи HTML-таблиць.

## A. Перевірені джерела

- [`platform/postgres/schema.sql`](../../../platform/postgres/schema.sql): таблиці, literal SQL types, PK, FK, UNIQUE, CHECK, nullable, identity, generated columns, enum types.
- [`platform/postgres/indexes.sql`](../../../platform/postgres/indexes.sql): 13 неунікальних індексів продуктивності; вони не змінюють cardinality.
- [`platform/postgres/seed_reference.sql`](../../../platform/postgres/seed_reference.sql): довідникові INSERT; структуру не розширює.
- [`platform/postgres/init/05-mlflow-database.sql`](../../../platform/postgres/init/05-mlflow-database.sql): окрема база MLflow, не доменні таблиці FMCG.
- [`create_schema.py`](../../../src/fmcg_sales_intelligence/pipelines/persistence/create_schema.py), [`load_data.py`](../../../src/fmcg_sales_intelligence/pipelines/persistence/load_data.py), [`validate_database.py`](../../../src/fmcg_sales_intelligence/pipelines/persistence/validate_database.py): застосування DDL/індексів і перевірки цілісності.
- [`test_database.py`](../../../tests/integration/test_database.py): тести обмежень, прочитані без запуску операцій з БД.
- [`init_streaming.py`](../../../src/fmcg_sales_intelligence/pipelines/streaming/init_streaming.py): окремі технічні таблиці replay/idempotency/DLQ.
- [`docs/erd.md`](../../erd.md), [`erd_metadata.json`](../../erd_metadata.json), [`erd_verification.json`](../../erd_verification.json), [`data_engineering_v1.md`](../../data/data_engineering_v1.md): допоміжна семантика та попередня перевірка БД. Історичні snapshots не перезаписано.

Пошук CREATE TABLE, ALTER TABLE та ORM/SQLAlchemy declarations у `platform`, `src`, `tools`, `tests` не виявив додаткового джерела доменної структури поза вказаним DDL. Для physical model пріоритет має SQL, зокрема `timestamp`, а не нормалізоване позначення типу з історичного metadata snapshot.

## B. Знайдена модель

18 доменних таблиць, 146 колонок, 29 FK, 15 UNIQUE constraints, 49 CHECK clauses, 3 enum types.

| Домен | Фактичні таблиці |
|---|---|
| Каталог | categories, brands, products, skus |
| Роздрібна структура | regions, stores |
| Ціни та промо | promotions, promotion_skus, promotion_stores, product_prices |
| Замовлення та продажі | orders, order_items, sales |
| Постачання | warehouses, deliveries, delivery_items |
| Запаси та спостереження попиту | inventory, daily_demand |

## C. Logical model

16 сутностей і 27 зв’язків. Назви в однині, бізнес-ідентифікатори та вибрані змістовні атрибути; SQL types, FK columns, provenance, timestamps технічного аудиту й назви constraints не перенесено.

`promotion_skus` і `promotion_stores` не мають бізнес-атрибутів поза парою ключів: замінені на Promotion ↔ SKU і Promotion ↔ Store, обидва `0..N : 0..N`. Order Item і Delivery Item залишені, оскільки представляють позиції з кількістю та, для Order Item, ціною й сумами. Delivery Item має складений бізнес-ідентифікатор Delivery + SKU.

Inventory Snapshot представляє залишки SKU на складі на дату. Demand Observation відображає `daily_demand`, зокрема реалізований/втрачений попит і censoring. Sale — щоденний запис продажів SKU у магазині; прямого зв’язку Sale → Order або Order Item немає в DDL, тому його не додано.

## D. Physical model

Побудована з `schema.sql`: усі 18 таблиць і всі 146 колонок у порядку DDL, буквальні SQL types, PK/FK, усі UNIQUE groups, NN/NL та generated stored markers. `U1`/`U2` позначають стовпці одного UNIQUE constraint **в межах конкретної таблиці**. Повторені PK markers означають один складений PK.

Лінії прив’язані до центрів конкретних FK та referenced PK rows. На схемі немає вигаданих FK чи зв’язків за схожими назвами. Найважливіші CHECK показані стисло; повні 49 expressions, definitions/defaults, identity, referential actions і склад enum types збережено у [машинному аудиті](fmcg_schema_audit.json).

## E. Рішення щодо цілісності та меж моделі

- Числова min..max нотація: `1` — рівно один; `0..1` — необов’язковий один; `0..N` — нуль або багато. Число біля сутності описує кількість її екземплярів на один екземпляр протилежної сутності. Перетин ліній не створює додаткового зв’язку.
- Чотири nullable FK: `categories.parent_category_id`, `deliveries.order_id`, `sales.promotion_id`, `daily_demand.promotion_id`. Решта mandatory. Повний перелік 29 FK наведено в [аудиті зв’язків](relationships.md).
- SQL не вимагає хоча б однієї позиції для Order/Delivery: на відповідному кінці `0..N`, а не `1..N`. Nullable `deliveries.order_id` не є UNIQUE: замовлення може мати багато доставок.
- Ієрархія Category має optional parent; DDL не гарантує відсутність циклів.
- `order_items.line_total` та `inventory.available_quantity` generated stored, але не мають явно заданого NOT NULL: показано NL. PK columns завжди NN, включно зі складеними ключами.
- Nullable складові UNIQUE у categories/skus зберігають звичайну SQL семантику distinct NULL; діаграма не стверджує `NULLS NOT DISTINCT`.
- Перекриття цінових інтервалів та належність SKU/store до застосованої промоакції перевіряються pipeline validation. У DDL немає відповідного exclusion constraint або composite FK; на ERD їх не вигадано.
- `streaming.event_ledger`, `streaming.sales_replay`, `streaming.dead_letters` існують для replay/idempotency/DLQ і виключені з основного operational ERD. Їх definitions збережено в аудиті; declared FK між ними відсутні. Виключення не означає відсутність реалізованого Kafka replay path.
- MLflow має окрему БД. DuckDB/dbt warehouse — інша dimensional model; її не змішано з operational PostgreSQL. За потреби для неї має бути окрема діаграма.

## F. Перевірка та обмеження

[fmcg_erd_validation.json](fmcg_erd_validation.json) містить результати XML, геометрії, text fit, звірки з DDL, native mxGraph import/render і hashes артефактів. Незалежна повторна перевірка збереженого XML звіряє всі колонки/ключі/nullability, 29 пар FK→PK, cardinality та фактичні координати кінців ліній.

Обидві моделі імпортуються native mxGraph codec і рендеряться headless Chrome без repair. Це не замінює перевірку в інтерактивному diagrams.net: вона не виконувалася. PNG/SVG переглянуті візуально. Лінії не проходять через boxes або labels; текст не обрізано. Залишено 18 геометричних перетинів ліній у logical і 22 у physical: це явне обмеження поточної загальної схеми, а не твердження про повну відсутність перетинів.

Для друку використовуйте A3 landscape і векторний SVG або PDF export із draw.io. Physical model щільна через повний перелік колонок; зменшення до A4 погіршує читабельність. Дані/БД не змінювалися; runtime та integration tests не запускалися, оскільки змінено лише документацію.

## G. Інвентар і відтворення

Усі артефакти цієї задачі розташовані в `docs/diagrams/database/`:

- `fmcg_logical_erd.drawio`, `fmcg_logical_erd.svg`, `fmcg_logical_erd.png`;
- `fmcg_physical_erd.drawio`, `fmcg_physical_erd.svg`, `fmcg_physical_erd.png`;
- `README.md`, `relationships.md`, `fmcg_schema_audit.json`, `fmcg_erd_validation.json`;
- `audit_schema.py`, `build_erd.py`, `erd_layout.py`, `verify_erd.py`, `render_erd_mxgraph.py` — засоби генерації/перевірки документації.

З кореня репозиторію у Windows:

```powershell
.venv/Scripts/python.exe docs/diagrams/database/build_erd.py
.venv/Scripts/python.exe docs/diagrams/database/verify_erd.py
.venv/Scripts/python.exe docs/diagrams/database/render_erd_mxgraph.py --mxgraph-js '<path-to-mxgraph>/javascript/dist/build.js'
```

Генератор використовує Pillow/Arial для перевірки розмірів тексту; renderer — локальний mxGraph JavaScript і Chrome через CDP. Вони не додаються до runtime dependencies проєкту. DDL parser призначений для поточного repository schema, не є універсальним SQL migration interpreter; після зміни SQL його підтримку нових конструкцій слід перевірити.
