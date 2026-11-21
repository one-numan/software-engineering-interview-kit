# Real-World Production Debugging Exercises

This module contains practical production debugging scenarios based on real-world incidents from high-scale backend services. Each exercise includes the symptom, error stack trace, root cause analysis, diagnostic commands, and the verified fix.

---

## Exercise 1: Silent Memory Leak in Long-Running Python Background Worker

### Symptom
A background Celery worker processing customer data analytics steadily consumes memory until the Linux kernel terminates it with `Out of Memory: Kill process (oom-killer)`.

```
[2026-11-21 02:14:05,112: WARNING/MainProcess] Process 'ForkPoolWorker-2' pid:18492 exited with 'signal 9 (SIGKILL)'
kernel: [18921.412] oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER_MOVABLE), order=0, oom_score_adj=0
kernel: [18921.413] Memory cgroup out of memory: Killed process 18492 (celery) total-vm:4194304kB, anon-rss:3670016kB
```

### Diagnostic Procedure
1. Use Python's built-in `tracemalloc` to take memory snapshots at intervals.
2. Compare snapshots to identify top allocated object types and their allocation stack traces.

```python
import tracemalloc
import gc

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

# ... worker executes tasks ...

snap2 = tracemalloc.take_snapshot()
top_stats = snap2.compare_to(snap1, 'lineno')

for stat in top_stats[:5]:
    print(stat)
```

### Buggy Code Pattern
The worker attaches an event listener or callback closure that references the task instance, creating an uncollected reference cycle held by a module-level registry.

```python
# BUGGY: Global listener registry retains closures and large data payloads indefinitely
GLOBAL_LISTENERS = []

class AnalyticsProcessor:
    def __init__(self, dataset: list):
        self.dataset = dataset  # Several MBs of records

    def register(self):
        # Closure captures 'self', keeping large dataset pinned in memory
        GLOBAL_LISTENERS.append(lambda event: self.handle_event(event))

    def handle_event(self, event):
        pass
```

### The Fix: Weak References & Explicit Cleanup
Use `weakref` or an explicit unregister lifecycle hook to ensure garbage collection.

```python
import weakref

class FixedAnalyticsProcessor:
    def __init__(self, dataset: list):
        self.dataset = dataset

    def register(self, registry: list):
        # Store weak reference to instance; does not prevent garbage collection
        ref = weakref.ref(self)
        registry.append(ref)

    def handle_event(self, event):
        pass

# Worker configuration fix in Celery settings:
# Prevent memory accumulation by recycling worker processes periodically
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000  # 200MB max per child
```

---

## Exercise 2: PostgreSQL Transaction Deadlocks Under High Concurrency

### Symptom
During an inventory reservation surge, the API returns HTTP 500 errors with the following PostgreSQL exception:

```
psycopg2.errors.DeadlockDetected: deadlock detected
DETAIL:  Process 4120 waits for ShareLock on transaction 89123; blocked by process 4121.
Process 4121 waits for ExclusiveLock on tuple (42, 18) of relation "inventory"; blocked by process 4120.
HINT:  See server log for query details.
CONTEXT:  while updating tuple (42, 18) in relation "inventory"
```

### Root Cause
Two concurrent transactions update the same set of inventory items in opposite orders:
- **Transaction A:** Locks Item 101, then attempts to lock Item 202.
- **Transaction B:** Locks Item 202, then attempts to lock Item 101.
Both processes block indefinitely waiting for the other, prompting the PostgreSQL deadlock detector to abort one.

```mermaid
sequenceDiagram
    autonumber
    participant TxA as Transaction A
    participant DB as PostgreSQL
    participant TxB as Transaction B
    TxA->>DB: UPDATE inventory WHERE id = 101 (Acquires Exclusive Lock)
    TxB->>DB: UPDATE inventory WHERE id = 202 (Acquires Exclusive Lock)
    TxA->>DB: UPDATE inventory WHERE id = 202 (BLOCKED by TxB)
    TxB->>DB: UPDATE inventory WHERE id = 101 (BLOCKED by TxA)
    Note over DB: Deadlock detected after deadlock_timeout (1s)!
    DB-->>TxB: ERROR: deadlock detected (ABORT)
    DB-->>TxA: Lock acquired (PROCEED)
```

### The Fix: Deterministic Lock Acquisition Ordering
Always sort resource IDs prior to executing updates or acquiring row locks (`SELECT ... FOR UPDATE`).

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

async def reserve_order_inventory(session: AsyncSession, item_quantities: dict[int, int]):
    """
    Safely reserve inventory across multiple items without deadlocks.
    Enforces deterministic ascending lock acquisition order.
    """
    # CRITICAL FIX: Sort item IDs deterministically
    sorted_item_ids = sorted(item_quantities.keys())

    async with session.begin():
        # Acquire row-level locks in strictly ascending ID order
        stmt = (
            select("Inventory")
            .where("Inventory.id".in_(sorted_item_ids))
            .order_by("Inventory.id.asc()")
            .with_for_update()
        )
        # Concurrent transactions now queue in identical order, eliminating deadlocks
        # ... execute inventory decrement ...
