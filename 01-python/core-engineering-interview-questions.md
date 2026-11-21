# Python Core Engineering Interview Questions & Answers

## Overview
This guide provides direct, production-grade, and beginner-friendly answers to the **12 Core Python Engineering Questions** most frequently asked in senior backend and software architecture interviews.

---

## 1. List vs Tuple vs Set vs Dictionary

### Simple Explanation
These are Python's 4 built-in collection data structures, each optimized for different data organization needs.

### Comparison Table

| Data Structure | Syntax | Ordered? | Mutable? | Allows Duplicates? | Under-the-hood Implementation | Lookup Complexity |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **List** | `[1, 2, 3]` | :white_check_mark: Yes | :white_check_mark: Yes | :white_check_mark: Yes | Dynamic array of pointers (`PyListObject`) | $O(1)$ by index, $O(n)$ by value |
| **Tuple** | `(1, 2, 3)` | :white_check_mark: Yes | :x: No (Immutable) | :white_check_mark: Yes | Fixed-size array (`PyTupleObject`) | $O(1)$ by index, $O(n)$ by value |
| **Set** | `{1, 2, 3}` | :x: No | :white_check_mark: Yes | :x: No (Unique only) | Hash Table (`PySetObject`, keys only) | $O(1)$ average membership check |
| **Dictionary**| `{"a": 1}` | :white_check_mark: Yes (3.7+) | :white_check_mark: Yes | Keys: No, Values: Yes | Combined Hash Table (`PyDictObject`) | $O(1)$ average key lookup |

### One-Line Interview Answer
**Lists** are mutable dynamic arrays, **Tuples** are immutable fixed sequences (hashable if elements are immutable), **Sets** are unordered collections of unique elements based on hash tables, and **Dictionaries** are key-value associative hash maps.

---

## 2. What are Decorators?

### Simple Explanation
A **Decorator** is a function that takes another function as an input, adds extra functionality to it (like logging, authentication, or timing), and returns the modified function without changing the original function's source code.

### Easy Real-World Example
Think of putting a mobile phone inside a waterproof cover:
The phone is the original function. The cover is the decorator. The phone still makes calls, but now it can also work underwater without changing its internal circuitry.

### One-Line Interview Answer
A **decorator** is a callable that accepts a function object and dynamically extends or modifies its behavior using higher-order function closures.

### Practical Code Example

```python
import time
from functools import wraps

def time_tracker(func):
    @wraps(func) # Preserves original function name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"[Timing] {func.__name__} took {duration:.4f} seconds")
        return result
    return wrapper

@time_tracker
def compute_heavy_task(n: int):
    return sum(i * i for i in range(n))

compute_heavy_task(1_000_000)
```

---

## 3. What are Generators and Yield?

### Simple Explanation
A normal function runs to completion and returns all its results at once (e.g. returning a list of 10 million items, which consumes 800 MB of RAM).  
A **Generator** uses the `yield` keyword to return items **one by one on demand (lazy evaluation)**, pausing its state between items and consuming almost zero RAM ($O(1)$ memory).

### One-Line Interview Answer
A **generator** is a memory-efficient iterator produced by functions containing `yield`, maintaining its local execution frame state across calls via the Python iteration protocol (`__iter__` and `__next__`).

### Practical Code Example

```python
def read_massive_log_file(file_path: str):
    """Memory-efficient log reader: reads 1 line at a time instead of 10GB into RAM"""
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

# Memory consumption remains constant at < 50 KB even for a 100 GB file!
for error_log in read_massive_log_file("server.log"):
    print(f"Alert: {error_log}")
```

---

## 4. What is the GIL (Global Interpreter Lock)?

### Simple Explanation
In standard Python (CPython), the **GIL** is a master safety lock that allows only **one OS thread at a time** to execute Python bytecode, even on a machine with 64 CPU cores.

### Why does Python have the GIL?
CPython's internal memory manager uses **Reference Counting**. Without the GIL, multiple threads modifying object reference counters simultaneously would trigger race conditions and memory corruption.

### One-Line Interview Answer
The **GIL (Global Interpreter Lock)** is a mutual exclusion lock in CPython that prevents multiple native threads from executing Python bytecodes in parallel, ensuring thread-safe reference counting.

<u>Interview Tip:</u> Explain that the GIL restricts **CPU-bound tasks** (like heavy math or machine learning loops), but releases its lock during **I/O-bound tasks** (network requests, database queries, reading disk files).

---

## 5. Multithreading vs Multiprocessing?

### Comparison Table

