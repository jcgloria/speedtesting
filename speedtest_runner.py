"""Runs speedtest-cli and stores the result in SQLite.

Replaces spdtest.sh — no more SQL injection, proper error handling,
and retry logic for transient network failures.
"""

import csv
import io
import logging
import subprocess
import sys
import time

from db import get_connection, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

COLUMNS = [
    "server_id", "sponsor", "server_name", "timestamp",
    "distance", "ping", "download", "upload", "share", "ip_address",
]

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 60


def run_speedtest():
    """Run speedtest-cli --csv and return parsed row dict, or None on failure."""
    result = subprocess.run(
        ["speedtest-cli", "--csv"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        log.error("speedtest-cli failed: %s", result.stderr.strip())
        return None

    reader = csv.reader(io.StringIO(result.stdout.strip()))
    values = next(reader, None)
    if not values or len(values) < len(COLUMNS):
        log.error("Unexpected CSV output: %s", result.stdout.strip())
        return None

    return dict(zip(COLUMNS, values))


def store_result(row):
    """Insert a speed test result into the database using parameterized query."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO speedtest
               (timestamp, server_id, sponsor, server_name, distance,
                ping, download, upload, share, ip_address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row["timestamp"], row["server_id"], row["sponsor"],
                row["server_name"], row["distance"], row["ping"],
                row["download"], row["upload"], row["share"],
                row["ip_address"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def main():
    init_db()

    for attempt in range(1, MAX_RETRIES + 1):
        log.info("Speed test attempt %d/%d", attempt, MAX_RETRIES)
        row = run_speedtest()
        if row is not None:
            store_result(row)
            log.info(
                "Saved: %.2f Mbps down / %.2f Mbps up / %.1f ms ping",
                float(row["download"]) / 1_000_000,
                float(row["upload"]) / 1_000_000,
                float(row["ping"]),
            )
            return 0

        if attempt < MAX_RETRIES:
            log.warning("Retrying in %d seconds...", RETRY_DELAY_SECONDS)
            time.sleep(RETRY_DELAY_SECONDS)

    log.error("All attempts failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
