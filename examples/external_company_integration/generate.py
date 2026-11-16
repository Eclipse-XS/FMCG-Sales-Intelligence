from __future__ import annotations

import random
import sqlite3
from datetime import timedelta
from pathlib import Path

from servicedesk.features import REFERENCE_TIME, parse_time

SEED = 1701


def generate(database: Path, count=480):
    database.parent.mkdir(parents=True, exist_ok=True)
    rng, reference = random.Random(SEED), parse_time(REFERENCE_TIME)
    with sqlite3.connect(database) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, snapshot_at TEXT NOT NULL,
                priority TEXT NOT NULL, customer_tier TEXT NOT NULL, agent_workload INTEGER NOT NULL,
                status TEXT NOT NULL, sla_hours REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS outcomes (
                ticket_id INTEGER PRIMARY KEY REFERENCES tickets(ticket_id),
                future_resolution_hours REAL NOT NULL, sla_breached INTEGER NOT NULL);
        ''')
        if conn.execute("SELECT count(*) FROM tickets").fetchone()[0]:
            return
        for ticket_id in range(1, count + 1):
            priority = rng.choice(["low", "normal", "high", "urgent"])
            sla = {"low": 72., "normal": 48., "high": 24., "urgent": 12.}[priority]
            # Predict before the deadline: no already-known breaches at snapshot.
            age = round(rng.uniform(0.5, 0.9 * sla), 2)
            tier = rng.choice(["standard", "premium", "enterprise"])
            workload = rng.randint(1, 28)
            status = rng.choice(["open", "pending", "escalated"])
            # Future resolution is generated only for the training outcome table.
            # Runtime feature extraction never queries this table or receives it.
            remaining_work = max(0.5, 3 + workload * 0.8 + (12 if status == "pending" else 0)
                                 - (5 if tier == "enterprise" else 0) + rng.gauss(0, 7))
            future_resolution = age + remaining_work
            conn.execute("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?)", (
                ticket_id, (reference - timedelta(hours=age)).isoformat(), reference.isoformat(),
                priority, tier, workload, status, sla))
            conn.execute("INSERT INTO outcomes VALUES (?,?,?)", (ticket_id, future_resolution, int(future_resolution > sla)))
