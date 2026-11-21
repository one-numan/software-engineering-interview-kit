"""
fa_prod_basic.py
================
Basic FastAPI Production & Performance Questions: FA-BAS-176 to FA-BAS-200 (25 questions)
"""

basic_data = [
    # FA-BAS-176
    (
        "FA-BAS-176",
        "Running FastAPI in Production: Uvicorn vs Gunicorn with `UvicornWorker`",
        "In production, Gunicorn acts as a process manager overseeing multiple Uvicorn worker processes (`UvicornWorker`), combining process-level resilience with async event loop performance.",
        "While running `uvicorn main:app --workers 4` works for simple deployments, production enterprise environments pair Gunicorn with Uvicorn. Gunicorn acts as a master process manager: it handles OS signal management (SIGHUP, SIGTERM), worker process health monitoring, graceful rolling restarts on code changes, and automatic respawning if an individual worker process crashes due to an unhandled segfault or out-of-memory error. Each worker runs Uvicorn's async event loop (`UvicornWorker`), executing thousands of concurrent requests on each CPU core.",
        "# Running Gunicorn with Uvicorn worker class via CLI\n# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000\n\n# Or using standard Uvicorn in containerized Kubernetes pods:\n# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/health')\nasync def health():\n    return {'status': 'healthy', 'server': 'gunicorn+uvicorn'}",
        "Configuring Gunicorn with UvicornWorker for production process management and resilience.",
        "Gunicorn's master process listens on the binding socket (`0.0.0.0:8000`) and forks worker processes. Incoming socket connections are accepted by worker processes running Uvicorn's event loop via the `uvloop` engine. If a worker dies, Gunicorn immediately forks a replacement worker.",
        "Production API services deployed on Linux virtual machines, EC2 instances, and bare-metal servers.",
        ["Why is running `uvicorn main:app --reload` dangerous in production?", "In a Kubernetes pod, should you run Gunicorn with 4 workers or 1 Uvicorn worker per container?"],
        ["Running `uvicorn --reload` in production (reload consumes heavy CPU, watches files, and creates security risks).", "Setting worker counts too high on memory-constrained servers, causing Linux kernel OOM kills."],
        "Explain: Gunicorn provides process lifecycle management; Uvicorn provides async ASGI event loop performance.",
        ["[Gunicorn & Uvicorn](../11-devops/gunicorn-and-uvicorn.md)", "[ASGI Architecture](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/deployment/server-workers/"]
    ),

    # FA-BAS-177
    (
        "FA-BAS-177",
        "What is an ASGI Server and Why is Uvicorn Needed?",
        "An ASGI server translates low-level network socket protocols (HTTP/1.1, HTTP/2, WebSockets) into asynchronous Python dictionaries that FastAPI can process.",
        "Python web frameworks do not speak raw TCP sockets directly; they adhere to gateway interface standards. WSGI (Web Server Gateway Interface) was strictly synchronous, processing one request per thread. ASGI (Asynchronous Server Gateway Interface) is the asynchronous successor designed for Python coroutines. Uvicorn is a lightning-fast ASGI server built on `uvloop` (an ultra-fast libuv event loop) and `httptools` (Node.js HTTP parser). Uvicorn handles socket handshakes, TLS termination, and HTTP parsing, forwarding events to FastAPI via `app(scope, receive, send)`.",
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/info')\nasync def get_info():\n    return {\n        'framework': 'FastAPI',\n        'gateway_standard': 'ASGI 3.0',\n        'server': 'Uvicorn (uvloop + httptools)'\n    }\n\n# Programmatic server startup (for local development/debugging only)\nif __name__ == '__main__':\n    import uvicorn\n    uvicorn.run(app, host='127.0.0.1', port=8000)",
        "Demonstrating FastAPI's relationship with Uvicorn and ASGI standard.",
        "Uvicorn listens on the OS network socket using C-level `libuv` bindings. When HTTP packets arrive, `httptools` parses headers in C memory and constructs the ASGI `scope`. FastAPI receives the scope, evaluates routes, and streams response bytes back to Uvicorn.",
        "Powering all modern async Python web applications, WebSockets, and real-time event streaming services.",
        ["How does ASGI differ fundamentally from legacy WSGI?", "What C-libraries make Uvicorn significantly faster than pure-Python servers?"],
        ["Attempting to serve FastAPI applications using WSGI servers like legacy Gunicorn sync workers or uWSGI (they cannot await coroutines).", "Calling `uvicorn.run()` inside production Docker containers instead of using the CLI entrypoint."],
        "Remember: WSGI is synchronous (one thread per request); ASGI is asynchronous (one event loop for thousands of concurrent requests).",
        ["[ASGI vs WSGI](fundamentals.md)", "[Event Loops](../01-python/concurrency-and-parallelism.md)"],
        ["https://www.uvicorn.org/"]
    ),

    # FA-BAS-178
    (
        "FA-BAS-178",
        "Configuring Uvicorn with Command-Line Flags (`--host`, `--port`, `--workers`, `--proxy-headers`)",
        "Uvicorn is configured via CLI flags to bind network interfaces (`--host 0.0.0.0`), set ports (`--port 8000`), define concurrency (`--workers`), and trust reverse proxies (`--proxy-headers`).",
        "When launching FastAPI in Docker or production environments, critical Uvicorn flags include: 1) `--host 0.0.0.0`: Binds to all network interfaces (mandatory for Docker containers to be reachable externally); 2) `--port 8000`: Sets listening port; 3) `--workers N`: Sets number of worker processes; 4) `--proxy-headers`: Instructs Uvicorn to trust `X-Forwarded-For` and `X-Forwarded-Proto` headers from Nginx or AWS ALB; 5) `--forwarded-allow-ips`: Restricts which proxy IPs are trusted.",
        "# Production Uvicorn startup command inside Docker container\n# uvicorn app.main:app \\\n#   --host 0.0.0.0 \\\n#   --port 8000 \\\n#   --workers 4 \\\n#   --proxy-headers \\\n#   --forwarded-allow-ips='*' \\\n#   --timeout-keep-alive 5 \\\n#   --no-access-log\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/ping')\nasync def ping():\n    return {'status': 'pong'}",
        "Standard production CLI configuration flags for Uvicorn.",
        "Binding to `0.0.0.0` ensures the container bridge network forwards incoming packets into the container. `--proxy-headers` causes Uvicorn to parse `X-Forwarded-Proto` and set `scope['scheme'] = 'https'`, preventing redirect loops.",
        "Docker container entrypoints in AWS ECS, GCP Cloud Run, and Kubernetes pods.",
        ["Why does binding to `127.0.0.1` inside a Docker container make the app unreachable from the host?", "What security risk arises if `--proxy-headers` is enabled without restricting `--forwarded-allow-ips`?"],
        ["Binding to `localhost` or `127.0.0.1` inside Docker containers instead of `0.0.0.0`.", "Leaving `--reload` enabled in production Uvicorn startup commands."],
        "Always use `--host 0.0.0.0` inside containers and enable `--proxy-headers` behind reverse proxies.",
        ["[Docker Configuration](../11-devops/docker.md)", "[Reverse Proxies](../11-devops/nginx.md)"],
        ["https://www.uvicorn.org/settings/"]
    ),

    # FA-BAS-179
    (
        "FA-BAS-179",
        "Production Containerization: Writing a Dockerfile for FastAPI",
        "A production Dockerfile builds a self-contained Linux container running FastAPI with pinned dependencies, non-root user execution, and an optimized entrypoint.",
        "Containerization standardizes deployments across development, staging, and cloud production. A standard single-stage production Dockerfile uses official slim Python images (e.g. `python:3.11-slim`), sets environment variables to disable Python bytecode cache and buffering, installs dependencies with pip cache purging, copies source code, creates a non-root user for security, and launches Uvicorn.",
        "# Sample Production Dockerfile for FastAPI\n\"\"\"\nFROM python:3.11-slim\n\n# Prevent Python from writing .pyc files and enable unbuffered logging\nENV PYTHONDONTWRITEBYTECODE=1 \\\n    PYTHONUNBUFFERED=1\n\nWORKDIR /app\n\n# Install dependencies first to leverage Docker layer caching\nCOPY requirements.txt .\nRUN pip install --no-cache-dir --upgrade pip && \\\n    pip install --no-cache-dir -r requirements.txt\n\n# Copy application code\nCOPY . .\n\n# Run as non-privileged user for security hardening\nRUN useradd -m appuser && chown -R appuser:appuser /app\nUSER appuser\n\nEXPOSE 8000\n\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n\"\"\"",
        "Standard production Dockerfile for FastAPI with layer caching, unbuffered logging, and non-root execution.",
        "Docker caches intermediate build layers. By copying `requirements.txt` and running `pip install` before copying the rest of the source code, Docker only re-installs dependencies when `requirements.txt` changes, speeding up CI/CD builds significantly.",
        "Standard deployment artifact for Kubernetes, AWS ECS, Google Cloud Run, and Azure Container Apps.",
        ["Why should `COPY requirements.txt .` precede `COPY . .` in a Dockerfile?", "Why is running containers as `USER root` considered a security hazard?"],
        ["Running `pip install` after copying all source code, which invalidates the pip cache on every code edit.", "Omitting `PYTHONUNBUFFERED=1`, causing print and log statements to be delayed or lost during crashes."],
        "Always set `PYTHONUNBUFFERED=1` so log entries flush immediately to Docker/Kubernetes log collectors.",
        ["[Docker Fundamentals](../11-devops/docker.md)", "[Security Best Practices](../12-security/application-security.md)"],
        ["https://fastapi.tiangolo.com/deployment/docker/"]
    ),

    # FA-BAS-180
    (
        "FA-BAS-180",
        "Unit Testing FastAPI Endpoints Using `TestClient` from Starlette",
        "`TestClient` (built on `httpx`) allows executing synchronous unit tests against FastAPI applications without running a live HTTP network server.",
        "FastAPI provides `TestClient`, imported from `fastapi.testclient` (which wraps `httpx.Client`). It simulates HTTP requests against the FastAPI ASGI application directly in memory. You can test status codes, JSON responses, headers, and cookies synchronously using standard `pytest` assertions without binding a TCP socket port.",
        "from fastapi import FastAPI\nfrom fastapi.testclient import TestClient\nimport pytest\n\napp = FastAPI()\n\n@app.get('/items/{item_id}')\nasync def get_item(item_id: int):\n    return {'item_id': item_id, 'available': True}\n\n# Instantiate synchronous TestClient\nclient = TestClient(app)\n\ndef test_read_item():\n    response = client.get('/items/42')\n    assert response.status_code == 200\n    assert response.json() == {'item_id': 42, 'available': True}\n\ndef test_read_item_invalid_type():\n    response = client.get('/items/invalid-string')\n    assert response.status_code == 422  # Pydantic validation failure",
        "Writing synchronous unit tests for FastAPI routes using TestClient and pytest.",
        "`TestClient` implements Starlette's ASGI in-memory transport. When `client.get()` executes, it constructs the ASGI `scope` and invokes `app(scope, receive, send)` synchronously inside an event loop managed by httpx, returning a standard `httpx.Response`.",
        "Unit test suites running in CI/CD pipelines validating route endpoints, response contracts, and validation errors.",
        ["Why doesn't `TestClient` require binding to an actual TCP port like 8000?", "What library does modern `TestClient` use under the hood in FastAPI (`httpx`)?"],
        ["Spinning up a live Uvicorn subprocess just to run simple unit tests.", "Testing async route handlers directly with function calls (`await get_item(42)`) rather than testing through the HTTP transport layer."],
        "Use `TestClient` for fast, simple unit tests; use `AsyncClient` when testing async context managers, lifespans, or database fixtures.",
        ["[Async Testing](production-and-performance.md)", "[Testing Fixtures](testing.md)"],
        ["https://fastapi.tiangolo.com/tutorial/testing/"]
    ),

    # FA-BAS-181
    (
        "FA-BAS-181",
        "Asynchronous Testing with `httpx.AsyncClient` and `pytest-asyncio`",
        "`httpx.AsyncClient` paired with `pytest-asyncio` allows writing asynchronous tests that natively await async database sessions, lifespan events, and FastAPI routes.",
        "While `TestClient` is synchronous, production integration tests frequently interact with asynchronous fixtures (such as async SQLAlchemy sessions, Redis clients, or lifespan setup). Using `pytest.mark.asyncio` with `httpx.AsyncClient(transport=ASGITransport(app=app), base_url='http://test')` allows tests to be written with `async def` and `await`, matching the application's native async concurrency model.",
        "import pytest\nfrom fastapi import FastAPI\nfrom httpx import AsyncClient, ASGITransport\n\napp = FastAPI()\n\n@app.get('/async-hello')\nasync def async_hello():\n    return {'message': 'Hello Async World'}\n\n@pytest.mark.asyncio\nasync def test_async_endpoint():\n    # Test using native async httpx client with ASGI transport\n    transport = ASGITransport(app=app)\n    async with AsyncClient(transport=transport, base_url='http://test') as ac:\n        response = await ac.get('/async-hello')\n        assert response.status_code == 200\n        assert response.json() == {'message': 'Hello Async World'}",
        "Executing asynchronous integration tests using httpx.AsyncClient and ASGITransport.",
        "`ASGITransport` intercepts HTTP calls and dispatches them directly to the ASGI callable on the active asyncio event loop. This allows concurrent async operations and async database transactions to share the same event loop in test suites.",
        "Testing database integration endpoints, WebSocket interactions, and asynchronous lifespan hooks.",
        ["What is `ASGITransport` in modern `httpx`?", "Why does `app=app` argument in `AsyncClient` require `transport=ASGITransport(app=app)` in httpx >= 0.25.0?"],
        ["Passing `app=app` directly to `AsyncClient()` in httpx >= 0.25.0 (deprecated; must use `transport=ASGITransport(app=app)`).", "Forgetting the `@pytest.mark.asyncio` decorator, causing pytest to skip or fail async test functions."],
        "Note: In modern `httpx`, always use `AsyncClient(transport=ASGITransport(app=app), base_url='http://test')`.",
        ["[Unit Testing](production-and-performance.md)", "[Database Integration](database-integration.md)"],
        ["https://fastapi.tiangolo.com/advanced/async-tests/"]
    ),

    # FA-BAS-182
    (
        "FA-BAS-182",
        "Health Check Probes: Implementing `/healthz`, `/livez`, and `/readyz` Endpoints",
        "Health check endpoints allow container orchestrators (Kubernetes, AWS ECS) to monitor container lifecycle: liveness (`/livez`) checks if the process is alive; readiness (`/readyz`) checks if dependencies are ready.",
        "Container platforms require automated probes to manage application traffic and restart crashed pods: 1) Liveness Probe (`/livez` or `/healthz`): Returns HTTP 200 if the FastAPI process is running. If it fails or times out, Kubernetes restarts the container; 2) Readiness Probe (`/readyz`): Verifies whether external dependencies (PostgreSQL, Redis, RabbitMQ) are reachable and healthy. If it fails, Kubernetes stops routing incoming user traffic to this pod until it recovers.",
        "from fastapi import FastAPI, Response, status\n\napp = FastAPI()\n\n@app.get('/livez', tags=['Health'])\nasync def liveness_probe():\n    # Pure process liveness check (does NOT touch DB)\n    return {'status': 'alive'}\n\n@app.get('/readyz', tags=['Health'])\nasync def readiness_probe():\n    # Readiness check: Verify external dependencies\n    db_healthy = True  # In production: await check_database_connection()\n    redis_healthy = True  # In production: await check_redis_ping()\n    \n    if not (db_healthy and redis_healthy):\n        return Response(\n            content='Dependencies Unavailable',\n            status_code=status.HTTP_503_SERVICE_UNAVAILABLE\n        )\n    return {'status': 'ready', 'database': 'ok', 'cache': 'ok'}",
        "Implementing distinct liveness (/livez) and readiness (/readyz) probes in FastAPI.",
        "Kubernetes periodically executes HTTP GET requests against these endpoints. Liveness probes are intentionally lightweight (no external I/O) to prevent unnecessary container restart loops if the database experiences high load.",
        "Standard deployment configuration in Kubernetes pod manifests, AWS ALB target groups, and Cloud Run health checks.",
        ["Why should a liveness probe NEVER query the database?", "What happens if a readiness probe returns HTTP 503?"],
        ["Checking database connectivity inside `/livez` (if the database experiences a brief spike, Kubernetes restarts all app pods simultaneously, worsening the outage).", "Adding authentication requirements to health check endpoints, preventing orchestrators from probing them."],
        "Critical rule: Liveness probe checks ONLY the local process; Readiness probe checks external dependencies.",
        ["[Kubernetes Probes](../11-devops/deployment-and-troubleshooting.md)", "[Database Integration](database-integration.md)"],
        ["https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"]
    ),

    # FA-BAS-183
    (
        "FA-BAS-183",
        "Configuring Application Metadata: `FastAPI(title, version, docs_url)`",
        "FastAPI metadata parameters configure the public documentation title, versioning, description, license, and OpenAPI URL endpoints.",
        "When initializing `FastAPI()`, passing configuration arguments personalizes the auto-generated Swagger UI and OpenAPI specification: `title` (application name), `version` (SemVer API version), `description` (Markdown summary), `terms_of_service`, `contact`, and `license_info`. You can also customize the URLs where Swagger UI (`docs_url`) and ReDoc (`redoc_url`) are mounted.",
        "from fastapi import FastAPI\n\napp = FastAPI(\n    title='Order Management Microservice',\n    description='Enterprise REST API for inventory, orders, and payment webhooks.',\n    version='2.4.1',\n    docs_url='/api/docs',      # Custom Swagger UI path\n    redoc_url='/api/redoc',    # Custom ReDoc path\n    openapi_url='/api/v1/openapi.json',  # OpenAPI JSON schema location\n    contact={\n        'name': 'API Support Team',\n        'email': 'support@example.com',\n    },\n)\n\n@app.get('/version')\nasync def get_version():\n    return {'version': app.version}",
        "Configuring production metadata and custom documentation paths in FastAPI.",
        "FastAPI compiles these attributes into the generated OpenAPI 3.1 JSON schema, rendering professional headers, documentation summaries, and contact links in Swagger UI.",
        "Enterprise public APIs, developer portals, and cross-team microservice documentation.",
        ["How does updating the `version` string in `FastAPI` affect client SDK generators?", "What OpenAPI schema version does modern FastAPI generate (OpenAPI 3.1)?"],
        ["Hardcoding documentation URLs in code without allowing overrides via environment variables.", "Leaving generic 'FastAPI' titles on enterprise production APIs."],
        "Take pride in API documentation: Configure clear `title`, `version`, and `description` strings on every service.",
        ["[OpenAPI Specs](fundamentals.md)", "[Swagger UI](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/metadata/"]
    ),

    # FA-BAS-184
    (
        "FA-BAS-184",
        "Disabling OpenAPI and Swagger UI Documentation in Production",
        "Interactive documentation endpoints can be completely disabled in production by passing `docs_url=None`, `redoc_url=None`, and `openapi_url=None`.",
        "While Swagger UI (`/docs`) and ReDoc (`/redoc`) are invaluable during development, exposing interactive documentation on public production APIs can expose private endpoints, internal schemas, and parameter models to attackers. Setting these configuration parameters to `None` in production removes the documentation routes entirely, reducing the attack surface.",
        "import os\nfrom fastapi import FastAPI\n\n# Enable interactive docs ONLY in local/staging environments\nIS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'\n\napp = FastAPI(\n    docs_url=None if IS_PRODUCTION else '/docs',\n    redoc_url=None if IS_PRODUCTION else '/redoc',\n    openapi_url=None if IS_PRODUCTION else '/openapi.json',\n)\n\n@app.get('/data')\nasync def get_data():\n    return {'status': 'secure_in_production'}",
        "Conditionally disabling Swagger UI, ReDoc, and openapi.json in production environments.",
        "When `docs_url=None`, FastAPI does not register the Starlette HTML route handler for Swagger UI. Any request to `/docs` returns HTTP 404 Not Found.",
        "Fintech backends, banking APIs, internal microservices, and compliance-hardened production environments.",
        ["Why is exposing `openapi.json` considered an information disclosure risk in production?", "How can you protect Swagger UI with HTTP Basic Auth instead of disabling it completely?"],
        ["Disabling `docs_url` but forgetting `openapi_url`, leaving the raw JSON schema accessible at `/openapi.json`.", "Hardcoding `docs_url=None` without checking environment variables, making local developer testing frustrating."],
        "Security best practice: Disable `docs_url`, `redoc_url`, AND `openapi_url` in production, or guard them behind authentication.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Authentication](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/metadata/#conditional-openapi-from-environment"]
    ),

    # FA-BAS-185
    (
        "FA-BAS-185",
        "Setting Request Keep-Alive Timeouts in Uvicorn (`--timeout-keep-alive`)",
        "`--timeout-keep-alive` defines how long an idle HTTP connection remains open awaiting subsequent requests, balancing connection reuse latency against socket exhaustion.",
        "HTTP Keep-Alive allows clients to reuse open TCP connections across multiple HTTP requests, eliminating TLS handshake latency. However, if clients open connections and leave them idle, server connection pools can become exhausted. Uvicorn's `--timeout-keep-alive` (default 5 seconds) closes idle connections after the specified duration. In production behind load balancers (like AWS ALB), Uvicorn's keep-alive timeout MUST be configured slightly higher than the load balancer's idle timeout to prevent 502 Bad Gateway race conditions.",
        "# Running Uvicorn with explicit keep-alive timeout\n# uvicorn main:app --timeout-keep-alive 65\n\n# Behind AWS ALB (ALB default timeout is 60s -> Uvicorn must be 65s)\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/ping')\nasync def ping():\n    return {'status': 'pong'}",
        "Configuring Uvicorn keep-alive timeouts to coordinate with upstream load balancers.",
        "Uvicorn sets an internal timer on the socket when a request completes. If no incoming data packet arrives within `--timeout-keep-alive` seconds, Uvicorn sends a TCP FIN packet to cleanly close the connection.",
        "Production deployments operating behind AWS Application Load Balancers, Cloudflare, or Nginx.",
        ["Why does setting Uvicorn's keep-alive timeout lower than AWS ALB's timeout cause intermittent 502 Bad Gateway errors?", "What is the performance advantage of HTTP Keep-Alive for mobile clients?"],
        ["Setting keep-alive timeout to 0 (forces every request to establish a new TCP and TLS handshake, adding 50-100ms latency).", "Setting keep-alive timeout too high (e.g. 300s) on public-facing servers without load balancers, risking connection exhaustion."],
        "AWS ALB Golden Rule: Set Uvicorn's `--timeout-keep-alive` to 65 seconds (higher than ALB's default 60 seconds).",
        ["[AWS ALB Configuration](../11-devops/aws.md)", "[Nginx Optimization](../11-devops/nginx.md)"],
        ["https://www.uvicorn.org/settings/#timeouts"]
    ),

    # FA-BAS-186
    (
        "FA-BAS-186",
        "Logging Best Practices in Production: JSON Structured Logging vs `print()`",
        "Production logging requires structured JSON logging (using `structlog` or `python-json-logger`) rather than plaintext `print()`, enabling automated filtering and parsing in log aggregators.",
        "Using `print()` statements in production code is an anti-pattern: it lacks log levels (INFO, WARNING, ERROR), contains no timestamps, is not machine-readable, and cannot be parsed reliably by log aggregators (Elasticsearch, Datadog, AWS CloudWatch). Structured JSON logging outputs a single JSON object per log line containing `timestamp`, `level`, `message`, `correlation_id`, and contextual metadata, enabling instant querying (e.g. `level: ERROR AND tenant_id: 42`).",
        "import logging\nimport json\nfrom datetime import datetime, timezone\nfrom fastapi import FastAPI\n\nclass JSONFormatter(logging.Formatter):\n    def format(self, record: logging.LogRecord) -> str:\n        log_entry = {\n            'timestamp': datetime.now(timezone.utc).isoformat(),\n            'level': record.levelname,\n            'message': record.getMessage(),\n            'logger': record.name,\n            'module': record.module,\n        }\n        if hasattr(record, 'extra_data'):\n            log_entry['extra'] = record.extra_data\n        return json.dumps(log_entry)\n\n# Configure logger\nlogger = logging.getLogger('production_api')\nhandler = logging.StreamHandler()\nhandler.setFormatter(JSONFormatter())\nlogger.addHandler(handler)\nlogger.setLevel(logging.INFO)\n\napp = FastAPI()\n\n@app.get('/order')\nasync def create_order():\n    logger.info('Processing order', extra={'extra_data': {'order_id': 101, 'amount': 49.99}})\n    return {'status': 'success'}",
        "Implementing a structured JSON logging formatter for production log aggregators.",
        "The formatter intercepts standard Python `logging.LogRecord` objects, builds a dictionary, and converts it to a compact single-line JSON string written to stdout. Cloud log drivers (Docker `json-file`, AWS FluentBit) stream these JSON events directly to storage.",
        "Enterprise cloud monitoring, security audit trails, and automated error alerting systems.",
        ["Why is multiline plaintext logging problematic for container log aggregators like FluentBit?", "What are the advantages of using `structlog` over standard library logging in Python?"],
        ["Using `print()` in production code (cannot be filtered by severity level).", "Logging unstructured strings with string interpolation (`logger.info(f'User {uid} logged in')`), preventing aggregation by user ID."],
        "Emphasize: Always output structured JSON to stdout in containerized environments.",
        ["[Logging Middleware](middleware-and-exception-handling.md)", "[Monitoring & Logging](../11-devops/monitoring-and-logging.md)"],
        ["https://docs.python.org/3/library/logging.html"]
    ),

    # FA-BAS-187
    (
        "FA-BAS-187",
        "Graceful Shutdown Handling in Uvicorn (`--timeout-graceful-shutdown`)",
        "Graceful shutdown allows active in-flight HTTP requests to complete before terminating the server process, preventing aborted transactions during deployments.",
        "When Kubernetes or Docker stops a container during a rolling deployment, it sends a `SIGTERM` signal. If the server terminates immediately, active user requests are severed, database transactions are aborted, and clients receive connection reset errors. Uvicorn supports graceful shutdown: upon receiving `SIGTERM`, it stops accepting *new* connections and allows active requests up to `--timeout-graceful-shutdown` (default 30 seconds) to finish. If requests are still running after the timeout, Uvicorn forces termination.",
        "from contextlib import asynccontextmanager\nfrom fastapi import FastAPI\nimport asyncio\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    # Startup\n    print('Application booted and ready for traffic')\n    yield\n    # Graceful Shutdown cleanup\n    print('SIGTERM received: Draining background tasks and closing DB connections...')\n    await asyncio.sleep(0.5)  # Flush queues, close threadpools\n    print('Cleanup complete. Safe to terminate.')\n\napp = FastAPI(lifespan=lifespan)\n\n@app.get('/long-op')\nasync def long_op():\n    await asyncio.sleep(2)  # In-flight request will finish during graceful shutdown\n    return {'status': 'completed'}",
        "Coordinating application lifespan cleanup with Uvicorn's graceful shutdown process.",
        "Uvicorn catches the OS `SIGTERM` signal, pauses socket listening, and enters a draining loop. It awaits active coroutine tasks up to the timeout duration, executes FastAPI's lifespan shutdown phase, and terminates with exit code 0.",
        "Kubernetes rolling updates, zero-downtime deployments, and cloud autoscaling downscaling events.",
        ["What is the difference between `SIGTERM` and `SIGKILL`?", "How does Kubernetes `terminationGracePeriodSeconds` coordinate with Uvicorn's `--timeout-graceful-shutdown`?"],
        ["Setting container `terminationGracePeriodSeconds` shorter than Uvicorn's graceful shutdown timeout (Kubernetes kills the pod prematurely with SIGKILL).", "Holding long-lived WebSocket connections open indefinitely during shutdown without a disconnection timeout."],
        "Configure: Ensure Kubernetes `terminationGracePeriodSeconds` (e.g. 45s) is greater than Uvicorn's `--timeout-graceful-shutdown` (e.g. 30s).",
        ["[Lifespan Context Manager](async-and-concurrency.md)", "[Kubernetes Deployments](../11-devops/deployment-and-troubleshooting.md)"],
        ["https://www.uvicorn.org/settings/#timeouts"]
    ),

    # FA-BAS-188
    (
        "FA-BAS-188",
        "Managing Production Secrets with Environment Variables and `.env` Files",
        "Production secrets (database passwords, API keys, JWT secrets) must be loaded from system environment variables using `pydantic-settings`, never committed to source control.",
        "Hardcoding secrets in source files exposes infrastructure to compromise if repositories are leaked. In FastAPI, `pydantic-settings` defines a strongly typed configuration schema that reads from system environment variables with optional fallback to a local `.env` file during development. In production Kubernetes or AWS environments, secrets are mounted into environment variables securely via cloud secret managers (AWS Secrets Manager, HashiCorp Vault).",
        "from pydantic_settings import BaseSettings, SettingsConfigDict\nfrom pydantic import SecretStr\n\nclass AppSettings(BaseSettings):\n    ENVIRONMENT: str = 'production'\n    DATABASE_URL: SecretStr\n    JWT_SECRET_KEY: SecretStr\n    REDIS_HOST: str = 'localhost'\n    REDIS_PORT: int = 6379\n\n    model_config = SettingsConfigDict(env_file='.env', extra='ignore')\n\n# Instantiate singleton configuration\n# In production, SecretStr masks values in logs: repr(settings.DATABASE_URL) -> '**********'\nsettings = AppSettings(DATABASE_URL='sqlite+aiosqlite:///:memory:', JWT_SECRET_KEY='supersecret')",
        "Using pydantic-settings with SecretStr to prevent credential leakage in logs.",
        "`SecretStr` wraps string values so that calling `str(secret)` or printing the settings object displays `'**********'`, preventing accidental exposure in tracebacks, log files, or terminal outputs.",
        "Twelve-Factor App compliant microservice configuration in Kubernetes, AWS ECS, and Docker Swarm.",
        ["What is the benefit of `SecretStr` over standard `str` in Pydantic?", "Why should `.env` files be added to `.gitignore`?"],
        ["Committing `.env` files containing production passwords to GitHub.", "Accessing raw `os.environ` throughout codebase modules instead of a centralized, validated `pydantic-settings` class."],
        "Rule of thumb: Centralize all secrets in a `Settings` class using `SecretStr` and validate them at application boot.",
        ["[Pydantic Settings](pydantic-and-validation.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://docs.pydantic.dev/latest/concepts/pydantic_settings/"]
    ),

    # FA-BAS-189
    (
        "FA-BAS-189",
        "Serving Static Files with `StaticFiles` in FastAPI",
        "FastAPI serves static assets (CSS, JavaScript, images, frontend SPAs) by mounting Starlette's `StaticFiles` handler onto an application prefix via `app.mount()`.",
        "While production systems typically offload static assets to a CDN or Nginx, small internal tools, developer dashboards, and single-container deployments often require FastAPI to serve static files directly. FastAPI provides `StaticFiles` from `fastapi.staticfiles`. Mounting it maps a local filesystem directory (e.g. `static/`) to a URL path (e.g. `/static`).",
        "import os\nfrom fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles\n\napp = FastAPI()\n\n# Ensure static directory exists\nos.makedirs('static', exist_ok=True)\nwith open('static/app.js', 'w') as f:\n    f.write('console.log(\"FastAPI static asset loaded\");')\n\n# Mount static files directory onto /static URL prefix\napp.mount('/static', StaticFiles(directory='static'), name='static')\n\n@app.get('/')\nasync def index():\n    return {'message': 'Visit /static/app.js to view the static file'}",
        "Mounting a static directory onto /static URL prefix using StaticFiles.",
        "`StaticFiles` implements an ASGI application that parses HTTP `Range` headers, handles ETag and `Last-Modified` caching, determines MIME types automatically using Python's `mimetypes` library, and streams file bytes asynchronously.",
        "Serving Single Page Application (SPA) index.html bundles, Swagger UI local offline assets, and favicon files.",
        ["Why is serving static files through Nginx or AWS S3/CloudFront faster than serving through FastAPI in high-traffic production?", "What happens if a requested file in `StaticFiles` does not exist (404)?"],
        ["Using FastAPI routes with `FileResponse` for thousands of static image requests instead of mounting `StaticFiles` or using Nginx.", "Directory traversal risks if mounting raw root directories without path sandboxing."],
        "Emphasize: For high-traffic consumer websites, offload static asset delivery to Nginx or a CDN like Cloudflare/CloudFront.",
        ["[Nginx File Serving](../11-devops/nginx.md)", "[Static Files](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/static-files/"]
    ),

    # FA-BAS-190
    (
        "FA-BAS-190",
        "Mounting Sub-Applications Using `app.mount()`",
        "`app.mount()` mounts an independent ASGI or WSGI application (such as another FastAPI app, Starlette app, or Gradio dashboard) under a dedicated URL sub-path.",
        "Unlike `APIRouter` (which merges endpoints into the parent application's routing table and OpenAPI schema), `app.mount()` mounts a completely independent, standalone ASGI application. The mounted sub-application maintains its own separate OpenAPI documentation (`/subapp/docs`), its own independent middleware stack, and its own exception handlers.",
        "from fastapi import FastAPI\n\n# Main Application\nmain_app = FastAPI(title='Main API Service')\n\n# Independent Sub-Application with its own docs and OpenAPI schema\nadmin_subapp = FastAPI(title='Admin Sub-Application')\n\n@admin_subapp.get('/dashboard')\nasync def admin_dashboard():\n    return {'dashboard': 'admin_metrics'}\n\n# Mount the sub-app under /admin prefix\nmain_app.mount('/admin', admin_subapp)\n\n@main_app.get('/')\nasync def root():\n    return {'message': 'Main App Root'}",
        "Mounting an independent sub-application with dedicated documentation under /admin prefix.",
        "When an incoming request matches `/admin/...`, the main app strips the prefix from `scope['path']` and delegates the raw ASGI `(scope, receive, send)` call directly to the mounted sub-application.",
        "Embedding admin dashboards, hosting multiple microservices in a single container, or mounting WSGI legacy apps via `WSGIMiddleware`.",
        ["How does `app.mount()` differ fundamentally from `app.include_router()`?", "Does a mounted sub-application share middleware with the parent application?"],
        ["Confusing `app.mount()` with `app.include_router()` (router endpoints appear in the main OpenAPI schema; mounted apps have independent schemas).", "Assuming dependencies declared in the main app automatically apply to endpoints inside mounted sub-apps."],
        "Remember: Use `include_router` to modularize endpoints; use `app.mount()` to run independent applications together.",
        ["[Routing & Routers](routing-and-dependencies.md)", "[OpenAPI Documentation](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/advanced/sub-applications/"]
    ),

    # FA-BAS-191
    (
        "FA-BAS-191",
        "Testing Dependency Overrides Using `app.dependency_overrides`",
        "`app.dependency_overrides` is a dictionary on FastAPI applications that allows replacing dependencies with mock implementations during automated testing.",
        "FastAPI's dependency injection system was designed specifically for frictionless testing. When testing endpoints that require authenticated users, payment gateways, or database connections, you do not need complex patching (`unittest.mock.patch`). Instead, you assign a replacement callable to `app.dependency_overrides[original_dependency] = mock_dependency`. After the test finishes, clearing the dictionary restores normal operation.",
        "import pytest\nfrom fastapi import FastAPI, Depends\nfrom fastapi.testclient import TestClient\n\napp = FastAPI()\n\n# Production dependency\nasync def get_current_user():\n    raise NotImplementedError('Production auth required')\n\n@app.get('/profile')\nasync def user_profile(user: dict = Depends(get_current_user)):\n    return {'user': user['username']}\n\nclient = TestClient(app)\n\ndef test_profile_with_mock_user():\n    # Override dependency for this test\n    async def mock_get_current_user():\n        return {'username': 'test_admin_user', 'role': 'admin'}\n        \n    app.dependency_overrides[get_current_user] = mock_get_current_user\n    \n    response = client.get('/profile')\n    assert response.status_code == 200\n    assert response.json() == {'user': 'test_admin_user'}\n    \n    # Teardown: Clear overrides so other tests are not affected\n    app.dependency_overrides.clear()",
        "Overriding production authentication dependency with a mock user fixture during testing.",
        "Before resolving dependencies for any matched route, FastAPI checks if `dependency_callable` exists as a key in `app.dependency_overrides`. If present, it executes the override callable instead of the production function.",
        "Unit and integration test suites mocking external third-party APIs (Stripe, Twilio), authentication tokens, and databases.",
        ["Why is `app.dependency_overrides` preferred over `unittest.mock.patch` for testing dependencies?", "Why is clearing `app.dependency_overrides` in test teardowns mandatory?"],
        ["Forgetting to clear `app.dependency_overrides.clear()`, causing mock data to bleed into subsequent test cases.", "Attempting to override sub-dependencies that were not registered as FastAPI dependency callables."],
        "Use pytest fixtures with `yield` to automatically clear overrides: `yield; app.dependency_overrides.clear()`.",
        ["[Dependencies Basics](routing-and-dependencies.md)", "[Testing FastAPI](testing.md)"],
        ["https://fastapi.tiangolo.com/advanced/testing-dependencies/"]
    ),

    # FA-BAS-192
    (
        "FA-BAS-192",
        "Measuring Endpoint Response Time and Metrics with Prometheus",
        "FastAPI endpoints are monitored in production by collecting latency and throughput metrics using `prometheus-fastapi-instrumentator` and exposing them at `/metrics`.",
        "Observability requires tracking RED metrics (Rate, Errors, Duration). The `prometheus-fastapi-instrumentator` package hooks into FastAPI's ASGI pipeline to record: 1) Total HTTP requests grouped by method, path, and status code (`http_requests_total`); 2) Request latency histograms (`http_request_duration_seconds`). Prometheus periodically scrapes the `/metrics` endpoint to populate Grafana dashboards and trigger alerts.",
        "from fastapi import FastAPI\n# In production: from prometheus_fastapi_instrumentator import Instrumentator\n\napp = FastAPI()\n\n# Conceptual Prometheus instrumentation:\n# instrumentator = Instrumentator().instrument(app)\n# @app.on_event('startup')\n# async def startup():\n#     instrumentator.expose(app, endpoint='/metrics')\n\n@app.get('/checkout')\nasync def checkout():\n    return {'status': 'success'}",
        "Instrumenting FastAPI endpoints to export Prometheus metrics at /metrics.",
        "The instrumentator registers an ASGI middleware that records high-resolution monotonic timestamps on every request. It updates in-memory atomic counters and buckets that are formatted into Prometheus text exposition format when `/metrics` is scraped.",
        "Production monitoring dashboards in Grafana, alerting on high P99 latencies, and tracking HTTP 5xx error spikes.",
        ["What are the three RED metrics in microservice monitoring?", "Why should high-cardinality values (like user IDs) NEVER be used as Prometheus labels?"],
        ["Adding dynamic path parameters as Prometheus labels (e.g. `/users/{id}` producing 1,000,000 distinct time-series metrics, crashing Prometheus).", "Leaving `/metrics` accessible to the public internet without network firewall protection."],
        "Caution: Keep Prometheus label cardinality low; use route templates (`/users/{id}`) instead of resolved paths (`/users/12345`).",
        ["[Monitoring & Logging](../11-devops/monitoring-and-logging.md)", "[Production Instrumentation](production-and-performance.md)"],
        ["https://prometheus.io/docs/practices/instrumentation/"]
    ),

    # FA-BAS-193
    (
        "FA-BAS-193",
        "Enabling HTTP/2 Support in Uvicorn",
        "HTTP/2 support in Uvicorn enables multiplexing multiple concurrent HTTP requests over a single TCP connection, configured via the `--http h2` flag.",
        "HTTP/1.1 requires opening separate TCP connections for concurrent requests or suffers from head-of-line blocking. HTTP/2 introduces binary framing and stream multiplexing, allowing dozens of concurrent API requests and assets to flow through a single TCP socket. Uvicorn supports HTTP/2 when installed with the `h2` package (`pip install 'uvicorn[standard]' httptools h2`).",
        "# Installing HTTP/2 dependencies:\n# pip install h2\n\n# Launching Uvicorn with HTTP/2 enabled over TLS:\n# uvicorn main:app --ssl-keyfile key.pem --ssl-certfile cert.pem --http h2\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/http2-test')\nasync def test_h2():\n    return {'protocol': 'HTTP/2 enabled'}",
        "Enabling HTTP/2 protocol support in Uvicorn using the h2 package and TLS certificates.",
        "Web browsers only support HTTP/2 over TLS (ALPN negotiation). When the client initiates the TLS handshake, ALPN advertises `h2`. Uvicorn's `h2` protocol parser takes over the socket, multiplexing streams into individual ASGI request events.",
        "High-performance public APIs and web applications serving multiple assets to modern web and mobile clients.",
        ["What is ALPN (Application-Layer Protocol Negotiation) in HTTP/2 TLS handshakes?", "Why is HTTP/2 usually terminated at the reverse proxy (Nginx/Cloudflare) rather than directly in Uvicorn?"],
        ["Attempting to run HTTP/2 without TLS certificates (browsers refuse unencrypted HTTP/2).", "Forgetting to install the `h2` Python package before passing `--http h2`."],
        "Production note: In 95% of architectures, reverse proxies (Nginx/ALB) terminate HTTP/2 and forward plain HTTP/1.1 to internal Uvicorn pods.",
        ["[HTTP & HTTPS](../07-api-engineering/http-and-https.md)", "[Nginx Reverse Proxy](../11-devops/nginx.md)"],
        ["https://www.uvicorn.org/deployment/#http2"]
    ),

    # FA-BAS-194
    (
        "FA-BAS-194",
        "Using Gunicorn Configuration Files (`gunicorn.conf.py`)",
        "A `gunicorn.conf.py` file centralizes production process settings (workers, worker class, bind address, timeouts, logging) in version-controlled Python code.",
        "Rather than passing dozens of lengthy CLI flags to Gunicorn, production deployments store configuration in a `gunicorn.conf.py` file. Gunicorn automatically reads this file when launched in the current directory. The configuration file can also execute lifecycle hooks like `on_starting`, `worker_exit`, and `post_fork` to manage resources across process boundaries.",
        "# gunicorn.conf.py sample:\n\"\"\"\nimport multiprocessing\n\nbind = '0.0.0.0:8000'\nworkers = multiprocessing.cpu_count() * 2 + 1\nworker_class = 'uvicorn.workers.UvicornWorker'\ntimeout = 30\nkeepalive = 5\naccesslog = '-'\nerrorlog = '-'\nloglevel = 'info'\n\ndef post_fork(server, worker):\n    server.log.info(f'Worker spawned (pid: {worker.pid})')\n\"\"\"\n\n# Launching with config file:\n# gunicorn -c gunicorn.conf.py main:app",
        "Structuring a production gunicorn.conf.py configuration file with dynamic worker sizing and hooks.",
        "Gunicorn executes `gunicorn.conf.py` during master process initialization. Settings defined as module-level variables are applied before forking worker processes.",
        "Standard production deployment on EC2 instances, virtual machines, and standalone Docker containers.",
        ["What is the advantage of using `gunicorn.conf.py` over CLI flags?", "What Gunicorn hook allows disposing database engines after process forking (`post_fork`)?"],
        ["Hardcoding worker counts rather than calculating based on available CPU cores.", "Failing to set `accesslog = '-'` to output logs to standard output in Docker."],
        "Tip: Use `post_fork` hooks in `gunicorn.conf.py` to ensure database engines are properly initialized per process.",
        ["[Gunicorn & Uvicorn](../11-devops/gunicorn-and-uvicorn.md)", "[Database Integration](database-integration.md)"],
        ["https://docs.gunicorn.org/en/latest/configure.html"]
    ),

    # FA-BAS-195
    (
        "FA-BAS-195",
        "Inspecting CPU and Memory Usage of a Running FastAPI Process",
        "Process resource usage can be monitored programmatically using Python's `psutil` module or externally using Linux tools (`top`, `htop`, `pidstat`).",
        "Diagnosing performance degradation and memory leaks requires monitoring resource consumption. Python's `psutil` library allows checking CPU percent, Resident Set Size (RSS memory), and open file descriptor handles directly from within a running process, exposing these metrics to health endpoints.",
        "import os\nimport psutil\nfrom fastapi import FastAPI\n\napp = FastAPI()\nprocess = psutil.Process(os.getpid())\n\n@app.get('/metrics/system')\nasync def system_metrics():\n    memory_info = process.memory_info()\n    return {\n        'pid': process.pid,\n        'cpu_percent': process.cpu_percent(interval=None),\n        'memory_rss_mb': memory_info.rss / (1024 * 1024),  # Resident memory in MB\n        'open_files': len(process.open_files()),\n        'num_threads': process.num_threads(),\n    }",
        "Inspecting process memory (RSS), CPU, and open file handles using psutil.",
        "`psutil` reads process metrics directly from the Linux `/proc/[pid]/stat` and `/proc/[pid]/status` pseudo-filesystems, providing accurate kernel-level accounting without external subprocess overhead.",
        "Internal diagnostics, auto-tuning container memory limits, and detecting file descriptor leaks.",
        ["What is the difference between RSS (Resident Set Size) and VMS (Virtual Memory Size)?", "What happens when a process exceeds its open file descriptor limit (`ulimit -n`)?"],
        ["Confusing process RSS memory with total container host memory.", "Calling `psutil.cpu_percent(interval=1.0)` synchronously in an `async def` endpoint (blocks the event loop for 1 full second)."],
        "Caution: Always pass `interval=None` to `process.cpu_percent()` in async endpoints to avoid blocking the event loop.",
        ["[Async Concurrency](async-and-concurrency.md)", "[Linux & Bash](../11-devops/linux-and-bash.md)"],
        ["https://psutil.readthedocs.io/"]
    ),

    # FA-BAS-196
    (
        "FA-BAS-196",
        "Setting Maximum Request Body Size Limits in Nginx and Uvicorn",
        "Restricting maximum request body sizes prevents denial-of-service memory exhaustion caused by clients uploading massive payloads to endpoints expecting small JSON.",
        "Allowing unbounded request bodies allows attackers to flood servers with 500MB payloads, consuming RAM and network bandwidth. Body limits should be enforced at both the perimeter reverse proxy and application level: 1) Nginx: Set `client_max_body_size 10M;` in `nginx.conf`; 2) Uvicorn: Configure `--limit-max-requests` or enforce a custom middleware checking `request.headers.get('content-length')`.",
        "from fastapi import FastAPI, Request, HTTPException, status\n\napp = FastAPI()\nMAX_BODY_BYTES = 5 * 1024 * 1024  # 5 Megabytes limit\n\n@app.middleware('http')\nasync def enforce_max_body_size(request: Request, call_next):\n    content_length = request.headers.get('content-length')\n    if content_length and int(content_length) > MAX_BODY_BYTES:\n        raise HTTPException(\n            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,\n            detail=f'Payload exceeds maximum allowed limit of {MAX_BODY_BYTES} bytes'\n        )\n    return await call_next(request)\n\n@app.post('/upload')\nasync def upload_payload(payload: dict):\n    return {'status': 'accepted'}",
        "Enforcing a 5MB payload limit in middleware and rejecting oversized requests with HTTP 413.",
        "Checking `Content-Length` at the middleware entrypoint allows FastAPI to reject oversized requests immediately with HTTP 413 Payload Too Large before allocating memory to buffer the body bytes.",
        "Protecting REST endpoints from denial-of-service memory exhaustion and enforcing upload quotas.",
        ["What HTTP status code represents an oversized payload (413 Payload Too Large)?", "Why should request body size limits be enforced in Nginx in addition to FastAPI?"],
        ["Relying exclusively on application middleware without configuring Nginx `client_max_body_size` (Nginx default is 1MB, which can unexpectedly block valid uploads).", "Allowing chunked transfer requests (`Transfer-Encoding: chunked`) to bypass `Content-Length` checks without streaming byte counters."],
        "Remember: Pair Nginx `client_max_body_size` with application middleware to reject oversized requests early.",
        ["[Nginx Hardening](../11-devops/nginx.md)", "[API Security](../07-api-engineering/api-security.md)"],
        ["https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size"]
    ),

    # FA-BAS-197
    (
        "FA-BAS-197",
        "Profiling Endpoint Latency with `pytest-benchmark`",
        "`pytest-benchmark` integrates benchmarking into standard test suites to measure execution speed, detect performance regressions, and profile hot code paths.",
        "Performance optimization requires empirical measurement rather than guesswork. `pytest-benchmark` provides a `benchmark` fixture. In tests, you pass the callable to `benchmark(callable, *args)`. The tool runs the code thousands of times, computing statistical metrics (min, max, mean, standard deviation, rounds) and failing CI/CD builds if performance regresses beyond a defined threshold.",
        "from fastapi import FastAPI\nfrom fastapi.testclient import TestClient\nimport pytest\n\napp = FastAPI()\n\n@app.get('/compute')\ndef compute_data():\n    return {'result': sum(x * x for x in range(1000))}\n\nclient = TestClient(app)\n\n# Benchmark endpoint performance\ndef test_compute_benchmark(benchmark):\n    # Runs client.get('/compute') multiple rounds and generates statistical report\n    result = benchmark(client.get, '/compute')\n    assert result.status_code == 200",
        "Benchmarking endpoint latency and throughput using pytest-benchmark fixture.",
        "`pytest-benchmark` warms up the code, disables garbage collection during timing loops, records CPU time using high-precision timers, and outputs a formatted comparative table in terminal output.",
        "Continuous performance regression testing in CI/CD pipelines before merging pull requests.",
        ["Why must code be 'warmed up' before recording benchmark timings?", "How can benchmark results be saved and compared against historical runs in Git?"],
        ["Benchmarking with debug logging enabled (logging I/O skews CPU measurement).", "Running benchmarks on shared developer laptops with fluctuating background CPU activity instead of isolated CI runners."],
        "Tip: Use `pytest --benchmark-compare` in CI pipelines to automatically flag pull requests that degrade endpoint latency.",
        ["[Python Performance](../01-python/internals-and-performance.md)", "[Testing Fixtures](testing.md)"],
        ["https://pytest-benchmark.readthedocs.io/"]
    ),

    # FA-BAS-198
    (
        "FA-BAS-198",
        "Testing Database Endpoints Using SQLite In-Memory Databases",
        "FastAPI database endpoints are tested rapidly without external database servers by overriding database dependencies with an in-memory SQLite database configured with `StaticPool`.",
        "Running integration tests against external PostgreSQL or MySQL servers requires network provisioning, migrations, and database cleanup between tests. For fast local unit tests, developers override the database session dependency with an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`). Using `StaticPool` ensures that all test connections interact with the exact same in-memory database instance throughout the test lifecycle.",
        "import pytest\nfrom fastapi import FastAPI, Depends\nfrom httpx import AsyncClient, ASGITransport\nfrom sqlalchemy import select\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nfrom sqlalchemy.pool import StaticPool\nfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass User(Base):\n    __tablename__ = 'users'\n    id: Mapped[int] = mapped_column(primary_key=True)\n    name: Mapped[str] = mapped_column()\n\napp = FastAPI()\n\nasync def get_db(): raise NotImplementedError\n\n@app.get('/users')\nasync def list_users(db: AsyncSession = Depends(get_db)):\n    return (await db.scalars(select(User))).all()\n\n# Test Engine\ntest_engine = create_async_engine('sqlite+aiosqlite:///:memory:', poolclass=StaticPool)\nTestSession = async_sessionmaker(test_engine, expire_on_commit=False)\n\n@pytest.mark.asyncio\nasync def test_users_endpoint():\n    async with test_engine.begin() as conn:\n        await conn.run_sync(Base.metadata.create_all)\n        \n    async def override_db():\n        async with TestSession() as s:\n            yield s\n            \n    app.dependency_overrides[get_db] = override_db\n    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:\n        res = await ac.get('/users')\n        assert res.status_code == 200\n    app.dependency_overrides.clear()",
        "Configuring an isolated in-memory SQLite database fixture for rapid unit testing.",
        "`StaticPool` maintains a single open connection for the lifetime of the engine. In SQLite, in-memory databases (`:memory:`) are deleted when the last connection closes; `StaticPool` keeps the connection alive across multiple requests.",
        "Fast local test execution and pull-request verification in GitHub Actions.",
        ["Why is `StaticPool` required for in-memory SQLite databases in SQLAlchemy?", "When should you use Testcontainers (real PostgreSQL) instead of in-memory SQLite?"],
        ["Testing PostgreSQL-specific features (like JSONB, UUID, or ARRAY) against SQLite (fails due to dialect discrepancies).", "Forgetting to clear `app.dependency_overrides` after the test completes."],
        "Rule of thumb: SQLite in-memory for fast unit tests; Testcontainers PostgreSQL for dialect-specific integration tests.",
        ["[Database Integration](database-integration.md)", "[Dependency Overrides](production-and-performance.md)"],
        ["https://fastapi.tiangolo.com/advanced/testing-database/"]
    ),

    # FA-BAS-199
    (
        "FA-BAS-199",
        "Mocking External HTTP Calls in FastAPI Tests with `respx`",
        "`respx` intercepts and mocks outbound `httpx` HTTP requests in FastAPI unit tests, simulating third-party API responses without hitting real external networks.",
        "When FastAPI endpoints make outbound HTTP calls to third-party services (e.g. Stripe payment APIs, GitHub webhooks, OpenAI embeddings), automated test suites must never make real internet calls. Real calls are slow, flaky, cost money, and fail in offline CI environments. `respx` is the standard mock library for `httpx`. It intercepts outbound requests and returns mocked HTTP responses seamlessly.",
        "import pytest\nimport httpx\nimport respx\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/weather')\nasync def get_weather(city: str):\n    async with httpx.AsyncClient() as client:\n        res = await client.get(f'https://api.weather.com/v1/{city}')\n        return res.json()\n\n@pytest.mark.asyncio\n@respx.mock\nasync def test_weather_endpoint_with_mock():\n    # Mock outbound HTTP call to external weather API\n    respx.get('https://api.weather.com/v1/London').respond(\n        status_code=200,\n        json={'temp': 22, 'condition': 'Sunny'}\n    )\n    \n    # Test route handler\n    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as ac:\n        response = await ac.get('/weather?city=London')\n        assert response.status_code == 200\n        assert response.json() == {'temp': 22, 'condition': 'Sunny'}",
        "Mocking third-party HTTP API responses in FastAPI unit tests using respx.",
        "`respx` mocks HTTP calls at the `httpx.Transport` layer. When `client.get()` executes, `respx` matches the URL pattern and returns the configured mock response without opening any network sockets.",
        "Unit testing payment integrations, OAuth authentication handshakes, and third-party microservice calls.",
        ["Why shouldn't unit tests make real network requests to external APIs?", "How does `respx` compare to `unittest.mock.patch` for HTTP mocking?"],
        ["Mocking HTTP client internals with fragile `patch.object` calls instead of using declarative tools like `respx`.", "Failing to test how the endpoint behaves when the external API returns HTTP 500 or times out."],
        "Always test error paths: Mock external APIs returning 500 and network timeouts to verify your app degrades gracefully.",
        ["[Unit Testing](production-and-performance.md)", "[HTTP Client Usage](async-and-concurrency.md)"],
        ["https://lundberg.github.io/respx/"]
    ),

    # FA-BAS-200
    (
        "FA-BAS-200",
        "Top 5 Production Readiness Checklist for Deploying FastAPI",
        "Before deploying FastAPI to production, verify: 1) Non-root multi-stage Docker container; 2) Bounded database connection pooling; 3) Disabled debug and OpenAPI docs; 4) Liveness/Readiness probes; 5) Structured JSON logging.",
        "Deploying to production requires hardening across security, reliability, and observability. The essential 5-point Production Readiness Review (PRR) checklist includes: 1) Security: Disable `--reload` and `debug=True`, turn off `/docs` and `/redoc` on public endpoints, run containers as non-root users; 2) Concurrency: Run Uvicorn behind Gunicorn or in Kubernetes, size database connection pools strictly below server limits; 3) Probes: Implement distinct `/livez` (process alive) and `/readyz` (DB reachable) endpoints; 4) Observability: Configure structured JSON logging with correlation IDs and Prometheus `/metrics`; 5) Error Boundaries: Register global exception handlers to prevent raw tracebacks from leaking 500 errors to clients.",
        "# Production Deployment Verification Summary:\n# [x] Gunicorn / Uvicorn multi-worker process manager configured\n# [x] Database connection pool bounded (pool_size + max_overflow <= DB limits)\n# [x] docs_url=None, redoc_url=None, openapi_url=None in production\n# [x] Structured JSON logging to stdout with correlation IDs\n# [x] /livez and /readyz probes configured for container orchestrator\n# [x] Global exception handlers catch 500s without leaking stack traces\n# [x] CORS origins explicitly whitelisted (no allow_origins=['*'] with credentials)",
        "Production deployment checklist covering security, concurrency, observability, and error boundaries.",
        "Adhering to this checklist eliminates the most common production failures: database connection pool exhaustion, pod restart loops, credential leakage, and unhandled 500 crash storms.",
        "Go/No-Go production release reviews and cloud architecture sign-offs.",
        ["What is the single most common cause of database crashes when deploying FastAPI to production (unbounded connection pooling)?", "Why should Swagger UI be disabled on public production endpoints?"],
        ["Deploying with `reload=True` enabled in production.", "Sizing connection pools so that worker counts multiplied by pool size exceed PostgreSQL `max_connections`."],
        "Memorize the 5 pillars: Security Hardening, Bounded Resource Pools, Container Probes, Structured Observability, and Error Boundaries.",
        ["[Production Dockerfile](production-and-performance.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://fastapi.tiangolo.com/deployment/"]
    ),
]
