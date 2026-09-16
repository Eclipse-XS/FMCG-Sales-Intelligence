from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

from confluent_kafka import Consumer, Producer
from psycopg.types.json import Jsonb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "database"))
from connection import connect
from events import validate

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")


def main() -> None:
    consumer = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": "fmcg-replay-v3", "auto.offset.reset": "earliest", "enable.auto.commit": False})
    consumer.subscribe(["sales.events"])
    dlq = Producer({"bootstrap.servers": BOOTSTRAP, "enable.idempotence": True, "acks": "all"})
    accepted = rejected = idle_polls = 0
    with connect() as conn, conn.cursor() as cur:
        while idle_polls < 2:
            message = consumer.poll(5.0)
            if message is None:
                idle_polls += 1
                continue
            if message.error():
                raise RuntimeError(f"Kafka consume failed: {message.error()}")
            idle_polls = 0
            try:
                event = validate(message.value())
                payload = event["payload"]
                cur.execute(
                    "INSERT INTO streaming.event_ledger(event_id,event_type,event_time,source,schema_version,payload,status) VALUES(%s,%s,%s,%s,%s,%s,'accepted') ON CONFLICT(event_id) DO NOTHING",
                    (event["event_id"], event["event_type"], event["event_time"], event["source"], event["schema_version"], Jsonb(payload)),
                )
                cur.execute(
                    "INSERT INTO streaming.sales_replay(event_id,sale_id,store_id,sku_id,event_time,quantity_units,unit_price,payload) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(event_id) DO NOTHING",
                    (event["event_id"], payload["sale_id"], payload["store_id"], payload["sku_id"], event["event_time"], payload["quantity_units"], payload["unit_price"], Jsonb(payload)),
                )
                accepted += 1
            except Exception as exc:
                raw = message.value().decode("utf-8", errors="replace")
                cur.execute("INSERT INTO streaming.dead_letters(event_id,reason,raw_event) VALUES(%s,%s,%s)", (str(uuid.uuid4()), str(exc), Jsonb({"raw": raw})))
                dlq.produce("sales.dlq", value=json.dumps({"reason": str(exc), "raw": raw}).encode())
                rejected += 1
            conn.commit()
            consumer.commit(message=message, asynchronous=False)
    remaining = dlq.flush(30)
    consumer.close()
    if remaining:
        raise RuntimeError(f"DLQ flush timed out with {remaining} messages pending")
    print(f"accepted={accepted} rejected={rejected}")


if __name__ == "__main__":
    main()
