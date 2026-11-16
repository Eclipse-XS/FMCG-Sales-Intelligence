from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REFERENCE_TIME = "2026-01-15T12:00:00+00:00"
FEATURE_COLUMNS = ("hours_open", "urgency", "account_level", "assigned_agent_open_tickets", "state", "sla_hours")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("A timezone-aware timestamp is required")
    return parsed.astimezone(timezone.utc)


def get_ticket(database: str | Path, ticket_id: int) -> dict | None:
    # Runtime is read-only: no implicit SQLite file or schema creation.
    with sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT ticket_id,created_at,snapshot_at,priority,customer_tier,agent_workload,status,sla_hours "
                           "FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    return dict(row) if row is not None else None


def extract_features(ticket: dict, reference_time: str) -> dict:
    reference, created = parse_time(reference_time), parse_time(ticket["created_at"])
    if reference != parse_time(ticket["snapshot_at"]) or created > reference:
        raise ValueError("Features must use the recorded snapshot time")
    return {"hours_open": (reference - created).total_seconds() / 3600,
            "urgency": ticket["priority"], "account_level": ticket["customer_tier"],
            "assigned_agent_open_tickets": ticket["agent_workload"], "state": ticket["status"],
            "sla_hours": ticket["sla_hours"]}
