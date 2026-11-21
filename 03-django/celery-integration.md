# Django & Celery Integration Guide

## Module Overview
This guide covers integrating **Celery with Django**, configuring `django-celery-beat` for database-backed cron schedules, and handling database connections across forked worker processes.

---

## Visual Architecture: Django + Celery Production Runtime Topology

```mermaid
flowchart LR
    subgraph Django_Web_Container["Django Web Server (Gunicorn)"]
        View[Checkout View] -->|order.save()| DB[(PostgreSQL)]
        View -->|send_receipt.delay(order.id)| Broker[(Redis Broker)]
    end

    subgraph Celery_Worker_Container["Celery Worker Fleet"]
        Broker -->|Pulls Task| Worker[Celery Worker Process]
        Worker -->|Reads order details| DB
        Worker -->|Sends email| SES[AWS SES / SMTP Gateway]
    end

    subgraph Celery_Beat["Celery Beat Scheduler"]
        Beat[Beat Process] -->|Cron schedule| Broker
    end
```

---

## Production Setup & Configuration

### 1. Project Initialization (`myproject/celery.py`)
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 2. Ensuring Database Safety in Workers
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db' # Stores task status in Django ORM table
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60 # Force terminate tasks running longer than 30 mins
CELERY_ACKS_LATE = True # Acknowledge task ONLY after it finishes successfully!
```
