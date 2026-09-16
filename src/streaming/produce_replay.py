from __future__ import annotations
import os,sys
import json
from pathlib import Path
from confluent_kafka import Producer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"database"))
from connection import connect
from events import sale_event
BOOTSTRAP=os.getenv("KAFKA_BOOTSTRAP_SERVERS","localhost:9094")
def main():
    # librdkafka provides broker-level producer idempotence.  The previous pure
    # Python client accepted acks=all but did not implement this guarantee.
    producer=Producer({"bootstrap.servers": BOOTSTRAP, "enable.idempotence": True, "acks": "all"})
    with connect() as conn,conn.cursor() as cur:
        cur.execute("SELECT sale_id,sale_date,store_id,sku_id,quantity_units,unit_price,net_revenue,promotion_id FROM fmcg.sales ORDER BY sale_id LIMIT 20")
        cols=[x.name for x in cur.description];events=[sale_event(dict(zip(cols,row))) for row in cur.fetchall()]
    def delivery(error, message):
        if error is not None:
            raise RuntimeError(f"Kafka delivery failed: {error}")

    for event in events:
        producer.produce("sales.events", key=event["event_id"].encode(), value=json.dumps(event, default=str).encode(), on_delivery=delivery)
    producer.produce("sales.events", key=b"malformed", value=b'{"bad":true}', on_delivery=delivery)
    remaining=producer.flush(30)
    if remaining:
        raise RuntimeError(f"Kafka flush timed out with {remaining} messages pending")
    print(f"published valid={len(events)} malformed=1")
if __name__=="__main__":main()
