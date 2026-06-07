# Interview Question Difficulty Level Definitions

To maintain consistency and rigorous assessment standards across all 15 technical domains in this repository, contributors must classify questions according to the following criteria.

---

## 1. Basic Level

### Core Objectives
Assesses fundamental understanding, core syntax, common definitions, elementary operational mechanics, and baseline technical literacy.

### Candidate Profile
- College graduates / Freshers
- Junior Developers (0–2 years experience)
- Developers transitioning into Python / Backend development from other tech stacks

### Coverage & Question Scope
- **Definitions & Terminology**: What is Python? What is WSGI vs ASGI? What is an index?
- **Standard Syntax & Usage**: How do list comprehensions work? How do you define a Pydantic model?
- **Data Types & Operations**: Dictionaries, tuples, sets, strings, and standard manipulation methods.
- **Elementary Mechanics**: How does an `if __name__ == '__main__':` block function?
- **Standard Library Basics**: Basic usage of `math`, `datetime`, `os`, `sys`, `json`.
- **Basic DB Queries**: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, basic `JOIN`, `GROUP BY`.
- **HTTP Basics**: GET vs POST, status codes (200, 201, 400, 401, 403, 404, 500).

---

## 2. Intermediate Level

### Core Objectives
Assesses practical implementation skills, internal component behavior, performance trade-offs, debugging capability, framework idioms, and common production scenarios.

### Candidate Profile
- Mid-level Software Engineers (2–5 years experience)
- Full-Stack Developers handling backend microservices
- Engineers targeting standard MNC and product-firm interview rounds

### Coverage & Question Scope
- **Runtime Mechanics & Internals**: Python memory references, shallow vs deep copy, mutable default argument traps, descriptor protocol, closures.
- **Framework Lifecycles**: Django middleware execution chain, signal caveats, FastAPI dependency injection lifespans, request-response pipelining.
- **ORM & Database Optimization**: Solving the N+1 problem (`select_related`, `prefetch_related`), compound indexes, transaction isolation anomalies (dirty read, non-repeatable read).
- **Concurrency**: `asyncio` event loops vs threading vs multiprocessing, task scheduling, thread-safety pitfalls.
- **Caching & Asynchronous Processing**: Redis cache-aside pattern, Celery task retries, idempotent workers, message ack mechanisms.
- **API Architecture**: JWT lifecycle (refresh + access tokens), CORS resolution, schema validation, rate-limiting strategies.
- **Troubleshooting**: Debugging high response latency, identifying memory spikes, query profiling with `EXPLAIN ANALYZE`.

---

## 3. Advanced Level

### Core Objectives
Assesses system architecture, deep runtime engine internals, extreme performance optimization, scalability, distributed systems trade-offs, mission-critical security, and production troubleshooting under heavy load.

### Candidate Profile
- Senior Software Engineers (5+ years experience)
- Staff / Principal Engineers & System Architects
- Tech Leads designing distributed backend backbones

### Coverage & Question Scope
- **Engine & Runtime Internals**: CPython bytecode interpretation, PyObject structure, reference counting mechanics, cyclic garbage collector generations, GIL implications and free-threaded Python (PEP 703).
- **Distributed System Architectures**: Distributed consensus, two-phase commits, outbox pattern, event sourcing, CQRS, idempotency keys in payment systems.
- **High-Scale Database Engineering**: PostgreSQL WAL, MVCC vacuuming tuning, index bloat, connection pool exhaustion (PgBouncer), database sharding and read-replica replication lag handling.
- **Extreme Concurrency & Performance**: Epoll vs select, CPU profiling with cProfile/py-spy, memory profiling with tracemalloc, zero-copy socket transfers, custom Cython or C extensions.
- **Resilience & Fault Tolerance**: Circuit breaker pattern, backpressure handling, distributed deadlocks, cascading failure mitigation.
- **DevOps & Infrastructure Mastery**: Linux kernel tuning (sysctl, TCP socket reuse, file descriptor limits), Docker cgroups and OOM killer mechanics, zero-downtime rolling deployments, high-availability Nginx load-balancer tuning.
