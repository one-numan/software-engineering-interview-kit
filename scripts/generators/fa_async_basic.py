"""
fa_async_basic.py
=================
Basic FastAPI Async & Concurrency Questions: FA-BAS-101 to FA-BAS-125 (25 questions)
"""

basic_data = [
    # FA-BAS-101
    (
        "FA-BAS-101",
        "async def vs standard def in FastAPI Route Handlers",
        "FastAPI executes `async def` routes directly on the main event loop thread, while standard synchronous `def` routes are automatically dispatched to an external AnyIO worker thread pool.",
        "One of FastAPI's most powerful architectural features is its dual execution model: 1) `async def`: The route handler is a coroutine that runs directly on the single-threaded asyncio event loop. It MUST use non-blocking I/O (`await`) to avoid freezing the server. 2) standard `def`: If you define an endpoint with plain `def`, FastAPI recognizes it as synchronous and automatically offloads execution to an external AnyIO threadpool using `run_in_threadpool`. This allows using legacy blocking libraries (like standard `requests` or `psycopg2`) without blocking other concurrent requests.",
        "import time\nimport asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n# Asynchronous: Runs directly on event loop; non-blocking\n@app.get('/async-op')\nasync def async_op():\n    await asyncio.sleep(0.05)\n    return {'mode': 'async', 'concurrency': 'event_loop'}\n\n# Synchronous: Offloaded to external worker threadpool automatically\n@app.get('/sync-op')\ndef sync_op():\n    time.sleep(0.05)  # Safe in threadpool; does NOT block event loop\n    return {'mode': 'sync', 'concurrency': 'worker_threadpool'}",
        "Contrasting async def (event loop) with standard def (threadpool) execution models.",
        "When an incoming HTTP request matches a standard `def` route, Starlette wraps the call in `anyio.to_thread.run_sync`. A worker thread is leased from the pool, the synchronous code runs, and the result is signaled back to the event loop.",
        "Migrating legacy synchronous Django/Flask code into FastAPI microservices, or building mixed services with both async DB queries and sync PDF generators.",
        ["What happens if you use `time.sleep()` inside an `async def` route?", "Which executes faster for purely non-I/O in-memory calculations: `def` or `async def`?"],
        ["Using `async def` everywhere blindly and calling blocking libraries inside it (freezes the entire web server).", "Assuming `def` routes in FastAPI block all concurrent requests (they run in a threadpool)."],
        "Golden rule: Use `async def` ONLY when calling asynchronous libraries with `await`; use plain `def` if you call blocking or synchronous code.",
        ["[ASGI vs WSGI](fundamentals.md)", "[AnyIO Threadpools](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/async/#in-a-hurry"]
    ),

    # FA-BAS-102
    (
        "FA-BAS-102",
        "How FastAPI Executes Standard def Routes in AnyIO Threadpools",
        "FastAPI leverages AnyIO's `run_in_threadpool` to dispatch synchronous routes to a bounded pool of OS worker threads, allowing concurrent execution of blocking operations.",
        "In traditional synchronous frameworks (Flask/Django), serving concurrent requests requires spawning multiple worker processes or greenlets. In FastAPI, the ASGI server runs on an event loop, but delegates synchronous `def` routes to an AnyIO worker thread pool. The thread pool maintains a capacity limiter (default 40 threads). When a sync route is called, an idle thread picks up the job, executes the blocking code, and returns the result to the awaiting event loop.",
        "from fastapi import FastAPI\nfrom starlette.concurrency import run_in_threadpool\nimport time\n\napp = FastAPI()\n\ndef heavy_blocking_computation(n: int) -> int:\n    time.sleep(0.01)\n    return n * n\n\n@app.get('/compute/{n}')\nasync def compute(n: int):\n    # Explicitly offloading a blocking function from inside an async route\n    result = await run_in_threadpool(heavy_blocking_computation, n)\n    return {'input': n, 'result': result}",
        "Offloading synchronous blocking functions to the AnyIO threadpool using run_in_threadpool.",
        "`run_in_threadpool` uses `anyio.to_thread.run_sync`, which manages context variable propagation (`contextvars`) across the thread boundary, ensuring request state is preserved.",
        "Executing third-party synchronous SDKs (like Stripe or Boto3), hashing passwords with Bcrypt, or resizing images with Pillow.",
        ["What is the default size of the AnyIO thread pool used by FastAPI?", "Why does `contextvars` propagation matter when dispatching to a worker thread?"],
        ["Spawning manual `threading.Thread` instances inside routes instead of using `run_in_threadpool`.", "Exhausting the threadpool with long-running jobs (e.g. 5-minute exports) instead of using background queues."],
        "Architecture insight: Plain `def` routes in FastAPI give you multi-threaded concurrency out of the box with zero manual thread management.",
        ["[async def vs def](async-and-concurrency.md)", "[Threadpool Tuning](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/async/#path-operation-functions"]
    ),

    # FA-BAS-103
    (
        "FA-BAS-103",
        "The Python Event Loop and Cooperative Multitasking in Uvicorn",
        "The Python Event Loop manages concurrent I/O by switching between coroutines cooperatively whenever a task yields control at an `await` statement.",
        "Unlike operating system preemptive multitasking (where the OS kernel forcibly pauses threads), Python's `asyncio` uses cooperative multitasking on a single OS thread. The event loop continuously polls registered socket descriptors for readiness. When a coroutine hits `await socket.read()`, it yields control back to the event loop. The loop runs other pending tasks until the socket receives bytes, at which point it resumes the original coroutine where it left off.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def task_a():\n    print('Task A started')\n    await asyncio.sleep(0.01)  # Yields control to event loop\n    print('Task A finished')\n\nasync def task_b():\n    print('Task B started')\n    await asyncio.sleep(0.01)  # Yields control to event loop\n    print('Task B finished')\n\n@app.get('/cooperative')\nasync def cooperative_demo():\n    # Runs both tasks concurrently on the single event loop thread\n    await asyncio.gather(task_a(), task_b())\n    return {'status': 'tasks executed cooperatively'}",
        "Demonstrating cooperative multitasking with asyncio.gather yielding at await points.",
        "Uvicorn uses `uvloop` (a Cython wrapper around Node.js's `libuv` C library on Linux/macOS) as the event loop engine, achieving tens of thousands of I/O switches per second with minimal CPU overhead.",
        "Serving thousands of concurrent idle or streaming HTTP connections (WebSockets, SSE) on a single container with minimal RAM.",
        ["Why is it called 'cooperative' multitasking (what happens if a coroutine refuses to yield control)?", "How does `uvloop` improve event loop throughput over the standard library `asyncio` loop?"],
        ["Assuming `asyncio` runs multiple coroutines on multiple CPU cores in parallel (it runs on ONE thread).", "Believing `await` makes synchronous code asynchronous (only non-blocking coroutines can be awaited)."],
        "Core concept: An event loop cannot interrupt a running task; tasks MUST cooperatively surrender control using `await`.",
        ["[ASGI vs WSGI](fundamentals.md)", "[uvloop Internals](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-eventloop.html"]
    ),

    # FA-BAS-104
    (
        "FA-BAS-104",
        "What is a Coroutine and How await Pauses Execution",
        "A coroutine is a specialized Python generator-like function declared with `async def` that can suspend execution at `await` and resume later without blocking the underlying thread.",
        "In Python, calling a normal function executes its code immediately and returns a value. Calling an `async def` function does NOT execute its code immediately; it returns a `coroutine` object. The coroutine's body only runs when it is scheduled on an event loop and awaited (`await my_coro()`). The `await` keyword suspends the execution frame of the current coroutine, saving local variables on the heap, and passes control back to the event loop until the awaited `Future` completes.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def fetch_remote_data() -> str:\n    # Coroutine function\n    await asyncio.sleep(0.02)\n    return 'external_payload'\n\n@app.get('/coroutine-demo')\nasync def handler():\n    # 1. Calling fetch_remote_data() creates a coroutine object\n    coro = fetch_remote_data()\n    assert asyncio.iscoroutine(coro)\n    \n    # 2. 'await' pauses handler() until coro completes\n    data = await coro\n    return {'data': data}",
        "Demonstrating coroutine instantiation and execution suspension via await.",
        "In CPython, coroutines are implemented via `PyCoroObject`. When paused at `await`, the execution frame (`PyFrameObject`) remains preserved in memory until resumed via `send()` or `throw()`.",
        "Executing concurrent database queries, microservice HTTP calls, and distributed cache lookups.",
        ["What is the return value of an `async def` function when called without `await`?", "Can you use `await` outside of an `async def` function?"],
        ["Calling a coroutine without `await` (e.g. `data = fetch_data()`), which returns an unexecuted coroutine object and logs a `RuntimeWarning: coroutine was never awaited`.", "Using `await` inside a standard synchronous `def` function (syntax error)."],
        "Compiler rule: You can only use `await` inside an `async def` function; calling an async function without `await` does not execute it.",
        ["[Event Loop](async-and-concurrency.md)", "[async def vs def](async-and-concurrency.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#coroutines"]
    ),

    # FA-BAS-105
    (
        "FA-BAS-105",
        "Background Tasks with BackgroundTasks in FastAPI",
        "`BackgroundTasks` allows route handlers to schedule lightweight post-response tasks (like sending emails or audit logs) to execute after the HTTP response has been sent to the client.",
        "In many web operations, the client does not need to wait for secondary operations to finish before receiving an HTTP response (e.g. user registration shouldn't wait for a welcome email to be delivered). FastAPI provides `BackgroundTasks`. You declare a parameter `background_tasks: BackgroundTasks` and call `background_tasks.add_task(func, *args)`. FastAPI sends the HTTP response to the client immediately and runs the background task afterwards in the same process.",
        "from fastapi import FastAPI, BackgroundTasks\nimport time\n\napp = FastAPI()\n\ndef write_audit_log(email: str, message: str):\n    time.sleep(0.05)  # Simulated file/DB write\n    print(f'Audit log written for {email}: {message}')\n\n@app.post('/register')\ndef register(email: str, background_tasks: BackgroundTasks):\n    # 1. Schedule background task\n    background_tasks.add_task(write_audit_log, email, 'User account created')\n    # 2. Client receives response IMMEDIATELY without waiting for write_audit_log\n    return {'status': 'user registered', 'email': email}",
        "Scheduling a post-response audit log write using FastAPI BackgroundTasks.",
        "FastAPI inherits `BackgroundTasks` from Starlette. When the ASGI response transmission completes, Starlette runs scheduled tasks sequentially. If a task is synchronous (`def`), it runs in the threadpool; if async (`async def`), it is awaited on the loop.",
        "Sending transactional confirmation emails, updating non-critical analytics counters, and clearing temporary upload buffers.",
        ["What happens if an unhandled exception occurs inside a `BackgroundTask`?", "When should you use Celery instead of FastAPI's built-in `BackgroundTasks`?"],
        ["Using `BackgroundTasks` for mission-critical jobs like payment processing (if the container crashes, in-memory background tasks are lost).", "Queueing heavy multi-hour data processing jobs in `BackgroundTasks` instead of dedicated worker queues."],
        "Rule of thumb: Use `BackgroundTasks` for short, lightweight, non-critical operations (emails, logs). Use Celery/RabbitMQ for mission-critical or heavy tasks.",
        ["[Background Processing](../06-redis-and-messaging/background-processing.md)", "[Celery Integration](../06-redis-and-messaging/celery.md)"],
        ["https://fastapi.tiangolo.com/tutorial/background-tasks/"]
    ),

    # FA-BAS-106
    (
        "FA-BAS-106",
        "asyncio.sleep() vs time.sleep() in Asynchronous Route Handlers",
        "`asyncio.sleep()` yields control back to the event loop allowing other requests to execute, whereas `time.sleep()` freezes the entire OS thread, halting all concurrent requests.",
        "The most critical bug in asynchronous Python programming is using synchronous blocking calls inside `async def` functions. `time.sleep(5)` is an OS-level sleep: it puts the single Python thread to sleep for 5 seconds. Because FastAPI runs all `async def` routes on that same thread, ALL concurrent user requests freeze. In contrast, `await asyncio.sleep(5)` creates an async timer: it tells the event loop 'wake me in 5 seconds' and immediately yields control, allowing thousands of other requests to be processed in the meantime.",
        "import time\nimport asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n# CATASTROPHIC BUG: Freezes the entire web server for 5 seconds for ALL users!\n@app.get('/bad-sleep')\nasync def bad_sleep():\n    time.sleep(0.05)  # BLOCKS THE ENTIRE EVENT LOOP\n    return {'status': 'bad'}\n\n# PROPER ASYNC: Yields control cooperatively to event loop\n@app.get('/good-sleep')\nasync def good_sleep():\n    await asyncio.sleep(0.05)  # Other requests continue running seamlessly\n    return {'status': 'good'}",
        "Contrasting blocking time.sleep() with non-blocking await asyncio.sleep().",
        "`time.sleep()` invokes the operating system's `nanosleep()` system call on the current OS thread. `asyncio.sleep()` schedules a callback in the event loop's timer wheel and yields execution back to the loop's selector.",
        "Simulating network delays in tests, implementing polling backoff loops, and throttling rate-limited external API clients.",
        ["What happens if a developer puts `requests.get()` inside an `async def` route?", "How can you detect if an endpoint is blocking the event loop?"],
        ["Using `time.sleep()` in an `async def` route (freezes all concurrent traffic).", "Using `asyncio.sleep()` without `await` (does not sleep at all and returns an unawaited coroutine)."],
        "Golden rule of async: Never, ever call blocking functions (`time.sleep`, `requests.get`, `urllib`) inside an `async def` function.",
        ["[Event Loop](async-and-concurrency.md)", "[Blocking the Event Loop](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.sleep"]
    ),

    # FA-BAS-107
    (
        "FA-BAS-107",
        "I/O-Bound vs CPU-Bound Work in Python Web Services",
        "I/O-bound tasks spend most time waiting for external network/disk operations and thrive on `asyncio`, while CPU-bound tasks consume processor cores and require multiprocessing.",
        "Understanding the nature of your workload determines concurrency architecture: 1) I/O-Bound: Operations that spend 99% of time waiting for external systems (database queries, Redis calls, HTTP requests to third-party APIs, disk reads). Python's `asyncio` is exceptionally effective for I/O-bound tasks because a single thread can manage 10,000+ waiting sockets. 2) CPU-Bound: Operations that actively calculate numbers in Python (image resizing, video encoding, password hashing, machine learning matrix math, large JSON serialization). CPU-bound tasks block the event loop and are constrained by the GIL, requiring multi-process pools.",
        "from fastapi import FastAPI\n\n# I/O-Bound: Ideal for async/await\n# Database queries, Redis lookups, external HTTP API calls\n\n# CPU-Bound: Requires ProcessPoolExecutor or background worker\n# Image transformation, data encryption, statistical simulations",
        "Categorizing backend workloads into I/O-bound vs CPU-bound disciplines.",
        "During I/O waits, the Python thread is idle and the OS handles socket buffers. During CPU calculations, CPython bytecode instructions consume 100% of a core while holding the Global Interpreter Lock (GIL).",
        "Architecting backend services: handling 50k concurrent WebSocket connections with `asyncio` vs delegating image resizing to Celery worker processes.",
        ["Why doesn't `asyncio` speed up CPU-bound calculations?", "How do you run CPU-bound calculations in FastAPI without blocking the event loop?"],
        ["Writing an `async def` function to calculate prime numbers or process images, wondering why all other requests freeze.", "Using multiprocessing for simple I/O-bound database queries (wastes memory and process coordination)."],
        "Mental model: Asyncio is for WAITING (I/O); Multiprocessing is for WORKING (CPU).",
        ["[CPU-Bound in FastAPI](async-and-concurrency.md)", "[Multithreading vs Multiprocessing](../01-python/concurrency-and-parallelism.md)"],
        ["https://fastapi.tiangolo.com/async/#what-is-concurrency"]
    ),

    # FA-BAS-108
    (
        "FA-BAS-108",
        "Why asyncio Does NOT Make CPU-Bound Calculations Faster",
        "`asyncio` provides concurrent scheduling on a single OS thread, meaning CPU-heavy calculations will monopolize the core and block the event loop entirely.",
        "A widespread misconception among junior engineers is believing that adding `async` makes Python code run in parallel across multiple CPU cores. Python's `asyncio` is single-threaded cooperative multitasking. When a function executes CPU-intensive code (e.g. loop computing 10 million hashes), there are no `await` statements yielding control to the event loop. The calculation monopolizes the thread, the event loop cannot service incoming network packets, and all concurrent user requests time out.",
        "from fastapi import FastAPI\nimport math\n\napp = FastAPI()\n\n# ANTI-PATTERN: Heavy CPU work in async def blocks the entire server!\n@app.get('/heavy-cpu')\nasync def heavy_cpu():\n    # Monopolizes the event loop thread for 500ms; freezes all other requests!\n    total = sum(math.sqrt(i) for i in range(1000000))\n    return {'result': total}",
        "Demonstrating how CPU-bound calculations block the single event loop thread in async def.",
        "Because Python's `asyncio` event loop runs on one operating system thread, CPU-bound code executes sequentially. Parallel execution requires separate OS processes (`ProcessPoolExecutor`) to utilize multi-core hardware.",
        "Recognizing when to offload machine learning model inference, cryptographic hashing, or video transcoding to separate worker processes.",
        ["How does Python's Global Interpreter Lock (GIL) impact multithreading for CPU-bound tasks?", "How do you offload CPU-bound calculations to a `ProcessPoolExecutor` in FastAPI?"],
        ["Believing `asyncio` utilizes multiple CPU cores.", "Placing heavy mathematical computations directly in `async def` endpoint handlers."],
        "Interview answer: 'Asyncio is concurrency, not parallelism. It allows waiting for multiple I/O operations simultaneously on one thread, but cannot distribute CPU work across multiple cores.'",
        ["[I/O vs CPU-Bound](async-and-concurrency.md)", "[ProcessPoolExecutor](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/async/#what-is-parallelism"]
    ),

    # FA-BAS-109
    (
        "FA-BAS-109",
        "WebSockets Basics in FastAPI with @app.websocket",
        "FastAPI defines real-time full-duplex communication channels using the `@app.websocket()` decorator and the `WebSocket` connection parameter.",
        "While standard HTTP follows a request-response lifecycle where the client initiates and the server responds, WebSockets (RFC 6455) provide persistent, bidirectional, full-duplex communication over a single TCP connection. Once connected, both client and server can transmit data frames at any time with minimal header overhead. FastAPI supports WebSockets out of the box using `@app.websocket('/path')`.",
        "from fastapi import FastAPI, WebSocket\n\napp = FastAPI()\n\n@app.websocket('/ws')\nasync def websocket_endpoint(websocket: WebSocket):\n    # 1. Accept incoming connection handshake\n    await websocket.accept()\n    # 2. Bidirectional message loop\n    while True:\n        data = await websocket.receive_text()\n        await websocket.send_text(f'Echo from server: {data}')",
        "Building a minimal WebSocket echo server in FastAPI.",
        "The connection begins with an HTTP GET request containing `Upgrade: websocket`. Uvicorn upgrades the protocol, transfers the socket to the ASGI `websocket` scope, and executes the route handler as a long-lived async coroutine.",
        "Real-time chat applications, live financial stock tickers, online multiplayer games, and collaborative document editing.",
        ["What is the difference between HTTP polling and WebSockets?", "What happens if you do not call `await websocket.accept()`?"],
        ["Forgetting `await websocket.accept()`, causing client connection attempts to hang.", "Writing a synchronous `while True` loop inside a WebSocket handler without `await`."],
        "Emphasize: WebSockets are persistent connections; your route handler remains running in an async `while True` loop until the socket disconnects.",
        ["[WebSocket Lifecycle](async-and-concurrency.md)", "[WebSocket Disconnect](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/advanced/websockets/"]
    ),

    # FA-BAS-110
    (
        "FA-BAS-110",
        "WebSocket Connection Lifecycle: accept(), receive_text(), send_text(), close()",
        "The WebSocket lifecycle consists of accepting the handshake (`accept()`), streaming messages (`receive_*`, `send_*`), and cleanly terminating the connection (`close()`).",
        "Operating a WebSocket endpoint requires managing four core lifecycle methods on the `WebSocket` object: 1) `await websocket.accept()`: Completes the HTTP-to-WebSocket handshake. 2) `await websocket.receive_text()` / `receive_json()` / `receive_bytes()`: Waits for the client to transmit a frame. 3) `await websocket.send_text()` / `send_json()` / `send_bytes()`: Transmits data to the client. 4) `await websocket.close(code=1000)`: Cleanly closes the socket connection with an RFC 6455 status code.",
        "from fastapi import FastAPI, WebSocket\n\napp = FastAPI()\n\n@app.websocket('/ws/lifecycle')\nasync def ws_lifecycle(ws: WebSocket):\n    # 1. Handshake\n    await ws.accept()\n    # 2. Receive and send\n    msg = await ws.receive_text()\n    await ws.send_json({'received': msg, 'status': 'success'})\n    # 3. Clean close\n    await ws.close(code=1000)",
        "Demonstrating the four primary stages of the WebSocket lifecycle.",
        "Under the hood, Starlette translates these calls into ASGI messages: `websocket.accept`, `websocket.receive`, `websocket.send`, and `websocket.close`.",
        "Building interactive terminal sessions, streaming IoT sensor readings, and managing notification feeds.",
        ["What does WebSocket close code 1000 signify (Normal Closure)?", "Can a server send JSON directly to a WebSocket client without manual string serialization?"],
        ["Attempting to `send_text` before calling `accept()`.", "Calling `receive_text()` after the connection has already closed."],
        "Convenience tip: Use `await websocket.receive_json()` and `await websocket.send_json()` for automatic JSON parsing and serialization over WebSockets.",
        ["[WebSocket Basics](async-and-concurrency.md)", "[WebSocket Disconnect](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/advanced/websockets/"]
    ),

    # FA-BAS-111
    (
        "FA-BAS-111",
        "Handling WebSocket Disconnections with WebSocketDisconnect",
        "When a client closes a WebSocket connection or loses network connectivity, Starlette raises a `WebSocketDisconnect` exception that must be caught to release resources.",
        "WebSockets are long-lived, but clients inevitably disconnect: users navigate away, close browser tabs, or mobile devices enter tunnels. When the socket drops, calling `await websocket.receive_text()` raises a `starlette.websockets.WebSocketDisconnect` exception. If unhandled, this logs noisy error traces and leaves dangling references in connection pools. The standard pattern wraps the message loop in a `try...except WebSocketDisconnect` block to clean up state.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect\n\napp = FastAPI()\n\nclass ConnectionPool:\n    def __init__(self):\n        self.active_sockets = []\n    async def connect(self, ws: WebSocket):\n        await ws.accept()\n        self.active_sockets.append(ws)\n    def remove(self, ws: WebSocket):\n        self.active_sockets.remove(ws)\n\npool = ConnectionPool()\n\n@app.websocket('/ws/chat')\nasync def chat(ws: WebSocket):\n    await pool.connect(ws)\n    try:\n        while True:\n            msg = await ws.receive_text()\n    except WebSocketDisconnect:\n        # Clean cleanup when client disconnects\n        pool.remove(ws)\n        print('Client disconnected cleanly; removed from pool.')",
        "Handling client disconnects safely using try...except WebSocketDisconnect.",
        "When Uvicorn receives a TCP FIN packet or close frame, Starlette raises `WebSocketDisconnect(code=...)`. Catching this allows executing pool eviction and resource cleanup.",
        "Preventing memory leaks and zombie socket references in chat rooms, live dashboard feeds, and collaborative workspaces.",
        ["What happens if an unhandled `WebSocketDisconnect` propagates out of the route handler?", "How do you extract the client's close code from `WebSocketDisconnect`?"],
        ["Failing to catch `WebSocketDisconnect`, leaking socket references in memory lists and causing future broadcasts to fail.", "Trying to call `await websocket.send_text()` after catching `WebSocketDisconnect`."],
        "Best practice: Always wrap WebSocket message loops in `try...except WebSocketDisconnect` to ensure connection managers stay clean.",
        ["[WebSocket Lifecycle](async-and-concurrency.md)", "[Connection Pools](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections"]
    ),

    # FA-BAS-112
    (
        "FA-BAS-112",
        "Introduction to Server-Sent Events (SSE) in FastAPI",
        "Server-Sent Events (SSE) provide a lightweight, unidirectional HTTP streaming protocol allowing servers to push live text updates to browser clients over a single HTTP connection.",
        "While WebSockets provide bidirectional communication, many applications only require the server to push updates to the client (e.g. streaming LLM token generation, live stock price updates, dashboard metric feeds). WebSockets are complex, require special proxies, and do not support HTTP/2 multiplexing out of the box. SSE uses standard HTTP: the server returns `Content-Type: text/event-stream` and streams formatted text events (`data: ...\\n\\n`). Browsers natively handle SSE using the `EventSource` JavaScript API with automatic reconnection.",
        "import asyncio\nfrom fastapi import FastAPI\nfrom fastapi.responses import StreamingResponse\n\napp = FastAPI()\n\nasync def live_ticker():\n    for price in [100.5, 101.2, 102.0, 101.8]:\n        await asyncio.sleep(0.01)\n        # SSE standard format: 'data: <payload>\\n\\n'\n        yield f'data: {{\"price\": {price}}}\\n\\n'\n\n@app.get('/stocks/live')\ndef stream_stock_prices():\n    return StreamingResponse(live_ticker(), media_type='text/event-stream')",
        "Streaming live ticker updates to clients using Server-Sent Events (SSE) with StreamingResponse.",
        "SSE operates on standard HTTP/1.1 or HTTP/2. The server keeps the HTTP response stream open indefinitely, flushing chunks as they are generated by the async generator.",
        "Streaming ChatGPT/Gemini token responses in generative AI apps, live sports scoreboards, and CI/CD build log viewers.",
        ["How does Server-Sent Events (SSE) compare to WebSockets in protocol complexity and directionality?", "Why must every SSE event terminate with two newline characters (`\\n\\n`)?"],
        ["Using heavy WebSockets when unidirectional server-to-client streaming was all that was needed.", "Forgetting the trailing `\\n\\n` in SSE chunks, causing browser `EventSource` clients to buffer indefinitely."],
        "Architecture rule: If communication is unidirectional (server -> client), prefer SSE over WebSockets for simplicity, HTTP/2 multiplexing, and built-in browser reconnection.",
        ["[Streaming Responses](routing-and-dependencies.md)", "[WebSockets Basics](async-and-concurrency.md)"],
        ["https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"]
    ),

    # FA-BAS-113
    (
        "FA-BAS-113",
        "Lifespan Events in FastAPI: @asynccontextmanager vs Legacy on_event",
        "Modern FastAPI manages startup and shutdown lifecycles using an `@asynccontextmanager` lifespan function, replacing legacy `@app.on_event('startup')` handlers.",
        "Web services frequently require setup actions before accepting traffic (e.g. initializing database connection pools, warming machine learning models, connecting to Redis) and cleanup actions on shutdown. In modern FastAPI, lifecycles are defined using a single `@asynccontextmanager` function passed to `FastAPI(lifespan=lifespan)`. Code before `yield` runs at startup; code after `yield` runs at shutdown. This replaces legacy `@app.on_event` and provides unified error handling and state sharing.",
        "from contextlib import asynccontextmanager\nfrom fastapi import FastAPI\n\n# Modern lifespan management in FastAPI\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    # 1. Startup: Connect to DB and warm caches\n    print('-> Application starting up: Initializing database connection pool')\n    app.state.db_pool = {'status': 'connected', 'pool_size': 20}\n    yield\n    # 2. Shutdown: Close connections and flush buffers safely\n    print('<- Application shutting down: Closing database connection pool')\n    app.state.db_pool['status'] = 'closed'\n\napp = FastAPI(lifespan=lifespan)",
        "Managing application startup and shutdown lifecycle using modern asynccontextmanager lifespan.",
        "The ASGI lifespan protocol runs before the socket starts listening for HTTP traffic. Starlette invokes `lifespan.__aenter__` during boot and `lifespan.__aexit__` when receiving SIGTERM.",
        "Initializing SQLAlchemy 2.0 AsyncEngines, connecting to Redis, loading PyTorch model weights, and registering with Consul/Eureka service registries.",
        ["Why was `@app.on_event('startup')` deprecated in favor of `lifespan`?", "How can you share initialized resources (like DB pools) from `lifespan` to route handlers (`app.state`)?"],
        ["Using deprecated `@app.on_event('startup')` in greenfield FastAPI applications.", "Performing blocking synchronous operations inside the async lifespan function."],
        "Migration mandate: Always use `@asynccontextmanager` for application lifecycles; it guarantees cleanup runs even if startup encounters errors.",
        ["[Database Integration](database-integration.md)", "[Production Deployment](production-and-performance.md)"],
        ["https://fastapi.tiangolo.com/advanced/events/"]
    ),

    # FA-BAS-114
    (
        "FA-BAS-114",
        "Async Context Managers (async with) in FastAPI Routes",
        "Async context managers (`async with`) guarantee deterministic acquisition and release of asynchronous resources (locks, client sessions, transactions) across route executions.",
        "Just as synchronous Python uses `with` to manage file handles, asynchronous Python uses `async with` to manage asynchronous resources implementing `__aenter__` and `__aexit__`. Inside FastAPI routes, `async with` ensures that network sessions (like `httpx.AsyncClient`), distributed locks, or database transactions are cleanly committed or rolled back and sockets are released back to the pool, even if unhandled exceptions occur.",
        "import httpx\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/fetch-external')\nasync def fetch_external():\n    # Safe async context management: Client session is cleanly closed upon exit\n    async with httpx.AsyncClient() as client:\n        # In production: resp = await client.get('https://httpbin.org/get')\n        pass\n    return {'status': 'external call completed cleanly'}",
        "Managing HTTP client session lifecycle safely using async with.",
        "`async with` awaits the `__aenter__()` coroutine upon entering the block. When exiting (normally or via exception), it awaits `__aexit__(exc_type, exc_val, exc_tb)`, ensuring socket cleanup.",
        "Managing database transactions (`async with session.begin():`), acquiring Redis distributed locks, and managing HTTP client connection pools.",
        ["What is the difference between `__enter__` and `__aenter__`?", "What happens if an unhandled exception occurs inside an `async with` block?"],
        ["Using standard `with` on an async context manager, raising `AttributeError: __enter__`.", "Creating unclosed HTTP client sessions outside an `async with` block, leaking TCP sockets."],
        "Resource safety rule: Always wrap async I/O clients and transactions in `async with` blocks to prevent socket leaks.",
        ["[Async HTTP Clients](async-and-concurrency.md)", "[Yield Dependencies](routing-and-dependencies.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#async-context-managers"]
    ),

    # FA-BAS-115
    (
        "FA-BAS-115",
        "Async Iterators and Generators (async for, yield) in Streaming Routes",
        "Async generators (`async def` with `yield`) produce data streams incrementally, enabling memory-efficient HTTP chunked responses and live event streams.",
        "While standard generators yield values synchronously, asynchronous generators yield values produced by asynchronous operations (e.g. reading from a network socket or streaming database cursor). Declared as an `async def` function containing `yield`, consumers iterate over them using `async for item in gen:`. In FastAPI, pairing async generators with `StreamingResponse` streams data to clients in real time with constant O(1) memory usage.",
        "import asyncio\nfrom fastapi import FastAPI\nfrom fastapi.responses import StreamingResponse\n\napp = FastAPI()\n\nasync def number_stream():\n    for i in range(5):\n        await asyncio.sleep(0.01)  # Simulate async work\n        yield f'Chunk {i}\\n'\n\n@app.get('/stream-numbers')\ndef stream_numbers():\n    return StreamingResponse(number_stream(), media_type='text/plain')",
        "Streaming incremental chunks using an async generator and StreamingResponse.",
        "An async generator implements `__aiter__` and `__anext__`. When `StreamingResponse` iterates over it, it awaits the next chunk and flushes it immediately across the ASGI socket.",
        "Exporting massive database tables to CSV, streaming LLM chat tokens, and delivering live audit log feeds.",
        ["What is the difference between `for` and `async for`?", "How does an async generator handle client cancellation mid-stream?"],
        ["Using `return` instead of `yield` inside a streaming generator.", "Buffering all elements in a list before yielding, completely defeating the purpose of streaming."],
        "Memory tip: Async generators allow streaming 10GB datasets with only 5MB of server RAM.",
        ["[Streaming Responses](routing-and-dependencies.md)", "[Server-Sent Events](async-and-concurrency.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#asynchronous-generators"]
    ),

    # FA-BAS-116
    (
        "FA-BAS-116",
        "Running Multiple Concurrent Async Calls with asyncio.gather",
        "`asyncio.gather(*coros)` executes multiple asynchronous operations concurrently on the event loop, returning a combined list of results once all tasks finish.",
        "When an API endpoint must fetch data from multiple independent sources (e.g. querying a user profile from PostgreSQL, fetching recommendations from Redis, and checking order history from a third-party microservice), executing them sequentially with `await a(); await b(); await c()` wastes time. `asyncio.gather(a(), b(), c())` schedules all three tasks on the event loop simultaneously, reducing total endpoint latency to the duration of the single slowest operation.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\nasync def fetch_user():\n    await asyncio.sleep(0.02)\n    return {'username': 'alice'}\n\nasync def fetch_orders():\n    await asyncio.sleep(0.03)\n    return [{'id': 101, 'item': 'Laptop'}]\n\n@app.get('/dashboard')\nasync def get_dashboard():\n    # Executes both coroutines concurrently on the event loop\n    user, orders = await asyncio.gather(fetch_user(), fetch_orders())\n    return {'user': user, 'orders': orders}",
        "Executing independent async calls concurrently using asyncio.gather.",
        "`asyncio.gather` wraps each coroutine into an `asyncio.Task` and registers callbacks. If any task raises an exception, by default `gather` immediately raises it unless `return_exceptions=True` is configured.",
        "Building API gateway aggregator endpoints (BFF - Backend For Frontend) that consolidate data from multiple backend microservices.",
        ["What happens if one task in `asyncio.gather()` raises an unhandled exception?", "How does `return_exceptions=True` alter error handling in `asyncio.gather`?"],
        ["Awaiting independent async calls sequentially (`await call1(); await call2()`), doubling or tripling API response latency.", "Using `asyncio.gather()` on CPU-bound operations expecting multi-core parallelism."],
        "Latency optimization: Whenever an endpoint makes 2 or more independent I/O calls, ALWAYS execute them concurrently with `asyncio.gather()`.",
        ["[Event Loop](async-and-concurrency.md)", "[Exception Handling in Gather](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.gather"]
    ),

    # FA-BAS-117
    (
        "FA-BAS-117",
        "Setting Timeouts on Async Operations with asyncio.wait_for",
        "`asyncio.wait_for(coro, timeout=seconds)` sets a strict execution deadline on asynchronous operations, raising `TimeoutError` and cancelling the task if it exceeds the limit.",
        "In production microservice architectures, relying on external services without timeouts is a dangerous liability: if a downstream service hangs, your worker tasks pile up, exhausting socket connections and causing cascading failures. `asyncio.wait_for()` wraps any coroutine with an expiration deadline. If the operation does not finish within the timeout, `wait_for` automatically cancels the underlying task and raises `asyncio.TimeoutError`.",
        "import asyncio\nfrom fastapi import FastAPI, HTTPException, status\n\napp = FastAPI()\n\nasync def slow_third_party_call():\n    await asyncio.sleep(2.0)  # Simulates slow external service\n    return {'status': 'success'}\n\n@app.get('/external-data')\nasync def get_external_data():\n    try:\n        # Enforce strict 0.5-second SLA deadline\n        data = await asyncio.wait_for(slow_third_party_call(), timeout=0.5)\n        return data\n    except asyncio.TimeoutError:\n        raise HTTPException(\n            status_code=status.HTTP_504_GATEWAY_TIMEOUT,\n            detail='Downstream service timed out'\n        )",
        "Enforcing strict SLA deadlines on downstream async operations with asyncio.wait_for.",
        "When the timeout expires, `asyncio.wait_for` calls `task.cancel()`, which injects an `asyncio.CancelledError` into the coroutine to release resources, and raises `TimeoutError`.",
        "Protecting services from hanging third-party payment gateways, slow database queries, and unresponsive microservices.",
        ["Why is it critical that `asyncio.wait_for()` cancels the inner task upon timeout?", "How should your API respond when a downstream dependency times out (504 Gateway Timeout)?"],
        ["Making outbound network calls without explicit timeouts, risking thread and socket exhaustion.", "Catching generic `Exception` and hiding `TimeoutError`."],
        "Resilience rule: Never make an external network call without a timeout. Wrap downstream calls in `asyncio.wait_for()`.",
        ["[Async HTTP Clients](async-and-concurrency.md)", "[Task Cancellation](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for"]
    ),

    # FA-BAS-118
    (
        "FA-BAS-118",
        "Asynchronous HTTP Clients: httpx.AsyncClient vs requests",
        "`httpx.AsyncClient` is a modern, non-blocking asynchronous HTTP client designed for `asyncio`, whereas `requests` is strictly synchronous and blocks the event loop.",
        "When an API endpoint must call other HTTP services, using Python's standard `requests` library inside an `async def` route freezes the event loop because `requests` uses blocking sockets. `httpx.AsyncClient` is the standard async HTTP client for FastAPI. It provides a familiar API matching `requests`, but uses non-blocking async I/O (`await client.get(...)`), supports connection pooling, HTTP/2, and integrates natively into `asyncio` pipelines.",
        "import httpx\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n# INSECURE ANTI-PATTERN in async def:\n# import requests\n# data = requests.get('https://api.com')  # FREEZES EVENT LOOP!\n\n# SECURE & ASYNC PATTERN:\n@app.get('/proxy-data')\nasync def proxy_data():\n    async with httpx.AsyncClient(timeout=5.0) as client:\n        # Non-blocking async HTTP call\n        resp = await client.get('https://httpbin.org/json')\n        return {'proxied_data': resp.json()}",
        "Making non-blocking external HTTP calls using httpx.AsyncClient.",
        "`httpx` leverages AnyIO and non-blocking socket selectors under the hood. While waiting for the external server's response bytes, the event loop handles hundreds of other incoming requests.",
        "Microservice communication, querying payment gateways (Stripe), and consuming external REST APIs.",
        ["Why shouldn't you instantiate a new `httpx.AsyncClient()` on every request in high-traffic services?", "How can you share a persistent `httpx.AsyncClient` across the entire FastAPI application lifecycle?"],
        ["Importing and using `requests.get()` inside `async def` routes.", "Creating `httpx.AsyncClient()` without setting explicit connection timeouts."],
        "Production tip: Create a singleton `httpx.AsyncClient()` inside your application `lifespan` and attach it to `app.state.http_client` to reuse connection pools.",
        ["[Lifespan Events](async-and-concurrency.md)", "[Blocking the Event Loop](async-and-concurrency.md)"],
        ["https://www.python-httpx.org/async/"]
    ),

    # FA-BAS-119
    (
        "FA-BAS-119",
        "What Happens When You Block the Event Loop in an async def Route",
        "Blocking the event loop stalls the single OS execution thread, preventing Uvicorn from processing incoming network connections, health checks, and concurrent coroutines.",
        "Because `async def` routes execute directly on the main event loop thread, executing any blocking operation (like `time.sleep()`, synchronous database queries, slow CPU calculations, or `requests.get()`) halts the event loop. While the thread is blocked, Uvicorn cannot process incoming TCP handshakes, existing coroutines cannot resume, and container orchestrators (Kubernetes) receive no response on `/healthz` probes, resulting in cascading pod restarts and service blackouts.",
        "from fastapi import FastAPI\nimport time\n\napp = FastAPI()\n\n@app.get('/unresponsive')\nasync def block_server():\n    # Catastrophic: Entire container becomes completely unresponsive for 2 seconds\n    time.sleep(2.0)\n    return {'status': 'recovered'}",
        "Demonstrating server-wide event loop freeze caused by blocking call in async def.",
        "Uvicorn's event loop selector is blocked in the synchronous call. Sockets buffer in the OS TCP backlog until the backlog overflows and clients receive `Connection Refused` errors.",
        "Diagnosing intermittent 504 Gateway Timeouts and Kubernetes pod liveness probe failures during high-traffic surges.",
        ["How do Kubernetes liveness probes trigger pod restarts when the event loop is blocked?", "What monitoring tools detect event loop lag in Python (e.g. `aiomonitor`)?"],
        ["Assuming blocking only affects the single user making the request (it blocks ALL users on that worker process).", "Running CPU-intensive JSON parsing or cryptography directly in `async def` routes."],
        "Architectural rule: If you must run blocking synchronous code, declare the endpoint as standard `def` (so it runs in a threadpool) or use `run_in_threadpool`.",
        ["[async def vs def](async-and-concurrency.md)", "[Event Loop Lag](async-and-concurrency.md)"],
        ["https://fastapi.tiangolo.com/async/#in-a-hurry"]
    ),

    # FA-BAS-120
    (
        "FA-BAS-120",
        "AnyIO as FastAPI's Asynchronous Structured Concurrency Library",
        "AnyIO is the asynchronous networking and concurrency library powering Starlette and FastAPI, providing structured concurrency primitives and cross-runtime compatibility (Asyncio/Trio).",
        "Underneath Starlette and FastAPI sits `anyio`. While Python's standard `asyncio` is powerful, its APIs historically lacked structured concurrency and cross-platform consistency. AnyIO provides: 1) Structured Concurrency: Task groups that ensure child tasks are cleanly scoped and cancelled if siblings fail. 2) Safe Thread Offloading: `anyio.to_thread.run_sync` for threadpool execution. 3) Cross-Runtime: Code written with AnyIO can run on either `asyncio` or `trio`.",
        "from fastapi import FastAPI\nimport anyio\n\napp = FastAPI()\n\nasync def async_worker(task_id: int):\n    await anyio.sleep(0.01)\n    return f'Worker {task_id} completed'\n\n@app.get('/taskgroup-demo')\nasync def run_structured_tasks():\n    # AnyIO TaskGroup enforces structured concurrency\n    async with anyio.create_task_group() as tg:\n        tg.start_soon(async_worker, 1)\n        tg.start_soon(async_worker, 2)\n    return {'status': 'All child tasks in task group completed safely'}",
        "Executing structured concurrent tasks using AnyIO TaskGroup in FastAPI.",
        "An AnyIO `TaskGroup` guarantees that execution does not leave the context block until all spawned tasks complete. If any child task raises an exception, all other sibling tasks are automatically cancelled.",
        "Managing multi-stage background pipelines, orchestrating parallel network requests, and structured error handling.",
        ["What is Structured Concurrency and why is it safer than unstructured `asyncio.create_task()`?", "How does AnyIO manage threadpool capacity limits?"],
        ["Spawning 'fire-and-forget' background tasks with `asyncio.create_task()` that swallow exceptions silently.", "Ignoring unhandled exceptions in background child tasks."],
        "Clean concurrency principle: Use `anyio.create_task_group()` or Python 3.11+ `asyncio.TaskGroup` to ensure no orphan tasks leak.",
        ["[TaskGroup](async-and-concurrency.md)", "[Threadpool Limiter](async-and-concurrency.md)"],
        ["https://anyio.readthedocs.io/en/latest/"]
    ),

    # FA-BAS-121
    (
        "FA-BAS-121",
        "Background Tasks vs Dedicated Task Queues (Celery/RabbitMQ)",
        "`BackgroundTasks` runs in-memory within the same web server process, whereas dedicated queues (Celery/RabbitMQ) distribute persistent, fault-tolerant jobs across dedicated worker clusters.",
        "Architecting background processing requires choosing the right tool: 1) `BackgroundTasks`: In-process, lightweight, zero infrastructure setup. However, tasks live in process RAM: if the web server restarts, deploys, or crashes, all pending tasks are permanently lost. 2) Celery / RabbitMQ / Redis Queues: Distributed, persistent, retryable, and independent of web server lifecycles. If a web container dies, jobs remain safe in the message broker.",
        "from fastapi import FastAPI, BackgroundTasks\n\napp = FastAPI()\n\n# Use BackgroundTasks for: Short, non-critical, ephemeral tasks\n# Examples: Sending confirmation email, deleting local temp file\n\n# Use Celery / RabbitMQ for: Heavy, critical, long-running tasks\n# Examples: Processing video encoding, financial ledger reconciliation, batch ML inference",
        "Contrasting in-process BackgroundTasks with distributed Celery workers.",
        "`BackgroundTasks` runs on the local event loop or threadpool after sending the response. Celery serializes task arguments to a message broker (RabbitMQ/Redis) consumed by independent worker nodes.",
        "Choosing between sending a welcome email (`BackgroundTasks`) vs generating a 100MB tax report (Celery).",
        ["What happens to pending `BackgroundTasks` when a Kubernetes pod terminates during a rolling deployment?", "How does Celery provide automatic task retries with exponential backoff?"],
        ["Using `BackgroundTasks` for mission-critical jobs that must never be lost (e.g. payment processing).", "Deploying complex Celery and RabbitMQ clusters when simple in-process `BackgroundTasks` would suffice."],
        "Decision heuristic: If losing the task due to a server crash is acceptable, use `BackgroundTasks`. If the task MUST run, use Celery.",
        ["[BackgroundTasks](async-and-concurrency.md)", "[Celery Integration](../06-redis-and-messaging/celery.md)"],
        ["https://fastapi.tiangolo.com/tutorial/background-tasks/"]
    ),

    # FA-BAS-122
    (
        "FA-BAS-122",
        "Reading Request Body Asynchronously with await request.body()",
        "`await request.body()` streams and buffers the raw incoming request bytes asynchronously from the network socket without blocking the event loop.",
        "In scenarios where an endpoint needs to inspect raw request bytes (such as computing HMAC webhook signatures, receiving custom binary formats, or processing raw XML), developers access Starlette's `request.body()`. Because reading network bytes involves socket I/O, `request.body()` is a coroutine and must be awaited. Starlette reads chunks from the ASGI `receive` callable, buffering bytes in memory and caching them on `request._body` for subsequent reads.",
        "from fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.post('/raw-payload')\nasync def handle_raw_payload(request: Request):\n    # Non-blocking async read of raw byte stream\n    raw_bytes: bytes = await request.body()\n    return {\n        'byte_length': len(raw_bytes),\n        'preview_hex': raw_bytes[:16].hex()\n    }",
        "Reading raw incoming request bytes asynchronously using await request.body().",
        "Starlette iterates over ASGI `http.request` messages until `more_body=False` is received. It caches the assembled byte string, allowing multiple dependencies to call `await request.body()` safely.",
        "Verifying Stripe/GitHub HMAC webhook signatures, ingesting raw Protobuf payloads, and logging raw request sizes.",
        ["What is the memory risk of calling `await request.body()` on a 500MB file upload?", "Why is `request.body()` cached on the request instance after the first read?"],
        ["Calling `await request.body()` on massive file uploads (exhausts server RAM; use `request.stream()` instead).", "Forgetting `await` when calling `request.body()`, resulting in an unawaited coroutine object."],
        "Memory tip: For small payloads (JSON, webhooks), `await request.body()` is safe; for large file uploads, stream chunks via `request.stream()`.",
        ["[HMAC Webhook Signing](authentication-and-security.md)", "[File Uploads](routing-and-dependencies.md)"],
        ["https://www.starlette.io/requests/#request-body"]
    ),

    # FA-BAS-123
    (
        "FA-BAS-123",
        "Asynchronous File I/O with aiofiles in FastAPI Routes",
        "Standard Python `open()` blocks the operating system thread; non-blocking asynchronous file operations require `aiofiles` to delegate disk I/O to thread pools.",
        "Operating systems do not provide truly asynchronous file system APIs comparable to network sockets (epoll/kqueue). Calling standard `with open('file.txt', 'r') as f: f.read()` inside an `async def` route halts the event loop while the thread waits for disk heads or network filesystems. The library `aiofiles` wraps file operations in threadpools, providing an `async with aiofiles.open()` interface that keeps the event loop responsive.",
        "import aiofiles\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/read-async-file')\nasync def read_file():\n    # In production: aiofiles delegates blocking disk I/O to a worker thread\n    # async with aiofiles.open('/tmp/sample.txt', mode='r') as f:\n    #     contents = await f.read()\n    return {'status': 'file read without blocking event loop'}",
        "Reading files asynchronously without blocking the event loop using aiofiles.",
        "`aiofiles` runs blocking file system calls (`read`, `write`, `seek`) inside an executor thread pool, exposing coroutines that the main event loop can await cooperatively.",
        "Reading local configuration files, streaming large static assets from disk, and writing incoming file uploads safely.",
        ["Why don't standard Linux kernels support truly asynchronous file system I/O (unlike network sockets)?", "What is Linux `io_uring` and how will it change asynchronous file I/O in Python?"],
        ["Using standard `open()` inside `async def` routes, causing event loop stalls on slow network filesystems (NFS).", "Forgetting to `await` file operations when using `aiofiles` (e.g. `await f.read()`)."],
        "Best practice: If your endpoint reads or writes files on disk inside an `async def` function, always use `aiofiles`.",
        ["[File Uploads](routing-and-dependencies.md)", "[Blocking the Event Loop](async-and-concurrency.md)"],
        ["https://github.com/tinom/aiofiles"]
    ),

    # FA-BAS-124
    (
        "FA-BAS-124",
        "Common Async Anti-patterns in FastAPI",
        "Prevalent async anti-patterns include calling blocking libraries in `async def`, forgetting `await` on coroutines, and mixing CPU-heavy calculations into event loop handlers.",
        "Writing asynchronous code introduces unique failure modes that do not exist in synchronous programming: 1) The 'Sync-in-Async' trap: Calling `time.sleep()`, `requests.get()`, or synchronous ORM queries inside `async def`. 2) The Unawaited Coroutine: Calling `fetch_data()` without `await`, resulting in unexecuted tasks and silent bugs. 3) Unbounded Concurrency: Spawning 10,000 tasks with `asyncio.gather()` without a semaphore, exhausting database connection pools and file descriptors.",
        "from fastapi import FastAPI\nimport asyncio\n\napp = FastAPI()\n\n# ANTI-PATTERN 1: Unawaited coroutine\nasync def async_notification():\n    await asyncio.sleep(0.01)\n\n@app.get('/anti-pattern-demo')\nasync def demo():\n    # BUG: Calling without await; task NEVER runs!\n    # async_notification()\n    \n    # CORRECT: Must await the coroutine\n    await async_notification()\n    return {'status': 'fixed'}",
        "Identifying and fixing the unawaited coroutine anti-pattern.",
        "CPython detects unawaited coroutines when they are garbage collected, printing `RuntimeWarning: coroutine was never awaited`. In production, this means operations were silently skipped.",
        "Code review audits, onboarding engineers transitioning from Flask/Django to FastAPI, and production debugging.",
        ["What are the three most dangerous async anti-patterns in FastAPI services?", "How does `asyncio.Semaphore` prevent unbounded concurrency in `asyncio.gather()`?"],
        ["Silencing `RuntimeWarning: coroutine was never awaited` warnings instead of fixing missing `await` calls.", "Believing that wrapping blocking synchronous code in an `async def` function magically makes it non-blocking."],
        "Code review checklist: Verify that every coroutine is awaited, no synchronous blocking libraries are imported in async routes, and gather calls are bounded.",
        ["[Blocking the Event Loop](async-and-concurrency.md)", "[Semaphore](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html"]
    ),

    # FA-BAS-125
    (
        "FA-BAS-125",
        "Debugging Async Code and Inspecting Running Tasks with asyncio.all_tasks()",
        "`asyncio.all_tasks()` inspects all currently scheduled, running, or stalled coroutines on the event loop, enabling diagnosis of deadlocks and hanging requests.",
        "When an asynchronous service becomes sluggish or stops responding, traditional thread stack traces (`threading.enumerate()`) show only a single thread stuck in the event loop selector. Debugging requires inspecting active asyncio tasks: `asyncio.all_tasks()` returns a set of all active `Task` objects. Printing their stack traces (`task.print_stack()`) reveals exactly which line of code each coroutine is currently waiting on, exposing deadlocks and stalled network calls.",
        "import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/debug/tasks')\nasync def debug_active_tasks():\n    # Inspect all active coroutines currently scheduled on the event loop\n    tasks = asyncio.all_tasks()\n    task_info = []\n    for t in tasks:\n        task_info.append({\n            'task_name': t.get_name(),\n            'coro': t.get_coro().__name__ if hasattr(t, 'get_coro') else 'unknown',\n            'done': t.done(),\n            'cancelled': t.cancelled()\n        })\n    return {'total_active_tasks': len(tasks), 'tasks': task_info}",
        "Inspecting active asyncio tasks on the event loop for diagnostic debugging.",
        "`asyncio.all_tasks()` queries the event loop's internal task registry. Each task preserves its current execution frame, allowing programmatic inspection of coroutine state.",
        "Diagnosing mysterious request hangs, locating unclosed background loops, and monitoring worker concurrency in production.",
        ["How do you assign custom names to asyncio tasks for easier debugging (`task.set_name()`)?", "What is `PYTHONASYNCIODEBUG=1` and what does it reveal about slow callbacks?"],
        ["Restarting production servers blindly when requests hang instead of capturing task dump traces.", "Failing to enable asyncio debug mode in staging environments to detect slow callbacks."],
        "Diagnostic superpower: Set `PYTHONASYNCIODEBUG=1` in your staging container to automatically log any callback that blocks the event loop for longer than 100ms.",
        ["[Event Loop Lag](async-and-concurrency.md)", "[Deadlocks in Asyncio](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-task.html#asyncio.all_tasks"]
    ),
]
