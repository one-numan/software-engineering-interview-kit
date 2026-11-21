# Django, FastAPI & Backend Engineering Interview Guide

## Overview
This guide provides direct, production-grade answers to the **12 Core Backend Engineering Questions** spanning **Django**, **FastAPI**, **ORM Optimization**, **Authentication**, **Concurrency**, and **LLM Integration**.

---

## 1. Django vs FastAPI?

### Comparison Table

| Feature | Django | FastAPI |
| :--- | :--- | :--- |
| **Philosophy** | "Batteries-Included" Monolith (ORM, Admin, Auth, Forms built-in) | Lightweight, Modern Microframework for High-Performance APIs |
| **Server Interface** | Traditional WSGI (Sync-first; async added incrementally) | Native **ASGI (Asynchronous Server Gateway Interface)** from ground up |
| **Concurrency / Speed** | Moderate; processes requests synchronously via thread workers | **Extremely High**; comparable to Node.js and Go via `asyncio` and `uvloop` |
| **Data Validation** | Django Forms & Serializers | **Pydantic v2** with automatic type hints and Rust core validation |
| **API Documentation** | Requires third-party package (`drf-spectacular` / Swagger) | **Automatic Interactive Docs** generated at `/docs` (Swagger UI / OpenAPI) |
| **Best Used For** | Large enterprise web apps, admin-heavy backends, CMS | High-QPS Microservices, Real-time APIs, GenAI & ML model serving |

---

## 2. Explain Django Middleware

### Simple Explanation
Django Middleware is a series of security gates or filters that sit between the web browser and your view code. Every incoming request must pass through all middleware layers before reaching your view, and the outgoing response passes back through them in reverse order.

### One-Line Interview Answer
**Django Middleware** is a lightweight, low-level plugin system that globally intercepts, inspects, and modifies HTTP requests and responses throughout the request-response lifecycle.

### Practical Middleware Example: Request ID Logging

```python
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Pre-processing: Generate unique correlation ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id

        # 2. Pass request to next middleware or view
        response = self.get_response(request)

        # 3. Post-processing: Attach ID to outgoing response headers
        response["X-Request-ID"] = request_id
        return response
```

---

## 3. What are Django QuerySets?

### One-Line Answer
A **Django QuerySet** is a lazily-evaluated representation of a database query; constructing or filtering a QuerySet does not hit the database until data is explicitly evaluated (iterated, sliced, or converted to a list).

---

## 4. What is the N+1 Query Problem?

### One-Line Answer
The **N+1 query problem** is an ORM anti-pattern where an application executes 1 initial SQL query to retrieve $N$ parent records, followed by $N$ separate queries inside a loop to fetch related child records, causing severe latency degradation.

---

## 5. `select_related` vs `prefetch_related`?

### Comparison Table

| Dimension | `select_related` | `prefetch_related` |
| :--- | :--- | :--- |
| **Relationship Type** | Single-valued: `ForeignKey`, `OneToOne` | Multi-valued: `ManyToManyField`, reverse `ForeignKey` |
| **SQL Strategy** | Single SQL query using **SQL `JOIN`** | **Two separate SQL queries**, joined in Python memory |
| **Query Example** | `Book.objects.select_related('author')` | `Author.objects.prefetch_related('books')` |

---

## 6. How do you implement Authentication in modern backends?

### Industry Standard: Stateless JWT Authentication
1. User submits username and password via `POST /api/login`.
2. Backend verifies hashed credentials against PostgreSQL using **Argon2** or **Bcrypt**.
3. Backend generates a signed **JSON Web Token (JWT)** containing claims (`user_id`, `role`, `exp`).
4. Backend returns:
   - **Access Token:** Short-lived (e.g. 15 minutes) passed in `Authorization: Bearer <token>`.
   - **Refresh Token:** Long-lived (e.g. 7 days) stored in a secure `HttpOnly, Secure, SameSite=Strict` cookie.
5. In FastAPI, endpoints validate tokens via dependency injection (`Depends(oauth2_scheme)`).

---

## 7. How do you design Scalable REST APIs?

### 5 Core Architecture Principles:
1. **Stateless App Servers:** Store sessions in Redis or JWTs so any load balancer can route requests to any server node.
2. **Database Read Replicas & Connection Pooling:** Offload read queries to read replicas and use PgBouncer for connection pooling.
3. **Cursor-Based (Keyset) Pagination:** Avoid `OFFSET` for high-volume endpoints (`WHERE id > cursor LIMIT 20`).
4. **Idempotency Keys:** Enforce idempotency on transactional mutations (`POST /orders`).
5. **Edge Caching with CDNs:** Cache public static assets and cacheable GET endpoints on Cloudflare.

---

## 8. How do you handle Background Tasks?

### Architecture:
- In **FastAPI**: Use native `BackgroundTasks` for lightweight tasks (e.g. logging an audit event) that run after returning the HTTP response.
- In **Production (Distributed)**: Use **Celery backed by RabbitMQ or Redis** for heavy tasks (generating PDFs, processing videos, sending bulk emails) to distribute work across a dedicated worker cluster.

---

## 9. How do you implement Redis Caching?

### Cache-Aside Pattern:
```python
import json
import redis
from fastapi import FastAPI

app = FastAPI()
cache = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    cache_key = f"product:{product_id}"
    
    # 1. Check Redis RAM
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached) # Cache Hit! < 2ms
    
    # 2. Query Database on Cache Miss
    product_data = {"id": product_id, "name": "Mechanical Keyboard", "price_inr": 4500}
    
    # 3. Store in Redis with a 5-minute TTL
    cache.set(cache_key, json.dumps(product_data), ex=300)
    return product_data
```

---

## 10. How do you handle Concurrent API Requests?

### Strategies:
1. **Asynchronous Non-Blocking I/O:** FastAPI running on Uvicorn with `async def` routes handles tens of thousands of idle/waiting network connections simultaneously.
2. **Pessimistic Row Locking (`SELECT ... FOR UPDATE`):** When modifying bank balances or booking seats, lock the exact row inside a transaction to prevent race conditions.
3. **Distributed Locks (Redis `SETNX`):** Ensure multiple workers cannot process the exact same order or webhook simultaneously.

---

## 11. How would you integrate an LLM API into FastAPI?

### Production Best Practice: Asynchronous Streaming via SSE (Server-Sent Events)

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google import genai

app = FastAPI()
client = genai.Client()

async def stream_llm_tokens(prompt: str):
    """Streams tokens chunk by chunk directly to the browser"""
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt
    )
    for chunk in response:
        if chunk.text:
            yield f"data: {chunk.text}\n\n"
            await asyncio.sleep(0.01) # Yield control to event loop

@app.get("/chat/stream")
async def chat_endpoint(prompt: str):
    return StreamingResponse(
        stream_llm_tokens(prompt),
        media_type="text/event-stream"
    )
```

---

## 12. How do you handle API Rate Limits and Retries?

### Production Resilience: Exponential Backoff with Jitter

```python
import random
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RateLimitException(Exception): pass

# Retry up to 5 times with exponential backoff and randomized jitter
@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(RateLimitException)
)
async def call_external_llm_api():
    # Simulated API call with random 429 response
    if random.random() < 0.3:
        raise RateLimitException("HTTP 429: Too Many Requests")
    return {"status": "SUCCESS"}
```
