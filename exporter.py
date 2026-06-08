#!/usr/bin/env python3
import time
import requests
from prometheus_client import start_http_server, Gauge

APP_URL = "http://localhost:32500/api/latest-confidence"
METRIC_PORT = 8000
POLL_INTERVAL = 5

confidence_gauge = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence from sentiment API'
)

def poll_forever():
    while True:
        try:
            resp = requests.get(APP_URL, timeout=4)
            data = resp.json()
            value = float(data.get("confidence", 1.0))
        except Exception:
            value = 1.0
        confidence_gauge.set(value)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    start_http_server(METRIC_PORT)
    print(f"Exporter running on :{METRIC_PORT}/metrics")
    poll_forever()
