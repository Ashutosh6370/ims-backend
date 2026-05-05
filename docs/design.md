# Design Notes

- Async queue used for ingestion
- Debounce logic using 10-second window
- In-memory DB for simplicity
- Incident lifecycle handled via state transitions
- Rate limiting added to avoid overload
