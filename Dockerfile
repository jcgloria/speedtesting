FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    cron \
    speedtest-cli \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY db.py speedtest_runner.py app.py ./
COPY templates templates
COPY static static

# Cron job: run speed test every 30 minutes
RUN echo "*/30 * * * * cd /app && /usr/local/bin/python speedtest_runner.py >> /var/log/speedtest.log 2>&1" | crontab -

EXPOSE 8080

VOLUME /app/db

HEALTHCHECK --interval=60s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["sh", "-c", "service cron start && waitress-serve --host=0.0.0.0 --port=8080 app:app"]
