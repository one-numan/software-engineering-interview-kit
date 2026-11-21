# WebSockets & Real-Time Communication Interview Guide

## Module Overview
This module covers **WebSockets**, the WebSocket protocol handshake (`Upgrade: websocket`), **WebSockets vs SSE vs Long Polling**, and **Horizontal Scaling using Redis Pub/Sub**.

---

## Visual Comparison: Real-Time Protocols

```mermaid
flowchart TD
    subgraph Short_Polling["1. Short Polling (High Waste)"]
        C1[Client] -->|HTTP GET every 1s| S1[Server]
        S1 -->|No new data| C1
    end

    subgraph Server_Sent_Events["2. Server-Sent Events - SSE (Unidirectional)"]
        C2[Client] -->|Single HTTP Request| S2[Server]
        S2 -->|Stream Data Chunk 1| C2
        S2 -->|Stream Data Chunk 2| C2
        Note1[Best for LLM token streaming & live dashboards]
    end

    subgraph WebSockets["3. WebSockets (Bidirectional Full-Duplex)"]
        C3[Client] <-->|HTTP 101 Switching Protocols| S3[Server]
        C3 <-->|Frame: Client to Server| S3
        S3 <-->|Frame: Server to Client| C3
        Note2[Best for multiplayer gaming, live chat, trading apps]
    end
```

---

## Questions & Comprehensive Solutions

### WS-BAS-001: WebSockets vs Server-Sent Events (SSE) vs Long Polling

**Comparison Matrix:**

| Feature | Long Polling | Server-Sent Events (SSE) | WebSockets |
| :--- | :--- | :--- | :--- |
| **Protocol** | Standard HTTP | Standard HTTP (`text/event-stream`) | **`ws://` / `wss://` (TCP-based)** |
| **Direction** | Client $\rightarrow$ Server | **Server $\rightarrow$ Client Only (Unidirectional)** | **Full-Duplex (Bidirectional)** |
| **Header Overhead** | Massive: Full HTTP headers sent on every request | Low: Single HTTP header at connection setup | **Minimal: 2 to 6 bytes per frame** after handshake |
| **Reconnection** | Handled manually in app logic | Built-in native browser auto-reconnect | Handled manually in client code |
| **HTTP/2 Compatibility**| Standard | Supported natively over single multiplexed TCP | Supported via RFC 8441 |
| **Best Used For** | Legacy fallback systems | **LLM token streaming, stock tickers, notification feeds** | **Live chat apps, multiplayer gaming, collaborative whiteboards** |

---

### WS-INT-002: How do you scale WebSockets horizontally across multiple server instances?

**Difficulty:** Advanced  
**Topic:** Real-Time Distributed Systems

#### The Problem:
WebSockets maintain a **persistent, stateful TCP connection** to a specific server instance. If User A is connected to Server 1 and User B is connected to Server 2, Server 1 cannot directly send a message to User B because the socket connection lives on Server 2's memory!

#### The Solution: Redis Pub/Sub Backplane (Message Broker)

```mermaid
flowchart TD
    subgraph Web_Tier["FastAPI WebSocket Cluster"]
        UserA([User A]) <--> S1[WebSocket Server 1]
        UserB([User B]) <--> S2[WebSocket Server 2]
    end

    subgraph Backplane["Redis Pub/Sub Message Broker"]
        S1 -->|1. PUBLISH chat_channel 'Hello'| RedisBroker[(Redis Pub/Sub)]
        RedisBroker -->|2. Broadcasts message| S1
        RedisBroker -->|2. Broadcasts message| S2
    end

    S2 -->|3. Forward message over WebSocket| UserB
```

#### Fast Python Implementation with FastAPI & Redis:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
import asyncio

app = FastAPI()
redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(room_id)

    async def redis_listener():
        """Listens to Redis messages and broadcasts down to client WebSocket"""
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"])
        except Exception:
            pass

    listener_task = asyncio.create_task(redis_listener())

    try:
        while True:
            # Reads incoming message from client and publishes to Redis
            text = await websocket.receive_text()
            await redis_client.publish(room_id, text)
    except WebSocketDisconnect:
        listener_task.cancel()
        await pubsub.unsubscribe(room_id)
```
