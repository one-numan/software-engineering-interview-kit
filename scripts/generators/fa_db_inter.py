"""
fa_db_inter.py
==============
Intermediate FastAPI Database Integration Questions: FA-INT-126 to FA-INT-150 (25 questions)
"""

inter_data = [
    # FA-INT-126
    (
        "FA-INT-126",
        "Database Transaction Management with `session.begin()` in FastAPI",
        "Explicit transaction management in SQLAlchemy 2.0 is achieved using `async with session.begin():`, which automatically commits on success and rolls back on unhandled exceptions.",
        "While manual `await session.commit()` works, wrapping transactional units of work in `async with session.begin():` provides robust, atomic guarantees. If any error occurs inside the block, SQLAlchemy automatically triggers `ROLLBACK` and closes the transaction scope. If the block completes successfully without exceptions, it issues a `COMMIT`. This pattern enforces ACID properties across multiple database mutations without requiring verbose `try/except/rollback` boilerplate.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Wallet(Base):\n    __tablename__ = 'wallets'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    balance: Mapped[int] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/transfer')\nasync def transfer_funds(sender_id: int, receiver_id: int, amount: int, db: AsyncSession = Depends(get_db)):\n    async with db.begin():  # Manages BEGIN, COMMIT, and ROLLBACK automatically\n        sender = (await db.scalars(select(Wallet).where(Wallet.id == sender_id))).one_or_none()\n        receiver = (await db.scalars(select(Wallet).where(Wallet.id == receiver_id))).one_or_none()\n        \n        if not sender or not receiver:\n            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Wallet not found')\n        if sender.balance < amount:\n            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient funds')\n            \n        sender.balance -= amount\n        receiver.balance += amount\n        \n    return {'status': 'transferred', 'amount': amount}",
        "Atomic wallet fund transfer executed inside an explicit async with db.begin() context manager.",
        "Entering `async with db.begin()` issues a SQL `BEGIN` command. The session tracks object modifications in its Identity Map. Upon exiting the context block, SQLAlchemy flushes all changes and issues `COMMIT`. If an exception like `HTTPException` is raised, it issues `ROLLBACK` prior to propagating the exception.",
        "Financial systems, inventory deductions, multi-table booking operations where partial writes would cause data corruption.",
        ["What happens if an exception is raised inside the `async with db.begin()` block?", "Can you nest multiple `db.begin()` blocks within the same session?"],
        ["Calling `await db.commit()` manually inside an `async with db.begin()` block, causing an InvalidRequestError.", "Assuming database transactions span across external HTTP API calls without distributed saga coordination."],
        "Explain that `async with session.begin()` guarantees atomicity by automatically rolling back if any exception escapes the block.",
        ["[Transaction Isolation](../05-databases/transactions-and-isolation.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#framing-out-a-begin-commit-rollback-block"]
    ),

    # FA-INT-127
    (
        "FA-INT-127",
        "Connection Pooling Mechanics (`QueuePool`, `pool_size`, `max_overflow`, `pool_recycle`)",
        "SQLAlchemy's `QueuePool` manages persistent database socket connections, configured by pool size, overflow allowance, idle connection timeouts, and pre-ping validation.",
        "Establishing a new TCP/TLS database connection is an expensive operation involving OS handshakes, authentication, and backend process spawning (especially on PostgreSQL). A connection pool maintains an internal queue of open connections that are checked out by incoming requests and returned upon request completion. Key parameters include: 1) `pool_size`: The steady-state number of persistent connections; 2) `max_overflow`: The maximum number of temporary connections created when all pooled connections are busy; 3) `pool_recycle`: Periodically re-creates connections after a set number of seconds to prevent firewall drops; 4) `pool_timeout`: Seconds to wait before raising a TimeoutError when the pool is exhausted.",
        "from sqlalchemy.ext.asyncio import create_async_engine\nfrom sqlalchemy.pool import AsyncAdaptedQueuePool\n\nDATABASE_URL = 'postgresql+asyncpg://user:pass@localhost:5432/app_db'\n\nengine = create_async_engine(\n    DATABASE_URL,\n    poolclass=AsyncAdaptedQueuePool,\n    pool_size=20,         # Keep 20 persistent connections open\n    max_overflow=10,      # Allow up to 10 extra temporary connections during bursts\n    pool_timeout=30,      # Wait up to 30s for an available connection\n    pool_recycle=1800,    # Recycle connections older than 30 minutes\n    pool_pre_ping=True,   # Verify connection liveness with SELECT 1 before checkout\n)",
        "Configuring an AsyncAdaptedQueuePool with bounded capacity, timeouts, and recycling.",
        "When a coroutine requests a connection, `QueuePool` pops an available connection from its queue. If the queue is empty and total connections < `pool_size + max_overflow`, a new connection is spawned. If the pool is completely full, the coroutine awaits until a connection is returned or `pool_timeout` expires.",
        "High-concurrency API servers operating behind load balancers with fluctuating traffic surges.",
        ["What happens when `pool_size + max_overflow` is exceeded?", "How does `pool_recycle` prevent 'server closed the connection unexpectedly' errors?"],
        ["Setting `pool_size` too high without checking the database server's `max_connections` (causes PostgreSQL out of connection errors).", "Using `NullPool` in production when persistent connections are needed for low latency."],
        "Calculate pool capacity carefully: `(Uvicorn workers) * (pool_size + max_overflow)` must remain below the database server's `max_connections`.",
        ["[Async Engine Setup](database-integration.md)", "[PostgreSQL Tuning](../05-databases/postgresql.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/pooling.html"]
    ),

    # FA-INT-128
    (
        "FA-INT-128",
        "Solving the N+1 Query Problem in FastAPI with `selectinload` vs `joinedload`",
        "The N+1 problem occurs when fetching related records causes N secondary queries; it is resolved in async SQLAlchemy using relationship loading strategies like `selectinload` and `joinedload`.",
        "In relational mapping, loading 50 parent records (1 query) and iterating over their child collections triggers 50 separate queries (N+1 queries). In async SQLAlchemy, implicit lazy loading is disabled and raises `MissingGreenlet`. To eagerly load relationships in async FastAPI: 1) `selectinload(Model.relationship)`: Issues a primary query followed by a single secondary query using `WHERE parent_id IN (...)`. Best for 1-to-many and many-to-many collections; 2) `joinedload(Model.relationship)`: Employs a SQL `LEFT OUTER JOIN` in a single query. Best for many-to-one and one-to-one scalar relationships.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import select, ForeignKey\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Author(Base):\n    __tablename__ = 'authors'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n    books: Mapped[list['Book']] = relationship(back_populates='author')\n\nclass Book(Base):\n    __tablename__ = 'books'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))\n    author: Mapped['Author'] = relationship(back_populates='books')\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/authors-with-books')\nasync def get_authors(db: AsyncSession = Depends(get_db)):\n    # selectinload executes 2 queries regardless of author count (solves N+1)\n    stmt = select(Author).options(selectinload(Author.books))\n    authors = (await db.scalars(stmt)).all()\n    return [{'name': a.name, 'books': [b.title for b in a.books]} for a in authors]",
        "Eagerly loading child collections with selectinload to prevent N+1 queries and MissingGreenlet exceptions.",
        "`selectinload` first executes `SELECT id, name FROM authors`. It collects all returned author primary keys `[1, 2, 3...]` and immediately executes a second query: `SELECT id, title, author_id FROM books WHERE author_id IN (1, 2, 3...)`, populating the in-memory collections without Cartesian duplication.",
        "Endpoints returning nested data structures like blog posts with comments, users with roles, or invoices with line items.",
        ["Why is `joinedload` inefficient for loading 1-to-many collections with thousands of child records?", "What error does SQLAlchemy raise if you access an unloaded relationship in async mode?"],
        ["Using `joinedload` on large collections, which creates Cartesian product row multiplication and excessive bandwidth overhead.", "Forgetting relationship options and accessing `author.books` in response serialization, triggering `MissingGreenlet`."],
        "Rule of thumb: Use `selectinload` for collections (1-to-N); use `joinedload` for single objects (N-to-1).",
        ["[SQLAlchemy Relationships](database-integration.md)", "[Query Optimization](../05-databases/indexing-and-optimization.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loading-techniques"]
    ),

    # FA-INT-129
    (
        "FA-INT-129",
        "Setting Up Alembic for Asynchronous Database Migrations with FastAPI",
        "Alembic manages version-controlled database schema migrations, configured to run asynchronously by utilizing `connectable = async_engine_from_config` inside `env.py`.",
        "Alembic is SQLAlchemy's official schema migration tool. By default, `alembic init` generates a synchronous `env.py`. For FastAPI async projects, running `alembic init -t async migrations` creates an async-aware template. In this template, `env.py` imports `async_engine_from_config`, creates an `AsyncEngine`, and executes migration operations using `await connection.run_sync(do_run_migrations)`.",
        "# alembic/env.py async snippet:\n# import asyncio\n# from sqlalchemy.ext.asyncio import async_engine_from_config\n# from alembic import context\n# from app.models import Base  # Import DeclarativeBase metadata\n#\n# target_metadata = Base.metadata\n#\n# def do_run_migrations(connection):\n#     context.configure(connection=connection, target_metadata=target_metadata)\n#     with context.begin_transaction():\n#         context.run_migrations()\n#\n# async def run_async_migrations():\n#     connectable = async_engine_from_config(\n#         config.get_section(config.config_ini_section, {}),\n#         prefix='sqlalchemy.',\n#         poolclass=pool.NullPool,\n#     )\n#     async with connectable.connect() as connection:\n#         await connection.run_sync(do_run_migrations)\n#     await connectable.dispose()\n#\n# def run_migrations_online():\n#     asyncio.run(run_async_migrations())",
        "Key structure of an async-enabled Alembic env.py configured with target metadata and NullPool.",
        "`env.py` runs inside a standard Python process invoked by the `alembic` CLI. It spawns an event loop via `asyncio.run()`, opens an async connection, and executes Alembic's DDL generator synchronously through the `run_sync` greenlet bridge.",
        "Managing version-controlled database schema upgrades across local development, CI/CD pipelines, and production clusters.",
        ["What command initializes an async Alembic environment?", "Why is `target_metadata = Base.metadata` required for autogenerate?"],
        ["Running `alembic init` without `-t async`, resulting in driver incompatibility errors when using `postgresql+asyncpg`.", "Forgetting to import all DeclarativeBase model files into `env.py`, causing `alembic revision --autogenerate` to detect zero changes."],
        "Emphasize that `target_metadata` MUST import all model classes so Alembic can discover the declared tables for autogeneration.",
        ["[Lifespan Events](async-and-concurrency.md)", "[Database Normalization](../05-databases/database-design.md)"],
        ["https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic"]
    ),

    # FA-INT-130
    (
        "FA-INT-130",
        "Autogenerating Alembic Migrations and Programmatic Execution",
        "Alembic detects schema discrepancies between ORM models and the database via `alembic revision --autogenerate -m '...'` and can be executed programmatically using `alembic.command`.",
        "Autogeneration compares the `target_metadata` object (defined by SQLAlchemy models) against the actual live database schema inspectable via the connection. Alembic detects added/removed tables, columns, indexes, and primary keys, generating a migration script containing `upgrade()` and `downgrade()` instructions. In addition to CLI usage, FastAPI services can run migrations programmatically during automated testing or entrypoint startup using `alembic.command.upgrade()`.",
        "import os\nfrom alembic.config import Config\nfrom alembic import command\n\ndef run_migrations_programmatically(db_url: str):\n    alembic_cfg = Config('alembic.ini')\n    alembic_cfg.set_main_option('sqlalchemy.url', db_url)\n    # Run all pending migrations up to head\n    command.upgrade(alembic_cfg, 'head')\n\n# CLI equivalent commands:\n# alembic revision --autogenerate -m 'create users table'\n# alembic upgrade head\n# alembic downgrade -1",
        "Programmatically executing Alembic migrations via Python code and standard CLI command equivalents.",
        "Alembic maintains an `alembic_version` table in the target database storing a single revision hash string. When `upgrade head` is called, Alembic constructs a Directed Acyclic Graph (DAG) of migration revisions and executes all unapplied scripts in sequence within a transaction.",
        "Container entrypoint scripts in Docker Compose and Kubernetes init containers ensuring schemas are up to date before launching pods.",
        ["What schema alterations does Alembic autogenerate FAIL to detect by default?", "Why should programmatic migrations generally NOT be run inside multiple parallel app pods?"],
        ["Assuming Alembic automatically detects column name changes (it sees them as a column drop and a column add, risking data loss).", "Running `alembic upgrade head` in parallel across 10 Uvicorn worker pods at startup, causing race conditions on the migration lock."],
        "Always review autogenerated migration scripts before committing; check for column renames that might cause accidental data deletion.",
        ["[Alembic Setup](database-integration.md)", "[Docker Entrypoints](../11-devops/docker.md)"],
        ["https://alembic.sqlalchemy.org/en/latest/autogenerate.html"]
    ),

    # FA-INT-131
    (
        "FA-INT-131",
        "Handling Connection Timeouts and `pool_pre_ping=True`",
        "`pool_pre_ping=True` performs an optimistic health-check query before leasing a connection from the pool, preventing 'MySQL server has gone away' or terminated socket errors.",
        "In production cloud environments (AWS RDS, GCP Cloud SQL, Azure Database), idle network connections are frequently closed by stateful cloud firewalls, NAT gateways, or database servers without sending a TCP RST/FIN packet. When a web server attempts to reuse a dead connection, it encounters connection reset errors. Enabling `pool_pre_ping=True` causes SQLAlchemy to issue a lightweight query (e.g. `SELECT 1`) on connection checkout. If the ping fails, the dead connection is silently recycled and a fresh connection is opened.",
        "from sqlalchemy.ext.asyncio import create_async_engine\n\nDATABASE_URL = 'postgresql+asyncpg://user:pass@db.internal:5432/app'\n\nengine = create_async_engine(\n    DATABASE_URL,\n    pool_size=15,\n    pool_pre_ping=True,  # Tests connection before handing to route\n    pool_recycle=1800,   # Proactively recycle connections every 30 minutes\n    connect_args={\n        'timeout': 10,                 # Driver connect timeout in seconds\n        'command_timeout': 30,         # Maximum query execution timeout\n    }\n)",
        "Configuring engine resilience with pool_pre_ping, pool_recycle, and asyncpg timeouts.",
        "When `pool_pre_ping=True` is enabled, the engine's `checkout()` routine intercepts the connection before returning it to the caller. It executes a test query within a `try/except` block. If the socket is dead or the server disconnected, the engine catches the exception, closes the socket, and requests a new connection from the pool.",
        "FastAPI apps communicating with managed cloud databases where idle connections are dropped after 5-15 minutes of inactivity.",
        ["What is the performance overhead of `pool_pre_ping=True`?", "How does `pool_recycle` complement `pool_pre_ping`?"],
        ["Disabling `pool_pre_ping` in cloud environments, leading to intermittent 500 errors on the first request after periods of low traffic.", "Confusing database connect timeout with HTTP request timeout."],
        "Explain that `pool_pre_ping` incurs negligible overhead (a microsecond in-memory ping) compared to the resilience against dropped connections.",
        ["[Connection Pooling](database-integration.md)", "[AWS RDS Fundamentals](../11-devops/aws.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/pooling.html#disconnect-handling-pessimistic"]
    ),

    # FA-INT-132
    (
        "FA-INT-132",
        "Managing Multi-Tenant Database Connections per Request",
        "Multi-tenancy in FastAPI can be achieved by extracting tenant identifiers from request headers or JWT tokens and dynamically routing queries to tenant-specific databases or schemas.",
        "In multi-tenant SaaS platforms, tenant data isolation is enforced using: 1) Shared Database, Separate Schemas (PostgreSQL `search_path`): Each tenant gets a dedicated schema within the same database; 2) Separate Databases per Tenant: Each tenant has an independent database instance; 3) Shared Schema with Tenant ID column: Rows include a `tenant_id` foreign key. FastAPI's dependency injection allows extracting the tenant ID from headers or authentication tokens and configuring the `AsyncSession` accordingly.",
        "from fastapi import FastAPI, Depends, Header, HTTPException\nfrom sqlalchemy import text\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('postgresql+asyncpg://user:pass@localhost:5432/saas_db')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_tenant_db(x_tenant_id: str = Header(...)) -> AsyncSession:\n    # Validate tenant ID format to prevent SQL injection in schema names\n    if not x_tenant_id.isalnum():\n        raise HTTPException(status_code=400, detail='Invalid tenant identifier')\n        \n    async with SessionLocal() as session:\n        # Set PostgreSQL search_path dynamically for this session\n        await session.execute(text(f'SET search_path TO tenant_{x_tenant_id}, public'))\n        yield session\n\napp = FastAPI()\n\n@app.get('/tenant-data')\nasync def read_tenant_data(db: AsyncSession = Depends(get_tenant_db)):\n    result = await db.execute(text('SELECT current_schema()'))\n    return {'current_schema': result.scalar()}",
        "Dynamic multi-tenant schema switching per request using PostgreSQL search_path and FastAPI header dependency.",
        "PostgreSQL's `SET search_path` modifies the table resolution namespace for the current database connection session. When the route executes queries against table `users`, PostgreSQL resolves it against `tenant_{x_tenant_id}.users` automatically, guaranteeing complete tenant isolation.",
        "B2B SaaS architectures where enterprise customers require dedicated schema or database separation for GDPR and compliance.",
        ["What are the security risks of dynamically setting schema names from request headers?", "How does separate database multi-tenancy compare with separate schema multi-tenancy?"],
        ["Interpolating unvalidated tenant IDs directly into raw `SET search_path` SQL, creating SQL injection vulnerabilities.", "Forgetting to reset connection state when returning pooled connections, risking cross-tenant data leakage."],
        "Emphasize: Always sanitize or validate tenant identifiers strictly before using them in dynamic SQL statements.",
        ["[Header Dependencies](routing-and-dependencies.md)", "[Database Normalization](../05-databases/database-design.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.connection"]
    ),

    # FA-INT-133
    (
        "FA-INT-133",
        "Read-Replica Routing with Multiple Engines in FastAPI Dependencies",
        "Read-replica routing directs read-only queries (SELECTs) to database replicas and write queries (INSERT/UPDATE/DELETE) to the primary database using specialized FastAPI dependencies.",
        "High-scale web applications offload read traffic to one or more read replicas while directing write transactions to the primary database master. In FastAPI, this is implemented cleanly through separate dependency functions: `get_read_db` (bound to a read-replica pool) and `get_write_db` (bound to the primary writer pool). Route handlers declare whichever session they require, ensuring optimal load distribution.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Article(Base):\n    __tablename__ = 'articles'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n\n# Writer Engine (Primary)\nwriter_engine = create_async_engine('postgresql+asyncpg://user:pass@primary-db:5432/app')\nWriterSession = async_sessionmaker(writer_engine, expire_on_commit=False)\n\n# Reader Engine (Replica)\nreader_engine = create_async_engine('postgresql+asyncpg://user:pass@replica-db:5432/app')\nReaderSession = async_sessionmaker(reader_engine, expire_on_commit=False)\n\nasync def get_read_db():\n    async with ReaderSession() as session:\n        yield session\n\nasync def get_write_db():\n    async with WriterSession() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/articles')\nasync def list_articles(db: AsyncSession = Depends(get_read_db)):\n    return (await db.scalars(select(Article))).all()\n\n@app.post('/articles')\nasync def create_article(title: str, db: AsyncSession = Depends(get_write_db)):\n    article = Article(title=title)\n    db.add(article)\n    await db.commit()\n    return {'id': article.id, 'title': article.title}",
        "Separating read and write traffic across independent database pools using dedicated FastAPI dependencies.",
        "By binding `ReaderSession` to the replica endpoint and `WriterSession` to the primary writer endpoint, traffic is bifurcated at the application layer. The primary node handles WAL generation while read replicas serve read-only queries without competing for write locks.",
        "High-traffic content platforms, news sites, and e-commerce stores with 90:10 read-to-write traffic ratios.",
        ["What is replication lag and how does it affect read-your-own-writes consistency?", "How can you enforce read-only safety on the replica session?"],
        ["Attempting to execute `INSERT` or `UPDATE` on a read-replica session, resulting in a database read-only transaction error.", "Failing to account for replication lag when a user creates a resource and is immediately redirected to a read endpoint."],
        "Mention 'read-your-own-writes' consistency: After a write, either read from the primary for that user session or pass a replication token.",
        ["[Dependencies Injection](routing-and-dependencies.md)", "[PostgreSQL Replication](../05-databases/postgresql.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html#custom-vertical-partitioning"]
    ),

    # FA-INT-134
    (
        "FA-INT-134",
        "Soft Delete Pattern with SQLAlchemy and FastAPI",
        "Soft deletion marks records as deleted by setting an `is_deleted` boolean flag or `deleted_at` timestamp rather than physically removing the row from disk.",
        "Hard deletes permanently remove rows from disk, which can break foreign key integrity, destroy historical audit trails, and complicate accidental deletion recovery. The soft delete pattern retains rows by introducing `deleted_at: Mapped[datetime | None] = mapped_column(default=None)`. Queries filter out deleted records with `.where(Model.deleted_at.is_(None))`. Deletion endpoints update `deleted_at = datetime.utcnow()` instead of issuing SQL `DELETE` statements.",
        "from datetime import datetime, timezone\nfrom fastapi import FastAPI, Depends, HTTPException, status, Response\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Document(Base):\n    __tablename__ = 'documents'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n    deleted_at: Mapped[datetime | None] = mapped_column(default=None)\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.delete('/documents/{doc_id}', status_code=status.HTTP_204_NO_CONTENT)\nasync def soft_delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):\n    result = await db.scalars(select(Document).where(Document.id == doc_id, Document.deleted_at.is_(None)))\n    doc = result.one_or_none()\n    if not doc:\n        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document not found')\n        \n    doc.deleted_at = datetime.now(timezone.utc)\n    await db.commit()\n    return Response(status_code=status.HTTP_204_NO_CONTENT)",
        "Implementing soft delete by populating deleted_at timestamp and filtering active records.",
        "Instead of generating `DELETE FROM documents WHERE id = ?`, SQLAlchemy issues `UPDATE documents SET deleted_at = ? WHERE id = ?`. The row remains intact on disk, allowing restoration or compliance auditing while being hidden from standard application queries.",
        "SaaS applications, customer records, invoices, and compliance-regulated medical/financial records.",
        ["How do unique constraints interact with soft-deleted rows?", "How can SQLAlchemy event listeners or custom queries automatically apply `deleted_at IS NULL`?"],
        ["Using standard unique constraints (e.g., `UNIQUE(email)`) with soft deletes, preventing re-registration with a deleted email (fix with partial unique indexes).", "Forgetting to add `deleted_at IS NULL` to joined queries, accidentally exposing deleted child records."],
        "Advise using PostgreSQL partial indexes: `CREATE UNIQUE INDEX idx_user_email ON users(email) WHERE deleted_at IS NULL`.",
        ["[Database Indexing](../05-databases/indexing-and-optimization.md)", "[CRUD Deletion](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/events.html"]
    ),

    # FA-INT-135
    (
        "FA-INT-135",
        "Complex Queries: Joins, Grouping, and Aggregations (`func.count`, `group_by`)",
        "Complex SQL queries in SQLAlchemy 2.0 combine `select()`, `.join()`, `.group_by()`, and `func` aggregation functions to produce grouped analytical metrics.",
        "Real-world APIs require aggregated metrics, such as calculating total orders per customer or average ratings per product. SQLAlchemy provides SQL functions via `sqlalchemy.func` (e.g., `func.count()`, `func.sum()`, `func.avg()`). Joining tables uses `.join(TargetModel, JoinCondition)`. Aggregated results are retrieved by executing the query and iterating over the resulting tuples or mappings.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import select, func, ForeignKey\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Customer(Base):\n    __tablename__ = 'customers'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nclass Order(Base):\n    __tablename__ = 'orders'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    amount: Mapped[int] = mapped_column()\n    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/analytics/customers')\nasync def customer_summary(db: AsyncSession = Depends(get_db)):\n    stmt = (\n        select(\n            Customer.id,\n            Customer.name,\n            func.count(Order.id).label('order_count'),\n            func.coalesce(func.sum(Order.amount), 0).label('total_spent'),\n        )\n        .outerjoin(Order, Customer.id == Order.customer_id)\n        .group_by(Customer.id, Customer.name)\n        .having(func.count(Order.id) >= 0)\n    )\n    result = await db.execute(stmt)\n    return [dict(row) for row in result.mappings().all()]",
        "Aggregating customer order metrics with outerjoin, group_by, func.sum, and having clauses.",
        "SQLAlchemy compiles the expression into a standard SQL `SELECT customers.id, customers.name, count(orders.id), coalesce(sum(orders.amount), 0) ... LEFT OUTER JOIN ... GROUP BY ...`. `result.mappings()` transforms each row into an accessible dictionary keyed by column labels.",
        "Analytics dashboards, executive summary reports, and accounting reconciliation endpoints.",
        ["Why is `outerjoin` preferred over `join` when reporting customer summaries?", "What does `func.coalesce()` do when a customer has zero orders?"],
        ["Omitting non-aggregated columns from the `GROUP BY` clause, causing SQL syntax errors on PostgreSQL.", "Using `.scalars()` on queries returning multiple columns (returns only the first column, discarding the rest)."],
        "Remember: Use `session.execute()` + `.mappings()` for multi-column aggregations, NOT `session.scalars()`.",
        ["[Raw SQL Execution](database-integration.md)", "[SQL Fundamentals](../05-databases/sql-fundamentals.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#aggregate-functions-with-group-by-having"]
    ),

    # FA-INT-136
    (
        "FA-INT-136",
        "Bulk Insert and Update Operations with `insert()` and `session.execute()`",
        "Bulk database operations in SQLAlchemy 2.0 bypass ORM instance creation by compiling multi-row `insert()` statements directly into high-speed batch SQL queries.",
        "Inserting 10,000 records one by one via `session.add()` generates 10,000 individual ORM instances, populating identity maps and creating severe CPU and memory bottlenecks. SQLAlchemy 2.0 provides direct bulk operations via `insert(Model).values(list_of_dicts)`. This compiles to a single multi-row SQL `INSERT INTO table (col1, col2) VALUES (?, ?), (?, ?)...`, executing in milliseconds without ORM overhead.",
        "from fastapi import FastAPI, Depends, status\nfrom sqlalchemy import insert\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass LogEntry(Base):\n    __tablename__ = 'log_entries'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    level: Mapped[str] = mapped_column()\n    message: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/logs/batch', status_code=status.HTTP_201_CREATED)\nasync def bulk_insert_logs(logs: list[dict], db: AsyncSession = Depends(get_db)):\n    # logs is a list of dicts: [{'level': 'INFO', 'message': '...'}, ...]\n    if not logs:\n        return {'inserted': 0}\n        \n    stmt = insert(LogEntry)\n    await db.execute(stmt, logs)  # High-speed bulk batch execution\n    await db.commit()\n    return {'inserted': len(logs)}",
        "Executing high-speed bulk inserts by passing a list of parameter dictionaries to db.execute().",
        "SQLAlchemy's dialect driver compiles the list of dictionaries into an optimized database batch protocol (such as PostgreSQL's `copy` or multi-values batch insert), bypassing the ORM state machine entirely.",
        "CSV data ingestion endpoints, audit log ingestion, and telemetry data collection.",
        ["What are the trade-offs of using Core bulk insert vs ORM `session.add_all()`?", "How does PostgreSQL `ON CONFLICT DO UPDATE` (upsert) work with bulk inserts?"],
        ["Loading thousands of records into individual ORM model instances and calling `session.add()` in a loop.", "Exceeding database bind parameter limits (e.g., SQLite's 999 or 32766 parameter limit) by inserting too many records in a single batch."],
        "Chunk massive datasets (e.g. into batches of 1,000 records) to stay well within database driver parameter limits.",
        ["[CRUD Operations](database-integration.md)", "[Performance Optimization](../01-python/internals-and-performance.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#bulk-insert-upsert"]
    ),

    # FA-INT-137
    (
        "FA-INT-137",
        "Implementing Repository and Unit-of-Work Patterns with FastAPI Dependencies",
        "The Repository pattern decouples database access logic from FastAPI route handlers, while the Unit-of-Work coordinates transactional state across multiple repositories.",
        "Directly embedding SQL queries inside route handlers creates tight coupling, complicates unit testing, and violates the Single Responsibility Principle. The Repository pattern encapsulates data access behind an interface (e.g., `UserRepository.get_by_email()`). The Unit-of-Work pattern wraps the database session, exposing repositories and committing transactions atomically. FastAPI's dependency injection instantiates the Unit-of-Work per request.",
        "from fastapi import FastAPI, Depends, HTTPException\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass User(Base):\n    __tablename__ = 'users'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    email: Mapped[str] = mapped_column(unique=True)\n\nclass UserRepository:\n    def __init__(self, session: AsyncSession):\n        self.session = session\n\n    async def get_by_id(self, user_id: int) -> User | None:\n        return (await self.session.scalars(select(User).where(User.id == user_id))).one_or_none()\n\n    async def create(self, email: str) -> User:\n        user = User(email=email)\n        self.session.add(user)\n        return user\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_user_repo() -> UserRepository:\n    async with SessionLocal() as session:\n        async with session.begin():\n            yield UserRepository(session)\n\napp = FastAPI()\n\n@app.get('/users/{user_id}')\nasync def read_user(user_id: int, repo: UserRepository = Depends(get_user_repo)):\n    user = await repo.get_by_id(user_id)\n    if not user:\n        raise HTTPException(status_code=404, detail='User not found')\n    return {'id': user.id, 'email': user.email}",
        "Decoupling route handlers from SQLAlchemy via the Repository pattern injected via FastAPI Depends.",
        "The router communicates exclusively with the `UserRepository` contract. Database technologies can be refactored, mocked in unit tests, or swapped without changing route handler business logic.",
        "Enterprise-grade applications adhering to Clean Architecture or Domain-Driven Design (DDD).",
        ["What is the difference between the Repository pattern and the DAO (Data Access Object) pattern?", "How does Unit-of-Work ensure multiple repositories participate in the same transaction?"],
        ["Over-engineering simple CRUD microservices with unnecessary layers of abstraction.", "Having repositories manage their own independent sessions, breaking transaction atomicity across multiple operations."],
        "Emphasize: Repositories handle data access; Unit-of-Work manages the transaction lifecycle across repositories.",
        ["[Dependencies Basics](routing-and-dependencies.md)", "[Software Architecture](../10-system-design/fundamentals.md)"],
        ["https://martinfowler.com/eaaCatalog/repository.html"]
    ),

    # FA-INT-138
    (
        "FA-INT-138",
        "Optimistic Locking with Version Columns in SQLAlchemy and FastAPI",
        "Optimistic locking prevents concurrent update conflicts by verifying a version number column before committing updates, failing if another transaction modified the row concurrently.",
        "When two concurrent users attempt to update the same record (the 'lost update' anomaly), without concurrency control, the second write silently overwrites the first. Optimistic locking avoids database lock contention by allowing concurrent reads. A `version_id` column is added to the model. When updating, SQLAlchemy executes `UPDATE table SET ..., version_id = version_id + 1 WHERE id = :id AND version_id = :current_version`. If another process modified the row, the row count is 0, raising `StaleDataError`, which can be converted to an HTTP 409 Conflict.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom sqlalchemy import select\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy.orm.exc import StaleDataError\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Product(Base):\n    __tablename__ = 'products'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n    price: Mapped[int] = mapped_column()\n    version_id: Mapped[int] = mapped_column(default=1)\n\n    __mapper_args__ = {'version_id_col': version_id}\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.put('/products/{prod_id}')\nasync def update_product(prod_id: int, new_price: int, db: AsyncSession = Depends(get_db)):\n    product = (await db.scalars(select(Product).where(Product.id == prod_id))).one_or_none()\n    if not product:\n        raise HTTPException(status_code=404, detail='Product not found')\n        \n    product.price = new_price\n    try:\n        await db.commit()\n        return {'status': 'updated', 'version': product.version_id}\n    except StaleDataError:\n        await db.rollback()\n        raise HTTPException(\n            status_code=status.HTTP_409_CONFLICT,\n            detail='Resource was modified concurrently by another user; please refresh and retry'\n        )",
        "Configuring SQLAlchemy mapper version_id_col to enforce optimistic locking and handle StaleDataError.",
        "SQLAlchemy embeds the expected `version_id` into the generated `UPDATE` statement's `WHERE` clause and increments the version. If zero rows match the condition, SQLAlchemy detects that a concurrent update intervened and raises `StaleDataError`.",
        "Collaborative document editing, inventory price adjustments, and administrative profile updates.",
        ["When is optimistic locking preferable to pessimistic locking?", "What HTTP status code represents an optimistic locking failure?"],
        ["Using optimistic locking in systems with extremely high write contention (causes excessive retries and 409 errors).", "Forgetting to catch `StaleDataError`, producing unhandled 500 Internal Server Errors."],
        "Remember: Use optimistic locking when conflicts are rare (low contention); use pessimistic locking when conflicts are frequent (high contention).",
        ["[Pessimistic Locking](database-integration.md)", "[Transaction Isolation](../05-databases/transactions-and-isolation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/versioning.html"]
    ),

    # FA-INT-139
    (
        "FA-INT-139",
        "Pessimistic Locking (`with_for_update`) in High-Concurrency Financial Transactions",
        "Pessimistic locking acquires exclusive database row-level locks via `with_for_update()` inside a transaction, preventing other transactions from reading or modifying the locked rows.",
        "In critical financial operations (like debiting accounts or reserving limited concert tickets), optimistic locking fails due to high concurrent collisions. Pessimistic locking locks the targeted row at the database engine level by issuing `SELECT ... FOR UPDATE`. Any concurrent transaction attempting to read that row `FOR UPDATE` will block until the locking transaction issues `COMMIT` or `ROLLBACK`. Flags like `nowait=True` or `skip_locked=True` allow immediate failure or skipping locked rows instead of waiting.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Account(Base):\n    __tablename__ = 'accounts'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    balance: Mapped[int] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/accounts/{acc_id}/debit')\nasync def debit_account(acc_id: int, amount: int, db: AsyncSession = Depends(get_db)):\n    async with db.begin():\n        # SELECT ... FOR UPDATE acquires an exclusive row lock\n        stmt = select(Account).where(Account.id == acc_id).with_for_update()\n        account = (await db.scalars(stmt)).one_or_none()\n        \n        if not account:\n            raise HTTPException(status_code=404, detail='Account not found')\n        if account.balance < amount:\n            raise HTTPException(status_code=400, detail='Insufficient funds')\n            \n        account.balance -= amount\n        \n    return {'account_id': acc_id, 'new_balance': account.balance}",
        "Acquiring row-level exclusive locks with with_for_update() inside an atomic transaction.",
        "`with_for_update()` instructs the database query planner to acquire an exclusive lock (e.g. `X` lock on PostgreSQL) on the selected tuple. Concurrent transactions attempting `SELECT FOR UPDATE` on the same ID enter a lock-wait queue until the lock holder commits.",
        "Banking withdrawals, flash sale ticket reservations, and flight seat assignments.",
        ["What does `with_for_update(skip_locked=True)` do, and why is it used in message queues?", "How do deadlocks happen with pessimistic locking?"],
        ["Using `with_for_update()` outside of a transaction block (the lock is released immediately, rendering it useless).", "Acquiring locks on multiple resources in inconsistent order across endpoints, causing deadlocks."],
        "Golden rule: Always acquire pessimistic locks in a consistent primary key order across all transactions to avoid deadlocks.",
        ["[Transactions](database-integration.md)", "[Database Concurrency](../05-databases/transactions-and-isolation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#locking-with-for-update"]
    ),

    # FA-INT-140
    (
        "FA-INT-140",
        "Using PostgreSQL UUIDs and JSONB Columns with Pydantic Serialization",
        "PostgreSQL native types like `UUID` and `JSONB` are mapped in SQLAlchemy 2.0 via `sqlalchemy.dialects.postgresql` and serialized seamlessly into Pydantic models.",
        "Modern API systems avoid sequential auto-incrementing integer IDs to prevent enumeration attacks and enable client-side ID generation. PostgreSQL provides a native 128-bit `UUID` type. Furthermore, semi-structured data is stored efficiently using PostgreSQL's binary JSON format (`JSONB`), supporting GIN indexing and key-level queries. SQLAlchemy 2.0 provides `postgresql.UUID` and `postgresql.JSONB` column types, which pair cleanly with Python's `uuid.UUID` and `dict` / Pydantic models.",
        "import uuid\nfrom typing import Any\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel, ConfigDict\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Event(Base):\n    __tablename__ = 'events'\n    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)\n    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)\n\nclass EventResponse(BaseModel):\n    id: uuid.UUID\n    payload: dict[str, Any]\n    model_config = ConfigDict(from_attributes=True)\n\napp = FastAPI()\n\n@app.get('/events/mock', response_model=EventResponse)\nasync def mock_event():\n    return Event(id=uuid.uuid4(), payload={'user_action': 'click', 'device': 'mobile'})",
        "Mapping PostgreSQL native UUID and JSONB columns to typed SQLAlchemy 2.0 models and Pydantic response schemas.",
        "The `asyncpg` driver converts PostgreSQL's internal binary UUID and JSONB wire representations directly into Python `uuid.UUID` objects and native dictionaries, eliminating string serialization overhead.",
        "Audit logging pipelines, event-driven microservices, and user preference storage with dynamic schemas.",
        ["What is the performance advantage of JSONB over plain JSON in PostgreSQL?", "Why is `as_uuid=True` passed to `postgresql.UUID`?"],
        ["Storing UUIDs as standard 36-character VARCHAR strings instead of native UUID columns (wastes 4x storage and degrades index efficiency).", "Attempting to query JSONB columns without GIN indexes in high-volume tables."],
        "Emphasize that `JSONB` decomposes JSON into binary trees for fast indexing and query execution, unlike plain `JSON` text storage.",
        ["[PostgreSQL Features](../05-databases/postgresql.md)", "[Pydantic Serialization](pydantic-and-validation.md)"],
        ["https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#postgresql-data-types"]
    ),

    # FA-INT-141
    (
        "FA-INT-141",
        "Database Query Performance Profiling with SQL Logging and Event Listeners",
        "SQLAlchemy event listeners (`before_cursor_execute`, `after_cursor_execute`) track query execution durations to detect slow queries and profile database overhead in FastAPI.",
        "Identifying slow queries before they degrade production SLAs is essential. While setting `echo=True` prints SQL statements to stdout, production profiling requires programmatic timing. SQLAlchemy's `event.listen` hooks into the database execution pipeline to measure the elapsed time of every query. Warnings or metrics can be logged to OpenTelemetry or Prometheus whenever a query exceeds a predefined threshold (e.g., > 100ms).",
        "import time\nimport logging\nfrom sqlalchemy import event\nfrom sqlalchemy.ext.asyncio import create_async_engine\n\nlogger = logging.getLogger('db_profiler')\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\n\n# Profile query duration using SQLAlchemy event listeners\n@event.listens_for(engine.sync_engine, 'before_cursor_execute')\ndef before_query(conn, cursor, statement, parameters, context, executemany):\n    conn.info['query_start_time'] = time.perf_counter()\n\n@event.listens_for(engine.sync_engine, 'after_cursor_execute')\ndef after_query(conn, cursor, statement, parameters, context, executemany):\n    total_time = time.perf_counter() - conn.info.get('query_start_time', 0.0)\n    if total_time > 0.1:  # Log slow queries taking > 100ms\n        logger.warning(f'Slow query ({total_time * 1000:.2f}ms): {statement}')",
        "Instrumenting SQLAlchemy query execution hooks to profile execution latency and log slow queries.",
        "The `before_cursor_execute` event fires immediately before the database driver dispatches the SQL command over the network socket. The `after_cursor_execute` event fires when the cursor receives the result packets. Calculating the difference gives the exact query round-trip duration.",
        "Production observability, APM integration (DataDog, NewRelic), and automated performance regression testing.",
        ["Why must event listeners be attached to `engine.sync_engine` in async SQLAlchemy?", "How do you avoid leaking query parameters containing sensitive user credentials in slow query logs?"],
        ["Leaving `echo=True` enabled in production, which floods logs and incurs massive I/O serialization overhead.", "Failing to sanitize SQL statements and parameters before logging, exposing plaintext user passwords in log aggregators."],
        "Always attach SQLAlchemy event hooks to `engine.sync_engine` when working with async engines.",
        ["[Production Logging](production-and-performance.md)", "[Indexing & Optimization](../05-databases/indexing-and-optimization.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute"]
    ),

    # FA-INT-142
    (
        "FA-INT-142",
        "Asynchronous Full-Text Search with PostgreSQL `to_tsvector` in FastAPI",
        "PostgreSQL full-text search is implemented in FastAPI using SQLAlchemy by querying `to_tsvector` and `to_tsquery` expressions matched with the `op('@@')` text search operator.",
        "Standard SQL `LIKE '%query%'` queries require full table sequential scans, rendering them unusable on large text datasets. PostgreSQL full-text search parses text into tokens (lexemes), normalizes them (stemming), and indexes them using Generalized Inverted Indexes (GIN). In FastAPI with SQLAlchemy, full-text queries are expressed using `func.to_tsvector()` and `func.plainto_tsquery()`, combined with the `@@` match operator.",
        "from fastapi import FastAPI, Depends, Query\nfrom sqlalchemy import select, func\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Article(Base):\n    __tablename__ = 'articles'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n    content: Mapped[str] = mapped_column()\n\nengine = create_async_engine('postgresql+asyncpg://user:pass@localhost:5432/app')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/search/articles')\nasync def search_articles(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):\n    # Compiles to: to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', :q)\n    ts_vector = func.to_tsvector('english', Article.title + ' ' + Article.content)\n    ts_query = func.plainto_tsquery('english', q)\n    \n    stmt = select(Article).where(ts_vector.op('@@')(ts_query))\n    return (await db.scalars(stmt)).all()",
        "Executing full-text search using PostgreSQL tsvector and plainto_tsquery via SQLAlchemy expressions.",
        "`to_tsvector` strips stop words and stems words down to root lexemes (e.g. 'jumping' becomes 'jump'). The `@@` operator performs index lookups against a GIN index on the generated vector, returning matching records in logarithmic time.",
        "Knowledge bases, documentation portals, and e-commerce product search engines.",
        ["Why is `plainto_tsquery` safer for user input than raw `to_tsquery`?", "What index type must be created on the database to accelerate full-text searches?"],
        ["Using `to_tsquery` with raw user input, which raises database syntax errors if the user types unescaped characters like `&` or `!`.", "Searching large text columns with `LIKE '%term%'` instead of full-text search GIN indexes."],
        "Emphasize `plainto_tsquery`: It treats input as plain text without requiring users to type boolean search operators.",
        ["[PostgreSQL Indexing](../05-databases/postgresql.md)", "[Search Architecture](../10-system-design/fundamentals.md)"],
        ["https://www.postgresql.org/docs/current/textsearch.html"]
    ),

    # FA-INT-143
    (
        "FA-INT-143",
        "Nested Transactions and Savepoints with `session.begin_nested()`",
        "SQLAlchemy's `session.begin_nested()` establishes database savepoints, allowing granular rollbacks of specific sub-operations without aborting the parent transaction.",
        "In complex transaction workflows, an individual sub-step (such as charging a secondary payment card or inserting optional metadata) might fail. If executed inside a standard transaction, any database error invalidates the entire transaction. Savepoints, created via `async with session.begin_nested():`, issue SQL `SAVEPOINT savepoint_name`. If an exception occurs within the nested block, only the statements executed after that savepoint are rolled back (`ROLLBACK TO SAVEPOINT`), allowing the parent transaction to proceed and commit.",
        "from fastapi import FastAPI, Depends, HTTPException\nfrom sqlalchemy import select\nfrom sqlalchemy.exc import IntegrityError\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass AuditLog(Base):\n    __tablename__ = 'audit_logs'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    action: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/perform-operation')\nasync def perform_operation(db: AsyncSession = Depends(get_db)):\n    async with db.begin():  # Outer main transaction\n        # Primary business mutation...\n        \n        # Optional sub-step inside a Savepoint\n        try:\n            async with db.begin_nested():  # SAVEPOINT created here\n                db.add(AuditLog(action='user_action'))\n                # If this fails, only the savepoint is rolled back\n        except IntegrityError:\n            # Savepoint automatically rolled back to; outer transaction remains intact\n            pass\n            \n    return {'status': 'success'}",
        "Isolating non-critical sub-operations using savepoints with db.begin_nested().",
        "`begin_nested()` emits `SAVEPOINT sa_savepoint_1`. If an exception occurs, SQLAlchemy issues `ROLLBACK TO SAVEPOINT sa_savepoint_1`. The connection returns to the outer transaction state without marking the entire transaction as aborted.",
        "Batch imports where invalid rows should be skipped without discarding valid rows, and optional audit logging.",
        ["What is the difference between `session.begin()` and `session.begin_nested()`?", "Can you nest multiple savepoints within one another?"],
        ["Assuming standard SQL databases support true independent nested transactions (databases use savepoints within a single physical transaction).", "Catching exceptions inside an outer transaction without using `begin_nested()`, resulting in 'current transaction is aborted' errors on PostgreSQL."],
        "Key takeaway: In PostgreSQL, once an error occurs in a transaction, NO further queries can execute unless that error occurred inside a `SAVEPOINT`.",
        ["[Transaction Isolation](../05-databases/transactions-and-isolation.md)", "[CRUD Operations](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#using-savepoint"]
    ),

    # FA-INT-144
    (
        "FA-INT-144",
        "Handling Transient Database Connection Drops with Retry Mechanisms",
        "Transient network blips, failovers, and deadlocks are handled using exponential backoff retry decorators (e.g. `tenacity`) around database service calls.",
        "In cloud environments, brief network partitions, database primary failovers (AWS RDS Multi-AZ failovers), or serialization failures (deadlocks) can abort operations transiently. Rather than immediately returning HTTP 500 errors to clients, services wrap transactional operations in retry decorators. Using libraries like `tenacity`, endpoints automatically retry transient exceptions (`asyncpg.PostgresConnectionError`, `OperationalError`, `DBAPIError`) with randomized exponential backoff and jitter.",
        "from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type\nfrom sqlalchemy.exc import OperationalError, DBAPIError\nfrom fastapi import FastAPI, Depends\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\n# Retry decorator for transient database connection errors\nretry_db_call = retry(\n    stop=stop_after_attempt(3),\n    wait=wait_exponential(multiplier=0.1, min=0.1, max=1.0),\n    retry=retry_if_exception_type((OperationalError, DBAPIError)),\n    reraise=True,\n)\n\n@retry_db_call\nasync def execute_resilient_query(session: AsyncSession):\n    # Queries executed here will retry up to 3 times on transient connection drops\n    pass",
        "Implementing automated retry with exponential backoff on transient database exceptions using tenacity.",
        "When an `OperationalError` is raised, `tenacity` intercepts the exception, computes a randomized backoff delay (e.g. 100ms, 200ms, 400ms), sleeps asynchronously without blocking the event loop, and re-invokes the callable.",
        "Mission-critical payment processors, booking engines, and background worker queues processing events.",
        ["Why must retries ONLY be applied to idempotent operations or uncommitted transactions?", "What is retry jitter and why is it essential?"],
        ["Retrying operations that already partially committed, causing duplicate charges or double records.", "Retrying non-transient errors like `IntegrityError` or `ProgrammingError` (syntax errors will never succeed on retry)."],
        "Never retry `IntegrityError`; only retry transient infrastructure errors like `OperationalError` or connection dropouts.",
        ["[Resilience Architecture](../10-system-design/fundamentals.md)", "[Async Engine](database-integration.md)"],
        ["https://tenacity.readthedocs.io/en/latest/"]
    ),

    # FA-INT-145
    (
        "FA-INT-145",
        "Integrating a Redis Caching Layer Over SQLAlchemy Query Results",
        "A Redis cache-aside layer stores serialized query results in memory with a Time-To-Live (TTL), reducing database query load by serving hot reads from cache.",
        "High-read endpoints (such as product details, user profiles, or configuration flags) can overwhelm database connection pools. In the Cache-Aside pattern, the FastAPI route first inspects Redis using an asynchronous client (`redis.asyncio`). If a cache hit occurs, the cached JSON string is deserialized and returned immediately. On a cache miss, the route queries PostgreSQL via SQLAlchemy, writes the result to Redis with a TTL, and returns the response.",
        "import json\nfrom fastapi import FastAPI, Depends\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Item(Base):\n    __tablename__ = 'items'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n# Simulated async Redis client\nclass MockRedis:\n    def __init__(self):\n        self.store = {}\n    async def get(self, key: str): return self.store.get(key)\n    async def setex(self, key: str, ttl: int, val: str): self.store[key] = val\n\nredis_client = MockRedis()\n\n@app.get('/items/{item_id}')\nasync def get_item(item_id: int, db: AsyncSession = Depends(get_db)):\n    cache_key = f'item:{item_id}'\n    cached = await redis_client.get(cache_key)\n    if cached:\n        return json.loads(cached)\n        \n    item = (await db.scalars(select(Item).where(Item.id == item_id))).one_or_none()\n    if not item:\n        return {'error': 'not found'}\n        \n    data = {'id': item.id, 'name': item.name}\n    await redis_client.setex(cache_key, 300, json.dumps(data))  # 5-minute TTL\n    return data",
        "Implementing the Cache-Aside pattern with Redis and SQLAlchemy in a FastAPI route.",
        "Reading from Redis occurs in memory (< 1ms latency) over an async socket connection, bypassing SQL parsing, query planning, table locks, and disk I/O on the primary relational database.",
        "E-commerce product detail pages, social media profiles, and catalog listings experiencing 95%+ read workloads.",
        ["What is cache stampede (dog-piling) and how do you prevent it?", "How do you invalidate or update the Redis cache when an item is modified?"],
        ["Caching without a TTL, resulting in stale data remaining in Redis indefinitely.", "Failing to invalidate the cache upon update or delete operations."],
        "Discuss Cache Invalidation: Update/delete endpoints must delete or update the corresponding Redis cache key.",
        ["[Redis Caching](../06-redis-and-messaging/redis.md)", "[Pydantic Serialization](pydantic-and-validation.md)"],
        ["https://redis.io/docs/manual/patterns/distributed-caching/"]
    ),

    # FA-INT-146
    (
        "FA-INT-146",
        "Using MongoDB with Motor and Beanie ODM in FastAPI",
        "MongoDB is integrated asynchronously into FastAPI using the Motor driver or Beanie ODM, which maps MongoDB documents directly to Pydantic models.",
        "For unstructured, hierarchical, or document-centric data models, MongoDB provides a NoSQL alternative to relational databases. Rather than using the synchronous `pymongo` driver, FastAPI applications use `motor` (an asyncio wrapper around PyMongo) or `Beanie` (an asynchronous Object Document Mapper built directly on top of Pydantic v2). In Beanie, models inherit from `Document` and support native async querying with `await Document.find(...).to_list()`.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\n# Conceptual Beanie Document definition:\n# from beanie import Document, init_beanie\n# import motor.motor_asyncio\n#\n# class UserLog(Document):\n#     user_id: int\n#     action: str\n#     metadata: dict = {}\n#\n#     class Settings:\n#         name = 'user_logs'\n#\n# @app.post('/logs')\n# async def create_log(log: UserLog):\n#     await log.insert()\n#     return log",
        "Declaring an asynchronous MongoDB document model with Beanie ODM based on Pydantic.",
        "Beanie leverages Pydantic's schema inspection to validate documents on read and write, translating model methods into Motor async command dispatches to the MongoDB wire protocol.",
        "Content management systems, user activity tracking, logging pipelines, and catalog storage with dynamic attributes.",
        ["What is the difference between Motor and standard PyMongo?", "When should you choose MongoDB over PostgreSQL with JSONB?"],
        ["Using standard synchronous `pymongo` in `async def` routes, causing event loop starvation.", "Choosing MongoDB when strict multi-table relational foreign keys and ACID transactions across disparate domains are required."],
        "Mention that PostgreSQL `JSONB` satisfies 90% of document-store needs while preserving relational integrity; choose MongoDB when horizontal sharding is paramount.",
        ["[PostgreSQL JSONB](database-integration.md)", "[NoSQL Fundamentals](../05-databases/database-design.md)"],
        ["https://beanie-odm.net/"]
    ),

    # FA-INT-147
    (
        "FA-INT-147",
        "FastAPI with DynamoDB (`aioboto3`) vs Relational Databases",
        "AWS DynamoDB provides managed serverless NoSQL persistence, accessed asynchronously in FastAPI via `aioboto3` for predictable single-digit millisecond latency at scale.",
        "Amazon DynamoDB is a managed key-value and document database that scales horizontally without connection pool limits or server management. Unlike relational databases that degrade under thousands of concurrent connections, DynamoDB operates over stateless HTTPS API calls. To integrate DynamoDB into async FastAPI without blocking the event loop, developers use `aioboto3` (an asyncio wrapper for boto3) to execute `put_item`, `get_item`, and `query` operations.",
        "# Conceptual aioboto3 DynamoDB integration:\n# import aioboto3\n# session = aioboto3.Session()\n#\n# async def get_dynamo_table():\n#     async with session.resource('dynamodb', region_name='us-east-1') as dynamo:\n#         yield await dynamo.Table('user_sessions')\n#\n# @app.get('/session/{token}')\n# async def read_session(token: str, table = Depends(get_dynamo_table)):\n#     response = await table.get_item(Key={'session_token': token})\n#     return response.get('Item')",
        "Accessing Amazon DynamoDB asynchronously using aioboto3 session resources.",
        "Standard `boto3` uses Python's synchronous `urllib3` under the hood. `aioboto3` replaces standard HTTP transports with `aiohttp`, allowing AWS API requests to be awaited asynchronously on the main event loop.",
        "Serverless microservices on AWS Lambda/ECS, global user session stores, and real-time gaming leaderboards.",
        ["Why doesn't DynamoDB suffer from connection pool exhaustion like PostgreSQL?", "What is a Partition Key and Sort Key in DynamoDB?"],
        ["Using standard `boto3` inside `async def` FastAPI routes, which blocks the event loop on every AWS API request.", "Designing DynamoDB tables like relational tables with cross-table join expectations."],
        "Highlight that DynamoDB queries must be designed around access patterns using partition keys; it is not suited for ad-hoc analytical queries.",
        ["[AWS Fundamentals](../11-devops/aws.md)", "[Async Concurrency](async-and-concurrency.md)"],
        ["https://aioboto3.readthedocs.io/"]
    ),

    # FA-INT-148
    (
        "FA-INT-148",
        "Streaming Large Query Result Sets with `session.stream_scalars()`",
        "Massive database query results are streamed to clients using `session.stream_scalars()` paired with FastAPI's `StreamingResponse`, preventing Out-Of-Memory crashes.",
        "When an endpoint exports millions of records (e.g. CSV or JSON report generation), calling `result.all()` fetches the entire dataset into application memory at once, which can trigger an Out-Of-Memory (OOM) kill on the container. SQLAlchemy 2.0 provides `session.stream_scalars(stmt)`, which yields records incrementally from a database server-side cursor. Streaming these chunks into a `StreamingResponse` sends data over HTTP as it arrives.",
        "from collections.abc import AsyncGenerator\nfrom fastapi import FastAPI, Depends\nfrom fastapi.responses import StreamingResponse\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Audit(Base):\n    __tablename__ = 'audits'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    entry: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\nasync def csv_generator(db: AsyncSession) -> AsyncGenerator[str, None]:\n    yield 'id,entry\\n'\n    stmt = select(Audit).order_by(Audit.id)\n    # stream_scalars uses server-side cursor to fetch rows in batches\n    async for record in await db.stream_scalars(stmt):\n        yield f'{record.id},{record.entry}\\n'\n\n@app.get('/export/csv')\nasync def export_csv(db: AsyncSession = Depends(get_db)):\n    return StreamingResponse(csv_generator(db), media_type='text/csv')",
        "Streaming database query rows incrementally as CSV chunks using stream_scalars and StreamingResponse.",
        "`stream_scalars()` creates a server-side cursor on databases like PostgreSQL. Instead of buffering the entire table in Python RAM, the driver fetches rows in configurable buffer sizes (e.g., 100 rows at a time) and yields them directly to the HTTP streaming generator.",
        "Financial data exports, compliance audit log downloads, and large dataset CSV generation.",
        ["Why does `result.all()` cause memory spikes on large tables?", "What happens to the database connection while a client slowly consumes a StreamingResponse?"],
        ["Holding a database connection open indefinitely while streaming to a slow client (can starve the connection pool).", "Forgetting to sort (`order_by`) when streaming records with a server-side cursor."],
        "Caution: Long-running streaming endpoints tie up database connections; consider background job exports (Celery + S3) for massive multi-gigabyte datasets.",
        ["[Streaming Responses](async-and-concurrency.md)", "[Background Tasks](../06-redis-and-messaging/celery.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#streaming-results"]
    ),

    # FA-INT-149
    (
        "FA-INT-149",
        "Implementing Composite Keys and Foreign Key Cascades in SQLAlchemy 2.0",
        "Composite keys combine multiple columns into a primary key, and foreign key cascades (`ondelete='CASCADE'`) ensure database-level relational consistency.",
        "In relational schemas, association tables (many-to-many join tables) and localized sub-entities often use composite primary keys (e.g. `(user_id, role_id)`). Furthermore, configuring `ForeignKey(..., ondelete='CASCADE')` instructs the database engine to automatically remove child rows when the parent row is deleted, eliminating orphaned records without requiring manual application-side cleanup.",
        "from sqlalchemy import ForeignKey, PrimaryKeyConstraint\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Organization(Base):\n    __tablename__ = 'organizations'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n    # cascade='all, delete-orphan' synchronizes SQLAlchemy in-memory state\n    memberships: Mapped[list['Membership']] = relationship(back_populates='org', cascade='all, delete-orphan')\n\nclass User(Base):\n    __tablename__ = 'users'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nclass Membership(Base):\n    __tablename__ = 'memberships'\n    # Composite primary key made of two foreign keys\n    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)\n    org_id: Mapped[int] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True)\n    role: Mapped[str] = mapped_column(default='member')\n\n    org: Mapped['Organization'] = relationship(back_populates='memberships')",
        "Defining composite primary keys and database-level foreign key cascades in SQLAlchemy 2.0.",
        "`ForeignKey(..., ondelete='CASCADE')` writes an `ON DELETE CASCADE` constraint into the SQL DDL. When an organization is deleted, the database engine deletes all matching membership rows in the same transaction. The ORM-side `cascade='all, delete-orphan'` keeps Python in-memory objects synchronized.",
        "Multi-tenant permissions, organization membership systems, and order line-item relationships.",
        ["What is the difference between database `ondelete='CASCADE'` and SQLAlchemy's `cascade='delete'`?", "Why are composite keys useful in association tables?"],
        ["Relying solely on ORM-level cascades without database-level `ON DELETE CASCADE`, which fails if rows are deleted via raw SQL or external migrations.", "Using composite primary keys when an entity requires independent reference by foreign keys elsewhere."],
        "Pair both: Database-level `ondelete='CASCADE'` guarantees consistency at the storage layer; ORM-level `cascade='all, delete-orphan'` maintains in-memory object coherence.",
        ["[Database Normalization](../05-databases/database-design.md)", "[Declarative Models](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/cascades.html"]
    ),

    # FA-INT-150
    (
        "FA-INT-150",
        "Testing FastAPI Database Endpoints with In-Memory SQLite and Dependency Overrides",
        "FastAPI routes with database integration are tested by replacing the production database dependency with a test database using `app.dependency_overrides`.",
        "Unit and integration tests should never run against production or shared developer databases. FastAPI's `app.dependency_overrides` dictionary allows replacing any dependency (including `get_db`) with a test fixture. In test suites, tests create an in-memory SQLite database (`sqlite+aiosqlite:///:memory:` with `StaticPool`), run `create_all`, and execute requests using `httpx.AsyncClient` without modifying application source code.",
        "import pytest\nfrom fastapi import FastAPI, Depends\nfrom httpx import AsyncClient, ASGITransport\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.pool import StaticPool\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Item(Base):\n    __tablename__ = 'test_items'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\napp = FastAPI()\n\n# Placeholder dependency for production\nasync def get_db():\n    raise NotImplementedError\n\n@app.get('/items')\nasync def list_items(db: AsyncSession = Depends(get_db)):\n    return (await db.scalars(select(Item))).all()\n\n# Test setup\ntest_engine = create_async_engine('sqlite+aiosqlite:///:memory:', poolclass=StaticPool)\nTestSession = async_sessionmaker(test_engine, expire_on_commit=False)\n\nasync def override_get_db():\n    async with TestSession() as session:\n        yield session\n\napp.dependency_overrides[get_db] = override_get_db\n\n@pytest.mark.asyncio\nasync def test_read_items():\n    async with test_engine.begin() as conn:\n        await conn.run_sync(Base.metadata.create_all)\n    \n    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:\n        response = await ac.get('/items')\n        assert response.status_code == 200\n        assert response.json() == []",
        "Overriding the database dependency in FastAPI tests using in-memory SQLite and StaticPool.",
        "FastAPI checks `app.dependency_overrides` before resolving any dependency callable. When `get_db` is encountered, it substitutes `override_get_db`, isolating the test execution within the temporary in-memory database.",
        "Automated continuous integration (CI) test suites running in GitHub Actions without external services.",
        ["Why is `StaticPool` mandatory when using in-memory SQLite in test suites?", "How do you clean up `app.dependency_overrides` between test cases?"],
        ["Forgetting to clear `app.dependency_overrides` after tests finish, causing state leakage into other test modules.", "Testing PostgreSQL-specific features (like JSONB or ARRAY) against SQLite, which causes test failures due to dialect differences."],
        "Clear overrides in test teardowns: `app.dependency_overrides.clear()`, or use testcontainers-python when testing dialect-specific queries.",
        ["[Testing FastAPI](testing.md)", "[Dependencies Injection](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/advanced/testing-database/"]
    ),
]
