"""
fa_db_adv.py
============
Advanced FastAPI Database Integration Questions: FA-ADV-126 to FA-ADV-150 (25 questions)
"""

adv_data = [
    # FA-ADV-126
    (
        "FA-ADV-126",
        "High-Throughput Async Connection Pool Sizing in Multi-Worker Uvicorn Deployments",
        "Total database connections equal `Number of Workers * (pool_size + max_overflow)`; exceeding database limits causes connection exhaustion, requiring precise pool sizing or PgBouncer.",
        "In production, FastAPI runs with multiple Uvicorn worker processes (e.g. 4 to 16 workers managed by Gunicorn). Because each OS process maintains its own independent SQLAlchemy connection pool in memory, pool settings multiply across workers: `Total Connections = Workers * (pool_size + max_overflow)`. If PostgreSQL has `max_connections = 100`, running 8 workers with `pool_size = 20` and `max_overflow = 10` can spawn up to 240 connections, crashing the database. In high-concurrency environments, developers must either strictly bound client pool sizes (e.g., `pool_size = 5, max_overflow = 5`) or place an external connection pooler like PgBouncer in front of PostgreSQL using `NullPool` in SQLAlchemy.",
        "from sqlalchemy.ext.asyncio import create_async_engine\nfrom sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool\n\n# Scenario A: Direct to PostgreSQL (Strictly bounded per-worker pool)\n# With 4 Uvicorn workers: 4 * (5 + 2) = 28 connections maximum\ndirect_engine = create_async_engine(\n    'postgresql+asyncpg://user:pass@db:5432/app',\n    poolclass=AsyncAdaptedQueuePool,\n    pool_size=5,\n    max_overflow=2,\n    pool_timeout=15,\n)\n\n# Scenario B: Behind PgBouncer (Transaction Pooling mode)\n# Disable SQLAlchemy in-process pooling to let PgBouncer handle pooling\npgbouncer_engine = create_async_engine(\n    'postgresql+asyncpg://user:pass@pgbouncer:6432/app',\n    poolclass=NullPool,\n)",
        "Comparing bounded in-process QueuePool sizing with NullPool configuration behind PgBouncer.",
        "Each Uvicorn worker is an independent POSIX process with separate memory and address space. SQLAlchemy pools cannot coordinate or share connections across process boundaries. PgBouncer, by contrast, sits as a lightweight C proxy maintaining server connections and assigning them to client sockets on a per-transaction basis.",
        "High-traffic API deployments handling tens of thousands of requests per second across multi-core Kubernetes clusters.",
        ["Why can't multiple Uvicorn worker processes share a single SQLAlchemy connection pool?", "What are the three pooling modes supported by PgBouncer (session, transaction, statement)?"],
        ["Configuring large pool sizes per worker (e.g., `pool_size=50`) under multiple workers, triggering 'too many clients already' from PostgreSQL.", "Using prepared statements with PgBouncer in transaction pooling mode without proper dialect configuration."],
        "Formula to memorize: `Workers * (pool_size + max_overflow) <= Postgres max_connections * 0.8` (reserve 20% for admin/migrations).",
        ["[Gunicorn & Uvicorn](../11-devops/gunicorn-and-uvicorn.md)", "[Connection Pooling](database-integration.md)"],
        ["https://www.postgresql.org/docs/current/runtime-config-connection.html"]
    ),

    # FA-ADV-127
    (
        "FA-ADV-127",
        "Preventing Connection Pool Starvation During Long-Running Streaming Endpoints",
        "Connection starvation occurs when streaming or long-polling endpoints hold database connections open for the duration of the HTTP response; it is mitigated by releasing the connection before streaming.",
        "If an endpoint streams large datasets or server-sent events (SSE) while keeping an `AsyncSession` open, that database connection remains locked for the entire duration of the client connection. If 20 slow clients connect on a 3G network, all 20 pooled connections become occupied doing network I/O, completely blocking all other API requests from obtaining a database connection. To prevent pool starvation: 1) Paginate or pre-fetch data in batches, closing the database session immediately; 2) Use a background worker to generate files in S3 and return a pre-signed URL; 3) Release the database connection back to the pool before starting the HTTP stream.",
        "import asyncio\nfrom collections.abc import AsyncGenerator\nfrom fastapi import FastAPI, Depends\nfrom fastapi.responses import StreamingResponse\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Record(Base):\n    __tablename__ = 'records'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    val: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:', pool_size=5)\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\napp = FastAPI()\n\n# Anti-pattern: Holding session open during slow HTTP stream (starves pool)\n# Safe pattern: Read chunk, release session, stream chunk\nasync def safe_stream_records() -> AsyncGenerator[str, None]:\n    last_id = 0\n    while True:\n        # Open and close session per batch; connection is NOT held during slow network writes\n        async with SessionLocal() as session:\n            stmt = select(Record).where(Record.id > last_id).order_by(Record.id).limit(100)\n            batch = (await session.scalars(stmt)).all()\n            if not batch:\n                break\n            last_id = batch[-1].id\n            chunk = '\\n'.join(r.val for r in batch) + '\\n'\n            \n        yield chunk  # Yield occurs OUTSIDE the database session context!\n        await asyncio.sleep(0.01)\n\n@app.get('/safe-export')\nasync def export_data():\n    return StreamingResponse(safe_stream_records(), media_type='text/plain')",
        "Preventing pool starvation by scoping database sessions per batch and yielding HTTP chunks outside session boundaries.",
        "In the safe pattern, the database socket connection is checked out for ~2ms to fetch 100 rows and immediately returned to `QueuePool`. While the HTTP streaming response writes packets to the slow client, the connection is free to serve other API requests.",
        "CSV/PDF export endpoints, telemetry log dumps, and event stream broadcasts.",
        ["How does holding a connection open during network I/O violate the Single Responsibility Principle of connection pools?", "Why is asynchronous streaming particularly vulnerable to slowloris-style connection exhaustion?"],
        ["Wrapping the entire `StreamingResponse` generator inside a single `async with SessionLocal() as db:` block.", "Failing to set client timeouts on streaming endpoints."],
        "Emphasize: NEVER yield to a network client from inside an open database transaction or session.",
        ["[Streaming Responses](async-and-concurrency.md)", "[Connection Pooling](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects"]
    ),

    # FA-ADV-128
    (
        "FA-ADV-128",
        "Distributed Transactions Across Microservices: Saga Pattern vs Two-Phase Commit (2PC)",
        "Two-Phase Commit (2PC) is rarely feasible in cloud microservices due to blocking locks; the Saga pattern coordinates transactions via local ACID transactions and compensating actions.",
        "In distributed architectures, an operation (e.g. placing an order) spans multiple microservices with separate databases (Order DB, Payment DB, Inventory DB). Traditional Two-Phase Commit (2PC / XA) relies on a centralized coordinator holding locks across all nodes, creating severe latency bottlenecks and single points of failure. The Saga pattern decomposes the distributed transaction into a series of local transactions: each service updates its own database and emits an event. If a step fails, the Saga executes compensating transactions (e.g., refund payment, restore inventory) in reverse order to achieve eventual consistency.",
        "# Conceptual Saga Orchestration in FastAPI:\n# async def execute_order_saga(order_id: str, user_id: str, amount: int):\n#     # Step 1: Create pending order in local DB\n#     await order_repo.create_order(order_id, 'PENDING')\n#     \n#     # Step 2: Reserve payment (via Payment Service)\n#     pay_ok = await payment_client.charge(user_id, amount)\n#     if not pay_ok:\n#         await order_repo.update_status(order_id, 'PAYMENT_FAILED')\n#         return {'status': 'failed', 'reason': 'payment'}\n#         \n#     # Step 3: Reserve inventory (via Inventory Service)\n#     inv_ok = await inventory_client.reserve(order_id)\n#     if not inv_ok:\n#         # COMPENSATING TRANSACTION: Refund payment\n#         await payment_client.refund(user_id, amount)\n#         await order_repo.update_status(order_id, 'INVENTORY_UNAVAILABLE')\n#         return {'status': 'failed', 'reason': 'inventory'}\n#         \n#     await order_repo.update_status(order_id, 'CONFIRMED')",
        "Implementing an orchestrated Saga workflow with automated compensating transactions on partial failures.",
        "The Saga coordinator maintains a state machine. When an error occurs at Step N, it traverses the saga history backwards, invoking idempotent compensation APIs on previously completed steps to guarantee eventual consistency without distributed locks.",
        "E-commerce checkouts, flight and hotel booking aggregates, and multi-bank wire transfers.",
        ["What is the difference between Orchestrated Sagas and Choreographed Sagas?", "Why must compensating transactions be strictly idempotent?"],
        ["Attempting to implement distributed ACID transactions using standard database locks across network boundaries.", "Failing to make compensating actions idempotent, causing double refunds if compensation retries occur."],
        "Key insight: In distributed systems, trade absolute ACID consistency for Eventual Consistency using Sagas with compensating actions.",
        ["[Distributed Systems](../10-system-design/distributed-systems.md)", "[Event-Driven Architecture](../06-redis-and-messaging/background-processing.md)"],
        ["https://microservices.io/patterns/data/saga.html"]
    ),

    # FA-ADV-129
    (
        "FA-ADV-129",
        "Asynchronous Database Failover and Active-Passive Cluster Switching",
        "FastAPI applications survive database failovers (e.g. AWS Aurora/RDS Multi-AZ) by combining DNS caching controls, health-check timeouts, and dynamic connection recreation.",
        "When an active primary database fails, cloud providers promote a passive standby replica to become the new primary. During this 15-60 second transition: 1) The database DNS endpoint points to the new primary; 2) Existing TCP sockets to the dead primary hang; 3) Read-only replicas may reject writes. To handle this cleanly: configure `pool_pre_ping=True`, set low socket connect timeouts (`timeout=5, command_timeout=10` in asyncpg), configure OS-level TCP keepalives, and ensure container DNS TTL is low (e.g. 5 seconds in AWS CoreDNS) to resolve the new IP address immediately.",
        "from sqlalchemy.ext.asyncio import create_async_engine\n\n# Database cluster endpoint with resilient failover settings\nFAILOVER_DB_URL = 'postgresql+asyncpg://app_user:secret@aurora-cluster.internal:5432/production'\n\nresilient_engine = create_async_engine(\n    FAILOVER_DB_URL,\n    pool_size=10,\n    pool_pre_ping=True,      # Discards severed sockets immediately upon checkout\n    pool_recycle=300,        # Recycle connections every 5 minutes to adapt to topology changes\n    connect_args={\n        'timeout': 5,                # Abort socket connect after 5s if old IP is blackholed\n        'command_timeout': 10,        # Abort stuck queries if primary freezes\n        'server_settings': {\n            'tcp_user_timeout': '10000', # Linux TCP timeout (10 seconds)\n        },\n    },\n)",
        "Configuring asyncpg engine with low connect timeouts and pool_pre_ping for automated cluster failover recovery.",
        "When Aurora fails over, the old primary ceases acknowledging TCP packets. Without `tcp_user_timeout` or `connect_args['timeout']`, standard TCP socket reads hang for minutes in `ESTABLISHED` state. Low timeouts cause the dead connection to raise an exception, triggering `pool_pre_ping` to drop it and establish a fresh connection to the newly promoted host IP.",
        "High-availability healthcare and banking APIs requiring 99.99% uptime through AWS RDS Multi-AZ failovers.",
        ["How does stale DNS caching in Java/Python containers delay database failover recovery?", "What is the difference between AWS Aurora regional clusters and Multi-AZ RDS failover?"],
        ["Relying on default OS TCP keepalive settings (which can take up to 2 hours to detect a dead socket on Linux).", "Not catching `asyncpg.CannotConnectNowError` or `ReadOnlyDatabaseError` during failover promotion windows."],
        "Emphasize configuring `connect_args={'timeout': 5}` and `pool_pre_ping=True` to recover from failovers in seconds instead of hanging.",
        ["[AWS RDS Fundamentals](../11-devops/aws.md)", "[Transient Retry](database-integration.md)"],
        ["https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html"]
    ),

    # FA-ADV-130
    (
        "FA-ADV-130",
        "Real-Time Database Change Data Capture (CDC) with PostgreSQL `LISTEN`/`NOTIFY` and WebSockets",
        "PostgreSQL's native `LISTEN`/`NOTIFY` mechanism allows FastAPI to receive asynchronous database events via asyncpg and broadcast them directly to connected WebSockets.",
        "Polling a database every second for updates wastes CPU and bandwidth. PostgreSQL includes a built-in publish/subscribe mechanism via `LISTEN` and `NOTIFY`. Database triggers on tables (or backend workers) emit `NOTIFY channel_name, 'payload'`. FastAPI can dedicate a long-lived asyncpg connection to listen on that channel. When an event fires, asyncpg invokes a callback, which pushes the update through FastAPI's WebSocket connection manager to frontend clients in real time.",
        "import asyncio\nimport asyncpg\nfrom fastapi import FastAPI, WebSocket, WebSocketDisconnect\n\napp = FastAPI()\n\nclass ConnectionManager:\n    def __init__(self):\n        self.active_connections: list[WebSocket] = []\n    async def connect(self, ws: WebSocket):\n        await ws.accept()\n        self.active_connections.append(ws)\n    def disconnect(self, ws: WebSocket):\n        self.active_connections.remove(ws)\n    async def broadcast(self, message: str):\n        for connection in self.active_connections:\n            await connection.send_text(message)\n\nmanager = ConnectionManager()\n\n# Dedicated listener background coroutine\nasync def pg_listener():\n    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/app')\n    def on_notification(connection, pid, channel, payload):\n        asyncio.create_task(manager.broadcast(payload))\n    await conn.add_listener('order_updates', on_notification)\n    while True:\n        await asyncio.sleep(3600)\n\n@app.websocket('/ws/orders')\nasync def order_ws(websocket: WebSocket):\n    await manager.connect(websocket)\n    try:\n        while True:\n            await websocket.receive_text()\n    except WebSocketDisconnect:\n        manager.disconnect(websocket)",
        "Streaming PostgreSQL NOTIFY events to browser WebSockets using asyncpg add_listener.",
        "PostgreSQL's engine dispatches notification packets across the open client connection. `asyncpg` listens on the socket asynchronously without polling; when a packet arrives, it triggers the registered Python callback on the asyncio event loop.",
        "Real-time delivery driver tracking, stock market ticker updates, and collaborative whiteboard notifications.",
        ["What is the maximum payload size supported by PostgreSQL `NOTIFY` (8000 bytes)?", "How do you handle multi-instance FastAPI scaling when using `LISTEN`/`NOTIFY`?"],
        ["Sending massive JSON payloads through `NOTIFY` exceeding the 8KB limit (send record IDs instead and fetch details).", "Using a connection from the general SQLAlchemy pool for `LISTEN`, which removes a connection permanently from the pool."],
        "Crucial detail: Always use a dedicated, standalone `asyncpg.connect()` connection for `LISTEN`, never a pooled SQLAlchemy connection.",
        ["[WebSockets](../07-api-engineering/websockets.md)", "[PostgreSQL Features](../05-databases/postgresql.md)"],
        ["https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.add_listener"]
    ),

    # FA-ADV-131
    (
        "FA-ADV-131",
        "Custom SQLAlchemy Compilation Extensions and AST Query Rewriting",
        "SQLAlchemy's compiler extension system (`@compiles`) enables extending the SQL compiler to inject custom database syntax, hints, or transparent multi-tenant filters.",
        "SQLAlchemy allows developers to intercept and customize how SQL statements are compiled. By using `@compiles`, you can add support for proprietary database syntax (e.g. PostgreSQL `ON CONFLICT`, MySQL optimizer hints, or custom cryptographic functions) or implement automatic AST query rewriting (such as appending tenant security filters or `deleted_at IS NULL` conditions to every `Select` statement automatically).",
        "from sqlalchemy.ext.compiler import compiles\nfrom sqlalchemy.sql.expression import ClauseElement\nfrom sqlalchemy import select\n\n# Define a custom SQL clause element\nclass IndexHint(ClauseElement):\n    def __init__(self, index_name: str):\n        self.index_name = index_name\n\n# Register custom compilation for PostgreSQL vs SQLite\n@compiles(IndexHint, 'postgresql')\ndef compile_hint_pg(element, compiler, **kw):\n    # PostgreSQL doesn't support FORCE INDEX; return empty string or custom comment\n    return f'/* PG_INDEX({element.index_name}) */'\n\n@compiles(IndexHint, 'sqlite')\ndef compile_hint_sqlite(element, compiler, **kw):\n    return f'INDEXED BY {element.index_name}'",
        "Creating a custom SQL clause construct and registering dialect-specific compilation logic with @compiles.",
        "When `engine.execute()` compiles a statement, it traverses the expression tree. When it encounters `IndexHint`, it dispatches to the function registered for the active dialect in `compiles`, generating precise vendor-specific SQL.",
        "High-performance tuning with database optimizer hints, proprietary database functions, and transparent multi-tenant AST rewriting.",
        ["How can `@compiles` be used to automatically enforce soft delete filters across all queries?", "What is the danger of AST query modification on complex subqueries?"],
        ["Overusing query compilation hooks for business logic that belongs in the service layer.", "Writing compiler extensions that break cross-database portability without defining dialect-specific handlers."],
        "Explain that `@compiles` acts as a compiler plugin for SQLAlchemy's SQL generation pipeline.",
        ["[SQLAlchemy Core](database-integration.md)", "[Query Optimization](../05-databases/indexing-and-optimization.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/compiler.html"]
    ),

    # FA-ADV-132
    (
        "FA-ADV-132",
        "Zero-Downtime Database Schema Migrations (Expand and Contract Pattern) with Alembic",
        "Zero-downtime migrations use the Expand and Contract (Parallel Run) pattern to apply schema changes across multiple deployment phases without locking tables or breaking running app instances.",
        "Running destructive migrations (e.g., dropping columns, renaming columns, or adding non-nullable columns without defaults) during a rolling deployment causes errors when old application pods read the modified schema or new pods read the old schema. The Expand and Contract pattern splits migrations into phases: 1) Expand: Add new columns as nullable, deploy code that writes to both old and new columns; 2) Backfill: Asynchronously copy legacy data to the new column; 3) Contract: Deploy code reading exclusively from the new column; 4) Cleanup: Issue a final migration dropping the obsolete old column.",
        "# Phase 1: Expand (Alembic migration)\n# op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))\n\n# Phase 2: Dual-Writing Application Code (FastAPI service)\n# @app.post('/users')\n# async def create_user(first: str, last: str, db: AsyncSession = Depends(get_db)):\n#     full = f'{first} {last}'\n#     # Writes to BOTH legacy columns and new column\n#     user = User(first_name=first, last_name=last, full_name=full)\n#     db.add(user)\n#     await db.commit()\n\n# Phase 3: Contract (Switch reads to full_name)\n# Phase 4: Cleanup (Drop first_name and last_name via Alembic)",
        "Phased lifecycle of zero-downtime column migration using the expand and contract pattern.",
        "Because both old and new application versions run concurrently during Kubernetes rolling deployments, this pattern ensures backward and forward database compatibility at every step without requiring table locks or downtime.",
        "High-availability consumer platforms (fintech, e-commerce) deploying multiple times daily without maintenance windows.",
        ["Why does renaming a column with `ALTER TABLE RENAME COLUMN` cause downtime during rolling deployments?", "What is an Access Exclusive table lock in PostgreSQL?"],
        ["Adding a `NOT NULL` column with a slow Python backfill inside an exclusive lock transaction, locking the table for minutes.", "Dropping an old column before all legacy pods have been fully terminated."],
        "Core rule: Never rename or drop columns in a single deploy; always use Expand, Migrate, Contract, and Cleanup phases.",
        ["[Alembic Migrations](database-integration.md)", "[CI/CD & Blue-Green](../11-devops/ci-cd.md)"],
        ["https://martinfowler.com/bliki/ParallelRun.html"]
    ),

    # FA-ADV-133
    (
        "FA-ADV-133",
        "Dynamic Database Sharding Across Multiple Physical Instances in FastAPI",
        "Database sharding horizontally partitions data across multiple physical database instances, routed dynamically based on a shard key using custom dependency resolvers.",
        "When a single database server reaches its maximum physical vertical scaling capacity (CPU, IOPS, RAM), horizontal sharding distributes data across independent database clusters. A deterministic sharding function (such as `hash(user_id) % num_shards` or consistent hashing) maps a shard key to a specific physical database instance. In FastAPI, a dynamic dependency resolves the shard key from the request and yields an `AsyncSession` bound to the appropriate shard's engine.",
        "from fastapi import FastAPI, Depends, Header, HTTPException\nfrom sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\n\n# Pre-configured shard engines for 2 physical database clusters\nSHARD_ENGINES = {\n    0: create_async_engine('sqlite+aiosqlite:///:memory:', echo=False),\n    1: create_async_engine('sqlite+aiosqlite:///:memory:', echo=False),\n}\n\nSHARD_FACTORIES = {\n    idx: async_sessionmaker(eng, expire_on_commit=False)\n    for idx, eng in SHARD_ENGINES.items()\n}\n\ndef get_shard_id(account_id: int) -> int:\n    return account_id % len(SHARD_ENGINES)\n\nasync def get_shard_session(x_account_id: int = Header(...)) -> AsyncSession:\n    shard_id = get_shard_id(x_account_id)\n    session_factory = SHARD_FACTORIES[shard_id]\n    async with session_factory() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/account/status')\nasync def get_status(db: AsyncSession = Depends(get_shard_session)):\n    return {'status': 'connected_to_shard'}",
        "Dynamic session routing to physical database shards based on a hash of the account ID header.",
        "The request header provides the shard key. The dependency calculates the partition index and leases a connection from the corresponding shard's engine pool. Queries are isolated to that shard, eliminating cross-node lock contention.",
        "Hyper-scale messaging platforms, gaming user databases, and multi-region SaaS architectures.",
        ["What are the trade-offs of hash-based sharding vs range-based sharding?", "How do you execute cross-shard aggregations or joins?"],
        ["Performing cross-shard joins in application code (extremely slow; data should be co-located by shard key).", "Resharding when adding new shard instances (requires consistent hashing algorithms like Ketama)."],
        "Highlight that cross-shard joins are the primary complexity of sharding; choose shard keys that co-locate related data.",
        ["[Distributed Systems](../10-system-design/distributed-systems.md)", "[Database Design](../05-databases/database-design.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/extensions/horizontal_shard.html"]
    ),

    # FA-ADV-134
    (
        "FA-ADV-134",
        "PostgreSQL Declarative Table Partitioning with SQLAlchemy Routing",
        "Declarative table partitioning divides large PostgreSQL tables into physical sub-tables (by range, list, or hash) while exposing a unified virtual table to FastAPI queries.",
        "Tables with hundreds of millions of rows suffer from bloated indexes and slow queries. PostgreSQL native declarative partitioning splits a master table into smaller physical partitions (e.g., partitioning `orders` by `order_date` ranges like `orders_2026_q1`, `orders_2026_q2`). SQLAlchemy maps to the master table name; PostgreSQL's query planner automatically applies 'partition pruning' to route queries and inserts directly to the relevant sub-table without querying unneeded partitions.",
        "from datetime import datetime\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy import PrimaryKeyConstraint\n\nclass Base(DeclarativeBase):\n    pass\n\n# SQLAlchemy model mapping to a partitioned PostgreSQL table\nclass MetricEvent(Base):\n    __tablename__ = 'metric_events'\n    \n    # In partitioned tables, the partition key MUST be part of the primary key\n    id: Mapped[int] = mapped_column()\n    created_at: Mapped[datetime] = mapped_column()\n    metric_name: Mapped[str] = mapped_column()\n    value: Mapped[float] = mapped_column()\n\n    __table_args__ = (\n        PrimaryKeyConstraint('id', 'created_at'),\n        {\n            'postgresql_partition_by': 'RANGE (created_at)',\n        }\n    )",
        "Declaring a range-partitioned PostgreSQL table using SQLAlchemy table_args and composite primary keys.",
        "When executing `select(MetricEvent).where(MetricEvent.created_at >= '2026-01-01')`, PostgreSQL's query optimizer evaluates partition boundaries and executes scans exclusively against the matched partition sub-tables, skipping all others (partition pruning).",
        "Time-series metrics, financial ledger logs, clickstream tracking, and IoT sensor telemetry.",
        ["Why must the partition key be part of the table's composite primary key in PostgreSQL?", "What is partition pruning in database query optimization?"],
        ["Attempting to enforce global unique constraints on non-partition columns in partitioned tables.", "Creating too many small partitions (e.g. hourly partitions over 10 years), which bloats PostgreSQL query planning time."],
        "Emphasize partition pruning: Always include the partition key in `WHERE` clauses to reap performance gains.",
        ["[PostgreSQL Optimization](../05-databases/postgresql.md)", "[Indexing](../05-databases/indexing-and-optimization.md)"],
        ["https://www.postgresql.org/docs/current/ddl-partitioning.html"]
    ),

    # FA-ADV-135
    (
        "FA-ADV-135",
        "Solving Memory Exhaustion During Massive Server-Side Cursor Exports",
        "Server-side cursors fetch query results incrementally from the database server buffer, preventing memory exhaustion when processing millions of rows in FastAPI.",
        "By default, database drivers buffer the complete query result into client-side RAM before handing it to Python. A query returning 5,000,000 rows can instantly consume 8GB of memory and trigger an OOM kill. Server-side cursors (created in asyncpg via `session.stream()`) stream rows over the network in configurable batch chunks (e.g., 2,000 rows at a time). Combined with Python generators, memory consumption remains constant (O(1)) regardless of total table size.",
        "from collections.abc import AsyncGenerator\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass LargeRecord(Base):\n    __tablename__ = 'large_records'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    data: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def stream_large_dataset(batch_size: int = 1000) -> AsyncGenerator[str, None]:\n    async with SessionLocal() as session:\n        # yield_per sets server-side cursor batch size\n        stmt = select(LargeRecord).execution_options(yield_per=batch_size)\n        async_result = await session.stream_scalars(stmt)\n        \n        async for record in async_result:\n            yield f'{record.id}:{record.data}\\n'",
        "Using execution_options(yield_per=1000) with session.stream_scalars for constant-memory data processing.",
        "`yield_per=1000` instructs the driver to declare a named database cursor (`DECLARE ... CURSOR FOR SELECT`). It executes `FETCH FORWARD 1000` sequentially, allowing garbage collection to reclaim memory from processed batches.",
        "Large-scale database dumps, data warehouse ETL pipelines, and generating multi-gigabyte regulatory audit reports.",
        ["What is the difference between client-side buffering and server-side cursors?", "How does `yield_per` affect network round-trips?"],
        ["Setting `yield_per` too small (e.g. 1), causing millions of tiny network round-trips and drastic performance degradation.", "Holding a server-side cursor open inside a transaction for hours, blocking vacuuming and causing table bloat."],
        "Recommend a `yield_per` value between 1,000 and 5,000 for an optimal balance between network round-trips and memory footprint.",
        ["[Streaming Responses](async-and-concurrency.md)", "[Performance Optimization](../01-python/internals-and-performance.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.yield_per"]
    ),

    # FA-ADV-136
    (
        "FA-ADV-136",
        "Concurrency Control and Deadlock Mitigation in Asynchronous FastAPI Backends",
        "Deadlocks occur when two transactions mutually wait for locks held by each other; they are prevented by uniform lock ordering and mitigated with automated retry handlers.",
        "In high-concurrency systems, if Transaction A locks Row 1 and attempts to lock Row 2, while Transaction B concurrently locks Row 2 and attempts to lock Row 1, a cyclic lock dependency (deadlock) occurs. The database engine detects this cycle and aborts one transaction with a serialization error (e.g., PostgreSQL `DeadlockDetected: 40P01`). Mitigation requires: 1) Ordering: Always acquire locks in a consistent, deterministic order (e.g., sort IDs before locking); 2) Short transactions: Never execute external HTTP calls or heavy computation inside lock transactions; 3) Retry decorators on deadlock error codes.",
        "from fastapi import FastAPI, Depends, HTTPException\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Inventory(Base):\n    __tablename__ = 'inventory'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    stock: Mapped[int] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/reserve-bundle')\nasync def reserve_bundle(item_ids: list[int], db: AsyncSession = Depends(get_db)):\n    # CRITICAL: Sort IDs to guarantee consistent lock acquisition order across all threads\n    sorted_ids = sorted(item_ids)\n    \n    async with db.begin():\n        # SELECT ... FOR UPDATE locked deterministically in ascending ID order\n        stmt = select(Inventory).where(Inventory.id.in_(sorted_ids)).with_for_update()\n        items = (await db.scalars(stmt)).all()\n        \n        for item in items:\n            if item.stock < 1:\n                raise HTTPException(status_code=400, detail=f'Item {item.id} out of stock')\n            item.stock -= 1\n            \n    return {'status': 'reserved', 'items': sorted_ids}",
        "Eliminating deadlocks during multi-row lock acquisition by sorting target IDs prior to locking.",
        "By enforcing that all transactions lock Row 1 before Row 2, cyclic dependencies are mathematically impossible, completely eliminating deadlocks between transactions that follow this protocol.",
        "High-volume inventory reservations, multi-account ledger transfers, and gaming matchmaking systems.",
        ["Why does sorting IDs before acquiring row locks eliminate the possibility of cyclic deadlocks?", "What is PostgreSQL's `deadlock_timeout` setting?"],
        ["Acquiring locks in arbitrary or user-supplied order, leading to intermittent deadlocks under high concurrency.", "Holding database locks while awaiting third-party payment gateway HTTP calls."],
        "Rule of thumb: Sort your keys before locking; never execute network I/O inside a locked database transaction.",
        ["[Pessimistic Locking](database-integration.md)", "[Transaction Isolation](../05-databases/transactions-and-isolation.md)"],
        ["https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS"]
    ),

    # FA-ADV-137
    (
        "FA-ADV-137",
        "Custom Pydantic v2 TypeAdapters and SQLAlchemy Hybrid Properties for Spatial/GIS Data",
        "Geographic/GIS data is handled in FastAPI by combining PostGIS geometry columns, SQLAlchemy `@hybrid_property`, and custom Pydantic v2 `TypeAdapter` validators.",
        "Handling spatial data (coordinates, GPS breadcrumbs, polygonal geofences) requires PostGIS. SQLAlchemy integrates PostGIS via `GeoAlchemy2` (`Geometry('POINT', srid=4326)`). To expose coordinates cleanly through FastAPI: 1) SQLAlchemy `@hybrid_property` exposes latitude and longitude as virtual attributes; 2) Pydantic v2 `TypeAdapter` or annotated schemas validate GeoJSON structures on incoming payloads and serialize coordinates on responses.",
        "from typing import Annotated\nfrom pydantic import BaseModel, ConfigDict, Field, PlainSerializer\nfrom sqlalchemy.ext.hybrid import hybrid_property\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass StoreLocation(Base):\n    __tablename__ = 'store_locations'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n    # Simulated latitude/longitude storage (in PostGIS this would be a Geometry column)\n    _lat: Mapped[float] = mapped_column('lat')\n    _lon: Mapped[float] = mapped_column('lon')\n\n    @hybrid_property\n    def coordinates(self) -> dict[str, float]:\n        return {'lat': self._lat, 'lon': self._lon}\n\nclass StoreResponse(BaseModel):\n    id: int\n    name: str\n    coordinates: dict[str, float]\n    model_config = ConfigDict(from_attributes=True)",
        "Mapping coordinate attributes via SQLAlchemy hybrid_property for clean Pydantic response serialization.",
        "The `@hybrid_property` decorator allows an attribute to behave as a Python instance method at runtime while also allowing it to be compiled into SQL expressions when used within `select().where()` clauses.",
        "Ride-sharing geofencing, delivery tracking, store locator APIs, and real estate mapping services.",
        ["What is an SRID (Spatial Reference System Identifier) in PostGIS?", "How do hybrid properties differ from standard Python `@property` getters in SQLAlchemy?"],
        ["Storing coordinates as unindexed floating point columns and attempting to calculate distances in Python rather than using PostGIS `ST_DWithin`.", "Forgetting `from_attributes=True` when serializing hybrid properties in Pydantic v2."],
        "Mention that PostGIS provides spatial R-Tree GiST indexes, enabling sub-millisecond proximity queries across millions of points.",
        ["[Pydantic Models](pydantic-and-validation.md)", "[PostgreSQL Extensions](../05-databases/postgresql.md)"],
        ["https://geoalchemy-2.readthedocs.io/"]
    ),

    # FA-ADV-138
    (
        "FA-ADV-138",
        "Managing Database Transaction Isolation Levels in Async FastAPI",
        "Transaction isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE) balance concurrency throughput against anomalies; they are configured per-engine or per-session in SQLAlchemy.",
        "Relational databases offer 4 ANSI standard isolation levels: 1) READ COMMITTED: Default in PostgreSQL; prevents dirty reads, but allows non-repeatable reads and phantom reads; 2) REPEATABLE READ: Guarantees that a transaction sees a snapshot of data as of the transaction start; prevents non-repeatable reads; 3) SERIALIZABLE: Strictest isolation; executes transactions as if run serially; aborts transactions on conflict. In FastAPI, isolation levels can be set globally on `create_async_engine(..., isolation_level='REPEATABLE READ')` or per-session via `session.connection(execution_options={'isolation_level': 'SERIALIZABLE'})`.",
        "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\n\nDATABASE_URL = 'postgresql+asyncpg://user:pass@localhost:5432/app'\n\n# Configure global engine default isolation level\nengine = create_async_engine(\n    DATABASE_URL,\n    isolation_level='REPEATABLE READ',\n)\n\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def run_strict_financial_transaction(db: AsyncSession):\n    # Override isolation level dynamically for a single transaction\n    async with db.begin():\n        await db.connection(execution_options={'isolation_level': 'SERIALIZABLE'})\n        # Strict serializable operations executed here",
        "Configuring engine-level isolation and dynamically overriding to SERIALIZABLE for financial transactions.",
        "PostgreSQL implements MVCC (Multi-Version Concurrency Control). In SERIALIZABLE isolation, PostgreSQL tracks read-write dependencies using Serializable Snapshot Isolation (SSI). If an SSI conflict is detected, it raises a `40001` serialization failure, requiring the client to retry.",
        "Double-entry bookkeeping ledgers, regulatory compliance audits, and financial trade settlement engines.",
        ["What concurrency anomalies are prevented by REPEATABLE READ compared to READ COMMITTED?", "What is a serialization failure (`40001`) and how should FastAPI handle it?"],
        ["Running entire applications on SERIALIZABLE isolation (drastically degrades throughput and causes constant serialization failures).", "Assuming READ COMMITTED prevents phantom reads or lost updates."],
        "Keep default READ COMMITTED for 95% of endpoints; selectively elevate to SERIALIZABLE or use pessimistic locking for sensitive mutations.",
        ["[Transaction Isolation](../05-databases/transactions-and-isolation.md)", "[Pessimistic Locking](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#setting-isolation-for-individual-sessions"]
    ),

    # FA-ADV-139
    (
        "FA-ADV-139",
        "Transactional Outbox Pattern in FastAPI and Async Message Brokers",
        "The Transactional Outbox pattern guarantees reliable event publishing to Kafka/RabbitMQ by persisting events to an outbox table within the same ACID database transaction as business mutations.",
        "When an API endpoint creates an order and publishes an event to RabbitMQ, a dual-write failure can occur: if the database commits but the network blip aborts the message broker call, the event is lost. Conversely, if the event is sent first and the database transaction fails, downstream services process a phantom order. The Transactional Outbox pattern solves this: an `outbox` record is written to the database in the *same* local transaction as the order. A background worker (or Debezium CDC) reads un-published outbox rows and dispatches them to the broker reliably.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nimport uuid\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Order(Base):\n    __tablename__ = 'orders'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    user_id: Mapped[int] = mapped_column()\n    total: Mapped[int] = mapped_column()\n\nclass OutboxEvent(Base):\n    __tablename__ = 'outbox_events'\n    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))\n    event_type: Mapped[str] = mapped_column()\n    payload: Mapped[str] = mapped_column()\n    processed: Mapped[bool] = mapped_column(default=False)\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/orders')\nasync def place_order(user_id: int, total: int, db: AsyncSession = Depends(get_db)):\n    async with db.begin():\n        # 1. Mutate business state\n        order = Order(user_id=user_id, total=total)\n        db.add(order)\n        \n        # 2. In the SAME transaction, write to outbox table (Guarantees At-Least-Once Delivery)\n        outbox = OutboxEvent(\n            event_type='OrderCreated',\n            payload=f'{{\"user_id\": {user_id}, \"total\": {total}}}'\n        )\n        db.add(outbox)\n        \n    return {'status': 'order_created'}",
        "Writing business entity and event message to the same atomic database transaction using the Outbox pattern.",
        "Because both writes participate in a single local ACID transaction, either both succeed or both roll back. A separate worker process polls the `outbox_events` table (or reads the WAL) and relays events to RabbitMQ with guaranteed at-least-once delivery.",
        "Mission-critical event-driven microservices where losing an event causes cross-service data divergence.",
        ["Why is publishing directly to RabbitMQ inside an HTTP route handler an anti-pattern?", "How does Debezium automate outbox event extraction from PostgreSQL WAL?"],
        ["Publishing to the message queue before committing the database transaction (phantom events).", "Publishing after committing without an outbox table (events lost if the process crashes before publishing)."],
        "Golden rule: Never dual-write to two independent systems (DB + Queue) without the Outbox pattern or two-phase commit.",
        ["[RabbitMQ Integration](../06-redis-and-messaging/rabbitmq.md)", "[Distributed Architecture](../10-system-design/distributed-systems.md)"],
        ["https://microservices.io/patterns/data/transactional-outbox.html"]
    ),

    # FA-ADV-140
    (
        "FA-ADV-140",
        "Designing CQRS (Command Query Responsibility Segregation) in FastAPI",
        "CQRS separates read models (optimized for query performance) from write models (optimized for business validation and domain constraints).",
        "In complex enterprise systems, a single database schema struggles to excel at both high-throughput transactional writes (requiring normalized 3NF schemas to prevent anomalies) and high-speed analytical queries (requiring denormalized views and pre-aggregated caches). CQRS splits operations into Commands (POST/PUT/DELETE: state mutations) and Queries (GET: read-only views). In FastAPI, Commands write to the primary database and trigger updates to a denormalized read model (e.g. Elasticsearch, Read Replica, or Redis), keeping query endpoints lightning fast.",
        "# Conceptual CQRS Architecture in FastAPI:\n# 1) Command Route (Write side):\n# @app.post('/orders')\n# async def create_order_command(cmd: CreateOrderCommand, uow = Depends(get_uow)):\n#     # Validates domain invariants, writes to normalized SQL tables, emits OrderCreated event\n#     await uow.orders.add(cmd.to_domain())\n#     await uow.commit()\n#\n# 2) Query Route (Read side):\n# @app.get('/orders/{order_id}')\n# async def get_order_query(order_id: str, search_client = Depends(get_elasticsearch)):\n#     # Reads directly from denormalized read-model optimized for instant lookups\n#     return await search_client.get(index='orders', id=order_id)",
        "Segregating write commands (normalized domain logic) from read queries (denormalized search store).",
        "Commands focus on data consistency, invariants, and state transitions. Queries bypass domain logic entirely, reading denormalized projection tables or search indexes with minimal latency and zero lock contention on the write database.",
        "E-commerce product search, social media feeds, and enterprise ERP systems.",
        ["What is eventual consistency in CQRS read models?", "When is CQRS an over-engineering anti-pattern?"],
        ["Introducing CQRS to simple CRUD applications that have low traffic and simple schemas.", "Assuming read models update synchronously with commands without handling eventual consistency lag."],
        "Emphasize: CQRS introduces complexity (eventual consistency, dual models); only use it when write and read scaling requirements diverge significantly.",
        ["[System Design Patterns](../10-system-design/fundamentals.md)", "[Distributed Architecture](../10-system-design/distributed-systems.md)"],
        ["https://martinfowler.com/bliki/CQRS.html"]
    ),

    # FA-ADV-141
    (
        "FA-ADV-141",
        "Connection Pooling Proxies: PgBouncer Transaction Pooling vs Client-Side Pooling",
        "PgBouncer in transaction pooling mode multiplexes thousands of incoming client connections over a small pool of actual PostgreSQL connections, scaling beyond PostgreSQL's native connection limits.",
        "PostgreSQL uses a process-per-connection architecture: each open connection consumes ~5-10MB of server RAM and creates OS process scheduling overhead. 1,000 direct connections can degrade PostgreSQL performance or trigger OOM. PgBouncer sits between FastAPI and PostgreSQL: 1) In Transaction Pooling mode, a database connection is only assigned to a client while a transaction is actively executing; once committed, the connection is immediately assigned to another request; 2) SQLAlchemy engines must use `NullPool` to avoid double pooling; 3) Prepared statements must be disabled or managed carefully because server connections change between transactions.",
        "# SQLAlchemy configuration for PgBouncer Transaction Pooling\nfrom sqlalchemy.ext.asyncio import create_async_engine\nfrom sqlalchemy.pool import NullPool\n\n# Pointing to PgBouncer port (default 6432)\nPGBOUNCER_URL = 'postgresql+asyncpg://user:pass@pgbouncer-host:6432/production'\n\nengine = create_async_engine(\n    PGBOUNCER_URL,\n    poolclass=NullPool,  # PgBouncer handles pooling; disable SQLAlchemy client pool\n    connect_args={\n        'statement_cache_size': 0,  # CRITICAL: Disable asyncpg prepared statement caching\n        'prepared_statement_cache_size': 0,\n    },\n)",
        "Configuring SQLAlchemy with NullPool and disabling asyncpg statement cache for PgBouncer transaction pooling.",
        "In transaction pooling, PgBouncer reassigns backend connections dynamically after every `COMMIT`/`ROLLBACK`. If `asyncpg` attempts to reuse a prepared statement handle cached for a previous connection, PostgreSQL throws an error (`prepared statement does not exist`). Disabling `statement_cache_size` fixes this compatibility issue.",
        "Kubernetes clusters running 100+ FastAPI pods connecting to a single PostgreSQL RDS instance.",
        ["Why must `statement_cache_size=0` be set when using asyncpg with PgBouncer transaction pooling?", "What PostgreSQL features are unsupported in PgBouncer transaction pooling mode (e.g., `LISTEN`/`NOTIFY`, session variables)?"],
        ["Enabling prepared statement caching with PgBouncer transaction pooling, causing random `DuplicatePreparedStatement` errors.", "Using Session Pooling instead of Transaction Pooling when connection scaling is the primary objective."],
        "Remember: With PgBouncer transaction pooling: Use `NullPool` in SQLAlchemy and set `statement_cache_size: 0` in asyncpg `connect_args`.",
        ["[PostgreSQL Tuning](../05-databases/postgresql.md)", "[Connection Pooling](database-integration.md)"],
        ["https://www.pgbouncer.org/features.html"]
    ),

    # FA-ADV-142
    (
        "FA-ADV-142",
        "PostgreSQL SSL/TLS Mutual Authentication (mTLS) with asyncpg in FastAPI",
        "mTLS encrypts database traffic and verifies client identity using x509 cryptographic certificates passed into asyncpg via Python's `ssl.SSLContext`.",
        "In zero-trust enterprise infrastructure and PCI-DSS/HIPAA environments, password-only database authentication is insufficient. Mutual TLS (mTLS) enforces that: 1) The client verifies the database server's TLS certificate against a trusted CA (preventing Man-in-the-Middle attacks); 2) The database server validates the client's x509 certificate and private key, granting access without transmitting passwords across the wire. In asyncpg, this is configured via `ssl.create_default_context()` passed into `connect_args['ssl']`.",
        "import ssl\nfrom sqlalchemy.ext.asyncio import create_async_engine\n\ndef create_mtls_ssl_context() -> ssl.SSLContext:\n    ctx = ssl.create_default_context(\n        purpose=ssl.Purpose.SERVER_AUTH,\n        cafile='/etc/ssl/certs/db-ca.pem'\n    )\n    # Load client certificate and private key for mutual TLS\n    ctx.load_cert_chain(\n        certfile='/etc/ssl/certs/client-cert.pem',\n        keyfile='/etc/ssl/certs/client-key.pem'\n    )\n    ctx.check_hostname = True\n    ctx.verify_mode = ssl.CERT_REQUIRED\n    return ctx\n\n# Configure async engine with mTLS SSL context\n# engine = create_async_engine(\n#     'postgresql+asyncpg://app_user@db.internal:5432/secure_db',\n#     connect_args={'ssl': create_mtls_ssl_context()},\n# )",
        "Configuring an ssl.SSLContext with client certificates for secure mTLS database authentication.",
        "During TCP handshake, the client and database server exchange certificates. OpenSSL verifies cryptographic signatures against the root CA. If valid, an ephemeral symmetric AES-GCM session key is established, encrypting all SQL statements and data payloads over the wire.",
        "Banking APIs, healthcare HIPAA-compliant patient databases, and government cloud deployments.",
        ["What is the difference between `sslmode=require` and `sslmode=verify-full` in PostgreSQL?", "Why does mTLS eliminate the risk of database credential theft from environment variables?"],
        ["Setting `check_hostname = False` in production, leaving connections susceptible to DNS spoofing and MITM attacks.", "Hardcoding private key file contents in source code rather than mounting them via Kubernetes secrets."],
        "Emphasize: `sslmode=verify-full` (or `check_hostname = True` in Python) verifies both certificate validity and host identity.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://magicstack.github.io/asyncpg/current/api/index.html#connection-ssl"]
    ),

    # FA-ADV-143
    (
        "FA-ADV-143",
        "Asynchronous Background Worker Database Sessions Outside HTTP Request Contexts",
        "Background workers (Celery, ARQ, or asyncio tasks) must create their own independent database sessions and engines, never sharing sessions from HTTP request contexts.",
        "Passing a request-scoped `AsyncSession` into `BackgroundTasks.add_task()` or Celery is a critical concurrency bug: once the HTTP response returns, FastAPI's dependency cleanup closes the session. If the background worker attempts to execute queries using that closed session, it crashes with `StatementError: session is closed`. Furthermore, in Celery or multiprocessing workers, sharing an engine across forked processes corrupts socket handles. Background workers must create their own session contexts using a dedicated sessionmaker.",
        "from fastapi import FastAPI, BackgroundTasks, Depends\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass TaskLog(Base):\n    __tablename__ = 'task_logs'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    msg: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionFactory = async_sessionmaker(engine, expire_on_commit=False)\n\n# SAFE Background worker task creating its OWN isolated session\nasync def background_log_task(message: str):\n    async with SessionFactory() as session:\n        async with session.begin():\n            session.add(TaskLog(msg=message))\n\napp = FastAPI()\n\n@app.post('/trigger-job')\nasync def trigger_job(bg_tasks: BackgroundTasks):\n    # DO NOT pass the request-scoped session into the background task!\n    bg_tasks.add_task(background_log_task, 'Job completed successfully')\n    return {'status': 'queued'}",
        "Scoping database sessions independently inside background tasks to avoid closed session errors.",
        "The background task executes asynchronously on the event loop after the HTTP response has already completed and returned to the client. By instantiating `async with SessionFactory()`, the worker acquires its own clean connection from the pool and handles its own commit/close lifecycle safely.",
        "Email dispatch audit logging, analytics aggregation, and report generation triggered via HTTP endpoints.",
        ["What happens if you pass an active `db: AsyncSession` directly into `BackgroundTasks.add_task`?", "Why does `os.fork()` in Celery workers break SQLAlchemy connection pools?"],
        ["Passing request-scoped database sessions to background threads or tasks, causing `InterfaceError: connection closed`.", "Sharing an un-disposed engine across process forks, leading to shared file descriptor race conditions."],
        "Remember: Request lifecycle != Background task lifecycle. Always instantiate a fresh session inside background tasks.",
        ["[Background Tasks](async-and-concurrency.md)", "[Celery Integration](../06-redis-and-messaging/celery.md)"],
        ["https://fastapi.tiangolo.com/tutorial/background-tasks/#caveat"]
    ),

    # FA-ADV-144
    (
        "FA-ADV-144",
        "Multi-Level Distributed Caching (L1 Local / L2 Redis) with Database Invalidation",
        "A multi-level cache serves ultra-hot reads from an in-memory L1 cache (< 100ns) and falls back to distributed L2 Redis (< 1ms) before querying the relational database.",
        "In extreme-scale systems (millions of RPS), even Redis network round-trips can become a bottleneck. Multi-level caching introduces: 1) L1 Cache: In-process memory (e.g. `cachetools` or Python dict with TTL) inside each FastAPI worker process (sub-microsecond access); 2) L2 Cache: Distributed Redis cluster shared across all workers and pods; 3) Source of Truth: Relational database. When mutations occur, a Redis Pub/Sub broadcast invalidates the L1 cache in all running FastAPI worker processes simultaneously.",
        "# Conceptual Multi-Level Caching Architecture:\n# L1: Local in-memory dict/LRU cache per worker (TTL: 10s)\n# L2: Redis cluster shared across all pods (TTL: 1 hour)\n# L3: PostgreSQL database\n\n# async def get_product(product_id: int) -> dict:\n#     # 1. Check L1 local process cache\n#     if product_id in L1_CACHE:\n#         return L1_CACHE[product_id]\n#     \n#     # 2. Check L2 Redis cache\n#     cached = await redis.get(f'product:{product_id}')\n#     if cached:\n#         L1_CACHE[product_id] = json.loads(cached)\n#         return L1_CACHE[product_id]\n#         \n#     # 3. Cache Miss: Query PostgreSQL\n#     async with SessionLocal() as db:\n#         product = await db.get(Product, product_id)\n#         data = {'id': product.id, 'name': product.name}\n#         await redis.setex(f'product:{product_id}', 3600, json.dumps(data))\n#         L1_CACHE[product_id] = data\n#         return data",
        "Conceptual implementation of L1 in-memory / L2 Redis / L3 Database multi-tier caching hierarchy.",
        "L1 eliminates network socket serialization overhead for hot items (e.g. viral homepage banners). Redis Pub/Sub invalidation channels ensure that when an item is updated, an invalidation message evicts the item from L1 memory across all running worker processes.",
        "Flash sales, breaking news headlines, and live sports scores handling 100,000+ requests per second.",
        ["How do you solve L1 cache divergence across 50 Kubernetes pods without Redis Pub/Sub invalidation?", "What is Cache Stampede and how does probabilistic early expiration (XFetch) mitigate it?"],
        ["Using long TTLs on L1 in-process caches without an invalidation mechanism (serves stale data for minutes).", "Failing to bound L1 memory size with an LRU policy, leading to container OOM crashes."],
        "Emphasize: L1 cache provides extreme read throughput, but MUST be bounded in size (LRU) and have short TTLs or Pub/Sub invalidation.",
        ["[Redis Caching](../06-redis-and-messaging/redis.md)", "[Scalability](../10-system-design/scalability-and-performance.md)"],
        ["https://en.wikipedia.org/wiki/Cache_hierarchy"]
    ),

    # FA-ADV-145
    (
        "FA-ADV-145",
        "Automated Query Plan Analysis (`EXPLAIN ANALYZE`) and Slow Query Alerting",
        "Automated profiling captures query execution plans using `EXPLAIN (ANALYZE, BUFFERS)` to detect sequential scans and missing indexes during automated testing or staging runs.",
        "A query that runs in 2ms on a developer's 100-row database might take 15 seconds on a 10,000,000-row production table due to missing indexes. By executing `EXPLAIN (ANALYZE, BUFFERS) <query>`, developers inspect the database engine's query execution plan. Key warning signs include `Seq Scan` (full table sequential scan on large tables), high `Buffers: shared hit/read` counts, and inefficient nested loops. Automated CI/CD integration tests can assert that core query execution plans use index scans (`Index Scan` or `Bitmap Index Scan`).",
        "from sqlalchemy import text\nfrom sqlalchemy.ext.asyncio import create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\n\nasync def analyze_query_plan(sql_query: str):\n    async with engine.connect() as conn:\n        # On SQLite use 'EXPLAIN QUERY PLAN'; on PostgreSQL use 'EXPLAIN (ANALYZE, BUFFERS)'\n        result = await conn.execute(text(f'EXPLAIN QUERY PLAN {sql_query}'))\n        plan = result.fetchall()\n        for step in plan:\n            print(f'Execution Plan Step: {step}')",
        "Inspecting database execution plan programmatically using EXPLAIN QUERY PLAN.",
        "The database query optimizer evaluates multiple execution strategies (hash joins, merge joins, index scans) and chooses the one with the lowest estimated cost. `EXPLAIN ANALYZE` executes the query and compares estimated costs against actual execution times and buffer page accesses.",
        "Automated database performance regression testing in CI/CD pipelines before deploying to production.",
        ["What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?", "What does a `Seq Scan` on a table with 10 million rows indicate?"],
        ["Running `EXPLAIN ANALYZE` on destructive queries like `DELETE` or `UPDATE` in production without a transaction rollback (it executes the statement!).", "Relying solely on local dev SQLite plans to predict PostgreSQL production behavior."],
        "Caution: `EXPLAIN` only plans; `EXPLAIN ANALYZE` ACTUALLY EXECUTES the query. Never run `EXPLAIN ANALYZE UPDATE/DELETE` in production without wrapping in a rolled-back transaction.",
        ["[PostgreSQL Tuning](../05-databases/postgresql.md)", "[Indexing](../05-databases/indexing-and-optimization.md)"],
        ["https://www.postgresql.org/docs/current/using-explain.html"]
    ),

    # FA-ADV-146
    (
        "FA-ADV-146",
        "Zero-Downtime Blue-Green Database Schema Migrations and Backward Compatibility",
        "Blue-Green deployments run old (Blue) and new (Green) application versions simultaneously against the same database, requiring database migrations to remain strictly backward and forward compatible.",
        "In a Blue-Green deployment, the Green environment is deployed with the new code while the Blue environment continues serving live traffic. Once Green is healthy, the load balancer switches traffic. Because both Blue and Green share the same production database during cutover and potential rollback: 1) The database schema must be backward-compatible with Blue; 2) The schema must be forward-compatible with Green; 3) No column can be dropped or renamed until Blue is completely decommissioned and the rollback window has closed.",
        "# Blue-Green compatibility rules:\n# 1. Adding columns: MUST be nullable OR have a database-level DEFAULT.\n# 2. Deleting columns: Application must stop reading the column 1 release BEFORE dropping it.\n# 3. Renaming columns: Treat as Add new column + Dual write + Backfill + Drop old column.\n# 4. Table splits: Use SQL views to present the legacy table structure to the Blue app.",
        "Core design rules for maintaining backward and forward schema compatibility during Blue-Green deployments.",
        "By enforcing that all schema changes are additive (expanding) rather than destructive (contracting), old application pods can continue executing queries without throwing missing column or constraint violation errors during the deployment transition.",
        "High-reliability enterprise services requiring zero dropped requests and instant 1-second rollback capabilities.",
        ["What happens to the Blue application if Green applies a migration that drops an active column?", "How can SQL Views preserve backward compatibility for deprecated tables?"],
        ["Applying destructive migrations before switching traffic from Blue to Green, breaking the live Blue environment.", "Assuming instant rollback is possible if non-backward-compatible database changes have already been applied."],
        "Golden rule of Blue-Green: All database migrations MUST support the previous version of the application code.",
        ["[Zero-Downtime Migrations](database-integration.md)", "[DevOps Blue-Green](../11-devops/ci-cd.md)"],
        ["https://martinfowler.com/bliki/BlueGreenDeployment.html"]
    ),

    # FA-ADV-147
    (
        "FA-ADV-147",
        "Integrating Vector Databases (`pgvector`) for AI Embeddings Alongside Relational Data",
        "PostgreSQL's `pgvector` extension allows storing and querying high-dimensional vector embeddings (e.g. OpenAI or Gemini embeddings) directly alongside relational models in FastAPI.",
        "Modern AI-enabled FastAPI applications frequently combine structured business data (users, permissions, orders) with vector embeddings for semantic search or Retrieval-Augmented Generation (RAG). Using a separate vector database (Pinecone, Weaviate) introduces dual-write consistency issues and extra infrastructure costs. `pgvector` adds a native `vector` data type and indexing (HNSW, IVFFlat) to PostgreSQL. In SQLAlchemy 2.0, `pgvector.sqlalchemy.Vector` maps vector columns, supporting cosine distance (`<=>`) and L2 distance (`<->`) queries.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import select\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n# from pgvector.sqlalchemy import Vector\n\nclass Base(DeclarativeBase):\n    pass\n\nclass DocumentChunk(Base):\n    __tablename__ = 'document_chunks'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    content: Mapped[str] = mapped_column()\n    # In pgvector: embedding: Mapped[list[float]] = mapped_column(Vector(1536))\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n# Querying nearest neighbors using cosine similarity (<=> operator in PostgreSQL)\n# stmt = select(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(query_vector)).limit(5)",
        "Configuring vector embeddings alongside relational data in SQLAlchemy and querying nearest neighbors.",
        "`pgvector` builds an HNSW (Hierarchical Navigable Small World) graph or IVFFlat index directly inside PostgreSQL storage. Nearest-neighbor searches traverse the graph index in logarithmic time, returning relevant document chunks alongside relational foreign key data in a single ACID query.",
        "Semantic search endpoints, AI knowledge base Q&A, and recommendation engines in FastAPI.",
        ["What is the difference between HNSW and IVFFlat index types in pgvector?", "What are the advantages of pgvector over standalone vector databases like Pinecone?"],
        ["Building an IVFFlat index on an empty table (IVFFlat requires training on existing data; HNSW does not).", "Storing vector embeddings without an index, resulting in linear scans across high-dimensional vectors."],
        "Emphasize: `pgvector` allows combining vector similarity search with relational filters (`WHERE user_id = :id`) in a single SQL query.",
        ["[PostgreSQL Features](../05-databases/postgresql.md)", "[Gemini API Dev](../01-python/fundamentals.md)"],
        ["https://github.com/pgvector/pgvector"]
    ),

    # FA-ADV-148
    (
        "FA-ADV-148",
        "Building an Automated Audit Logging Subsystem via SQLAlchemy ORM Mapper Events",
        "SQLAlchemy ORM mapper events (`after_insert`, `after_update`, `after_delete`) intercept database modifications to record automated, tamper-evident audit trails.",
        "Regulatory standards (SOC 2, HIPAA, GDPR) mandate recording an immutable audit log whenever sensitive data is created, modified, or deleted. Manually writing audit log code inside every FastAPI route is error-prone. SQLAlchemy provides mapper event hooks (`event.listens_for`) that intercept session flushes. By inspecting `session.dirty`, `session.new`, and `session.deleted`, the audit subsystem records the timestamp, user ID, previous values, and new values into an `audit_logs` table automatically.",
        "from datetime import datetime, timezone\nfrom sqlalchemy import event\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass AuditLog(Base):\n    __tablename__ = 'audit_logs'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    table_name: Mapped[str] = mapped_column()\n    action: Mapped[str] = mapped_column()  # INSERT, UPDATE, DELETE\n    record_id: Mapped[int] = mapped_column()\n    changed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))\n\nclass SecureRecord(Base):\n    __tablename__ = 'secure_records'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    data: Mapped[str] = mapped_column()\n\n# Intercept inserts automatically\n@event.listens_for(SecureRecord, 'after_insert')\ndef log_insert(mapper, connection, target):\n    connection.execute(\n        AuditLog.__table__.insert().values(\n            table_name='secure_records',\n            action='INSERT',\n            record_id=target.id,\n            changed_at=datetime.now(timezone.utc)\n        )\n    )",
        "Automating audit trail creation using SQLAlchemy ORM after_insert mapper event listeners.",
        "The mapper event fires during `session.flush()`, executing within the exact same database transaction as the primary mutation. If the primary insert fails or rolls back, the audit log entry is rolled back too, guaranteeing 100% audit accuracy.",
        "Enterprise compliance auditing, financial transaction ledgers, and administrative access tracking.",
        ["Why must audit log insertions participate in the same transaction as the target mutation?", "How do you capture the authenticated user's ID inside an ORM event listener?"],
        ["Writing audit logs asynchronously outside the transaction, risking missing audit records if the app crashes.", "Generating audit logs in HTTP routers instead of database hooks, leaving direct database modifications un-audited."],
        "Pass user context to the session using `session.info['user_id'] = current_user.id`, which is accessible inside event listeners.",
        ["[Security Compliance](../12-security/application-security.md)", "[ORM Events](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/events.html#mapper-events"]
    ),

    # FA-ADV-149
    (
        "FA-ADV-149",
        "High-Concurrency Ticket Booking / Inventory Reservation Race Condition Prevention",
        "Preventing overselling under high concurrency requires atomic database-level operations (`UPDATE inventory SET stock = stock - 1 WHERE id = :id AND stock > 0`) or Redis distributed locks.",
        "When 10,000 users click 'Buy Ticket' for the last remaining 100 seats within the same second, naive application code (`if item.stock > 0: item.stock -= 1`) fails due to race conditions, selling hundreds of phantom tickets. To guarantee zero overselling: 1) Atomic SQL Update: Execute `UPDATE items SET stock = stock - qty WHERE id = :id AND stock >= qty RETURNING stock`. If rows updated = 0, stock is exhausted; 2) Redis Lua Scripting: Atomically decrement a Redis counter before hitting the database; 3) Database Pessimistic Locking: `SELECT stock FROM items WHERE id = :id FOR UPDATE`.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom sqlalchemy import text\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/tickets/{ticket_id}/reserve')\nasync def reserve_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):\n    # ATOMIC conditional update: Prevents race condition without explicit pessimistic locks\n    stmt = text('''\n        UPDATE tickets\n        SET available_seats = available_seats - 1\n        WHERE id = :ticket_id AND available_seats > 0\n    ''')\n    result = await db.execute(stmt, {'ticket_id': ticket_id})\n    await db.commit()\n    \n    if result.rowcount == 0:\n        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Tickets sold out!')\n        \n    return {'status': 'reserved', 'ticket_id': ticket_id}",
        "Preventing overselling race conditions using single atomic conditional SQL UPDATE statement.",
        "The database's internal row lock guarantees that only one transaction modifies the row at any instant. Because the condition `AND available_seats > 0` is evaluated inside the engine's write lock, overselling is physically impossible at the storage layer.",
        "Flash sale platforms, concert ticket booking systems, airline seat allocation, and limited-edition product drops.",
        ["Why is an atomic conditional `UPDATE` faster than `SELECT ... FOR UPDATE` followed by `UPDATE`?", "How can Redis Lua scripts throttle traffic before it reaches the relational database?"],
        ["Reading stock with `SELECT`, checking `stock > 0` in Python, and then issuing `UPDATE` (classic check-then-act race condition).", "Relying on application-level Python locks (`asyncio.Lock`), which only work within a single process and fail across multiple Uvicorn workers."],
        "Emphasize: Python `asyncio.Lock` does NOT protect against concurrency across multiple worker processes or Kubernetes pods; always enforce race safety at the database or Redis layer.",
        ["[Pessimistic Locking](database-integration.md)", "[Redis Atomic Operations](../06-redis-and-messaging/redis.md)"],
        ["https://www.postgresql.org/docs/current/sql-update.html"]
    ),

    # FA-ADV-150
    (
        "FA-ADV-150",
        "Architecting Database Resilience: Circuit Breakers, Fallback Caches, and Graceful Degradation",
        "Resilient FastAPI backends integrate Circuit Breakers to stop sending queries to an overloaded database, serving degraded responses from cache or fallback stores.",
        "When a database experiences severe latency spikes or an outage, incoming API requests continue hammering the database, piling up in connection queues and eventually taking down the entire web service (cascading failure). A Circuit Breaker (e.g. using `pybreaker` or custom asyncio state machines) monitors error rates and query timeouts: 1) Closed: Normal operation; 2) Open: Database calls are tripped and fail immediately without touching the database; responses are served from fallback Redis caches or default placeholders; 3) Half-Open: Periodic test queries verify if the database has recovered.",
        "from fastapi import FastAPI, Depends\nimport time\n\nclass CircuitBreaker:\n    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):\n        self.threshold = failure_threshold\n        self.recovery_timeout = recovery_timeout\n        self.state = 'CLOSED'\n        self.failure_count = 0\n        self.last_failure_time = 0.0\n\n    def record_failure(self):\n        self.failure_count += 1\n        self.last_failure_time = time.time()\n        if self.failure_count >= self.threshold:\n            self.state = 'OPEN'\n\n    def record_success(self):\n        self.state = 'CLOSED'\n        self.failure_count = 0\n\n    def can_execute(self) -> bool:\n        if self.state == 'CLOSED':\n            return True\n        if self.state == 'OPEN' and (time.time() - self.last_failure_time) > self.recovery_timeout:\n            self.state = 'HALF-OPEN'\n            return True\n        return False\n\ndb_breaker = CircuitBreaker()\napp = FastAPI()\n\n@app.get('/catalog')\nasync def get_catalog():\n    if not db_breaker.can_execute():\n        # Graceful degradation: Serve stale cache or fallback response\n        return {'status': 'degraded', 'items': [{'id': 0, 'name': 'Popular Items (Cached)'}]}\n    \n    try:\n        # Simulated database query\n        db_breaker.record_success()\n        return {'status': 'live', 'items': [{'id': 1, 'name': 'Item A'}]}\n    except Exception:\n        db_breaker.record_failure()\n        return {'status': 'fallback', 'items': []}",
        "Implementing a Circuit Breaker pattern with graceful degradation and cached fallback responses.",
        "When the database is unresponsive, the Circuit Breaker trips to `OPEN`. Subsequent requests return instantly in < 1ms from cache, preventing connection pool exhaustion and allowing the database time to recover from load spikes.",
        "Tier-1 e-commerce platforms, streaming service homepages, and payment gateways requiring high availability.",
        ["What are the three states of a Circuit Breaker pattern (CLOSED, OPEN, HALF-OPEN)?", "What is graceful degradation in distributed web systems?"],
        ["Allowing hundreds of requests per second to continue waiting for 30-second database timeouts during an outage, hanging all worker processes.", "Failing to implement a HALF-OPEN probing state to automatically resume normal operations when the database recovers."],
        "Remember: It is vastly better to return a degraded or cached response in 5ms than to hang for 30s and return a 504 Gateway Timeout.",
        ["[Resilience Architecture](../10-system-design/fundamentals.md)", "[Redis Caching](../06-redis-and-messaging/redis.md)"],
        ["https://martinfowler.com/bliki/CircuitBreaker.html"]
    ),
]
