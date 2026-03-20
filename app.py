import json
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, request, redirect, url_for

from db import get_connection, init_db

app = Flask(__name__)

VALID_UNITS = {
    "hour": lambda n: timedelta(hours=n),
    "day": lambda n: timedelta(days=n),
    "week": lambda n: timedelta(weeks=n),
}

MAX_PERIOD_DAYS = 365


def query_speedtest_data(number, unit):
    """Query speed test results for the given time window. Returns dict."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return None
    if number < 1 or unit not in VALID_UNITS:
        return None

    delta = VALID_UNITS[unit](number)
    if delta.days > MAX_PERIOD_DAYS:
        return None

    cutoff = (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%S")

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT timestamp, download, upload, ping FROM speedtest "
            "WHERE strftime('%s', timestamp) > strftime('%s', ?) "
            "ORDER BY timestamp",
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return {
            "data": [],
            "average": {"download": 0, "upload": 0, "ping": 0},
        }

    data = []
    total_dl = total_ul = total_ping = 0
    for row in rows:
        dl = round(row["download"] / 1_000_000, 2)
        ul = round(row["upload"] / 1_000_000, 2)
        p = round(row["ping"], 1)
        data.append({
            "timestamp": row["timestamp"],
            "download": dl,
            "upload": ul,
            "ping": p,
        })
        total_dl += dl
        total_ul += ul
        total_ping += p

    n = len(data)
    return {
        "data": data,
        "average": {
            "download": round(total_dl / n, 2),
            "upload": round(total_ul / n, 2),
            "ping": round(total_ping / n, 1),
        },
    }


@app.route("/")
def main():
    number = request.args.get("number")
    unit = request.args.get("unit")

    if number is None or unit is None:
        return redirect(url_for("main", number=1, unit="week"))

    result = query_speedtest_data(number, unit)
    if result is None:
        return redirect(url_for("main", number=1, unit="week"))

    return render_template(
        "index.html",
        data_json=json.dumps(result),
        data=result,
        number=number,
        unit=unit,
    )


@app.route("/health")
def health():
    """Health check — confirms DB is reachable and returns last test time."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT timestamp FROM speedtest ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()

    last_test = row["timestamp"] if row else None
    return {"status": "ok", "last_test": last_test}


init_db()
