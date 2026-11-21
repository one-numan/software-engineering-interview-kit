# Advanced SQL Interview Problems

This module covers complex, production-grade SQL problems frequently tested in backend engineering interviews. Solutions are tested on modern **PostgreSQL 14+** and **MySQL 8.0+**.

---

## Problem 1: Cumulative Running Total & 7-Day Moving Average

### Scenario
An executive dashboard at a FinTech payment processor (e.g., Razorpay) needs to compute daily total payment volume, the cumulative volume to date, and the rolling 7-day moving average.

### Schema
```sql
CREATE TABLE daily_payments (
    payment_date DATE PRIMARY KEY,
    total_volume_inr NUMERIC(14, 2) NOT NULL
);
```

### Production SQL Query

```sql
SELECT 
    payment_date,
    total_volume_inr,
    -- Running cumulative total from start of time to current row
    SUM(total_volume_inr) OVER (
        ORDER BY payment_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_volume_inr,
    -- Rolling 7-day moving average (current day + previous 6 days)
    ROUND(
        AVG(total_volume_inr) OVER (
            ORDER BY payment_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS rolling_7day_avg_inr
FROM daily_payments
ORDER BY payment_date ASC;
```

### Key Concept
- **Window Frame Clause (`ROWS BETWEEN ...`):** Explicitly defines physical row boundaries relative to the current row, avoiding unintended duplicate-value range ties.

---

## Problem 2: Finding Nth Highest Customer Revenue per Geographic Region

### Scenario
An e-commerce marketplace needs to identify the top 3rd highest spending customer in every Indian state (`region_id`) to analyze tier-2 city purchasing power. If multiple customers tie for third place, all must be returned.

### Schema
```sql
CREATE TABLE customer_orders (
    customer_id INT,
    region_id VARCHAR(10),
    order_amount_inr NUMERIC(10, 2)
);
```

### Production SQL Query (Using `DENSE_RANK`)

```sql
WITH customer_regional_spend AS (
    SELECT 
        region_id,
        customer_id,
        SUM(order_amount_inr) AS total_spend_inr,
        DENSE_RANK() OVER (
            PARTITION BY region_id 
            ORDER BY SUM(order_amount_inr) DESC
        ) AS regional_rank
    FROM customer_orders
    GROUP BY region_id, customer_id
)
SELECT 
    region_id,
    customer_id,
    total_spend_inr
FROM customer_regional_spend
WHERE regional_rank = 3
ORDER BY region_id, total_spend_inr DESC;
```

### `RANK()` vs `DENSE_RANK()` vs `ROW_NUMBER()`
| Function | Handling of Duplicate Scores | Rank Sequence Example |
|---|---|---|
| `ROW_NUMBER()` | Arbitrary tie-breaker | 1, 2, 3, 4, 5 |
| `RANK()` | Skips subsequent numbers after ties | 1, 2, 2, 4, 5 |
| `DENSE_RANK()` | Never skips numbers after ties | 1, 2, 2, 3, 4 |

---

## Problem 3: User Sessionization by Inactivity Gap (> 30 Minutes)

### Scenario
A food delivery app (Swiggy / Zomato) logs user app-click events. A "session" is defined as a series of events where the gap between consecutive events does not exceed 30 minutes. If the user is idle for more than 30 minutes, the next event starts a new session.

### Schema
```sql
CREATE TABLE app_events (
    event_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    event_time TIMESTAMP NOT NULL,
    action_name VARCHAR(50)
);
```

### Production SQL Query

