# Use a Python base image
FROM python:latest

WORKDIR /app

# Install sqlite3, cron, and speedtest-cli
RUN apt-get update && apt-get install -y \
    sqlite3 \
    cron \
    speedtest-cli \
    && rm -rf /var/lib/apt/lists/*

# Install the Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Prepare the speedtest script and the cronjob
COPY spdtest.sh .
RUN chmod +x spdtest.sh
RUN echo "*/30 * * * * /app/spdtest.sh >> /tmp/spdtest.log 2>&1" | crontab -

# Prepare the web app
COPY app.py .
COPY templates templates
COPY static static

# Run with waitress (default port is 8080)
EXPOSE 8080

VOLUME /app/db

CMD ["sh", "-c", "service cron start && waitress-serve app:app"]

