# Database Management Systems (DBMS) Fundamentals Guide

## Module Overview
This module covers fundamental **Database Management Systems (DBMS)** theory, **Relational vs NoSQL trade-offs**, file storage organization, and concurrency control.

---

## Relational (RDBMS) vs NoSQL Comparison

| Dimension | Relational Database (SQL) | NoSQL (Document / Key-Value / Columnar) |
| :--- | :--- | :--- |
| **Data Model** | Fixed tabular schemas with rows and columns | Flexible schemas (JSON documents, key-value pairs, wide-column) |
| **Transaction Model**| **Strict ACID** (Atomicity, Consistency, Isolation, Durability) | **BASE** (Basically Available, Soft state, Eventual consistency) |
| **Scaling Model** | Primarily **Vertical** (Read replicas provide read scaling) | Built natively for **Horizontal Scaling (Sharding)** |
| **Relationships** | First-class `JOIN` operations | Joins are discouraged or unsupported (denormalized nested objects) |
| **Examples** | PostgreSQL, MySQL, SQLite | MongoDB, Redis, Apache Cassandra, DynamoDB |

---

## File Organization: Heap Files vs Clustered Indexes

- **Heap File Organization:** Rows are written wherever there is free space in disk pages. Searching requires scanning the entire table unless an index exists.
- **Clustered Index Organization (e.g. MySQL InnoDB):** Table rows are physically stored on disk in the exact sorted order of the Primary Key B+Tree.
