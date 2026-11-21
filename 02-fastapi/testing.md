# FastAPI Testing Guide & Interview Reference

> [!NOTE]
> In accordance with our single-page consolidation strategy (**Less Pages, More Information**), all comprehensive unit, integration, and performance testing questions have been consolidated into [**production-and-performance.md**](production-and-performance.md) and [**middleware-and-exception-handling.md**](middleware-and-exception-handling.md).

---

## Testing Topics & Question Navigation

| Topic | Direct Question Link | Key Concepts Covered |
|---|---|---|
| **Synchronous Unit Testing** | [**FA-BAS-180**](production-and-performance.md#fa-bas-180-unit-testing-fastapi-endpoints-using-testclient-from-starlette) | `TestClient`, Starlette in-memory transport, status assertions, validation error assertions |
| **Asynchronous Integration Testing** | [**FA-BAS-181**](production-and-performance.md#fa-bas-181-asynchronous-testing-with-httpxasyncclient-and-pytest-asyncio) | `httpx.AsyncClient`, `ASGITransport`, `pytest.mark.asyncio`, native coroutine awaiting |
| **Testing Dependency Overrides** | [**FA-BAS-191**](production-and-performance.md#fa-bas-191-testing-dependency-overrides-using-appdependency_overrides) | `app.dependency_overrides`, mock authentication, teardown cleanup |
| **In-Memory SQLite Database Testing** | [**FA-BAS-198**](production-and-performance.md#fa-bas-198-testing-database-endpoints-using-sqlite-in-memory-databases) | `sqlite+aiosqlite:///:memory:`, `StaticPool`, schema initialization, session fixtures |
| **Mocking External HTTP APIs** | [**FA-BAS-199**](production-and-performance.md#fa-bas-199-mocking-external-http-calls-in-fastapi-tests-with-respx) | `respx`, mocking `httpx` transports, simulating timeouts and 500 errors |
| **Isolated Middleware Testing** | [**FA-INT-174**](middleware-and-exception-handling.md#fa-int-174-testing-middleware-in-isolation-using-testclient-and-starlette-endpoint) | Testing middleware on dummy apps, header validation, unhandled exceptions |
| **Real Ephemeral Containers** | [**FA-INT-182**](production-and-performance.md#fa-int-182-asynchronous-integration-testing-with-testcontainers-postgresql-redis) | `testcontainers-python`, real PostgreSQL/Redis instances, eliminating SQLite dialect skew |
| **Endpoint Latency Benchmarking** | [**FA-BAS-197**](production-and-performance.md#fa-bas-197-profiling-endpoint-latency-with-pytest-benchmark) | `pytest-benchmark`, statistical analysis, regression detection |
| **Load & Stress Testing** | [**FA-INT-197**](production-and-performance.md#fa-int-197-load-testing-fastapi-applications-with-locust-and-k6) | Locust, k6, virtual user ramp-up, P95/P99 latency analysis under concurrency |

---

## Quick Testing Setup Snippet

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/livez")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}
```
