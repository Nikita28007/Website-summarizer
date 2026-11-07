"""
SQLite persistence layer for website summaries.

The database file (summaries.db) is created automatically on first use.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("summaries.db")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS summaries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    url        TEXT    NOT NULL,
    model      TEXT    NOT NULL,
    summary    TEXT    NOT NULL,
    created_at TEXT    NOT NULL
)
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(_CREATE_TABLE)
    conn.commit()


def save_summary(url: str, summary: str, model: str) -> int:
    """Insert a new summary row and return its auto-assigned id."""
    with _connect() as conn:
        _ensure_schema(conn)
        cur = conn.execute(
            "INSERT INTO summaries (url, model, summary, created_at) VALUES (?, ?, ?, ?)",
            (url, model, summary, datetime.now(timezone.utc).isoformat()),
        )
        return cur.lastrowid


def list_summaries(limit: int = 20) -> list[sqlite3.Row]:
    """Return the most recent *limit* summaries, newest first."""
    with _connect() as conn:
        _ensure_schema(conn)
        return conn.execute(
            "SELECT * FROM summaries ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()


def get_summary(row_id: int) -> sqlite3.Row | None:
    """Return a single summary by its id, or None if not found."""
    with _connect() as conn:
        _ensure_schema(conn)
        return conn.execute(
            "SELECT * FROM summaries WHERE id = ?", (row_id,)
        ).fetchone()

