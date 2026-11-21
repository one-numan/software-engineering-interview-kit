"""
mem_basic.py
============
Basic Memory Management Questions: PY-BAS-126 to PY-BAS-150 (25 questions)
"""

basic_data = [
    # PY-BAS-126
    (
        "PY-BAS-126",
        "How Python Manages Memory",
        "Python manages memory automatically via a private interpreter heap, using reference counting as its primary mechanism and a generational cyclic garbage collector for circular references.",
        "CPython abstracts system memory through three primary layers: the raw OS memory allocator (`malloc`/`free`), the Python core memory manager (`PyMem_Malloc`), and the object-specific allocator (`PyObject_Malloc` or `pymalloc`). Small objects (<= 512 bytes) are allocated within dedicated 256KB arenas subdivided into 4KB pools to eliminate OS allocation overhead and fragmentation. Every object maintains an internal reference counter. When an object's reference counter drops to zero, its memory is immediately deallocated or returned to pymalloc free lists. For cyclical references where counts never reach zero, a background generational cyclic garbage collector runs periodically.",
        "import sys\n\n# Creating an object on Python's private heap\ndata = [1, 2, 3]\nprint(f'Initial refcount: {sys.getrefcount(data)}')\n\nalias = data\nprint(f'Refcount after alias: {sys.getrefcount(data)}')\n\ndel alias\nprint(f'Refcount after del alias: {sys.getrefcount(data)}')",
        "Observing reference count changes as variables bind and unbind from an object on the heap.",
        "CPython structures all data as `PyObject` C structs. Memory allocation requests <= 512 bytes are routed to `pymalloc` which operates on pre-allocated 256KB arenas. Objects larger than 512 bytes bypass pymalloc and call system `malloc` directly.",
        "Understanding Python's private heap is critical when deploying microservices in memory-constrained Docker containers to prevent sudden Out-Of-Memory (OOM) kills.",
        ["What is the role of pymalloc vs standard OS malloc?", "Why doesn't Python return all freed memory back to the OS immediately?"],
        ["Assuming Python relies exclusively on a tracing garbage collector like Java or Go.", "Believing `del x` immediately frees RAM back to the OS kernel."],
        "Explain the two-tier model: immediate deterministic reference counting plus periodic cyclic garbage collection.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/c-api/memory.html"]
    ),

    # PY-BAS-127
    (
        "PY-BAS-127",
        "Reference Counting Mechanics",
        "Reference counting tracks the number of active references pointing to an object, deallocating it the instant its count drops to zero.",
        "Every Python object contains a header field named `ob_refcnt` defined in `PyObject`. The reference count increases whenever an object is assigned to a variable (`a = b`), stored in a container (`list.append(b)`), passed as an argument to a function, or bound to an attribute. The reference count decreases when an object's reference goes out of scope, a variable is reassigned (`a = None`), explicitly unbound via `del a`, or cleared from a collection. When `ob_refcnt` hits zero, the object's type deallocator (`tp_dealloc`) is executed immediately.",
        "import sys\n\nclass Resource:\n    def __init__(self, name: str):\n        self.name = name\n    def __del__(self):\n        print(f'Resource {self.name} deallocated!')\n\n# Create resource (refcount = 1)\nres = Resource('DB_Conn')\n# Pass to alias (refcount = 2)\nalias = res\nprint('Deleting alias...')\ndel alias\nprint('Deleting primary ref...')\ndel res  # Hits zero -> triggers immediate deallocation",
        "Demonstrating immediate, deterministic deallocation upon reference counter zeroing.",
        "In CPython, `Py_INCREF()` and `Py_DECREF()` macros increment and decrement `ob_refcnt`. When `Py_DECREF()` detects `ob_refcnt == 0`, it calls `_Py_Dealloc(op)`, which invokes `tp_dealloc` to free object attributes and recycle the memory block.",
        "Deterministic resource management: file descriptors and network sockets are closed immediately when their holding object goes out of scope in CPython.",
        ["What happens if two objects reference each other when their local variables are deleted?", "Why is reference counting thread-unsafe without the GIL?"],
        ["Assuming `del var` deletes the object rather than merely decrementing its reference count.", "Expecting other Python runtimes like Jython or PyPy to behave with deterministic reference counting."],
        "Emphasize that `del` deletes the name binding from the namespace, not the object itself.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/c-api/intro.html#reference-counts"]
    ),

    # PY-BAS-128
    (
        "PY-BAS-128",
        "sys.getrefcount() Behavior",
        "`sys.getrefcount(obj)` returns the current reference count of an object, which is always one higher than expected because passing `obj` into the function creates an ephemeral temporary reference.",
        "When an object is passed as an argument to `sys.getrefcount(obj)`, the function's internal stack frame binds a new local reference to that object, incrementing `ob_refcnt` by 1. For example, a newly created list bound to a single variable has an actual reference count of 1, but `sys.getrefcount()` reports 2. As soon as the call finishes and returns, the function's stack frame pops and the temporary reference count decrements back to 1.",
        "import sys\n\ntarget = [10, 20, 30]\n# Expected: 1 local variable + 1 from getrefcount argument = 2\nprint('Refcount:', sys.getrefcount(target))\n\nholders = [target, target]\n# Expected: 1 (target) + 2 (list slots) + 1 (getrefcount arg) = 4\nprint('Refcount with holders:', sys.getrefcount(target))",
        "Inspecting the temporary argument reference added by sys.getrefcount.",
        "CPython's C function `sys_getrefcount(PyObject *self, PyObject *args)` receives the object pointer inside its `args` tuple, which increments `ob_refcnt` during argument parsing and tuple binding.",
        "Debugging memory leaks in development scripts where tracking whether objects remain anchored in global data structures is required.",
        ["Why do small integers and short strings display huge reference counts in sys.getrefcount?", "How does ctypes inspect reference counts without incrementing them?"],
        ["Forgetting that `sys.getrefcount(x)` adds +1 to the actual count.", "Believing `sys.getrefcount()` is safe for production performance profiling (it introduces overhead)."],
        "Mention that `ctypes.c_long.from_address(id(obj)).value` can read `ob_refcnt` without creating a temporary reference.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/sys.html#sys.getrefcount"]
    ),

    # PY-BAS-129
    (
        "PY-BAS-129",
        "Garbage Collector Purpose",
        "Python's cyclic garbage collector (`gc` module) detects and reclaims isolated reference cycles that reference counting alone can never deallocate.",
        "Reference counting has a critical flaw: reference cycles. If Object A references Object B, and Object B references Object A, their reference counts can never drop to zero even if all external references from the program are removed. Without an auxiliary mechanism, these cyclic objects would leak memory indefinitely. CPython's `gc` module periodically scans container objects (lists, dictionaries, custom class instances, tuples containing mutables), executes a trial deletion algorithm to identify isolated subgraphs whose references are entirely internal, and frees them.",
        "import gc\n\nclass Node:\n    def __init__(self, val: int):\n        self.val = val\n        self.neighbor = None\n\n# Create reference cycle\na = Node(1)\nb = Node(2)\na.neighbor = b\nb.neighbor = a\n\n# Remove external references\ndel a\ndel b\n\n# Cycle remains in memory until cyclic GC collects it\nunreachable = gc.collect()\nprint(f'Unreachable cyclic objects collected: {unreachable}')",
        "Creating an isolated circular reference and demonstrating its recovery via cyclic GC.",
        "Atomic types (like integers, floats, and strings) cannot contain references to other objects and are not tracked by the cyclic GC. Only container objects tracked via `PyGC_Head` headers are inspected by the GC's generation lists.",
        "Long-running web servers (FastAPI/Django) handling tree or graph data structures (like DOM trees or ORM models) rely on cyclic GC to prevent gradual memory bloat.",
        ["Why doesn't the GC track atomic types like integers or strings?", "What is the computational overhead of cyclic garbage collection?"],
        ["Assuming the `gc` module is responsible for freeing all Python objects.", "Believing calling `gc.collect()` after every request improves web app performance."],
        "Emphasize that reference counting does 99% of deallocations; the cyclic GC only handles cyclic remnants.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/gc.html"]
    ),

    # PY-BAS-130
    (
        "PY-BAS-130",
        "Circular References",
        "A circular reference occurs when two or more objects reference each other directly or indirectly, keeping their reference counts strictly positive even when unreachable.",
        "In a reference cycle, Object A holds a reference to Object B, and Object B holds a reference to Object A (or a longer chain A -> B -> C -> A). When the external variables pointing to A and B are removed, each object still has `ob_refcnt >= 1` due to the internal peer reference. Because the count never reaches zero, standard reference counting cannot deallocate them. Only CPython's cyclic garbage collector, using its trial deletion algorithm on tracked container objects, can detect that the cycle is unreachable from the roots and free it.",
        "class Parent:\n    def __init__(self):\n        self.children = []\n\nclass Child:\n    def __init__(self, parent: Parent):\n        self.parent = parent\n\np = Parent()\nc = Child(p)\np.children.append(c)\n\n# p points to c, c points to p -> reference cycle!\nprint('Parent has children:', len(p.children))\nprint('Child parent matches:', c.parent is p)",
        "Constructing a classic Parent-Child reference cycle in object-oriented Python.",
        "CPython tracks container objects by embedding double-linked list pointers (`gc_next` and `gc_prev`) inside a `PyGC_Head` struct prepended to each object's memory allocation.",
        "Parent-child relationships in GUI widgets or AST syntax trees frequently create reference cycles; using `weakref` breaks these cycles cleanly.",
        ["How do you prevent reference cycles in parent-child hierarchies?", "What algorithm does Python use to detect isolated cycles?"],
        ["Believing Python crashes or leaks forever when a cycle is created (the cyclic GC reclaims it).", "Thinking tuples can never be part of a reference cycle (a tuple containing a mutable list can)."],
        "Recommend using `weakref.ref` for parent pointers in hierarchical data structures.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/gc.html"]
    ),

    # PY-BAS-131
    (
        "PY-BAS-131",
        "GC Generations (0, 1, 2)",
        "Python's cyclic GC categorizes tracked container objects into three generations (0, 1, and 2) based on the weak generational hypothesis that most objects die young.",
        "Generation 0 holds newly allocated container objects. When the number of allocations in Generation 0 exceeds a defined threshold relative to deallocations, Generation 0 is collected. Objects that survive a collection are promoted to Generation 1. Generation 1 is collected less frequently; survivors are promoted to Generation 2 (the oldest, longest-lived generation). Generation 2 is collected least frequently. This generational strategy minimizes the CPU overhead of traversing long-lived objects like loaded modules, classes, and configurations.",
        "import gc\n\n# Inspect current collection counts and thresholds\ncounts = gc.get_count()\nthresholds = gc.get_threshold()\n\nprint(f'Current object counts in (Gen0, Gen1, Gen2): {counts}')\nprint(f'Threshold triggers for (Gen0, Gen1, Gen2): {thresholds}')",
        "Inspecting generational object counts and collection thresholds using the gc module.",
        "By default, thresholds are `(700, 10, 10)`. Gen 0 runs when `allocations - deallocations > 700`. Gen 1 runs when Gen 0 has been collected 10 times. Gen 2 runs when Gen 1 has been collected 10 times.",
        "Tuning GC thresholds in memory-intensive batch jobs or ML model inference scripts can reduce CPU pause times caused by Gen 2 full collections.",
        ["What is the weak generational hypothesis?", "What triggers a full Generation 2 collection?"],
        ["Assuming all three generations are scanned during every GC run.", "Confusing the object count returned by `gc.get_count()` with total active objects in memory."],
        "Remember: surviving Gen 0 promotes to Gen 1; surviving Gen 1 promotes to Gen 2.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/gc.html#gc.get_threshold"]
    ),

    # PY-BAS-132
    (
        "PY-BAS-132",
        "Manual vs Automatic gc.collect()",
        "`gc.collect(generation=2)` manually forces a cyclic garbage collection pass across specified generations, returning the count of unreachable objects found and freed.",
        "Automatic garbage collection occurs transparently during runtime allocation when Generation 0 allocation thresholds are exceeded. However, developers can invoke `gc.collect()` manually to reclaim memory at deterministic points, such as immediately after completing a large batch ETL pipeline, freeing a large dataset, or during test teardown. Calling `gc.collect()` without arguments performs a full collection across all generations (0, 1, and 2). Calling `gc.collect(0)` only collects Generation 0.",
        "import gc\n\n# Create a cyclic structure and delete references\ncycle = [None]\ncycle[0] = cycle\ndel cycle\n\n# Force collection across all generations\ncollected = gc.collect()\nprint(f'Reclaimed {collected} cyclic object(s) manually.')",
        "Forcing a full cyclic garbage collection pass and inspecting the returned count.",
        "`gc.collect()` temporarily halts normal Python bytecode execution, moves objects from generation lists to an unreachable list via trial decrements, breaks cycles, and frees unreferenced memory blocks.",
        "In API endpoints processing large PDF generation or image manipulation tasks, running `gc.collect()` after responding can reclaim heap space before subsequent requests.",
        ["What is the performance cost of running `gc.collect()`?", "Can `gc.collect()` cause latency spikes in web APIs?"],
        ["Placing `gc.collect()` in tight loops or frequent hot paths.", "Expecting `gc.collect()` to return physical RAM to the OS instantly in all cases."],
        "Warn that explicit `gc.collect()` calls freeze the GIL and introduce noticeable latency jitter.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/gc.html#gc.collect"]
    ),

    # PY-BAS-133
    (
        "PY-BAS-133",
        "Stack vs Heap Memory in Python",
        "In CPython, call frames and variable name references live on the execution stack, while all actual Python objects (even primitive integers) reside on the private heap.",
        "Unlike languages like C or Rust where primitive values can live directly inside a stack frame's contiguous memory, every Python value is an allocated heap object (`PyObject`). The execution stack (managed via `PyFrameObject` structures) stores call frames, bytecode evaluation stacks, and local variable pointers pointing to objects on the private heap. When a function executes, its local variables point to heap objects; when the function returns, its frame is popped and the reference counts of referenced heap objects decrement.",
        "def compute(a: int) -> int:\n    b = 10         # 'b' pointer on call frame stack -> int(10) on heap\n    result = a + b # 'result' pointer on stack -> int(a+b) on heap\n    return result\n\n# Frame created, executed, and popped\nval = compute(5)\nprint('Computed value:', val)",
        "Demonstrating stack frame execution and heap object creation.",
        "Each function invocation allocates a `PyFrameObject` on the C call stack/heap containing a table of fast local variable pointers (`f_localsplus`) indexed directly by bytecode instructions like `LOAD_FAST` and `STORE_FAST`.",
        "Understanding recursion depth limits: deeply nested recursion exhausts Python's frame stack limit (`sys.getrecursionlimit()`), triggering `RecursionError`.",
        ["Are integers ever stored directly on the stack in CPython?", "What does `sys.setrecursionlimit()` modify?"],
        ["Believing Python primitives like `int` or `float` are stored value-by-value on the CPU stack.", "Thinking local variables inside a function avoid heap allocation overhead."],
        "Clarify: In CPython, references live on the evaluation stack/frame, but all objects live on the heap.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/c-api/frame.html"]
    ),

    # PY-BAS-134
    (
        "PY-BAS-134",
        "The del Statement",
        "The `del` statement unbinds a name from the local or global namespace and decrements the target object's reference count, but does not directly delete the object itself.",
        "A common misconception is that `del obj` physically destroys the object. In reality, `del` removes the name binding from the current namespace (e.g. `locals()` or `globals()`) or removes an element from a mutable container (`del my_list[0]`). If other variables or containers still reference the object, its reference count remains above zero and the object persists unharmed. Only when the reference count drops to zero does CPython invoke its deallocator.",
        "items = [1, 2, 3]\nalias = items\n\n# Delete the name 'items'\ndel items\n\n# The underlying list object still exists and is fully functional\nprint('Alias persists:', alias)\n\n# Only when 'alias' is deleted or rebound is the list deallocated\ndel alias",
        "Proving that deleting a name does not destroy the underlying object when another reference exists.",
        "Bytecode for `del x` executes `DELETE_FAST` (for local variables) or `DELETE_NAME` / `DELETE_GLOBAL`, which zeroes the pointer in the frame and calls `Py_DECREF` on the underlying object.",
        "Deleting massive temporary data structures (e.g. raw CSV rows or unprocessed byte payloads) in long batch scripts so their memory can be reclaimed before downstream steps.",
        ["What error occurs if you call `del x` when `x` is not defined?", "How does `del my_dict['key']` differ from `del my_var`?"],
        ["Believing `del` invokes `free()` or `delete` immediately on the underlying C memory block.", "Expecting `del` to clear objects that are trapped in uncollected circular references."],
        "Emphasize: `del` deletes bindings/names, not objects directly.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/reference/simple_stmts.html#the-del-statement"]
    ),

    # PY-BAS-135
    (
        "PY-BAS-135",
        "__del__ Finalizer Method",
        "`__del__` is an object finalizer method called by CPython immediately before an object's memory is deallocated when its reference count drops to zero or when collected by the GC.",
        "`__del__` allows an object to perform cleanup operations right before destruction. Unlike constructors (`__init__`), developers cannot predict the exact moment `__del__` executes because it depends on reference counts reaching zero or garbage collector cycles. Furthermore, exceptions raised inside `__del__` are ignored by Python and printed to `sys.stderr` as warnings to avoid crashing interpreter shutdown. For reliable resource cleanup, context managers (`with` blocks) should always be preferred over `__del__`.",
        "class ManagedFile:\n    def __init__(self, filename: str):\n        self.filename = filename\n        print(f'Opened {self.filename}')\n    \n    def __del__(self):\n        print(f'Finalizer __del__ called for {self.filename}')\n\ndef scope_test():\n    f = ManagedFile('test.txt')\n    # f goes out of scope here\n\nscope_test()\nprint('Function scope ended.')",
        "Demonstrating the execution of __del__ upon local variable scope termination.",
        "The `__del__` method maps to the `tp_finalize` slot in CPython's `PyTypeObject`. It is called once before `tp_dealloc` tears down the object's dictionary and internal attributes.",
        "Logging warnings when developers forget to explicitly close unmanaged network or C-library handles before an object is garbage collected.",
        ["What happens if an exception is raised inside `__del__`?", "Can `__del__` resurrect an object by assigning `self` to an external variable?"],
        ["Treating `__del__` as a reliable destructor like C++ destructors.", "Relying on `__del__` to flush database transactions or close network sockets."],
        "Always recommend context managers (`__enter__` / `__exit__`) for deterministic resource disposal.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#object.__del__"]
    ),

    # PY-BAS-136
    (
        "PY-BAS-136",
        "Why Not Rely on __del__ for Resource Cleanup",
        "Relying on `__del__` is dangerous because object destruction timing is non-deterministic, circular references delay execution, and interpreter shutdown may terminate without calling it.",
        "System resources such as file descriptors, database connections, and OS sockets are finite kernel resources. If cleanup relies on `__del__`, a file descriptor may remain open indefinitely if the holding object is involved in a reference cycle waiting for GC, or if the process exits before a final collection cycle. Moreover, during interpreter shutdown, global variables are set to `None`, causing `__del__` methods that access globals to crash with `AttributeError`. Context managers (`with` statement) guarantee immediate, deterministic release via `__exit__`.",
        "class ResourceWithContext:\n    def __enter__(self):\n        print('Acquired file descriptor')\n        return self\n    \n    def __exit__(self, exc_type, exc_val, exc_tb):\n        print('Deterministically closed file descriptor')\n        return False\n\n# Deterministic cleanup even if errors occur\nwith ResourceWithContext():\n    print('Doing critical I/O operations')",
        "Demonstrating deterministic resource cleanup with a context manager instead of __del__.",
        "CPython does not guarantee that `__del__` will be called for objects that still exist when the interpreter exits. During shutdown, module teardown nulls module dictionaries, rendering late `__del__` executions unpredictable.",
        "Database connection pooling: sockets must be returned to the pool immediately upon request completion rather than whenever GC decides to run.",
        ["What is the difference between `with` statement cleanup and `__del__`?", "What happens to `__del__` during interpreter shutdown?"],
        ["Assuming Python automatically calls `__del__` on all objects during process exit.", "Using `__del__` to commit database transactions."],
        "Emphasize: Use `with` blocks (Context Managers) for external resources, and use `__del__` only as a secondary fail-safe logging mechanism.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#object.__del__"]
    ),

    # PY-BAS-137
    (
        "PY-BAS-137",
        "The weakref Module",
        "The `weakref` module allows creating weak references to objects, enabling access to an object without increasing its reference count or preventing its garbage collection.",
        "Normally, binding an object to a variable or adding it to a collection increments its `ob_refcnt`, preventing deallocation. A weak reference (`weakref.ref`) refers to an object without incrementing `ob_refcnt`. If only weak references remain, the referent is deallocated immediately. Weak references are essential for implementing caches without memory leaks and breaking circular references in parent-child or observer patterns.",
        "import weakref\n\nclass HeavySession:\n    def __init__(self, session_id: str):\n        self.session_id = session_id\n\nsession = HeavySession('SES-9988')\nw_ref = weakref.ref(session)\n\n# Accessing the referent by calling the weakref\nprint('Referent alive:', w_ref() is session)\n\n# Deallocating primary reference\ndel session\nprint('Referent after deletion:', w_ref())  # Returns None",
        "Creating a weak reference and observing it return None once the target object is deleted.",
        "Objects supporting weak references contain a `tp_weaklistoffset` slot in their `PyTypeObject`. CPython maintains a linked list of weak reference callback structures and automatically updates them to point to `NULL` upon referent deallocation.",
        "In-memory caches (e.g. image caches or user session stores) where objects should be kept alive only as long as active requests hold strong references to them.",
        ["What happens when you call a weak reference whose target has been collected?", "Which built-in Python types cannot be weakly referenced directly?"],
        ["Calling `w_ref.session_id` directly instead of calling `w_ref().session_id`.", "Assuming built-in `list` or `dict` can be weakly referenced without subclassing."],
        "Remember: Call the weakref instance like a function `w_ref()` to retrieve the underlying object.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/weakref.html"]
    ),

    # PY-BAS-138
    (
        "PY-BAS-138",
        "weakref.ref vs weakref.proxy",
        "`weakref.ref` returns a callable reference object requiring invocation `r()` to access the target, whereas `weakref.proxy` returns a transparent proxy that forwards all attribute accesses directly.",
        "`weakref.ref(obj)` creates an explicit handle; if the referent is alive, calling `r()` returns `obj`; if dead, `r()` returns `None`. `weakref.proxy(obj)` creates a proxy wrapper that behaves syntactically like `obj` itself without requiring function call syntax (`proxy.name` instead of `ref().name`). However, if the referent has been collected, accessing any attribute on a proxy raises a `ReferenceError` exception immediately.",
        "import weakref\n\nclass Config:\n    def __init__(self, env: str):\n        self.env = env\n\ncfg = Config('production')\n\n# weakref.ref requires calling ()\nr = weakref.ref(cfg)\nprint('ref access:', r().env)\n\n# weakref.proxy behaves like the object directly\np = weakref.proxy(cfg)\nprint('proxy access:', p.env)\n\ndel cfg\n# r() returns None safely\nprint('ref after del:', r())\ntry:\n    print(p.env)  # Raises ReferenceError!\nexcept ReferenceError:\n    print('Proxy raised ReferenceError as expected!')",
        "Contrasting explicit callable weakref.ref against transparent weakref.proxy.",
        "`weakref.proxy` constructs a `PyWeakProxy` C struct that intercepts `tp_getattro` and `tp_setattro` slots, validating that the referent pointer is not null before dispatching attribute lookups.",
        "Using `weakref.proxy` to pass lightweight, non-retaining parent pointers into child nodes in tree structures while keeping natural attribute access syntax.",
        ["What exception does `weakref.proxy` raise when the target is dead?", "How does `weakref.ref` handle optional callbacks upon referent destruction?"],
        ["Failing to handle `ReferenceError` when using `weakref.proxy`.", "Assuming `weakref.proxy` can be compared for equality when the target object is dead."],
        "Use `weakref.ref` when you need to check if the target is still alive with `if ref() is not None:`.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/weakref.html#weakref.proxy"]
    ),

    # PY-BAS-139
    (
        "PY-BAS-139",
        "WeakValueDictionary and WeakKeyDictionary",
        "`WeakValueDictionary` and `WeakKeyDictionary` are mapping classes that hold weak references to their values or keys, automatically removing entries when those objects are garbage collected.",
        "In a standard Python `dict`, inserting an object as a key or value increments its reference count, holding it in memory until explicitly removed. In a `WeakValueDictionary`, values are stored as weak references; as soon as no external strong references to a value exist, its key-value entry is automatically purged from the dictionary. Conversely, `WeakKeyDictionary` uses weak references for keys, automatically discarding entries when their key objects are collected.",
        "import weakref\n\nclass HeavyModel:\n    def __init__(self, model_id: int):\n        self.model_id = model_id\n\ncache = weakref.WeakValueDictionary()\n\nm1 = HeavyModel(101)\ncache['m1'] = m1\nprint('Cache contents:', list(cache.keys()))\n\n# Delete strong reference to m1\ndel m1\n# Entry is automatically evicted!\nprint('Cache after deleting strong ref:', list(cache.keys()))",
        "Demonstrating automatic key-value eviction in WeakValueDictionary.",
        "`WeakValueDictionary` registers a cleanup callback with each weakref value. When CPython deallocates the value, the callback triggers a hash table deletion of the corresponding key without requiring manual eviction sweeps.",
        "Thread-safe object registries, factory flyweight caches, and ORM identity maps where cached instances should vanish automatically when out of active use.",
        ["Can you store primitive strings or ints as values in WeakValueDictionary?", "When would you prefer WeakKeyDictionary over WeakValueDictionary?"],
        ["Attempting to store non-weakrefable types (like raw `dict`, `int`, or `tuple`) as values in `WeakValueDictionary`.", "Expecting `len(cache)` to be constant while other threads deallocate objects."],
        "Remember: Keys or values must be weakref-capable types (custom classes, not built-in literals).",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/weakref.html#weakref.WeakValueDictionary"]
    ),

    # PY-BAS-140
    (
        "PY-BAS-140",
        "id() and Memory Addresses",
        "`id(obj)` returns an integer representing an object's identity, which in CPython corresponds directly to the memory address of the object's `PyObject` structure.",
        "Python guarantees that `id()` returns a unique and constant integer for the lifetime of an object. In CPython, this integer is simply the memory address of the object in C (cast from `(uintptr_t)obj`). Two objects with non-overlapping lifetimes may share the exact same `id()` value because newly allocated objects can reuse the recycled memory address of a recently deallocated object.",
        "x = [1, 2, 3]\nprint(f'Memory address (hex): {hex(id(x))}')\n\ny = x\nprint('Identical objects have identical id:', id(x) == id(y))\n\n# Address reuse demonstration\ndel x, y\nz = [4, 5, 6]\nprint('New object might reuse address:', hex(id(z)))",
        "Inspecting object memory addresses using id() and hex() representation.",
        "CPython implements `id(op)` in `Python/bltinmodule.c` by casting the object pointer `(PyObject *)` directly into a Python integer `PyLong_FromVoidPtr(op)`.",
        "Testing object identity with `is` (which compiles to direct pointer comparison `a == b` in C bytecode) rather than value equality `==`.",
        ["Why might two distinct objects created at different times have the same `id()`?", "Does `id()` return the memory address in PyPy or Jython?"],
        ["Assuming two objects with the same `id()` were alive simultaneously.", "Using `id(x) == id(y)` instead of the idiomatic and faster `x is y`."],
        "Emphasize: `is` performs an identity check by comparing memory addresses directly in C.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/functions.html#id"]
    ),

    # PY-BAS-141
    (
        "PY-BAS-141",
        "Object Interning",
        "Object interning is an internal optimization where CPython reuses a single immutable object in memory rather than creating duplicate instances with identical values.",
        "CPython automatically interns small integers in the range `[-5, 256]` during interpreter startup. Whenever an integer in this range is computed or referenced, Python points to the pre-allocated singleton rather than allocating new memory. CPython also automatically interns string literals that look like Python identifiers (ASCII letters, digits, underscores) and allows manual string interning via `sys.intern()`. Interning saves heap memory and makes equality checks lightning-fast because strings can be compared via pointer identity (`is`).",
        "import sys\n\n# Small integer caching: [-5, 256]\na = 250\nb = 250\nprint('Small ints are identical:', a is b)  # True\n\n# Large ints are distinct heap allocations\nx = 1000\ny = 1000\nprint('Large ints in separate evaluations:', x is y)  # False (in CLI)\n\n# Manual string interning\ns1 = sys.intern('custom_long_unique_token_identifier')\ns2 = sys.intern('custom_long_unique_token_identifier')\nprint('Interned strings share identity:', s1 is s2)  # True",
        "Demonstrating small integer caching and manual string interning with sys.intern.",
        "CPython maintains an internal global array of integer objects `small_ints[262]` and a global dictionary `interned` in `unicodeobject.c` mapping string values to their canonical `PyUnicodeObject` pointers.",
        "Parsing large XML/JSON feeds or compiler tokens: interning dictionary keys dramatically reduces memory usage and accelerates key lookups.",
        ["Why is `x = 257; y = 257; x is y` True in a single file/module but False in the interactive REPL?", "What is the memory benefit of `sys.intern()`?"],
        ["Relying on `is` for value equality on strings or integers without explicit interning.", "Assuming floats or lists are interned."],
        "In interviews, explain that compiler constant folding interns constants within a single code object, which differs from runtime global interning.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/sys.html#sys.intern"]
    ),

    # PY-BAS-142
    (
        "PY-BAS-142",
        "Freeing Memory to the OS",
        "Python does not immediately return all freed object memory to the operating system; it retains allocated arenas in `pymalloc` pools for future object allocations.",
        "When an object is deallocated, its memory block is returned to its parent 4KB pool inside a 256KB arena. If other objects in that same arena are still alive, the entire 256KB OS page cannot be released back to the operating system kernel. CPython can only call OS `free()` or `munmap()` when an entire 256KB arena becomes completely empty. Consequently, a Python process's Resident Set Size (RSS) reported by `top` or Task Manager often remains high even after large collections are deleted.",
        "import gc\n\n# Allocate millions of small objects\nlarge_list = [{'id': i} for i in range(500000)]\nprint('Allocated 500,000 dicts.')\n\n# Delete references\ndel large_list\ngc.collect()\nprint('References deleted; memory retained in pymalloc pools for future use.')",
        "Demonstrating that deleting objects recycles memory within pymalloc rather than dropping process RSS immediately.",
        "CPython's `pymalloc` manages memory in 256KB arenas. An arena is freed via `free()` / `VirtualFree()` only when `arena->nfreepools == arena->ntotalpools`. If a single 8-byte object remains in a 256KB arena, the OS cannot reclaim the page.",
        "Understanding why celery worker processes or web workers gradually consume memory over time and require max-tasks-per-child recycling settings.",
        ["What is memory fragmentation in pymalloc arenas?", "How can you force a Python process to release memory back to the OS?"],
        ["Assuming `gc.collect()` drops process RSS back to baseline.", "Blaming Python for memory leaks when the issue is arena fragmentation."],
        "Mention worker recycling (`max_requests` in Gunicorn, `max-tasks-per-child` in Celery) as the standard remedy for process memory retention.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/c-api/memory.html#pymalloc"]
    ),

    # PY-BAS-143
    (
        "PY-BAS-143",
        "Memory Leaks in Python",
        "Memory leaks in Python occur when unwanted objects remain reachable through active references (such as global lists, caches, or circular references with broken cleanup), preventing garbage collection.",
        "Even though Python features automatic memory management and garbage collection, a Python program can easily leak memory. A memory leak occurs whenever an application unintentionally retains a reference to an object that will never be used again. Common causes include appending items to module-level lists or dictionaries without eviction, unbounded caches (`@lru_cache(maxsize=None)`), registered callbacks or event listeners that are never unregistered, and long-running threads holding local variables.",
        "import functools\n\n# Anti-pattern: Unbounded cache causes silent memory leak\n@functools.lru_cache(maxsize=None)\ndef compute_payload(user_id: int):\n    return f'heavy_user_data_payload_for_{user_id}' * 100\n\n# Simulating thousands of unique user requests\nfor uid in range(1000):\n    compute_payload(uid)\n\nprint('Cache info shows 1000 retained entries:', compute_payload.cache_info())",
        "Simulating an unbounded in-memory cache leak using lru_cache(maxsize=None).",
        "Because references in global dictionaries or caches remain reachable from the root namespace, `ob_refcnt` remains >= 1 and the cyclic GC considers them reachable live objects, never marking them for collection.",
        "Investigating slow memory degradation in production microservices that run fine for days before triggering Kubernetes OOMKilled errors.",
        ["How do you diagnose a memory leak in a running Python service?", "What is the difference between an uncollected cycle and an intentional reference leak?"],
        ["Thinking garbage collection guarantees absence of memory leaks.", "Believing only C extensions can cause memory leaks in Python."],
        "State clearly: If a reference to an object exists in any active scope or collection, Python's GC will not and cannot collect it.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/tracemalloc.html"]
    ),

    # PY-BAS-144
    (
        "PY-BAS-144",
        "sys.getsizeof() Limitations",
        "`sys.getsizeof(obj)` returns the memory consumption of an object's direct struct in bytes, but does not include the memory of nested or referenced objects inside containers.",
        "When you call `sys.getsizeof([1, 2, [3, 4]])`, Python returns only the memory allocated for the outer list struct itself and its array of internal item pointers (typically 8 bytes per pointer on 64-bit systems). It does not recursively compute the size of the referenced integers or child lists. To calculate the true recursive memory footprint of a deep data structure, developers must implement a recursive traversal script or use third-party libraries like `pympler`.",
        "import sys\n\nempty_list = []\nprint('Empty list struct size:', sys.getsizeof(empty_list), 'bytes')\n\n# List with large sub-objects\nlarge_nested = [[i] * 1000 for i in range(10)]\nprint('Direct size of container:', sys.getsizeof(large_nested), 'bytes')\nprint('Direct size only accounts for pointer array, not nested lists!')",
        "Demonstrating that sys.getsizeof measures shallow container overhead only.",
        "In CPython, `sys.getsizeof()` calls the object's `__sizeof__()` method, which calculates `sizeof(PyObject)` plus any variable-length array buffer directly allocated within that C structure (`ob_size * sizeof(PyObject*)`).",
        "Evaluating whether an in-memory caching mechanism is exceeding allocated Redis/RAM limits when caching complex nested dictionaries or pandas dataframes.",
        ["How would you implement a deep recursive getsizeof function?", "What is `__sizeof__()` vs `sys.getsizeof()`?"],
        ["Relying on `sys.getsizeof(my_dict)` to measure the total RAM consumed by a nested JSON structure.", "Forgetting that `sys.getsizeof()` includes garbage collector header overhead."],
        "Highlight that `sys.getsizeof` is shallow; use recursive traversal or `pympler.asizeof` for accurate sizing.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/sys.html#sys.getsizeof"]
    ),

    # PY-BAS-145
    (
        "PY-BAS-145",
        "The tracemalloc Module",
        "`tracemalloc` is a built-in Python module that traces memory allocations back to the exact Python source file and line number where they originated.",
        "Introduced in Python 3.4 (PEP 454), `tracemalloc` hooks into Python's internal memory allocators. It captures stack traces at the point of allocation, allowing developers to take snapshots of current memory usage, compare two snapshots over time to view allocation diffs, and pinpoint exact lines of code causing memory bloat or leaks without needing external C profilers.",
        "import tracemalloc\n\n# Start tracing allocations\ntracemalloc.start()\n\n# Allocate objects\ndata = [f'record_{i}' for i in range(10000)]\n\n# Take snapshot\nsnapshot = tracemalloc.take_snapshot()\ntop_stats = snapshot.statistics('lineno')\n\nprint('[Top Memory Allocation]')\nfor stat in top_stats[:3]:\n    print(stat)",
        "Starting tracemalloc, capturing a snapshot, and printing top allocation lines.",
        "`tracemalloc` replaces default allocator function pointers with tracking wrappers that store allocation metadata (size, address, and traceback frames) inside an internal hash table.",
        "Running memory regression benchmarks during CI test suites to ensure new features do not introduce unbounded memory spikes.",
        ["What is the runtime performance overhead of enabling tracemalloc in production?", "How do you compare two tracemalloc snapshots to find memory leaks?"],
        ["Leaving `tracemalloc.start(25)` permanently enabled in high-throughput production services (it adds 10-30% CPU/memory overhead).", "Forgetting to call `tracemalloc.stop()` after testing."],
        "Mention `snapshot.compare_to(old_snapshot, 'lineno')` as the premier technique for finding memory leaks.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/tracemalloc.html"]
    ),

    # PY-BAS-146
    (
        "PY-BAS-146",
        "__slots__ for Memory Optimization",
        "`__slots__` eliminates the default per-instance `__dict__` and `__weakref__` attributes in a class, replacing them with fixed-size descriptor arrays to dramatically reduce memory consumption.",
        "By default, every Python object stores its attributes dynamically in an internal dictionary (`self.__dict__`). A dictionary has substantial memory overhead (hundreds of bytes) to support dynamic attribute additions. When instantiating millions of small objects (e.g. data points, coordinates, graph nodes), defining `__slots__ = ('x', 'y')` instructs CPython to allocate a fixed C struct with descriptor offsets instead of a dictionary, reducing memory usage per instance by 60% to 80%.",
        "import sys\n\nclass RegularPoint:\n    def __init__(self, x: float, y: float):\n        self.x = x\n        self.y = y\n\nclass SlottedPoint:\n    __slots__ = ('x', 'y')\n    def __init__(self, x: float, y: float):\n        self.x = x\n        self.y = y\n\np1 = RegularPoint(1.0, 2.0)\np2 = SlottedPoint(1.0, 2.0)\n\nprint('Regular point with __dict__ size:', sys.getsizeof(p1) + sys.getsizeof(p1.__dict__))\nprint('Slotted point size:', sys.getsizeof(p2))\nprint('Has __dict__?', hasattr(p2, '__dict__'))",
        "Comparing memory footprint of a standard class instance with __dict__ vs a slotted class instance.",
        "CPython allocates member descriptors in `tp_members`. Attribute access `p.x` computes a direct pointer offset from the object's base address in C rather than executing a dictionary hash lookup.",
        "Designing high-throughput data processing systems that load millions of records or telemetry events into memory.",
        ["Can you dynamically assign arbitrary new attributes to an instance with `__slots__`?", "How does `__slots__` interact with class inheritance?"],
        ["Forgetting that child classes must also declare `__slots__` to prevent `__dict__` creation.", "Declaring `__slots__` as a string instead of a tuple/sequence (e.g. `__slots__ = 'x'` allows only 'x')."],
        "Always declare `__slots__` as a tuple: `__slots__ = ('attr1', 'attr2')`.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#slots"]
    ),

    # PY-BAS-147
    (
        "PY-BAS-147",
        "List Memory Growth & Over-Allocation",
        "Python lists pre-allocate extra buffer capacity proportionally during appends to achieve amortized O(1) time complexity, which causes `sys.getsizeof()` to grow in discrete steps.",
        "If a Python list reallocated its underlying array by exactly 1 element on every `append()`, appending $N$ items would require $O(N^2)$ memory copies. To achieve amortized $O(1)$ appends, CPython uses an over-allocation growth algorithm: when the capacity is exceeded, it allocates extra slots using the formula `new_allocated = (newsize >> 3) + (newsize < 9 ? 3 : 6) + newsize`. Thus, a list often has unused pointer capacity allocated in heap memory.",
        "import sys\n\nitems = []\nlast_size = sys.getsizeof(items)\nprint(f'Initial empty list: {last_size} bytes')\n\nfor i in range(15):\n    items.append(i)\n    current_size = sys.getsizeof(items)\n    if current_size != last_size:\n        print(f'Length {len(items):2d}: Reallocated from {last_size} -> {current_size} bytes')\n        last_size = current_size",
        "Observing stepped memory jumps in list size as over-allocation occurs during sequential appends.",
        "CPython's `list_resize()` function in `listobject.c` recalculates `allocated`. If `size < allocated`, it appends directly without calling `realloc()`. Only when `size == allocated` is system `realloc()` invoked.",
        "Optimizing memory when building large static lists: converting an appended list to a tuple (`tuple(items)`) trims unused over-allocated capacity.",
        ["What is the growth factor formula used by CPython lists?", "Why does `[0] * 1000` allocate less memory than appending 1000 times in a loop?"],
        ["Assuming list memory grows continuously by a fixed byte count on every single append.", "Failing to realize that pre-sized lists via comprehensions allocate exact memory without over-allocation padding."],
        "Mention that list comprehensions pre-size their allocation more tightly than manual `.append()` loops.",
        ["[Data Types & Collections](data-types-and-collections.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/c-api/list.html"]
    ),

    # PY-BAS-148
    (
        "PY-BAS-148",
        "Dict Memory Layout & Compact Dictionaries",
        "Python 3.6+ uses a compact dictionary layout separating a sparse hash index table from a dense, insertion-ordered array of entries, reducing memory consumption by 20% to 25%.",
        "Historically, Python dictionaries stored a single sparse array of 24-byte entries (`hash`, `key`, `value`) where 2/3 of slots were empty to prevent hash collisions, wasting substantial memory. Under Raymond Hettinger's compact dict design, CPython stores entries contiguously in a dense `entries` array, while a separate small `indices` array (storing 1-byte, 2-byte, or 4-byte integer indices) acts as the sparse hash table. This drastically reduces padding and naturally preserves insertion order.",
        "import sys\n\n# Creating dict with several keys\nd = {'a': 1, 'b': 2, 'c': 3, 'd': 4}\nprint('Dict size in bytes:', sys.getsizeof(d))\n\n# Proving insertion order preservation\nkeys = list(d.keys())\nprint('Keys retain strict insertion order:', keys)",
        "Demonstrating compact dict memory efficiency and guaranteed insertion ordering.",
        "In `dictobject.c`, `PyDictKeysObject` contains `dk_indices` (sparse table of bytes/shorts) and `dk_entries` (dense `PyDictKeyEntry` structs). Hash lookups search `dk_indices[hash & mask]` to find the index into `dk_entries`.",
        "Configuring caching schemas or serializer mappings where memory conservation across millions of dictionary records is paramount.",
        ["How does compact dict preserve insertion order?", "What are split tables vs combined tables in class instance dictionaries?"],
        ["Believing Python dicts still waste 2/3 of their entry memory on sparse NULL entries.", "Assuming insertion order preservation was added as a language design goal rather than an artifact of compact memory layout."],
        "Highlight that Python 3.7 made insertion order an official language specification, born from this memory layout optimization.",
        ["[Data Types & Collections](data-types-and-collections.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/c-api/dict.html"]
    ),

    # PY-BAS-149
    (
        "PY-BAS-149",
        "Shallow Copy vs Deep Copy Memory Impact",
        "A shallow copy constructs a new container object while inserting references to the original child objects, whereas a deep copy recursively allocates duplicate copies of all child objects.",
        "`copy.copy()` duplicates only the outer container; both the original and shallow copy point to the exact same child object memory addresses. If a child object is mutable and modified, the change is reflected in both containers. `copy.deepcopy()` traverses the entire object graph, allocating brand new memory for every nested mutable object and using an internal memoization dictionary to handle cyclical references safely.",
        "import copy\n\noriginal = [[1, 2], [3, 4]]\nshallow = copy.copy(original)\ndeep = copy.deepcopy(original)\n\n# Modify child list\noriginal[0].append(99)\n\nprint('Original:', original)\nprint('Shallow copy affected:', shallow)\nprint('Deep copy isolated:', deep)",
        "Comparing memory isolation and mutability side effects of shallow vs deep copy.",
        "`copy.deepcopy` maintains a `memo = {}` mapping `id(original_obj)` to `cloned_obj`. If an object has already been copied in the current pass, deepcopy reuses the memoized reference to prevent infinite recursion on circular graphs.",
        "Duplicating request context state or configuration templates safely across asynchronous tasks without thread race conditions.",
        ["What is the computational and memory risk of calling `copy.deepcopy()` on massive object graphs?", "How does `copy.deepcopy()` handle circular references without infinite loops?"],
        ["Using `copy.deepcopy()` when a shallow copy `list.copy()` or slice `lst[:]` is sufficient.", "Assuming immutable objects (ints, strings, tuples of immutables) are duplicated by `deepcopy()` (they are returned as-is)."],
        "Remind that `deepcopy` does not duplicate immutable scalars because their immutability makes sharing 100% safe.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/copy.html"]
    ),

    # PY-BAS-150
    (
        "PY-BAS-150",
        "Global Variables and Process Memory Bloat",
        "Global variables persist for the entire lifetime of the Python process inside module dictionaries, preventing their referenced objects from ever being deallocated by reference counting or GC.",
        "Variables defined at module top-level are stored in the module's `__dict__`. Because module dictionaries are referenced by `sys.modules`, any data structure attached to a global variable remains strongly referenced forever. In long-running worker processes (Celery workers, uWSGI/Gunicorn web processes), accumulating data in global lists or dicts causes continuous process memory growth. Cleaning up requires explicitly deleting keys, calling `.clear()`, or rebinding the global variable to `None`.",
        "import sys\n\n# Module-level global accumulator\nGLOBAL_CACHE = []\n\ndef process_batch(records):\n    # Accumulating into globals causes memory retention\n    GLOBAL_CACHE.extend(records)\n\nprocess_batch(['rec1', 'rec2'])\nprint('Global cache retains:', len(GLOBAL_CACHE))\n\n# Explicit cleanup to release heap references\nGLOBAL_CACHE.clear()\nprint('Global cache cleared:', len(GLOBAL_CACHE))",
        "Demonstrating global variable memory retention and explicit clearing via .clear().",
        "CPython roots all global references in `PyInterpreterState->modules`. The cyclic GC treats `sys.modules` as a permanent root; therefore, any object reachable from a module dictionary is never considered an unreachable candidate.",
        "Preventing memory creep in background worker processes that process thousands of queue jobs sequentially without restarting.",
        ["Why doesn't the cyclic garbage collector clean up unused global variables?", "How does Celery's `max_tasks_per_child` mitigate global memory bloat?"],
        ["Using global lists as temporary accumulators across requests.", "Expecting module-level variables to be garbage collected when functions finish."],
        "Emphasize: Scope variables locally inside functions or classes; use dependency injection instead of global state.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/reference/datamodel.html"]
    )
]
