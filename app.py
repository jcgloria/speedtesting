from flask import Flask, render_template, request, redirect, url_for
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

DATABASE_FILE = '/app/db/speedtest_results.db'

conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)

# Create table if it doesn't exist
createStatement = """
CREATE TABLE IF NOT EXISTS speedtest (
    Timestamp TEXT,
    Server_ID INTEGER,
    Sponsor TEXT,
    Server_Name TEXT,
    Distance REAL,
    Ping REAL,
    Download REAL,
    Upload REAL,
    Share TEXT,
    IP_Address TEXT
);
"""

conn.execute(createStatement)
conn.commit()

query = """
SELECT * 
FROM speedtest 
WHERE strftime('%s', Timestamp) > strftime('%s', '{}');
"""

def getQuery(number, unit):
    try:
        number = int(number)
    except:
        return None
    if unit == 'hour':
        timeDeltaObject = timedelta(hours=int(number))
    elif unit == 'day':
        timeDeltaObject = timedelta(days=int(number))
    elif unit == 'week':
        timeDeltaObject = timedelta(weeks=int(number))
    else:
        return None
    timeQuery = datetime.now(timezone.utc) - timeDeltaObject
    timeQueryStr = timeQuery.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return query.format(timeQueryStr)

@app.route("/")
def main():
    if 'number' not in request.args or 'unit' not in request.args:
        return redirect(url_for('main', number=1, unit='week'))
    requestQuery = getQuery(request.args.get(
        'number'), request.args.get('unit'))
    if requestQuery is None:
        return redirect(url_for('main', number=1, unit='week'))
    try:
        df = pd.read_sql_query(requestQuery, conn)
        data = process_df(df)
        dataString = json.dumps(data)
    except Exception as e:
        print(e)
        data = {}
    dataString = json.dumps(data)
    return render_template('index.html', dataString=dataString, data=data, number=request.args.get('number'), unit=request.args.get('unit'))

def process_df(df):
    if df.empty:
        return {"data": [], "average": {"Download": 0, "Upload": 0}}
    result_dict = {}
    df['Download'] = df['Download'] / 1000000
    df['Download'] = df['Download'].round(2)
    df['Upload'] = df['Upload'] / 1000000
    df['Upload'] = df['Upload'].round(2)
    result_dict['data'] = df[['Timestamp', 'Download', 'Upload']
                             ].to_dict(orient='records')
    result_dict['average'] = {"Download": df['Download'].mean().round(
        2), "Upload": df['Upload'].mean().round(2)}
    return result_dict
