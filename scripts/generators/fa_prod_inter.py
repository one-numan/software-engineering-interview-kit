"""
fa_prod_inter.py
================
Intermediate FastAPI Production & Performance Questions: FA-INT-176 to FA-INT-200 (25 questions)
"""

inter_data = [
    # FA-INT-176
    (
        "FA-INT-176",
        "Multi-Stage Docker Builds for Minimal Container Image Size and Security",
        "Multi-stage Docker builds separate build dependencies (compilers, git, dev packages) from the final runtime image, reducing image sizes from 1GB to < 100MB and eliminating security vulnerabilities.",
        "Compiling C-extensions (like `asyncpg`, `cryptography`, or `pydantic-core`) requires build tools (`gcc`, `g++`, `python3-dev`, `libpq-dev`). In a single-stage build, these heavy compilers remain in the final image, increasing image pull times and expanding the vulnerability attack surface. A multi-stage Docker build uses a `builder` stage to compile wheels, then copies *only* the compiled virtual environment into a clean, minimal `runtime` image (`python:3.11-slim` or `distroless`).",
        "# Multi-stage Dockerfile for FastAPI\n\"\"\"\n# Stage 1: Build environment\nFROM python:3.11-slim AS builder\nWORKDIR /app\nRUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev\nCOPY requirements.txt .\nRUN pip install --no-cache-dir --user -r requirements.txt\n\n# Stage 2: Minimal Runtime environment\nFROM python:3.11-slim AS runtime\nWORKDIR /app\n# Copy only the compiled Python packages from builder stage\nCOPY --from=builder /root/.local /root/.local\nCOPY . .\nENV PATH=/root/.local/bin:$PATH \\\n    PYTHONDONTWRITEBYTECODE=1 \\\n    PYTHONUNBUFFERED=1\n\nEXPOSE 8000\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n\"\"\"",
        "Multi-stage Dockerfile compiling wheels in builder stage and copying only artifacts to minimal runtime stage.",
        "The final container contains only the Python runtime and compiled wheel binaries. Compilers, package caches, headers, and git history are completely discarded with the builder stage container.",
        "Kubernetes clusters, autoscaling ECS services where fast container pull times (< 5s) are essential for rapid scaling.",
        ["How does multi-stage building improve vulnerability scanning (Trivy/Snyk) results?", "Why should `gcc` never be present in a production runtime container?"],
        ["Leaving build tools and package manager caches in production images.", "Accidentally copying local virtual environment (`.venv`) into the build context."],
        "Emphasize: Multi-stage builds yield smaller images (faster deploys) and fewer OS vulnerabilities (safer production).",
        ["[Docker Fundamentals](../11-devops/docker.md)", "[Security Hardening](../12-security/application-security.md)"],
        ["https://docs.docker.com/build/building/multi-stage/"]
    ),

    # FA-INT-177
    (
        "FA-INT-177",
        "Non-Root User Execution in Docker Containers for Production Security",
        "Running containers as an unprivileged non-root user prevents container breakout attacks from compromising the underlying host operating system.",
        "By default, processes inside a Docker container run as UID 0 (`root`). If an attacker exploits a remote code execution (RCE) vulnerability in an application or third-party dependency, running as root grants them root permissions within the container namespace. If combined with a container breakout vulnerability, they gain complete root control of the host node. Running under an explicit non-root user (`USER appuser`) prevents modifying system binaries, binding privileged ports (<1024), and escaping container boundaries.",
        "# Securing container with non-root user execution\n\"\"\"\nFROM python:3.11-slim\nWORKDIR /app\n\n# Create explicit group and user with non-root UID 10001\nRUN groupadd -g 10001 appgroup && \\\n    useradd -u 10001 -g appgroup -s /bin/false -m appuser\n\nCOPY --chown=appuser:appgroup requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY --chown=appuser:appgroup . .\n\n# Switch execution to unprivileged user\nUSER appuser\n\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n\"\"\"",
        "Creating an explicit unprivileged UID 10001 user and switching execution via USER appuser.",
        "The Linux kernel enforces file system and capability boundaries on UID 10001. The process cannot write to `/etc`, cannot install packages with `apt`, cannot invoke `sudo`, and has no `CAP_SYS_ADMIN` capabilities.",
        "SOC 2, ISO 27001, and PCI-DSS compliance mandates; secure multi-tenant Kubernetes clusters.",
        ["What is a container escape attack and how does non-root execution mitigate it?", "Can a non-root user bind to port 80 or 443 directly (no; privileged ports require UID 0 or `CAP_NET_BIND_SERVICE`)?"],
        ["Running production containers as `USER root`.", "Switching to non-root user before installing pip dependencies (fails with permission denied)."],
        "Security rule: Install packages as root, then switch to `USER appuser` before launching Uvicorn.",
        ["[Docker Security](../11-devops/docker.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html"]
    ),

    # FA-INT-178
    (
        "FA-INT-178",
        "Gunicorn Worker Configuration Formula (`workers = 2 * CPU_CORES + 1`) and Trade-Offs",
        "The classic Gunicorn formula `(2 * CPU) + 1` was designed for synchronous WSGI; for async Uvicorn, running 1 to 2 workers per core or 1 worker per Kubernetes container is optimal.",
        "The traditional Gunicorn heuristic `workers = (2 * CPU_CORES) + 1` assumes workers are synchronous threads that block during I/O. In an asynchronous framework like FastAPI with Uvicorn, a single worker can handle thousands of concurrent requests while awaiting I/O. In containerized Kubernetes deployments, running 1 Uvicorn worker per container pod allows the Kubernetes Horizontal Pod Autoscaler (HPA) to scale pods based on actual CPU metrics cleanly. On standalone multi-core VMs, running `workers = CPU_CORES` or `CPU_CORES * 1.5` prevents excessive process context switching.",
        "# Dynamic worker sizing in gunicorn.conf.py\nimport multiprocessing\nimport os\n\n# In Kubernetes: 1 worker per container pod (scaled by HPA)\n# On standalone VM: CPU_CORES to utilize all cores\nCORES = multiprocessing.cpu_count()\n\ndef get_worker_count() -> int:\n    if os.getenv('KUBERNETES_SERVICE_HOST'):\n        return 1  # 1 worker per pod for optimal HPA scaling\n    return max(2, CORES)  # Standalone VM\n\nworkers = get_worker_count()\nworker_class = 'uvicorn.workers.UvicornWorker'",
        "Calculating optimal worker processes dynamically based on deployment environment.",
        "Each Gunicorn worker is an independent Python process running its own GIL and event loop. Scaling workers across cores bypasses Python's Global Interpreter Lock (GIL) for CPU operations, while the async event loop within each worker handles I/O concurrency.",
        "Sizing VM clusters and Kubernetes deployments for high-throughput APIs.",
        ["Why is running 1 Uvicorn worker per container pod preferred in Kubernetes over multi-worker containers?", "How does Python's GIL affect CPU-bound tasks in a single-worker Uvicorn process?"],
        ["Applying the synchronous `(2 * CPU) + 1` formula blindly on async services with 64-core servers (spawns 129 processes, causing severe memory bloat and connection exhaustion).", "Running only 1 worker on an 8-core bare-metal VM (wastes 7 CPU cores)."],
        "Sizing rule: In Kubernetes, run 1 worker per pod; on standalone VMs, run 1 to 2 workers per physical CPU core.",
        ["[Gunicorn & Uvicorn](../11-devops/gunicorn-and-uvicorn.md)", "[GIL Fundamentals](../01-python/concurrency-and-parallelism.md)"],
        ["https://docs.gunicorn.org/en/latest/design.html#how-many-workers"]
    ),

    # FA-INT-179
    (
        "FA-INT-179",
        "Instrumenting FastAPI with Prometheus Metrics Using `prometheus-fastapi-instrumentator`",
        "`prometheus-fastapi-instrumentator` automatically generates Prometheus RED metrics (request count, latency histograms, error rates) and exposes a scrapable `/metrics` endpoint.",
        "Manually instrumenting metrics on every endpoint is tedious and error-prone. The `prometheus-fastapi-instrumentator` library automates this: 1) It intercepts all incoming requests and outgoing responses via ASGI middleware; 2) It records Prometheus counters and histograms (`http_requests_total`, `http_request_duration_seconds_bucket`); 3) It normalizes route paths (e.g. `/users/123` becomes `/users/{id}`) to prevent metric cardinality explosion.",
        "from fastapi import FastAPI\nfrom prometheus_fastapi_instrumentator import Instrumentator\n\napp = FastAPI()\n\n# Configure and instrument the application\ninstrumentator = Instrumentator(\n    should_group_status_codes=False,\n    should_ignore_untemplated=True,\n    should_respect_env_var=True,\n    env_var_name='ENABLE_METRICS',\n    excluded_handlers=['/metrics', '/healthz'],\n)\n\n# Add instrumentation middleware\ninstrumentator.instrument(app)\n\n# Expose scrapable Prometheus metrics endpoint\n@app.on_event('startup')\nasync def startup():\n    instrumentator.expose(app, endpoint='/metrics', include_in_schema=False)\n\n@app.get('/items')\nasync def list_items():\n    return [{'id': 1, 'name': 'Item A'}]",
        "Automated Prometheus instrumentation and /metrics exposition with route templating.",
        "The instrumentator registers an ASGI middleware that records high-resolution monotonic timestamps. When requests complete, it records metrics into Prometheus `Histogram` and `Counter` objects in memory. Scraping `/metrics` serializes these structures into Prometheus exposition format.",
        "Production observability, Grafana dashboards, and automated Prometheus alert rules.",
        ["What is high-cardinality in Prometheus and why does `should_ignore_untemplated=True` prevent it?", "What metric types are used for request rate and request latency (Counter vs Histogram)?"],
        ["Exposing `/metrics` without excluding it from metrics collection (causes recursive self-monitoring metrics).", "Recording unbounded user-input query strings as Prometheus metric labels."],
        "Golden rule: Always exclude `/metrics` and `/healthz` from instrumentation, and ensure route paths are templated.",
        ["[Monitoring & Logging](../11-devops/monitoring-and-logging.md)", "[Prometheus Setup](production-and-performance.md)"],
        ["https://github.com/trallnag/prometheus-fastapi-instrumentator"]
    ),

    # FA-INT-180
    (
        "FA-INT-180",
        "Protecting the `/metrics` Endpoint with Authentication and Network Isolation",
        "Prometheus metrics endpoints expose sensitive system architecture, endpoint names, and traffic patterns; they must be protected via HTTP Basic Auth or network-level firewall isolation.",
        "Allowing public access to `/metrics` allows competitors and attackers to monitor your exact traffic volume, endpoint error rates, and internal infrastructure topology. To protect `/metrics`: 1) Network Isolation: Configure Kubernetes or Nginx to allow `/metrics` requests *only* from the internal Prometheus scraper IP subnet; 2) Application Security: Guard the `/metrics` endpoint behind HTTP Basic Authentication using `fastapi.security.HTTPBasic`.",
        "import secrets\nfrom fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import HTTPBasic, HTTPBasicCredentials\n\napp = FastAPI()\nsecurity = HTTPBasic()\n\nPROMETHEUS_USER = 'prometheus-scraper'\nPROMETHEUS_PASS = 'super-secret-metrics-token'\n\ndef verify_metrics_auth(credentials: HTTPBasicCredentials = Depends(security)):\n    correct_username = secrets.compare_digest(credentials.username, PROMETHEUS_USER)\n    correct_password = secrets.compare_digest(credentials.password, PROMETHEUS_PASS)\n    if not (correct_username and correct_password):\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Invalid metrics authentication credentials',\n            headers={'WWW-Authenticate': 'Basic'},\n        )\n    return credentials.username\n\n@app.get('/metrics', dependencies=[Depends(verify_metrics_auth)], include_in_schema=False)\nasync def metrics():\n    # In production, return prometheus_client.generate_latest()\n    return {'status': 'authenticated_metrics'}",
        "Securing Prometheus /metrics endpoint using HTTP Basic Authentication and constant-time string comparison.",
        "Prometheus supports HTTP Basic Auth in its `prometheus.yml` scrape configuration (`basic_auth: {username, password}`). The dependency checks the `Authorization: Basic <base64>` header on every scrape round, rejecting unauthorized requests.",
        "Securing cloud microservice metrics in public or multi-tenant Kubernetes clusters.",
        ["Why is `secrets.compare_digest` required when checking metrics credentials?", "How do you configure Prometheus `scrape_configs` to pass Basic Authentication credentials?"],
        ["Leaving `/metrics` accessible to the public internet without authentication.", "Including `/metrics` in the public Swagger UI OpenAPI documentation (`include_in_schema=True`)."],
        "Set `include_in_schema=False` on `/metrics` and secure it with Basic Auth or VPC private networking.",
        ["[Authentication & Security](authentication-and-security.md)", "[Security Hardening](../12-security/application-security.md)"],
        ["https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config"]
    ),

    # FA-INT-181
    (
        "FA-INT-181",
        "Distributed Rate Limiting Across Kubernetes Pods Using Redis and Lua",
        "Distributed rate limiting coordinates request quotas across multiple independent FastAPI worker pods using atomic Redis Lua scripts.",
        "In-memory rate limiters (like Python dictionaries) fail in production because requests are distributed across multiple Kubernetes pods and Gunicorn workers: a client rate-limited to 10 req/min could send 100 requests if balanced across 10 pods. Distributed rate limiting shares state via Redis. An atomic Lua script executes sliding-window or token-bucket logic directly on the Redis server, guaranteeing strict cluster-wide rate limit enforcement.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Atomic Redis Lua script for token-bucket rate limiting\nLUA_RATE_LIMITER = \"\"\"\nlocal key = KEYS[1]\nlocal limit = tonumber(ARGV[1])\nlocal current = tonumber(redis.call('get', key) or \"0\")\nif current + 1 > limit then\n    return 0\nelse\n    redis.call('INCRBY', key, 1)\n    if current == 0 then\n        redis.call('EXPIRE', key, tonumber(ARGV[2]))\n    end\n    return 1\nend\n\"\"\"\n\n@app.middleware('http')\nasync def distributed_rate_limiter_middleware(request: Request, call_next):\n    client_ip = request.client.host if request.client else '127.0.0.1'\n    # In production: allowed = await redis.eval(LUA_RATE_LIMITER, 1, f'rate:{client_ip}', 10, 60)\n    allowed = 1  # Simulated\n    \n    if allowed == 0:\n        return JSONResponse(\n            status_code=status.HTTP_429_TOO_MANY_REQUESTS,\n            content={'error': 'CLUSTER_RATE_LIMIT_EXCEEDED'}\n        )\n    return await call_next(request)",
        "Enforcing cluster-wide distributed rate limiting using atomic Redis Lua script.",
        "Redis executes Lua scripts atomically in a single thread. No other command can run while the script executes, preventing race conditions between concurrent requests originating from different Kubernetes pods.",
        "Global API rate limiting, preventing distributed brute-force attacks, and protecting payment gateways.",
        ["Why can't multiple individual Redis commands (`GET`, `INCR`, `EXPIRE`) achieve atomic rate limiting without Lua?", "What happens to the rate limiter if the Redis cluster becomes unavailable (Fail Open policy)?"],
        ["Using local in-memory rate limiting in Kubernetes environments.", "Failing to adopt a 'Fail Open' strategy when Redis experiences network partitions."],
        "Emphasize: In distributed architectures, rate limiting MUST use a centralized store (Redis) with atomic Lua scripting.",
        ["[Redis Caching](../06-redis-and-messaging/redis.md)", "[Rate Limiting](middleware-and-exception-handling.md)"],
        ["https://redis.io/docs/manual/programmability/eval-intro/"]
    ),

    # FA-INT-182
    (
        "FA-INT-182",
        "Asynchronous Integration Testing with Testcontainers (PostgreSQL, Redis)",
        "Testcontainers spins up real, ephemeral Docker containers (PostgreSQL, Redis) dynamically in Python test suites, ensuring tests run against production-identical database engines.",
        "While in-memory SQLite works for simple unit tests, it fails to support PostgreSQL-specific features (JSONB, full-text search, PostGIS, UUIDs, array columns, concurrency locks). The `testcontainers-python` library programmatically launches real Docker containers during `pytest` execution, runs migrations, and tears them down after tests finish, providing 100% production fidelity.",
        "import pytest\nfrom testcontainers.postgres import PostgresContainer\nfrom sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker\n\n@pytest.fixture(scope='session')\ndef postgres_container():\n    # Spin up ephemeral PostgreSQL Docker container for integration test session\n    with PostgresContainer('postgres:16-alpine') as postgres:\n        yield postgres\n\n@pytest.mark.asyncio\nasync def test_postgres_features(postgres_container):\n    # Extract dynamic connection URL assigned to random host port\n    sync_url = postgres_container.get_connection_url()\n    async_url = sync_url.replace('postgresql://', 'postgresql+asyncpg://')\n    \n    engine = create_async_engine(async_url)\n    async with engine.connect() as conn:\n        result = await conn.execute(select(1))\n        assert result.scalar() == 1\n    await engine.dispose()",
        "Spinning up real ephemeral PostgreSQL container for integration testing using Testcontainers.",
        "Testcontainers communicates with the local Docker daemon via the Docker socket (`/var/run/docker.sock`). It binds ephemeral host ports, waits for PostgreSQL to pass internal health checks, runs the tests, and terminates the container cleanly.",
        "CI/CD integration pipelines testing database transactions, complex queries, and Redis caching.",
        ["Why are Testcontainers preferred over in-memory SQLite for PostgreSQL codebases?", "How do Testcontainers prevent port collisions when running parallel tests in CI?"],
        ["Running integration tests against a shared, persistent developer database that retains dirty test data.", "Forgetting to dispose async engines before container shutdown in pytest fixtures."],
        "Tip: Use Testcontainers in CI/CD to eliminate 'works on SQLite, crashes on Postgres' bugs forever.",
        ["[Docker Fundamentals](../11-devops/docker.md)", "[Database Testing](database-integration.md)"],
        ["https://testcontainers-python.readthedocs.io/"]
    ),

    # FA-INT-183
    (
        "FA-INT-183",
        "Database Connection Pooling Across Multiple Gunicorn Workers",
        "Each Gunicorn worker maintains its own independent SQLAlchemy connection pool; total connections equal `Workers * (pool_size + max_overflow)`, requiring PgBouncer to prevent exceeding database connection limits.",
        "When running Gunicorn with 4 workers, each worker process instantiates its own `AsyncEngine` with its own `QueuePool`. If `pool_size=10` and `max_overflow=5`, each worker can hold 15 connections, totaling 60 connections for that pod. If you scale to 5 Kubernetes pods, total connections reach 300, which can exceed PostgreSQL's default `max_connections = 100`. In multi-worker architectures, developers must either bound pool sizes strictly (e.g. `pool_size=2`) or place PgBouncer in front of the database using `NullPool` in SQLAlchemy.",
        "from sqlalchemy.ext.asyncio import create_async_engine\nfrom sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool\n\n# Scenario: 4 Gunicorn workers connecting to PostgreSQL\n# Bound pool to 3 persistent connections per worker (Total: 4 * (3 + 1) = 16 connections)\nengine = create_async_engine(\n    'postgresql+asyncpg://user:pass@db:5432/app',\n    poolclass=AsyncAdaptedQueuePool,\n    pool_size=3,\n    max_overflow=1,\n    pool_timeout=15,\n    pool_recycle=1800,\n)",
        "Configuring strictly bounded connection pool sizes for multi-worker Gunicorn deployments.",
        "Because worker processes have distinct memory address spaces, connection pools cannot communicate across processes. Bounding the pool mathematically ensures that even under maximum burst traffic, the application cannot exhaust PostgreSQL's connection limits.",
        "Production Gunicorn/Uvicorn deployments connecting to Amazon RDS or Google Cloud SQL.",
        ["Why can't multiple Gunicorn worker processes share a single database connection pool?", "How does PgBouncer transaction pooling decouple worker counts from database connection limits?"],
        ["Setting `pool_size=20` on a 16-worker server, causing immediate 'sorry, too many clients already' crashes on PostgreSQL.", "Forgetting to dispose the engine pool in Gunicorn's `post_fork` hook if the engine was instantiated globally before fork."],
        "Calculation: `Pods * Workers_per_pod * (pool_size + max_overflow) <= DB max_connections * 0.8`.",
        ["[Database Connection Pools](database-integration.md)", "[Gunicorn & Uvicorn](../11-devops/gunicorn-and-uvicorn.md)"],
        ["https://docs.sqlalchemy.org/en/20/core/pooling.html"]
    ),

    # FA-INT-184
    (
        "FA-INT-184",
        "Configuring Nginx as an SSL-Terminating Reverse Proxy in Front of Uvicorn",
        "Nginx terminates TLS/HTTPS, serves static files directly, buffers slow client requests, and forwards clean HTTP traffic to Uvicorn via local sockets or internal network ports.",
        "While Uvicorn can terminate TLS, doing so in Python consumes event loop CPU cycles. In production, Nginx sits in front of Uvicorn: 1) TLS Termination: Nginx decrypts HTTPS using high-speed OpenSSL C libraries; 2) Static Assets: Nginx serves images and CSS directly from disk with zero Python overhead; 3) Buffer Defense: Nginx buffers slow client uploads before sending to Uvicorn, protecting Uvicorn from Slowloris attacks; 4) Header Forwarding: Passes `X-Forwarded-For` and `X-Forwarded-Proto`.",
        "# Sample Nginx configuration block for FastAPI / Uvicorn\n\"\"\"\nserver {\n    listen 443 ssl http2;\n    server_name api.example.com;\n\n    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;\n    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;\n\n    client_max_body_size 10M;\n\n    location /static/ {\n        alias /app/static/;\n        expires 30d;\n    }\n\n    location / {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n    }\n}\n\"\"\"",
        "Production Nginx reverse proxy configuration with TLS termination, HTTP/2, and header forwarding.",
        "Nginx manages the public TLS handshake, decodes the HTTP/2 stream, and proxies a clean HTTP/1.1 stream over a local loopback socket (`127.0.0.1:8000`) or UNIX domain socket (`/tmp/uvicorn.sock`) directly into Uvicorn.",
        "Standard production architecture on AWS EC2, DigitalOcean droplets, and bare-metal servers.",
        ["Why is Nginx significantly faster at terminating TLS than Uvicorn?", "What is the purpose of `proxy_set_header Upgrade $http_upgrade` in Nginx?"],
        ["Forgetting `proxy_set_header X-Forwarded-Proto $scheme`, causing FastAPI's `HTTPSRedirectMiddleware` to enter an infinite redirect loop.", "Failing to enable `proxy_http_version 1.1`, which breaks WebSocket proxying."],
        "Emphasize: Always pass `X-Forwarded-Proto` from Nginx so FastAPI knows whether the original request was HTTPS.",
        ["[Nginx Hardening](../11-devops/nginx.md)", "[HTTPS Enforcement](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/deployment/nginx/"]
    ),

    # FA-INT-185
    (
        "FA-INT-185",
        "Forwarding Client IPs Correctly with `Forwarded` and `X-Forwarded-For` in Uvicorn",
        "Uvicorn must be launched with `--proxy-headers` and configured `--forwarded-allow-ips` to resolve the real client IP from `X-Forwarded-For` instead of the reverse proxy's internal IP.",
        "When an application sits behind Nginx, AWS ALB, or Cloudflare, every incoming TCP socket connects from the reverse proxy's internal IP (e.g. `10.0.0.5` or `127.0.0.1`). If Uvicorn is not told to trust proxy headers, `request.client.host` returns the proxy IP, corrupting IP rate limiters and access logs. Passing `--proxy-headers` instructs Uvicorn to parse `X-Forwarded-For` and `X-Forwarded-Proto`. For security, `--forwarded-allow-ips` specifies which proxy IPs are trusted to prevent client IP spoofing.",
        "# Launching Uvicorn with secure proxy header parsing\n# uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='127.0.0.1,10.0.0.0/8'\n\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.get('/client-ip')\nasync def read_ip(request: Request):\n    # request.client.host will contain the REAL client IP, not Nginx IP!\n    return {'real_client_ip': request.client.host if request.client else 'unknown'}",
        "Configuring Uvicorn proxy headers to resolve real client IP addresses from trusted proxies.",
        "When `--proxy-headers` is active, Uvicorn inspects `X-Forwarded-For` if the immediate TCP socket peer matches `--forwarded-allow-ips`. It updates the ASGI `scope['client']` tuple with the client's actual public IP before forwarding to FastAPI.",
        "Accurate geo-location tracking, IP rate limiting, and security incident investigations.",
        ["What is the danger of setting `--forwarded-allow-ips='*'` in public cloud environments?", "How does `X-Forwarded-For` handle multiple intermediate proxy hops?"],
        ["Setting `--forwarded-allow-ips='*'` when Uvicorn is directly accessible to the public internet (allows attackers to forge arbitrary IP headers).", "Failing to enable `--proxy-headers`, causing all rate limiters to throttle the Nginx proxy IP for all users."],
        "Rule: Set `--proxy-headers` and restrict `--forwarded-allow-ips` strictly to your internal VPC/proxy CIDR block.",
        ["[Nginx Proxy Configuration](../11-devops/nginx.md)", "[Rate Limiting](middleware-and-exception-handling.md)"],
        ["https://www.uvicorn.org/settings/#http"]
    ),

    # FA-INT-186
    (
        "FA-INT-186",
        "Memory Leak Detection in Production Using `objgraph` and `tracemalloc`",
        "Memory leaks in Python async applications are diagnosed by snapshotting object allocations with `tracemalloc` and visualizing object reference graphs with `objgraph`.",
        "In long-running FastAPI services, memory leaks often manifest as gradually climbing RAM usage (RSS) until the container is terminated by an OOM kill. Leaks typically stem from: global collections accumulating items indefinitely, circular references escaping GC, or lingering closures holding `Request` objects. Python's built-in `tracemalloc` captures memory allocation snapshots to identify the exact line of code allocating leaking memory.",
        "import tracemalloc\nfrom fastapi import FastAPI\n\napp = FastAPI()\ntracemalloc.start()  # Track memory allocations\n\nsnapshot_start = tracemalloc.take_snapshot()\n\n@app.get('/debug/memory-diff')\nasync def memory_diff():\n    current_snapshot = tracemalloc.take_snapshot()\n    # Compare current memory allocations against startup snapshot\n    top_stats = current_snapshot.compare_to(snapshot_start, 'lineno')\n    \n    report = []\n    for stat in top_stats[:5]:\n        report.append(str(stat))\n    return {'top_memory_growers': report}",
        "Comparing memory allocation snapshots with tracemalloc to identify memory growth bottlenecks.",
        "`tracemalloc` hooks into Python's memory allocator (pymalloc). It records the filename and line number of every allocated Python object. Comparing two snapshots highlights code regions with the highest net byte increases.",
        "Diagnosing slow memory leaks in production staging environments and performance regression testing.",
        ["What is the performance overhead of running `tracemalloc` in high-traffic production environments?", "How does `objgraph.show_most_common_types()` help identify leaking object types?"],
        ["Leaving `tracemalloc.start()` permanently active in high-traffic production (adds 10-20% memory and CPU overhead).", "Confusing memory fragmentation with true Python object memory leaks."],
        "Tip: Enable `tracemalloc` on staging environments or run diagnostic endpoints temporarily to capture memory diffs under load.",
        ["[Memory Management](../01-python/memory-management.md)", "[Production Monitoring](production-and-performance.md)"],
        ["https://docs.python.org/3/library/tracemalloc.html"]
    ),

    # FA-INT-187
    (
        "FA-INT-187",
        "CPU Profiling Async FastAPI Applications Using `py-spy` Flamegraphs",
        "`py-spy` is a zero-overhead sampling profiler for Python that inspects running processes from the outside without modifying code, generating interactive SVG flamegraphs.",
        "When an API endpoint suffers from unexpected CPU spikes or high response latency, traditional profilers (like `cProfile`) cannot profile running production containers without adding massive overhead and disrupting async coroutines. `py-spy` is a sampling profiler written in Rust that reads the memory of a running Python process using OS system calls (`process_vm_readv` on Linux). It visualizes hot code paths and GIL contention as interactive flamegraphs.",
        "# Recording an interactive flamegraph of a running FastAPI process with py-spy\n# py-spy record -o profile.svg --pid 12345 --duration 30 --native\n\n# Or dumping live top functions directly in terminal:\n# py-spy top --pid 12345\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/heavy-calc')\nasync def heavy_calc():\n    # py-spy will pinpoint this function as a flamegraph bottleneck\n    return {'result': sum(i * i for i in range(500000))}",
        "Profiling running FastAPI process CPU usage non-invasively using py-spy.",
        "`py-spy` inspects Python's runtime symbols in memory at a sample rate (e.g. 100Hz). It traces the active CPython call stack and async coroutine frames, aggregating stack traces into a hierarchical flamegraph where horizontal width corresponds to percentage of CPU time spent.",
        "Diagnosing production CPU spikes, identifying serialization bottlenecks, and optimizing slow endpoints.",
        ["Why doesn't `py-spy` require modifying application code or restarting Uvicorn?", "What does the width of a box in a flamegraph represent?"],
        ["Attempting to run `cProfile` in production under high traffic, which degrades throughput by 30-50%.", "Running `py-spy` inside a container without `SYS_PTRACE` capability (Docker security blocks memory inspection by default)."],
        "Remember: In Docker/Kubernetes, `py-spy` requires `docker run --cap-add SYS_PTRACE` to inspect process memory.",
        ["[Python Performance](../01-python/internals-and-performance.md)", "[Production Optimization](production-and-performance.md)"],
        ["https://github.com/benfred/py-spy"]
    ),

    # FA-INT-188
    (
        "FA-INT-188",
        "Optimizing JSON Serialization Performance with `orjson` or `ujson` in FastAPI",
        "FastAPI can replace the standard library `json` serializer with ultra-fast C/Rust libraries like `orjson` using `ORJSONResponse` to speed up JSON serialization by up to 5x.",
        "In APIs returning large datasets (thousands of records or nested dictionaries), JSON serialization is often the single biggest CPU bottleneck. Python's standard `json` library is written in pure Python/C and has moderate performance. `orjson` is an ultra-fast JSON library written in Rust that serializes dataclasses, UUIDs, datetimes, and numpy arrays natively. Passing `default_response_class=ORJSONResponse` to `FastAPI` accelerates JSON rendering across the entire application.",
        "from fastapi import FastAPI\nfrom fastapi.responses import ORJSONResponse\nfrom pydantic import BaseModel\n\n# Enable ORJSONResponse globally across the entire application\napp = FastAPI(default_response_class=ORJSONResponse)\n\nclass DataPayload(BaseModel):\n    id: int\n    label: str\n\n@app.get('/fast-json', response_class=ORJSONResponse)\nasync def get_fast_json():\n    # Serialized up to 5x faster than standard JSONResponse\n    return [{'id': i, 'label': f'record_{i}'} for i in range(10000)]",
        "Configuring ORJSONResponse globally to accelerate large JSON payload serialization.",
        "`orjson` compiles Rust SIMD instructions to serialize Python dictionaries directly into UTF-8 bytes without intermediate string allocations, cutting CPU cycles and garbage collector overhead significantly.",
        "High-throughput APIs returning large catalog listings, analytics tables, or financial market depth feeds.",
        ["Why is `orjson` significantly faster than Python's standard `json` module?", "How does `orjson` handle Python `datetime` and `uuid.UUID` objects natively?"],
        ["Installing `orjson` without configuring `default_response_class=ORJSONResponse`, leaving the default slower serializer active.", "Assuming `ujson` and `orjson` produce identical strict JSON output (check date/time formatting options)."],
        "Tip: Set `FastAPI(default_response_class=ORJSONResponse)` to immediately improve JSON serialization throughput by 3x-5x.",
        ["[Pydantic Serialization](pydantic-and-validation.md)", "[Python Performance](../01-python/internals-and-performance.md)"],
        ["https://fastapi.tiangolo.com/advanced/custom-response/#use-orjsonresponse"]
    ),

    # FA-INT-189
    (
        "FA-INT-189",
        "Optimizing Docker Layer Caching for `requirements.txt` and `pyproject.toml`",
        "Structuring Dockerfiles to copy dependency specification files before application source code ensures pip installations are cached unless dependencies actually change.",
        "Docker builds images layer by layer. If any line in a Dockerfile changes, that layer and all subsequent layers must be rebuilt from scratch (cache invalidation). If a Dockerfile runs `COPY . .` followed by `RUN pip install -r requirements.txt`, editing a single comment in a Python file invalidates the pip cache, forcing a multi-minute dependency reinstall on every build. Splitting the copy into dependency files first guarantees near-instant sub-second builds.",
        "# Highly Optimized Dockerfile Layer Caching Pattern\n\"\"\"\nFROM python:3.11-slim\nWORKDIR /app\n\n# Step 1: Copy ONLY dependency files\nCOPY requirements.txt pyproject.toml ./\n\n# Step 2: Install dependencies (This layer is cached unless requirements change!)\nRUN pip install --no-cache-dir -r requirements.txt\n\n# Step 3: Copy frequently changing application source code (Invalidates only this layer)\nCOPY . .\n\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n\"\"\"",
        "Optimizing Dockerfile layer ordering to maximize build cache reuse and speed up CI/CD.",
        "Docker computes a SHA-256 checksum of the copied files. Because `requirements.txt` changes infrequently compared to application source code, Docker reuses the cached layer containing installed wheels, skipping pip downloads entirely.",
        "Continuous integration (CI) pipelines where fast build times (< 30s) are required for rapid PR feedback.",
        ["How does Docker calculate layer cache hits for `COPY` instructions?", "What is `.dockerignore` and why is it essential for Docker build caching?"],
        ["Omitting a `.dockerignore` file, accidentally copying `.git`, `__pycache__`, or `.venv` into the Docker build context.", "Copying the entire repository before running `pip install`."],
        "Always create a `.dockerignore` containing `.git`, `__pycache__`, `.venv`, and `.env`.",
        ["[Docker Fundamentals](../11-devops/docker.md)", "[CI/CD Optimization](../11-devops/ci-cd.md)"],
        ["https://docs.docker.com/build/cache/"]
    ),

    # FA-INT-190
    (
        "FA-INT-190",
        "Implementing Readiness Probes That Verify Database and Cache Connectivity",
        "A readiness probe (`/readyz`) verifies active network communication with PostgreSQL and Redis, signaling to Kubernetes that the pod is ready to accept user traffic.",
        "When a new pod launches, Uvicorn starts listening on port 8000 in milliseconds. However, database connection pools might not be warmed up, or migrations might still be running. If traffic is routed to the pod immediately, early user requests fail. A robust `/readyz` probe executes lightweight verification queries (`SELECT 1` on PostgreSQL and `PING` on Redis) with strict 1-second timeouts, returning HTTP 200 only when all systems are functional.",
        "from fastapi import FastAPI, Response, status, Depends\nfrom sqlalchemy import select, text\nfrom sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine\nimport asyncio\n\napp = FastAPI()\nengine = create_async_engine('sqlite+aiosqlite:///:memory:')\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\n@app.get('/readyz', tags=['Probes'])\nasync def readiness_probe():\n    try:\n        # Verify database connectivity with 1-second timeout\n        async with asyncio.timeout(1.0):\n            async with SessionLocal() as session:\n                await session.execute(text('SELECT 1'))\n                \n        # Verify Redis cache connectivity with 1-second timeout\n        # async with asyncio.timeout(1.0):\n        #     await redis_client.ping()\n            \n        return {'status': 'ready', 'database': 'healthy', 'redis': 'healthy'}\n    except Exception as exc:\n        # Return 503 so Kubernetes removes this pod from load balancer endpoints\n        return Response(\n            content=f'Readiness check failed: {exc}',\n            status_code=status.HTTP_503_SERVICE_UNAVAILABLE\n        )",
        "Implementing a strict readiness probe verifying database and cache health with asyncio timeouts.",
        "Kubernetes queries `/readyz` every few seconds. If the endpoint returns 503 or times out, the pod's IP is removed from the Kubernetes Service endpoints, preventing traffic routing to degraded pods.",
        "Kubernetes rolling updates, zero-downtime deployments, and graceful recovery from database failovers.",
        ["Why must readiness probe checks have strict, short timeouts (e.g. 1 second)?", "What is the difference between a failing liveness probe and a failing readiness probe in Kubernetes?"],
        ["Failing to set timeouts on readiness probes, causing the probe to hang during database freezes.", "Putting expensive queries (like full table scans) inside readiness probes."],
        "Rule: Readiness probe verifies dependencies with lightweight `SELECT 1` queries and strict 1-second timeouts.",
        ["[Health Checks](production-and-performance.md)", "[Kubernetes Deployments](../11-devops/deployment-and-troubleshooting.md)"],
        ["https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"]
    ),

    # FA-INT-191
    (
        "FA-INT-191",
        "Liveness vs Readiness vs Startup Probes in Kubernetes for FastAPI",
        "Kubernetes uses three distinct probe types: Startup probes wait for slow bootups, Liveness probes detect deadlocks and restart pods, and Readiness probes manage traffic routing.",
        "Understanding probe responsibilities prevents destructive restart cascades: 1) Startup Probe: Used for applications with slow initialization (e.g. warming machine learning models or loading large caches); disables liveness and readiness checks until startup succeeds; 2) Liveness Probe: Checks if the Python event loop is stuck or deadlocked; if it fails, Kubernetes kills and restarts the container; 3) Readiness Probe: Checks if dependencies are ready to serve requests; if it fails, traffic is temporarily paused without restarting the container.",
        "# Kubernetes Pod Spec snippet configuring all 3 probes:\n\"\"\"\nspec:\n  containers:\n  - name: fastapi-app\n    image: api:v1\n    startupProbe:\n      httpGet:\n        path: /livez\n        port: 8000\n      failureThreshold: 30\n      periodSeconds: 5\n    livenessProbe:\n      httpGet:\n        path: /livez\n        port: 8000\n      periodSeconds: 10\n    readinessProbe:\n      httpGet:\n        path: /readyz\n        port: 8000\n      periodSeconds: 5\n\"\"\"",
        "Kubernetes YAML specification defining startup, liveness, and readiness probes.",
        "During pod boot, the Startup probe runs first. Once it succeeds, Kubernetes begins running Liveness and Readiness probes periodically. Decoupling readiness from liveness ensures database blips don't cause mass container restart storms.",
        "Production Kubernetes cluster deployments running AI inference, heavy microservices, or large caches.",
        ["What dangerous failure cascade occurs when a liveness probe checks external database health?", "How does a Startup probe prevent Kubernetes from prematurely killing slow-starting containers?"],
        ["Checking external dependencies in liveness probes (causes all pods to restart when the database is slow, crashing the entire cluster).", "Setting probe timeouts too short without accounting for network jitter."],
        "Golden rule: Liveness = Process alive? (Restart on fail); Readiness = Ready for traffic? (Pause traffic on fail).",
        ["[Kubernetes Architecture](../11-devops/deployment-and-troubleshooting.md)", "[Production Probes](production-and-performance.md)"],
        ["https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/"]
    ),

    # FA-INT-192
    (
        "FA-INT-192",
        "Zero-Downtime Rolling Deploys with Kubernetes `RollingUpdate` and Uvicorn Graceful Shutdown",
        "Zero-downtime rolling deploys replace old pods with new pods incrementally, coordinating Uvicorn's graceful shutdown and `preStop` hooks to ensure zero dropped requests.",
        "During a Kubernetes `RollingUpdate`, old pods are terminated while new pods are spawned. However, a race condition exists: the Kubernetes endpoint controller takes 1-3 seconds to update iptables/kube-proxy to stop routing traffic to terminating pods. If Uvicorn shuts down immediately upon receiving `SIGTERM`, incoming requests hit dead sockets (502 Bad Gateway). A `preStop` hook sleeping for 3-5 seconds ensures the network stops routing traffic before Uvicorn enters graceful shutdown.",
        "# Kubernetes preStop hook configuration for zero-downtime rolling deploys\n\"\"\"\nspec:\n  containers:\n  - name: fastapi-api\n    lifecycle:\n      preStop:\n        exec:\n          # Sleep 5 seconds to let iptables/ALB update before sending SIGTERM to Uvicorn\n          command: [\"/bin/sh\", \"-c\", \"sleep 5\"]\n    terminationGracePeriodSeconds: 45\n\"\"\"",
        "Kubernetes lifecycle preStop hook delaying SIGTERM to allow network load balancers to deregister the pod.",
        "When Kubernetes terminates a pod: 1) The pod is removed from the Service endpoint list; 2) The `preStop` hook executes `sleep 5`, allowing in-flight requests and proxy updates to complete; 3) Kubernetes sends `SIGTERM` to Uvicorn; 4) Uvicorn drains remaining connections and exits cleanly without dropping a single packet.",
        "Tier-1 financial backends, payment services, and e-commerce platforms requiring 99.99% availability during deployments.",
        ["Why does a `sleep 5` in a `preStop` hook eliminate intermittent 502 Bad Gateway errors during deployments?", "How does `maxSurge` and `maxUnavailable` control rollout speed in Kubernetes?"],
        ["Omitting a `preStop` hook, resulting in 502 Bad Gateway errors during high-traffic rolling deployments.", "Setting `terminationGracePeriodSeconds` shorter than the `preStop` sleep plus Uvicorn graceful shutdown."],
        "Always add `preStop: exec: command: ['sleep', '5']` to production Kubernetes manifests for zero-downtime deploys.",
        ["[CI/CD Pipelines](../11-devops/ci-cd.md)", "[Graceful Shutdown](production-and-performance.md)"],
        ["https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination"]
    ),

    # FA-INT-193
    (
        "FA-INT-193",
        "Asynchronous Background Worker Processes (Celery / ARQ) Alongside FastAPI Web Pods",
        "Heavy background tasks (PDF generation, bulk email dispatch, video encoding) must be offloaded to dedicated worker processes (Celery or ARQ) via message brokers (Redis or RabbitMQ).",
        "FastAPI's built-in `BackgroundTasks` executes tasks on the same event loop or threadpool as the web server, making it unsuitable for CPU-intensive or long-running jobs (which steal CPU and memory from HTTP requests). For heavy workloads, FastAPI publishes task messages to a broker (Redis/RabbitMQ). Dedicated worker processes running in separate containers consume and execute the jobs asynchronously, keeping API response times under 50ms.",
        "# Enqueuing a heavy Celery job from a FastAPI route\nfrom fastapi import FastAPI, status\n# from app.tasks import generate_pdf_report  # Celery task\n\napp = FastAPI()\n\n@app.post('/reports/generate', status_code=status.HTTP_202_ACCEPTED)\nasync def request_report(user_id: int):\n    # Enqueue task in Celery / Redis in < 2ms without blocking API\n    # task = generate_pdf_report.delay(user_id=user_id)\n    task_id = 'mock-celery-task-uuid-12345'\n    \n    return {\n        'status': 'accepted',\n        'task_id': task_id,\n        'check_status_url': f'/reports/status/{task_id}'\n    }",
        "Offloading heavy computation to asynchronous worker queues and returning HTTP 202 Accepted.",
        "The HTTP endpoint publishes a lightweight JSON message to Redis in < 2ms and immediately returns HTTP 202 Accepted. An independent worker container running Celery or ARQ consumes the message, executes the task in the background, and persists results to S3 or a database.",
        "Report exports, video transcoding, bulk notifications, and machine learning inference pipelines.",
        ["When is FastAPI's built-in `BackgroundTasks` appropriate vs Celery/ARQ?", "What HTTP status code is recommended when a background job is accepted (HTTP 202 Accepted)?"],
        ["Running CPU-intensive video or PDF rendering inside FastAPI `BackgroundTasks`, freezing the web server event loop.", "Sharing database connections or global sessions between web processes and forked Celery worker processes."],
        "Architecture rule: Tasks taking > 500ms or consuming significant CPU belong in Celery or ARQ, not the web server.",
        ["[Celery Integration](../06-redis-and-messaging/celery.md)", "[RabbitMQ Basics](../06-redis-and-messaging/rabbitmq.md)"],
        ["https://docs.celeryq.dev/"]
    ),

    # FA-INT-194
    (
        "FA-INT-194",
        "Sentry Integration for Real-Time Exception Tracking and Performance Tracing",
        "Sentry instruments FastAPI applications via `sentry-sdk` to capture unhandled exceptions, stack traces, request metadata, and distributed transaction spans in real time.",
        "When an unexpected exception occurs in production, relying solely on server log files makes debugging slow and chaotic. Sentry automatically captures unhandled exceptions, scrubs sensitive PII, records local variable state at each frame of the traceback, attaches the active user ID and release version, and alerts engineering teams via Slack or PagerDuty. It also records distributed performance spans.",
        "# Production Sentry integration in FastAPI\n\"\"\"\nimport sentry_sdk\nfrom sentry_sdk.integrations.fastapi import FastApiIntegration\nfrom sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration\n\nsentry_sdk.init(\n    dsn='https://examplePublicKey@o0.ingest.sentry.io/0',\n    integrations=[FastApiIntegration(), SqlalchemyIntegration()],\n    traces_sample_rate=0.1,      # Record 10% of transaction performance traces\n    profiles_sample_rate=0.05,   # Profile 5% of requests for CPU flamegraphs\n    environment='production',\n    release='api@2.4.1',\n    send_default_pii=False,      # Protect user privacy\n)\n\"\"\"",
        "Initializing Sentry SDK with FastAPI, SQLAlchemy integration, and performance sampling.",
        "Sentry's ASGI integration wraps the application. When an unhandled exception bubbles up, Sentry captures the exception context, serializes local variables, and dispatches an asynchronous telemetry payload to Sentry's ingestion API over HTTPS.",
        "Production error tracking, release regression detection, and APM performance monitoring.",
        ["Why should `traces_sample_rate` be set to a fraction (e.g. 0.1) in high-traffic production?", "How does Sentry capture SQLAlchemy database queries executed during an HTTP request?"],
        ["Setting `send_default_pii=True` in healthcare or banking applications, inadvertently transmitting patient data to third-party servers.", "Setting 100% trace sampling in high-traffic services, creating massive network overhead and Sentry quota exhaustion."],
        "Always set `send_default_pii=False` and configure `environment` and `release` strings to track deployments.",
        ["[Global Exception Handlers](middleware-and-exception-handling.md)", "[Production Monitoring](production-and-performance.md)"],
        ["https://docs.sentry.io/platforms/python/integrations/fastapi/"]
    ),

    # FA-INT-195
    (
        "FA-INT-195",
        "Centralized Log Aggregation with Vector, FluentBit, and Elasticsearch/Loki",
        "In containerized cloud environments, application logs output as JSON to stdout/stderr, where sidecar or daemonset agents (FluentBit, Vector) collect and forward them to Elasticsearch or Grafana Loki.",
        "Writing logs directly to local disk files (`/var/log/app.log`) inside containers is an anti-pattern: containers are ephemeral, disks are wiped upon pod restarts, and multiple pod logs cannot be searched together. Following Twelve-Factor App principles, FastAPI writes single-line JSON logs to `stdout`. A node-level log shipper (FluentBit, Vector, or Promtail) scrapes container output, enriches logs with Kubernetes metadata (pod name, namespace), and ships them to a centralized search store (Elasticsearch, OpenSearch, Grafana Loki).",
        "# Architecture diagram:\n# FastAPI (stdout JSON) -> Docker log driver -> FluentBit / Vector DaemonSet -> Grafana Loki / Elasticsearch\n\nimport logging\nimport json\nfrom fastapi import FastAPI\n\napp = FastAPI()\nlogger = logging.getLogger('cloud_log')\nlogging.basicConfig(level=logging.INFO)\n\n@app.get('/audit')\nasync def log_audit_event():\n    # Emits single-line JSON log directly to stdout for FluentBit scraping\n    log_payload = {'event': 'USER_LOGIN', 'user_id': 101, 'status': 'success'}\n    print(json.dumps(log_payload))  # Captured by container runtime\n    return {'status': 'logged'}",
        "Streaming single-line JSON logs to stdout for automated collection by FluentBit or Vector.",
        "The Linux container runtime streams container stdout/stderr to `/var/log/pods/`. FluentBit monitors these files using kernel inotify events, parses JSON structures, attaches Kubernetes pod labels, and streams batches over HTTP to Loki/Elasticsearch.",
        "Enterprise cloud platforms with hundreds of distributed microservice pods.",
        ["Why does writing logs to local files inside Docker containers cause disk exhaustion?", "What is the difference between Elasticsearch (full text index) and Grafana Loki (label index)?"],
        ["Writing multiline formatted Python tracebacks to stdout without a JSON wrapper, causing FluentBit to split one exception into 15 distinct log lines.", "Logging sensitive tokens and passwords into centralized search engines."],
        "Remember: Always format logs as single-line JSON so log aggregators treat multi-line tracebacks as a single search event.",
        ["[JSON Structured Logging](production-and-performance.md)", "[Monitoring & Logging](../11-devops/monitoring-and-logging.md)"],
        ["https://12factor.net/logs"]
    ),

    # FA-INT-196
    (
        "FA-INT-196",
        "Preventing OOM (Out-of-Memory) Kills in Kubernetes Using Container Resource Limits",
        "Out-of-Memory (OOM) kills occur when a container exceeds its memory limit; they are prevented by setting appropriate container resource requests and limits, and bounding application memory usage.",
        "When a container consumes more RAM than allowed by its Kubernetes manifest (`resources.limits.memory`), the Linux kernel's OOM Killer abruptly terminates the container process with exit code 137 (`SIGKILL`). To prevent OOM kills: 1) Set `requests` based on baseline memory (e.g. 256Mi) and `limits` with sufficient headroom (e.g. 1Gi); 2) Bounded connection pools and batch sizes; 3) Never buffer unbounded file uploads in RAM; 4) Stream large database results with server-side cursors.",
        "# Kubernetes Container Resource Limits Specification\n\"\"\"\nspec:\n  containers:\n  - name: fastapi-container\n    image: api:v1\n    resources:\n      requests:\n        memory: \"256Mi\"     # Minimum guaranteed RAM for pod scheduling\n        cpu: \"250m\"         # 0.25 CPU core\n      limits:\n        memory: \"1Gi\"       # Maximum RAM before kernel issues OOM Kill (Exit 137)\n        cpu: \"1000m\"        # 1.0 CPU core throttle limit\n\"\"\"",
        "Configuring Kubernetes container resource requests and limits to guard against OOM kills.",
        "The Linux kernel enforces memory boundaries via cgroups (control groups). If a process attempts to allocate memory beyond its cgroup limit, the kernel selects and sends `SIGKILL` (signal 9) to the highest-memory process, leaving zero opportunity for application cleanup.",
        "Production container sizing in Kubernetes, AWS ECS, and Docker Swarm.",
        ["What exit code does a container return when terminated by the Linux OOM Killer (Exit Code 137)?", "What is the difference between CPU throttling (limits) and memory termination (limits)?"],
        ["Omitting memory limits, allowing a single leaking pod to consume all RAM on a shared Kubernetes node and crash neighbor pods.", "Setting memory limits too close to `requests` without headroom for traffic bursts."],
        "Rule of thumb: CPU limits cause throttling (slow execution); Memory limits cause immediate process death (OOM Kill).",
        ["[Memory Management](../01-python/memory-management.md)", "[Kubernetes Deployments](../11-devops/deployment-and-troubleshooting.md)"],
        ["https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"]
    ),

    # FA-INT-197
    (
        "FA-INT-197",
        "Load Testing FastAPI Applications with Locust and k6",
        "Load testing tools (Locust, k6) simulate thousands of concurrent virtual users to identify concurrency bottlenecks, event loop lag, and connection pool exhaustion before production launch.",
        "Deploying without load testing risks sudden production outages during marketing campaigns or traffic spikes. Locust (Python-based) and k6 (Go/JavaScript-based) simulate realistic user traffic patterns: 1) Ramp-up users gradually to detect concurrency degradation; 2) Measure P95 and P99 latency percentiles; 3) Identify breaking points where error rates spike (stress testing); 4) Verify that database connection pools and Redis caches handle peak loads.",
        "# Sample Locust load testing script (locustfile.py)\n\"\"\"\nfrom locust import HttpUser, task, between\n\nclass APIUser(HttpUser):\n    wait_time = between(0.1, 0.5)  # Simulate user think time\n\n    @task(3)\n    def view_catalog(self):\n        self.client.get('/items')\n\n    @task(1)\n    def checkout(self):\n        self.client.post('/orders', json={'item_id': 42, 'quantity': 1})\n\"\"\"\n\n# Run Locust test via CLI:\n# locust -f locustfile.py --headless -u 500 -r 50 -t 5m --host http://localhost:8000",
        "Defining realistic multi-scenario load testing workflows using Locust.",
        "Locust spawns greenlet/gevent virtual users that dispatch concurrent HTTP requests. It records response times and error rates, generating statistical distributions for P50, P90, P95, and P99 latencies.",
        "Pre-launch readiness reviews, Black Friday capacity planning, and evaluating server sizing.",
        ["Why is measuring P99 latency more informative than measuring average (mean) latency?", "What is the difference between stress testing, load testing, and soak testing?"],
        ["Running load tests against production databases without isolated test data.", "Testing from a single client laptop that hits local network interface bottlenecks rather than testing true server capacity."],
        "Emphasize: Always evaluate P99 latency during load tests; averages hide severe latency spikes experienced by users.",
        ["[Production Benchmarking](production-and-performance.md)", "[Performance Optimization](../01-python/internals-and-performance.md)"],
        ["https://locust.io/"]
    ),

    # FA-INT-198
    (
        "FA-INT-198",
        "Tuning Linux Kernel Socket Parameters (`somaxconn`, `tcp_max_syn_backlog`) for High Concurrency",
        "Linux kernel networking parameters (`somaxconn`, `tcp_max_syn_backlog`, `file-max`) must be tuned to allow Uvicorn to accept thousands of incoming TCP connections without dropping packets.",
        "Under high concurrency (e.g. 20,000 requests/sec), standard Linux default kernel settings drop incoming connections before they even reach Uvicorn: 1) `net.core.somaxconn`: Maximum length of the listen queue for unaccepted sockets (default 128 or 4096; tune to 65535); 2) `net.ipv4.tcp_max_syn_backlog`: Number of half-open SYN connections held during TCP handshakes (tune to 65535); 3) `fs.file-max`: Maximum open file descriptors across the OS.",
        "# Linux kernel tuning settings in /etc/sysctl.conf for high-concurrency servers\n\"\"\"\nnet.core.somaxconn = 65535\nnet.ipv4.tcp_max_syn_backlog = 65535\nnet.ipv4.tcp_fin_timeout = 15\nnet.ipv4.tcp_tw_reuse = 1\nfs.file-max = 2097152\n\"\"\"\n\n# Apply settings live:\n# sysctl -p\n\n# Increase per-process open file descriptor limit in limits.conf:\n# * soft nofile 65535\n# * hard nofile 65535",
        "Tuning Linux sysctl kernel network socket parameters for high-concurrency servers.",
        "When incoming TCP SYN packets flood a server, the kernel places them in the SYN queue, responds with SYN-ACK, and moves completed handshakes to the listen queue. Increasing `somaxconn` prevents the kernel from dropping connection requests during traffic spikes.",
        "Bare-metal Linux servers and Kubernetes worker nodes running high-traffic edge gateways.",
        ["What symptom occurs when `somaxconn` is too low under sudden traffic spikes (connection refused / timeout)?", "What does `ulimit -n` control in a Linux process?"],
        ["Tuning Uvicorn worker counts while ignoring Linux kernel socket limits (traffic drops at the OS layer).", "Setting `file-max` too low, causing 'Too many open files' socket crashes under peak load."],
        "Remember: Both the OS kernel socket queue (`somaxconn`) and process file limits (`ulimit -n 65535`) must be elevated.",
        ["[Linux & Bash](../11-devops/linux-and-bash.md)", "[Nginx Hardening](../11-devops/nginx.md)"],
        ["https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt"]
    ),

    # FA-INT-199
    (
        "FA-INT-199",
        "Managing API Deprecation and Version Migration in Production",
        "API evolution in production is managed through URI versioning (`/v1`, `/v2`), RFC 8594 deprecation headers, and dual-run migration periods before retiring old endpoints.",
        "Public APIs must evolve without breaking mobile apps or third-party consumers running older versions. Production versioning best practices include: 1) URL prefixing (`/api/v1/orders`, `/api/v2/orders`); 2) Non-breaking changes (adding optional fields) are deployed in-place without incrementing major versions; 3) Breaking changes (modifying types, deleting fields) require a new version prefix; 4) Deprecated versions attach `Deprecation` and `Sunset` headers notifying clients of decommissioning timelines.",
        "from fastapi import FastAPI, APIRouter\n\napp = FastAPI()\n\n# Version 1 Router (Deprecated)\nv1_router = APIRouter(prefix='/api/v1', tags=['v1 (Deprecated)'])\n@v1_router.get('/users')\nasync def get_users_v1():\n    return [{'id': 1, 'full_name': 'Alice Smith'}]\n\n# Version 2 Router (Current Standard)\nv2_router = APIRouter(prefix='/api/v2', tags=['v2'])\n@v2_router.get('/users')\nasync def get_users_v2():\n    return [{'id': 1, 'first_name': 'Alice', 'last_name': 'Smith'}]\n\napp.include_router(v1_router)\napp.include_router(v2_router)",
        "Managing API version progression cleanly using independent APIRouter instances.",
        "By grouping endpoints into version-prefixed routers, both `/api/v1` and `/api/v2` coexist seamlessly in the same application process, allowing clients to migrate at their own pace.",
        "Enterprise public APIs, SaaS integrations, and mobile backend platforms.",
        ["What constitutes a breaking change in a REST API response contract?", "What headers are standardized by RFC 8594 for deprecating API endpoints?"],
        ["Introducing breaking changes into existing `/v1` endpoints, crashing production mobile applications.", "Maintaining legacy API versions indefinitely without establishing clear sunset dates."],
        "Golden rule: Never alter existing response structures on an active API version; create a `/v2` prefix for breaking changes.",
        ["[API Versioning](../07-api-engineering/rest-api.md)", "[Deprecation Headers](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]
    ),

    # FA-INT-200
    (
        "FA-INT-200",
        "Blue-Green and Canary Deployment Strategies for FastAPI Services",
        "Blue-Green deployments switch 100% of traffic instantly between identical production environments, while Canary deployments route 5-10% of live traffic to the new version to detect errors safely.",
        "Deploying changes directly to production risks outages. Advanced deployment patterns eliminate risk: 1) Blue-Green: Two identical environments exist (Blue = live, Green = idle). The new release is deployed and tested on Green. The load balancer switches 100% of traffic to Green instantly; if an issue is detected, switching back to Blue takes 1 second; 2) Canary: The new version is deployed to a small percentage of pods (e.g. 5%). Traffic splitters (Istio, AWS ALB, Argo Rollouts) route 5% of users to Canary. Error rates and latency are observed before rolling out to 100%.",
        "# Conceptual Canary traffic split in Kubernetes / Service Mesh:\n# 95% traffic -> app-v1 (Stable Blue)\n#  5% traffic -> app-v2 (Canary Green)\n\n# Automated Rollback Trigger Condition:\n# IF (canary_http_5xx_rate > 0.01 OR canary_p99_latency > 500ms):\n#     ROLLBACK Canary immediately to 0%\n# ELSE:\n#     PROMOTE Canary incrementally (10% -> 25% -> 50% -> 100%)",
        "Canary deployment verification logic based on automated error rate and latency thresholds.",
        "Canary testing limits blast radius: if a fatal bug exists in the new release, only 5% of users encounter it, and automated APM metrics trigger instant rollback before widespread disruption occurs.",
        "Tier-1 cloud platforms, banking APIs, and continuous delivery pipelines deploying multiple times per day.",
        ["What is the difference between Blue-Green deployments and Canary deployments?", "Why do database migrations need special care (backward compatibility) during Blue-Green deployments?"],
        ["Running non-backward-compatible database migrations before a Blue-Green switch, breaking the live Blue environment.", "Promoting Canary deployments manually without automated metrics verification."],
        "Core principle: Canary deployments limit blast radius; pair with automated Prometheus rollback alerts for safe continuous delivery.",
        ["[Zero-Downtime Migrations](database-integration.md)", "[CI/CD Pipelines](../11-devops/ci-cd.md)"],
        ["https://martinfowler.com/bliki/BlueGreenDeployment.html"]
    ),
]
