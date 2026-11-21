# SQLite Architecture, WAL Mode & Embedded Databases Guide

## Module Overview
This module covers **SQLite Architecture**, serverless embedded storage, **Write-Ahead Logging (WAL)** mode, and Python concurrency limits.

---

## Questions & Comprehensive Solutions

### SQLITE-BAS-001: What makes SQLite different from Client-Server Databases?

**Comparison Table:**

| Feature | SQLite | Client-Server (PostgreSQL / MySQL) |
| :--- | :--- | :--- |
| **Architecture** | **Serverless / Embedded**: Runs directly inside application process | Client-Server: Separate server daemon over TCP/IP |
| **Storage Model** | Entire database is stored in a **single disk file** (`db.sqlite3`) | Complex directory structures across tablespaces and raw pages |
| **Concurrency** | Single writer at a time; multiple concurrent readers in WAL mode | Thousands of concurrent writers via row-level MVCC |
| **Network Latency** | **Zero Network Overhead**: In-process function call | ~1ms network round-trip time |
| **Best Used For** | Mobile apps, CLI tools, local dev, embedded devices, unit tests | High-concurrency web services, multi-user SaaS |

---

### SQLITE-INT-002: Enabling WAL Mode for High Read Concurrency

By default, writing to SQLite locks the entire database file, blocking readers. Enabling **WAL Mode (Write-Ahead Logging)** allows multiple readers to read concurrently while one writer writes:

```python
import sqlite3

conn = sqlite3.connect("app.db")
# Enable WAL Mode
conn.execute("PRAGMA journal_mode = WAL;")
conn.commit()
```
