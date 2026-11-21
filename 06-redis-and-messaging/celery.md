# Celery & Asynchronous Task Processing Interview Guide

## Module Overview
This guide covers **Celery**, Python's distributed task queue used to handle long-running background tasks, scheduled cron jobs, and asynchronous workloads without blocking web requests.

---

## Visual Architecture: Celery Producer-Consumer Lifecycle

```mermaid
flowchart LR
    Client([User Request]) --> WebAPI[FastAPI / Django Web Service]
    WebAPI -->|1. .delay() - Fast Return < 15ms| Broker[(Message Broker: RabbitMQ / Redis)]
    WebAPI -.->|2. Return 202 Accepted| Client
    
    subgraph Celery_Worker_Cluster["Celery Distributed Workers"]
        Broker -->|3. Deliver Task| Worker1[Worker Process 1]
        Broker -->|Deliver Task| Worker2[Worker Process 2]
    end
    
    Worker1 -->|4. Heavy Computation / PDF / Email| External[External SMTP / S3 / Bank API]
    Worker1 -->|5. Store Task Result| Backend[(Result Backend: Redis / PostgreSQL)]
```

---

## Questions & Comprehensive Solutions

### CEL-BAS-001: What is Celery and why do web applications need it?

**Difficulty:** Basic  
**Topic:** Asynchronous Background Processing

#### 1. Simple Explanation
In a web application, an HTTP request should ideally finish within 100 to 200 milliseconds. If a user clicks a button to *"Generate Monthly GST Invoice (PDF)"* or *"Send 5,000 Welcome Emails"*, that task might take 30 seconds. If the web server runs that task directly, the user's browser freezes waiting, and the web server runs out of worker threads.  
**Celery** solves this by letting the web server hand the heavy job to a separate worker process in the background and immediately tell the user: *"Your task has started!"*

#### 2. Easy Real-World Example
Imagine ordering food at a fast-food counter (McDonald's):
- **Without Celery:** You order a burger. The cashier leaves the counter, walks into the kitchen, fries the patty, bakes the bun, wraps the burger, and hands it to you after 10 minutes. The line of waiting customers stretches out the door.
- **With Celery:** You order a burger. The cashier immediately gives you a **Token Receipt (`task_id`)** and shouts the order into the kitchen (Message Broker). The cashier is instantly ready to serve the next customer. The dedicated chefs in the kitchen (Celery Workers) prepare the burger in the background.

#### 3. One-Line Interview Answer
**Celery** is an asynchronous, distributed task queue in Python based on distributed message passing, used to offload and schedule long-running operations outside the HTTP request-response cycle.

#### 4. Detailed Technical Explanation
A production Celery architecture consists of 4 distinct components:
1. **Producer:** The web application (Django or FastAPI) that initiates a task by calling `.delay(*args, **kwargs)` or `.apply_async()`.
2. **Message Broker:** The intermediary queue (RabbitMQ or Redis) that stores serialized task messages (`task_id`, function name, arguments) until a worker is ready.
3. **Workers:** Independent OS processes or container pods running `celery -A proj worker` that continuously pull messages from the broker, execute the Python function, and acknowledge completion.
4. **Result Backend (Optional):** A database or cache (Redis, PostgreSQL) storing the status (`PENDING`, `SUCCESS`, `FAILURE`) and return value of completed tasks.

#### 5. Practical Python Implementation

```python
# tasks.py
from celery import Celery
import time

# Configure Celery with Redis as Broker and Result Backend
app = Celery(
    "invoice_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@app.task(bind=True, max_retries=3)
def generate_gst_invoice(self, user_id: int, invoice_id: str):
    """
    Simulates a heavy 5-second PDF generation and email sending task.
    """
    try:
        print(f"[Worker] Starting invoice generation for {invoice_id}...")
        time.sleep(5) # Simulating heavy PDF generation
        print(f"[Worker] Invoice {invoice_id} generated and emailed!")
        return {"status": "SUCCESS", "invoice_url": f"https://s3.aws.com/invoices/{invoice_id}.pdf"}
    except Exception as exc:
        # Exponential backoff retry: 5s, 10s, 20s
        countdown = 5 * (2 ** self.request.retries)
        print(f"[Worker] Error! Retrying in {countdown} seconds...")
        raise self.retry(exc=exc, countdown=countdown)
```

**Dispatching the Task from FastAPI:**
```python
# main.py
from fastapi import FastAPI
from tasks import generate_gst_invoice

api = FastAPI()

@api.post("/invoices/generate")
def create_invoice(invoice_id: str, user_id: int):
    # .delay() is non-blocking! Returns in < 5ms
    task = generate_gst_invoice.delay(user_id=user_id, invoice_id=invoice_id)
    return {"message": "Invoice generation started", "task_id": task.id}
```

#### 6. Code Explanation
- `Celery("invoice_tasks", broker=...)`: Instantiates the Celery app pointing to Redis database `0` for queues and database `1` for results.
- `@app.task(bind=True)`: `bind=True` grants the function access to `self` (the task instance), allowing programmatic retries with `self.retry()`.
- `generate_gst_invoice.delay(...)`: Serializes the task call into JSON and pushes it to the Redis list `celery`. The FastAPI endpoint finishes immediately without waiting 5 seconds.

#### 7. Internal Message Delivery Flow
1. FastAPI calls `task.delay()`.
2. Celery serializes payload: `{"task": "tasks.generate_gst_invoice", "id": "uuid-1234", "args": [101, "INV-9901"]}`.
3. Message is pushed via `LPUSH celery <json>` to Redis.
4. An idle Celery worker process executes `BRPOP celery` to pop the task atomically.
5. Worker executes the Python function inside an isolated worker process thread.
6. Worker issues an acknowledgment (ACK) to the broker and writes the result to Redis.

#### 8. Real-World Indian Production Scenarios
- **Bulk WhatsApp / SMS OTP Notification:** Processing 10,000 festival promotion SMS messages on Swiggy or Meesho without slowing down checkout APIs.
- **Payment Reconciliation:** Reconciling daily bank settlement sheets against merchant transactions at 2:00 AM every night using **Celery Beat**.
- **Video & Image Transcoding:** Resizing user-uploaded product images into thumbnails.

#### 9. Common Mistakes to Avoid
- *Mistake:* Passing massive complex objects (like a Django Model instance or an open file handler) as task arguments.  
  *Fix:* Only pass **primitive IDs** (`user_id=42`, `order_id=9801`). Let the Celery worker fetch the fresh record from the database itself.
- *Mistake:* Forgetting to make tasks **Idempotent**. If a task is retried after a temporary network timeout, it must not bill the customer twice or send two duplicate emails.

---

### CEL-INT-002: How do you prevent duplicate task execution (Task Deduplication)?

**Difficulty:** Intermediate  
**Topic:** Celery Reliability & Idempotency

#### The Solution: Redis Distributed Lock Key

```python
import redis
from celery import Celery

app = Celery("dedup_tasks", broker="redis://localhost:6379/0")
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.task(bind=True)
def process_order_payment(self, order_id: str):
    lock_key = f"celery:lock:order:{order_id}"

    # Try acquiring lock with 30-second TTL
    is_locked = redis_client.set(lock_key, "active", nx=True, ex=30)
    if not is_locked:
        print(f"[Warning] Duplicate task detected for order {order_id}! Skipping.")
        return {"status": "SKIPPED_DUPLICATE"}

    try:
        # Execute business logic (debit bank account, update order status)
        print(f"[Processing] Debiting payment for order {order_id}...")
        return {"status": "COMPLETED"}
    finally:
        redis_client.delete(lock_key) # Release lock when finished
```
