# db.py
"""Database utilities for Contadores Impressoras.
Uses a local SQLite file (data/counters.db) to store:
- printer_id (text)
- model (text)
- timestamp (datetime)
- total_pages (integer)
"""

import os
import sqlite3
from datetime import datetime

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DB_DIR, "counters.db")

def _ensure_db():
    """Create the database and tables if they do not exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS counters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_id TEXT NOT NULL,
            model TEXT,
            timestamp TEXT NOT NULL,
            total_pages INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def insert_counter(printer_id: str, model: str, total_pages: int, ts: datetime = None):
    """Insert a new counter record.
    Args:
        printer_id: Unique identifier of the printer (e.g., serial number).
        model: Model name of the printer.
        total_pages: Total pages printed at the moment of the email.
        ts: Timestamp of the reading; defaults to now.
    """
    _ensure_db()
    ts = ts or datetime.utcnow()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO counters (printer_id, model, timestamp, total_pages) VALUES (?,?,?,?)",
        (printer_id, model, ts.isoformat(), total_pages),
    )
    conn.commit()
    conn.close()

def get_monthly_summary():
    """Return a dict with months (YYYY‑MM) as keys and two totals:
    {'bw': int, 'color': int}
    For demo purposes we treat all pages as "bw"; real implementation would
    distinguish by model or a flag.
    """
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT substr(timestamp,1,7) as month, SUM(total_pages) FROM counters GROUP BY month ORDER BY month"
    )
    rows = cur.fetchall()
    conn.close()
    summary = {row[0]: row[1] for row in rows}
    return summary

def get_printer_list():
    """Return a list of distinct printers with latest counter.
    Each item is a dict: {printer_id, model, last_timestamp, last_total}.
    """
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.printer_id, c.model, c.timestamp, c.total_pages
        FROM counters c
        INNER JOIN (
            SELECT printer_id, MAX(timestamp) AS max_ts
            FROM counters
            GROUP BY printer_id
        ) latest ON c.printer_id = latest.printer_id AND c.timestamp = latest.max_ts
        ORDER BY c.printer_id
        """
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for printer_id, model, timestamp, total_pages in rows:
        result.append({
            "printer_id": printer_id,
            "model": model,
            "last_timestamp": timestamp,
            "last_total": total_pages,
        })
    return result
