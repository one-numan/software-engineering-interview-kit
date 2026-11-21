"""
fa_async_inter.py
=================
Intermediate FastAPI Async & Concurrency Questions: FA-INT-101 to FA-INT-125 (25 questions)
"""

inter_data = [
    # FA-INT-101
    (
        "FA-INT-101",
        "Starlette AnyIO Threadpool Limiter Tuning",
        "Tuning AnyIO's `CapacityLimiter.total_tokens` expands the maximum number of worker threads available for synchronous `def` routes, preventing thread exhaustion under high concurrent load.",
        "When FastAPI executes synchronous `def` endpoints, it delegates execution to AnyIO's default threadpool. By default, AnyIO sets a `CapacityLimiter` of 40 worker threads. If 60 concurrent requests arrive for synchronous routes that block for 200ms, 40 requests occupy all threads and the remaining 20 requests are queued in memory, causing latency spikes. In high-throughput synchronous workloads, tuning `limiter.total_tokens = 200` in the application lifespan expands thread capacity.",
        "from contextlib import asynccontextmanager\nimport anyio\nfrom fastapi import FastAPI\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    # Expand AnyIO worker threadpool capacity for high-throughput sync operations\n    limiter = anyio.to_thread.current_default_thread_limiter()\n    limiter.total_tokens = 150  # Increase from default 40 to 150 worker threads\n    yield\n\napp = FastAPI(lifespan=lifespan)\n\n@app.get('/sync-heavy')\ndef sync_heavy():\n    return {'status': 'processed in tuned threadpool'}",
        "Expanding AnyIO threadpool capacity limiter during application lifespan startup.",
        "When a synchronous route is executed, `anyio.to_thread.run_sync` acquires a token from the `CapacityLimiter`. Increasing `total_tokens` allows more OS threads to be spawned concurrently before queueing begins.",
        "High-traffic APIs that wrap synchronous legacy microservice clients, synchronous database drivers, or cryptographic hashing functions.",
        ["What are the operating system resource trade-offs of increasing worker threads to 1,000 (RAM per thread stack)?", "How do you monitor whether the AnyIO threadpool is actively queueing tasks?"],
        ["Increasing threadpool tokens to arbitrarily high numbers (e.g. 10,000), causing OS thread exhaustion and high context-switching overhead.", "Assuming tuning the threadpool speeds up CPU-bound operations (threads are still constrained by the GIL)."],
        "Tuning heuristic: Size threadpool tokens based on `Available_RAM / Thread_Stack_Size (8MB)` and downstream database connection pool limits.",
        ["[Threadpool Basics](async-and-concurrency.md)", "[async def vs def](async-and-concurrency.md)"],
        ["https://anyio.readthedocs.io/en/latest/threads.html"]
    ),

    # FA-INT-102
    (
        "FA-INT-102",
        "Offloading CPU-Bound Tasks to Process Pools via ProcessPoolExecutor",
        "Executing CPU-intensive calculations requires dispatching tasks to `concurrent.futures.ProcessPoolExecutor` to bypass the GIL and utilize multiple physical CPU cores.",
        "Because Python's Global Interpreter Lock (GIL) permits only one thread to execute Python bytecode at a time, running CPU-heavy calculations in threadpools or async routes provides zero parallelism. To utilize multiple CPU cores, FastAPI services instantiate a `ProcessPoolExecutor`. Coroutines call `await loop.run_in_executor(pool, heavy_func, *args)`, which serializes arguments, dispatches the job to a separate worker process on another core, and awaits the result without stalling the main event loop.",
        "import math\nimport asyncio\nfrom concurrent.futures import ProcessPoolExecutor\nfrom fastapi import FastAPI\n\napp = FastAPI()\n# Process pool utilizing physical CPU cores\nprocess_pool = ProcessPoolExecutor(max_workers=4)\n\ndef compute_heavy_primes(limit: int) -> int:\n    # Pure CPU calculation executed in separate OS process\n    return sum(1 for i in range(2, limit) if all(i % d != 0 for d in range(2, int(math.sqrt(i)) + 1)))\n\n@app.get('/primes/{limit}')\nasync def get_primes(limit: int):\n    loop = asyncio.get_running_loop()\n    # Non-blocking dispatch to external worker process across CPU cores\n    prime_count = await loop.run_in_executor(process_pool, compute_heavy_primes, limit)\n    return {'limit': limit, 'primes_found': prime_count}",
        "Offloading CPU-bound prime number calculations to a ProcessPoolExecutor across multi-core CPUs.",
        "`run_in_executor` pickles function arguments, sends them across IPC pipes to the child process, and registers an OS pipe watcher on the event loop. The child process executes on a separate CPU core with its own independent GIL.",
        "Resizing images with Pillow, calculating cryptographic hashes, running machine learning feature extraction, and generating complex PDF reports.",
        ["What are the serialization (pickling) overheads of passing large arrays to `ProcessPoolExecutor`?", "Why must `ProcessPoolExecutor` be instantiated once at module level rather than inside route functions?"],
        ["Instantiating a new `ProcessPoolExecutor()` on every incoming request (process creation is extremely expensive).", "Passing non-picklable objects (like active database connections or open file handles) to process pool functions."],
        "Architecture rule: Create a singleton `ProcessPoolExecutor` in your application lifespan and shutdown cleanly on exit via `pool.shutdown()`.",
        ["[I/O vs CPU-Bound](async-and-concurrency.md)", "[Multiprocessing](../01-python/concurrency-and-parallelism.md)"],
        ["https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor"]
    ),

    # FA-INT-103
    (
        "FA-INT-103",
        "asyncio.TaskGroup and Structured Concurrency in Python 3.11+",
        "`asyncio.TaskGroup` provides structured concurrency: child tasks run concurrently, the block awaits all tasks before exiting, and if any child fails, all siblings are cancelled automatically.",
        "Historically, running concurrent tasks with `asyncio.create_task()` created unstructured 'fire-and-forget' tasks: if one task crashed, other tasks continued running as orphaned background zombies, leaking memory. Python 3.11 introduced `asyncio.TaskGroup`. Using `async with asyncio.TaskGroup() as tg:`, multiple tasks are spawned with `tg.create_task()`. The block guarantees that execution does not proceed until all tasks finish. If any task raises an exception, the remaining tasks are immediately cancelled and an `ExceptionGroup` is raised.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def fetch_pricing():\n    await asyncio.sleep(0.01)\n    return 199.99\n\nasync def fetch_inventory():\n    await asyncio.sleep(0.01)\n    return 42\n\n@app.get('/product-summary')\nasync def get_product_summary():\n    # Structured concurrency using Python 3.11+ TaskGroup\n    async with asyncio.TaskGroup() as tg:\n        t1 = tg.create_task(fetch_pricing())\n        t2 = tg.create_task(fetch_inventory())\n    # Execution only reaches here when BOTH tasks have succeeded\n    return {'price': t1.result(), 'inventory': t2.result()}",
        "Executing concurrent tasks with guaranteed completion and automatic cancellation via TaskGroup.",
        "If `fetch_pricing()` raises an error, `TaskGroup` immediately calls `.cancel()` on `t2`, unwinds their execution frames, and raises an `ExceptionGroup` containing all errors.",
        "Coordinating multi-service checkouts where inventory reservation, payment processing, and fraud checks must succeed together or be cleanly cancelled.",
        ["What is an `ExceptionGroup` in Python 3.11 and how do you handle it using `except*` syntax?", "How does `asyncio.TaskGroup` differ from `asyncio.gather()`?"],
        ["Using unmanaged `asyncio.create_task()` without tracking task references, allowing exceptions to be swallowed silently.", "Accessing `task.result()` before the `async with TaskGroup()` block exits."],
        "Python 3.11+ standard: Prefer `asyncio.TaskGroup` over `asyncio.gather()` for structured error propagation and automatic orphan task cleanup.",
        ["[gather vs TaskGroup](async-and-concurrency.md)", "[Exception Handling](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#task-groups"]
    ),

    # FA-INT-104
    (
        "FA-INT-104",
        "WebSocket Connection Pools and In-Memory Broadcast Channels",
        "A centralized `ConnectionManager` class maintains a thread-safe registry of active WebSockets, enabling message broadcasting across connected clients and room channels.",
        "In collaborative applications (chat rooms, live dashboard feeds, trading floors), messages originating from one client or backend event must be fanned out to dozens or hundreds of connected users. In FastAPI, a `ConnectionManager` maintains an in-memory collection of active `WebSocket` objects. When a broadcast is triggered, it iterates over the active connections and sends the message concurrently, handling disconnections gracefully.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect\nimport asyncio\n\napp = FastAPI()\n\nclass ConnectionManager:\n    def __init__(self):\n        self.active_connections: list[WebSocket] = []\n\n    async def connect(self, websocket: WebSocket):\n        await websocket.accept()\n        self.active_connections.append(websocket)\n\n    def disconnect(self, websocket: WebSocket):\n        if websocket in self.active_connections:\n            self.active_connections.remove(websocket)\n\n    async def broadcast(self, message: str):\n        # Fan out message concurrently to all active sockets\n        for connection in self.active_connections:\n            await connection.send_text(message)\n\nmanager = ConnectionManager()\n\n@app.websocket('/ws/feed')\nasync def websocket_endpoint(websocket: WebSocket):\n    await manager.connect(websocket)\n    try:\n        while True:\n            data = await websocket.receive_text()\n            await manager.broadcast(f'Broadcast: {data}')\n    except WebSocketDisconnect:\n        manager.disconnect(websocket)",
        "Managing active WebSocket connections and broadcasting messages using ConnectionManager.",
        "The manager holds references to open ASGI connection scopes. Calling `send_text` on each socket queues text frames directly into the respective client's TCP socket buffer.",
        "Real-time team chat channels, live sports scoreboards, collaborative document editing, and notification feeds.",
        ["What is the limitation of an in-memory `ConnectionManager` when scaling to multiple Uvicorn worker processes?", "How do you broadcast messages concurrently using `asyncio.gather()` inside the manager?"],
        ["Broadcasting sequentially in a slow loop where one slow client delays broadcasts to all other users.", "Failing to remove disconnected sockets from the manager list, causing subsequent broadcasts to crash."],
        "Production tip: For multiple connections, fan out messages concurrently with `asyncio.gather(*[ws.send_text(msg) for ws in pool], return_exceptions=True)`.",
        ["[WebSockets Basics](async-and-concurrency.md)", "[Distributed WebSockets](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/advanced/websockets/"]
    ),

    # FA-INT-105
    (
        "FA-INT-105",
        "Distributed WebSocket Broadcasting with Redis Pub/Sub",
        "Scaling WebSockets across multiple Uvicorn worker processes or Kubernetes pods requires an external Redis Pub/Sub message broker to synchronize broadcasts across nodes.",
        "An in-memory `ConnectionManager` only knows about WebSockets connected to its specific worker process. In a production cluster running 8 Uvicorn worker processes across 3 Kubernetes pods, User A connected to Pod 1 cannot send messages to User B connected to Pod 2 via in-memory lists. Integrating Redis Pub/Sub solves this: each worker process subscribes to Redis channels; when a message is published to Redis, all worker processes receive the event and broadcast it to their locally connected WebSockets.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect\nimport asyncio\n\napp = FastAPI()\n\n# Conceptual Redis Pub/Sub Integration Pattern\nclass RedisBroadcaster:\n    def __init__(self):\n        self.local_sockets: list[WebSocket] = []\n\n    async def publish_message(self, channel: str, text: str):\n        # In production: await redis_client.publish(channel, text)\n        pass\n\n    async def listen_redis_channel(self, channel: str):\n        # In production: async for message in pubsub.listen():\n        #     for ws in self.local_sockets: await ws.send_text(message['data'])\n        pass\n\nbroadcaster = RedisBroadcaster()\n\n@app.websocket('/ws/distributed')\nasync def ws_distributed(ws: WebSocket):\n    await ws.accept()\n    broadcaster.local_sockets.append(ws)\n    try:\n        while True:\n            msg = await ws.receive_text()\n            await broadcaster.publish_message('chat_channel', msg)\n    except WebSocketDisconnect:\n        broadcaster.local_sockets.remove(ws)",
        "Architecture pattern for distributed WebSocket broadcasting across multi-worker clusters via Redis Pub/Sub.",
        "Redis Pub/Sub decouples publishers from subscribers. The message is pushed once to Redis, which fans it out to all subscribing Uvicorn workers in sub-millisecond latency.",
        "Multi-node production chat systems, distributed gaming servers, and real-time collaborative applications on Kubernetes.",
        ["Why doesn't an in-memory Python list work for WebSockets across multiple Gunicorn/Uvicorn workers?", "What is the difference between Redis Pub/Sub and Redis Streams for WebSocket message history?"],
        ["Relying on in-memory state in multi-worker production deployments, causing messages to randomly disappear for other users.", "Failing to handle Redis connection reconnects during transient network partitions."],
        "Scale rule: The moment you run more than 1 worker process, you MUST use Redis Pub/Sub or RabbitMQ to route WebSocket messages between workers.",
        ["[Connection Pools](async-and-concurrency.md)", "[Redis Integration](../06-redis-and-messaging/redis.md)"],
        ["https://redis.io/docs/latest/develop/data-types/pubsub/"]
    ),

    # FA-INT-106
    (
        "FA-INT-106",
        "Handling Client Disconnects during Async Streaming Responses",
        "Detecting client disconnects during long-running streaming responses allows the server to abort expensive database queries and generator iterations immediately.",
        "When streaming large datasets or generative AI tokens using `StreamingResponse`, clients frequently close their browser tab or lose network connectivity before the stream completes. If the server does not detect the disconnect, the async generator continues running to completion, wasting database connections, CPU, and external API credits. By checking `await request.is_disconnected()` inside the iteration loop, the generator halts immediately upon client departure.",
        "import asyncio\nfrom fastapi import FastAPI, Request\nfrom fastapi.responses import StreamingResponse\n\napp = FastAPI()\n\nasync def monitored_event_stream(request: Request):\n    for i in range(100):\n        # Check if the HTTP client has closed the connection\n        if await request.is_disconnected():\n            print('Client disconnected prematurely - aborting streaming task!')\n            break\n        await asyncio.sleep(0.05)\n        yield f'data: Chunk {i}\\n\\n'\n\n@app.get('/stream-monitored')\ndef stream_monitored(request: Request):\n    return StreamingResponse(monitored_event_stream(request), media_type='text/event-stream')",
        "Detecting client disconnects and breaking generator iteration using request.is_disconnected().",
        "`request.is_disconnected()` inspects the ASGI receive stream for an `http.disconnect` message from Uvicorn, which indicates the client closed the TCP socket.",
        "Streaming responses from OpenAI/Gemini LLMs, large financial CSV exports, and continuous telemetry feeds.",
        ["What happens if an endpoint continues streaming after the client closes the TCP socket?", "Why does `is_disconnected()` require an `await` statement?"],
        ["Continuing expensive database queries or LLM token generation after the client has disconnected.", "Polling `is_disconnected()` too frequently in tight loops (checking once per yielded chunk is optimal)."],
        "Resource optimization: Always check `if await request.is_disconnected(): break` inside long-running streaming generators.",
        ["[Streaming Responses](routing-and-dependencies.md)", "[Server-Sent Events](async-and-concurrency.md)"],
        ["https://www.starlette.io/requests/#disconnections"]
    ),

    # FA-INT-107
    (
        "FA-INT-107",
        "Safe Background Task Execution with Async Exit Stacks and Error Logging",
        "Background tasks execute outside the route's exception handler; robust implementations wrap tasks in `try...except` and manage database sessions inside dedicated exit stacks.",
        "When an unhandled exception occurs inside a standard route handler, FastAPI catches it and returns a 500 error. However, `BackgroundTasks` execute *after* the response has already been sent to the client. If an unhandled exception occurs inside a background task, it cannot return an HTTP error; it prints an unhandled traceback to stdout and terminates. Robust background tasks must manage their own error logging, metrics, and database session lifecycles.",
        "import logging\nfrom fastapi import FastAPI, BackgroundTasks\n\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger('background.worker')\n\napp = FastAPI()\n\nasync def safe_background_job(job_id: str, email: str):\n    try:\n        logger.info(f'Starting background job {job_id} for {email}')\n        # Simulated task logic\n        if job_id == 'invalid':\n            raise ValueError('Corrupted job payload')\n        logger.info(f'Job {job_id} completed successfully')\n    except Exception as exc:\n        # Catch and record errors; prevents silent task failure\n        logger.error(f'Background task {job_id} failed: {exc}', exc_info=True)\n\n@app.post('/jobs/{job_id}')\ndef dispatch_job(job_id: str, bg: BackgroundTasks):\n    bg.add_task(safe_background_job, job_id, 'user@example.com')\n    return {'status': 'job dispatched'}",
        "Wrapping background tasks in try...except with structured error logging.",
        "Because the HTTP response lifecycle is over, Starlette's response handler simply awaits background tasks sequentially. The application must handle its own error recovery.",
        "Dispatching analytics events, clearing file caches, and triggering external webhook deliveries post-response.",
        ["Can a background task access a database session passed from a route's `Depends(get_db)` yield dependency?", "Why does using a route's database session in a background task cause `Session is closed` errors?"],
        ["Passing a route-scoped database session into a background task (the session is closed by the route's exit stack before the task runs!).", "Allowing background tasks to fail silently without alerting Sentry or logging."],
        "Database warning: Never pass a route's database session to a background task; create a fresh database session inside the background task itself.",
        ["[BackgroundTasks](async-and-concurrency.md)", "[Database Integration](database-integration.md)"],
        ["https://fastapi.tiangolo.com/tutorial/background-tasks/"]
    ),

    # FA-INT-108
    (
        "FA-INT-108",
        "asyncio.Lock and Synchronization Primitives in Asynchronous Handlers",
        "`asyncio.Lock` synchronizes access to shared in-memory resources across concurrent coroutines running on the event loop, preventing race conditions.",
        "Even though `asyncio` runs on a single thread, race conditions occur whenever a coroutine yields control (`await`) while in the middle of modifying shared state (e.g. read-modify-write operations on an in-memory cache, shared counter, or local file). `asyncio.Lock` ensures that only one coroutine can enter a critical section at a time. Other coroutines attempting to acquire the lock are suspended non-blockingly until the lock is released.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nshared_counter = 0\nlock = asyncio.Lock()\n\n@app.post('/increment')\nasync def increment_counter():\n    global shared_counter\n    # Protect critical section against concurrent race conditions\n    async with lock:\n        current = shared_counter\n        await asyncio.sleep(0.01)  # Simulate async work during calculation\n        shared_counter = current + 1\n    return {'counter': shared_counter}",
        "Synchronizing shared state mutations using asyncio.Lock.",
        "`asyncio.Lock` maintains a FIFO queue of waiting coroutines. When `lock.release()` is called (upon exiting `async with lock`), the loop wakes the next suspended task in the queue.",
        "Protecting in-memory token buckets, managing single-writer file buffers, and coordinating local cache refresh locks (mutex).",
        ["Why do race conditions occur in single-threaded `asyncio` code?", "What is the difference between `threading.Lock` and `asyncio.Lock`?"],
        ["Using `threading.Lock` inside async coroutines (blocks the entire event loop thread instead of suspending the coroutine).", "Holding an `asyncio.Lock` across long-running operations, causing all concurrent requests to queue up."],
        "Lock rule: Never use `threading.Lock` in an `async def` function; always use `asyncio.Lock` to avoid blocking the event loop.",
        ["[Event Loop](async-and-concurrency.md)", "[Concurrency & Parallelism](../01-python/concurrency-and-parallelism.md)"],
        ["https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock"]
    ),

    # FA-INT-109
    (
        "FA-INT-109",
        "asyncio.Semaphore for Rate Limiting Outbound Concurrent Calls",
        "`asyncio.Semaphore` bounds the maximum number of concurrent operations allowed simultaneously, preventing downstream service overload during traffic spikes.",
        "When an API endpoint must fetch data for 500 items concurrently using `asyncio.gather()`, firing 500 simultaneous outbound HTTP requests or database queries can exhaust socket connections or trigger downstream rate limits. `asyncio.Semaphore(max_concurrent)` acts as a concurrency gate: tasks acquire a permit before executing and release it when done, capping active concurrent calls to a safe threshold (e.g. 10 at a time).",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n# Limit outbound concurrency to maximum 5 simultaneous requests\nsemaphore = asyncio.Semaphore(5)\n\nasync def call_downstream_api(item_id: int) -> dict:\n    async with semaphore:\n        # At most 5 coroutines can enter this block simultaneously\n        await asyncio.sleep(0.02)\n        return {'id': item_id, 'status': 'fetched'}\n\n@app.get('/batch-fetch')\nasync def batch_fetch():\n    # Schedule 50 tasks, safely bounded by the semaphore\n    tasks = [call_downstream_api(i) for i in range(50)]\n    results = await asyncio.gather(*tasks)\n    return {'total_fetched': len(results)}",
        "Bounding outbound concurrent API requests using asyncio.Semaphore.",
        "`asyncio.Semaphore` maintains an internal counter initialized to `value`. `acquire()` decrements the counter if > 0, or suspends the coroutine until another task calls `release()`.",
        "Throttling concurrent database queries during batch imports, respecting third-party API rate limits (e.g. OpenAI API calls), and bounding file descriptor usage.",
        ["What happens if you use `asyncio.gather()` on 10,000 items without a semaphore (OS socket exhaustion / EMFILE)?", "How does a Semaphore differ from a Lock?"],
        ["Spawning unbounded concurrent outbound requests with `asyncio.gather(*[call() for call in calls])`.", "Creating a new Semaphore instance inside the loop instead of sharing a single instance."],
        "Production tip: Always wrap high-concurrency `asyncio.gather()` calls in an `asyncio.Semaphore(20)` to prevent socket and database pool exhaustion.",
        ["[asyncio.gather](async-and-concurrency.md)", "[Rate Limiting](authentication-and-security.md)"],
        ["https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore"]
    ),

    # FA-INT-110
    (
        "FA-INT-110",
        "asyncio.Event for Cross-Task Signaling and State Changes",
        "`asyncio.Event` coordinates asynchronous coroutines by allowing multiple tasks to pause execution until a notifying task signals that an event has occurred.",
        "In reactive architectures, tasks frequently need to wait for a specific condition or event without busy-polling in a CPU-wasting `while not ready: await sleep()`. `asyncio.Event` manages an internal boolean flag initialized to `False`. Multiple worker tasks can call `await event.wait()`, suspending non-blockingly. When another task or background job calls `event.set()`, the event loop immediately wakes all waiting coroutines simultaneously.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\nready_event = asyncio.Event()\n\nasync def background_initialization():\n    await asyncio.sleep(0.05)  # Simulate warm-up work (loading ML weights)\n    ready_event.set()          # Signal that system is ready!\n\n@app.on_event('startup')\ndef startup_task():\n    asyncio.create_task(background_initialization())\n\n@app.get('/wait-for-ready')\nasync def wait_for_ready():\n    # Suspends execution until background initialization calls ready_event.set()\n    await ready_event.wait()\n    return {'status': 'system fully initialized'}",
        "Coordinating startup readiness and task synchronization using asyncio.Event.",
        "When `event.set()` is called, `asyncio.Event` iterates through its list of waiting futures and marks them as resolved, scheduling their parent coroutines for immediate resumption on the loop.",
        "Coordinating multi-stage startup pipelines, signaling cache warm-up completion, and implementing graceful shutdown notifications across background workers.",
        ["What is the difference between `event.set()` and `event.clear()`?", "Why is `await event.wait()` superior to a polling loop with `asyncio.sleep()`?"],
        ["Busy-waiting in a loop with `while not flag: await asyncio.sleep(1)` instead of using `asyncio.Event`.", "Calling `event.set()` and forgetting to call `event.clear()` if the event is meant to be recurring."],
        "Clean architecture pattern: Use `asyncio.Event` for clean reactive signaling between decoupled asynchronous tasks.",
        ["[Lifespan Events](async-and-concurrency.md)", "[Event Loop](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-sync.html#asyncio.Event"]
    ),

    # FA-INT-111
    (
        "FA-INT-111",
        "Connection Pooling Mechanics in Asynchronous Database Clients (asyncpg)",
        "Asynchronous database connection pools maintain pre-established TCP sockets to databases, multiplexing queries across pooled connections without connection setup latency.",
        "Opening a new TCP and TLS connection to PostgreSQL takes 20-50 milliseconds and consumes significant database RAM. In high-throughput APIs, opening a connection per request destroys performance. Asynchronous connection pools (like `asyncpg` or SQLAlchemy 2.0 `AsyncEngine`) maintain a pool of pre-authenticated database connections. A route acquires a connection from the pool, executes its query, and immediately releases it back to the pool in a few microseconds.",
        "from fastapi import FastAPI, Depends\nimport asyncio\n\napp = FastAPI()\n\n# Simulated async connection pool\nclass AsyncDatabasePool:\n    def __init__(self):\n        self._connections = ['conn_1', 'conn_2', 'conn_3']\n        self._lock = asyncio.Lock()\n\n    async def acquire(self):\n        return 'active_db_connection'\n\n    async def release(self, conn):\n        pass\n\npool = AsyncDatabasePool()\n\nasync def get_db_connection():\n    conn = await pool.acquire()\n    try:\n        yield conn\n    finally:\n        await pool.release(conn)\n\n@app.get('/users')\nasync def list_users(db=Depends(get_db_connection)):\n    return {'status': 'queried using pooled connection'}",
        "Managing database connection checkout and return using async yield dependency.",
        "The pool maintains a queue of ready sockets. When traffic spikes exceed pool size, requests wait non-blockingly for the next connection to be released rather than crashing the database with 1,000 new connections.",
        "High-throughput PostgreSQL and MySQL querying in microservices serving 10,000+ requests per second.",
        ["What happens if the pool size is too small under high traffic (connection timeouts)?", "Why is opening connections per request catastrophic for PostgreSQL memory?"],
        ["Leaking database connections by not using `try...finally` or `async with pool.acquire()`.", "Setting pool size higher than PostgreSQL's `max_connections` limit, causing database crashes."],
        "Production formula: Pool Size per Worker = `PostgreSQL max_connections / (Number_of_Uvicorn_Workers * Number_of_Pods)`.",
        ["[Database Integration](database-integration.md)", "[Yield Dependencies](routing-and-dependencies.md)"],
        ["https://magicstack.github.io/asyncpg/current/usage.html#connection-pools"]
    ),

    # FA-INT-112
    (
        "FA-INT-112",
        "contextvars and Request Context Propagation across Async Tasks",
        "Python's `contextvars` module provides asynchronous context-local storage that propagates automatically across coroutines and child tasks without leaking between concurrent requests.",
        "In synchronous frameworks, `threading.local()` stores per-request data (like correlation IDs or tenant IDs). In asynchronous frameworks where thousands of requests execute concurrently on the *same* thread, `threading.local()` is completely broken because all requests share the same thread. Python's `contextvars` module solves this: variables are bound to the current asynchronous execution context, propagating safely down coroutine call chains without cross-request contamination.",
        "import contextvars\nimport uuid\nfrom fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n# Request-scoped context variable\nrequest_id_ctx = contextvars.ContextVar('request_id', default='none')\n\n@app.middleware('http')\nasync def request_id_middleware(request: Request, call_next):\n    req_id = str(uuid.uuid4())\n    # Set value for the current async execution context\n    token = request_id_ctx.set(req_id)\n    try:\n        response: Response = await call_next(request)\n        response.headers['X-Request-ID'] = req_id\n        return response\n    finally:\n        request_id_ctx.reset(token)\n\n@app.get('/trace')\nasync def trace_handler():\n    # Automatically accesses the current request's unique ID\n    return {'active_request_id': request_id_ctx.get()}",
        "Storing and propagating request IDs safely across async contexts using contextvars.",
        "When an `asyncio.Task` is spawned, it inherits a copy of the parent's `Context`. Modifications inside child tasks affect only their local context, providing complete isolation between concurrent user requests.",
        "Propagating distributed tracing trace IDs, user authentication tokens, and tenant isolation contexts to logging filters.",
        ["Why does `threading.local()` cause severe data leaks in FastAPI?", "Why is it mandatory to call `ctx_var.reset(token)` in middleware finally blocks?"],
        ["Using `threading.local()` in async FastAPI applications, causing User A to see User B's request context.", "Using global variables to pass request state between functions."],
        "Architecture rule: In asynchronous Python, NEVER use `threading.local()`; ALWAYS use `contextvars.ContextVar`.",
        ["[Shared State in Middleware](routing-and-dependencies.md)", "[Distributed Tracing](routing-and-dependencies.md)"],
        ["https://docs.python.org/3/library/contextvars.html"]
    ),

    # FA-INT-113
    (
        "FA-INT-113",
        "Cancelling Long-Running Async Tasks Gracefully",
        "Cancelling an asyncio task injects `asyncio.CancelledError` at its current `await` point, allowing the task to execute cleanup logic before terminating.",
        "When a user cancels an operation or an endpoint times out, the server should stop processing to free up resources. Calling `task.cancel()` does not forcibly kill the thread; it schedules an `asyncio.CancelledError` exception to be raised inside the coroutine the next time it hits an `await`. Coroutines can catch `CancelledError` in a `try...except` block, perform cleanup, and re-raise it to complete cancellation.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def cancelable_worker():\n    try:\n        print('Worker started running...')\n        await asyncio.sleep(10)  # Waiting operation\n    except asyncio.CancelledError:\n        print('CancelledError received: Releasing locks and closing sockets safely!')\n        raise  # Must re-raise CancelledError to acknowledge cancellation\n    finally:\n        print('Teardown code executed.')\n\n@app.get('/cancel-demo')\nasync def cancel_demo():\n    task = asyncio.create_task(cancelable_worker())\n    await asyncio.sleep(0.01)\n    # Gracefully cancel the running task\n    task.cancel()\n    try:\n        await task\n    except asyncio.CancelledError:\n        pass\n    return {'status': 'task cancelled gracefully'}",
        "Gracefully intercepting and completing task cancellation with CancelledError.",
        "In Python 3.8+, `CancelledError` inherits from `BaseException` (not `Exception`). When raised, `finally` blocks execute normally. If the coroutine does not re-raise `CancelledError`, cancellation is considered rejected.",
        "Cancelling background data exports when clients disconnect, and stopping worker loops during server shutdown.",
        ["Why does `asyncio.CancelledError` inherit from `BaseException` rather than `Exception`?", "What happens if a coroutine catches `CancelledError` and swallows it without re-raising?"],
        ["Catching `Exception` thinking it catches `CancelledError` (in modern Python, `CancelledError` bypasses `except Exception:`).", "Performing slow blocking operations inside cleanup blocks during task cancellation."],
        "Cancellation contract: Always re-raise `CancelledError` after running emergency cleanup in your `finally` block.",
        ["[Task Cancellation in Yield](routing-and-dependencies.md)", "[Setting Timeouts](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel"]
    ),

    # FA-INT-114
    (
        "FA-INT-114",
        "Asynchronous Generator Yield Dependencies in FastAPI",
        "Declaring an `async def` dependency with `yield` manages asynchronous resource lifecycles (`__aenter__` / `__aexit__`) with guaranteed post-response cleanup.",
        "While synchronous yield dependencies use standard generators, asynchronous yield dependencies are declared with `async def` and use `yield`. Code before `yield` can await asynchronous operations (e.g. `conn = await pool.acquire()`). The yielded object is injected into the route. After the response finishes transmitting, code after `yield` executes asynchronously (e.g. `await conn.close()`), managed inside an `AsyncExitStack`.",
        "from fastapi import FastAPI, Depends\nimport asyncio\n\napp = FastAPI()\n\nasync def get_async_resource():\n    print('-> 1. Async Setup: Checkout connection')\n    await asyncio.sleep(0.01)\n    resource = {'id': 'res_42', 'active': True}\n    try:\n        yield resource\n    finally:\n        print('<- 2. Async Teardown: Return connection to pool')\n        await asyncio.sleep(0.01)\n\n@app.get('/async-resource')\nasync def resource_route(res=Depends(get_async_resource)):\n    return {'resource': res['id']}",
        "Managing asynchronous resource checkout and teardown using async yield dependency.",
        "FastAPI inspects `inspect.isasyncgenfunction(dependency)`. It drives the async generator via `await gen.asend(None)` to yield the value, and resumes with `await gen.asend(None)` or `await gen.athrow()` after the response completes.",
        "Managing SQLAlchemy 2.0 `AsyncSession` transactions, checking out Redis connection clients, and releasing distributed locks.",
        ["What is the difference between `yield` in a synchronous dependency vs an asynchronous dependency?", "How does FastAPI guarantee that the `finally` block in an async generator executes if the client disconnects?"],
        ["Using standard `def` for dependencies that need to await async database sessions.", "Yielding multiple times inside an async generator dependency (raises runtime error)."],
        "Clean pattern: Use `async def` yield dependencies for all async database sessions (SQLAlchemy `AsyncSession`).",
        ["[Yield Dependencies](routing-and-dependencies.md)", "[Database Integration](database-integration.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/"]
    ),

    # FA-INT-115
    (
        "FA-INT-115",
        "Streaming Server-Sent Events with Keep-Alive Heartbeats",
        "Long-lived Server-Sent Events streams require periodic keep-alive heartbeat comments (`: ping\\n\\n`) to prevent intermediate proxies, firewalls, and load balancers from dropping idle connections.",
        "In cloud environments, reverse proxies (Nginx, AWS ALB, Cloudflare) automatically terminate idle TCP connections that transmit no data for 60 seconds. In SSE streams where events occur infrequently (e.g. notifications arriving every few minutes), the connection will be dropped by the proxy. Adding a periodic keep-alive heartbeat (sending an SSE comment `: keepalive\\n\\n` every 15-30 seconds) keeps the proxy connection open indefinitely.",
        "import asyncio\nfrom fastapi import FastAPI\nfrom fastapi.responses import StreamingResponse\n\napp = FastAPI()\n\nasync def resilient_sse_generator():\n    counter = 0\n    while True:\n        await asyncio.sleep(5)  # Simulate event wait\n        counter += 1\n        if counter % 2 == 0:\n            # Send real event\n            yield f'data: {{\"event\": \"update\", \"id\": {counter}}}\\n\\n'\n        else:\n            # Send SSE keep-alive heartbeat comment (ignored by browser EventSource)\n            yield ': keepalive\\n\\n'\n\n@app.get('/sse/resilient')\ndef resilient_sse():\n    return StreamingResponse(resilient_sse_generator(), media_type='text/event-stream')",
        "Transmitting periodic keep-alive heartbeats in Server-Sent Events streams.",
        "Under the SSE specification, lines starting with a colon `:` are treated as comments and ignored by browser `EventSource` parsers, but count as active data bytes for TCP proxies.",
        "Live financial tickers, IoT monitoring dashboards, and real-time collaborative applications running behind AWS Application Load Balancers.",
        ["Why do load balancers close idle SSE connections after 60 seconds by default?", "What HTTP header disables response buffering in Nginx reverse proxies (`X-Accel-Buffering: no`)?"],
        ["Sending keep-alive data as regular JSON events instead of SSE comments, confusing client parsers.", "Forgetting `X-Accel-Buffering: no`, causing Nginx to buffer SSE events until buffer fills."],
        "Proxy tip: Always return `headers={'X-Accel-Buffering': 'no'}` and send `: keepalive\\n\\n` every 20 seconds on SSE streams behind Nginx.",
        ["[Server-Sent Events](async-and-concurrency.md)", "[Streaming Responses](routing-and-dependencies.md)"],
        ["https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events"]
    ),

    # FA-INT-116
    (
        "FA-INT-116",
        "Deadlock Scenarios in Asyncio: Circular Waiting and Lock Starvation",
        "Deadlocks in asynchronous Python occur when two or more coroutines mutually wait for locks held by each other, causing all affected tasks to freeze permanently.",
        "Even without threads, `asyncio` code can deadlock. Common scenarios include: 1) Circular Lock Acquisition: Coroutine 1 acquires Lock A and waits for Lock B; Coroutine 2 acquires Lock B and waits for Lock A. 2) Re-entrant Lock Deadlock: A coroutine holding an `asyncio.Lock` attempts to acquire the *same* lock again (standard `asyncio.Lock` is NOT re-entrant). 3) Resource Pool Starvation: Tasks checkout all DB connections and wait for a secondary resource that also needs a DB connection.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\nlock_a = asyncio.Lock()\nlock_b = asyncio.Lock()\n\n# DEADLOCK PREVENTION RULE: Always acquire locks in a globally consistent order!\nasync def safe_worker_1():\n    async with lock_a:\n        async with lock_b:  # Consistent order: A then B\n            pass\n\nasync def safe_worker_2():\n    async with lock_a:      # Consistent order: A then B (prevents deadlock!)\n        async with lock_b:\n            pass",
        "Enforcing consistent lock acquisition hierarchy to prevent circular deadlocks.",
        "When deadlocked, coroutines remain permanently suspended in the event loop's wait queue. Because neither can proceed, execution never resumes.",
        "Managing distributed locks in multi-resource transaction pipelines and shared in-memory caches.",
        ["Why is `asyncio.Lock` not re-entrant (what happens if a task tries to acquire a lock it already holds)?", "How do timeout wrappers (`asyncio.wait_for`) mitigate indefinite deadlock freezes?"],
        ["Acquiring multiple locks in different orders across different endpoints.", "Attempting to acquire an `asyncio.Lock` inside a recursive function without a re-entrant lock pattern."],
        "Deadlock prevention rule: Always acquire multiple locks in the exact same global order across all codebase locations.",
        ["[asyncio.Lock](async-and-concurrency.md)", "[Setting Timeouts](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-sync.html"]
    ),

    # FA-INT-117
    (
        "FA-INT-117",
        "Event Loop Lag Monitoring and Latency Profiling",
        "Event loop lag measures the delay between when a task is scheduled and when the event loop actually executes it, serving as the primary health metric for async services.",
        "In a healthy `asyncio` application, when a timer expires or I/O is ready, the callback executes within 1-2 milliseconds. If a developer introduces blocking CPU code or synchronous calls, the event loop stalls, and pending tasks experience delay. Event loop lag monitors schedule an empty callback every 100ms and measure the actual elapsed time. If elapsed time exceeds 150ms, the delta is the 'loop lag'—the exact duration the event loop was frozen.",
        "import asyncio\nimport time\nfrom fastapi import FastAPI\n\napp = FastAPI()\nloop_lag_ms = 0.0\n\nasync def monitor_loop_lag():\n    global loop_lag_ms\n    while True:\n        start = time.perf_counter()\n        await asyncio.sleep(0.1)  # Expected: 100ms\n        elapsed = time.perf_counter() - start\n        loop_lag_ms = max(0.0, (elapsed - 0.1) * 1000)\n\n@app.on_event('startup')\ndef start_monitor():\n    asyncio.create_task(monitor_loop_lag())\n\n@app.get('/metrics/loop-lag')\ndef get_loop_lag():\n    return {'event_loop_lag_ms': round(loop_lag_ms, 2)}",
        "Continuous event loop lag monitoring background task.",
        "Loop lag directly correlates with API P99 latency. Exporting loop lag to Prometheus allows automated alerting before servers experience outages.",
        "Production observability in Kubernetes pods monitored by Datadog, Prometheus, or Grafana.",
        ["What is an acceptable threshold for event loop lag in high-performance production services (< 20ms)?", "What causes event loop lag spikes in seemingly asynchronous applications?"],
        ["Monitoring only CPU and RAM utilization while ignoring event loop lag (a server can have 10% CPU but 5,000ms loop lag due to a single blocking call!).", "Running heavy profiling tools in production that distort event loop metrics."],
        "Key SRE metric: Event loop lag is the #1 leading indicator of performance degradation in asynchronous Python services.",
        ["[Blocking the Event Loop](async-and-concurrency.md)", "[Performance Profiling](production-and-performance.md)"],
        ["https://github.com/numerodix/eventlet/wiki/Hub-inspection"]
    ),

    # FA-INT-118
    (
        "FA-INT-118",
        "Exception Handling in asyncio.gather(return_exceptions=True)",
        "`return_exceptions=True` in `asyncio.gather()` captures exceptions as return values instead of aborting the entire batch, allowing partial success in concurrent operations.",
        "By default, if any coroutine in `asyncio.gather(a(), b(), c())` raises an exception, `gather` immediately raises that exception, and results from successful sibling tasks are inaccessible. Passing `return_exceptions=True` changes this: `gather` waits for ALL tasks to complete. The returned list contains either successful results or exception objects (`isinstance(res, Exception)`), enabling resilient fallback handling.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def fetch_weather(): return {'temp': 72}\nasync def fetch_news(): raise ConnectionError('News feed down')\nasync def fetch_stocks(): return {'AAPL': 180.5}\n\n@app.get('/resilient-dashboard')\nasync def dashboard():\n    # return_exceptions=True prevents one failed service from crashing the whole dashboard\n    results = await asyncio.gather(fetch_weather(), fetch_news(), fetch_stocks(), return_exceptions=True)\n    \n    weather = results[0] if not isinstance(results[0], Exception) else {'error': 'unavailable'}\n    news = results[1] if not isinstance(results[1], Exception) else {'error': 'news unavailable'}\n    stocks = results[2] if not isinstance(results[2], Exception) else {'error': 'unavailable'}\n    \n    return {'weather': weather, 'news': news, 'stocks': stocks}",
        "Handling partial failures gracefully using asyncio.gather(return_exceptions=True).",
        "`gather` collects exceptions without re-raising. Sibling tasks continue running to normal completion, maximizing data recovery.",
        "Aggregator microservices, multi-source search engines, and dashboard widgets where one third-party failure must not crash the whole page.",
        ["What is the danger of `return_exceptions=True` if the developer forgets to check `isinstance(res, Exception)`?", "How does `asyncio.TaskGroup` handle exceptions compared to `asyncio.gather(return_exceptions=True)`?"],
        ["Treating returned items as successful data without checking `isinstance(r, Exception)`, causing `AttributeError` crashes later in code.", "Using default `gather` in aggregator endpoints, allowing a minor widget failure to cause a 500 error for the entire user request."],
        "Resilience pattern: Always use `return_exceptions=True` in aggregator endpoints to deliver degraded graceful responses instead of 500 errors.",
        ["[asyncio.gather](async-and-concurrency.md)", "[TaskGroup](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.gather"]
    ),

    # FA-INT-119
    (
        "FA-INT-119",
        "Custom Async Lifespans with Multi-Service Health Handshakes",
        "Enterprise application lifespans execute multi-service health handshakes (DB, Redis, Kafka) during startup, aborting server boot if critical dependencies are unreachable.",
        "Starting a web server when its underlying database or message broker is offline causes thousands of immediate 500 errors when traffic hits. A robust enterprise lifespan verifies all downstream dependencies during startup: it connects to PostgreSQL, pings Redis, and checks Kafka brokers within a strict timeout. If any critical service fails the handshake, the lifespan raises an exception, causing Uvicorn to exit immediately with an error code and preventing bad deployments.",
        "from contextlib import asynccontextmanager\nimport asyncio\nfrom fastapi import FastAPI\n\n@asynccontextmanager\nasync def robust_lifespan(app: FastAPI):\n    print('-> 1. Testing PostgreSQL connection...')\n    await asyncio.sleep(0.01)  # Simulates DB handshake\n    \n    print('-> 2. Testing Redis connection...')\n    await asyncio.sleep(0.01)  # Simulates Redis handshake\n    \n    print('-> All infrastructure verified! Server ready for traffic.')\n    yield\n    print('<- Closing database connection pools cleanly.')\n\napp = FastAPI(lifespan=robust_lifespan)",
        "Executing multi-service dependency verification handshakes in application lifespan.",
        "If an exception is raised before `yield`, Uvicorn aborts startup. Kubernetes detects the failure and automatically halts rolling deployments, preserving traffic on healthy existing pods.",
        "Zero-downtime CI/CD deployments and preventing broken containers from receiving live production traffic.",
        ["Why is failing startup preferable to booting with a broken database connection?", "How do Kubernetes readiness probes complement lifespan health handshakes?"],
        ["Swallowing connection errors during startup, allowing broken containers to accept customer traffic.", "Setting excessively long timeouts on startup handshakes, causing container orchestrators to kill pods for timeout."],
        "Reliability principle: Fail fast during startup! If your primary database is down, abort boot so Kubernetes won't route traffic to the broken pod.",
        ["[Lifespan Basics](async-and-concurrency.md)", "[Production Deployment](production-and-performance.md)"],
        ["https://fastapi.tiangolo.com/advanced/events/"]
    ),

    # FA-INT-120
    (
        "FA-INT-120",
        "Asynchronous File Upload Streaming with Chunked Buffers",
        "Streaming uploaded files asynchronously in fixed-size chunk buffers directly to cloud storage avoids buffering entire files in server RAM or temporary disk.",
        "When handling large file uploads (e.g. 500MB video or data exports), reading the entire file into memory with `await file.read()` consumes half a gigabyte of server RAM per upload. By reading in 1MB chunked buffers (`while chunk := await file.read(1024 * 1024):`), memory consumption remains strictly capped at 1MB regardless of whether the uploaded file is 50MB or 50GB.",
        "from fastapi import FastAPI, UploadFile, File\n\napp = FastAPI()\n\n@app.post('/upload-stream')\nasync def upload_stream(file: UploadFile = File(...)):\n    chunk_size = 1024 * 1024  # 1MB buffer\n    total_uploaded = 0\n    \n    # Stream chunks asynchronously with O(1) memory footprint\n    while chunk := await file.read(chunk_size):\n        total_uploaded += len(chunk)\n        # In production: Stream chunk directly to S3 multipart upload\n        \n    await file.close()\n    return {'filename': file.filename, 'total_bytes': total_uploaded}",
        "Streaming large file uploads in 1MB chunks with constant memory consumption.",
        "`UploadFile.read()` reads from Starlette's `SpooledTemporaryFile` asynchronously, keeping memory consumption bounded by `chunk_size`.",
        "Ingesting video assets, audio podcasts, large genomic datasets, and database backup uploads.",
        ["What is the optimal chunk size for streaming file uploads (typically 1MB - 5MB)?", "How does S3 Multipart Upload integrate with chunked streaming in FastAPI?"],
        ["Reading entire large files into RAM with `contents = await file.read()`, causing out-of-memory crashes.", "Forgetting `await file.close()`, leaving orphaned temporary files in the `/tmp` directory."],
        "Memory law: Always process file uploads in chunked loops (`while chunk := await file.read(1024*1024):`) to enforce constant memory usage.",
        ["[File Uploads](routing-and-dependencies.md)", "[UploadFile Security](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile"]
    ),

    # FA-INT-121
    (
        "FA-INT-121",
        "Memory Leak Patterns in Long-Lived WebSocket Connections",
        "Memory leaks in WebSockets occur when connection managers retain references to disconnected sockets, closures capture request scopes, or un-bounded buffers accumulate in memory.",
        "Because WebSockets remain open for hours or days, memory leaks that are harmless in short-lived HTTP requests become fatal. Common leak patterns: 1) Zombie Socket References: Retaining `WebSocket` instances in global broadcast lists after clients disconnect. 2) Unbounded In-Memory Buffers: Appending messages to unconstrained per-user chat histories. 3) Closure Retainment: Event handlers capturing references to large application scopes.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect\nimport weakref\n\napp = FastAPI()\n\n# ANTI-PATTERN: Leaks memory if remove() fails\n# active_sockets = []\n\n# SAFE PATTERN: WeakSet allows garbage collection even if explicit cleanup fails\nactive_sockets = weakref.WeakSet()\n\n@app.websocket('/ws/leak-free')\nasync def leak_free_ws(ws: WebSocket):\n    await ws.accept()\n    active_sockets.add(ws)\n    try:\n        while True:\n            await ws.receive_text()\n    except WebSocketDisconnect:\n        pass  # WeakSet ensures socket is automatically pruned upon garbage collection",
        "Preventing socket memory leaks using weakref.WeakSet for connection tracking.",
        "A `WeakSet` holds weak references to objects. When a disconnected socket has no other references, CPython's reference-counting GC collects it immediately, preventing memory leaks.",
        "Large-scale chat systems, live trading feeds, and IoT telemetry gateways serving 50,000+ concurrent connections.",
        ["What is a Python `WeakSet` and how does it prevent memory retention?", "How do you detect memory leaks in long-running WebSocket services using `tracemalloc`?"],
        ["Appending messages to a user's connection object without length bounds, bloating RAM over long sessions.", "Failing to remove sockets from broadcast lists upon `WebSocketDisconnect`."],
        "Memory tip: Use `weakref.WeakSet` for connection tracking as defense-in-depth against forgotten cleanup in disconnect handlers.",
        ["[WebSocket Disconnect](async-and-concurrency.md)", "[Connection Pools](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/weakref.html#weakref.WeakSet"]
    ),

    # FA-INT-122
    (
        "FA-INT-122",
        "WebSocket Ping/Pong Keep-Alive Configuration in Uvicorn",
        "Uvicorn automatically sends RFC 6455 Ping control frames and expects Pong responses within a timeout window to detect dead connections and keep sockets alive through firewalls.",
        "Network connections frequently die silently (e.g. mobile client enters airplane mode or drops off Wi-Fi without sending a TCP FIN packet). Without heartbeats, the server keeps the socket open indefinitely (half-open socket), leaking memory and file descriptors. Uvicorn solves this via automatic WebSocket Ping/Pong: 1) `--ws-ping-interval 20`: Uvicorn sends a Ping frame every 20 seconds. 2) `--ws-ping-timeout 20`: If the client fails to return a Pong frame within 20 seconds, Uvicorn terminates the dead socket.",
        "# Production Uvicorn command configuring WebSocket heartbeats:\n# $ uvicorn main:app \\\n#     --ws websockets \\\n#     --ws-ping-interval 20 \\\n#     --ws-ping-timeout 20\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\nprint('Uvicorn configured with 20s ping interval to terminate dead half-open sockets.')",
        "Documenting Uvicorn WebSocket ping/pong keep-alive command-line parameters.",
        "RFC 6455 Ping/Pong operates at the protocol transport layer. Browser WebSocket engines handle Pong responses automatically without custom JavaScript code.",
        "Eliminating phantom connections and memory bloat across real-time multiplayer games, live tickers, and collaborative tools.",
        ["What is a 'half-open' TCP socket and why doesn't standard TCP detect it immediately?", "Why does the browser JavaScript WebSocket API not expose Ping/Pong frames to application code?"],
        ["Disabling Uvicorn ping/pong, allowing thousands of dead mobile sockets to consume server memory indefinitely.", "Setting ping intervals too low (e.g. 1 second), generating excessive network overhead."],
        "Production mandate: Always deploy Uvicorn with `--ws-ping-interval 20 --ws-ping-timeout 20` to purge dead half-open sockets automatically.",
        ["[WebSockets Basics](async-and-concurrency.md)", "[Uvicorn Tuning](../11-devops/gunicorn-and-uvicorn.md)"],
        ["https://www.uvicorn.org/settings/#websockets"]
    ),

    # FA-INT-123
    (
        "FA-INT-123",
        "Combining Thread Pools, Process Pools, and Event Loops in a Single API",
        "Architecting complex backend services combines the event loop for I/O, thread pools for legacy synchronous code, and process pools for CPU-intensive tasks.",
        "High-performance production microservices often handle heterogeneous workloads simultaneously: 1) Async Event Loop: Handles high-concurrency network I/O, WebSockets, and Redis queries. 2) AnyIO Threadpool: Runs legacy synchronous database queries or third-party blocking SDKs. 3) ProcessPoolExecutor: Runs heavy CPU tasks (image processing, cryptography) across multi-core CPUs without blocking the event loop. Orchestrating all three in a single FastAPI application provides peak scalability.",
        "import asyncio\nfrom concurrent.futures import ProcessPoolExecutor\nfrom starlette.concurrency import run_in_threadpool\nfrom fastapi import FastAPI\n\napp = FastAPI()\nprocess_pool = ProcessPoolExecutor(max_workers=2)\n\ndef blocking_sync_io(): return 'sync_db_result'\ndef heavy_cpu_math(n: int): return sum(i*i for i in range(n))\n\n@app.get('/hybrid-workload')\nasync def hybrid_route():\n    loop = asyncio.get_running_loop()\n    # 1. Async I/O on event loop\n    await asyncio.sleep(0.01)\n    # 2. Sync I/O offloaded to thread pool\n    db_data = await run_in_threadpool(blocking_sync_io)\n    # 3. CPU math offloaded to process pool across CPU cores\n    calc_result = await loop.run_in_executor(process_pool, heavy_cpu_math, 100000)\n    return {'db': db_data, 'calc': calc_result}",
        "Harmonizing event loop, threadpool, and process pool in a single FastAPI endpoint.",
        "The async event loop orchestrates the pipeline without blocking. Threadpool handles blocking I/O while process pool executes CPU math on independent hardware cores.",
        "Multi-modal AI services: async web gateway -> sync database lookup -> CPU-intensive image embedding generation.",
        ["Why shouldn't CPU-bound calculations run in the AnyIO threadpool?", "What are the IPC overhead costs of transferring data to a ProcessPoolExecutor?"],
        ["Running everything in `async def` without thread or process offloading.", "Spawning multiple process pools instead of sharing a single managed pool across the application."],
        "Architecture synthesis: Event loop for I/O, Threadpool for blocking sync I/O, Process pool for CPU calculations.",
        ["[ProcessPoolExecutor](async-and-concurrency.md)", "[AnyIO Threadpools](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/async/#what-is-concurrency"]
    ),

    # FA-INT-124
    (
        "FA-INT-124",
        "Asynchronous Queueing Patterns with asyncio.Queue",
        "`asyncio.Queue` implements an in-memory, thread-safe asynchronous producer-consumer queue for buffering, smoothing traffic spikes, and decoupling background worker tasks.",
        "When an API receives bursty traffic (e.g. 5,000 incoming telemetry packets per second), writing each packet to a database individually causes connection pool exhaustion. Using `asyncio.Queue` allows route handlers (producers) to push incoming items into an in-memory queue instantly (`await queue.put(item)`), returning an immediate 202 Accepted response. A dedicated async worker coroutine (consumer) reads items from the queue and flushes them to the database in efficient micro-batches.",
        "import asyncio\nfrom fastapi import FastAPI, status\n\napp = FastAPI()\n# Bounded queue preventing memory exhaustion\ntelemetry_queue = asyncio.Queue(maxsize=1000)\n\nasync def batch_consumer():\n    while True:\n        # Read items from queue non-blockingly\n        item = await telemetry_queue.get()\n        # In production: Flush items in micro-batches to database\n        telemetry_queue.task_done()\n\n@app.on_event('startup')\ndef start_worker():\n    asyncio.create_task(batch_consumer())\n\n@app.post('/telemetry', status_code=status.HTTP_202_ACCEPTED)\nasync def ingest_telemetry(payload: dict):\n    # Fast producer: enqueues in microseconds without waiting for DB writes\n    await telemetry_queue.put(payload)\n    return {'status': 'queued'}",
        "Buffering bursty API traffic using an in-memory asyncio.Queue producer-consumer pattern.",
        "`asyncio.Queue` uses condition variables (`asyncio.Event` / `Condition`). If the queue is full (`maxsize`), producers wait non-blockingly; if empty, consumers wait without consuming CPU.",
        "High-frequency IoT sensor telemetry ingestion, log aggregation buffers, and traffic burst smoothing.",
        ["What is the risk of using an unbounded `asyncio.Queue(maxsize=0)` under sustained traffic spikes?", "What happens to queued items if the container is abruptly restarted?"],
        ["Using unbounded queues that accumulate millions of items during database slowdowns, crashing containers with OOM.", "Forgetting to call `queue.task_done()` after processing items."],
        "Queue design rule: Always set an explicit `maxsize` on `asyncio.Queue` to apply backpressure when consumer workers fall behind.",
        ["[BackgroundTasks](async-and-concurrency.md)", "[Backpressure Management](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-queue.html"]
    ),

    # FA-INT-125
    (
        "FA-INT-125",
        "Performance Benchmarking: 10,000 Concurrent Async Connections in FastAPI",
        "FastAPI on Uvicorn with `uvloop` effortlessly handles 10,000+ concurrent idle/streaming connections (C10K problem) on a single container using less than 200MB of RAM.",
        "The classic 'C10K problem' (handling 10,000 concurrent connections on a single server) crippled legacy thread-per-request architectures (like Flask on Apache), where 10,000 threads would require 80GB of RAM for thread stacks alone. In FastAPI on Uvicorn, connections are non-blocking socket descriptors registered with Linux `epoll`. 10,000 idle connections consume less than 200MB of RAM, making FastAPI ideal for high-concurrency WebSocket and SSE workloads.",
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n# FastAPI + Uvicorn + uvloop solves the C10K problem out of the box:\n# Memory per connection is ~15KB (socket buffer + coroutine frame)\n# 10,000 concurrent idle connections = ~150MB RAM total\n\n@app.get('/health')\ndef health():\n    return {'status': 'healthy', 'concurrency_model': 'epoll_uvloop'}",
        "Demonstrating the architecture underpinning FastAPI's C10K concurrency scalability.",
        "`uvloop` uses Linux `epoll` edge-triggered notifications. When any of the 10,000 sockets receives data, the kernel notifies the single event loop thread, which dispatches the coroutine in microseconds.",
        "Handling massive concurrent WebSocket connections in gaming, chat platforms, and real-time dashboard gateways.",
        ["What is the C10K problem and why did thread-per-request architectures fail to solve it?", "What Linux kernel settings (`ulimit -n`, `somaxconn`) must be tuned to support 10,000 concurrent sockets?"],
        ["Hitting OS open file descriptor limits (`ulimit -n 1024`) during load tests and misdiagnosing it as a Python framework limit.", "Comparing raw hello-world benchmarks to real database-backed production workloads."],
        "System tuning tip: Increase `ulimit -n 65536` and `net.core.somaxconn = 4096` in Linux to allow Uvicorn to accept 10,000+ concurrent connections.",
        ["[uvloop Internals](async-and-concurrency.md)", "[Linux Epoll](async-and-concurrency.md)"],
        ["https://www.uvicorn.org/"]
    ),
]
