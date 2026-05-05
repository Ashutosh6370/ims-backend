# Backpressure Handling

## Problem
In high-throughput systems, incoming signals can overwhelm the backend if processed synchronously.

## Solution Implemented

### 1. Async Queue
- Used `asyncio.Queue` as a buffer
- Incoming signals are queued instead of processed immediately

### 2. Worker-Based Processing
- A background worker continuously processes signals
- This decouples ingestion from processing

### 3. Rate Limiting
- Middleware limits requests per client
- Prevents abuse and sudden spikes

### 4. Debounce Mechanism
- Signals within 10 seconds are grouped
- Avoids duplicate incident creation

## Outcome

- System remains stable under burst traffic
- No blocking of API layer
- Smooth handling of high load (10k signals/sec scenario)
