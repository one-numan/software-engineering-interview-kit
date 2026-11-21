# Junior Software Engineer Mock Interview (0–2 Years Experience)

**Target Roles:** Junior Python Developer, Backend SDE-1, Associate Software Engineer  
**Target Companies:** Indian IT Services (TCS Digital/Ninja, Infosys DSE/SE, Wipro, Cognizant), Tech Consultancies, and Early-Stage Startups  
**Interview Duration:** 60 Minutes  
**Focus Areas:** Python Fundamentals, OOP, Basic SQL, REST API Essentials, Problem Solving  

---

## Interview Rubric & Scoring Criteria

| Dimension | Weight | Target Competency for Junior Level |
|---|---|---|
| **Python Core** | 30% | Clear mental model of mutability, standard collections, scope, and memory. |
| **SQL & Databases** | 25% | Ability to write correct JOINs, aggregations, and understand primary/foreign keys. |
| **API & Web Basics** | 20% | Understanding of HTTP methods, status codes, and JSON structure. |
| **Problem Solving** | 15% | Translating requirements into bug-free Python code with edge-case awareness. |
| **Communication** | 10% | Articulating thoughts, asking clarifying questions, and explaining complexity. |

---

## Section 1: Python Core Fundamentals (20 Minutes)

### Question 1.1: Mutability & Default Arguments
**Interviewer:**  
"Can you look at this Python code snippet and tell me what it prints, and why?"

```python
def append_to_list(element, target_list=[]):
    target_list.append(element)
    return target_list

print(append_to_list(10))
print(append_to_list(20))
```

**Candidate Answer:**  
"The first call will print `[10]`, but the second call will print `[10, 20]`, not just `[20]`.

This happens because in Python, default argument expressions are evaluated **once at function definition time**, when the function object is compiled, not each time the function is called. Because a Python list is a mutable object, all subsequent calls that omit the second argument reuse the exact same list instance stored in the function's `__defaults__` tuple."

**Interviewer Follow-up:**  
"How would you rewrite this function following industry best practices?"

**Candidate Answer:**  
"I would use `None` as a sentinel default value, and instantiate a fresh list inside the function body if `None` is provided:"

```python
def append_to_list(element, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(element)
    return target_list
```

> **Interviewer Evaluation:** **Exceeds Expectations (5/5).** Immediately identified the underlying CPython mechanism (`__defaults__` evaluation at compile-time) and provided the idiomatic fix.

---

### Question 1.2: Lists vs Tuples and Memory Overhead
**Interviewer:**  
"What is the difference between a `list` and a `tuple` in Python? Why would you use a tuple when a list can do everything a tuple does?"

**Candidate Answer:**  
"There are three main differences:
1. **Mutability:** Lists are mutable; tuples are immutable. Once created, elements in a tuple cannot be reassigned, added, or removed.
2. **Dictionary Keys:** Because tuples are immutable (provided their elements are also hashable), they implement `__hash__()` and can be used as dictionary keys or stored in sets. Lists cannot.
3. **Memory and Performance:** Tuples have lower memory overhead than lists. CPython lists allocate extra space to achieve amortized $O(1)$ appends (`list_resize` over-allocation). Tuples are allocated with the exact fixed size required. Furthermore, CPython optimizes small tuples through a free-list cache, making tuple creation faster."

> **Interviewer Evaluation:** **Strong Pass (4.5/5).** Good technical depth mentioning over-allocation and hashability constraints.

---

## Section 2: SQL & Relational Databases (15 Minutes)

### Question 2.1: Writing a Practical JOIN Query
**Interviewer:**  
"Given two tables: `employees (id, name, department_id, salary)` and `departments (id, dept_name)`, write a SQL query to return every department's name along with the total number of employees working in it, including departments that currently have zero employees."

**Candidate Answer:**  
"Because we need to include departments with zero employees, an `INNER JOIN` would incorrectly filter them out. We must use a `LEFT JOIN` starting from the `departments` table, and use `COUNT(e.id)` instead of `COUNT(*)` so null matches count as 0:"

```sql
SELECT 
    d.dept_name,
    COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.dept_name
ORDER BY employee_count DESC;
```

**Interviewer Follow-up:**  
"Why is `COUNT(e.id)` different from `COUNT(*)` in this query?"

**Candidate Answer:**  
"`COUNT(*)` counts total rows in the grouped result set, including rows where employee columns are `NULL`. If a department has no employees, `COUNT(*)` would return 1 because the department row exists in the left join. In contrast, `COUNT(e.id)` only counts non-NULL values, correctly returning 0."

> **Interviewer Evaluation:** **Exceeds Expectations (5/5).** Distinguished between `COUNT(*)` and `COUNT(column)` in an outer join context, which trips up many freshers.

---

## Section 3: REST API & Web Basics (10 Minutes)

### Question 3.1: HTTP Status Codes & Verbs
**Interviewer:**  
"When designing a REST API:
1. What HTTP verb and status code do you return when a resource is successfully created?
2. What is the difference between HTTP `401 Unauthorized` and `403 Forbidden`?"

**Candidate Answer:**  
"1. When creating a resource, you use `POST`, and the response status should be `201 Created`, typically accompanied by a `Location` header pointing to the new resource URL.
2. The difference between 401 and 403:
   - `401 Unauthorized` specifically means **Unauthenticated**. The client has not supplied valid credentials (e.g. missing or expired JWT token). The client can retry with valid credentials.
   - `403 Forbidden` means **Unauthorized / Permission Denied**. The server knows who the client is, but that identity does not have sufficient privileges to access the resource (e.g., a regular customer trying to delete another user's account). Providing credentials again will not change the outcome."

> **Interviewer Evaluation:** **Strong Pass (5/5).** Crisp, accurate distinction between authentication and authorization.

---

## Section 4: Live Coding Challenge (15 Minutes)

### Problem: First Non-Repeating Character
**Interviewer:**  
"Write a Python function that takes a string (e.g. `'swiggydelivery'`) and returns the index of the first character that does not repeat. If all characters repeat, return `-1`. What is the time and space complexity?"

**Candidate Implementation:**

```python
def first_unique_char(s: str) -> int:
    """
    Finds index of the first non-repeating character in a string.
    Time Complexity: O(N) where N is length of string.
    Space Complexity: O(1) bounded by alphabet size (at most 26 lowercase letters).
    """
    if not s:
        return -1

    # Pass 1: Build frequency map
    frequency: dict[str, int] = {}
    for char in s:
        frequency[char] = frequency.get(char, 0) + 1

    # Pass 2: Iterate through string preserving original order
    for idx, char in enumerate(s):
        if frequency[char] == 1:
            return idx

    return -1
```

**Candidate Test Walkthrough:**
- Input: `"swiss"` -> Frequencies: `{'s': 3, 'w': 1, 'i': 1}`. First char with freq 1 is `'w'` at index 1.
- Input: `"aabb"` -> Frequencies: `{'a': 2, 'b': 2}` -> returns `-1`.
- Input: `""` (Empty string) -> Handled by guard clause, returns `-1`.

> **Interviewer Evaluation:** **Pass (5/5).** Clean two-pass $O(N)$ algorithm, accounted for empty string edge case, correctly analyzed bounded auxiliary space.

---

## Final Assessment & Summary

- **Overall Recommendation:** **Strong Hire (SDE-1 / Junior Backend Engineer)**
- **Candidate Strengths:** Strong grasp of Python memory semantics, excellent SQL fundamentals, clean code structure with edge case handling.
- **Growth Areas:** Practice asynchronous Python (`asyncio`) and basic Docker containerization for production readiness.
