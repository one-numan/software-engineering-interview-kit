"""
fa_mid_inter.py
===============
Intermediate FastAPI Middleware & Exception Handling Questions: FA-INT-151 to FA-INT-175 (25 questions)
"""

inter_data = [
    # FA-INT-151
    (
        "FA-INT-151",
        "Pure ASGI Middleware vs `BaseHTTPMiddleware` Performance Comparison",
        "Pure ASGI middleware operates directly on `scope`, `receive`, and `send` without memory allocations, whereas `BaseHTTPMiddleware` spawns AnyIO task groups and buffers streaming responses.",
        "While `BaseHTTPMiddleware` (used by `@app.middleware('http')`) is convenient, it introduces significant architectural overhead: 1) It spawns an AnyIO task group for every request; 2) It buffers streaming responses into memory, increasing latency and memory usage; 3) It can cause subtle context-variable leaks across task boundaries. By contrast, a Pure ASGI middleware is a standard 3-callable class that intercepts low-level ASGI events directly. Pure ASGI middleware executes 2x-5x faster and natively supports non-buffering streaming responses and WebSockets.",
        "from fastapi import FastAPI\nfrom starlette.types import ASGIApp, Scope, Receive, Send\n\n# High-performance Pure ASGI Middleware\nclass PureASGIMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send):\n        if scope['type'] != 'http':\n            await self.app(scope, receive, send)\n            return\n            \n        async def custom_send(message):\n            if message['type'] == 'http.response.start':\n                headers = list(message.get('headers', []))\n                headers.append((b'x-asgi-engine', b'pure-asgi-v1'))\n                message['headers'] = headers\n            await send(message)\n            \n        await self.app(scope, receive, custom_send)\n\napp = FastAPI()\napp.add_middleware(PureASGIMiddleware)",
        "Implementing a zero-overhead pure ASGI middleware modifying response headers via send interceptor.",
        "Pure ASGI middleware directly wraps the ASGI `(scope, receive, send)` coroutine. When the downstream application emits an `http.response.start` message, the middleware intercepts the event dictionary, mutates byte headers in-place, and forwards the packet directly to the server socket.",
        "High-performance microservices serving tens of thousands of requests per second with strict P99 latency budgets.",
        ["Why does `BaseHTTPMiddleware` break streaming responses in certain Starlette versions?", "Can Pure ASGI middleware handle both HTTP and WebSocket connections?"],
        ["Using `BaseHTTPMiddleware` for high-throughput streaming endpoints without realizing it buffers the stream in memory.", "Confusing ASGI byte strings (e.g. `b'x-header'`) with Python unicode strings in ASGI headers."],
        "Emphasize: For high-concurrency production services, write Pure ASGI middleware rather than `BaseHTTPMiddleware`.",
        ["[ASGI Architecture](async-and-concurrency.md)", "[Streaming Responses](async-and-concurrency.md)"],
        ["https://github.com/encode/starlette/issues/1012"]
    ),

    # FA-INT-152
    (
        "FA-INT-152",
        "The Streaming Response Buffering Problem in `BaseHTTPMiddleware`",
        "`BaseHTTPMiddleware` consumes and buffers streaming response chunks inside an internal task group, negating the memory and latency benefits of `StreamingResponse`.",
        "When an endpoint returns a `StreamingResponse` (e.g. video streaming, massive CSV exports, or AI token streams via Server-Sent Events), chunks are intended to be transmitted over the socket immediately. When wrapped in `BaseHTTPMiddleware`, Starlette executes the endpoint inside a background task and pipes chunks through an in-memory queue. This queue can cause high memory consumption, delay chunk delivery, and cause connection hang-ups if clients disconnect prematurely.",
        "# Architecture comparison:\n# 1. BaseHTTPMiddleware Pipeline:\n#    Route -> In-Memory Queue -> TaskGroup -> Middleware -> Network Socket\n#    (Results in buffering, increased TTFB, and memory spikes)\n#\n# 2. Pure ASGI Middleware Pipeline:\n#    Route -> ASGI send('http.response.body') -> Network Socket (Direct Zero-Copy Stream)",
        "Contrasting the buffered queue architecture of BaseHTTPMiddleware with zero-copy pure ASGI.",
        "`BaseHTTPMiddleware` must build a complete Starlette `Response` object to pass into `call_next(request)`. To do so, it intercepts `http.response.body` chunks and buffers them through an internal memory channel, which breaks streaming flow control.",
        "Generative AI streaming responses (LLM token-by-token output), large file downloads, and audio/video streaming.",
        ["What is Time To First Byte (TTFB) and how does `BaseHTTPMiddleware` degrade it?", "What happens if a client disconnects midway through a stream inside `BaseHTTPMiddleware`?"],
        ["Using `@app.middleware('http')` on SSE (Server-Sent Events) or LLM streaming routes, causing tokens to arrive in bursts instead of real time.", "Ignoring memory growth when streaming multi-gigabyte files."],
        "Golden rule: Never use `BaseHTTPMiddleware` or `@app.middleware('http')` on streaming or WebSocket endpoints.",
        ["[Streaming Responses](async-and-concurrency.md)", "[Pure ASGI Middleware](middleware-and-exception-handling.md)"],
        ["https://github.com/encode/starlette/issues/485"]
    ),

    # FA-INT-153
    (
        "FA-INT-153",
        "Writing a High-Performance Pure ASGI 3-Callable Middleware (`app, scope, receive, send`)",
        "A Pure ASGI middleware implements the ASGI 3.0 protocol: an asynchronous callable accepting `scope`, `receive`, and `send` to intercept raw events with maximum throughput.",
        "The ASGI (Asynchronous Server Gateway Interface) standard defines web application communication as a stream of asynchronous dictionaries. A Pure ASGI middleware class stores `self.app` in `__init__`. In its `__call__` method, it receives: 1) `scope`: A dictionary describing connection metadata (type, path, method, headers); 2) `receive`: A coroutine returning incoming messages (e.g. `http.request` with body bytes); 3) `send`: A coroutine dispatched to push outgoing messages (`http.response.start`, `http.response.body`).",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nfrom fastapi import FastAPI\n\nclass TimingASGIMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] != 'http':\n            await self.app(scope, receive, send)\n            return\n\n        async def send_wrapper(message: dict) -> None:\n            if message['type'] == 'http.response.start':\n                headers = list(message.get('headers', []))\n                headers.append((b'x-powered-by', b'fastapi-pure-asgi'))\n                message['headers'] = headers\n            await send(message)\n\n        await self.app(scope, receive, send_wrapper)\n\napp = FastAPI()\napp.add_middleware(TimingASGIMiddleware)",
        "Writing a production-grade Pure ASGI 3-callable middleware wrapping the send channel.",
        "When Uvicorn dispatches an incoming socket event, it invokes `middleware(scope, receive, send)`. The middleware creates a closure `send_wrapper` that wraps `send`. As downstream routers generate response chunks, `send_wrapper` intercepts and forwards them directly to Uvicorn without task allocations.",
        "Ultra-low-latency financial gateways, high-frequency telemetry endpoints, and streaming proxies.",
        ["What dictionary key in `scope` distinguishes HTTP requests from WebSocket connections?", "Why are header names and values in ASGI scopes represented as raw `bytes` rather than `str`?"],
        ["Passing decoded strings instead of raw bytes in ASGI header tuples `(b'name', b'value')`.", "Failing to forward non-HTTP scopes (such as `lifespan` or `websocket`) to the downstream application."],
        "Always check `if scope['type'] != 'http': await self.app(scope, receive, send); return` to avoid intercepting lifespan or WebSocket events incorrectly.",
        ["[ASGI Specification](async-and-concurrency.md)", "[Production Performance](production-and-performance.md)"],
        ["https://asgi.readthedocs.io/en/latest/specs/main.html"]
    ),

    # FA-INT-154
    (
        "FA-INT-154",
        "Correlation ID / Request ID Tracking Across Microservices Using Middleware",
        "A Correlation ID middleware extracts an existing `X-Correlation-ID` from request headers or generates a new UUID, attaching it to request state, logger context, and response headers.",
        "In a microservices architecture, a single user click triggers a cascade of HTTP requests across multiple services. Without a unified Correlation ID (or Request ID), debugging failures across distributed logs is nearly impossible. Middleware extracts `X-Correlation-ID` (or `X-Request-ID`) if supplied by an upstream gateway; if missing, it generates a fresh UUID4. It stores this ID in `request.state.correlation_id` and sets it in outgoing `response.headers`.",
        "import uuid\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def correlation_id_middleware(request: Request, call_next):\n    # Extract from incoming header or generate new UUID\n    correlation_id = request.headers.get('x-correlation-id') or str(uuid.uuid4())\n    \n    # Store in request state for route handlers and logger filters\n    request.state.correlation_id = correlation_id\n    \n    response = await call_next(request)\n    \n    # Echo back to client for distributed tracing\n    response.headers['X-Correlation-ID'] = correlation_id\n    return response\n\n@app.get('/order')\nasync def process_order(request: Request):\n    return {'status': 'processed', 'trace_id': request.state.correlation_id}",
        "Extracting, propagating, and returning a consistent X-Correlation-ID header across requests.",
        "The middleware assigns the identifier at the earliest entrypoint of the ASGI stack. When downstream services make external HTTP calls (via `httpx.AsyncClient`), they propagate this identifier, creating an unbroken trace across all distributed log aggregators (Elasticsearch/Loki).",
        "Enterprise microservice architectures requiring unified log searching across dozens of backend services.",
        ["How do you propagate correlation IDs into asynchronous background worker tasks?", "What is the difference between W3C `traceparent` and `X-Correlation-ID`?"],
        ["Regenerating a new correlation ID when an upstream service already passed an existing valid one.", "Failing to attach the correlation ID to outgoing client error responses."],
        "Emphasize: Always check if the incoming request already has an `X-Correlation-ID` before generating a new one.",
        ["[Contextvars Logging](middleware-and-exception-handling.md)", "[Distributed Tracing](../10-system-design/distributed-systems.md)"],
        ["https://www.w3.org/TR/trace-context/"]
    ),

    # FA-INT-155
    (
        "FA-INT-155",
        "Transforming Exception Payloads to RFC 7807 (Problem Details for HTTP APIs)",
        "RFC 7807 defines a standardized JSON structure (`application/problem+json`) for HTTP API errors, including `type`, `title`, `status`, `detail`, and `instance`.",
        "Custom, proprietary error formats (`{'err': 'msg'}`) force API consumers to write bespoke error parsing for every API. RFC 7807 ('Problem Details for HTTP APIs') standardizes error responses. A compliant error payload contains: `type` (URI reference identifying the problem type), `title` (short human-readable summary), `status` (HTTP status code), `detail` (explanation specific to this occurrence), and `instance` (URI of the specific resource that failed). FastAPI exception handlers can serialize all exceptions into RFC 7807 format.",
        "from fastapi import FastAPI, Request, HTTPException, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n@app.exception_handler(HTTPException)\nasync def rfc7807_exception_handler(request: Request, exc: HTTPException):\n    problem_details = {\n        'type': f'https://api.example.com/errors/http-{exc.status_code}',\n        'title': status.description(exc.status_code) if hasattr(status, 'description') else 'HTTP Error',\n        'status': exc.status_code,\n        'detail': exc.detail,\n        'instance': str(request.url.path),\n    }\n    return JSONResponse(\n        status_code=exc.status_code,\n        content=problem_details,\n        media_type='application/problem+json'\n    )\n\n@app.get('/accounts/{acc_id}')\nasync def get_account(acc_id: int):\n    if acc_id <= 0:\n        raise HTTPException(status_code=400, detail='Account ID must be a positive integer')\n    return {'acc_id': acc_id, 'balance': 1000}",
        "Formatting error responses strictly according to RFC 7807 with application/problem+json media type.",
        "Setting `media_type='application/problem+json'` instructs the client's HTTP library that the error payload adheres to RFC 7807 specifications. Standardized fields allow automated client-side error handling.",
        "Public enterprise APIs, banking and open finance APIs (PSD2), and multi-vendor integrations.",
        ["What are the 5 core members defined in RFC 7807?", "What media type is required for RFC 7807 responses?"],
        ["Returning standard `application/json` instead of `application/problem+json` when claiming RFC 7807 compliance.", "Using non-standard custom field names instead of the RFC-mandated `type`, `title`, and `status` keys."],
        "State clearly: RFC 7807 specifies `application/problem+json` as the Content-Type header.",
        ["[Exception Handlers](middleware-and-exception-handling.md)", "[API Standards](../07-api-engineering/rest-api.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc7807"]
    ),

    # FA-INT-156
    (
        "FA-INT-156",
        "Global Exception Handling vs Endpoint `try/except` Blocks",
        "Global exception handlers centralize error translation and logging at the application boundary, whereas endpoint `try/except` should be reserved for local error recovery.",
        "In naive implementations, developers write repetitive `try/except` blocks inside every route handler, cluttering business logic with HTTP responses and status codes. Clean FastAPI architecture follows the 'fail-fast' principle: 1) Endpoints and services let domain exceptions bubble up naturally; 2) Global exception handlers intercept specific exception types at the ASGI boundary, logging context and converting them to standardized responses; 3) Local `try/except` blocks are used ONLY when the route can meaningfully recover or fallback locally (e.g. attempting an alternative cache if primary read fails).",
        "# Clean Architecture Pattern: Let exceptions bubble to global handlers\nfrom fastapi import FastAPI, Depends\n\napp = FastAPI()\n\nclass UserNotFound(Exception):\n    pass\n\n# Service layer raises pure domain exception\nasync def get_user_service(user_id: int):\n    if user_id != 1:\n        raise UserNotFound(f'User {user_id} not found')\n    return {'id': 1, 'name': 'Alice'}\n\n# Global handler converts domain exception to HTTP response\n@app.exception_handler(UserNotFound)\nasync def handle_user_not_found(request, exc):\n    return JSONResponse(status_code=404, content={'error': str(exc)})\n\n# Route remains clean and readable (ZERO try/except boilerplate)\n@app.get('/users/{user_id}')\nasync def read_user(user_id: int):\n    return await get_user_service(user_id)",
        "Demonstrating clean separation: service raises domain error, global handler converts to 404, route contains zero boilerplate.",
        "Decoupling error rendering from endpoint logic simplifies unit testing. The service function can be tested in isolation by asserting `pytest.raises(UserNotFound)` without mocking HTTP request or response objects.",
        "Standard production pattern for enterprise FastAPI backends adhering to Clean Architecture.",
        ["When is a local `try/except` block appropriate inside a route handler?", "How do global exception handlers improve codebase maintainability?"],
        ["Catching generic `Exception` inside route handlers and returning `HTTPException(500)` manually.", "Duplicate error serialization logic repeated across 50 different router files."],
        "Emphasize: Use local `try/except` for business recovery; use global exception handlers for error serialization.",
        ["[Domain Exceptions](middleware-and-exception-handling.md)", "[Testing FastAPI](testing.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]
    ),

    # FA-INT-157
    (
        "FA-INT-157",
        "Handling Database Exceptions Globally (`IntegrityError`, `OperationalError`)",
        "Global exception handlers catch SQLAlchemy database errors like `IntegrityError` to return HTTP 409 Conflict, and `OperationalError` to return HTTP 503 Service Unavailable.",
        "Directly exposing database errors to users causes 500 crashes and leaks internal SQL queries and table schemas. Registering global exception handlers for SQLAlchemy exceptions solves this centrally: 1) `IntegrityError`: Raised when unique constraints or foreign keys fail; caught to roll back the session and return HTTP 409 Conflict; 2) `OperationalError`: Raised on connection dropouts or database outages; caught to return HTTP 503 Service Unavailable with a `Retry-After: 5` header.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\nfrom sqlalchemy.exc import IntegrityError, OperationalError\n\napp = FastAPI()\n\n@app.exception_handler(IntegrityError)\nasync def handle_db_integrity_error(request: Request, exc: IntegrityError):\n    # Extract constraint details without exposing full raw SQL\n    return JSONResponse(\n        status_code=status.HTTP_409_CONFLICT,\n        content={\n            'error': 'DATA_CONFLICT',\n            'message': 'A resource with these unique attributes already exists.',\n        }\n    )\n\n@app.exception_handler(OperationalError)\nasync def handle_db_operational_error(request: Request, exc: OperationalError):\n    return JSONResponse(\n        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,\n        content={\n            'error': 'DATABASE_UNAVAILABLE',\n            'message': 'Database connection temporarily unavailable; please retry shortly.',\n        },\n        headers={'Retry-After': '5'}\n    )",
        "Centrally translating SQLAlchemy IntegrityError and OperationalError into HTTP 409 and 503 responses.",
        "When a database query raises an exception during an endpoint call, FastAPI's exception middleware intercepts it before it reaches Uvicorn. The session is marked for rollback, and the registered handler constructs the standardized JSON response.",
        "Enterprise CRUD applications protecting internal relational schemas from leaking in error outputs.",
        ["Why shouldn't the raw `exc.orig` database error string be returned directly to the client?", "What HTTP status code is most appropriate for unique constraint collisions?"],
        ["Leaking database column names, primary keys, or raw SQL queries in public API error responses.", "Forgetting to roll back aborted database transactions when catching `IntegrityError`."],
        "Security reminder: Never return raw SQL error strings; return sanitized, domain-specific conflict messages.",
        ["[Database Integration](database-integration.md)", "[API Security](../07-api-engineering/api-security.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/exceptions.html"]
    ),

    # FA-INT-158
    (
        "FA-INT-158",
        "Implementing Sliding-Window Rate Limiting Middleware with Redis",
        "A sliding-window rate limiting middleware tracks request timestamps in a Redis sorted set (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`), rejecting requests that exceed the rate limit with HTTP 429.",
        "Fixed-window rate limiters (e.g. allowing 100 requests per minute) suffer from the 'burst at the boundary' flaw: a client sends 100 requests at 00:59 and another 100 at 01:01, effectively executing 200 requests in 2 seconds. The sliding-window rate limiter uses Redis Sorted Sets (ZSET): 1) Remove timestamps older than `now - window_seconds` via `ZREMRANGEBYSCORE`; 2) Count remaining entries in the window via `ZCARD`; 3) If count >= limit, reject with HTTP 429 Too Many Requests; 4) Otherwise, add current timestamp via `ZADD` and allow the request.",
        "import time\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Simulated async Redis client for sliding window rate limiter\nclass MockRedisRateLimiter:\n    def __init__(self):\n        self.history = {}  # key -> list of timestamps\n    async def is_allowed(self, client_id: str, limit: int = 10, window: int = 60) -> bool:\n        now = time.time()\n        timestamps = self.history.get(client_id, [])\n        # Evict timestamps outside sliding window\n        timestamps = [t for t in timestamps if t > now - window]\n        if len(timestamps) >= limit:\n            return False\n        timestamps.append(now)\n        self.history[client_id] = timestamps\n        return True\n\nlimiter = MockRedisRateLimiter()\n\n@app.middleware('http')\nasync def rate_limit_middleware(request: Request, call_next):\n    client_ip = request.client.host if request.client else '127.0.0.1'\n    if not await limiter.is_allowed(client_ip, limit=5, window=10):\n        return JSONResponse(\n            status_code=status.HTTP_429_TOO_MANY_REQUESTS,\n            content={'error': 'RATE_LIMIT_EXCEEDED', 'message': 'Too many requests; slow down.'},\n            headers={'Retry-After': '10'}\n        )\n    return await call_next(request)",
        "Enforcing sliding-window rate limits in middleware and returning HTTP 429 with Retry-After header.",
        "Redis sorted sets store timestamps as both score and value. Atomically executing the eviction, count, and insertion within a Redis pipeline or Lua script guarantees thread-safe, distributed rate limiting across all FastAPI worker pods.",
        "Public API rate limiting, preventing brute-force login attacks, and protecting expensive downstream AI/payment endpoints.",
        ["Why is the sliding-window algorithm more accurate than the fixed-window algorithm?", "What header should always accompany an HTTP 429 response according to RFC 6585?"],
        ["Using in-memory dictionaries for rate limiting across multiple Uvicorn workers (each worker tracks independent counts).", "Failing to attach the `Retry-After` header when returning HTTP 429."],
        "Always include `Retry-After` on 429 responses to inform clients when they can safely resume requests.",
        ["[Redis Caching](../06-redis-and-messaging/redis.md)", "[Rate Limiting Architecture](../10-system-design/fundamentals.md)"],
        ["https://redis.io/docs/manual/patterns/rate-limiter/"]
    ),

    # FA-INT-159
    (
        "FA-INT-159",
        "IP Blacklisting and CIDR Subnet Blocking in ASGI Middleware",
        "IP filtering middleware inspects client IP addresses against blacklists or CIDR subnets (using Python's `ipaddress` module), immediately rejecting malicious traffic with HTTP 403.",
        "When security systems detect brute-force attacks, credential stuffing, or vulnerability scanners, malicious IPs must be rejected before any database or routing overhead occurs. Using Python's built-in `ipaddress.ip_network()`, middleware verifies whether `request.client.host` belongs to any blocked CIDR range (e.g. `198.51.100.0/24`). Blocked requests are terminated immediately with an HTTP 403 Forbidden.",
        "import ipaddress\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Configure blocked CIDR subnets\nBLOCKED_NETWORKS = [\n    ipaddress.ip_network('192.0.2.0/24'),\n    ipaddress.ip_network('203.0.113.50/32'),\n]\n\n@app.middleware('http')\nasync def ip_firewall_middleware(request: Request, call_next):\n    client_ip_str = request.client.host if request.client else '127.0.0.1'\n    try:\n        client_ip = ipaddress.ip_address(client_ip_str)\n        for network in BLOCKED_NETWORKS:\n            if client_ip in network:\n                return JSONResponse(\n                    status_code=status.HTTP_403_FORBIDDEN,\n                    content={'error': 'IP_BLOCKED', 'message': 'Access from this IP range is forbidden'}\n                )\n    except ValueError:\n        pass\n        \n    return await call_next(request)\n\n@app.get('/public')\nasync def public_endpoint():\n    return {'status': 'accessible'}",
        "Evaluating client IP against blocked CIDR networks using Python's ipaddress module in middleware.",
        "The evaluation happens at the outermost layer of the application. By dropping the request before running routing or dependency injection, server memory and CPU cycles are protected from denial-of-service degradation.",
        "WAF-adjacent application defense, blocking malicious scrapers, and enforcing geo-fenced IP restrictions.",
        ["Why is `ipaddress.ip_network` preferred over raw string comparisons for IP blocking?", "What header must be parsed if the FastAPI application is behind a reverse proxy?"],
        ["Parsing client IP without catching `ValueError` if the proxy forwards an invalid IP string.", "Doing sequential linear scans across 100,000 blocked IPs in Python (large blacklists belong in Redis or edge firewalls)."],
        "Tip: Large IP blacklists (> 1000 subnets) should be enforced at the Cloudflare/AWS WAF edge, not in Python middleware.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Nginx Security](../11-devops/nginx.md)"],
        ["https://docs.python.org/3/library/ipaddress.html"]
    ),

    # FA-INT-160
    (
        "FA-INT-160",
        "Inspecting and Replaying Request Bodies in Middleware Without Breaking Routes",
        "Because ASGI request body streams can only be read once, middleware that inspects the request body must buffer the bytes and construct a replacement `receive` callable to allow downstream routes to read it.",
        "In ASGI, the request body is an asynchronous stream consumed via `await receive()`. Once read, the stream is exhausted. If middleware calls `await request.body()` to log payloads or verify HMAC signatures, subsequent route handlers calling Pydantic validation will receive an empty body and fail with a validation error. To inspect request bodies safely, middleware reads the raw bytes and replaces `receive` with an asynchronous generator that replays those cached bytes.",
        "from fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def inspect_and_replay_body(request: Request, call_next):\n    # 1. Read and cache raw body bytes\n    body_bytes = await request.body()\n    \n    # 2. Inspect or log payload (e.g. verify HMAC signature)\n    print(f'Inspected payload length: {len(body_bytes)} bytes')\n    \n    # 3. Construct a replayable receive coroutine for downstream handlers\n    async def replayed_receive():\n        return {\n            'type': 'http.request',\n            'body': body_bytes,\n            'more_body': False\n        }\n    \n    # 4. Create new Request object with replayed receive and forward\n    request = Request(request.scope, replayed_receive)\n    return await call_next(request)\n\n@app.post('/webhook')\nasync def webhook(data: dict):\n    return {'received': data}",
        "Buffering the raw request body and constructing a replayed receive callable to preserve downstream parsing.",
        "ASGI applications communicate via the `receive` channel. Replacing `request._receive` or instantiating a new `Request` with a mock receive coroutine satisfies downstream Pydantic body parsers as if the stream was untouched.",
        "Webhook cryptographic signature verification (Stripe, GitHub), request HMAC validation, and audit logging of request payloads.",
        ["Why can an ASGI request body stream only be read once by default?", "What are the memory risks of buffering request bodies for large file uploads?"],
        ["Reading `await request.body()` without replaying it, causing all downstream POST/PUT routes to fail with validation errors.", "Buffering multi-gigabyte file upload streams into memory, triggering container OOM crashes."],
        "Caution: Never buffer request bodies on file upload endpoints; check `request.headers.get('content-type')` before buffering.",
        ["[Pure ASGI Middleware](middleware-and-exception-handling.md)", "[File Uploads](routing-and-dependencies.md)"],
        ["https://www.starlette.io/requests/#request-body"]
    ),

    # FA-INT-161
    (
        "FA-INT-161",
        "Sanitizing Request Headers and Stripping Dangerous Forwarded Headers",
        "Security middleware strips spoofed proxy headers like `X-Forwarded-Host` or `X-Forwarded-For` from requests when the immediate client is not a trusted reverse proxy.",
        "Attackers can send arbitrary spoofed headers (e.g. `X-Forwarded-For: 8.8.8.8` or `X-Forwarded-Proto: https`) directly to an application server. If the application trusts these headers blindly without verifying that the request originated from an authorized internal proxy (like Nginx or AWS ALB), security controls (like IP rate limiting and HTTPS redirects) are bypassed. Middleware sanitizes incoming headers by verifying `request.client.host` against a list of trusted proxy CIDRs before reading forwarded headers.",
        "from fastapi import FastAPI, Request\nfrom starlette.datastructures import Headers\n\napp = FastAPI()\nTRUSTED_PROXIES = {'10.0.0.1', '127.0.0.1'}\n\n@app.middleware('http')\nasync def sanitize_proxy_headers(request: Request, call_next):\n    client_ip = request.client.host if request.client else None\n    \n    # If the request did NOT come from our trusted proxy, strip dangerous forwarded headers\n    if client_ip not in TRUSTED_PROXIES:\n        # Clean raw headers in ASGI scope\n        cleaned_headers = [\n            (name, val) for name, val in request.scope['headers']\n            if name.lower() not in (b'x-forwarded-for', b'x-forwarded-proto', b'x-forwarded-host')\n        ]\n        request.scope['headers'] = cleaned_headers\n        \n    return await call_next(request)\n\n@app.get('/verify')\nasync def verify_headers(request: Request):\n    return {'client_ip': request.client.host}",
        "Sanitizing untrusted X-Forwarded headers from incoming ASGI request scope.",
        "Modifying `request.scope['headers']` mutates the underlying ASGI header tuples. When downstream code calls `request.headers.get('x-forwarded-for')`, the spoofed headers have been removed, preventing IP spoofing.",
        "Zero-trust environments and services exposed directly to public internet traffic without managed perimeter proxies.",
        ["What is IP Spoofing via `X-Forwarded-For`?", "Why should reverse proxies overwrite rather than append to client-supplied `X-Forwarded-Host` headers?"],
        ["Trusting `X-Forwarded-For` unconditionally in code without checking whether the TCP peer is a trusted proxy.", "Stripping headers using string lookups without accounting for case-insensitivity in HTTP headers."],
        "Remember: Either strip forwarded headers in Python middleware or configure Nginx/ALB to overwrite them at the perimeter.",
        ["[Nginx Proxy Configuration](../11-devops/nginx.md)", "[API Security](../07-api-engineering/api-security.md)"],
        ["https://en.wikipedia.org/wiki/X-Forwarded-For"]
    ),

    # FA-INT-162
    (
        "FA-INT-162",
        "Catching Unhandled Background Task Exceptions vs Route Exceptions",
        "Exceptions raised inside `BackgroundTasks` execute after the HTTP response has completed and cannot be caught by standard route `try/except` or HTTP exception handlers.",
        "FastAPI's `BackgroundTasks` runs coroutines *after* the HTTP response has already been sent over the wire. Consequently, if a background task raises an exception: 1) The client already received HTTP 200 OK; 2) Route `try/except` blocks cannot catch it; 3) Standard HTTP exception handlers cannot alter the response. Background task exceptions must be handled with internal `try/except` blocks inside the task function itself, logging errors directly to monitoring systems (Sentry).",
        "import logging\nfrom fastapi import FastAPI, BackgroundTasks\n\nlogger = logging.getLogger('background')\napp = FastAPI()\n\n# SAFE Background task: Handles its OWN errors internally\nasync def safe_background_worker(recipient_email: str):\n    try:\n        # Simulate email sending or processing\n        if recipient_email == 'fail@test.com':\n            raise ValueError('SMTP server connection failed')\n        logger.info(f'Email sent to {recipient_email}')\n    except Exception as exc:\n        # Log error to Sentry/APM directly; client response is already gone!\n        logger.error(f'Background task failed for {recipient_email}: {exc}', exc_info=True)\n\n@app.post('/notify')\nasync def trigger_notification(email: str, bg: BackgroundTasks):\n    bg.add_task(safe_background_worker, email)\n    return {'status': 'notification_queued'}",
        "Wrapping background task logic in internal try/except to capture and log errors safely.",
        "Starlette executes background tasks in an `anyio.create_task_group()` context after sending the final HTTP response packet. If an exception escapes the task, Starlette catches it and prints a traceback to stderr, but cannot notify the client.",
        "Email dispatch, report generation, analytics aggregation, and webhook deliveries.",
        ["Why can't an HTTP exception handler catch an exception raised in a `BackgroundTask`?", "What happens to a background task if the server process terminates abruptly?"],
        ["Assuming raising `HTTPException` inside a background task will send an error response to the user.", "Leaving background tasks without error handling, resulting in silent failures where un-alerted tasks fail."],
        "Emphasize: Always place `try/except` logging inside background task functions; the HTTP response is already closed.",
        ["[Background Tasks](async-and-concurrency.md)", "[Celery Integration](../06-redis-and-messaging/celery.md)"],
        ["https://fastapi.tiangolo.com/tutorial/background-tasks/"]
    ),

    # FA-INT-163
    (
        "FA-INT-163",
        "Middleware Error Handling: What Happens When Middleware Raises an Uncaught Exception?",
        "When an uncaught exception occurs inside middleware, Starlette's `ServerErrorMiddleware` intercepts it, logs the error, and returns a generic 500 Internal Server Error.",
        "If middleware crashes (e.g. uncaught database dropout in logging middleware, or `KeyError` reading state): 1) The exception escapes the user middleware stack; 2) It is caught by Starlette's outermost `ServerErrorMiddleware`; 3) In production (`debug=False`), it returns a plaintext `Internal Server Error` (status 500); 4) In local development (`debug=True`), it displays an HTML debug traceback. To prevent raw 500 plaintext responses, developers should wrap custom middleware logic in defensive `try/except` blocks.",
        "from fastapi import FastAPI, Request\nfrom fastapi.responses import JSONResponse\nimport logging\n\nlogger = logging.getLogger('middleware')\napp = FastAPI()\n\n@app.middleware('http')\nasync def resilient_middleware(request: Request, call_next):\n    try:\n        # Critical pre-processing logic\n        return await call_next(request)\n    except Exception as exc:\n        logger.error(f'Middleware captured fatal error: {exc}', exc_info=True)\n        # Return structured JSON 500 instead of allowing Starlette to return plain text\n        return JSONResponse(\n            status_code=500,\n            content={'error': 'MIDDLEWARE_FAILURE', 'message': 'An internal processing error occurred'}\n        )",
        "Defensively catching uncaught exceptions inside middleware to return consistent JSON error envelopes.",
        "`ServerErrorMiddleware` sits at the top of the ASGI chain. If an unhandled exception escapes through all middleware without being handled, `ServerErrorMiddleware` renders the default 500 response.",
        "Mission-critical APIs where all responses must adhere to strict JSON schemas, even during fatal middleware crashes.",
        ["What is Starlette's `ServerErrorMiddleware`?", "Why should middleware catch exceptions and return `JSONResponse` rather than letting them bubble up?"],
        ["Allowing middleware crashes to return plaintext `Internal Server Error`, breaking frontend mobile app JSON parsers.", "Swallowing exceptions without logging them, hiding fatal bugs from observability dashboards."],
        "Catch unexpected middleware errors and return structured `JSONResponse(status_code=500)` to preserve API contracts.",
        ["[Global Exception Handlers](middleware-and-exception-handling.md)", "[Production Monitoring](production-and-performance.md)"],
        ["https://www.starlette.io/exceptions/"]
    ),

    # FA-INT-164
    (
        "FA-INT-164",
        "Enforcing Content-Security-Policy (CSP) and HSTS Security Headers in Middleware",
        "Security middleware injects defense-in-depth HTTP response headers like `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, and `X-Frame-Options`.",
        "To protect clients against cross-site scripting (XSS), clickjacking, MIME-type sniffing, and SSL stripping, security standards (OWASP, Mozilla Observatory) mandate strict HTTP response headers. Middleware appends these headers to every outgoing response: 1) `Strict-Transport-Security (HSTS)`: Forces browsers to use HTTPS for future requests; 2) `Content-Security-Policy (CSP)`: Restricts origins of executable scripts; 3) `X-Content-Type-Options: nosniff`: Prevents MIME confusion; 4) `X-Frame-Options: DENY`: Prevents embedding in iframes.",
        "from fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def security_headers_middleware(request: Request, call_next) -> Response:\n    response: Response = await call_next(request)\n    \n    # Enforce OWASP Recommended Security Headers\n    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'\n    response.headers['Content-Security-Policy'] = \"default-src 'self'; frame-ancestors 'none';\"\n    response.headers['X-Content-Type-Options'] = 'nosniff'\n    response.headers['X-Frame-Options'] = 'DENY'\n    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'\n    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'\n    \n    return response\n\n@app.get('/health')\nasync def health():\n    return {'status': 'healthy'}",
        "Injecting OWASP recommended security headers onto all outgoing API responses.",
        "Modern browsers inspect these response headers before parsing payloads or rendering assets, disabling risky browser behaviors like running unauthorized external scripts or displaying pages in unauthorized frames.",
        "Compliance with security audits (SOC 2, ISO 27001, PCI-DSS) and hardening web applications against common web vulnerabilities.",
        ["What does the `preload` directive in HSTS do?", "How does `X-Frame-Options: DENY` protect against clickjacking?"],
        ["Configuring overly restrictive CSP policies that break legitimate Swagger UI (`/docs`) script assets.", "Omitting `includeSubDomains` from HSTS, leaving subdomains vulnerable to SSL stripping."],
        "Tip: If Swagger UI `/docs` breaks after adding CSP, whitelist `'unsafe-inline'` or CDN domains specifically for documentation routes.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://owasp.org/www-project-secure-headers/"]
    ),

    # FA-INT-165
    (
        "FA-INT-165",
        "Integrating OpenTelemetry Distributed Tracing and Spans in FastAPI Middleware",
        "OpenTelemetry middleware instruments FastAPI to generate distributed trace spans, propagating W3C `traceparent` headers across microservices for end-to-end observability.",
        "In modern cloud-native architectures, diagnosing latency requires distributed tracing. OpenTelemetry provides standard instrumentation for FastAPI (`opentelemetry-instrumentation-fastapi`). The middleware intercepts incoming requests, extracts the W3C `traceparent` header to join existing traces, starts a root server span, records HTTP attributes (`http.method`, `http.status_code`, `http.route`), and exports span metrics to Jaeger, Zipkin, or OpenTelemetry Collector.",
        "# Conceptual OpenTelemetry Integration in FastAPI:\n# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor\n# from opentelemetry import trace\n# from opentelemetry.sdk.trace import TracerProvider\n#\n# tracer_provider = TracerProvider()\n# trace.set_tracer_provider(tracer_provider)\n#\n# app = FastAPI()\n#\n# # Automatically instruments all route handlers with OpenTelemetry spans\n# FastAPIInstrumentor.instrument_app(app)",
        "Instrumenting FastAPI application with OpenTelemetry distributed tracing using FastAPIInstrumentor.",
        "The instrumentor hooks into Starlette's ASGI lifecycle. Each request generates a unique span ID and links to the parent trace ID. As the request interacts with databases, Redis, or external APIs, child spans are recorded and visualized in distributed flamegraphs.",
        "Microservices tracing across Kubernetes clusters running Jaeger or Datadog APM.",
        ["What is the structure of a W3C `traceparent` header?", "What is the performance overhead of OpenTelemetry tracing in production?"],
        ["Sampling 100% of traces in high-traffic production environments (use probabilistic sampling like 1-5% to avoid network bottlenecks).", "Failing to propagate trace headers when calling downstream microservices via HTTP clients."],
        "Always use trace sampling (e.g. 5%) in high-throughput production to balance observability with CPU and network overhead.",
        ["[Distributed Tracing](../10-system-design/distributed-systems.md)", "[Production Monitoring](production-and-performance.md)"],
        ["https://opentelemetry.io/docs/languages/python/"]
    ),

    # FA-INT-166
    (
        "FA-INT-166",
        "Handling Client Disconnects (`http.disconnect`) During Middleware Processing",
        "Client disconnect events (`http.disconnect`) occur when a client aborts an HTTP connection, requiring middleware to cancel in-flight queries and release resources.",
        "In slow-loading queries or large file downloads, users frequently navigate away or close the browser tab. The client sends a TCP RST/FIN packet, causing Uvicorn to emit an `http.disconnect` ASGI event. If middleware or route handlers do not monitor this event, they continue executing expensive database queries and computations for a response that will never be received. Async route handlers can monitor `await request.is_disconnected()` to abort early.",
        "import asyncio\nfrom fastapi import FastAPI, Request\nimport logging\n\nlogger = logging.getLogger('disconnect')\napp = FastAPI()\n\n@app.get('/heavy-computation')\nasync def heavy_computation(request: Request):\n    for step in range(10):\n        # Check if the client disconnected before proceeding with each batch\n        if await request.is_disconnected():\n            logger.warning('Client disconnected! Aborting further database computation.')\n            return {'status': 'aborted'}\n            \n        await asyncio.sleep(0.5)  # Simulate expensive chunk processing\n        \n    return {'status': 'completed'}",
        "Checking request.is_disconnected() periodically during expensive operations to cancel processing on client disconnect.",
        "`request.is_disconnected()` listens for an `http.disconnect` event on the ASGI `receive` channel. When detected, the coroutine can terminate early, freeing database connections and CPU cycles.",
        "Costly AI model inference, large report generation, and video transcoding endpoints.",
        ["What happens if an endpoint keeps running after a client disconnects?", "How does `anyio` handle cancellation when a client aborts an ASGI connection?"],
        ["Ignoring client disconnects during heavy multi-second processing, wasting expensive cloud compute resources.", "Performing non-cancellable blocking operations in threadpools that ignore event loop cancellations."],
        "Tip: Check `await request.is_disconnected()` in long-running loops to save server CPU and database resources.",
        ["[Async Concurrency](async-and-concurrency.md)", "[Production Optimization](production-and-performance.md)"],
        ["https://www.starlette.io/requests/#disconnected-state"]
    ),

    # FA-INT-167
    (
        "FA-INT-167",
        "Dynamic CORS Policy per Tenant or Subdomain",
        "Dynamic CORS middleware verifies incoming `Origin` headers against dynamic database or regex patterns, returning personalized CORS headers per tenant.",
        "Standard static `CORSMiddleware` requires a hardcoded list of allowed origins. In multi-tenant SaaS platforms where enterprise customers use custom domains (e.g. `tenant1.com`, `tenant2.customdomain.org`), the allowed origin list cannot be hardcoded. Custom CORS middleware intercepts the `Origin` header, inspects a database or Redis cache to verify if that domain is a registered tenant, and dynamically issues `Access-Control-Allow-Origin: <origin>`.",
        "from fastapi import FastAPI, Request, Response, status\n\napp = FastAPI()\n\n# Simulated tenant domain whitelist check\nasync def is_valid_tenant_origin(origin: str) -> bool:\n    allowed_domains = {'https://alpha.example.com', 'https://beta.example.com'}\n    return origin in allowed_domains or origin.endswith('.internal.net')\n\n@app.middleware('http')\nasync def dynamic_cors_middleware(request: Request, call_next):\n    origin = request.headers.get('origin')\n    \n    # Handle Preflight OPTIONS request dynamically\n    if request.method == 'OPTIONS' and origin:\n        if await is_valid_tenant_origin(origin):\n            return Response(\n                status_code=status.HTTP_200_OK,\n                headers={\n                    'Access-Control-Allow-Origin': origin,\n                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',\n                    'Access-Control-Allow-Headers': 'Authorization, Content-Type',\n                    'Access-Control-Allow-Credentials': 'true',\n                }\n            )\n            \n    response = await call_next(request)\n    if origin and await is_valid_tenant_origin(origin):\n        response.headers['Access-Control-Allow-Origin'] = origin\n        response.headers['Access-Control-Allow-Credentials'] = 'true'\n    return response",
        "Dynamic tenant-based CORS verification and preflight response generation in middleware.",
        "The middleware evaluates the `Origin` header dynamically. If the origin belongs to a verified tenant, the exact matching origin is returned in `Access-Control-Allow-Origin`, allowing credentials like cookies to work seamlessly without wildcards.",
        "Multi-tenant SaaS platforms supporting white-label custom client domains.",
        ["Why doesn't `CORSMiddleware` support dynamic database-driven origin lookups out of the box?", "Why can't `Access-Control-Allow-Origin: *` be used with `Access-Control-Allow-Credentials: true`?"],
        ["Caching preflight responses without considering tenant revocation.", "Reflecting any arbitrary `Origin` header back without validation (creates a severe cross-origin security vulnerability)."],
        "Warning: Never echo the `Origin` header back blindly; ALWAYS validate against a database whitelist or strict regex.",
        ["[CORS Configuration](middleware-and-exception-handling.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"]
    ),

    # FA-INT-168
    (
        "FA-INT-168",
        "Decompressing Gzip and Brotli Request Bodies in Middleware",
        "Request decompression middleware checks `Content-Encoding: gzip`, decompresses incoming compressed request payloads, and replaces the body stream for downstream route handlers.",
        "While response compression is common, mobile and IoT clients frequently send compressed *request* bodies (e.g. uploading large JSON telemetry batches) to minimize upload bandwidth. Because standard ASGI servers do not decompress request bodies automatically, custom middleware inspects `request.headers.get('content-encoding')`. If it is `gzip`, the middleware reads the compressed bytes, decompresses them using Python's `gzip.decompress()`, and updates the ASGI `receive` stream with the plaintext bytes.",
        "import gzip\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def decompress_request_body_middleware(request: Request, call_next):\n    encoding = request.headers.get('content-encoding', '').lower()\n    \n    if encoding == 'gzip':\n        raw_body = await request.body()\n        # Decompress gzip payload\n        decompressed_body = gzip.decompress(raw_body)\n        \n        async def decompressed_receive():\n            return {'type': 'http.request', 'body': decompressed_body, 'more_body': False}\n            \n        # Reconstruct request with decompressed receive\n        request = Request(request.scope, decompressed_receive)\n        \n    return await call_next(request)\n\n@app.post('/telemetry')\nasync def receive_telemetry(payload: dict):\n    return {'status': 'processed', 'keys': list(payload.keys())}",
        "Decompressing gzip-encoded incoming request payloads before Pydantic route parsing.",
        "The middleware intercepts the raw compressed byte stream, executes `gzip.decompress()`, and substitutes the decompressed bytes into the ASGI `receive` callable, allowing Pydantic validation to parse standard JSON.",
        "IoT sensor data uploads, mobile crash reporting SDKs, and high-volume telemetry ingestion pipelines.",
        ["What is a Zip Bomb attack and how do you protect decompression middleware against it?", "What other content encodings exist besides gzip (e.g. br, deflate)?"],
        ["Decompressing unbounded input streams without a maximum byte limit, making the server vulnerable to Zip Bomb denial-of-service attacks.", "Forgetting to update or remove the `Content-Encoding` header after decompression."],
        "Security essential: Always enforce a strict decompressed byte size limit (e.g. 10MB) to prevent Zip Bomb attacks.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Performance Optimization](../01-python/internals-and-performance.md)"],
        ["https://en.wikipedia.org/wiki/Zip_bomb"]
    ),

    # FA-INT-169
    (
        "FA-INT-169",
        "Custom Response Caching Middleware Using ETag and `If-None-Match` (HTTP 304)",
        "ETag caching middleware computes cryptographic hashes of response bodies; if the incoming `If-None-Match` header matches, it returns an empty HTTP 304 Not Modified response.",
        "Transferring unchanged data wastes client and server bandwidth. An ETag (Entity Tag) is an HTTP validator header containing a hash (e.g. MD5 or SHA-256) of the response body. When a client makes a subsequent request, it sends `If-None-Match: \"<etag>\"`. The middleware computes the response hash. If they match, the middleware discards the body and returns `304 Not Modified`, instructing the client browser to reuse its local cached copy.",
        "import hashlib\nfrom fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def etag_caching_middleware(request: Request, call_next):\n    response = await call_next(request)\n    \n    # Only apply to successful GET requests\n    if request.method == 'GET' and response.status_code == 200:\n        # Read response body from Starlette response\n        body = b''.join([chunk async for chunk in response.body_iterator])\n        etag = f'\"{hashlib.md5(body).hexdigest()}\"'\n        \n        # Check client cache validator\n        if request.headers.get('if-none-match') == etag:\n            return Response(status_code=304, headers={'ETag': etag})\n            \n        # Return full response with ETag header\n        return Response(content=body, status_code=200, headers=dict(response.headers) | {'ETag': etag})\n        \n    return response\n\n@app.get('/catalog')\nasync def get_catalog():\n    return {'items': ['Laptop', 'Monitor', 'Desk']}",
        "Implementing ETag computation and HTTP 304 Not Modified response evaluation in middleware.",
        "Returning HTTP 304 avoids transmitting data over the network. The client browser immediately renders the cached asset, reducing network transit time to near-zero.",
        "Static asset serving, product catalogs, user settings, and documentation endpoints.",
        ["What is the difference between a Strong ETag and a Weak ETag?", "Why is returning HTTP 304 beneficial for mobile network clients?"],
        ["Consuming `response.body_iterator` without reconstructing the response body, resulting in empty responses.", "Applying ETag caching to POST or PUT mutating endpoints."],
        "Emphasize: ETag validation saves bandwidth, but still requires the server to generate the response; pair with Redis for true database offloading.",
        ["[HTTP & HTTPS](../07-api-engineering/http-and-https.md)", "[Redis Caching](../06-redis-and-messaging/redis.md)"],
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag"]
    ),

    # FA-INT-170
    (
        "FA-INT-170",
        "Masking Sensitive PII Data in Request Logs via Middleware Filters",
        "Logging middleware must scrub Personally Identifiable Information (PII) such as passwords, credit card numbers, and SSNs from request bodies and headers before writing to logs.",
        "Compliance regulations (GDPR, PCI-DSS, HIPAA) strictly forbid logging plaintext credentials, card numbers, or social security numbers. In middleware that logs request payloads or query parameters, a PII sanitizer recursively traverses dictionaries or applies regular expressions to mask sensitive keys (`password`, `token`, `cvv`, `ssn`) with `***REDACTED***` before sending log entries to aggregators.",
        "import re\nimport json\nfrom fastapi import FastAPI, Request\nimport logging\n\nlogger = logging.getLogger('audit')\napp = FastAPI()\n\nSENSITIVE_KEYS = {'password', 'token', 'secret', 'credit_card', 'cvv'}\n\ndef redact_sensitive_data(data: dict) -> dict:\n    clean = {}\n    for k, v in data.items():\n        if k.lower() in SENSITIVE_KEYS:\n            clean[k] = '***REDACTED***'\n        elif isinstance(v, dict):\n            clean[k] = redact_sensitive_data(v)\n        else:\n            clean[k] = v\n    return clean\n\n@app.middleware('http')\nasync def pii_scrubbing_log_middleware(request: Request, call_next):\n    if request.method in ('POST', 'PUT'):\n        try:\n            body_bytes = await request.body()\n            if body_bytes:\n                payload = json.loads(body_bytes)\n                scrubbed = redact_sensitive_data(payload)\n                logger.info(f'Request body: {scrubbed}')\n        except Exception:\n            pass\n    return await call_next(request)",
        "Scrubbing sensitive credentials and PII data from request payloads prior to logging.",
        "The sanitizer intercepts the data structure in memory. By recursively inspecting key names against a redaction set, passwords and payment tokens are replaced with masked strings before log formatting occurs.",
        "Financial applications, healthcare portals, and SOC 2 / PCI-DSS compliance audits.",
        ["What are the consequences of logging plaintext credit card numbers under PCI-DSS?", "How do you redact sensitive Authorization Bearer tokens from request header logs?"],
        ["Logging raw request query strings without redacting tokens passed in URLs (e.g. `?token=secret`).", "Logging un-scrubbed JSON request bodies during user login or registration flows."],
        "Golden rule: Never log request bodies without a PII redaction filter in place.",
        ["[Security Compliance](../12-security/application-security.md)", "[Logging Middleware](middleware-and-exception-handling.md)"],
        ["https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"]
    ),

    # FA-INT-171
    (
        "FA-INT-171",
        "Context-Aware Logging Using Python's `contextvars` Populated by Middleware",
        "Python's `contextvars` module provides asynchronous context-local storage, allowing middleware to set request IDs that are automatically injected into all log statements throughout the call stack.",
        "In multithreaded synchronous code, `threading.local()` stores thread-scoped state. In asynchronous code, multiple concurrent requests execute on the same thread, making `threading.local()` corrupt across coroutines. Python 3.7+ introduced `contextvars`. Middleware sets `request_id_var.set(correlation_id)`. Custom logging filters read from `request_id_var.get()`, ensuring every log message output by database services or background workers includes the active request ID without explicitly passing it through function arguments.",
        "import contextvars\nimport logging\nimport uuid\nfrom fastapi import FastAPI, Request\n\n# Asynchronous context variable\ncorrelation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='system')\n\n# Custom logging filter injecting contextvar into log records\nclass CorrelationFilter(logging.Filter):\n    def filter(self, record):\n        record.correlation_id = correlation_id_ctx.get()\n        return True\n\nlogger = logging.getLogger('service')\nhandler = logging.StreamHandler()\nhandler.setFormatter(logging.Formatter('[%(correlation_id)s] %(levelname)s: %(message)s'))\nhandler.addFilter(CorrelationFilter())\nlogger.addHandler(handler)\nlogger.setLevel(logging.INFO)\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def contextvar_middleware(request: Request, call_next):\n    cid = request.headers.get('x-correlation-id', str(uuid.uuid4()))\n    token = correlation_id_ctx.set(cid)  # Set for current async task context\n    try:\n        return await call_next(request)\n    finally:\n        correlation_id_ctx.reset(token)  # Clean up context\n\n@app.get('/do-work')\nasync def do_work():\n    logger.info('Processing business logic')  # Log automatically includes [correlation_id]!\n    return {'status': 'done'}",
        "Managing asynchronous request context using contextvars and automatic log record injection.",
        "`contextvars` copies execution context across coroutine invocations. When `await` suspends a coroutine, the event loop preserves the context, ensuring that log messages emitted deep inside database repositories reference the correct request ID.",
        "Production backend logging pipelines integrating with Datadog, ELK, or CloudWatch.",
        ["Why does `threading.local()` fail in asynchronous FastAPI applications?", "What is the purpose of `correlation_id_ctx.reset(token)` in the finally block?"],
        ["Using `threading.local()` in async coroutines, causing logs to display random correlation IDs from concurrent requests.", "Forgetting to reset context tokens, leading to memory leaks across long-lived event loop tasks."],
        "Emphasize: In async Python, ALWAYS use `contextvars`, NEVER use `threading.local()`.",
        ["[Python Concurrency](../01-python/concurrency-and-parallelism.md)", "[Correlation IDs](middleware-and-exception-handling.md)"],
        ["https://docs.python.org/3/library/contextvars.html"]
    ),

    # FA-INT-172
    (
        "FA-INT-172",
        "Overriding Starlette's Default `ServerErrorMiddleware`",
        "Starlette's `ServerErrorMiddleware` handles uncaught exceptions at the root of the ASGI stack, customizable to render uniform JSON payloads on fatal server crashes.",
        "When an exception is raised that escapes all route handlers and user middleware, it hits Starlette's root `ServerErrorMiddleware`. By default, it returns a plaintext `Internal Server Error` string. To ensure that fatal crashes (such as unexpected database driver faults or OS signal terminations) return valid JSON matching your API schema, you can configure a custom 500 handler when instantiating `FastAPI` or override the `ServerErrorMiddleware` handler.",
        "from fastapi import FastAPI, Request\nfrom fastapi.responses import JSONResponse\n\n# Custom 500 handler for root ServerErrorMiddleware\nasync def custom_500_handler(request: Request, exc: Exception) -> JSONResponse:\n    return JSONResponse(\n        status_code=500,\n        content={\n            'status': 'fatal_error',\n            'error_code': 'INTERNAL_SERVER_ERROR',\n            'message': 'A critical system error occurred. Operations team notified.'\n        }\n    )\n\n# Attach custom 500 handler directly to FastAPI app initialization\napp = FastAPI(exception_handlers={500: custom_500_handler})\n\n@app.get('/unhandled-crash')\nasync def crash():\n    raise SystemError('Unexpected kernel/driver failure')",
        "Registering a custom 500 handler on FastAPI initialization to override root ServerErrorMiddleware.",
        "FastAPI passes the dictionary of `exception_handlers` to Starlette's internal routing and middleware setup. Status code `500` is mapped directly to `ServerErrorMiddleware`, replacing the default plaintext responder.",
        "SLA-critical enterprise APIs where every HTTP response must conform to JSON API specifications.",
        ["Where does `ServerErrorMiddleware` sit relative to user-added middleware in the ASGI chain?", "What is the difference between `@app.exception_handler(Exception)` and `exception_handlers={500: ...}`?"],
        ["Assuming `@app.exception_handler(Exception)` catches errors raised inside user middleware (it only catches errors inside routes; ServerErrorMiddleware catches middleware errors).", "Returning non-serializable objects from custom 500 error handlers."],
        "Key insight: `@app.exception_handler(Exception)` catches route errors; `ServerErrorMiddleware` catches errors that escape all middleware.",
        ["[ASGI Architecture](middleware-and-exception-handling.md)", "[Exception Handling](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/exceptions/#servererrormiddleware"]
    ),

    # FA-INT-173
    (
        "FA-INT-173",
        "Handling WebSocket Exceptions vs HTTP Exceptions",
        "WebSocket exceptions cannot use `HTTPException` because WebSockets operate over bidirectional framed protocols, requiring explicit closure codes (`WebSocketDisconnect`, `code=1008`).",
        "Unlike HTTP's request-response lifecycle, WebSockets maintain a persistent, bidirectional TCP connection. Raising an `HTTPException(404)` inside an active WebSocket route will not work as expected because HTTP status codes do not apply after the WebSocket handshake. If an error occurs (such as token expiration or permission denial), the server must close the socket using standard RFC 6455 WebSocket close codes (e.g. `1008 Policy Violation`, `1000 Normal Closure`, `1011 Internal Error`) via `await websocket.close(code=1008)`.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status\n\napp = FastAPI()\n\n@app.websocket('/ws/chat')\nasync def chat_socket(websocket: WebSocket):\n    await websocket.accept()\n    token = websocket.query_params.get('token')\n    \n    # WebSocket authorization validation\n    if token != 'valid_secret':\n        # Close with standard RFC 6455 policy violation close code\n        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='Invalid authentication token')\n        return\n        \n    try:\n        while True:\n            msg = await websocket.receive_text()\n            await websocket.send_text(f'Echo: {msg}')\n    except WebSocketDisconnect:\n        print('Client disconnected normally')",
        "Closing WebSocket connections cleanly with RFC 6455 close codes rather than raising HTTPException.",
        "The server dispatches a WebSocket Close frame containing a 2-byte unsigned integer code and optional UTF-8 reason string. The client's WebSocket implementation receives the close frame and triggers `onclose` with the code.",
        "Real-time chat services, stock trading dashboards, and multiplayer gaming backends.",
        ["What are the standard WebSocket close codes (1000 Normal, 1008 Policy Violation, 1011 Server Error)?", "Can an HTTP middleware intercept WebSocket messages after the handshake?"],
        ["Raising `HTTPException` inside a WebSocket loop after the connection has been accepted.", "Not catching `WebSocketDisconnect`, resulting in unhandled exception tracebacks in server logs."],
        "Emphasize: Use `await websocket.close(code=1008)` for WebSocket authorization errors; never raise `HTTPException` after `websocket.accept()`.",
        ["[WebSockets Basics](../07-api-engineering/websockets.md)", "[Authentication](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc6455#section-7.4"]
    ),

    # FA-INT-174
    (
        "FA-INT-174",
        "Testing Middleware in Isolation Using `TestClient` and Starlette `Endpoint`",
        "Middleware is tested in isolation by mounting it onto a minimalist dummy FastAPI application using `TestClient` or `httpx.AsyncClient` without booting the entire production app.",
        "Testing middleware inside a full production application introduces heavy external dependencies (databases, Redis, external APIs). Isolated middleware testing mounts the target middleware on a lightweight, dedicated test FastAPI instance with dummy test routes. Tests assert that headers are injected, rate limits trigger, and unauthorized requests are rejected as expected.",
        "import pytest\nfrom fastapi import FastAPI, Request\nfrom httpx import AsyncClient, ASGITransport\n\n# Middleware to test\nasync def dummy_middleware(request: Request, call_next):\n    response = await call_next(request)\n    response.headers['X-Tested'] = 'True'\n    return response\n\n# Minimal isolated test app\ntest_app = FastAPI()\ntest_app.middleware('http')(dummy_middleware)\n\n@test_app.get('/test-route')\nasync def sample_route():\n    return {'status': 'ok'}\n\n@pytest.mark.asyncio\nasync def test_middleware_header_injection():\n    async with AsyncClient(transport=ASGITransport(app=test_app), base_url='http://test') as ac:\n        res = await ac.get('/test-route')\n        assert res.status_code == 200\n        assert res.headers['X-Tested'] == 'True'",
        "Testing middleware in isolation using a lightweight dedicated test FastAPI application and AsyncClient.",
        "The test client executes requests directly through the ASGI interface without opening TCP network sockets, allowing lightning-fast unit test execution in CI/CD pipelines.",
        "Unit testing authentication middleware, header injection, IP whitelisting, and rate-limiting modules.",
        ["Why is testing middleware in isolation better than running full end-to-end integration tests?", "How do you test error conditions where the downstream route raises an unhandled exception?"],
        ["Running full production database migrations just to test a CORS or header injection middleware.", "Using synchronous `TestClient` on async pure ASGI middleware that requires native asyncio loop context."],
        "Best practice: Build lightweight dummy apps inside your test files to test each middleware class in complete isolation.",
        ["[Testing FastAPI](testing.md)", "[Pure ASGI Middleware](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/testclient/"]
    ),

    # FA-INT-175
    (
        "FA-INT-175",
        "Graceful Error Recovery with Circuit-Breaker Tripping Middleware",
        "Circuit-breaker middleware tracks downstream error rates and trips to an open state when thresholds are breached, returning fast HTTP 503 fallback responses without stressing failing services.",
        "When an upstream database or external dependency fails, incoming requests continue to pile up, exhausting threadpools and memory until the entire application crashes (cascading failure). Circuit-breaker middleware wraps the request pipeline: 1) Closed: Normal execution; errors increment a failure counter; 2) Open: When failure rate exceeds threshold (e.g. 5 failures in 10s), the circuit trips to OPEN, instantly returning HTTP 503 Service Unavailable with `Retry-After: 30` without calling downstream handlers; 3) Half-Open: After a cooldown, allows a single test request to check if downstream systems have recovered.",
        "import time\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\nclass CircuitBreaker:\n    def __init__(self, threshold: int = 3, cooldown: float = 10.0):\n        self.threshold = threshold\n        self.cooldown = cooldown\n        self.failures = 0\n        self.state = 'CLOSED'\n        self.last_failure_time = 0.0\n\n    def is_available(self) -> bool:\n        if self.state == 'OPEN':\n            if time.time() - self.last_failure_time > self.cooldown:\n                self.state = 'HALF-OPEN'\n                return True\n            return False\n        return True\n\nbreaker = CircuitBreaker()\n\n@app.middleware('http')\nasync def circuit_breaker_middleware(request: Request, call_next):\n    if not breaker.is_available():\n        return JSONResponse(\n            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,\n            content={'error': 'CIRCUIT_OPEN', 'message': 'Service temporarily degraded; please retry later.'},\n            headers={'Retry-After': '10'}\n        )\n    try:\n        response = await call_next(request)\n        if breaker.state == 'HALF-OPEN' and response.status_code < 500:\n            breaker.state = 'CLOSED'\n            breaker.failures = 0\n        return response\n    except Exception:\n        breaker.failures += 1\n        breaker.last_failure_time = time.time()\n        if breaker.failures >= breaker.threshold:\n            breaker.state = 'OPEN'\n        raise",
        "Implementing a circuit-breaker middleware protecting backend infrastructure from cascading failures.",
        "When the circuit is OPEN, requests are terminated in < 1ms at the outer middleware boundary. This halts the influx of requests to the failing database or backend service, giving it time to recover.",
        "High-traffic e-commerce checkouts, payment gateway integrations, and microservice inter-service communication.",
        ["What are the three states of the Circuit Breaker pattern?", "Why is returning HTTP 503 with a `Retry-After` header better than letting requests time out after 30 seconds?"],
        ["Allowing requests to wait for 30s timeouts during an outage, causing threadpool exhaustion across all application servers.", "Failing to implement a Half-Open state, requiring a manual restart to reset the circuit breaker."],
        "Remember: Fast failure (5ms 503 response) is vastly superior to slow failure (30-second gateway timeout).",
        ["[Resilience Architecture](../10-system-design/fundamentals.md)", "[Rate Limiting](middleware-and-exception-handling.md)"],
        ["https://martinfowler.com/bliki/CircuitBreaker.html"]
    ),
]
