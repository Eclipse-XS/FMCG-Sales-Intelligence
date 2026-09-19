# Kafka replay operations

Start the isolated broker and UI with `docker compose --profile streaming up -d`. The host broker endpoint is `localhost:9094`; Kafka UI is `http://localhost:8088`.

Run `src/fmcg_sales_intelligence/pipelines/streaming/init_streaming.py`, then `produce_replay.py` and `consume_replay.py`. The producer uses librdkafka with `enable.idempotence=true` and `acks=all`. Every event has `event_id`, `event_type`, `event_time`, `source`, `schema_version`, and `payload`. A malformed envelope is routed to `sales.dlq` and recorded in `streaming.dead_letters`.

The consumer uses `event_id` as the primary key in both `streaming.event_ledger` and `streaming.sales_replay`, with `ON CONFLICT DO NOTHING`. Replaying the same sales events cannot duplicate the materialized replay rows. This is an isolated demonstration stream, not a change-data-capture feed for `fmcg.sales`.
