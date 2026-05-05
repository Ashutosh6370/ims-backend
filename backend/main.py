from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import asyncio
import time
from collections import defaultdict, deque

app = FastAPI()

# -----------------------------
# DATA STORES
# -----------------------------
signals_db = []          # raw audit log (NoSQL sink simulation)
incidents_db = {}        # source of truth
signal_queue = asyncio.Queue()

# debounce buffer (10 sec window)
signal_buffer = defaultdict(deque)

# rate limiting
request_times = defaultdict(deque)
RATE_LIMIT = 50  # requests per 10 sec per client

# metrics
metrics = {
    "signals_processed": 0,
    "incidents_created": 0
}

# -----------------------------
# MODELS
# -----------------------------
class Signal(BaseModel):
    component_id: str
    severity: str
    message: str

class RCA(BaseModel):
    root_cause: str
    fix: str
    prevention: str

# -----------------------------
# HEALTH + METRICS
# -----------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "signals_processed": metrics["signals_processed"],
        "active_incidents": len(incidents_db),
        "queue_size": signal_queue.qsize()
    }

# -----------------------------
# RATE LIMIT MIDDLEWARE
# -----------------------------
@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    q = request_times[ip]
    q.append(now)

    # keep last 10 sec window
    while q and now - q[0] > 10:
        q.popleft()

    if len(q) > RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    return await call_next(request)

# -----------------------------
# WORKER (ASYNC ENGINE)
# -----------------------------
async def signal_worker():
    while True:
        signal = await signal_queue.get()

        comp = signal["component_id"]
        now = time.time()

        # -------------------------
        # RAW STORAGE (AUDIT LOG)
        # -------------------------
        signals_db.append(signal)

        # -------------------------
        # DEBOUNCE (10 sec window)
        # -------------------------
        buffer = signal_buffer[comp]
        buffer.append((now, signal))

        # remove old signals
        while buffer and now - buffer[0][0] > 10:
            buffer.popleft()

        # -------------------------
        # INCIDENT CREATION
        # -------------------------
        if comp not in incidents_db:
            incidents_db[comp] = {
                "component_id": comp,
                "signals": [],
                "status": "OPEN",
                "rca": None,
                "created_at": datetime.now().isoformat(),
                "closed_at": None,
                "mttr": None
            }
            metrics["incidents_created"] += 1

        incident = incidents_db[comp]

        # attach all debounced signals
        incident["signals"] = [s for _, s in buffer]

        # state transition
        if incident["status"] == "OPEN":
            incident["status"] = "INVESTIGATING"

        metrics["signals_processed"] += 1

        signal_queue.task_done()

# start worker
@app.on_event("startup")
async def startup():
    asyncio.create_task(signal_worker())

# -----------------------------
# INGEST SIGNAL (ASYNC ENTRY POINT)
# -----------------------------
@app.post("/signal")
async def receive_signal(signal: Signal):
    await signal_queue.put(signal.dict())
    return {"status": "queued"}

# -----------------------------
# GET SIGNALS (RAW LOG)
# -----------------------------
@app.get("/signals")
def get_signals():
    return signals_db

# -----------------------------
# GET INCIDENTS (SOURCE OF TRUTH)
# -----------------------------
@app.get("/incidents")
def get_incidents():
    return incidents_db

# -----------------------------
# RESOLVE INCIDENT
# -----------------------------
@app.post("/incident/{component_id}/resolve")
def resolve(component_id: str):

    if component_id not in incidents_db:
        raise HTTPException(404, "Not found")

    incidents_db[component_id]["status"] = "RESOLVED"

    return {"status": "resolved"}

# -----------------------------
# CLOSE INCIDENT (RCA REQUIRED)
# -----------------------------
@app.post("/incident/{component_id}/close")
def close(component_id: str, rca: RCA):

    if component_id not in incidents_db:
        raise HTTPException(404, "Not found")

    incident = incidents_db[component_id]

    # enforce workflow
    if incident["status"] != "RESOLVED":
        raise HTTPException(400, "Must be RESOLVED before CLOSE")

    # RCA validation
    if not rca.root_cause or not rca.fix or not rca.prevention:
        raise HTTPException(400, "Incomplete RCA")

    incident["status"] = "CLOSED"
    incident["rca"] = rca.dict()

    closed_time = datetime.now()
    incident["closed_at"] = closed_time.isoformat()

    created_time = datetime.fromisoformat(incident["created_at"])
    incident["mttr"] = (closed_time - created_time).total_seconds()

    return {
        "status": "closed",
        "mttr_seconds": incident["mttr"]
    }