```

---

## Exercise 3: Connection Pool Exhaustion in Asynchronous FastAPI

### Symptom
Under heavy load, response times degrade rapidly and endpoints throw connection errors:

```
asyncpg.exceptions.TooManyConnectionsError: remaining connection slots are reserved for non-replication superuser connections
- OR -
asyncio.exceptions.TimeoutError: QueuePool limit of size 20 overflow 10 reached, connection timed out, timeout 30.00
```

### Root Cause
1. Sessions are opened without deterministic context managers or `finally` blocks, causing connection leaks on uncaught exceptions.
2. The connection pool size is misconfigured: too many Uvicorn worker processes multiplied by large pool sizes exceeds `max_connections` on the PostgreSQL server.

```
Total Active Connections = (Gunicorn Workers) x (DB Pool Size + Max Overflow)
Example: 8 workers x (20 pool + 10 overflow) = 240 connections (Server max_connections = 100)
```

### The Fix: Correct Pool Sizing and Context Management

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI, Depends
from typing import AsyncGenerator

# Proper connection pool sizing:
# Allocate pool size based on: (max_db_connections - reserved) / worker_count
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/production_db"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,            # Bounded active connections per worker
    max_overflow=5,          # Temporary burst allowance
    pool_timeout=10,         # Fail fast instead of hanging request for 30s
    pool_recycle=1800,       # Recycle connections every 30 minutes to drop dead sockets
    pool_pre_ping=True       # Validate connection health before checkout
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# FastAPI dependency guaranteeing connection return to pool
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## Exercise 4: Asyncio Event Loop Starvation from Blocking Synchronous Calls

### Symptom
A FastAPI application handling 5,000 req/sec suddenly experiences 10-second latencies across **all** endpoints, including lightweight health check endpoints (`GET /healthz`).

### Root Cause
An engineer called a synchronous, blocking library (e.g. `requests.get()`, `time.sleep()`, or CPU-intensive image resizing) directly inside an `async def` route.

```python
# BUGGY: Stalls the entire OS thread running the single asyncio event loop
@app.get("/api/v1/payment-status")
async def check_status():
    import requests  # Blocking sync library!
    # During network lag, this blocks the entire event loop for 5.0 seconds
    resp = requests.get("https://bank-gateway.example/status", timeout=5.0)
    return resp.json()
```

### Diagnostic: Detecting Event Loop Stalls
Enable asyncio debug mode to log calls that block the event loop longer than `slow_callback_duration`:

```python
import asyncio
loop = asyncio.get_event_loop()
loop.slow_callback_duration = 0.05  # Flag callbacks taking longer than 50ms
```

### The Fix: Offload to Threadpool or Use Async Client

```python
import asyncio
import httpx
from fastapi import FastAPI

app = FastAPI()

# Solution A: Use native async non-blocking client (Recommended)
@app.get("/api/v1/payment-status")
async def check_status_async():
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("https://bank-gateway.example/status")
        return resp.json()

# Solution B: Offload blocking CPU or legacy sync library to threadpool
@app.get("/api/v1/legacy-call")
async def check_legacy():
    def blocking_work():
        import time
        time.sleep(1.0)
        return {"status": "ok"}

    # Runs in separate worker thread, leaving event loop unblocked
    result = await asyncio.to_thread(blocking_work)
    return result
```

---

## Exercise 5: Celery Worker OOM Crash During Large Data Exports

### Symptom
Exporting 500,000 customer orders to Excel/CSV terminates the worker process with signal 9.

### Root Cause
Executing `orders = Order.objects.all()` or `await session.scalars(select(Order))` loads half a million full ORM objects into Python memory. In CPython, each ORM model instance consumes ~1–2 KB of memory. 500,000 instances consume over 1 GB of RAM instantaneously.

### The Fix: Chunked Server-Side Cursors and Row Streaming

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def export_orders_in_stream(session: AsyncSession, writer):
    """
    Streams rows using server-side cursor without loading all objects into RAM.
    Memory footprint remains constant (<10MB).
    """
    query = select("Order.id", "Order.total", "Order.status").execution_options(yield_per=1000)
    
    result = await session.stream(query)
    async for partition in result.partitions(1000):
        for row in partition:
            writer.writerow([row.id, row.total, row.status])
```

---

## Exercise 6: Redis Cache Penetration & Thundering Herd During Flash Sale

### Symptom
Attackers or bots repeatedly query non-existent product IDs (`GET /products/non-existent-uuid-999`). Because these IDs do not exist, Redis has no cache entry, causing every single request to hit PostgreSQL with expensive `SELECT` queries, crashing the database.

### The Fix: Bloom Filters & Negative Caching

```python
import json
from typing import Optional

async def get_product_secure(redis, db, product_id: str) -> Optional[dict]:
    cache_key = f"product:{product_id}"

    # 1. Check Redis
    cached = await redis.get(cache_key)
    if cached == b"NOT_FOUND":
        return None  # Negative cache hit: fast reject
    if cached:
        return json.loads(cached)

    # 2. Query Database
    product = await db.fetch_product(product_id)

    if product is None:
        # Negative Caching: Cache the absence with short TTL (e.g., 60 seconds)
        # Prevents repeated DB hits for non-existent entities
        await redis.set(cache_key, "NOT_FOUND", ex=60)
        return None

    await redis.set(cache_key, json.dumps(product), ex=3600)
    return product
```