| Feature | Multithreading (`threading`) | Multiprocessing (`multiprocessing`) |
| :--- | :--- | :--- |
| **Process Model** | Multiple threads inside **one OS process** | Multiple **separate OS processes** |
| **Memory Space** | Shared memory space | Separate, isolated memory space (requires IPC / Pickle) |
| **Impact of GIL** | Bound by GIL (no true CPU parallelism in CPython) | **Bypasses GIL** (each process has its own Python interpreter) |
| **Context Switch Overhead**| Low overhead (shares memory) | Higher overhead (OS process context switching) |
| **Best Used For** | **I/O-bound tasks** (web scraping, downloading files) | **CPU-bound tasks** (image processing, data crunching) |

---

## 6. Asyncio vs Threading?

### Simple Explanation
- **Threading (Preemptive Multitasking):** The Operating System decides when to switch between threads, pausing them forcefully at any arbitrary instruction.
- **Asyncio (Cooperative Multitasking):** A single Python thread runs an **Event Loop**. A task runs until it hits an `await` keyword (e.g. waiting for a database response), at which point it **voluntarily yields control** to the event loop to run another task.

### One-Line Interview Answer
**Threading** uses OS-level threads scheduled preemptively by the kernel, while **Asyncio** uses a single-threaded event loop with user-space coroutines that yield control cooperatively via `await`.

---

## 7. What are Python Memory Management Mechanisms?

### Detailed Explanation
CPython manages memory through 3 coordinated tiers:
1. **Raw Memory Allocator (`malloc` / `PyMem_Malloc`):** Allocates memory from the OS.
2. **PyMalloc (Small Object Allocator):** For small objects ($\le 512$ bytes), PyMalloc organizes memory into **Arenas (256 KB)**, **Pools (4 KB)**, and **Blocks (multiples of 8 bytes)** to eliminate OS fragmentation.
3. **Reference Counting (Primary Collector):** Every object stores `ob_refcnt`. When reference count drops to 0, memory is freed immediately.
4. **Cyclic Garbage Collector (Secondary Collector):** Detects circular references (e.g. `a.b = b; b.a = a`) using 3 generational heaps (Generation 0, 1, 2) and tri-color mark-and-sweep.

---

## 8. Shallow Copy vs Deep Copy?

### Simple Explanation
- **Shallow Copy (`copy.copy(x)`):** Creates a new container, but inserts references to the *same* child objects. Modifying a nested list affects both copies.
- **Deep Copy (`copy.deepcopy(x)`):** Recursively creates a new container AND duplicates all nested child objects inside it. Modifying one copy has zero effect on the other.

```python
import copy

original = [[1, 2, 3], [4, 5, 6]]
shallow = copy.copy(original)
deep = copy.deepcopy(original)

original[0][0] = 999
print(shallow[0][0]) # 999 (Modified! Shared nested reference)
print(deep[0][0])    # 1 (Intact! Truly independent clone)
```

---

## 9. What are Closures?

### One-Line Answer
A **Closure** is a nested inner function that retains access to variables in its enclosing scope even after the outer function has finished executing.

```python
def make_multiplier(factor: int):
    def multiply(n: int) -> int:
        return n * factor # 'factor' is retained in closure cell (__closure__)
    return multiply

double = make_multiplier(2)
print(double(10)) # Output: 20
```

---

## 10. What are Context Managers?

### One-Line Answer
A **Context Manager** is an object that manages runtime resource setup and cleanup via the `with` statement by implementing `__enter__()` and `__exit__()` (or `@contextmanager`).

```python
from contextlib import contextmanager

@contextmanager
def db_transaction():
    print("BEGIN TRANSACTION")
    try:
        yield
        print("COMMIT TRANSACTION")
    except Exception as e:
        print(f"ROLLBACK TRANSACTION due to {e}")
        raise
```

---

## 11. How does Exception Handling work in Python?

### One-Line Answer
Exception handling uses `try...except...else...finally` blocks where:
- `except` catches specific `Exception` subclasses.
- `else` executes **only** if no exception occurred in the `try` block.
- `finally` **always** executes, guaranteeing resource cleanup even if `return` or unhandled errors occur.

---

## 12. How do you optimize Python applications?

### Top 5 Optimization Strategies:
1. **Algorithmic Complexity First:** Replace $O(n^2)$ nested loops with $O(1)$ dictionary/set hash lookups.
2. **Use Built-in C Implementations:** Use `collections.deque` for queues and `itertools` for iteration.
3. **Memory Optimization with `__slots__`:** In classes instantiated millions of times, declare `__slots__ = ('x', 'y')` to eliminate the default instance `__dict__`, reducing memory by up to 60%.
4. **Asynchronous Non-Blocking I/O:** Use FastAPI and `asyncio` (`httpx.AsyncClient`, `asyncpg`) to handle thousands of concurrent I/O connections.
5. **C/Rust Extensions / Cython / PyPy:** For extreme mathematical bottlenecks, compile with Cython or offload to PyO3 (Rust extensions).
