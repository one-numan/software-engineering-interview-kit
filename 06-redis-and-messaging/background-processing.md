# Background Processing & Event-Driven Architecture Guide

## Module Overview
This guide covers architectural patterns for **asynchronous background processing**, **event-driven design**, **worker autoscaling (KEDA)**, and handling extreme traffic spikes in production web systems.

---

## Architectural Comparison: Synchronous vs Asynchronous Processing

```mermaid
flowchart TD
    subgraph Synchronous_AntiPattern["1. Synchronous Blocking Request (Fragile)"]
        Client1[Client] -->|HTTP POST /order| Web1[Web Server]
        Web1 -->|Wait 4s| DB1[(PostgreSQL)]
        Web1 -->|Wait 3s| SMS1[External SMS Gateway]
        Web1 -->|Wait 5s| PDF1[Generate PDF Invoice]
        Web1 -->|Total: 12 seconds!| Client1
    end

    subgraph Asynchronous_Pattern["2. Asynchronous Decoupled Processing (Scalable)"]
        Client2[Client] -->|HTTP POST /order| Web2[Web Server]
        Web2 -->|Save Order < 20ms| DB2[(PostgreSQL)]
        Web2 -->|Publish Event < 5ms| Queue[(Message Queue: RabbitMQ / Redis)]
        Web2 -->|Total: 25ms - 202 Accepted| Client2
        
        Queue --> WorkerPool[Background Worker Fleet: Celery]
        WorkerPool -.-> AsyncSMS[Send SMS]
        WorkerPool -.-> AsyncPDF[Generate PDF]
    end
```

---

## Core Questions & Comprehensive Solutions

### BKG-BAS-001: When should an operation be offloaded to a background task?

**Difficulty:** Basic  
**Topic:** Architectural Decision Making

#### Decision Framework: The Rule of 200ms
Any operation that meets one of the following criteria should **never** run synchronously inside an HTTP request handler:
1. **Third-Party Network Calls:** Sending emails (SendGrid/SES), SMS OTPs (Twilio), push notifications (Firebase), or calling external bank APIs where latency is uncontrollable.
2. **CPU-Intensive Tasks:** Image resizing, video transcoding, PDF generation, or calculating machine learning inferences.
3. **Heavy I/O & Batch Operations:** Importing a CSV file with 50,000 rows, exporting financial reports, or bulk updating search indexes.
4. **Non-Critical Side Effects:** Logging audit analytics, updating recommendation engines, or sending Slack alerts to internal teams.

---

### BKG-INT-002: How do you autoscale background workers based on queue depth?

**Difficulty:** Intermediate  
**Topic:** DevOps & Cloud Scaling

#### 1. Why CPU-Based Autoscaling Fails for Workers
Standard Kubernetes HPA (Horizontal Pod Autoscaler) scales based on CPU utilization. However, a queue with 500,000 pending tasks might have workers whose CPU is low because they are waiting on network I/O. As a result, the cluster never scales up, and queue lag grows uncontrollably.

#### 2. The Solution: KEDA (Kubernetes Event-driven Autoscaling)
**KEDA** monitors the queue directly (measuring message count in RabbitMQ or list length in Redis).
- If Queue Length = 0 $\rightarrow$ Scale workers down to 1 or 0 (saving cloud costs).
- If Queue Length > 1,000 $\rightarrow$ Rapidly scale worker pods from 2 to 50.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: celery-worker-scaler
spec:
  scaleTargetRef:
    name: celery-worker-deployment
  minReplicaCount: 1
  maxReplicaCount: 30
  triggers:
  - type: rabbitmq
    metadata:
      protocol: amqp
      queueName: celery
      mode: QueueLength
      value: "50" # Scale up 1 worker for every 50 pending messages
```
