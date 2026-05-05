import requests
import time

url = "http://localhost:8000/signal"

for i in range(10):
    requests.post(url, json={
        "component_id": "db1",
        "severity": "high",
        "message": f"Error {i}"
    })
    time.sleep(0.2)

print("Signals sent")
