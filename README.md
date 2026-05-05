🚀 Incident Management System (IMS)
🧠 Overview

This project implements a resilient Incident Management System (IMS) designed to handle high-throughput signals from distributed systems and manage the full incident lifecycle with mandatory Root Cause Analysis (RCA).

The system simulates real-world production scenarios where thousands of signals are generated and must be processed efficiently without failure.

🏗 Architecture
🧱 Architecture Diagram

Client → FastAPI → Rate Limiter → Async Queue → Worker
↓
Debounce Engine
↓
Incidents DB (Source of Truth)
Signals DB (Audit Log)

⚙️ Features
Async signal ingestion using asyncio.Queue
Handles burst traffic (simulated high throughput)
Debounce logic (10-second window per component)
Incident lifecycle:
OPEN → INVESTIGATING → RESOLVED → CLOSED
Mandatory RCA before closing incident
MTTR (Mean Time To Repair) calculation
Rate limiting (50 requests / 10 sec per IP)
Health endpoint for observability
🧰 Tech Stack
Python
FastAPI
Uvicorn
Docker & Docker Compose
In-memory storage (simulating NoSQL + cache)
🚀 How to Run
Using Docker (Recommended)
docker-compose up -d --build

Access Swagger UI:
http://localhost:8000/docs

📡 API Endpoints
🔍 Health Check
GET /health
Returns system status, processed signals, active incidents, and queue size
📥 Signal Ingestion
POST /signal
Ingest a new signal into the system (async queue)

Request Body:

{
  "component_id": "db1",
  "severity": "high",
  "message": "Database failure"
}
📊 Data Retrieval
GET /signals
Returns all raw signals (audit log)
GET /incidents
Returns all incidents (source of truth)
🔄 Incident Workflow
POST /incident/{component_id}/resolve
Moves incident from INVESTIGATING → RESOLVED
POST /incident/{component_id}/close
Closes incident (requires mandatory RCA)

Request Body:

{
  "root_cause": "Database overload",
  "fix": "Restarted DB service",
  "prevention": "Added monitoring and pooling"
}
🔄 Backpressure Handling

The system uses an asynchronous queue (asyncio.Queue) to decouple signal ingestion from processing.

If incoming traffic exceeds processing speed:

Signals are buffered in memory
API remains responsive
System avoids crashes and cascading failures

This simulates real-world backpressure handling in distributed systems.

🧪 How to Test

Start the system:

docker-compose up -d --build
Open Swagger UI:
http://localhost:8000/docs
Send signals using /signal
Check incidents:
GET /incidents
Resolve incident:
POST /incident/{component_id}/resolve
Close with RCA:
POST /incident/{component_id}/close
📥 Sample Signal
{
  "component_id": "db1",
  "severity": "high",
  "message": "Database failure"
}
🧩 Design Patterns Used
Producer-Consumer Pattern → Async queue for ingestion
State Machine Pattern → Incident lifecycle management
Sliding Window Pattern → Debounce logic
Middleware Pattern → Rate limiting
📊 Observability

The /health endpoint provides:

Total signals processed
Active incidents
Queue size

This helps monitor system health and throughput.

⚠️ Limitations
Uses in-memory storage (no persistence)
Single worker (not horizontally scalable yet)
No external message broker (Kafka/Redis not used)
🚀 Future Improvements
Add Redis/Kafka for real message queue
Add PostgreSQL for persistent storage
Build frontend dashboard (React)
Add alerting (Email/Slack)
Implement horizontal scaling
🏁 Conclusion

This project demonstrates:

Handling high-throughput systems
Async processing and backpressure control
Incident lifecycle enforcement
Clean and scalable backend design

⭐ Built as part of an engineering challenge to simulate production-grade incident management systems.

