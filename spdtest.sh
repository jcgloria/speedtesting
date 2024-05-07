#!/bin/bash

DATABASE_FILE="/app/db/speedtest_results.db"

# Check if the database file was created successfully
if [ ! -f "$DATABASE_FILE" ]; then
  sqlite3 "$DATABASE_FILE" ""
fi

# Create table if it doesn't exist
sqlite3 "$DATABASE_FILE" <<EOF
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
EOF

# Run speedtest and save output to SQLite database
speedtest-cli --csv > ./speedtest_output.csv
# Check if the speedtest command was successful
if [ $? -ne 0 ]; then
  exit 1
fi

# Parse the CSV and insert into the SQLite database
IFS=, read -r Server_ID Sponsor Server_Name Timestamp Distance Ping Download Upload Share IP_Address < ./speedtest_output.csv
sqlite3 "$DATABASE_FILE" <<EOF
INSERT INTO speedtest (Timestamp, Server_ID, Sponsor, Server_Name, Distance, Ping, Download, Upload, Share, IP_Address) VALUES ('$Timestamp', '$Server_ID', '$Sponsor', '$Server_Name', '$Distance', '$Ping', '$Download', '$Upload', '$Share', '$IP_Address');
EOF

echo $Timestamp
echo "Speedtest results saved to $DATABASE_FILE"

# Remove temporary CSV file
rm ./speedtest_output.csv
