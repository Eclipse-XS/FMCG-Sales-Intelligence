from __future__ import annotations
import json
import uuid
from decimal import Decimal, InvalidOperation
from datetime import datetime
REQUIRED={"event_id","event_type","event_time","source","schema_version","payload"}
def validate(raw: bytes) -> dict:
    event=json.loads(raw.decode("utf-8"));missing=REQUIRED-set(event)
    if missing:raise ValueError(f"missing envelope fields: {sorted(missing)}")
    uuid.UUID(str(event["event_id"]));datetime.fromisoformat(str(event["event_time"]).replace("Z","+00:00"))
    if event["schema_version"]!=1:raise ValueError("unsupported schema_version")
    if event["event_type"]=="sale":
        payload=event["payload"]
        for key in ("sale_id","store_id","sku_id","quantity_units","unit_price"):
            if key not in payload:raise ValueError(f"sale payload missing {key}")
        try:
            quantity = Decimal(str(payload["quantity_units"]))
            price = Decimal(str(payload["unit_price"]))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("sale numeric fields must be numeric") from exc
        if quantity < 0 or price < 0:raise ValueError("negative business value")
    return event
def sale_event(row: dict) -> dict:
    return {"event_id":str(uuid.uuid5(uuid.NAMESPACE_URL,f"fmcg-sale:{row['sale_id']}")),"event_type":"sale","event_time":f"{row['sale_date']}T23:59:59+00:00","source":"pos_replay","schema_version":1,"payload":row}
def encode(event:dict)->bytes:return json.dumps(event,default=str,sort_keys=True).encode("utf-8")
