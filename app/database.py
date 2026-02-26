import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DATABASE_URL = "river_status.db"

def init_db():
    """Initializes the SQLite database with the required schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measure_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                value REAL,
                status TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                lat REAL,
                long REAL
            )
        """)
        # Index to query the latest reading for a measure
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_measure_timestamp
            ON readings (measure_id, timestamp DESC)
        """)
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def insert_reading(measure_id: str, timestamp: str, value: Optional[float], status: str, name: str, type: str, lat: Optional[float], long: Optional[float]):
    """Inserts a new reading into the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO readings (measure_id, timestamp, value, status, name, type, lat, long) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (measure_id, timestamp, value, status, name, type, lat, long)
        )
        conn.commit()

def get_latest_readings() -> List[Dict[str, Any]]:
    """Gets the latest reading for each measure_id."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Query to get the row with max timestamp for each measure_id
        cursor.execute("""
            SELECT r.*
            FROM readings r
            INNER JOIN (
                SELECT measure_id, MAX(timestamp) as max_timestamp
                FROM readings
                GROUP BY measure_id
            ) as grouping
            ON r.measure_id = grouping.measure_id AND r.timestamp = grouping.max_timestamp
            ORDER BY r.name
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_reading_at_time(measure_id: str, max_timestamp: str) -> Optional[Dict[str, Any]]:
    """Gets the latest reading for a measure_id at or before a given timestamp."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM readings
            WHERE measure_id = ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (measure_id, max_timestamp))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
