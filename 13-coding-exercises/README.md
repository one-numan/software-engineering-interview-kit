# Module 13: Practical Coding & Engineering Exercises

Welcome to the **Practical Coding Exercises** module of the `software-engineering-interview-kit`.

While theoretical knowledge of algorithms and data structures is foundational, senior backend engineering interviews at top-tier product companies (Swiggy, Razorpay, Zomato, Flipkart, CRED, Amazon) focus heavily on practical system coding, real-world debugging, concurrency, and SQL performance tuning.

---

## Directory Navigation

| File | Focus Area | Description |
|---|---|---|
| [backend-practical-tasks.md](backend-practical-tasks.md) | **Backend Architecture** | 6 complete production engineering implementations (N+1 query elimination, 100MB+ streaming, Redis stampede defense, Celery deduplication, UPI webhook idempotency, PostgreSQL CPU debugging). |
| [debugging-exercises.md](debugging-exercises.md) | **Production Incidents** | 6 deep-dive debugging scenarios (memory leaks, deadlocks, connection exhaustion, asyncio event loop stalls, Celery OOM, Redis cache penetration). |
| [python-problems.md](python-problems.md) | **Algorithmic Python** | 6 essential engineering problems (LRU Cache, Thread-Safe Token Bucket, JSON Flattener, Circular Buffer, DAG Topological Sort). |
| [sql-problems.md](sql-problems.md) | **Advanced SQL** | 6 enterprise SQL patterns (Running totals, DENSE_RANK, sessionization by inactivity, booking interval overlap, recursive CTEs, keyset cursor pagination). |

---

## Suggested Preparation Strategy

1. **For SDE-1 / Junior Engineers**:
   - Master all problems in [python-problems.md](python-problems.md) and understand space/time trade-offs.
   - Practice SQL queries in [sql-problems.md](sql-problems.md) (Problems 1, 2, and 6).
2. **For SDE-2 / Mid-Level Engineers**:
   - Implement the tasks in [backend-practical-tasks.md](backend-practical-tasks.md) using FastAPI or Django.
   - Study the incident investigations in [debugging-exercises.md](debugging-exercises.md).
3. **For Senior / Staff Engineers**:
   - Focus on distributed concurrency, idempotency guarantees, and cache stampede algorithms.
   - Lead mock incident triage sessions using the debugging scenarios.
