import sqlite3
import os

DATABASE_FILE = os.environ.get("DB_PATH", "/app/db/speedtest_results.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS speedtest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    server_id INTEGER,
    sponsor TEXT,
    server_name TEXT,
    distance REAL,
    ping REAL,
    download REAL,
    upload REAL,
    share TEXT,
    ip_address TEXT
);

CREATE INDEX IF NOT EXISTS idx_speedtest_timestamp ON speedtest(timestamp);
"""


def get_connection():
    """Create a new connection per call — safe for multi-threaded use."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.close()
