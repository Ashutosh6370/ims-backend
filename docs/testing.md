# Testing Strategy

## 1. Functional Testing

- Verified signal ingestion via POST /signal
- Confirmed incident creation
- Validated state transitions:
  - OPEN → INVESTIGATING → RESOLVED → CLOSED

## 2. Negative Testing

- Attempted closing without resolving → rejected
- Attempted closing without RCA → rejected

## 3. Performance Testing

- Simulated burst traffic using script
- Verified system stability under load
- Checked queue behavior

## 4. Debounce Testing

- Sent multiple signals within 10 seconds
- Confirmed only one incident created

## 5. UI Testing

- Verified incident listing
- Checked detail rendering
- Confirmed real-time refresh

## 6. Metrics Validation

- Checked /health endpoint
- Verified signals_processed and queue_size
