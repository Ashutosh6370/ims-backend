import requests
import time

API = "http://localhost:8000/signal"

events = [
    {
        "component_id": "RDBMS_PRIMARY",
        "severity": "high",
        "message": "Database outage"
    },
    {
        "component_id": "MCP_SERVICE",
        "severity": "high",
        "message": "Dependency failure"
    }
]

for event in events:
    for _ in range(5):
        requests.post(API, json=event)
        time.sleep(0.2)

print("Simulation complete")
