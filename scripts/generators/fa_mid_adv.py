"""
fa_mid_adv.py
=============
Advanced FastAPI Middleware & Exception Handling Questions: FA-ADV-151 to FA-ADV-175 (25 questions)
"""

adv_data = [
    # FA-ADV-151
    (
        "FA-ADV-151",
        "ASGI Specification Deep Dive: `scope`, `receive`, and `send` Event Lifecycles",
        "ASGI standardizes Python asynchronous web servers through three primitives: a connection metadata dictionary (`scope`), an incoming message channel (`receive`), and an outgoing message channel (`send`).",
        "The ASGI (Asynchronous Server Gateway Interface) 3.0 specification structures server-application communication: 1) `scope`: A dictionary created per connection containing immutable metadata (`type`, `asgi`, `http_version`, `method`, `path`, `raw_path`, `query_string`, `headers`, `client`, `server`); 2) `receive`: An awaitable callable that yields event messages from the server (e.g. `{'type': 'http.request', 'body': b'...', 'more_body': False}`); 3) `send`: An awaitable callable dispatched by the application to send events to the server (`{'type': 'http.response.start', 'status': 200, 'headers': [...]}`, followed by one or more `{'type': 'http.response.body', 'body': b'...', 'more_body': False}`).",
        "from starlette.types import Scope, Receive, Send\n\n# Minimal pure ASGI 3.0 application without framework overhead\nasync def minimal_asgi_app(scope: Scope, receive: Receive, send: Send) -> None:\n    if scope['type'] == 'http':\n        # 1. Consume incoming request body\n        request_message = await receive()\n        \n        # 2. Send response start event\n        await send({\n            'type': 'http.response.start',\n            'status': 200,\n            'headers': [(b'content-type', b'text/plain'), (b'server', b'asgi-core')],\n        })\n        \n        # 3. Send response body event\n        await send({\n            'type': 'http.response.body',\n            'body': b'Hello from raw ASGI 3.0!',\n            'more_body': False,\n        })",
        "Writing a minimal zero-dependency ASGI 3.0 application handling raw receive and send events.",
        "Uvicorn manages the OS TCP socket. When an HTTP request packet arrives, Uvicorn parses the HTTP framing, populates `scope`, and invokes `app(scope, receive, send)`. The application awaits `receive` to fetch body bytes and awaits `send` to stream response chunks back down to Uvicorn's socket buffer.",
        "Building custom ultra-high-throughput proxies, raw WebSocket multiplexers, and custom ASGI gateway routers.",
        ["What is the significance of the `more_body: True` flag in `http.response.body` messages?", "What happens if an application dispatches `http.response.body` before `http.response.start`?"],
        ["Attempting to send `http.response.body` without first awaiting `http.response.start` (causes protocol violation error in Uvicorn).", "Assuming `headers` in ASGI scope is a dictionary (it is a list of two-item byte tuples: `list[tuple[bytes, bytes]]`)."],
        "Remember: In ASGI scope, headers are stored as raw `list[tuple[bytes, bytes]]` with lowercase byte names.",
        ["[Pure ASGI Middleware](middleware-and-exception-handling.md)", "[ASGI Architecture](async-and-concurrency.md)"],
        ["https://asgi.readthedocs.io/en/latest/specs/www.html"]
    ),

    # FA-ADV-152
    (
        "FA-ADV-152",
        "Eliminating Memory Leaks and Reference Cycles in ASGI Middleware Chains",
        "Memory leaks in ASGI middleware chains stem from uncollected closures, lingering task groups, and circular references between `Request` objects and middleware instances.",
        "In high-concurrency servers handling millions of requests, improper closure scoping in ASGI middleware can retain references to large request bodies or session objects. Common causes include: 1) Storing request references on class attributes (`self.last_request = request`); 2) Retaining circular references between custom response wrappers and the ASGI `send` callable; 3) Lingering coroutine frames in uncancelled task groups. To prevent leaks: scope all state strictly to local variables inside `__call__`, avoid class-level state mutations, and ensure `request.state` objects are garbage-collected upon response completion.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nimport weakref\n\nclass LeakFreeMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app  # Singleton application reference\n        # NEVER store request-scoped data on self (e.g. self.current_request = ...)\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] != 'http':\n            await self.app(scope, receive, send)\n            return\n            \n        # Local variable only; automatically collected when coroutine frame exits\n        request_metadata = {'start_time': 0.0}\n        \n        async def send_wrapper(message: dict) -> None:\n            # Clean closure: does not retain circular references to scope or app\n            await send(message)\n            \n        await self.app(scope, receive, send_wrapper)",
        "Writing clean, leak-free ASGI middleware with local scoping and zero state retention on self.",
        "Python's garbage collector frees local variables immediately when the coroutine frame finishes and exits. Storing state on `self` or creating cross-task closures attaches objects to the long-lived singleton middleware instance, preventing cyclic garbage collection and causing progressive memory growth.",
        "Production backends running 24/7 in Kubernetes pods with strict 512MB RAM limits.",
        ["How do circular references between closures and ASGI callables evade standard reference counting?", "How can `tracemalloc` be used to profile memory growth across middleware layers?"],
        ["Storing request-specific data on instance attributes (`self.user = ...`), causing data race conditions and memory leaks.", "Retaining references to consumed byte streams in global lists for logging purposes."],
        "Golden rule: Middleware instances are application-level singletons; NEVER assign per-request state to `self`.",
        ["[Memory Management](../01-python/memory-management.md)", "[Production Performance](production-and-performance.md)"],
        ["https://docs.python.org/3/library/gc.html"]
    ),

    # FA-ADV-153
    (
        "FA-ADV-153",
        "Handling Backpressure and Flow Control in Streaming ASGI Middleware",
        "Backpressure ensures that a fast database or file producer does not overwhelm a slow network consumer, implemented in ASGI by awaiting socket drain notifications between chunk sends.",
        "When an endpoint streams a 10GB video or millions of database records, if the server reads data faster than the client's network connection can download, intermediate memory buffers inflate until the server runs out of RAM. ASGI provides native flow control: `await send({'type': 'http.response.body', 'body': chunk, 'more_body': True})` does not return immediately if the OS socket buffer is full. It pauses the coroutine until Uvicorn drains the socket buffer, providing natural backpressure that throttles the producer.",
        "from collections.abc import AsyncGenerator\nfrom fastapi import FastAPI\nfrom fastapi.responses import StreamingResponse\nimport asyncio\n\napp = FastAPI()\n\nasync def controlled_data_producer() -> AsyncGenerator[bytes, None]:\n    # Produces chunks only as fast as the client consumes them (Backpressure)\n    for chunk_idx in range(100):\n        chunk = b'X' * 65536  # 64KB chunk\n        yield chunk\n        # Yielding to event loop ensures socket write drains before producing next chunk\n        await asyncio.sleep(0)\n\n@app.get('/stream/video')\nasync def stream_video():\n    return StreamingResponse(controlled_data_producer(), media_type='application/octet-stream')",
        "Enforcing backpressure by yielding discrete chunks through StreamingResponse and allowing socket drainage.",
        "Under the hood, Uvicorn connects the ASGI `send` callable to asyncio's `transport.write()`. When high-water marks are exceeded, Uvicorn pauses protocol reading and resumes only when the kernel emits a low-water mark drain notification (`resume_writing`).",
        "High-definition video delivery, audio podcast streaming, and massive database cursor exports.",
        ["What is TCP window size and how does it propagate backpressure across network connections?", "What happens if a streaming producer ignores backpressure and buffers everything in Python memory?"],
        ["Reading an entire 5GB file into memory before streaming, causing instant OOM crashes.", "Wrapping streaming responses in middleware that eagerly reads all chunks to calculate hashes."],
        "Emphasize: Awaiting `send` in ASGI naturally propagates TCP backpressure from the client up to the data generator.",
        ["[Streaming Database Cursors](database-integration.md)", "[Async Concurrency](async-and-concurrency.md)"],
        ["https://asgi.readthedocs.io/en/latest/specs/www.html#response-start-send-event"]
    ),

    # FA-ADV-154
    (
        "FA-ADV-154",
        "Distributed Tracing Propagation (W3C `traceparent` / B3) Across Async Middleware",
        "Distributed tracing middleware extracts incoming W3C `traceparent` headers, sets OpenTelemetry active trace contexts, and injects outbound headers into downstream HTTP clients.",
        "In modern microservice meshes, a distributed trace follows an end-to-end user operation across dozens of services. The W3C Trace Context standard defines the `traceparent` header format: `00-{trace_id}-{parent_id}-{trace_flags}` (e.g. `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`). Middleware parses this header, links the current FastAPI span to the parent trace, and attaches the context to `contextvars` so outbound `httpx` calls automatically propagate the trace.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nimport re\n\nTRACEPARENT_REGEX = re.compile(r'^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$')\n\nclass TracePropagationMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] == 'http':\n            traceparent = None\n            for key, val in scope.get('headers', []):\n                if key.lower() == b'traceparent':\n                    traceparent = val.decode('latin1')\n                    break\n            \n            if traceparent and TRACEPARENT_REGEX.match(traceparent):\n                scope['state'] = scope.get('state', {})\n                scope['state']['traceparent'] = traceparent\n                \n        await self.app(scope, receive, send)",
        "Parsing and validating incoming W3C traceparent headers directly in ASGI scope.",
        "The middleware reads the incoming byte headers from `scope['headers']`. By validating the hex regex, it extracts the 128-bit trace ID and 64-bit parent span ID, configuring the distributed tracer before application routing begins.",
        "Distributed observability across Kubernetes clusters integrating with Datadog, Honeycomb, or AWS X-Ray.",
        ["What are the 4 fields of a W3C `traceparent` header (version, trace_id, parent_id, trace_flags)?", "How do B3 propagation headers (`X-B3-TraceId`) differ from W3C `traceparent`?"],
        ["Generating a brand new trace ID on every service hop instead of propagating the parent trace ID.", "Failing to inject trace headers into outbound downstream API calls, breaking the distributed trace graph."],
        "Remember: Always propagate existing `traceparent` headers to keep microservice spans linked under one trace.",
        ["[Contextvars Logging](middleware-and-exception-handling.md)", "[Distributed Architecture](../10-system-design/distributed-systems.md)"],
        ["https://www.w3.org/TR/trace-context/"]
    ),

    # FA-ADV-155
    (
        "FA-ADV-155",
        "Zero-Copy Request Proxying and ASGI Reverse Proxy Middleware",
        "ASGI reverse proxy middleware forwards incoming request streams directly to upstream microservices using `httpx.AsyncClient` streaming, achieving near zero-copy proxying without buffering in RAM.",
        "Building an API gateway or backend-for-frontend (BFF) in FastAPI often requires reverse proxying specific requests to internal backend microservices. Naive implementations read the entire request body into RAM with `await request.body()`, send a new request, and buffer the response. A high-performance reverse proxy pipes the incoming ASGI `receive` stream directly into an outbound `httpx.AsyncClient(stream=True)` stream, forwarding response chunks to `send` as they arrive.",
        "from fastapi import FastAPI, Request\nfrom fastapi.responses import StreamingResponse\nimport httpx\n\napp = FastAPI()\nclient = httpx.AsyncClient(base_url='https://internal-upstream-service.local')\n\n@app.api_route('/proxy/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])\nasync def reverse_proxy(request: Request, path: str):\n    url = httpx.URL(path=f'/{path}', query=request.url.query.encode('utf-8'))\n    \n    # Stream incoming request body directly to upstream without buffering in RAM\n    req = client.build_request(\n        method=request.method,\n        url=url,\n        headers=request.headers.raw,\n        content=request.stream()\n    )\n    upstream_response = await client.send(req, stream=True)\n    \n    # Stream upstream response directly back to client\n    return StreamingResponse(\n        upstream_response.aiter_raw(),\n        status_code=upstream_response.status_code,\n        headers=dict(upstream_response.headers),\n        background=httpx.Response(200).aclose  # Cleanup upstream socket on finish\n    )",
        "Streaming bidirectional reverse proxy pipeline using httpx request and response streams.",
        "By binding `content=request.stream()` and `upstream_response.aiter_raw()`, data packets flow from the client socket through FastAPI's event loop to the upstream socket in small 8KB-64KB buffers without holding the entire payload in memory.",
        "API Gateway microservices, Backend-for-Frontend (BFF) aggregators, and dynamic microservice routers.",
        ["Why must you use `stream=True` on both request and response in reverse proxies?", "What hop-by-hop headers (e.g. `Transfer-Encoding`, `Connection`) must be stripped when proxying?"],
        ["Forwarding hop-by-hop headers (`Connection: keep-alive`), which violates RFC 7230 and causes proxy connection failures.", "Buffering multi-gigabyte file uploads in memory inside proxy gateways."],
        "Strip hop-by-hop headers (`Connection`, `Keep-Alive`, `Proxy-Authenticate`, `Transfer-Encoding`) before proxying HTTP requests.",
        ["[HTTP & HTTPS](../07-api-engineering/http-and-https.md)", "[Streaming Responses](async-and-concurrency.md)"],
        ["https://www.encode.io/httpx/advanced/#streaming-requests"]
    ),

    # FA-ADV-156
    (
        "FA-ADV-156",
        "Byte-Range Requests and Partial Content (`206 Partial Content`) Middleware",
        "Byte-range middleware parses `Range: bytes=start-end` headers to serve partial content chunks (`HTTP 206`), enabling video seeking and resumable downloads.",
        "When web browsers stream video or audio files, they do not download the entire media file at once. They request small byte slices via `Range: bytes=1048576-2097151`. Middleware inspects the `Range` header, opens the file using asynchronous seekable file I/O, extracts the requested byte slice, sets `Content-Range: bytes start-end/total`, and returns status code `206 Partial Content`.",
        "from fastapi import FastAPI, Request, Response, status\nimport os\n\napp = FastAPI()\nVIDEO_PATH = 'media/sample.mp4'\n\n@app.get('/video')\nasync def stream_partial_video(request: Request):\n    if not os.path.exists(VIDEO_PATH):\n        return Response(status_code=404)\n        \n    file_size = os.path.getsize(VIDEO_PATH)\n    range_header = request.headers.get('range')\n    \n    if not range_header or not range_header.startswith('bytes='):\n        # Full content response if no Range header provided\n        with open(VIDEO_PATH, 'rb') as f:\n            return Response(f.read(), media_type='video/mp4')\n            \n    # Parse byte range: 'bytes=0-1023'\n    range_val = range_header.replace('bytes=', '')\n    parts = range_val.split('-')\n    start = int(parts[0])\n    end = int(parts[1]) if parts[1] else min(start + 1024 * 1024 - 1, file_size - 1)\n    length = end - start + 1\n    \n    with open(VIDEO_PATH, 'rb') as f:\n        f.seek(start)\n        data = f.read(length)\n        \n    headers = {\n        'Content-Range': f'bytes {start}-{end}/{file_size}',\n        'Accept-Ranges': 'bytes',\n        'Content-Length': str(length),\n    }\n    return Response(data, status_code=status.HTTP_206_PARTIAL_CONTENT, headers=headers, media_type='video/mp4')",
        "Serving seekable video slices with HTTP 206 Partial Content and Content-Range headers.",
        "When video players seek to the middle of a timeline, the browser sends a byte-range request for that timestamp. The server returns only those bytes with `206 Partial Content`, enabling instant playback without downloading preceding video data.",
        "Video-on-demand (VOD) streaming platforms, podcast streaming services, and large resumable file download managers.",
        ["What HTTP status code is used for byte-range responses (206)?", "What status code should be returned if the requested range is unsatisfiable (416 Range Not Satisfiable)?"],
        ["Returning HTTP 200 OK with the entire file when a client requested a `Range`, breaking video seeking controls in browsers.", "Off-by-one errors when computing `Content-Length` (`end - start + 1`)."],
        "Remember: Range boundaries are inclusive (`bytes 0-499/1000` represents 500 bytes).",
        ["[HTTP Headers](../07-api-engineering/http-and-https.md)", "[Static Files](routing-and-dependencies.md)"],
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests"]
    ),

    # FA-ADV-157
    (
        "FA-ADV-157",
        "Defending Against Slowloris and Slow-POST Attacks with ASGI Timeout Wrappers",
        "Slowloris attacks tie up server connection pools by sending HTTP headers or body bytes at a crawl; ASGI timeout wrappers abort sockets that fail to complete requests within strict timeouts.",
        "In a Slowloris attack, malicious clients open thousands of TCP connections to Uvicorn, sending 1 byte every 10 seconds (e.g. `X-Header: a...`). Because standard servers wait for complete headers or bodies, all worker connection slots become occupied, causing a denial of service for legitimate users. While reverse proxies (Nginx/Cloudflare) provide primary mitigation, ASGI timeout middleware enforces an aggressive read deadline: if the client does not send the complete request body within a bounded window (e.g. 15s), the middleware raises `asyncio.TimeoutError` and terminates the socket.",
        "import asyncio\nfrom starlette.types import ASGIApp, Scope, Receive, Send\nfrom fastapi.responses import JSONResponse\n\nclass SlowlorisDefenseMiddleware:\n    def __init__(self, app: ASGIApp, timeout_seconds: float = 15.0):\n        self.app = app\n        self.timeout = timeout_seconds\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] != 'http':\n            await self.app(scope, receive, send)\n            return\n\n        # Wrap receive with asyncio timeout to abort slow-POST / slowloris clients\n        async def timed_receive():\n            try:\n                return await asyncio.wait_for(receive(), timeout=self.timeout)\n            except asyncio.TimeoutError:\n                # Abort connection immediately\n                raise ConnectionResetError('Client read timeout exceeded')\n\n        await self.app(scope, timed_receive, send)",
        "Enforcing request receive timeouts to terminate Slowloris slow-drip connections.",
        "`asyncio.wait_for(receive(), timeout)` sets a timer on the incoming socket read. If the client drips bytes slower than the timeout, the event loop cancels the coroutine and drops the file descriptor, recycling the connection slot.",
        "Edge-facing FastAPI services exposed directly to public traffic without commercial WAF protection.",
        ["How does a Slowloris attack exhaust server resources without generating high bandwidth?", "Why is Nginx's `client_body_timeout` and `client_header_timeout` the preferred first line of defense?"],
        ["Setting read timeouts too short (e.g. 1s), which drops legitimate mobile clients on poor cellular connections.", "Assuming connection pools protect against Slowloris (connection pools manage DB connections, not client TCP sockets)."],
        "Best practice: Enforce client read timeouts at both the reverse proxy (Nginx `client_body_timeout 10s`) and ASGI application layers.",
        ["[Nginx Hardening](../11-devops/nginx.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://en.wikipedia.org/wiki/Slowloris_(computer_security)"]
    ),

    # FA-ADV-158
    (
        "FA-ADV-158",
        "Dynamic Rate Limiting Based on JWT Tenant Tiers Using Token-Bucket in Redis",
        "Tenant-tier rate limiting dynamically adjusts rate thresholds based on the authenticated user's tier (Free: 10 req/min, Pro: 100 req/min, Enterprise: 1000 req/min) using Redis token-bucket algorithms.",
        "One-size-fits-all rate limiting penalizes paying customers and under-protects against free-tier abuse. In tier-aware rate limiting: 1) Middleware inspects the request's JWT or API key to resolve the tenant ID and subscription tier; 2) It queries Redis using an atomic Token-Bucket Lua script with parameters tailored to that tier; 3) Headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` are returned; 4) Requests exceeding the tier quota are rejected with HTTP 429.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\nTIER_LIMITS = {\n    'free': 10,        # 10 req/min\n    'pro': 100,        # 100 req/min\n    'enterprise': 1000 # 1000 req/min\n}\n\ndef resolve_tenant_tier(request: Request) -> tuple[str, str]:\n    # Resolve tier from API key or JWT claim\n    api_key = request.headers.get('x-api-key', '')\n    if api_key.startswith('ent_'):\n        return api_key, 'enterprise'\n    if api_key.startswith('pro_'):\n        return api_key, 'pro'\n    return request.client.host if request.client else 'anonymous', 'free'\n\n@app.middleware('http')\nasync def dynamic_tier_rate_limiter(request: Request, call_next):\n    tenant_id, tier = resolve_tenant_tier(request)\n    limit = TIER_LIMITS[tier]\n    \n    # In production, check Redis token bucket for tenant_id with capacity=limit\n    is_allowed = True  # Simulated Redis check\n    \n    if not is_allowed:\n        return JSONResponse(\n            status_code=status.HTTP_429_TOO_MANY_REQUESTS,\n            content={'error': 'TIER_QUOTA_EXCEEDED', 'tier': tier, 'limit': limit}\n        )\n        \n    response = await call_next(request)\n    response.headers['X-RateLimit-Tier'] = tier\n    response.headers['X-RateLimit-Limit'] = str(limit)\n    return response",
        "Resolving tenant subscription tier and enforcing dynamic rate limit quotas in middleware.",
        "The token-bucket algorithm refills tokens continuously at rate `R` up to capacity `C`. A single Redis Lua script evaluates current tokens, subtracts 1, and calculates reset time atomically, ensuring thread-safe distributed enforcement across all server pods.",
        "SaaS developer APIs, multi-tenant B2B platforms, and paid API tier monetization.",
        ["Why is Redis Lua scripting required to implement atomic token-bucket rate limiting?", "What headers are standardized by the IETF for rate limiting (`RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`)?"],
        ["Executing multiple non-atomic Redis commands (`GET`, increment, `EXPIRE`), causing race conditions under high concurrency.", "Hardcoding rate limits in code rather than allowing dynamic configuration updates via Redis."],
        "Use Redis Lua scripts for token-bucket rate limiting to guarantee atomic decrement and refill calculations.",
        ["[Redis Integration](../06-redis-and-messaging/redis.md)", "[JWT Authentication](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/"]
    ),

    # FA-ADV-159
    (
        "FA-ADV-159",
        "TLS Fingerprinting (JA3/JA4) Inspection and Bot Mitigation in ASGI Middleware",
        "TLS fingerprinting (JA3/JA4) analyzes client SSL/TLS Client Hello parameters to identify automated scrapers and bots regardless of spoofed User-Agent headers.",
        "Malicious bots and scrapers frequently forge their `User-Agent` string to masquerade as standard Google Chrome or iOS Safari browsers. However, the cryptographic parameters negotiated during the TLS Client Hello handshake (ciphers, extensions, elliptic curves, signature algorithms) are determined by the underlying networking library (e.g. Python `requests`, Go `net/http`, cURL). Edge proxies (Cloudflare, Envoy) calculate the MD5 hash of these parameters (JA3 fingerprint) and forward it in a header (`X-JA3-Fingerprint`). ASGI middleware rejects requests whose JA3 hash matches known scraping toolkits.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Known JA3 hashes for malicious scrapers and default python-requests\nBLOCKED_JA3_FINGERPRINTS = {\n    'b32309a26951912be7dba376398abc3b',  # Known malicious scraper toolkit\n    'c129e12bf70942ff90df1d9d423cf9e3',  # Suspicious bot profile\n}\n\n@app.middleware('http')\nasync def ja3_bot_defense_middleware(request: Request, call_next):\n    ja3_hash = request.headers.get('x-ja3-fingerprint')\n    \n    if ja3_hash and ja3_hash in BLOCKED_JA3_FINGERPRINTS:\n        return JSONResponse(\n            status_code=status.HTTP_403_FORBIDDEN,\n            content={'error': 'BOT_DETECTED', 'message': 'Automated client fingerprint blocked'}\n        )\n        \n    return await call_next(request)\n\n@app.get('/market-data')\nasync def market_data():\n    return {'quote': 'AAPL', 'price': 185.50}",
        "Filtering bot traffic in middleware based on upstream JA3 TLS fingerprint headers.",
        "Because the TLS Client Hello handshake is completed before HTTP headers are transmitted, spoofing a JA3 fingerprint requires modifying the compiled C/Go TLS stack itself, making it far more resilient than User-Agent checks.",
        "Ticketing sites, airline seat inventory, financial quotes, and preventing automated scraping.",
        ["What components of the TLS Client Hello packet make up a JA3 fingerprint?", "Can Python's standard `ssl` library inspect JA3 fingerprints directly on incoming sockets?"],
        ["Relying exclusively on `User-Agent` strings for bot detection (trivial for attackers to forge).", "Blocking JA3 hashes without monitoring false positive rates across diverse mobile devices."],
        "Note: JA3 calculation is typically performed at the TLS termination layer (Envoy/Cloudflare) and passed to FastAPI via headers.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Security Hardening](../12-security/application-security.md)"],
        ["https://github.com/salesforce/ja3"]
    ),

    # FA-ADV-160
    (
        "FA-ADV-160",
        "Re-Entrancy and Exception Boundary Preservation in Nested ASGI Middleware",
        "Nested ASGI middleware must preserve exception propagation boundaries to ensure that outer error handlers and APM spans capture downstream failures correctly.",
        "In complex middleware stacks containing 10+ layers (Authentication -> RateLimit -> Tracing -> Database -> Compression), improper error catching in an intermediate layer can suppress exceptions, causing outer APM tracers to report false HTTP 200 successes for crashed requests. Robust ASGI middleware follows strict exception boundary rules: 1) Catch exceptions only to record metrics or clean up resources, then re-raise (`raise`); 2) Never swallow exceptions without returning a valid ASGI response message.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nimport logging\n\nlogger = logging.getLogger('boundary')\n\nclass ExceptionBoundaryMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] != 'http':\n            await self.app(scope, receive, send)\n            return\n            \n        try:\n            await self.app(scope, receive, send)\n        except Exception as exc:\n            # Record telemetry metric\n            logger.error(f'Downstream crash captured in boundary: {exc}')\n            # CRITICAL: Re-raise so outer ServerErrorMiddleware can generate 500 response\n            raise",
        "Preserving exception boundary propagation in pure ASGI middleware using try/except/raise.",
        "By re-raising the exception, the stack frame unwinds up to Starlette's `ServerErrorMiddleware`. Outer APM spans (Datadog/Sentry) intercept the exception, tag the span with `error=True`, and log the stack trace before rendering the HTTP 500 response.",
        "Enterprise microservice architectures requiring 100% trace fidelity and error alerting.",
        ["What happens if an intermediate middleware catches an exception and returns without calling `send`?", "How does `ServerErrorMiddleware` interact with re-raised exceptions?"],
        ["Catching exceptions in middleware and failing to call `send` or re-raise (the client socket hangs until timeout).", "Mutating response headers after downstream handlers have already dispatched `http.response.start`."],
        "Emphasize: Either re-raise the exception or dispatch a complete `http.response.start` and `http.response.body` response; never do neither.",
        ["[ServerErrorMiddleware](middleware-and-exception-handling.md)", "[Pure ASGI Middleware](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/exceptions/"]
    ),

    # FA-ADV-161
    (
        "FA-ADV-161",
        "Hot-Reloading Middleware Configurations Without Restarting Uvicorn",
        "Dynamic middleware reads configuration parameters from thread-safe shared state (Redis, Consul, or `asyncio.Event`) to update rate limits or CORS rules on the fly without zero-downtime restarts.",
        "Because `app.add_middleware()` constructs an immutable ASGI pipeline at startup, you cannot add or remove middleware classes while the server is running. However, high-availability systems must update rate limits, toggle maintenance mode, or adjust CORS whitelists instantly without restarting worker processes. This is accomplished by designing middleware to read configuration from a thread-safe shared state store (e.g. Redis Pub/Sub, etcd, or a background cache) on every request.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Dynamic configuration store updated in real time via background task or Redis\nDYNAMIC_CONFIG = {\n    'maintenance_mode': False,\n    'max_payload_bytes': 1024 * 1024,  # 1MB\n}\n\n@app.middleware('http')\nasync def dynamic_config_middleware(request: Request, call_next):\n    # Read current state dynamically on every request\n    if DYNAMIC_CONFIG['maintenance_mode'] and request.url.path != '/healthz':\n        return JSONResponse(\n            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,\n            content={'error': 'MAINTENANCE_MODE', 'message': 'System undergoing scheduled maintenance.'}\n        )\n    return await call_next(request)\n\n@app.post('/admin/toggle-maintenance')\nasync def toggle_maintenance(enable: bool):\n    # Hot-reload configuration without restarting Uvicorn\n    DYNAMIC_CONFIG['maintenance_mode'] = enable\n    return {'maintenance_mode': DYNAMIC_CONFIG['maintenance_mode']}",
        "Hot-reloading maintenance mode and configuration rules dynamically inside middleware.",
        "The middleware reads from the shared dictionary (or Redis client) during request execution. When the configuration is updated, all subsequent requests immediately observe the new behavior without triggering container restarts or socket dropouts.",
        "Feature flagging (LaunchDarkly), dynamic IP blocking, instant maintenance mode toggles, and emergency rate limit throttles.",
        ["Why can't `app.add_middleware()` be called dynamically while Uvicorn is running?", "How do you synchronize dynamic configuration across 20 Uvicorn worker pods simultaneously?"],
        ["Restarting production clusters just to update a simple rate limit or whitelist parameter.", "Using local in-memory dictionaries for dynamic config across multi-pod deployments without a central Redis/etcd pub/sub sync."],
        "Use Redis Pub/Sub or etcd watchers to synchronize dynamic configuration changes across all running worker processes.",
        ["[Redis Pub/Sub](../06-redis-and-messaging/redis.md)", "[Production Deployment](production-and-performance.md)"],
        ["https://12factor.net/config"]
    ),

    # FA-ADV-162
    (
        "FA-ADV-162",
        "Custom Protocol Upgrade Middleware: HTTP to WebSocket Handshake Inspection",
        "ASGI middleware intercepts connection upgrades by evaluating `scope['type'] == 'websocket'`, validating authentication tickets before accepting or rejecting the handshake.",
        "In WebSocket architectures, authentication must occur during the initial HTTP upgrade handshake. If unauthorized, the connection should be rejected before the WebSocket connection is accepted. In ASGI, a WebSocket connection begins with `scope['type'] == 'websocket'`. Middleware can inspect query parameters or cookies in `scope`, validate JWT tokens, and reject unauthorized handshakes by dispatching `websocket.close` without entering the endpoint handler.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\n\nclass WebSocketAuthMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] == 'websocket':\n            # Extract query string from scope\n            query_string = scope.get('query_string', b'').decode('utf-8')\n            token = dict(qc.split('=') for qc in query_string.split('&') if '=' in qc).get('token')\n            \n            if token != 'valid-secret-ticket':\n                # Reject handshake before acceptance\n                await send({'type': 'websocket.close', 'code': 4401})\n                return\n                \n        await self.app(scope, receive, send)",
        "Intercepting and rejecting unauthorized WebSocket upgrade handshakes in pure ASGI middleware.",
        "The ASGI server initiates a WebSocket connection with a `websocket.connect` event. If the middleware sends `{'type': 'websocket.close', 'code': 4401}` prior to `websocket.accept`, the server rejects the HTTP 101 Switching Protocols response, terminating the connection immediately.",
        "Real-time financial ticker sockets, authenticated collaborative whiteboard sessions, and secure chat gateways.",
        ["Why can't standard HTTP `Authorization: Bearer` headers easily be used in browser WebSocket connections?", "What is an ephemeral WebSocket ticket pattern?"],
        ["Accepting the WebSocket connection first (`websocket.accept()`) and then checking authorization (wastes server resources on unauthorized connections).", "Attempting to read request bodies on WebSocket scopes."],
        "Best practice: Use an ephemeral ticket pattern (`/ws?ticket=<short_lived_token>`) validated during the ASGI handshake.",
        ["[WebSockets Basics](../07-api-engineering/websockets.md)", "[Authentication](authentication-and-security.md)"],
        ["https://asgi.readthedocs.io/en/latest/specs/www.html#websocket"]
    ),

    # FA-ADV-163
    (
        "FA-ADV-163",
        "Resilient Fallback Caches in Middleware During Downstream Outages",
        "Fallback cache middleware catches downstream database and external API failures, returning stale cached copies to keep user-facing APIs functional during outages.",
        "In mission-critical user interfaces (e.g. e-commerce homepages, flight search, news feeds), showing slightly stale data is vastly preferable to displaying a raw 500 error page. Fallback middleware implements the 'stale-if-error' pattern: 1) On successful GET requests, it caches the response in Redis; 2) If the downstream route raises an unhandled exception or database error, the middleware intercepts the exception, retrieves the stale cached response, attaches `X-Cache-Fallback: True`, and returns HTTP 200.",
        "import json\nfrom fastapi import FastAPI, Request, Response\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\nFALLBACK_CACHE = {}\n\n@app.middleware('http')\nasync def stale_if_error_middleware(request: Request, call_next):\n    cache_key = request.url.path\n    try:\n        response = await call_next(request)\n        if request.method == 'GET' and response.status_code == 200:\n            # Cache successful response for emergency fallback\n            FALLBACK_CACHE[cache_key] = {'status': 'healthy', 'cached_data': True}\n        return response\n    except Exception:\n        # Downstream crash: serve emergency stale cache if available\n        if request.method == 'GET' and cache_key in FALLBACK_CACHE:\n            return JSONResponse(\n                status_code=200,\n                content=FALLBACK_CACHE[cache_key],\n                headers={'X-Cache-Fallback': 'true', 'Warning': '110 - \"Response is Stale\"'}\n            )\n        raise  # Re-raise if no fallback available",
        "Serving stale cached responses when downstream route crashes occur (stale-if-error).",
        "The middleware acts as a resilience safety net. By catching unhandled downstream exceptions on read-only endpoints, it prevents cascading outages from affecting frontend end-users.",
        "High-visibility consumer apps where 100% availability is required during backend database failovers.",
        ["What is the HTTP `stale-if-error` Cache-Control directive?", "Why should stale fallback caches NEVER be applied to mutating POST/PUT endpoints?"],
        ["Applying fallback caching to checkout or payment processing endpoints (risks executing unconfirmed mutations).", "Caching sensitive user-specific data in a shared global fallback cache."],
        "Caution: Only apply fallback caches to idempotent, non-personalized GET endpoints.",
        ["[Resilience Architecture](../10-system-design/fundamentals.md)", "[Redis Caching](../06-redis-and-messaging/redis.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc5861"]
    ),

    # FA-ADV-164
    (
        "FA-ADV-164",
        "Asynchronous Audit Logging Pipelines with Zero Latency Impact Using Lock-Free Queues",
        "High-performance audit logging in middleware decouples log writing from HTTP request execution using in-memory `asyncio.Queue` workers, achieving sub-millisecond response latency.",
        "Writing audit logs directly to a database or remote ElasticSearch instance inside HTTP middleware adds 20-100ms of latency to every single API request. In zero-latency audit architectures: 1) The middleware places a lightweight audit log record into an in-memory `asyncio.Queue` in < 5 microseconds; 2) The HTTP response returns to the client immediately; 3) A dedicated background worker task batches queue items and flushes them to the audit database in bulk.",
        "import asyncio\nfrom fastapi import FastAPI, Request\nfrom contextlib import asynccontextmanager\n\naudit_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)\n\nasync def audit_worker():\n    while True:\n        # Consume batch of audit events from queue and persist to DB\n        event = await audit_queue.get()\n        # Simulated asynchronous bulk database flush\n        await asyncio.sleep(0.01)\n        audit_queue.task_done()\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    worker_task = asyncio.create_task(audit_worker())\n    yield\n    worker_task.cancel()\n\napp = FastAPI(lifespan=lifespan)\n\n@app.middleware('http')\nasync def non_blocking_audit_middleware(request: Request, call_next):\n    response = await call_next(request)\n    # Enqueue audit log without awaiting database I/O\n    audit_record = {'path': request.url.path, 'status': response.status_code}\n    try:\n        audit_queue.put_nowait(audit_record)  # Takes < 5 microseconds!\n    except asyncio.QueueFull:\n        pass  # Drop or record buffer overflow metric\n    return response",
        "Decoupling audit logging from the request-response cycle using non-blocking asyncio.Queue.",
        "`audit_queue.put_nowait()` is a non-blocking in-memory operation. The client receives the HTTP response without waiting for database writes, while the background worker handles batch persistence asynchronously.",
        "High-throughput banking platforms, compliance tracking, and security telemetry pipelines.",
        ["What happens if the `asyncio.Queue` becomes full during sudden traffic spikes?", "How do you ensure audit records in the queue are not lost during graceful application shutdown?"],
        ["Awaiting direct database insertions inside middleware, doubling API response times.", "Using an unbounded queue (`maxsize=0`), allowing memory to grow infinitely until an OOM crash occurs."],
        "Emphasize: Always bound queue capacity (`maxsize=10000`) and drain the queue during lifespan shutdown.",
        ["[Async Concurrency](async-and-concurrency.md)", "[Lifespan Events](async-and-concurrency.md)"],
        ["https://docs.python.org/3/library/asyncio-queue.html"]
    ),

    # FA-ADV-165
    (
        "FA-ADV-165",
        "Transforming Legacy XML/SOAP Requests into JSON Dynamically via ASGI Middleware",
        "XML translation middleware intercepts incoming `application/xml` payloads, parses XML elements into Python dictionaries using `xmltodict` or `defusedxml`, and serializes them as JSON for Pydantic route handlers.",
        "Migrating legacy enterprise systems (banking, healthcare, government) to modern FastAPI often requires supporting legacy clients that send XML/SOAP payloads. Rather than writing custom XML parsers in every endpoint, translation middleware intercepts incoming `Content-Type: application/xml` requests. It securely parses the XML into a dictionary, serializes it to JSON, updates the ASGI `scope['headers']` to `application/json`, and forwards the request to standard Pydantic endpoints.",
        "import json\nfrom fastapi import FastAPI, Request\nimport xml.etree.ElementTree as ET\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def xml_to_json_translation_middleware(request: Request, call_next):\n    content_type = request.headers.get('content-type', '').lower()\n    \n    if 'application/xml' in content_type or 'text/xml' in content_type:\n        raw_xml = await request.body()\n        # Parse XML into dictionary (using safe XML parser in production)\n        root = ET.fromstring(raw_xml)\n        data_dict = {child.tag: child.text for child in root}\n        json_bytes = json.dumps(data_dict).encode('utf-8')\n        \n        # Replay as JSON receive\n        async def json_receive():\n            return {'type': 'http.request', 'body': json_bytes, 'more_body': False}\n            \n        # Rewrite Content-Type header to application/json\n        request.scope['headers'] = [\n            (name, val if name.lower() != b'content-type' else b'application/json')\n            for name, val in request.scope['headers']\n        ]\n        request = Request(request.scope, json_receive)\n        \n    return await call_next(request)\n\n@app.post('/orders')\nasync def process_order(payload: dict):\n    return {'status': 'processed', 'data': payload}",
        "Dynamically converting XML/SOAP payloads into JSON within ASGI middleware.",
        "The route handler receives standard JSON data and requires zero knowledge of XML. The middleware handles translation transparently at the transport layer, allowing modern Pydantic models to validate legacy XML input.",
        "Legacy system modernizations, banking core integrations, and healthcare HL7/XML interoperability.",
        ["What is an XML External Entity (XXE) vulnerability, and why must `defusedxml` be used?", "What are the limitations of automatic XML-to-JSON mapping for attributes vs elements?"],
        ["Using standard Python `xml.etree.ElementTree` without disabling entity expansion, making the app vulnerable to XXE attacks.", "Failing to update `Content-Length` and `Content-Type` headers after rewriting the payload."],
        "Security essential: Always use `defusedxml` rather than standard `xml.etree` to prevent Billion Laughs and XXE attacks.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing"]
    ),

    # FA-ADV-166
    (
        "FA-ADV-166",
        "Preventing BREACH and CRIME Attacks When Using GZip Compression with HTTPS",
        "The BREACH attack exploits HTTP compression over TLS to decrypt secret CSRF or authentication tokens; it is mitigated by masking secrets or disabling compression on responses with user input.",
        "The BREACH (Browser Reconnaissance and Exfiltration via Adaptive Compression of Hypertext) vulnerability attacks HTTPS by observing the byte length of gzip-compressed responses. If an attacker injects guessed reflection characters into an endpoint that also reflects a secret CSRF token, gzip will compress matching characters more efficiently, resulting in a slightly smaller payload. By observing response lengths across multiple guesses, the attacker extracts the token. Mitigation: 1) Mask tokens using XOR masking on every response (used by Django); 2) Disable compression on responses containing both user input and secrets; 3) Inject random byte padding into responses.",
        "import os\nfrom fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def breach_mitigation_middleware(request: Request, call_next):\n    response = await call_next(request)\n    \n    # Add randomized padding length to obscure exact compressed byte boundaries\n    if response.headers.get('content-encoding') == 'gzip':\n        random_padding = os.urandom(os.urandom(1)[0] % 32)\n        response.headers['X-Padding'] = random_padding.hex()\n        \n    return response",
        "Adding random byte padding headers to obscure gzip compression length differences and mitigate BREACH.",
        "Random padding introduces noise into the payload length, preventing statistical byte-length analysis from determining whether an attacker's guessed token character was a compression match.",
        "Banking APIs, authenticated user dashboards, and portals serving sensitive session cookies and CSRF tokens over TLS.",
        ["How does the combination of TLS, HTTP compression, and user reflection create the BREACH vulnerability?", "Why does XOR-masking CSRF tokens neutralize BREACH?"],
        ["Assuming HTTPS encryption makes GZip compression completely secure against traffic analysis.", "Compressing responses that reflect un-sanitized user query parameters alongside secret authentication tokens."],
        "Emphasize: Never compress responses that contain both secret tokens and reflected user input without token masking.",
        ["[API Security](../07-api-engineering/api-security.md)", "[GZip Middleware](middleware-and-exception-handling.md)"],
        ["https://en.wikipedia.org/wiki/BREACH"]
    ),

    # FA-ADV-167
    (
        "FA-ADV-167",
        "Mitigating HTTP Request Smuggling and Header Injection at the ASGI Layer",
        "HTTP Request Smuggling occurs when front-end proxies and back-end ASGI servers disagree on request framing (`Content-Length` vs `Transfer-Encoding`), prevented by strict ASGI header validation.",
        "In HTTP Request Smuggling (HRS), an attacker crafts a malicious request with ambiguous framing (e.g. both `Transfer-Encoding: chunked` and `Content-Length: 10`). If the frontend proxy relies on `Content-Length` while Uvicorn relies on `Transfer-Encoding`, the trailing bytes of the request are treated by the backend as the beginning of the *next* user's request, hijacking authentication sessions. Mitigation: 1) Reject requests containing both headers with HTTP 400; 2) Enforce HTTP/2 or HTTP/3 at edge reverse proxies; 3) Normalize headers at the ASGI boundary.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nfrom fastapi.responses import JSONResponse\n\nclass RequestSmugglingDefenseMiddleware:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        if scope['type'] == 'http':\n            has_cl = False\n            has_te = False\n            for name, val in scope.get('headers', []):\n                if name.lower() == b'content-length':\n                    has_cl = True\n                elif name.lower() == b'transfer-encoding':\n                    has_te = True\n                    \n            # RFC 7230: Requests containing BOTH must be rejected to prevent smuggling\n            if has_cl and has_te:\n                response = JSONResponse(\n                    status_code=400,\n                    content={'error': 'INVALID_FRAMING', 'message': 'Conflicting framing headers'}\n                )\n                await response(scope, receive, send)\n                return\n                \n        await self.app(scope, receive, send)",
        "Rejecting ambiguous HTTP framing headers in ASGI middleware to prevent request smuggling.",
        "RFC 7230 mandates that if a request contains both `Transfer-Encoding` and `Content-Length`, it is either an error or `Transfer-Encoding` overrides. By rejecting requests with both headers at the ASGI boundary, request smuggling desynchronization is eliminated.",
        "Perimeter API gateways and microservices operating behind heterogeneous reverse proxy clusters.",
        ["What is the difference between CL.TE and TE.CL request smuggling?", "Why does HTTP/2 eliminate request smuggling vulnerabilities between proxies?"],
        ["Allowing requests with multiple `Content-Length` headers through to backend handlers.", "Assuming reverse proxies catch all framing discrepancies (proxies often pass through raw headers)."],
        "Golden rule of HTTP security: Reject requests containing both `Content-Length` and `Transfer-Encoding` immediately with HTTP 400.",
        ["[Nginx Proxy Configuration](../11-devops/nginx.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://portswigger.net/web-security/request-smuggling"]
    ),

    # FA-ADV-168
    (
        "FA-ADV-168",
        "High-Performance Memory-Mapped Payload Buffering for Multi-Gigabyte File Uploads",
        "Streaming multi-gigabyte uploads to disk using `SpooledTemporaryFile` and memory-mapped files (`mmap`) prevents memory exhaustion while supporting random access in middleware.",
        "When handling large file uploads (e.g. 5GB video files or disk images), buffering the upload in memory crashes the container. Standard disk file operations introduce slow synchronous POSIX I/O. Using `tempfile.SpooledTemporaryFile(max_size=10*1024*1024)` buffers small files up to 10MB in memory; if the upload exceeds 10MB, it rolls over to a temporary disk file. Python's `mmap` module maps the file into the virtual address space, allowing high-speed zero-copy inspection.",
        "import tempfile\nimport mmap\nfrom fastapi import FastAPI, UploadFile, File\n\napp = FastAPI()\n\n@app.post('/upload/large-file')\nasync def upload_large_file(file: UploadFile = File(...)):\n    # SpooledTemporaryFile keeps up to 10MB in RAM, spilling to disk automatically\n    with tempfile.NamedTemporaryFile(delete=True) as temp_disk_file:\n        # Stream chunks asynchronously without loading entire file to RAM\n        while chunk := await file.read(1024 * 1024):  # 1MB chunk\n            temp_disk_file.write(chunk)\n            \n        temp_disk_file.flush()\n        file_size = temp_disk_file.tell()\n        \n        if file_size > 0:\n            # Memory-map the temporary file for zero-copy binary inspection\n            with mmap.mmap(temp_disk_file.fileno(), 0, access=mmap.ACCESS_READ) as mm:\n                # Inspect file magic bytes (e.g. check for ELF, PDF, or MP4 headers)\n                header_bytes = mm[:4]\n                \n    return {'status': 'processed', 'size_bytes': file_size, 'magic': header_bytes.hex()}",
        "Streaming large uploads to temporary disk files and performing zero-copy inspection using mmap.",
        "`mmap` leverages the operating system's virtual memory page cache. Pages are paged in from disk on demand, allowing the application to read binary headers and compute hashes without loading gigabytes of data into Python object memory.",
        "Biomedical imaging portals, raw video ingestion pipelines, and firmware update servers.",
        ["Why is `SpooledTemporaryFile` superior to a pure in-memory `io.BytesIO` buffer?", "How does `mmap` achieve zero-copy memory access during file inspection?"],
        ["Using `await file.read()` without chunking, loading multi-gigabyte files into RAM and causing OOM kills.", "Failing to clean up temporary files after request completion, filling the container's root disk."],
        "Tip: Always stream files in 1MB chunks and leverage `mmap` for instant binary header inspection.",
        ["[File Uploads](routing-and-dependencies.md)", "[Performance Optimization](../01-python/internals-and-performance.md)"],
        ["https://docs.python.org/3/library/mmap.html"]
    ),

    # FA-ADV-169
    (
        "FA-ADV-169",
        "Tenant-Isolated Rate Limiting and Quota Management in SaaS Middleware",
        "Multi-tenant SaaS platforms enforce dual-level rate limiting: per-user burst limits (preventing single-user flooding) and global tenant aggregate quotas (preventing neighbor noise).",
        "In B2B SaaS, an enterprise customer might purchase 100,000 API calls per day. If one developer within that company runs an infinite loop script, they could exhaust the entire company's quota within minutes. Multi-tenant rate limiting enforces a hierarchical policy: 1) Level 1 (Burst Limiter): Bounded per-user limits (e.g. 50 req/sec per user ID); 2) Level 2 (Tenant Aggregation): Bounded daily quota per organization ID (e.g. 100,000 req/day). Middleware tracks both keys in Redis pipelines.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Simulated hierarchical rate check\nasync def check_hierarchical_rate_limit(tenant_id: str, user_id: str) -> tuple[bool, str]:\n    # 1. Check user burst limit\n    user_burst_ok = True  # Redis check: user:{user_id}:burst\n    if not user_burst_ok:\n        return False, 'USER_BURST_LIMIT_EXCEEDED'\n        \n    # 2. Check tenant aggregate daily quota\n    tenant_quota_ok = True  # Redis check: tenant:{tenant_id}:daily_quota\n    if not tenant_quota_ok:\n        return False, 'TENANT_DAILY_QUOTA_EXHAUSTED'\n        \n    return True, ''\n\n@app.middleware('http')\nasync def multi_tenant_rate_limiter(request: Request, call_next):\n    tenant_id = request.headers.get('x-tenant-id', 'public')\n    user_id = request.headers.get('x-user-id', 'anonymous')\n    \n    allowed, reason = await check_hierarchical_rate_limit(tenant_id, user_id)\n    if not allowed:\n        return JSONResponse(\n            status_code=status.HTTP_429_TOO_MANY_REQUESTS,\n            content={'error': reason, 'tenant_id': tenant_id}\n        )\n        \n    return await call_next(request)",
        "Hierarchical rate limiting enforcing both per-user burst and per-tenant aggregate quotas.",
        "The middleware evaluates both rate limit dimensions in a single atomic Redis pipeline round-trip. This protects against the 'noisy neighbor' problem while safeguarding the tenant's daily quota from runaway scripts.",
        "Multi-tenant SaaS APIs, cloud developer platforms, and enterprise CRM integrations.",
        ["What is the 'noisy neighbor' problem in multi-tenant cloud architecture?", "How do you handle rate limiting when Redis experiences a temporary outage (Fail Open vs Fail Closed)?"],
        ["Failing closed during a Redis outage and blocking all legitimate customers (production rate limiters should fail open on cache failure).", "Tracking only tenant-level quotas, allowing one rogue user to lock out the entire company."],
        "Architecture principle: In production, rate limiters should FAIL OPEN if Redis is unreachable to avoid turning cache blips into total outages.",
        ["[Multi-Tenancy](database-integration.md)", "[Redis Architecture](../06-redis-and-messaging/redis.md)"],
        ["https://aws.amazon.com/blogs/architecture/rate-limiting-strategies-for-serverless-applications/"]
    ),

    # FA-ADV-170
    (
        "FA-ADV-170",
        "Asynchronous Distributed Session Store Middleware with Redis Sliding Expiration",
        "Distributed session middleware stores encrypted user session dictionaries in Redis, resetting the session Time-To-Live (TTL) on each active request via sliding expiration.",
        "Storing session state in local server memory breaks when scaling to multiple Uvicorn worker processes or Kubernetes pods. Custom distributed session middleware reads a signed `session_id` cookie from the client, fetches the session dictionary from Redis over an asynchronous connection, and exposes it as `request.state.session`. Upon response completion, the middleware refreshes the Redis key TTL (sliding expiration, e.g. 30 minutes from last activity).",
        "import json\nimport uuid\nfrom fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n# Simulated async Redis session store\nSESSION_STORE = {}\n\n@app.middleware('http')\nasync def distributed_session_middleware(request: Request, call_next):\n    session_id = request.cookies.get('session_token')\n    is_new = False\n    if not session_id or session_id not in SESSION_STORE:\n        session_id = str(uuid.uuid4())\n        SESSION_STORE[session_id] = {}\n        is_new = True\n        \n    # Attach session dictionary to request state\n    request.state.session = SESSION_STORE[session_id]\n    \n    response = await call_next(request)\n    \n    # Sliding expiration: refresh TTL on active request\n    if is_new:\n        response.set_cookie('session_token', session_id, httponly=True, secure=True, samesite='lax')\n        \n    return response\n\n@app.get('/profile')\nasync def profile(request: Request):\n    user = request.state.session.get('user', 'Guest')\n    return {'user': user}",
        "Implementing distributed session management with Redis and sliding cookie expiration.",
        "The session dictionary lives in distributed Redis memory accessible to any worker pod. The client only holds the opaque 128-bit session token, ensuring zero session affinity (sticky session) requirements at the load balancer.",
        "Stateless web applications, single sign-on (SSO) portals, and stateful shopping carts scaling across multi-region Kubernetes clusters.",
        ["Why are sticky sessions considered an anti-pattern in cloud-native Kubernetes deployments?", "What is session fixation and how does generating a new session ID upon login prevent it?"],
        ["Storing large objects (like database queries) in session dictionaries, causing Redis memory bloat.", "Forgetting to rotate the session ID upon user authentication (session fixation vulnerability)."],
        "Security rule: Always regenerate the session ID (`session_id = uuid4()`) immediately upon successful user login to defeat session fixation.",
        ["[Cookie Security](middleware-and-exception-handling.md)", "[Redis Caching](../06-redis-and-messaging/redis.md)"],
        ["https://owasp.org/www-community/attacks/Session_fixation"]
    ),

    # FA-ADV-171
    (
        "FA-ADV-171",
        "Chaos Engineering Middleware: Injecting Artificial Latency and Jitter in Staging",
        "Chaos engineering middleware injects configurable random latency, network timeouts, and artificial 500 errors in staging environments to verify system resilience.",
        "Services often behave well under low latency, but crash when downstream dependencies experience 3-second delays or intermittent 503 errors. Chaos middleware randomly injects faults based on configurable probabilities: 1) Latency injection: Adds 500ms to 3000ms delay with jitter using `asyncio.sleep()`; 2) Fault injection: Randomly returns HTTP 500 or 503 to 5% of requests. This tests whether frontend UI retry logic, circuit breakers, and timeouts handle degradation gracefully.",
        "import asyncio\nimport random\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Configure Chaos parameters (STAGING ONLY!)\nCHAOS_ENABLED = True\nERROR_RATE = 0.05       # 5% of requests will fail artificially\nMAX_JITTER_MS = 1500    # Up to 1.5s injected delay\n\n@app.middleware('http')\nasync def chaos_engineering_middleware(request: Request, call_next):\n    if CHAOS_ENABLED and request.url.path != '/healthz':\n        # 1. Inject artificial latency\n        delay = random.uniform(0.1, MAX_JITTER_MS / 1000.0)\n        await asyncio.sleep(delay)\n        \n        # 2. Inject artificial 500 failure\n        if random.random() < ERROR_RATE:\n            return JSONResponse(\n                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n                content={'error': 'CHAOS_INJECTED_FAILURE', 'message': 'Simulated chaos engineering fault'}\n            )\n            \n    return await call_next(request)",
        "Injecting simulated latency and random faults in staging environments using chaos middleware.",
        "By simulating production turbulence before deploying live, developers observe how clients handle slow responses and transient failures without risking live customer traffic.",
        "Continuous resilience verification, game-day disaster recovery exercises, and testing circuit breakers.",
        ["What is Chaos Engineering (Principles of Chaos)?", "Why must chaos injection middleware be strictly disabled in production environments?"],
        ["Accidentally deploying chaos middleware to production with `CHAOS_ENABLED=True`.", "Injecting blocking `time.sleep()` instead of non-blocking `await asyncio.sleep()` (freezes the entire event loop)."],
        "Crucial safety: Guard chaos middleware behind strict environment checks: `if os.getenv('ENVIRONMENT') != 'staging': return`.",
        ["[Resilience Architecture](../10-system-design/fundamentals.md)", "[Async Concurrency](async-and-concurrency.md)"],
        ["https://principlesofchaos.org/"]
    ),

    # FA-ADV-172
    (
        "FA-ADV-172",
        "Implementing Automated API Deprecation Headers (`Sunset`, `Deprecation`, `Link`)",
        "API deprecation middleware attaches standard RFC 8594 `Deprecation` and `Sunset` headers to deprecated routes, notifying clients of upcoming API decommissioning dates.",
        "Breaking changes require clear deprecation timelines. IETF RFC 8594 standardizes HTTP deprecation signaling: 1) `Deprecation: @<timestamp>`: Indicates the endpoint is deprecated; 2) `Sunset: <HTTP-Date>`: Declares the date when the endpoint will be permanently decommissioned; 3) `Link: <url>; rel=\"sunset\"`: Points to documentation explaining migration paths. Middleware inspects route paths or OpenAPI metadata to automatically inject these headers onto legacy routes.",
        "from fastapi import FastAPI, Request\n\napp = FastAPI()\n\nDEPRECATED_ROUTES = {\n    '/api/v1/users': {\n        'sunset_date': 'Wed, 11 Nov 2026 00:00:00 GMT',\n        'docs_url': 'https://api.example.com/docs/v2-migration'\n    }\n}\n\n@app.middleware('http')\nasync def api_deprecation_middleware(request: Request, call_next):\n    response = await call_next(request)\n    \n    route_info = DEPRECATED_ROUTES.get(request.url.path)\n    if route_info:\n        response.headers['Deprecation'] = 'true'\n        response.headers['Sunset'] = route_info['sunset_date']\n        response.headers['Link'] = f'<{route_info[\"docs_url\"]}>; rel=\"sunset\"'\n        \n    return response\n\n@app.get('/api/v1/users')\nasync def legacy_get_users():\n    return [{'id': 1, 'name': 'Legacy User'}]",
        "Injecting RFC 8594 Sunset and Deprecation headers onto legacy API endpoints.",
        "Automated client SDKs and monitoring tools parse `Sunset` and `Deprecation` headers, alerting engineering teams that they are calling deprecated endpoints long before breaking changes go live.",
        "Public API version transitions, migrating from v1 to v2 REST APIs, and partner deprecation notifications.",
        ["What are the standardized RFC 8594 headers for API deprecation?", "How does an HTTP client parse the `Sunset` header?"],
        ["Breaking legacy endpoints without prior deprecation headers or notice windows.", "Using non-standard custom headers like `X-API-Deprecated` instead of RFC 8594."],
        "State clearly: RFC 8594 defines `Deprecation` and `Sunset` headers for notifying API consumers of retirement schedules.",
        ["[API Versioning](../07-api-engineering/rest-api.md)", "[HTTP Headers](../07-api-engineering/http-and-https.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc8594"]
    ),

    # FA-ADV-173
    (
        "FA-ADV-173",
        "Advanced Profiling: Per-Middleware Latency Accounting and Flamegraph Generation",
        "Profiling middleware tracks the exact entry and exit timestamps of every middleware layer in the ASGI stack, attributing latency bottlenecks accurately.",
        "When an API endpoint exhibits a high P99 latency of 500ms, developers often blame database queries. However, the bottleneck may reside in middleware (e.g. slow JWT cryptographic verification, unindexed IP lookups, or synchronous logging). Advanced profiling middleware instruments each layer with monotonic performance counters, outputting a detailed breakdown in response headers (`Server-Timing`) or exporting metrics to profiling tools.",
        "import time\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def server_timing_profiling_middleware(request: Request, call_next):\n    start_time = time.perf_counter()\n    \n    # Simulate measuring auth stage\n    auth_start = time.perf_counter()\n    # Auth logic...\n    auth_duration = (time.perf_counter() - auth_start) * 1000\n    \n    response = await call_next(request)\n    \n    total_duration = (time.perf_counter() - start_time) * 1000\n    \n    # RFC Server-Timing header format\n    response.headers['Server-Timing'] = f'auth;dur={auth_duration:.2f}, total;dur={total_duration:.2f}'\n    return response\n\n@app.get('/metrics')\nasync def get_metrics():\n    return {'status': 'measured'}",
        "Recording per-stage execution durations and exposing them via RFC Server-Timing headers.",
        "Browsers and API profiling tools parse the `Server-Timing` header, displaying exact server-side timing bars in browser developer tools (Network tab) alongside network transit times.",
        "Diagnosing performance bottlenecks across complex microservice middleware pipelines.",
        ["What is the format of the W3C `Server-Timing` header?", "How can flamegraphs pinpoint CPU bottlenecks inside asynchronous Python coroutines?"],
        ["Enabling verbose CPU profilers like `cProfile` in high-traffic production (adds 20-40% CPU overhead).", "Blaming database queries for endpoint latency when JWT decoding middleware is the actual bottleneck."],
        "Tip: Use W3C `Server-Timing` headers to display server-side middleware timings directly in browser DevTools.",
        ["[Python Performance Optimization](../01-python/internals-and-performance.md)", "[Production Monitoring](production-and-performance.md)"],
        ["https://www.w3.org/TR/server-timing/"]
    ),

    # FA-ADV-174
    (
        "FA-ADV-174",
        "Custom ASGI Error Boundary Preventing Worker Crashes on C-Extension Faults",
        "An ASGI error boundary catches unhandled fatal C-extension or memory exceptions at the top level, preventing worker crashes from tearing down Uvicorn processes.",
        "When using compiled C-extensions (such as `ujson`, `cryptography`, or GIS libraries), low-level exceptions or unhandled C++ errors can escape standard Python `try/except` blocks, crashing the entire Uvicorn worker process and killing all other in-flight requests on that worker. A custom ASGI error boundary catches `BaseException` (including fatal system-level errors), logs diagnostic core dumps, and sends an emergency HTTP 500 response while keeping the worker alive.",
        "from starlette.types import ASGIApp, Scope, Receive, Send\nimport logging\nimport traceback\n\nlogger = logging.getLogger('kernel_boundary')\n\nclass KernelErrorBoundary:\n    def __init__(self, app: ASGIApp):\n        self.app = app\n\n    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:\n        try:\n            await self.app(scope, receive, send)\n        except BaseException as exc:\n            # Catch BaseException (including fatal system faults)\n            logger.critical(f'FATAL EXCEPTION BOUNDARY TRIGGERED: {exc}\\n{traceback.format_exc()}')\n            \n            if scope['type'] == 'http':\n                await send({\n                    'type': 'http.response.start',\n                    'status': 500,\n                    'headers': [(b'content-type', b'text/plain')],\n                })\n                await send({\n                    'type': 'http.response.body',\n                    'body': b'Fatal Server Crash Intercepted by Kernel Boundary',\n                    'more_body': False,\n                })\n            # Only re-raise if it is an explicit SystemExit or KeyboardInterrupt\n            if isinstance(exc, (SystemExit, KeyboardInterrupt)):\n                raise",
        "Intercepting fatal BaseException crashes at the root ASGI boundary to prevent worker termination.",
        "By placing this boundary at the absolute root of the ASGI chain, fatal exceptions that would otherwise terminate the process are caught, an emergency response is dispatched to the client, and the worker process survives to serve other concurrent requests.",
        "High-reliability backend services leveraging native C/Rust extensions (Pydantic Core, cryptography, OpenCV).",
        ["What is the difference between catching `Exception` and catching `BaseException` in Python?", "Why must `KeyboardInterrupt` and `SystemExit` always be re-raised?"],
        ["Swallowing `KeyboardInterrupt` or `SystemExit`, preventing Docker containers or Kubernetes from shutting down cleanly.", "Assuming Python `try/except` can catch actual operating system Segmentation Faults (SIGSEGV requires signal handlers)."],
        "Caution: Always re-raise `SystemExit` and `KeyboardInterrupt` so container orchestrators can shut down pods gracefully.",
        ["[Python Exception Handling](../01-python/fundamentals.md)", "[Production Deployment](production-and-performance.md)"],
        ["https://docs.python.org/3/library/exceptions.html#base-classes"]
    ),

    # FA-ADV-175
    (
        "FA-ADV-175",
        "Architecting Zero-Trust Perimeter Defense: mTLS Header Verification, WAF Integration, and Request Signing",
        "Zero-trust middleware verifies cryptographic request signatures (HMAC-SHA256) and mTLS client certificate headers injected by perimeter API gateways before processing requests.",
        "In zero-trust architecture, internal microservices do not trust requests simply because they originate from inside the private network. Perimeter defense middleware enforces: 1) HMAC Request Signature verification: Verifies `X-Signature` computed using a shared secret and timestamp to defeat replay attacks; 2) Client Certificate validation: Inspects `X-Client-Cert-SHA256` injected by the mTLS reverse proxy; 3) Replay protection: Rejects requests with timestamps older than 300 seconds.",
        "import hmac\nimport hashlib\nimport time\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\nHMAC_SECRET = b'enterprise-internal-signing-secret'\n\n@app.middleware('http')\nasync def zero_trust_security_middleware(request: Request, call_next):\n    # 1. Verify Request Timestamp (Replay Attack Defense)\n    timestamp = request.headers.get('x-timestamp')\n    if not timestamp or abs(time.time() - float(timestamp)) > 300:\n        return JSONResponse(status_code=401, content={'error': 'TIMESTAMP_INVALID_OR_EXPIRED'})\n        \n    # 2. Verify Cryptographic HMAC Signature\n    signature = request.headers.get('x-signature')\n    body_bytes = await request.body()\n    expected_sig = hmac.new(\n        HMAC_SECRET,\n        f'{request.method}{request.url.path}{timestamp}'.encode() + body_bytes,\n        hashlib.sha256\n    ).hexdigest()\n    \n    if not hmac.compare_digest(signature or '', expected_sig):\n        return JSONResponse(status_code=403, content={'error': 'INVALID_REQUEST_SIGNATURE'})\n        \n    # Replay request body for downstream route handlers\n    async def receive():\n        return {'type': 'http.request', 'body': body_bytes, 'more_body': False}\n        \n    return await call_next(Request(request.scope, receive))",
        "Enforcing HMAC request signatures and replay protection in zero-trust perimeter middleware.",
        "`hmac.compare_digest` performs constant-time comparison to prevent timing attacks. Combining the HTTP method, path, timestamp, and body into the HMAC digest guarantees that neither the payload nor the routing parameters were tampered with in transit.",
        "Inter-service banking gateways, payment webhooks, and military/financial zero-trust microservice meshes.",
        ["What is a timing attack on string comparison, and why is `hmac.compare_digest` mandatory?", "How does checking request timestamps prevent replay attacks?"],
        ["Using standard `==` equality for HMAC signature verification, exposing the service to timing side-channel attacks.", "Failing to include the request body in the HMAC signature, allowing attackers to modify payloads while preserving the signature."],
        "Security essential: Always use `hmac.compare_digest()` for cryptographic comparisons and include request timestamps to stop replay attacks.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://en.wikipedia.org/wiki/Zero_trust_security_model"]
    ),
]
