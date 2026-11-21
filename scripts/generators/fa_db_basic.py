"""
fa_db_basic.py
==============
Basic FastAPI Database Integration Questions: FA-BAS-126 to FA-BAS-150 (25 questions)
"""

basic_data = [
    # FA-BAS-126
    (
        "FA-BAS-126",
        "FastAPI Database Integration Approaches (SQLAlchemy 2.0 vs Raw SQL)",
        "FastAPI does not include a built-in ORM; developers typically integrate SQLAlchemy 2.0 for asynchronous object-relational mapping or use drivers like asyncpg for high-speed raw SQL execution.",
        "Unlike monolithic frameworks such as Django, FastAPI is database-agnostic. It provides no default ORM, letting developers select whatever persistence technology fits their architecture. In modern Python backend development, the standard choices are: 1) SQLAlchemy 2.0 with async support (`sqlalchemy.ext.asyncio`), offering type-safe querying, DeclarativeBase schema mapping, and cross-database portability; 2) Raw asynchronous drivers like `asyncpg` or `databases`, offering maximum raw throughput with direct parameter-bound SQL statements; 3) Async ORMs like Tortoise-ORM or Piccolo. SQLAlchemy 2.0 is the de facto industry standard because of its active maintenance, mature migration tooling (Alembic), and strong alignment with Pydantic v2 schemas.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy import select\n\nDATABASE_URL = 'sqlite+aiosqlite:///:memory:'\nengine = create_async_engine(DATABASE_URL, echo=False)\nasync_session = async_sessionmaker(engine, expire_on_commit=False)\n\nclass Base(DeclarativeBase):\n    pass\n\nclass ItemModel(Base):\n    __tablename__ = 'items'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nasync def get_db():\n    async with async_session() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/items')\nasync def list_items(db: AsyncSession = Depends(get_db)):\n    result = await db.execute(select(ItemModel))\n    return result.scalars().all()",
        "Configuring an asynchronous SQLAlchemy 2.0 engine, declarative model, and dependency session provider in FastAPI.",
        "SQLAlchemy's `create_async_engine` wraps a greenlet-based event loop adapter (`AsyncEngine`). When `await db.execute()` is called, SQLAlchemy runs dialect-level dialect instructions inside a greenlet while yielding control back to the asyncio event loop during I/O network operations.",
        "Production microservices requiring reliable transaction lifecycles, structured schema definitions, and seamless mapping to Pydantic responses.",
        ["Why is SQLAlchemy 2.0 preferred over SQLAlchemy 1.4 legacy syntax?", "Can you mix raw SQL queries with SQLAlchemy models in FastAPI?"],
        ["Attempting to use synchronous drivers like `psycopg2` or `sqlite3` inside `async def` route handlers without threadpool offloading.", "Forgetting `expire_on_commit=False`, leading to `MissingGreenlet` errors when accessing model attributes after committing."],
        "Highlight that FastAPI's dependency injection system makes managing database session lifecycles clean and leak-free.",
        ["[Dependencies Basics](routing-and-dependencies.md)", "[SQLAlchemy Async Engine](database-integration.md)"],
        ["https://fastapi.tiangolo.com/tutorial/sql-databases/", "https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html"]
    ),

    # FA-BAS-127
    (
        "FA-BAS-127",
        "Asynchronous vs Synchronous Database Drivers (asyncpg vs psycopg2)",
        "Asynchronous database drivers (such as asyncpg and aiosqlite) execute network socket I/O using non-blocking asyncio calls, whereas synchronous drivers (such as psycopg2) block the thread during queries.",
        "In a high-concurrency web server, database calls involve waiting for network round-trips and disk I/O on the database server. Synchronous drivers (e.g., `psycopg2`, standard `sqlite3`, `mysqlclient`) use blocking POSIX socket operations. If called directly in an `async def` FastAPI route, they block the entire asyncio event loop, freezing all concurrent requests. Asynchronous drivers (e.g., `asyncpg`, `asyncmy`, `aiosqlite`, `psycopg` v3 with async mode) implement non-blocking socket protocols using asyncio streams. They yield control back to the event loop while waiting for the database server to reply, enabling thousands of concurrent queries on a single operating system thread.",
        "# Async connection string (non-blocking with asyncpg)\nASYNC_PG_URL = 'postgresql+asyncpg://user:pass@localhost:5432/production_db'\n\n# Synchronous connection string (blocking; requires threadpool offloading if used)\nSYNC_PG_URL = 'postgresql+psycopg2://user:pass@localhost:5432/production_db'\n\n# Async SQLite connection string\nASYNC_SQLITE_URL = 'sqlite+aiosqlite:///./test.db'",
        "Contrasting connection URL dialect protocols for async vs sync database drivers.",
        "Async drivers register their file descriptors (socket handles) with the OS event notification subsystem (epoll on Linux, kqueue on macOS, IOCP on Windows). When a query packet is dispatched, the coroutine is suspended. When the database replies, the OS notifies the event loop, which wakes the coroutine.",
        "High-throughput API gateways and web services handling 10,000+ requests per second where thread-per-request blocking would exhaust server RAM.",
        ["What happens if you run `psycopg2` inside an `async def` route?", "Is `asyncpg` faster than `psycopg2` even in single-threaded benchmarks?"],
        ["Assuming that setting `async def` on a FastAPI route automatically makes database queries non-blocking even with sync drivers.", "Failing to prefix database URLs with the async dialect (e.g., using `postgresql://` instead of `postgresql+asyncpg://`)."],
        "State clearly: The `async` keyword in FastAPI only provides concurrency benefits if the underlying database driver is natively asynchronous.",
        ["[Event Loop Fundamentals](async-and-concurrency.md)", "[Database Connection Pools](database-integration.md)"],
        ["https://magicstack.github.io/asyncpg/current/", "https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg"]
    ),

    # FA-BAS-128
    (
        "FA-BAS-128",
        "Database Engine vs Session in SQLAlchemy",
        "The Engine manages the connection pool and database dialect communications, while the Session represents an active conversational workspace and unit of work for database operations.",
        "In SQLAlchemy architecture, the Engine (`AsyncEngine`) and Session (`AsyncSession`) serve distinct purposes: 1) Engine: A long-lived, application-wide object created once at startup. It holds the connection pool, handles dialect compilation (translating Python SQL expressions into PostgreSQL/MySQL dialect), and communicates with the underlying driver. 2) Session: A short-lived, transient object created per operation (or per HTTP request). It acts as a Unit of Work, keeping track of pending changes (objects added, modified, deleted) in an Identity Map and flushing them within an explicit transaction.",
        "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\n\n# Engine: Created ONCE at application startup\nengine = create_async_engine('sqlite+aiosqlite:///:memory:', pool_size=10)\n\n# Sessionmaker: Factory for creating short-lived sessions\nSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)\n\nasync def query_example():\n    # Session: Leased for a single operation/request, then closed\n    async with SessionLocal() as session:\n        # Transactions and queries happen here\n        pass",
        "Instantiating a singleton AsyncEngine and using a factory sessionmaker for transient requests.",
        "The engine maintains a connection pool (e.g., `QueuePool`). When an `AsyncSession` needs to execute a query, it leases an active connection from the pool. Upon session closure (`session.close()`), the connection is returned back to the engine's pool rather than terminated.",
        "Enterprise applications requiring bounded connection pools to prevent exhausting database max connections under heavy traffic spikes.",
        ["Why should an engine never be created inside a route handler?", "What is an Identity Map in an ORM session?"],
        ["Recreating `create_async_engine` inside every route handler, which leaks connection pools and rapidly crashes the database.", "Sharing a single `AsyncSession` instance across concurrent requests, causing race conditions and transaction collision."],
        "Emphasize: Engine = Singleton application-level resource; Session = Request-scoped unit of work.",
        ["[Dependencies with Yield](routing-and-dependencies.md)", "[Transactions](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_basics.html"]
    ),

    # FA-BAS-129
    (
        "FA-BAS-129",
        "Creating an Async Engine with `create_async_engine`",
        "`create_async_engine` is the SQLAlchemy 2.0 entrypoint for building an asynchronous engine configured with database credentials, connection pool parameters, and logging flags.",
        "To establish asynchronous database communication, SQLAlchemy requires `create_async_engine()` instead of the traditional synchronous `create_engine()`. The connection string must specify an async driver prefix (e.g., `postgresql+asyncpg://`, `mysql+aiomysql://`, or `sqlite+aiosqlite://`). Key configuration arguments include `echo=True` (for logging generated SQL statements during debugging), `pool_size` (number of persistent pooled connections), `max_overflow` (extra connections allowed during bursts), and `pool_pre_ping=True` (health checks before reusing connections).",
        "import os\nfrom sqlalchemy.ext.asyncio import create_async_engine\n\nDATABASE_URL = os.getenv(\n    'DATABASE_URL',\n    'postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db'\n)\n\nengine = create_async_engine(\n    DATABASE_URL,\n    echo=False,\n    pool_size=20,\n    max_overflow=10,\n    pool_pre_ping=True,\n    pool_recycle=3600,\n)",
        "Configuring create_async_engine with connection pooling, recycling, and health checks.",
        "`create_async_engine` initializes an `AsyncEngine` proxy that wraps an underlying synchronous engine using greenlets. Whenever an async method like `.connect()` or `.execute()` is awaited, SQLAlchemy translates the call through `greenlet_spawn` to execute non-blocking coroutine I/O via the async driver.",
        "Production backend microservices deployed on Kubernetes, requiring automatic reconnection when idle connections are terminated by firewalls.",
        ["What does `pool_pre_ping=True` do?", "Why should `echo=True` be disabled in production environments?"],
        ["Passing a synchronous driver connection string (e.g., `postgresql://`) to `create_async_engine`, causing a runtime dialect error.", "Forgetting `pool_recycle`, causing errors when cloud firewalls (e.g., AWS RDS 15-minute idle drops) sever stale sockets."],
        "Mention that `pool_pre_ping=True` issues a lightweight `SELECT 1` ping to ensure a connection is healthy before handing it to a request.",
        ["[Connection Pooling](database-integration.md)", "[Environment Variables](fundamentals.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.create_async_engine"]
    ),

    # FA-BAS-130
    (
        "FA-BAS-130",
        "Configuring `async_sessionmaker` and `expire_on_commit=False`",
        "`async_sessionmaker` is a factory for creating `AsyncSession` instances, and setting `expire_on_commit=False` is critical in async FastAPI applications to prevent `MissingGreenlet` errors.",
        "In SQLAlchemy 2.0, `async_sessionmaker` replaces the older `sessionmaker(class_=AsyncSession)` construct. A crucial configuration parameter is `expire_on_commit=False`. By default in synchronous SQLAlchemy, committing a session expires all mapped object attributes so that subsequent reads re-fetch fresh values from the database. In an async context, however, accessing an expired attribute outside an active awaitable statement triggers lazy loading, which fails with `MissingGreenlet: greenlet_spawn has not been called` because lazy loading cannot perform implicit I/O. Disabling expiration allows returned models to be serialized into Pydantic schemas without errors.",
        "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\n\n# Standard async session factory configuration\nAsyncSessionLocal = async_sessionmaker(\n    bind=engine,\n    class_=AsyncSession,\n    autoflush=False,\n    autocommit=False,\n    expire_on_commit=False,  # CRITICAL for async FastAPI\n)",
        "Configuring async_sessionmaker with expire_on_commit=False for seamless Pydantic serialization.",
        "When `expire_on_commit=False` is set, after `await session.commit()` finishes, the object's populated in-memory dictionary (`__dict__`) is preserved. FastAPI's serialization layer can read attributes like `item.id` and `item.name` directly in memory without triggering additional database round-trips.",
        "Any FastAPI endpoint that creates or updates an ORM record and immediately returns the model as a Pydantic response schema.",
        ["What specific exception is raised if `expire_on_commit` is left True in async code?", "What is the purpose of `autoflush=False`?"],
        ["Leaving `expire_on_commit=True`, causing mysterious `MissingGreenlet` exceptions during response serialization.", "Attempting to instantiate `AsyncSession` directly with `AsyncSession(engine)` instead of using a reusable sessionmaker factory."],
        "Emphasize `expire_on_commit=False` as the number one requirement when configuring SQLAlchemy with FastAPI.",
        ["[Pydantic Serialization](pydantic-and-validation.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncio"]
    ),

    # FA-BAS-131
    (
        "FA-BAS-131",
        "Injecting Database Sessions via `Depends(get_db)`",
        "FastAPI leverages its dependency injection system (`Depends`) to provide a dedicated, scoped `AsyncSession` to each incoming HTTP request.",
        "Instead of opening global database sessions or managing manual connection locks, FastAPI uses generator dependencies with `yield`. A dependency function, typically named `get_db()`, instantiates a session using the sessionmaker, yields it to the route handler, and automatically closes it when the HTTP request finishes. This guarantees that every request gets its own isolated session and transaction context, preventing connection leaks even if unhandled exceptions occur during execution.",
        "from collections.abc import AsyncGenerator\nfrom fastapi import FastAPI, Depends\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db() -> AsyncGenerator[AsyncSession, None]:\n    async with SessionLocal() as session:\n        try:\n            yield session\n        finally:\n            await session.close()\n\napp = FastAPI()\n\n@app.get('/health-db')\nasync def check_db(session: AsyncSession = Depends(get_db)):\n    return {'status': 'connected', 'is_active': session.is_active}",
        "Injecting an isolated AsyncSession into a route handler using a generator dependency with cleanup.",
        "FastAPI executes the dependency up to the `yield` statement before entering the endpoint handler. Once the endpoint returns its response (or raises an exception), FastAPI resumes the generator at the line following `yield`, executing the `finally` block to close the session.",
        "Standard production pattern for all database-backed endpoints in FastAPI applications.",
        ["Can a route handler accept multiple different database dependencies?", "What happens to the session if an unhandled HTTPException is raised inside the route?"],
        ["Using a standard function without `yield` and forgetting to close the session, causing connection pool exhaustion.", "Passing database sessions across threads or background tasks where the request context has already ended."],
        "Explain that `Depends(get_db)` enforces the Unit of Work pattern at the HTTP request boundary.",
        ["[Dependencies with Yield](routing-and-dependencies.md)", "[Session Lifecycle](database-integration.md)"],
        ["https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency"]
    ),

    # FA-BAS-132
    (
        "FA-BAS-132",
        "Database Session Lifecycle and Cleanup (`yield` and `finally`)",
        "The session lifecycle spans from request entry to response completion, where using `async with` or `try ... finally` guarantees connection return to the pool regardless of errors.",
        "A database session in FastAPI must strictly follow a predictable lifecycle: 1) Acquire: A session is leased when the route dependency resolves; 2) Execute: Queries and mutations are performed within the endpoint; 3) Commit/Rollback: Changes are committed explicitly, or rolled back if errors occur; 4) Release: The session is closed and its underlying socket connection is returned to the pool. If a session is left unclosed (e.g., due to an uncaught crash), the connection remains checked out from the pool, eventually causing the entire application to hang when pool connections are exhausted.",
        "from collections.abc import AsyncGenerator\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db_safe() -> AsyncGenerator[AsyncSession, None]:\n    async with SessionLocal() as session:\n        try:\n            yield session\n            await session.commit()\n        except Exception:\n            await session.rollback()\n            raise\n        finally:\n            await session.close()",
        "Robust session lifecycle management with explicit commit, rollback on error, and guaranteed cleanup.",
        "When `async with SessionLocal()` enters, it creates a transaction context. The `try/except/finally` pattern ensures that any Python exception triggers `await session.rollback()` to prevent partial database writes, followed by `await session.close()` to return the leased connection to `QueuePool`.",
        "E-commerce order placement where an exception mid-flow must roll back inventory deductions and release locks immediately.",
        ["Should `session.commit()` be handled inside `get_db()` or inside the endpoint logic?", "What is the consequence of connection leaks on a Kubernetes pod?"],
        ["Committing automatically in `get_db()` even for read-only GET endpoints (unnecessary overhead).", "Failing to rollback aborted transactions, leaving connections in 'idle in transaction' state on PostgreSQL."],
        "Discuss the trade-off: Automatic commit in `get_db()` reduces boilerplate, but explicit commit in service functions gives finer transactional control.",
        ["[Exception Handling](middleware-and-exception-handling.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_transaction.html"]
    ),

    # FA-BAS-133
    (
        "FA-BAS-133",
        "Defining Models with SQLAlchemy 2.0 `DeclarativeBase` and `Mapped`",
        "SQLAlchemy 2.0 uses `DeclarativeBase`, `Mapped[...]`, and `mapped_column()` to declare ORM models with full static type safety and IDE autocompletion.",
        "Legacy SQLAlchemy (1.x) relied on `declarative_base()` and untyped `Column(Integer, ...)` declarations. SQLAlchemy 2.0 introduces modern typed models: 1) Models inherit from a class derived from `DeclarativeBase`; 2) Fields are annotated with `Mapped[type]`, signaling to mypy, pyright, and IDEs the exact Python type; 3) Attributes use `mapped_column()` to specify database-specific details like primary keys, indexes, default values, and foreign keys. This design completely eliminates discrepancies between runtime ORM behavior and static type checking.",
        "from datetime import datetime\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\nfrom sqlalchemy import String, func\n\nclass Base(DeclarativeBase):\n    pass\n\nclass User(Base):\n    __tablename__ = 'users'\n\n    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)\n    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)\n    is_active: Mapped[bool] = mapped_column(default=True)\n    created_at: Mapped[datetime] = mapped_column(server_default=func.now())",
        "Declaring a type-annotated SQLAlchemy 2.0 model using DeclarativeBase, Mapped, and mapped_column.",
        "`DeclarativeBase` uses Python metaclass machinery to inspect the class annotations. When `Mapped[str]` is defined, SQLAlchemy automatically infers the SQL `VARCHAR` or `TEXT` type if not explicitly overridden in `mapped_column()`.",
        "Production backend codebases leveraging strict mypy/pyright type checking in CI/CD pipelines.",
        ["How does `default=True` differ from `server_default=func.now()`?", "Can `Mapped[Optional[str]]` be used to indicate nullable columns?"],
        ["Using deprecated 1.x `Column(Integer, primary_key=True)` syntax in new SQLAlchemy 2.0 projects.", "Confusing Python-side defaults (`default=...`) with database-side defaults (`server_default=...`)."],
        "Highlight that `server_default` creates a `DEFAULT` clause in the SQL DDL, whereas `default` evaluates in Python code.",
        ["[Type Hinting](../01-python/fundamentals.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html"]
    ),

    # FA-BAS-134
    (
        "FA-BAS-134",
        "CRUD Operations: Inserting Records (`session.add` and `session.commit`)",
        "To insert new records in FastAPI with SQLAlchemy 2.0, instantiate the model, add it to the session with `session.add()`, and persist it asynchronously with `await session.commit()`.",
        "Inserting records involves creating an instance of the Declarative model populated with validated data from a Pydantic input schema. Once instantiated, `session.add(instance)` registers the new entity in the session's 'pending' set. The database write occurs when `await session.commit()` is executed, sending an `INSERT INTO` SQL statement inside a database transaction. To read generated primary keys or server defaults, `await session.refresh(instance)` is called to re-populate the object from the database.",
        "from fastapi import FastAPI, Depends, status\nfrom pydantic import BaseModel, EmailStr\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass User(Base):\n    __tablename__ = 'users'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    email: Mapped[str] = mapped_column(unique=True)\n\nclass UserCreate(BaseModel):\n    email: EmailStr\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/users', status_code=status.HTTP_201_CREATED)\nasync def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):\n    new_user = User(email=payload.email)\n    db.add(new_user)\n    await db.commit()\n    await db.refresh(new_user)\n    return {'id': new_user.id, 'email': new_user.email}",
        "Inserting a new record, committing the transaction, refreshing the model, and returning the created entity.",
        "`session.add()` does not immediately execute SQL. It tracks the object in memory. When `await session.commit()` is awaited, SQLAlchemy flushes all pending changes, commits the SQL transaction, and releases row locks. `session.refresh()` issues a `SELECT` query to retrieve auto-generated columns like `id`.",
        "User registration endpoints, order creations, and audit event logging.",
        ["Why is `await db.refresh(instance)` necessary after `commit()`?", "What happens if a database unique constraint fails during `commit()`?"],
        ["Forgetting `await db.commit()`, which causes the data to be discarded when the session closes.", "Calling `db.refresh()` without `await`, resulting in an unawaited coroutine warning and unpopulated attributes."],
        "Emphasize that `session.add()` is synchronous and does not use `await`, but `session.commit()` and `session.refresh()` perform I/O and require `await`.",
        ["[Dependencies](routing-and-dependencies.md)", "[Pydantic Models](pydantic-and-validation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-objects"]
    ),

    # FA-BAS-135
    (
        "FA-BAS-135",
        "Querying Records with `select()` and `session.scalars()`",
        "SQLAlchemy 2.0 uses the 2.0-style `select(Model)` construct executed via `await session.scalars(statement)` to fetch ORM model entities asynchronously.",
        "In SQLAlchemy 2.0, the legacy 1.x `session.query(Model)` API is replaced by the unified `select(Model)` statement. When executing a query, `session.execute(select(Model))` returns a `ChunkedIteratorResult` yielding Row tuples (e.g., `(User, )`). To directly obtain a sequence of un-tupled ORM entity instances, SQLAlchemy provides `session.scalars(statement)`, which automatically unwraps the first column of every row. Common terminal methods include `.all()` (fetches all records as a list), `.first()` (first record or None), and `.one_or_none()` (guarantees at most one result).",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Product(Base):\n    __tablename__ = 'products'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/products')\nasync def list_products(db: AsyncSession = Depends(get_db)):\n    stmt = select(Product).order_by(Product.id.desc())\n    result = await db.scalars(stmt)\n    return result.all()",
        "Executing a select statement and unwrapping ORM entities using session.scalars().",
        "`session.scalars(stmt)` executes the SQL statement over the async driver and wraps the resulting rows in a `ScalarResult` proxy that extracts `row[0]` from each tuple, converting raw database rows into mapped Python model instances.",
        "Listing catalog items, fetching active subscriptions, and displaying user profiles.",
        ["What is the difference between `session.execute(stmt)` and `session.scalars(stmt)`?", "When would you use `.one_or_none()` instead of `.first()`?"],
        ["Using the deprecated `session.query(Product).all()` syntax in SQLAlchemy 2.0 async sessions (raises an error).", "Calling `result.scalars().all()` on a result that was already produced by `session.scalars()`, causing an AttributeError."],
        "Remember: `session.execute()` returns rows (tuples); `session.scalars()` returns unwrapped scalar entities.",
        ["[Filtering Queries](database-integration.md)", "[Pydantic Serialization](pydantic-and-validation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html"]
    ),

    # FA-BAS-136
    (
        "FA-BAS-136",
        "Filtering Queries with `.where()` in SQLAlchemy 2.0",
        "Filtering in SQLAlchemy 2.0 is performed by chaining `.where()` clauses to a `select()` statement using model column expressions and boolean operators.",
        "In SQLAlchemy 2.0, `.where()` replaces the legacy `.filter()` method (though `.filter()` remains as an alias). You can pass multiple criteria separated by commas (which acts as an implicit SQL `AND`), or use Python binary operators like `&` (AND), `|` (OR), and `~` (NOT), or the explicit `or_()`, `and_()` helper functions. Column comparisons support SQL operators like `.like()`, `.ilike()`, `.in_()`, `.is_(None)`, and `.between()`.",
        "from typing import Optional\nfrom fastapi import FastAPI, Depends, Query\nfrom sqlalchemy import select, and_, or_\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Article(Base):\n    __tablename__ = 'articles'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n    category: Mapped[str] = mapped_column()\n    is_published: Mapped[bool] = mapped_column(default=False)\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/articles')\nasync def search_articles(\n    category: Optional[str] = None,\n    published_only: bool = True,\n    db: AsyncSession = Depends(get_db)\n):\n    query = select(Article)\n    if category:\n        query = query.where(Article.category == category)\n    if published_only:\n        query = query.where(Article.is_published.is_(True))\n    \n    result = await db.scalars(query)\n    return result.all()",
        "Dynamically constructing a filtered query using conditional .where() clauses in FastAPI.",
        "SQLAlchemy constructs an Abstract Syntax Tree (AST) representing the SQL query. Calling `query.where()` returns a new immutable `Select` object with the additional boolean condition appended to its `WHERE` expression tree.",
        "Search endpoints, catalog filters, faceted navigation, and tenant data isolation.",
        ["Why must you use `is_(True)` or `== True` instead of `is True` when filtering with SQLAlchemy?", "How do you implement an `IN (...)` SQL query with SQLAlchemy?"],
        ["Using standard Python `is None` instead of `Column.is_(None)`, which bypasses operator overloading and breaks the SQL query.", "Mutating query objects in-place instead of reassigning `query = query.where(...)`."],
        "Emphasize that SQLAlchemy overrides Python comparison operators (`==`, `!=`, `<`, `>`) on column definitions to return BinaryExpression nodes.",
        ["[Querying Records](database-integration.md)", "[Pydantic Filters](pydantic-and-validation.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#the-where-clause"]
    ),

    # FA-BAS-137
    (
        "FA-BAS-137",
        "Updating Records in FastAPI with SQLAlchemy 2.0",
        "Records can be updated either by fetching the ORM model, mutating its attributes, and committing, or by executing an asynchronous direct `update()` statement.",
        "There are two primary paradigms for updating data in SQLAlchemy 2.0: 1) ORM Attribute Mutation: Fetch the existing record with `select().where(...)`, update attributes using data from a Pydantic schema (e.g. using `payload.model_dump(exclude_unset=True)`), and execute `await session.commit()`. This triggers ORM validation, change tracking, and events. 2) Bulk / Direct UPDATE: Execute `update(Model).where(...).values(...)` directly. This bypasses in-memory model loading, executing a single high-performance SQL `UPDATE` statement.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom pydantic import BaseModel\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass User(Base):\n    __tablename__ = 'users'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n    status: Mapped[str] = mapped_column(default='active')\n\nclass UserUpdate(BaseModel):\n    name: str | None = None\n    status: str | None = None\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.patch('/users/{user_id}')\nasync def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):\n    result = await db.scalars(select(User).where(User.id == user_id))\n    user = result.first()\n    if not user:\n        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')\n    \n    update_data = payload.model_dump(exclude_unset=True)\n    for field, val in update_data.items():\n        setattr(user, field, val)\n        \n    await db.commit()\n    await db.refresh(user)\n    return {'id': user.id, 'name': user.name, 'status': user.status}",
        "Updating a record selectively using model_dump(exclude_unset=True) and attribute mutation.",
        "SQLAlchemy's Session tracks modified attributes via an internal `AttributeHistory` mechanism. During `await db.commit()`, the session flushes only the columns that actually changed, generating an efficient `UPDATE users SET name = ? WHERE id = ?` query.",
        "REST PATCH endpoints where clients update only specific fields (e.g., updating only a user profile bio).",
        ["What is the advantage of `exclude_unset=True` over `exclude_none=True`?", "When would you prefer a direct `update()` statement over ORM attribute mutation?"],
        ["Overwriting unchanged fields with `None` because `exclude_unset=True` was omitted.", "Forgetting `await db.commit()`, causing the modifications to be lost when the session is closed."],
        "Mention that `exclude_unset=True` distinguishes between a field omitted by the client vs a field explicitly set to `null`.",
        ["[Pydantic Partial Updates](pydantic-and-validation.md)", "[Transactions](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_basics.html#updating-objects"]
    ),

    # FA-BAS-138
    (
        "FA-BAS-138",
        "Deleting Records in FastAPI with SQLAlchemy 2.0",
        "Deleting records is performed by either passing a loaded model instance to `await session.delete(instance)` or issuing a direct `delete(Model).where(...)` statement.",
        "In FastAPI applications, deletion is commonly handled via: 1) Fetch and delete: Fetch the instance to verify existence (returning 404 if missing), then call `await session.delete(instance)` followed by `await session.commit()`. This approach triggers ORM cascading deletes and lifecycle events. 2) Direct delete statement: Execute `await session.execute(delete(Model).where(Model.id == target_id))`, which issues a direct SQL `DELETE FROM table WHERE ...` query without loading the row into memory first. Successful DELETE endpoints typically return HTTP 204 No Content.",
        "from fastapi import FastAPI, Depends, HTTPException, status, Response\nfrom sqlalchemy import select, delete\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Note(Base):\n    __tablename__ = 'notes'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    text: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.delete('/notes/{note_id}', status_code=status.HTTP_204_NO_CONTENT)\nasync def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):\n    result = await db.scalars(select(Note).where(Note.id == note_id))\n    note = result.first()\n    if not note:\n        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')\n    \n    await db.delete(note)\n    await db.commit()\n    return Response(status_code=status.HTTP_204_NO_CONTENT)",
        "Deleting an ORM instance and returning HTTP 204 No Content.",
        "Calling `await session.delete(instance)` marks the object as deleted in the session's identity map. When `await session.commit()` is awaited, SQLAlchemy sends the `DELETE` query, commits the transaction, and expels the instance from the identity map.",
        "Resource removal endpoints (e.g., deleting a comment, dismissing a notification, removing a payment card).",
        ["What HTTP status code is recommended for successful deletion endpoints?", "What is soft delete and how does it compare to hard delete?"],
        ["Returning a JSON body with HTTP 204 No Content (HTTP 204 forbids a response message body according to RFC specs).", "Assuming `session.delete()` immediately executes the SQL query without needing `await session.commit()`."],
        "Emphasize that HTTP 204 responses must not contain a message body; use `Response(status_code=204)` directly.",
        ["[HTTP Status Codes](../07-api-engineering/http-and-https.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://docs.sqlalchemy.org/en/20/orm/session_basics.html#deleting"]
    ),

    # FA-BAS-139
    (
        "FA-BAS-139",
        "Mapping SQLAlchemy Models to Pydantic Schemas (`from_attributes=True`)",
        "Pydantic schemas serialize SQLAlchemy ORM models into JSON responses by configuring `model_config = ConfigDict(from_attributes=True)`.",
        "By default, Pydantic parses values from dictionaries using key lookup (`obj['title']`). SQLAlchemy ORM instances, however, expose column attributes via Python object attributes (`obj.title`). In Pydantic v2, setting `from_attributes = True` inside `ConfigDict` (known as `orm_mode = True` in Pydantic v1) enables Pydantic to read data directly from ORM object attributes. When an endpoint specifies `response_model=UserSchema`, FastAPI automatically converts the returned ORM instance into validated JSON.",
        "from pydantic import BaseModel, ConfigDict\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass DBBook(Base):\n    __tablename__ = 'books'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str] = mapped_column()\n    isbn: Mapped[str] = mapped_column()\n\n# Pydantic Response Schema\nclass BookResponse(BaseModel):\n    id: int\n    title: str\n    isbn: str\n\n    # Pydantic v2 configuration to read from ORM models\n    model_config = ConfigDict(from_attributes=True)\n\n# Example usage\norm_book = DBBook(id=1, title='FastAPI Architecture', isbn='978-0123456789')\npydantic_book = BookResponse.model_validate(orm_book)\nprint(pydantic_book.model_dump())",
        "Configuring a Pydantic v2 response model with from_attributes=True to serialize ORM instances.",
        "When `model_validate()` runs with `from_attributes=True`, Pydantic uses `getattr(obj, field_name)` instead of dictionary subscription. This bridges the gap between database entities and API response contracts without manual mapping code.",
        "Standard data serialization in all FastAPI REST endpoints returning database query results.",
        ["What was `from_attributes=True` called in Pydantic v1?", "Can Pydantic models with `from_attributes=True` serialize nested ORM relationships?"],
        ["Using the deprecated Pydantic v1 syntax `class Config: orm_mode = True` in Pydantic v2 codebases.", "Trying to serialize uncommitted or expired ORM objects with lazy-loaded relationships, triggering `MissingGreenlet`."],
        "State clearly: In Pydantic v2, use `ConfigDict(from_attributes=True)` and `Model.model_validate(orm_instance)`.",
        ["[Pydantic Schemas](pydantic-and-validation.md)", "[Querying Records](database-integration.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances"]
    ),

    # FA-BAS-140
    (
        "FA-BAS-140",
        "Handling Database 404s When a Record Is Not Found",
        "When a database query returns `None`, route handlers must raise an `HTTPException(status_code=404)` with a descriptive detail message.",
        "In REST API design, requesting a specific resource by ID that does not exist in the database must result in an HTTP 404 Not Found error. In FastAPI with SQLAlchemy, developers execute `select().where(...)` and inspect the result with `.first()` or `.one_or_none()`. If the result evaluates to `None`, an `HTTPException` is raised immediately. This halts route execution and instructs FastAPI to serialize an RFC 7807 or standard error JSON payload back to the client.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Order(Base):\n    __tablename__ = 'orders'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    status: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/orders/{order_id}')\nasync def get_order(order_id: int, db: AsyncSession = Depends(get_db)):\n    result = await db.scalars(select(Order).where(Order.id == order_id))\n    order = result.one_or_none()\n    if order is None:\n        raise HTTPException(\n            status_code=status.HTTP_404_NOT_FOUND,\n            detail=f'Order with id {order_id} not found'\n        )\n    return {'id': order.id, 'status': order.status}",
        "Querying an order by ID and raising an HTTP 404 exception if the record is missing.",
        "When `raise HTTPException(...)` is executed, Python control flow unwinds up to FastAPI's exception handling middleware. The dependency cleanup code in `get_db()` runs via `finally`, closing the database session safely before the HTTP response is serialized.",
        "Any resource retrieval, update, or deletion endpoint parameterized by a unique identifier.",
        ["Why use `result.one_or_none()` instead of `result.first()` when querying by primary key?", "Does raising `HTTPException` prevent the database session from closing?"],
        ["Returning `None` or an empty JSON object `{}` with HTTP 200 OK when a resource is missing.", "Catching `Exception` broadly in a `try/except` block and unintentionally swallowing `HTTPException`."],
        "Emphasize that `HTTPException` is a standard Python exception caught by Starlette middleware to generate error responses.",
        ["[Exception Handling](middleware-and-exception-handling.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]
    ),

    # FA-BAS-141
    (
        "FA-BAS-141",
        "SQLite Async Configuration with `sqlite+aiosqlite`",
        "SQLite can be used asynchronously in FastAPI by specifying the `sqlite+aiosqlite://` driver URL with `create_async_engine`.",
        "SQLite is an embedded, file-based database ideal for local development, prototyping, and automated testing. Because standard Python `sqlite3` performs blocking file I/O, FastAPI applications use the `aiosqlite` driver via SQLAlchemy. For in-memory testing, a special pool configuration (`StaticPool`) is necessary because an in-memory SQLite database (`:memory:`) is discarded the moment its connection closes. Using `StaticPool` ensures that all operations share the same persistent in-memory database instance.",
        "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\nfrom sqlalchemy.pool import StaticPool\n\n# Async file-based SQLite database\nFILE_DB_URL = 'sqlite+aiosqlite:///./app.db'\nfile_engine = create_async_engine(FILE_DB_URL, echo=False)\n\n# Async in-memory SQLite database for unit tests\nTEST_DB_URL = 'sqlite+aiosqlite:///:memory:'\ntest_engine = create_async_engine(\n    TEST_DB_URL,\n    connect_args={'check_same_thread': False},\n    poolclass=StaticPool,\n    echo=False,\n)\n\nTestSession = async_sessionmaker(test_engine, expire_on_commit=False)",
        "Configuring file-based and in-memory async SQLite engines with StaticPool and thread flags.",
        "`aiosqlite` manages a worker thread per connection to execute synchronous SQLite C-API operations while exposing standard asyncio awaitable primitives to Python.",
        "Unit testing FastAPI endpoints in GitHub Actions CI/CD pipelines without provisioning external database servers.",
        ["Why is `check_same_thread: False` needed for SQLite in multithreaded environments?", "What happens to an in-memory SQLite database when `StaticPool` is not used?"],
        ["Attempting to run concurrent writes against SQLite in high-concurrency production (causes database locked errors).", "Using `sqlite:///` instead of `sqlite+aiosqlite:///` with `create_async_engine`."],
        "Clarify: SQLite with `aiosqlite` is superb for local development and unit tests, but production web services should use PostgreSQL or MySQL.",
        ["[Unit Testing](testing.md)", "[Database Engines](database-integration.md)"],
        ["https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.aiosqlite"]
    ),

    # FA-BAS-142
    (
        "FA-BAS-142",
        "Database Connection Strings and Environment Variable Loading",
        "Database URLs must never be hardcoded; they should be loaded securely from environment variables using `pydantic-settings`.",
        "Hardcoding database connection strings exposes credentials (passwords, hostnames, ports) and violates Twelve-Factor App principles. The recommended practice in FastAPI is using `pydantic-settings` to define a `Settings` class that reads variables from system environment variables or `.env` files. This allows seamless transitions between local development (`sqlite` or local Docker PostgreSQL), staging, and production Kubernetes clusters.",
        "from pydantic_settings import BaseSettings, SettingsConfigDict\nfrom sqlalchemy.ext.asyncio import create_async_engine\n\nclass Settings(BaseSettings):\n    DATABASE_URL: str = 'postgresql+asyncpg://postgres:secret@localhost:5432/app_db'\n    DB_POOL_SIZE: int = 10\n    DB_MAX_OVERFLOW: int = 5\n\n    model_config = SettingsConfigDict(env_file='.env', extra='ignore')\n\nsettings = Settings()\n\nengine = create_async_engine(\n    settings.DATABASE_URL,\n    pool_size=settings.DB_POOL_SIZE,\n    max_overflow=settings.DB_MAX_OVERFLOW,\n)",
        "Configuring production database settings with Pydantic BaseSettings and environment loading.",
        "At startup, `BaseSettings` inspects `os.environ` and reads specified `.env` files. Type validation ensures that if an integer is expected for `DB_POOL_SIZE`, a string like `'twenty'` in the environment will immediately raise a validation error during application boot.",
        "Cloud deployments on AWS ECS, GCP Cloud Run, or Kubernetes where database URLs and secrets are injected via environment secrets.",
        ["How do you validate that the DATABASE_URL starts with an async driver prefix?", "What is the Twelve-Factor App recommendation for configuration?"],
        ["Committing `.env` files containing production passwords to GitHub repositories.", "Using raw `os.environ.get()` without fallback or type casting, resulting in string types for port or pool numbers."],
        "Emphasize Twelve-Factor App Config: Store config in the environment, validate it at startup with `pydantic-settings`.",
        ["[Pydantic Settings](pydantic-and-validation.md)", "[Docker Configuration](../11-devops/docker.md)"],
        ["https://docs.pydantic.dev/latest/concepts/pydantic_settings/"]
    ),

    # FA-BAS-143
    (
        "FA-BAS-143",
        "Initializing Database Tables with Lifespan Context Manager",
        "Database tables can be initialized at startup inside FastAPI's async `lifespan` handler by calling `metadata.create_all` via `conn.run_sync()`.",
        "While production applications use migration tools like Alembic, small projects, prototypes, and automated integration tests often initialize database schemas upon startup. In modern FastAPI, the deprecated `@app.on_event('startup')` has been replaced by the async `lifespan` context manager. Because DDL generation via `Base.metadata.create_all()` is synchronous, it must be executed within `await conn.run_sync()` on an open connection.",
        "from contextlib import asynccontextmanager\nfrom fastapi import FastAPI\nfrom sqlalchemy.ext.asyncio import create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Item(Base):\n    __tablename__ = 'items'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    # Startup: Create tables\n    async with engine.begin() as conn:\n        await conn.run_sync(Base.metadata.create_all)\n    yield\n    # Shutdown: Clean up engine pool\n    await engine.dispose()\n\napp = FastAPI(lifespan=lifespan)",
        "Using the lifespan context manager to initialize database tables and dispose the engine on shutdown.",
        "`engine.begin()` starts a transaction on a dedicated connection. `conn.run_sync()` runs the synchronous SQLAlchemy `metadata.create_all()` method inside a greenlet, executing SQL DDL statements (`CREATE TABLE IF NOT EXISTS`) without blocking the event loop.",
        "Automated integration test suites, self-contained microservice prototypes, and embedded SQLite apps.",
        ["Why is `metadata.create_all` NOT recommended for production databases?", "What is the purpose of `await engine.dispose()` on shutdown?"],
        ["Using deprecated `@app.on_event('startup')` instead of the modern `lifespan` context manager.", "Using `metadata.create_all` in production where altering existing column types is required (it only creates missing tables, never updates existing schemas)."],
        "Mention that `metadata.create_all` cannot alter tables; always use Alembic for production schema evolution.",
        ["[Lifespan Events](async-and-concurrency.md)", "[Alembic Migrations](database-integration.md)"],
        ["https://fastapi.tiangolo.com/advanced/events/#lifespan"]
    ),

    # FA-BAS-144
    (
        "FA-BAS-144",
        "The `databases` Package (`encode/databases`) vs SQLAlchemy 2.0",
        "`encode/databases` is an async query runner for raw SQL, whereas SQLAlchemy 2.0 is a full-featured ORM providing unit-of-work patterns, schema mapping, and type safety.",
        "Before SQLAlchemy 1.4/2.0 introduced native async support, the `databases` library (by Encode, creators of Starlette) was the primary tool for executing async queries with FastAPI. It provides a simple async wrapper around drivers like `asyncpg`, `aiomysql`, and `aiosqlite`. While lightweight and fast for raw SQL, it lacks full ORM features like identity mapping, change tracking, and relationship loaders. Today, SQLAlchemy 2.0 natively provides both async Core (for high-speed SQL) and async ORM, making external wrappers largely redundant for new projects.",
        "# Conceptual comparison:\n# 1) encode/databases style (raw SQL / Core focused):\n# database = Database('postgresql+asyncpg://...')\n# await database.connect()\n# rows = await database.fetch_all(query='SELECT id, name FROM users')\n\n# 2) Modern SQLAlchemy 2.0 async style (Core and ORM unified):\n# async with AsyncSessionLocal() as session:\n#     result = await session.scalars(select(User))\n#     users = result.all()",
        "Illustrating the difference between raw query runner syntax and unified SQLAlchemy 2.0 ORM.",
        "The `databases` package manages its own connection pool and converts database records into mapping-like `Record` objects. SQLAlchemy 2.0 achieves identical async performance using its own engine architecture while also providing full static typing and schema compilation.",
        "Legacy FastAPI applications built between 2018-2021 migrating gradually toward SQLAlchemy 2.0.",
        ["Why was `encode/databases` popular before SQLAlchemy 1.4?", "Can you use SQLAlchemy Core without the ORM layer?"],
        ["Assuming modern FastAPI tutorials using `encode/databases` represent current best practice (SQLAlchemy 2.0 is now standard).", "Thinking SQLAlchemy 2.0 has significant performance overhead compared to raw query runners for standard CRUD workloads."],
        "Advise interviewers that SQLAlchemy 2.0 is the modern industry choice, but understanding `databases` helps when maintaining legacy microservices.",
        ["[SQLAlchemy Engine](database-integration.md)", "[Raw SQL Queries](database-integration.md)"],
        ["https://github.com/encode/databases"]
    ),

    # FA-BAS-145
    (
        "FA-BAS-145",
        "Tortoise-ORM Basics in FastAPI",
        "Tortoise-ORM is an asynchronous ORM inspired by the Django ORM syntax, designed specifically for asyncio and FastAPI applications.",
        "Tortoise-ORM provides an alternative to SQLAlchemy for developers who prefer Django's active record pattern (`await User.filter(...).all()`) over SQLAlchemy's data mapper pattern (`session.execute(select(...))`). It includes native async support, an integrated schema generator (`register_tortoise`), and its own migration tool (Aerich). Models define fields using `fields.IntField()`, `fields.CharField()`, and methods are awaited directly on the model class.",
        "from fastapi import FastAPI\nfrom tortoise.models import Model\nfrom tortoise import fields\nfrom tortoise.contrib.fastapi import register_tortoise\n\nclass UserProfile(Model):\n    id = fields.IntField(pk=True)\n    username = fields.CharField(max_length=50, unique=True)\n    created_at = fields.DatetimeField(auto_now_add=True)\n\n    class Meta:\n        table = 'user_profiles'\n\napp = FastAPI()\n\n@app.get('/profiles')\nasync def get_profiles():\n    return await UserProfile.all()\n\n# Uncomment to register Tortoise with FastAPI lifespan\n# register_tortoise(\n#     app,\n#     db_url='sqlite://:memory:',\n#     modules={'models': ['__main__']},\n#     generate_schemas=True,\n#     add_exception_handlers=True,\n# )",
        "Defining an async Active Record model using Tortoise-ORM and registering with FastAPI.",
        "Tortoise-ORM registers startup and shutdown hooks on FastAPI that initialize connection pools using drivers like asyncpg or aiomysql. Queries construct SQL expressions asynchronously using a Python builder pattern.",
        "Rapid prototyping and internal tools built by teams with strong Django ORM backgrounds.",
        ["What is the architectural difference between Django/Tortoise Active Record and SQLAlchemy Data Mapper?", "How does Tortoise-ORM handle migrations?"],
        ["Mixing Tortoise-ORM calls with synchronous database calls.", "Choosing Tortoise-ORM for complex enterprise domains that require the strict separation of concerns provided by the Data Mapper pattern."],
        "Contrast Active Record (models encapsulate data and database operations) with Data Mapper (models are pure data; Session handles persistence).",
        ["[Django ORM Basics](../03-django/models-and-orm.md)", "[SQLAlchemy Data Mapper](database-integration.md)"],
        ["https://tortoise.github.io/"]
    ),

    # FA-BAS-146
    (
        "FA-BAS-146",
        "Comparing Python ORMs for FastAPI: SQLAlchemy, Tortoise-ORM, Piccolo, and Peewee",
        "SQLAlchemy 2.0 is the enterprise standard, Tortoise provides a Django-like active record, Piccolo offers a modern async batteries-included experience, and Peewee is primarily synchronous.",
        "Choosing an ORM for FastAPI involves trade-offs in typing, design patterns, and ecosystem maturity: 1) SQLAlchemy 2.0: Data Mapper pattern, enterprise standard, mature migrations (Alembic), first-class typing; 2) Tortoise-ORM: Active Record pattern, familiar to Django developers, intuitive API; 3) Piccolo: Modern async ORM with built-in ASGI admin interface, migrations, and schema validation; 4) Peewee: Lightweight synchronous ORM; requires threadpool offloading in FastAPI (`run_in_threadpool`) and lacks native asyncio.",
        "# Summary comparison:\n# - SQLAlchemy 2.0: Async native, Data Mapper, Alembic, high ecosystem maturity.\n# - Tortoise-ORM: Async native, Active Record, Aerich, medium ecosystem maturity.\n# - Piccolo: Async native, Active Record, built-in admin & migrations, growing ecosystem.\n# - Peewee: Sync native, requires threadpool, not recommended for high async concurrency.",
        "Summary matrix of Python ORM capabilities and concurrency models.",
        "SQLAlchemy decouples persistence concerns from in-memory objects via the Identity Map and Unit of Work, allowing fine-grained control over SQL generation and transaction isolation levels.",
        "Architecture reviews when selecting technical stack dependencies for new greenfield microservices.",
        ["Why is Peewee generally not recommended for high-concurrency FastAPI applications?", "Which ORMs support native Pydantic schema generation?"],
        ["Attempting to run Peewee or standard Django ORM directly inside `async def` routes, causing event loop blocking.", "Assuming all ORMs offer equivalent migration tooling."],
        "Recommend SQLAlchemy 2.0 as the default choice for production systems due to its wide industry adoption, Alembic support, and community longevity.",
        ["[Database Approaches](database-integration.md)", "[Django Comparison](../03-django/fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/sql-databases/"]
    ),

    # FA-BAS-147
    (
        "FA-BAS-147",
        "Handling Unique Constraint Violations in FastAPI Routes",
        "Database unique constraint violations raise `IntegrityError`, which must be caught to return an HTTP 409 Conflict status code instead of a 500 server crash.",
        "When attempting to insert or update a record with a value that violates a unique constraint (such as duplicate emails or usernames), the database driver rejects the query with an integrity error. In SQLAlchemy, this surfaces as `sqlalchemy.exc.IntegrityError`. If uncaught, FastAPI treats it as an internal server error, returning HTTP 500 to the client. Robust endpoints catch `IntegrityError`, roll back the transaction, and raise `HTTPException(status_code=409, detail=...)`.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom pydantic import BaseModel, EmailStr\nfrom sqlalchemy.exc import IntegrityError\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Account(Base):\n    __tablename__ = 'accounts'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    email: Mapped[str] = mapped_column(unique=True)\n\nclass AccountCreate(BaseModel):\n    email: EmailStr\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.post('/accounts', status_code=status.HTTP_201_CREATED)\nasync def register_account(payload: AccountCreate, db: AsyncSession = Depends(get_db)):\n    account = Account(email=payload.email)\n    db.add(account)\n    try:\n        await db.commit()\n        await db.refresh(account)\n        return {'id': account.id, 'email': account.email}\n    except IntegrityError:\n        await db.rollback()\n        raise HTTPException(\n            status_code=status.HTTP_409_CONFLICT,\n            detail='An account with this email already exists'\n        )",
        "Catching SQLAlchemy IntegrityError, rolling back the transaction, and returning HTTP 409 Conflict.",
        "The database engine aborts the transaction immediately upon constraint violation. Calling `await db.rollback()` resets the SQLAlchemy session to a clean state, clearing the rejected insert from the session's internal transaction log.",
        "User registration, unique coupon redemption, and resource creation where duplicates are prohibited.",
        ["Why must you call `await db.rollback()` before raising the HTTP exception?", "Can you inspect the `IntegrityError` to determine which specific constraint failed?"],
        ["Checking for duplicates with a preceding `SELECT` query without handling `IntegrityError` (vulnerable to race conditions).", "Leaving the session in an error state without rolling back, causing subsequent queries on the same session to fail."],
        "Emphasize: A pre-check `SELECT` does NOT prevent race conditions under concurrent requests; you MUST catch `IntegrityError` at the database level.",
        ["[Transactions](database-integration.md)", "[Exception Handlers](middleware-and-exception-handling.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.IntegrityError"]
    ),

    # FA-BAS-148
    (
        "FA-BAS-148",
        "Executing Raw SQL Queries Asynchronously with `text()`",
        "SQLAlchemy's `text()` construct allows executing raw, parameterized SQL queries safely and asynchronously via `await session.execute(text(...))`.",
        "While ORM models handle standard CRUD operations cleanly, complex reporting, analytics, window functions, and database-specific optimizations often require raw SQL. SQLAlchemy 2.0 provides `sqlalchemy.text()` to wrap raw SQL strings. Parameters are passed as dictionaries to prevent SQL injection vulnerabilities. Results can be inspected as mapping dictionaries via `.mappings().all()` or `.mappings().first()`.",
        "from fastapi import FastAPI, Depends\nfrom sqlalchemy import text\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/metrics/user-counts')\nasync def get_user_metrics(status_filter: str = 'active', db: AsyncSession = Depends(get_db)):\n    query = text('''\n        SELECT status, count(*) AS total\n        FROM (\n            SELECT 'active' AS status UNION ALL\n            SELECT 'pending' AS status\n        )\n        WHERE status = :status\n        GROUP BY status\n    ''')\n    result = await db.execute(query, {'status': status_filter})\n    rows = result.mappings().all()\n    return [dict(row) for row in rows]",
        "Executing a parameterized raw SQL query safely using text() and retrieving results as mappings.",
        "`text()` marks the SQL string for safe compilation. The bind parameters (e.g., `:status`) are converted into database-native placeholders (`$1` in PostgreSQL, `?` in SQLite) by the dialect, preventing SQL injection by keeping data separate from executable SQL code.",
        "Analytics dashboards, complex subqueries with window functions, and legacy database integrations.",
        ["Why must you NEVER format raw SQL with Python f-strings or string concatenation?", "What does `.mappings()` return on a SQLAlchemy Result object?"],
        ["Concatenating user input directly into SQL strings, exposing the entire database to SQL injection attacks.", "Assuming `text()` automatically sanitizes interpolated f-strings (it only binds parameters passed in the parameter dict)."],
        "Golden rule: Always use bind parameters (`:param_name`) with `text()`; never use f-strings to build SQL.",
        ["[API Security](../07-api-engineering/api-security.md)", "[SQL Fundamentals](../05-databases/sql-fundamentals.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text"]
    ),

    # FA-BAS-149
    (
        "FA-BAS-149",
        "Paginating Database Query Results with `limit` and `offset`",
        "Query pagination in FastAPI with SQLAlchemy 2.0 is implemented by applying `.limit()` and `.offset()` clauses to the `select()` statement.",
        "Endpoints that return collections must never return entire tables without limits, as large result sets exhaust server memory and cause network latency spikes. Basic pagination uses query parameters `limit` (page size, capped with Pydantic validation) and `offset` (number of records to skip). A companion query using `func.count()` retrieves the total record count to populate pagination metadata headers or response envelopes.",
        "from fastapi import FastAPI, Depends, Query\nfrom pydantic import BaseModel\nfrom sqlalchemy import select, func\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Customer(Base):\n    __tablename__ = 'customers'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db():\n    async with SessionLocal() as session:\n        yield session\n\napp = FastAPI()\n\n@app.get('/customers')\nasync def get_customers(\n    limit: int = Query(default=20, ge=1, le=100),\n    offset: int = Query(default=0, ge=0),\n    db: AsyncSession = Depends(get_db)\n):\n    total_stmt = select(func.count(Customer.id))\n    total = await db.scalar(total_stmt) or 0\n    \n    query = select(Customer).order_by(Customer.id).offset(offset).limit(limit)\n    items = (await db.scalars(query)).all()\n    \n    return {\n        'total': total,\n        'limit': limit,\n        'offset': offset,\n        'items': [{'id': c.id, 'name': c.name} for c in items]\n    }",
        "Implementing offset-based pagination with total count calculation and validated query parameters.",
        "SQLAlchemy compiles `.limit(limit).offset(offset)` into native SQL `LIMIT ? OFFSET ?`. The database skips `offset` rows and returns the next `limit` rows. `func.count(Customer.id)` compiles into `SELECT count(customers.id) AS count_1 FROM customers`.",
        "Admin dashboards, e-commerce product listings, and mobile client list views.",
        ["Why does offset pagination perform poorly on large datasets (e.g., offset > 100,000)?", "How does keyset (cursor) pagination improve performance over offset pagination?"],
        ["Allowing unbounded `limit` values, enabling malicious users to request `limit=1000000` and cause Out-Of-Memory crashes.", "Omitting an explicit `.order_by()`, leading to inconsistent row ordering across paginated pages."],
        "Highlight that for massive tables (>1M rows), keyset pagination (`WHERE id > last_seen_id ORDER BY id LIMIT 20`) is vastly superior to `OFFSET`.",
        ["[Query Parameters](routing-and-dependencies.md)", "[Database Indexing](../05-databases/indexing-and-optimization.md)"],
        ["https://fastapi.tiangolo.com/tutorial/query-params/"]
    ),

    # FA-BAS-150
    (
        "FA-BAS-150",
        "Separating Database Models, Pydantic Schemas, and Route Endpoints",
        "Clean FastAPI architecture maintains strict separation between database entities (SQLAlchemy), data validation/serialization contracts (Pydantic), and HTTP transport (routers).",
        "A critical architectural mistake in FastAPI projects is mixing persistence models with API contracts. Clean architectures enforce a layered separation: 1) `models.py`: Defines database tables, columns, indexes, and relationships using SQLAlchemy `DeclarativeBase`. 2) `schemas.py`: Defines input payloads (`UserCreate`, `UserUpdate`) and output contracts (`UserResponse`) using Pydantic `BaseModel`. 3) `database.py`: Manages the `AsyncEngine`, `async_sessionmaker`, and `get_db` dependency. 4) `routes/`: Contains HTTP route handlers focused strictly on request validation, calling business logic, and returning responses. This separation prevents leaking internal database columns (like password hashes) to external clients.",
        "# Recommended project layout:\n# app/\n# ├── database.py   -> Engine, sessionmaker, get_db dependency\n# ├── models/       -> SQLAlchemy DeclarativeBase models (DB entities)\n# ├── schemas/      -> Pydantic BaseModels (API DTO contracts)\n# ├── services/     -> Business logic & DB queries (Repositories)\n# └── routers/      -> APIRouter endpoints (HTTP layer)\n\nfrom pydantic import BaseModel, EmailStr\n\n# Schemas protect internal database representations\nclass UserReadSchema(BaseModel):\n    id: int\n    email: EmailStr\n    # Notice: hashed_password is NOT exposed here!",
        "Demonstrating clean directory architecture separating ORM models from client-facing Pydantic schemas.",
        "By defining separate Pydantic schemas for input and output, FastAPI generates accurate OpenAPI specifications without exposing internal database implementation details or sensitive database columns.",
        "Enterprise microservices requiring independent evolution of database schemas and public API versions.",
        ["Why should a SQLAlchemy model never be returned directly as an API response without a Pydantic schema?", "What is the Data Transfer Object (DTO) pattern?"],
        ["Adding API validation logic inside SQLAlchemy models instead of Pydantic schemas.", "Exposing sensitive database fields like `hashed_password` or internal audit flags in API responses."],
        "Emphasize the Separation of Concerns: Pydantic validates input and shapes output; SQLAlchemy models persist data.",
        ["[Pydantic Fundamentals](pydantic-and-validation.md)", "[Software Architecture](../10-system-design/fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models"]
    ),
]
