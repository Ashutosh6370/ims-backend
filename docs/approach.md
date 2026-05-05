# Approach

1. Built FastAPI backend
2. Added async queue for ingestion
3. Implemented debounce logic
4. Added incident lifecycle
5. Enforced RCA validation
6. Added rate limiting and health endpoint

## Design Decisions

- Used in-memory stores for simplicity and speed
- Async queue chosen for backpressure handling
- Debounce logic prevents alert flooding
- Simple UI used for rapid prototyping

## Trade-offs

- No persistent DB (can be replaced with PostgreSQL/Redis)
- No distributed queue (can upgrade to Kafka)