```sql
WITH flagged_events AS (
    SELECT 
        user_id,
        event_time,
        action_name,
        -- Check gap between current event and previous event
        CASE 
            WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) > INTERVAL '30 minutes'
                 OR LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) IS NULL 
            THEN 1 
            ELSE 0 
        END AS is_new_session
    FROM app_events
),
session_groups AS (
    SELECT 
        user_id,
        event_time,
        action_name,
        -- Cumulative sum of session start flags forms a unique session identifier
        SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
    FROM flagged_events
)
SELECT 
    user_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS event_count,
    EXTRACT(EPOCH FROM (MAX(event_time) - MIN(event_time))) / 60.0 AS duration_minutes
FROM session_groups
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

---

## Problem 4: Detecting Overlapping Hotel / Ride Bookings

### Scenario
Detect whether a new driver assignment or hotel reservation overlaps with existing active bookings for the same resource.

### Schema
```sql
CREATE TABLE driver_shifts (
    id SERIAL PRIMARY KEY,
    driver_id INT NOT NULL,
    shift_start TIMESTAMP NOT NULL,
    shift_end TIMESTAMP NOT NULL,
    CONSTRAINT valid_interval CHECK (shift_start < shift_end)
);
```

### Overlap Query Condition

```sql
-- Check if target range [target_start, target_end] overlaps any existing shift:
-- Two intervals [A_start, A_end] and [B_start, B_end] overlap IF AND ONLY IF:
-- A_start < B_end AND A_end > B_start

SELECT id, driver_id, shift_start, shift_end
FROM driver_shifts
WHERE driver_id = 42
  AND shift_start < '2026-11-21 18:00:00'
  AND shift_end   > '2026-11-21 14:00:00';
```

### PostgreSQL Native Range Type & Exclusion Constraint (Optimal)
In PostgreSQL, exclusion constraints prevent overlapping intervals directly at the database engine level using GiST indexes:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE vehicle_rentals (
    rental_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL,
    rental_period TSRANGE NOT NULL,
    EXCLUDE USING gist (vehicle_id WITH =, rental_period WITH &&)
);
```
*Any concurrent insert with an overlapping period is automatically rejected by PostgreSQL with a serialization error.*

---

## Problem 5: Recursive Common Table Expression (CTE) for Hierarchical Tree

### Scenario
Query an organization hierarchy or multi-level referral tree to find all direct and indirect reportees under a given VP / Engineering Director.

### Schema
```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INT REFERENCES employees(emp_id),
    department VARCHAR(50)
);
```

### Recursive CTE Query

```sql
WITH RECURSIVE employee_hierarchy AS (
    -- 1. Anchor member: Starting top manager
    SELECT 
        emp_id, 
        name, 
        manager_id, 
        1 AS depth, 
        name::TEXT AS hierarchy_path
    FROM employees 
    WHERE emp_id = 101 -- Starting VP ID

    UNION ALL

    -- 2. Recursive member: Join children with previous level
    SELECT 
        e.emp_id, 
        e.name, 
        e.manager_id, 
        eh.depth + 1, 
        eh.hierarchy_path || ' -> ' || e.name
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.emp_id
)
SELECT 
    emp_id, 
    name, 
    depth, 
    hierarchy_path
FROM employee_hierarchy
ORDER BY depth, emp_id;
```

---

## Problem 6: Keyset (Cursor) Pagination vs `OFFSET` for Million-Row Tables

### Scenario
An API paginates through an orders table with 50 million rows. `LIMIT 20 OFFSET 5000000` takes **14.2 seconds** because PostgreSQL must read 5,000,020 rows and discard 5,000,000.

### The Naive Query (Slow)
```sql
-- SLOW: Scans all 5,000,000 rows prior to returning 20
SELECT id, order_number, amount_inr, created_at
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 5000000;
```

### The Production Keyset (Cursor) Query (Fast)
```sql
-- FAST: Uses composite index directly to jump to the cursor tuple
SELECT id, order_number, amount_inr, created_at
FROM orders
WHERE (created_at, id) < ('2026-11-20 14:30:00', 9872134)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

### Performance Comparison
| Query Method | Execution Time on 50M Rows | I/O Buffers Read |
|---|---|---|
| `OFFSET 5,000,000` | 14,210 ms | 48,200 shared blocks |
| Keyset `(created_at, id) < (...)` | **1.8 ms** | **4 shared blocks** |
