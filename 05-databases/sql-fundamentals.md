# SQL Fundamentals, Joins & Advanced Window Functions Guide

## Module Overview
This module covers core **SQL Querying**, **SQL Joins**, **Common Table Expressions (CTEs)**, and **Advanced Window Functions** essential for database engineering and technical interview rounds.

---

## Visual Architecture: SQL Joins Venn Diagram & Venn Data Flow

```mermaid
flowchart TD
    subgraph INNER_JOIN["INNER JOIN: Matching rows in BOTH tables"]
        A1[Table A] --- AB1[(Matching Records)] --- B1[Table B]
    end

    subgraph LEFT_JOIN["LEFT JOIN: ALL rows from A + matches from B"]
        A2[Table A: All Rows] --> Merge2[(Keeps all A; fills NULL for missing B)] <-- B2[Table B: Matches]
    end

    subgraph FULL_OUTER["FULL OUTER JOIN: All rows from BOTH tables"]
        A3[Table A] <--> AB3[(All Rows from A and B; NULL where no match)] <--> B3[Table B]
    end
```

---

## Questions & Comprehensive Solutions

### SQL-BAS-001: SQL Joins Explained (INNER, LEFT, RIGHT, FULL, CROSS)

**Comparison Table:**

| Join Type | Description | Handling of Unmatched Rows |
| :--- | :--- | :--- |
| **`INNER JOIN`** | Returns only rows where there is a match in **both** tables | Discards unmatched rows from both tables |
| **`LEFT JOIN`** | Returns **all** rows from left table, plus matched rows from right table | Unmatched right table columns are populated with `NULL` |
| **`RIGHT JOIN`** | Returns **all** rows from right table, plus matched rows from left table | Unmatched left table columns are populated with `NULL` |
| **`FULL OUTER JOIN`** | Returns all rows when there is a match in **either** left or right table | Unmatched columns on either side become `NULL` |
| **`CROSS JOIN`** | Produces the **Cartesian Product** of both tables ($M \times N$ rows) | Combines every row of Table A with every row of Table B |

```sql
-- Finding users who have NEVER placed an order (Classic Interview Pattern):
SELECT u.id, u.email
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

---

### SQL-INT-002: Window Functions: `ROW_NUMBER()` vs `RANK()` vs `DENSE_RANK()`

**One-Line Answer:**  
**Window functions** perform calculations across a set of table rows related to the current row without collapsing the rows into a single group (unlike `GROUP BY`).

#### Comparison Table (Scenario: Scores of 100, 100, 90, 80):

| Function | Values for (100, 100, 90, 80) | Gap in Sequence? | Handling of Ties |
| :--- | :--- | :---: | :--- |
| **`ROW_NUMBER()`** | `1, 2, 3, 4` | No | Assigns arbitrary sequential numbering to ties |
| **`RANK()`** | `1, 1, 3, 4` | **Yes (skips rank 2)** | Same rank for ties; skips subsequent numbers |
| **`DENSE_RANK()`** | `1, 1, 2, 3` | **No (no skips)** | Same rank for ties; does **not** skip subsequent numbers |

#### Classic Interview Problem: Find the 2nd Highest Salary in Each Department:

```sql
WITH RankedSalaries AS (
    SELECT 
        department_id,
        employee_id,
        salary,
        DENSE_RANK() OVER (
            PARTITION BY department_id 
            ORDER BY salary DESC
        ) as salary_rank
    FROM employees
)
SELECT department_id, employee_id, salary
FROM RankedSalaries
WHERE salary_rank = 2;
```

---

### SQL-INT-003: Common Table Expressions (CTEs) vs Subqueries

**Why CTEs (`WITH` clauses) are Preferred over Nested Subqueries:**
1. **Readability:** Flattens deeply nested subqueries from the inside-out into clean, sequential, top-to-bottom steps.
2. **Reusability:** A CTE can be referenced multiple times within the same query without re-typing.
3. **Recursive CTEs:** Enables querying hierarchical tree/graph structures (e.g. employee reporting hierarchies or category trees) that subqueries cannot solve.

```sql
-- Recursive CTE: Find all management subordinates under Manager ID 1
WITH RECURSIVE OrgChart AS (
    -- Anchor member
    SELECT employee_id, manager_id, name, 1 as level
    FROM employees
    WHERE manager_id = 1
    
    UNION ALL
    
    -- Recursive member
    SELECT e.employee_id, e.manager_id, e.name, o.level + 1
    FROM employees e
    INNER JOIN OrgChart o ON e.manager_id = o.employee_id
)
SELECT * FROM OrgChart ORDER BY level, name;
```
