"""
gen_py_01_fundamentals.py
=========================
Generates 01-python/fundamentals.md
Contains:
- Basic: PY-BAS-001 to PY-BAS-025 (25 questions)
- Intermediate: PY-INT-001 to PY-INT-025 (25 questions)
- Advanced: PY-ADV-001 to PY-ADV-025 (25 questions)
Total: 75 questions
"""

import os
import sys
from base import Question, render_file

def get_basic_questions():
    qs = []
    
    # 001
    qs.append(Question(
        qid="PY-BAS-001",
        title="What is Python and what makes it dynamically typed?",
        difficulty="Basic",
        topic="Python Fundamentals",
        one_line="Python is a high-level, interpreted, general-purpose language where types are bound to runtime values rather than variables.",
        detailed="In Python, variable names are simply symbolic references (pointers) bound to runtime PyObject entities in memory. Unlike statically typed languages like C or Java, where variables are memory locations reserved for specific data types declared at compile-time, Python variables can reference any object at any time without explicit type declarations. Type enforcement and validation occur dynamically during execution when operations or method calls are attempted on objects.",
        example_code="x = 42\nprint(f'Type of x: {type(x)}')\nx = 'Antigravity'\nprint(f'New type of x: {type(x)}')",
        example_desc="Demonstrates variable reassignment from an integer to a string dynamically.",
        internal_working="In CPython, every variable name resides in a local or global symbol table pointing to a PyObject pointer. A PyObject contains ob_refcnt (reference count) and ob_type (pointer to type descriptor struct PyTypeObject). When assigning x = 42, Python allocates a PyLongObject and points the symbol 'x' to it. When assigning x = 'Antigravity', the pointer is simply updated to point to a PyUnicodeObject, and the reference count of the integer is decremented.",
        real_world="Dynamic typing enables rapid API prototyping and flexible JSON payload parsing in web frameworks like FastAPI and Django.",
        follow_ups=[
            "Is Python strongly typed or weakly typed?",
            "What is duck typing?",
            "What is the performance cost of dynamic typing?"
        ],
        mistakes=[
            "Confusing dynamically typed with weakly typed. Python is strongly typed because '5' + 5 raises a TypeError rather than performing implicit type coercion."
        ],
        tip="Emphasize that Python is both strongly typed and dynamically typed: types belong to objects, not variable names.",
        related=["[data-types-and-collections.md](data-types-and-collections.md)"],
        references=["https://docs.python.org/3/reference/datamodel.html"]
    ))

    # 002
    qs.append(Question(
        qid="PY-BAS-002",
        title="Is Python interpreted, compiled, or both?",
        difficulty="Basic",
        topic="Python Fundamentals",
        one_line="Python is both: source code is first compiled into intermediate bytecode (.pyc) and then interpreted by the CPython virtual machine.",
        detailed="When a Python script is executed, the CPython runtime first compiles the source text into a platform-independent intermediate representation called bytecode. This bytecode is structured into PyCodeObject instances. If the module is imported, bytecode is cached on disk inside the __pycache__ directory as .pyc files. The CPython virtual machine (a stack-based execution loop implemented in ceval.c) then interprets the bytecode instructions sequentially.",
        example_code="import dis\n\ndef add(a, b):\n    return a + b\n\ndis.dis(add)",
        example_desc="Using the dis module to inspect compiled bytecode instructions of a Python function.",
        internal_working="CPython's compiler pipeline performs lexical analysis (tokenizing), generates a Concrete Syntax Tree (CST), converts it into an Abstract Syntax Tree (AST), applies peephole/AST optimizations, and emits bytecode instructions. The virtual machine executes these opcodes using an evaluation loop (PyEval_EvalFrameDefault).",
        real_world="Understanding bytecode compilation helps explain cold-start latencies in serverless AWS Lambda environments and why __pycache__ exists in production containers.",
        follow_ups=[
            "What does a .pyc file contain?",
            "Can Python code be compiled to native machine code directly (e.g. PyPy, Nuitka, Cython)?"
        ],
        mistakes=[
            "Saying Python is purely interpreted with zero compilation step."
        ],
        tip="Explain the two-phase execution: compilation to bytecode followed by virtual machine evaluation.",
        related=["[internals-and-performance.md](internals-and-performance.md)"],
        references=["https://docs.python.org/3/library/dis.html"]
    ))

    # 003
    qs.append(Question(
        qid="PY-BAS-003",
        title="What is PEP 8 and why is it important?",
        difficulty="Basic",
        topic="Python Fundamentals",
        one_line="PEP 8 is Python's official style guide specifying formatting conventions for readable, consistent, and idiomatic Python code.",
        detailed="PEP 8 (Python Enhancement Proposal 8) outlines conventions regarding indentation (4 spaces, no tabs), variable and function naming (snake_case), class naming (PascalCase), constants (UPPER_CASE), maximum line length (typically 79-88 characters), imports grouping, and whitespace around operators. Adhering to PEP 8 ensures consistency across open-source libraries and production codebases, reducing cognitive load during code reviews.",
        example_code="# Compliant with PEP 8\nMAX_RETRIES = 3\n\n\nclass PaymentProcessor:\n    def process_transaction(self, account_id: str, amount: float) -> bool:\n        return amount > 0 and len(account_id) > 0\n",
        example_desc="Demonstrates PEP 8 naming, spacing, and typing conventions.",
        internal_working="PEP 8 has no impact on bytecode generation or execution speed; it purely enforces syntactic and structural cleanliness. Linters like Flake8, Ruff, and formatters like Black automate PEP 8 compliance by parsing source ASTs and reformatting source tokens.",
        real_world="Used in CI/CD pipelines (via Black or Ruff) to block PRs that deviate from unified engineering team style guidelines.",
        follow_ups=[
            "What tools enforce PEP 8 automatically in modern Python projects?",
            "What is the difference between PEP 8 and PEP 257?"
        ],
        mistakes=[
            "Treating PEP 8 as a runtime compiler enforcement rule rather than a developer convention."
        ],
        tip="Mention tools like Ruff or Black and emphasize that readability is a core tenet of the Zen of Python (PEP 20).",
        related=["[fundamentals.md](fundamentals.md)"],
        references=["https://peps.python.org/pep-0008/"]
    ))

    # 004
    qs.append(Question(
        qid="PY-BAS-004",
        title="What is the difference between '==' and 'is' operators in Python?",
        difficulty="Basic",
        topic="Python Fundamentals",
        one_line="'==' checks value equality (whether objects have equivalent contents), whereas 'is' checks identity (whether both variables point to the exact same memory address).",
        detailed="The '==' operator invokes the __eq__() dunder method of the left-hand operand to evaluate whether the contents or values of two objects are equal. The 'is' operator compares the memory addresses of two objects using their internal C pointers (equivalent to id(a) == id(b)). In Python, two distinct objects can have identical values (evaluating to True with '==') while residing at different memory locations (evaluating to False with 'is').",
        example_code="list_a = [1, 2, 3]\nlist_b = [1, 2, 3]\nprint(list_a == list_b)  # True (same values)\nprint(list_a is list_b)  # False (different memory addresses)\n\nval = None\nprint(val is None)       # True (None is a singleton)",
        example_desc="Comparing content equality vs object identity on lists and singletons.",
        internal_working="The 'is' comparison compiles to the TEST_OP or COMPARE_OP bytecode with an identity check, performing a single pointer comparison (a == b in C). The '==' comparison compiles to COMPARE_OP (==) which calls PyObject_RichCompareBool, dispatching to tp_richcompare in the C struct.",
        real_world="Used when comparing singletons like None, True, False, or sentinel values (`if x is None:`). Never use '==' for None comparisons.",
        follow_ups=[
            "Why does 'a = 100; b = 100; a is b' evaluate to True in CPython?",
            "What is integer interning?"
        ],
        mistakes=[
            "Using 'if x == None:' instead of idiomatic 'if x is None:', which can be hijacked if a class overrides __eq__."
        ],
        tip="State clearly: '==' is for values, 'is' is for identity/memory address. Always use 'is' for None checks.",
        related=["[memory-management.md](memory-management.md)"],
        references=["https://docs.python.org/3/reference/expressions.html#comparisons"]
    ))

    # 005
    qs.append(Question(
        qid="PY-BAS-005",
        title="What are Python keywords and how do you view them programmatically?",
        difficulty="Basic",
        topic="Python Fundamentals",
        one_line="Keywords are reserved tokens in Python that define the language's grammar and syntax; they cannot be used as identifiers.",
        detailed="Keywords are reserved by the Python tokenizer and parser to implement control flow, exception handling, function/class declarations, and async workflows (e.g., if, for, while, def, class, return, async, await, try, except). Because their syntactic roles are fixed, attempting to assign a value to a keyword results in a SyntaxError. Python provides the standard library module 'keyword' to inspect and query these reserved words dynamically.",
        example_code="import keyword\n\nprint('Total keywords:', len(keyword.kwlist))\nprint('Is \"async\" a keyword?', keyword.iskeyword('async'))\nprint('Sample keywords:', keyword.kwlist[:5])",
        example_desc="Querying reserved language keywords using the standard library.",
        internal_working="CPython's tokenizer uses a DFA (Deterministic Finite Automaton) generated from the Python grammar file (Grammar/python.gram). During lexical analysis, tokens matching reserved keywords are tagged with specific token IDs (e.g., NAME vs IF vs DEF) rather than generic user-defined identifiers.",
        real_world="Used in serializers, code generation tools, and dynamic ORM attribute builders to sanitize database column names that collide with Python keywords.",
        follow_ups=[
            "Can you override or rebind a Python keyword?",
            "What are soft keywords introduced in Python 3.10?"
        ],
        mistakes=[
            "Confusing built-in functions (like print, len, id) with keywords. Built-in functions can technically be shadowed, whereas keywords raise SyntaxError if reassigned."
        ],
        tip="Mention that Python 3.10 introduced soft keywords like 'match' and 'case' which act as keywords only in pattern matching context.",
        related=["[internals-and-performance.md](internals-and-performance.md)"],
        references=["https://docs.python.org/3/library/keyword.html"]
    ))

    # Add remaining basic questions 006-025 systematically
    fundamentals_basic_data = [
        ("PY-BAS-006", "What are Python built-in functions and how are they accessed?",
         "Built-in functions are preloaded functions available in Python's global namespace without requiring any import statements.",
         "Python includes over 70 built-in functions such as len(), range(), print(), id(), isinstance(), sum(), min(), max(), and open(). These functions reside in the 'builtins' module, which is automatically loaded into the interpreter during bootstrap.",
         "nums = [10, 20, 30]\nprint('Length:', len(nums))\nprint('Max value:', max(nums))\nprint('Sum:', sum(nums))",
         "Using common built-in utility functions.",
         "CPython initializes built-in functions in bltinmodule.c as C-level PyCFunction pointers. When resolving a name, Python follows the LEGB (Local, Enclosing, Global, Builtin) rule. Builtins are the final namespace checked.",
         "Frequently used in data pipelines and API validation logic for quick operations without external imports.",
         ["What happens if you define a variable named 'len'?", "How do you recover a shadowed built-in?"],
         ["Shadowing built-in names like 'list', 'dict', 'str', or 'id' by naming local variables after them."],
         "Remind candidates never to name variables after built-in types or functions."),
        
        ("PY-BAS-007", "What is the purpose of the 'pass' statement in Python?",
         "'pass' is a null operation (no-op) statement used as a syntactic placeholder where code is syntactically required but no action is needed.",
         "Python syntax requires an indented block of code after compound statements such as def, class, if, or try. When drafting abstract interfaces, stubbing methods during test-driven development, or creating empty exception handlers, 'pass' allows the file to parse and execute without syntax errors.",
         "class UnimplementedServiceError(Exception):\n    pass\n\ndef background_sync_worker():\n    pass  # To be implemented in next sprint",
         "Using pass in custom exception classes and function stubs.",
         "In bytecode, 'pass' emits no operational bytecode instructions, or in older versions a NOP (no operation). CPython's optimizer strips redundant pass statements during bytecode compilation.",
         "Used when declaring custom exception hierarchies that simply inherit from Exception with no extra attributes.",
         ["How does 'pass' differ from an ellipsis '...'?", "Does 'pass' have runtime overhead?"],
         ["Assuming 'pass' terminates a loop like 'break' does. 'pass' does nothing; execution proceeds normally."],
         "Mention that '...' (Ellipsis) is often preferred over 'pass' in modern type stubs and abstract definitions."),

        ("PY-BAS-008", "What is the difference between 'break' and 'continue' in loops?",
         "'break' terminates the innermost enclosing loop immediately, while 'continue' skips the remainder of the current iteration and jumps to the next iteration.",
         "Both are loop control statements. 'break' exits the loop entirely, passing control to the statement following the loop block. 'continue' aborts the current cycle, re-evaluating the loop condition in a while loop or advancing to the next item in a for loop.",
         "for n in range(5):\n    if n == 2:\n        continue  # skip 2\n    if n == 4:\n        break     # stop at 4\n    print(n, end=' ')  # Output: 0 1 3",
         "Demonstrating break and continue execution paths.",
         "In bytecode, 'break' emits a BREAK_LOOP (or JUMP_FORWARD to the loop exit address), while 'continue' emits a JUMP_ABSOLUTE/JUMP_BACKWARD to the loop header instruction.",
         "Used in event loops and message consumers to skip invalid records ('continue') or break out when shutdown signals are received ('break').",
         ["How do 'break' and 'continue' interact with the 'else' clause of a for loop?", "Can 'break' exit multiple nested loops?"],
         ["Believing that 'continue' breaks out of the loop."],
         "Highlight that if a loop exits via 'break', its 'else:' clause does NOT execute."),

        ("PY-BAS-009", "How does the 'else' clause work with 'for' and 'while' loops?",
         "The 'else' block of a loop executes if and only if the loop completes normally without encountering a 'break' statement.",
         "Python provides a unique 'for-else' and 'while-else' construct. The code inside 'else:' executes after the iterable is exhausted (in for) or the condition becomes false (in while). If the loop is terminated prematurely by a 'break' statement or an unhandled exception, the 'else' block is bypassed.",
         "target = 42\nnumbers = [10, 20, 30, 40]\nfor item in numbers:\n    if item == target:\n        print('Found!')\n        break\nelse:\n    print('Target not found in list.')",
         "Searching for an element without maintaining a boolean flag variable.",
         "The compiler links the normal loop termination jump to the beginning of the 'else' code block. The 'break' instruction jumps to the address immediately following the 'else' block.",
         "Eliminates the need for 'found = False' flag variables when searching lists or verifying preconditions in backend validation routines.",
         ["Why do many developers find loop 'else' clauses confusing?", "Does 'return' inside a loop trigger the 'else' block?"],
         ["Assuming the 'else' block executes when the loop does NOT run at all. If the iterable is empty, 'else' still executes because no 'break' occurred."],
         "Frame loop-else as 'nobreak': it runs when no break was encountered."),

        ("PY-BAS-010", "What are docstrings and how do they differ from comments?",
         "Docstrings are multi-line string literals defined as the first statement in a module, class, or function retained at runtime as __doc__, while comments (#) are discarded during compilation.",
         "Comments are human-readable annotations starting with '#' meant for source code readers and completely ignored by the compiler. Docstrings (PEP 257) are stored in the object's __doc__ attribute, accessible programmatically at runtime by tools like help(), Sphinx, and IDEs for auto-completion.",
         "def calculate_tax(income: float, rate: float = 0.2) -> float:\n    \"\"\"Calculate total tax for a given income.\n\n    :param income: Gross taxable income.\n    :param rate: Tax rate as decimal (default 0.2).\n    :return: Total calculated tax.\n    \"\"\"\n    return income * rate\n\nprint(calculate_tax.__doc__)",
         "Writing and inspecting a standard Sphinx/reST formatted docstring.",
         "The CPython parser detects string literals at the start of a code suite and binds them to the PyCodeObject's co_consts table, assigning it to the module, class, or function's __doc__ attribute upon instantiation.",
         "Essential in production APIs and shared microservice SDKs for generating automated documentation with Sphinx, MkDocs, or FastAPI Swagger docs.",
         ["How does Python optimize away docstrings when run with -OO flag?", "What are common docstring formats (Google, NumPy, Sphinx)?"],
         ["Using regular inline comments to document public APIs instead of docstrings, making them invisible to introspection tools."],
         "Mention running python with -OO strips docstrings from memory in resource-constrained environments."),

        ("PY-BAS-011", "What is the difference between mutable and immutable objects in Python?",
         "Immutable objects cannot have their state or value changed after creation; mutable objects allow in-place modification without changing their memory address.",
         "In Python, integers, floats, strings, tuples, frozensets, and booleans are immutable. Lists, dictionaries, sets, and bytearrays are mutable. Modifying an immutable object results in the allocation of a completely new object in memory with a new identity, whereas modifying a mutable object updates its internal data structure in place.",
         "s = 'hello'\n# s[0] = 'H'  # Raises TypeError: 'str' object does not support item assignment\ns = s + ' world'  # Creates a new string object\n\nlst = [1, 2, 3]\nlst.append(4)  # Modifies existing list in place\nprint(lst)  # [1, 2, 3, 4]",
         "Demonstrating in-place mutation vs reallocation.",
         "Mutable objects like PyListObject contain internal dynamic arrays of pointers that can be reallocated (over-allocated) as elements grow. Immutable objects like PyTupleObject or PyUnicodeObject have fixed buffer allocations allocated once at creation.",
         "Immutable objects are inherently thread-safe and can be safely used as dictionary keys and set elements because their hash value never changes.",
         ["Can a tuple contain mutable objects? Is that tuple hashable?", "Why can't lists be used as dictionary keys?"],
         ["Believing that variables are mutable or immutable. In Python, objects have mutability, while variables are merely references."],
         "Highlight that a tuple containing a list cannot be hashed, showing that immutability is deep for hashing."),

        ("PY-BAS-012", "What is string interning in Python?",
         "String interning is an optimization technique where CPython caches distinct immutable string objects so identical strings share the exact same memory address.",
         "To conserve memory and accelerate dictionary lookups, CPython interns strings that look like Python identifiers (ASCII letters, digits, underscores) at compile time. Interned strings can be compared in O(1) time using pointer comparison ('is') rather than character-by-character string traversal ('=='). Developers can also explicitly intern strings using sys.intern().",
         "import sys\na = sys.intern('custom_long_identifier_token')\nb = sys.intern('custom_long_identifier_token')\nprint(a is b)  # True (exact same memory address)",
         "Explicitly interning strings using sys.intern().",
         "CPython maintains an internal global dictionary of interned strings (interned in PyUnicode_InternInPlace). When a string is interned, if it already exists in the table, the reference count of the existing string is incremented and returned, discarding the duplicate.",
         "Used in compilers, serializers, parsers, and ORMs where millions of identical keys (like column names) are loaded into memory.",
         ["Does Python automatically intern all strings?", "Why aren't strings with spaces interned automatically?"],
         ["Assuming all strings are interned. Runtime dynamically generated strings with spaces or punctuation are typically not interned automatically."],
         "Mention that dictionary lookups depend on string interning for ultra-fast symbol table resolution."),

        ("PY-BAS-013", "What is the small integer caching mechanism in CPython?",
         "CPython pre-allocates an array of integer objects for values between -5 and 256 at interpreter startup and reuses them across the entire application.",
         "Because small integers are ubiquitously used as loop counters, indexing offsets, and status codes, allocating a new PyLongObject every time one is referenced would cause heavy memory fragmentation. CPython creates these singletons once at initialization; any variable assigned an integer in this range references the pre-allocated singleton.",
         "a = 256\nb = 256\nprint(a is b)  # True (small int cache)\n\nx = 257\ny = 257\nprint(x is y)  # False in interactive REPL (outside cache)",
         "Demonstrating small integer caching boundaries.",
         "In CPython's longobject.c, an array of 262 integer objects is defined via static PyLongObject small_ints[262]. The macro IS_SMALL_INT(val) checks if (-5 <= val && val <= 256) and returns the cached pointer directly.",
         "Saves substantial memory in high-throughput backend services that handle frequent numeric iterations, HTTP status codes, and loop operations.",
         ["Why does x = 257; y = 257 evaluate to True when executed inside the same script file?", "What is code-block constant folding?"],
         ["Relying on 'is' for integer comparisons in production logic instead of '=='."],
         "Explain that in scripts, the compiler constant-folds identical literals in the same code object, which is why 257 is 257 can be True in a file but False in REPL."),

        ("PY-BAS-014", "What is the difference between 'del' and garbage collection?",
         "'del' deletes a variable name reference from a namespace, decrementing the object's reference count, whereas garbage collection frees the underlying memory when the count reaches zero.",
         "'del x' does not directly destroy the object in memory. Instead, it unbinds the name 'x' from the current scope's symbol table and decrements the target object's ob_refcnt by 1. Only when the reference count drops to 0 (or when the cyclic GC resolves an isolated cycle) does CPython deallocate the memory via PyObject_Free.",
         "import sys\na = [1, 2, 3]\nb = a\nprint('Ref count before del:', sys.getrefcount(a) - 1)\ndel a  # Unbinds 'a', object still alive via 'b'\nprint('List accessible via b:', b)",
         "Demonstrating that del removes the variable name, not necessarily the object.",
         "When 'del x' executes, CPython invokes the DELETE_NAME or DELETE_FAST opcode. If Py_DECREF brings the object's ob_refcnt to zero, the object's tp_dealloc callback is invoked immediately to release memory back to pymalloc.",
         "Used in memory-intensive operations (e.g. processing large pandas DataFrames or image buffers) to release references early before entering long loops.",
         ["What happens if two objects reference each other and you 'del' both variables?", "What is cyclic garbage collection?"],
         ["Thinking 'del obj' guarantees immediate deallocation. If other references exist, the object persists."],
         "Be precise: 'del' deletes the reference, not the memory."),

        ("PY-BAS-015", "What is unpacking in Python and how does the '*' operator assist it?",
         "Unpacking allows iterable elements to be extracted and assigned to individual variables in a single expression, with '*' capturing excess elements into a list.",
         "Extended iterable unpacking (PEP 3132) allows clean destructuring of tuples, lists, and iterators. A single asterisk (*) can be prefixed to one variable in the assignment target to capture any unmatched elements as a list.",
         "first, *middle, last = [10, 20, 30, 40, 50]\nprint(f'First: {first}, Middle: {middle}, Last: {last}')\n# First: 10, Middle: [20, 30, 40], Last: 50",
         "Using extended unpacking to split head, middle, and tail of a collection.",
         "The compiler translates extended unpacking into UNPACK_EX bytecode. UNPACK_EX takes an argument encoding the number of items expected before and after the starred variable and slices the sequence in C accordingly.",
         "Used widely in API response processing, command-line argument parsing, and data migration scripts.",
         ["Can you have two '*' variables in a single assignment?", "How does '**' unpacking work for dictionaries?"],
         ["Placing multiple starred expressions in a single assignment, which causes a SyntaxError: multiple starred expressions in assignment."],
         "Highlight that the variable with '*' always receives a list, even if it captures zero or one element."),

        ("PY-BAS-016", "What is the difference between 'range' and 'enumerate'?",
         "'range' generates an arithmetic progression of integers, whereas 'enumerate' yields 2-tuples containing an auto-incrementing index and the corresponding item from an iterable.",
         "'range(start, stop, step)' is an immutable sequence type representing numbers. 'enumerate(iterable, start=0)' is an iterator wrapper that pairs each element of an existing collection with a sequential index counter, avoiding manual index tracking.",
         "fruits = ['apple', 'banana', 'cherry']\nfor idx, fruit in enumerate(fruits, start=1):\n    print(f'{idx}: {fruit}')",
         "Iterating over collections cleanly with enumerate.",
         "range objects compute values on demand in O(1) time and memory using arithmetic formulas rather than storing elements in memory. enumerate stores the underlying iterator and an internal integer counter, advancing both on each __next__() call.",
         "Used whenever both position and item values are required, such as rendering numbered lists in reports or tracking error line numbers during file parsing.",
         ["Why is 'for i in range(len(items)):' considered an anti-pattern in Python?", "What is the memory consumption of range(10**9)?"],
         ["Using 'range(len(lst))' followed by 'lst[i]' instead of idiomatic 'enumerate(lst)'."],
         "Emphasize that 'enumerate' is the idiomatic Python alternative to C-style indexing loops."),

        ("PY-BAS-017", "What are positional-only and keyword-only arguments in Python functions?",
         "Positional-only arguments (marked by '/') must be passed by position; keyword-only arguments (marked by '*') must be passed by keyword name.",
         "Introduced in PEP 570 and PEP 3102, these syntax markers control how callers supply arguments. Parameters before '/' cannot be called using keyword arguments (e.g., func(x=1) fails). Parameters after '*' must be specified with keyword names (e.g., func(1, mode='fast')).",
         "def configure_server(host, port, /, *, debug=False, timeout=30):\n    return f'{host}:{port} (debug={debug}, timeout={timeout})'\n\n# configure_server(host='localhost', 8080)  # TypeError\nprint(configure_server('localhost', 8080, debug=True))",
         "Function enforcing positional-only and keyword-only parameters.",
         "CPython stores parameter counts in the function's PyCodeObject: co_argcount (positional), co_posonlyargcount (positional-only), and co_kwonlyargcount (keyword-only). The argument parser validates caller inputs against these counts before creating the frame.",
         "Essential in library and framework development (like FastAPI and Django) to prevent callers from depending on internal parameter names or to mandate explicit flags.",
         ["Why are positional-only parameters useful when maintaining public APIs?", "What does a bare '*' signify in a function definition?"],
         ["Assuming '/' allows both positional and keyword arguments. Anything before '/' strictly forbids keyword calls."],
         "Mention that built-in functions like len() or pow() are positional-only in CPython for speed and simplicity."),

        ("PY-BAS-018", "What is the ternary conditional operator in Python?",
         "Python's ternary operator evaluates an expression conditionally in a single line using the syntax: 'x if condition else y'.",
         "Unlike C-style 'condition ? x : y', Python uses English-like readability: 'val = true_expr if condition else false_expr'. It evaluates lazily: only the chosen branch expression is evaluated at runtime.",
         "status_code = 200\nmessage = 'Success' if status_code == 200 else 'Error'\nprint('Result:', message)",
         "Concise conditional assignment using inline if-else.",
         "The compiler emits conditional jump bytecode (POP_JUMP_IF_FALSE or similar). If the condition evaluates to truthy, the first expression is evaluated and jumps past the else block; otherwise, the second expression evaluates.",
         "Used in configuration defaults, data serialization, and simple fallback assignments where full if-else blocks add unnecessary vertical clutter.",
         ["Can ternary expressions be nested? Why should deep nesting be avoided?", "Does the unchosen branch get evaluated?"],
         ["Writing 'condition ? a : b', which is a SyntaxError in Python."],
         "Mention short-circuit evaluation: if the condition is True, the 'else' expression is never executed."),

        ("PY-BAS-019", "What is the difference between 'raise' and 'raise from' in exception handling?",
         "'raise' triggers an exception, while 'raise from' explicitly chains an original causal exception to a new exception via the __cause__ attribute.",
         "Exception chaining (PEP 3134) preserves the diagnostic context when re-raising or translating low-level exceptions into domain-specific exceptions. 'raise NewError from original_error' populates __cause__, making the traceback show 'The above exception was the direct cause of the following exception'. Writing 'raise NewError from None' suppresses previous traceback context.",
         "class DatabaseConnectionError(Exception):\n    pass\n\ndef query_db():\n    try:\n        raise ConnectionRefusedError('TCP handshake failed')\n    except ConnectionRefusedError as exc:\n        raise DatabaseConnectionError('Database unavailable') from exc",
         "Explicit exception chaining with 'from exc'.",
         "When 'raise e from cause' is executed, CPython sets e.__cause__ = cause and e.__suppress_context__ = False. In uncaught traceback printing, the traceback formatter recursively displays the causal chain.",
         "Vital in clean backend architecture: wrap low-level driver errors (e.g. psycopg2.OperationalError) into domain exceptions (e.g. ServiceUnavailableException) without losing root-cause diagnostics.",
         ["How do you completely hide the internal traceback when raising an exception?", "What is the difference between __cause__ and __context__?"],
         ["Catching an exception and raising a new one without 'from', which can create confusing implicit context tracebacks."],
         "Explain 'from None' for clean client-facing API error masking to prevent leaking internal database stack traces."),

        ("PY-BAS-020", "What is the Zen of Python and how do you access it?",
         "The Zen of Python is a collection of 19 guiding design aphorisms for writing idiomatic Python, accessed by executing 'import this'.",
         "Authored by Tim Peters in PEP 20, the Zen of Python encapsulates core engineering values such as: 'Explicit is better than implicit', 'Simple is better than complex', 'Readability counts', and 'Errors should never pass silently'. It serves as a philosophical guide for library design and code reviews.",
         "import this",
         "Executing 'import this' outputs the 19 aphorisms of Python philosophy.",
         "In CPython, this.py contains an obfuscated string encoded with the ROT13 substitution cipher that decodes and prints the aphorisms upon import.",
         "Referenced during technical architecture reviews and PEP discussions when evaluating whether a proposed API design is 'Pythonic'.",
         ["Name three core principles from the Zen of Python.", "How does 'Explicit is better than implicit' apply to Python imports?"],
         ["Using wildcard imports ('from module import *'), which directly violates 'Explicit is better than implicit'."],
         "Quote 'Explicit is better than implicit' or 'Flat is better than nested' in design interviews to demonstrate idiomatic alignment."),

        ("PY-BAS-021", "What are type hints in Python and do they affect runtime performance?",
         "Type hints (PEP 484) are optional annotations specifying expected data types of variables, arguments, and return values, with zero runtime enforcement by standard CPython.",
         "Introduced in Python 3.5, type hints improve code documentation, enable static analysis tools (mypy, pyright), and enhance IDE auto-completion. CPython parses and stores type annotations in the __annotations__ dictionary of functions or classes at module load time, but does not perform runtime type checking or optimization based on them.",
         "def greet(name: str, repeat: int = 1) -> str:\n    return f'Hello, {name}! ' * repeat\n\nprint(greet.__annotations__)",
         "Defining type hints and inspecting __annotations__ at runtime.",
         "Annotations are compiled into dictionary entries in __annotations__. In Python 3.7+ with 'from __future__ import annotations', annotations are stored as raw strings rather than evaluated objects, avoiding circular import issues and reducing startup time.",
         "Heavily used in modern frameworks like FastAPI, Pydantic, and SQLModel for automated request validation, serialization, and OpenAPI schema generation.",
         ["Do type hints make Python run as fast as C or Java?", "How does Pydantic leverage type hints differently than pure CPython?"],
         ["Assuming Python raises a TypeError if you pass an integer to a function annotated with 'name: str'."],
         "Clarify that CPython ignores type hints during execution; libraries like Pydantic or static linters like Mypy do the actual validation."),

        ("PY-BAS-022", "What is the purpose of 'if __name__ == \"__main__\":'?",
         "It checks whether the script is being executed directly as the main program or imported as a module into another script.",
         "When a Python file is run from the command line, CPython sets the special top-level variable __name__ to the string '__main__'. When the file is imported by another script, __name__ is set to the module's file/package name. This boilerplate allows a file to act both as an importable library and an executable CLI script without auto-running top-level code upon import.",
         "def main():\n    print('Executing as standalone application.')\n\nif __name__ == '__main__':\n    main()",
         "Standard entrypoint guard pattern.",
         "During interpreter startup, the initialization routine in pythonrun.c initializes the module '__main__' and sets its __dict__['__name__'] = '__main__'. Imported modules receive their fully qualified module name in __name__.",
         "Standard practice in all entrypoints, test runners, CLI utilities, and database migration scripts to prevent side effects during unit testing imports.",
         ["What happens if you run code directly at the root level of a module without this guard?", "How does pytest interact with module-level execution?"],
         ["Running expensive operations or server listeners at root level, causing them to execute unexpectedly whenever another file imports a utility function."],
         "Explain that unit tests will inadvertently execute the script if this guard is omitted."),

        ("PY-BAS-023", "What is the difference between 'print()' and 'sys.stdout.write()'?",
         "'print()' formats arguments into strings, appends a newline by default, and flushes optionally, while 'sys.stdout.write()' writes raw strings directly without automatic separators or newlines.",
         "'print(*args, sep=\" \", end=\"\\n\", file=sys.stdout, flush=False)' is a high-level formatting utility that converts non-string objects via str() and writes them out. 'sys.stdout.write(s)' is a lower-level stream writer that accepts only strings and requires explicit '\\n'.",
         "import sys\n\nprint('Hello', 'World')  # Adds space and newline\nsys.stdout.write('Direct stream write\\n')  # Explicit newline needed",
         "Comparing print vs direct standard output stream writing.",
         "print() internally calls PyFile_WriteObject and handles string coercion, separators, and ending characters before invoking the underlying stream's write method. sys.stdout.write calls the TextIOWrapper buffer directly.",
         "sys.stdout.write is used in high-performance CLI progress bars, real-time logging, and interactive terminal interfaces where newline control and speed are critical.",
         ["Why is sys.stdout.write faster than print in tight loops?", "How do you flush standard output immediately in Python?"],
         ["Passing integers or floats to sys.stdout.write(), which raises a TypeError."],
         "Mention that print(..., flush=True) or sys.stdout.flush() is needed when outputting real-time logs in Docker containers with buffered I/O."),

        ("PY-BAS-024", "What are Python context managers and the 'with' statement?",
         "Context managers are objects that allocate and automatically release resources using the __enter__ and __exit__ dunder methods via the 'with' statement.",
         "The 'with' statement (PEP 343) guarantees that setup and cleanup logic are executed predictably, even if exceptions occur during execution. It eliminates resource leaks (such as unclosed file descriptors, dangling database connections, or unreleased locks) without requiring verbose try-finally boilerplate.",
         "with open('sample.txt', 'w') as f:\n    f.write('Safe file handling')\n# File is automatically closed upon exiting the block, even if an error occurred",
         "Automatic file resource cleanup with the 'with' statement.",
         "When entering 'with mgr as var:', Python calls type(mgr).__enter__(mgr). The return value is bound to 'var'. When leaving the block, type(mgr).__exit__(mgr, exc_type, exc_val, exc_tb) is guaranteed to execute. If __exit__ returns True, any raised exception is suppressed.",
         "Ubiquitous in backend development: database sessions (db.session), distributed Redis locks, transaction management, and mocking during tests.",
         ["How do you create a context manager using a generator?", "What do the arguments to __exit__ represent?"],
         ["Assuming 'with' catches and silences all exceptions. Exceptions are propagated unless __exit__ explicitly returns True."],
         "Mention the contextlib.contextmanager decorator as the idiomatic shortcut to writing full classes with __enter__ and __exit__."),

        ("PY-BAS-025", "What is the difference between 'repr()' and 'str()' in Python?",
         "'str()' returns a human-readable informal string representation for end users, while 'repr()' returns an unambiguous, formal representation useful for debugging and development.",
         "'str(obj)' calls obj.__str__() and aims to be readable, user-facing, and clean. 'repr(obj)' calls obj.__repr__() and aims to be unambiguous, often returning a valid Python expression that could recreate the object when passed to eval(). If __str__ is not defined on a class, Python falls back to __repr__.",
         "import datetime\ntoday = datetime.date.today()\nprint(str(today))   # '2026-11-21' (readable)\nprint(repr(today))  # 'datetime.date(2026, 11, 21)' (unambiguous)",
         "Distinguishing str vs repr output on date objects.",
         "In CPython, PyObject_Str and PyObject_Repr invoke the tp_str and tp_repr function pointers in the object's type struct. In interactive REPL shells, expressions are echoed using repr().",
         "Implementing __repr__ on domain models and ORM entities ensures informative logs and debugger stack traces when diagnosing production incidents.",
         ["What happens if a class defines __str__ but not __repr__?", "What should repr() return ideally according to convention?"],
         ["Defining only __str__ in custom classes. Best practice is to always define __repr__ first, because __str__ defaults to __repr__ automatically."],
         "Remember: __repr__ is for developers and debugging; __str__ is for end-user display.")
    ]

    for item in fundamentals_basic_data:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip = item
        qs.append(Question(
            qid=qid, title=title, difficulty="Basic", topic="Python Fundamentals",
            one_line=one_line, detailed=detailed, example_code=code, example_desc=desc,
            internal_working=internal, real_world=rw, follow_ups=follow_ups,
            mistakes=mistakes, tip=tip, related=["[fundamentals.md](fundamentals.md)"],
            references=["https://docs.python.org/3/reference/index.html"]
        ))

    return qs

def get_intermediate_questions():
    qs = []
    
    inter_data = [
        ("PY-INT-001", "Explain Python scopes and the LEGB resolution rule.",
         "Python resolves variable names using the LEGB hierarchy: Local, Enclosing, Global, and Built-in namespaces.",
         "When a variable name is referenced, Python searches namespaces in strict order: 1. Local (names inside the current function/lambda); 2. Enclosing (names in outer enclosing functions of a nested closure); 3. Global (module-level names); 4. Built-in (pre-allocated names in the builtins module). If the name is not found in any of these four namespaces, a NameError is raised.",
         "x = 'global'\ndef outer():\n    x = 'enclosing'\n    def inner():\n        x = 'local'\n        print('Resolved x:', x)\n    inner()\nouter()",
         "Demonstrating local shadowing of enclosing and global scopes.",
         "CPython evaluates local names via fast array indexing (LOAD_FAST opcode) based on compile-time slot offsets. Global and built-in names are resolved at runtime via dictionary lookups (LOAD_GLOBAL), which is slightly slower than local array lookups.",
         "Understanding LEGB is critical when debugging state leakage in Celery tasks or configuring module-level settings in Django applications.",
         ["How do the 'global' and 'nonlocal' keywords modify LEGB lookup?", "Why are local variable lookups faster than global lookups in Python?"],
         ["Confusing global and enclosing scope inside nested closures without using the 'nonlocal' keyword."],
         "Remember that CPython optimizes local variable access into an array index at compile time, making local variable lookups significantly faster than global dictionary lookups."),

        ("PY-INT-002", "What is the difference between 'global' and 'nonlocal' keywords?",
         "'global' declares that a variable refers to module-level scope, while 'nonlocal' binds a variable to the nearest enclosing (non-global) function scope in a closure.",
         "By default, assigning to a variable inside a function creates a local variable. If you intend to modify a module-level variable from inside a function, 'global var_name' must be declared. If you are inside a nested function and need to rebind a variable in an outer enclosing function without affecting the module global scope, 'nonlocal var_name' is used.",
         "def counter():\n    count = 0\n    def increment():\n        nonlocal count\n        count += 1\n        return count\n    return increment\n\nc = counter()\nprint(c(), c())  # Output: 1 2",
         "Using nonlocal to mutate state in an enclosing closure.",
         "CPython compiles 'global' variable modifications using STORE_GLOBAL or STORE_NAME opcodes. 'nonlocal' modifications compile to STORE_DEREF, which accesses a cell object (__closure__) shared between nested stack frames.",
         "Used in custom function decorators, stateful closure factories, and middleware pipelines to maintain per-request state.",
         ["What happens if 'nonlocal' cannot find a matching enclosing variable?", "Can 'nonlocal' bind to a global variable?"],
         ["Attempting to use 'nonlocal' to bind to a global variable, which raises a SyntaxError: no binding for nonlocal found."],
         "Clarify that 'global' jumps straight to module level, whereas 'nonlocal' looks exclusively at intermediate enclosing functions."),

        ("PY-INT-003", "What is the mutable default argument trap and how do you prevent it?",
         "Default argument expressions are evaluated once when the function definition is executed at module load time, not each time the function is called.",
         "If a mutable object (like a list, dictionary, or set) is used as a default argument, all function invocations that omit that parameter share the exact same instance in memory. Appending to the list in one invocation mutates the shared default for all subsequent invocations. The standard fix is to use 'None' as the default sentinel and initialize a new list inside the function body.",
         "def append_to(element, target_list=None):\n    if target_list is None:\n        target_list = []\n    target_list.append(element)\n    return target_list\n\nprint(append_to(1))  # [1]\nprint(append_to(2))  # [2] (independent list)",
         "Fixing the mutable default trap using None as a sentinel.",
         "CPython stores default parameter values in the function object's __defaults__ tuple at the moment the 'def' statement executes. Because the tuple holds a reference to the mutable object, mutating it alters the object stored inside __defaults__.",
         "Extremely common source of production bugs in API route handlers and background tasks where request data inadvertently leaks across distinct user calls.",
         ["How can you inspect a function's default arguments at runtime?", "Is there ever a valid use case for mutable default arguments?"],
         ["Using 'def add_item(item, basket=[])' in production, resulting in cross-request data leaks."],
         "Always answer with the sentinel pattern: default to None and initialize inside the function body."),

        ("PY-INT-004", "What is the difference between shallow copy and deep copy in Python?",
         "A shallow copy creates a new compound object but inserts references to the original child objects; a deep copy recursively duplicates the compound object and all its nested children.",
         "Using copy.copy() duplicates the outer container, meaning modifications to top-level elements of the copy don't affect the original. However, nested mutable elements (like lists inside lists) continue to point to the exact same child objects. copy.deepcopy() recursively traverses the entire object graph, creating fresh copies of all nested structures.",
         "import copy\norig = [[1, 2, 3], [4, 5, 6]]\nshallow = copy.copy(orig)\ndeep = copy.deepcopy(orig)\n\norig[0][0] = 999\nprint('Shallow reflects mutation:', shallow[0][0])  # 999\nprint('Deep remains isolated:', deep[0][0])         # 1",
         "Demonstrating shared nested references in shallow copies vs complete isolation in deep copies.",
         "copy.deepcopy maintains an internal 'memo' dictionary mapping id(obj) to newly created copies to correctly handle circular references and avoid infinite recursion loops.",
         "Used when cloning complex configuration dictionaries, ORM model instances, or game state trees before applying speculative transformations.",
         ["How does copy.deepcopy handle circular references?", "How can a custom class control its copy behavior?"],
         ["Assuming list.copy() or slicing [:] creates a deep copy. Slicing only creates a shallow copy."],
         "Mention __copy__() and __deepcopy__() methods for custom object serialization and cloning control."),

        ("PY-INT-005", "Explain the concept of closures in Python.",
         "A closure is a function object that retains access to variables from its enclosing lexical scope even after that outer scope has finished executing.",
         "When an inner function references a variable defined in its enclosing outer function and the outer function returns the inner function, a closure is created. The inner function retains a reference to those enclosed variables, preserving their values and state across subsequent calls.",
         "def make_multiplier(factor: int):\n    def multiply(x: int) -> int:\n        return x * factor\n    return multiply\n\ndouble = make_multiplier(2)\nprint('Double 5:', double(5))  # 10",
         "Creating a stateful closure function.",
         "CPython creates PyCellObject wrappers for enclosing variables referenced by inner functions. The inner function object stores these cells in its __closure__ attribute. When the outer stack frame is deallocated, the cell objects remain alive in heap memory.",
         "Closures form the technical foundation of Python decorators, callback handlers, and factories in frameworks like Flask and FastAPI.",
         ["How do you inspect the closed-over variables of a function at runtime?", "What is the difference between a closure and a class with __call__?"],
         ["Attempting to rebind a closure variable without the 'nonlocal' keyword, which results in an UnboundLocalError."],
         "Mention inspecting 'fn.__closure__[0].cell_contents' to show interviewers you understand the underlying runtime mechanics."),

        ("PY-INT-006", "What is an UnboundLocalError and why does it occur?",
         "UnboundLocalError occurs when code references a local variable before an assignment has taken place within that function scope.",
         "If a variable is assigned anywhere inside a function body, CPython marks that variable as local to the entire function during compile-time bytecode generation. If you attempt to read or reference that variable before the assignment line executes, Python cannot fall back to the global scope and raises UnboundLocalError.",
         "x = 10\ndef mutate_x():\n    # print(x)  # Would raise UnboundLocalError: local variable 'x' referenced before assignment\n    x = 20\n    return x\nprint(mutate_x())",
         "Illustrating compile-time local variable scoping.",
         "During code generation, the compiler scans all assignment targets (STORE_FAST) and tags those symbols as local. When the execution engine encounters LOAD_FAST before STORE_FAST has initialized the slot, it detects a NULL pointer in the frame and raises UnboundLocalError.",
         "Commonly encountered when developers try to increment a global counter inside a function (e.g. count += 1) without declaring 'global count'.",
         ["How does Python determine variable scope at compile time versus runtime?", "Why doesn't Python fall back to global scope if local assignment is later?"],
         ["Assuming Python is purely interpreted line-by-line; CPython determines local scope during the initial AST-to-bytecode compilation step."],
         "Explain that scoping decisions happen at compile time, not during runtime line execution."),

        ("PY-INT-007", "What is monkey patching in Python and what are its production risks?",
         "Monkey patching is the runtime modification of a class or module's attributes, methods, or functions without altering the original source code.",
         "Because Python classes and modules are mutable objects at runtime, developers can overwrite existing methods with custom functions dynamically. While useful for mocking external services in unit tests or applying hotfixes, monkey patching in production makes code unpredictable, complicates debugging, breaks static type checking, and creates hard-to-trace bugs.",
         "import math\n\ndef mock_sqrt(x):\n    return 42.0\n\n# Monkey patching math.sqrt\nmath.sqrt = mock_sqrt\nprint('Patched sqrt(9):', math.sqrt(9))",
         "Dynamically patching a standard library function at runtime.",
         "In CPython, module and class attribute lookups resolve via their __dict__ mapping. Monkey patching modifies the underlying dictionary entry directly at runtime, affecting all subsequent lookups across the entire process.",
         "Used legitimate in testing libraries (e.g. unittest.mock, gevent, eventlet) to replace blocking socket calls with cooperative greenlet calls.",
         ["Why is monkey patching dangerous in multi-threaded environments?", "How does unittest.mock.patch safely restore original behavior?"],
         ["Applying monkey patches in production application code, leading to side-effects that break other third-party dependencies."],
         "Emphasize that monkey patching should be strictly reserved for testing or controlled framework bootstrapping (like Gevent)."),

        ("PY-INT-008", "What is the difference between *args and **kwargs in function definitions?",
         "*args collects extra positional arguments into a tuple, while **kwargs collects extra keyword arguments into a dictionary.",
         "*args allows a function to accept an arbitrary number of positional arguments. Inside the function, 'args' is accessible as an immutable tuple. **kwargs allows a function to accept an arbitrary number of named keyword arguments, accessible inside the function as a mutable dictionary.",
         "def log_request(endpoint: str, *args, **kwargs):\n    print(f'Endpoint: {endpoint}')\n    print(f'Extra args (tuple): {args}')\n    print(f'Extra kwargs (dict): {kwargs}')\n\nlog_request('/api/v1/users', 'GET', 200, user_id=42, authenticated=True)",
         "Handling arbitrary positional and keyword arguments.",
         "CPython flags functions accepting variable arguments using flags in PyCodeObject.co_flags (CO_VARARGS for *args, CO_VARKEYWORDS for **kwargs). The interpreter packs surplus positional values into a tuple and keyword values into a dict during frame creation.",
         "Extensively used in writing decorators, subclass overrides, and wrapper functions that need to forward arguments transparently to wrapped functions.",
         ["Can you pass both *args and **kwargs to another function?", "What is the required parameter order in function definitions?"],
         ["Placing **kwargs before *args in a function definition, which triggers a SyntaxError."],
         "Mention parameter ordering: standard positional, *args, keyword-only, then **kwargs."),

        ("PY-INT-009", "How do list comprehensions differ from generator expressions in memory and evaluation?",
         "List comprehensions construct the entire list in memory immediately (eager evaluation), whereas generator expressions return a generator iterator that computes items on demand (lazy evaluation).",
         "A list comprehension ([x for x in data]) computes all elements immediately and allocates a full list object in heap memory. A generator expression ((x for x in data)) returns a generator object that produces one value at a time via the iterator protocol (__next__), consuming virtually constant O(1) memory regardless of dataset size.",
         "import sys\nlst = [x * 2 for x in range(10000)]\ngen = (x * 2 for x in range(10000))\nprint('List memory (bytes):', sys.getsizeof(lst))\nprint('Generator memory (bytes):', sys.getsizeof(gen))",
         "Comparing memory consumption of eager list comprehension vs lazy generator expression.",
         "List comprehensions emit bytecode that pre-allocates and appends to a list. Generator expressions compile to an internal code object with YIELD_VALUE instructions, creating a frame that suspends and resumes state upon request.",
         "Generator expressions are critical when streaming gigabytes of database records, parsing massive log files, or chaining processing pipelines without exhausting server RAM.",
         ["When would you choose a list comprehension over a generator expression?", "Can you iterate over a generator expression multiple times?"],
         ["Assuming a generator can be iterated multiple times. Once exhausted, a generator cannot be reset or reused."],
         "State clearly: use list comprehensions when you need indexing, length, or multiple passes; use generators for single-pass memory efficiency."),

        ("PY-INT-010", "What is the '__all__' variable in a Python module?",
         "'__all__' is a module-level list of strings defining the public interface exported when 'from module import *' is used.",
         "By default, 'from module import *' imports all names that do not start with an underscore ('_'). By defining an explicit '__all__' list, module authors restrict public exports strictly to the declared symbols. It also signals to static linters and documentation generators what constitutes the official public API of the library.",
         "# api_client.py\n__all__ = ['Client', 'connect']\n\nclass Client:\n    pass\n\ndef connect():\n    pass\n\ndef _internal_helper():\n    pass",
         "Restricting wildcard exports using __all__.",
         "When CPython encounters IMPORT_STAR bytecode, it checks the target module's dictionary for the key '__all__'. If present, it imports only those keys into the caller namespace; otherwise, it filters module.__dict__ for names not starting with '_'.",
         "Used in __init__.py files of production libraries and packages to provide clean public namespaces and prevent internal implementation helpers from leaking.",
         ["Does '__all__' prevent someone from importing a private function explicitly via 'from module import _internal_helper'?", "What happens if a name in '__all__' doesn't exist?"],
         ["Believing '__all__' provides security or prevents direct explicit imports. It only affects 'import *' and documentation tools."],
         "Emphasize that __all__ defines the public API contract of a package, even though 'import *' is generally discouraged in production."),

        ("PY-INT-011", "How do you create a custom exception class in Python and when should you?",
         "Custom exceptions are created by subclassing the built-in 'Exception' class to provide domain-specific error handling across application layers.",
         "Custom exceptions improve error granularity and allow calling code to catch specific business failures (e.g. InsufficientFundsError) rather than broad generic exceptions (e.g. ValueError). Custom exceptions should always inherit from 'Exception', never directly from 'BaseException', which is reserved for system-terminating signals like KeyboardInterrupt and SystemExit.",
         "class PaymentProcessingError(Exception):\n    \"\"\"Raised when payment gateway transaction fails.\"\"\"\n    def __init__(self, message: str, transaction_id: str, code: int):\n        super().__init__(message)\n        self.transaction_id = transaction_id\n        self.code = code\n\ntry:\n    raise PaymentProcessingError('Declined by issuer', 'tx_9876', 402)\nexcept PaymentProcessingError as err:\n    print(f'Error {err.code}: {err} (Tx: {err.transaction_id})')",
         "Creating and handling a structured custom exception with metadata.",
         "Exception subclasses inherit the standard PyBaseExceptionObject layout in CPython, which maintains args, __traceback__, __cause__, and __context__ pointers.",
         "Standard in clean architecture: defining a domain-specific exception hierarchy (e.g. UserServiceError -> UserNotFoundError, UserSuspendedError) for clean REST API error mapping.",
         ["Why should custom exceptions inherit from Exception rather than BaseException?", "How do you serialize custom exceptions into JSON API responses?"],
         ["Inheriting from BaseException, which prevents standard 'except Exception:' blocks from catching the error."],
         "Mention creating a base domain exception for your service (e.g., ServiceError) and subclassing all specific exceptions from it."),

        ("PY-INT-012", "What is the difference between staticmethod and classmethod in Python?",
         "'classmethod' receives the class object (cls) as its first implicit argument, while 'staticmethod' receives no implicit first argument and behaves like an isolated plain function bound to the class namespace.",
         "A @classmethod is bound to the class rather than instances, making it the standard pattern for alternative constructors and factory methods that support inheritance. A @staticmethod does not access or modify class state (cls) or instance state (self); it is simply a utility function logically namespaced within the class for organizational cohesion.",
         "class User:\n    def __init__(self, name: str, role: str):\n        self.name = name\n        self.role = role\n\n    @classmethod\n    def create_admin(cls, name: str):\n        return cls(name=name, role='Admin')  # Supports inheritance\n\n    @staticmethod\n    def is_valid_username(name: str) -> bool:\n        return len(name) >= 3 and name.isalnum()\n\nu = User.create_admin('Alice')\nprint(f'{u.name}: {u.role}, Valid: {User.is_valid_username(u.name)}')",
         "Alternative constructor via classmethod and validation utility via staticmethod.",
         "Both are implemented using the descriptor protocol. classmethod.__get__ wraps the function in a bound method object prepending the class (cls); staticmethod.__get__ returns the underlying function directly without binding.",
         "Widely used in Django ORM models and Pydantic models for factory instantiation methods (e.g., from_dict(), from_orm()).",
         ["Why is classmethod preferred over hardcoding the class name inside alternative constructors?", "Can staticmethod access instance variables?"],
         ["Using staticmethod for alternative constructors, which breaks factory inheritance when the class is subclassed."],
         "Use @classmethod for alternative constructors (factory pattern); use @staticmethod only for pure utility functions that don't need class or instance state."),

        ("PY-INT-013", "What is the purpose of the '__slots__' declaration in Python classes?",
         "'__slots__' explicitly defines a fixed set of allowed instance attributes, preventing the creation of the default dynamic '__dict__' and significantly reducing memory overhead.",
         "By default, every Python instance stores its attributes in an internal dictionary (__dict__), which consumes substantial memory due to hash table over-allocation. By defining '__slots__ = (\"attr1\", \"attr2\")', CPython allocates a compact fixed-size array of pointers for instance attributes instead, saving 40-70% memory and slightly improving attribute access speed.",
         "class CompactPoint:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\np = CompactPoint(10, 20)\n# p.z = 30  # AttributeError: 'CompactPoint' object has no attribute 'z'",
         "Restricting attribute creation and optimizing memory via __slots__.",
         "In CPython, __slots__ creates descriptor objects (member_descriptor) on the class for each attribute that map directly to fixed C struct offsets in the instance object, bypassing dictionary lookups.",
         "Vital when instantiating millions of lightweight data objects (e.g., geo-coordinates, trading ticks, network packets) where default __dict__ overhead causes OOM crashes.",
         ["Can an instance with __slots__ have dynamic attributes added if '__dict__' is included in __slots__?", "How does inheritance affect classes using __slots__?"],
         ["Assuming subclasses automatically inherit __slots__. If a subclass doesn't declare __slots__, it re-creates a dynamic __dict__."],
         "Highlight that __slots__ is primarily a memory optimization tool, not an access-control mechanism."),

        ("PY-INT-014", "What is the difference between a function and a method in Python?",
         "A function is a standalone callable defined outside a class, while a method is a function bound to a class or instance that automatically receives the instance (self) or class (cls) as its first argument.",
         "In Python, all functions defined within a class body are regular function objects until accessed through an instance. When accessed via an instance (e.g., obj.method), the descriptor protocol's __get__ method dynamically binds the function to the instance, producing a 'bound method' object that automatically passes the instance as 'self'.",
         "class Example:\n    def compute(self, x):\n        return x * 2\n\nobj = Example()\nprint('Class attribute type:', type(Example.compute))  # <class 'function'>\nprint('Instance attribute type:', type(obj.compute))   # <class 'method'>",
         "Demonstrating function vs bound method transformation via attribute lookup.",
         "In CPython, functions implement the descriptor protocol (PyFunction_Type contains tp_descr_get). When obj.compute is evaluated, PyMethod_New binds the function pointer and the instance pointer together into a PyMethodObject.",
         "Understanding bound methods explains how event listeners, callbacks, and thread targets preserve target instance state when passed across APIs.",
         ["How does the descriptor protocol convert a function into a bound method?", "Can you call an unbound method by passing 'self' explicitly?"],
         ["Treating methods as fundamentally distinct types of objects in the class body; they are regular functions until attribute access binds them."],
         "Explain that 'obj.method(arg)' is syntactic sugar for 'Class.method(obj, arg)'."),

        ("PY-INT-015", "How does the 'any()' and 'all()' built-in pair operate with short-circuiting?",
         "'any()' returns True if at least one element is truthy, stopping at the first True; 'all()' returns True if every element is truthy, stopping at the first False.",
         "Both functions iterate over an iterable and apply short-circuit evaluation. 'any()' terminates iteration immediately upon encountering the first truthy value. 'all()' terminates iteration immediately upon encountering the first falsy value. Both return booleans and work efficiently with infinite generators.",
         "numbers = [2, 4, 6, 7, 8]\n# Checks if any number is odd (stops at 7)\nhas_odd = any(n % 2 != 0 for n in numbers)\n# Checks if all numbers are positive\nall_pos = all(n > 0 for n in numbers)\nprint(f'Has odd: {has_odd}, All positive: {all_pos}')",
         "Using any() and all() with generator expressions for short-circuit evaluation.",
         "In CPython, bltinmodule.c implements builtin_any and builtin_all using a simple loop over PyIter_Next. Each item is checked via PyObject_IsTrue. The loop breaks immediately when the condition is satisfied.",
         "Used in authorization checks (verifying if a user has 'all' required permissions or 'any' valid role) and data validation pipelines.",
         ["What does 'all([])' evaluate to and why (vacuous truth)?", "What does 'any([])' evaluate to?"],
         ["Assuming all([]) is False. all([]) is True because there are no falsy values in an empty sequence (vacuous truth)."],
         "Emphasize that passing a generator expression rather than a list comprehension preserves lazy short-circuiting benefits."),

        ("PY-INT-016", "What are Python's magic (dunder) methods and why are they used?",
         "Magic (dunder) methods are special predefined methods with double leading and trailing underscores that enable operator overloading, object lifecycle hooks, and protocol implementation.",
         "Dunder methods (like __init__, __str__, __len__, __getitem__, __enter__, __eq__) allow custom user-defined classes to integrate seamlessly with Python's built-in syntax and protocols. For example, implementing __len__ allows len(obj) to work, and implementing __getitem__ allows indexing via obj[key].",
         "class Vector:\n    def __init__(self, x: int, y: int):\n        self.x = x\n        self.y = y\n\n    def __add__(self, other):\n        return Vector(self.x + other.x, self.y + other.y)\n\n    def __repr__(self):\n        return f'Vector({self.x}, {self.y})'\n\nv1 = Vector(1, 2)\nv2 = Vector(3, 4)\nprint('Added vectors:', v1 + v2)  # Vector(4, 6)",
         "Overloading the '+' operator via __add__.",
         "CPython type structs (PyTypeObject) have pre-allocated function pointer slots (tp_as_number, tp_as_sequence, tp_as_mapping). Implementing dunder methods populates these C-level slots, enabling direct opcode dispatch.",
         "Used extensively in ORM query builders (e.g. SQLAlchemy, Django ORM) to allow pythonic querying expressions like `User.age > 18`.",
         ["How does Python resolve reverse operators like __radd__?", "Can you invent your own arbitrary dunder methods?"],
         ["Calling dunder methods directly like 'obj.__len__()' instead of using the idiomatic built-in 'len(obj)'."],
         "Advise candidates never to invent arbitrary dunder names for their own methods, as Python reserves them for future language evolution."),

        ("PY-INT-017", "What is the difference between '__new__' and '__init__'?",
         "'__new__' is the static constructor that creates and returns a new instance of the class, while '__init__' is the initializer that configures attributes on that created instance.",
         "'__new__(cls, *args, **kwargs)' is called first to allocate the raw object in memory. It must return a newly created instance (typically by calling super().__new__(cls)). Only if __new__ returns an instance of 'cls' is '__init__(self, *args, **kwargs)' invoked to initialize its instance state. '__new__' is used when creating singletons, subclassing immutable types (like tuple, int, or str), or writing metaclasses.",
         "class Singleton:\n    _instance = None\n    def __new__(cls, *args, **kwargs):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance\n\ns1 = Singleton()\ns2 = Singleton()\nprint('Same instance:', s1 is s2)  # True",
         "Implementing the Singleton pattern using __new__.",
         "In typeobject.c, type_call invokes tp_new to allocate the PyObject struct, followed by tp_init to execute the initialization logic.",
         "Essential when designing custom immutable collections, caching factories, or controlling object creation in database ORMs.",
         ["What happens if __new__ returns an instance of a different class?", "Why must __new__ be used when subclassing immutable types like tuple?"],
         ["Attempting to initialize immutable attributes in __init__ when subclassing int or tuple, which is too late because the object is already created."],
         "Clearly state: __new__ creates the object (allocates memory); __init__ initializes the object (populates attributes)."),

        ("PY-INT-018", "What is the difference between 'isinstance()' and 'type()' checks?",
         "'isinstance()' checks if an object is an instance of a class or any of its subclasses (supporting polymorphism), while 'type()' checks for exact class identity.",
         "'isinstance(obj, Class)' respects the inheritance hierarchy: if Dog subclasses Animal, isinstance(dog, Animal) is True. 'type(obj) is Class' checks for an exact match, returning False if 'obj' is a subclass instance. In idiomatic Python, 'isinstance()' is preferred because it adheres to the Liskov Substitution Principle and supports duck typing through Abstract Base Classes.",
         "class Animal:\n    pass\n\nclass Dog(Animal):\n    pass\n\nd = Dog()\nprint(isinstance(d, Animal))  # True (respects inheritance)\nprint(type(d) is Animal)       # False (strict exact type check)",
         "Comparing polymorphic isinstance check vs strict type comparison.",
         "isinstance() calls PyObject_IsInstance, which traverses the object's method resolution order (tp_mro) or checks for virtual subclass registration via __subclasscheck__. type() simply inspects the ob_type pointer directly in O(1) time.",
         "Used in validation libraries, serialization frameworks, and API request parsing where polymorphism and inheritance are common.",
         ["When is 'type(x) is Class' preferred over 'isinstance(x, Class)'?", "How does isinstance() work with tuples of types?"],
         ["Using 'type(x) == Class' everywhere, which breaks when users provide subclasses or mocks."],
         "Recommend isinstance() for general validation because it preserves polymorphism; note that isinstance accepts a tuple of types e.g. isinstance(x, (int, float))."),

        ("PY-INT-019", "What is method chaining and how is it implemented in Python classes?",
         "Method chaining is a design pattern where multiple methods are called sequentially on a single object in one line, achieved by having each method return 'self'.",
         "By returning 'self' at the end of mutating methods, callers can chain successive method calls (e.g. query.filter().order_by().limit()). This pattern creates fluent interfaces and expressive builder APIs.",
         "class QueryBuilder:\n    def __init__(self):\n        self.query = []\n\n    def select(self, fields: str):\n        self.query.append(f'SELECT {fields}')\n        return self  # Return self for chaining\n\n    def from_table(self, table: str):\n        self.query.append(f'FROM {table}')\n        return self\n\n    def build(self) -> str:\n        return ' '.join(self.query)\n\nq = QueryBuilder().select('id, name').from_table('users').build()\nprint('Generated query:', q)",
         "Implementing a fluent query builder using method chaining.",
         "Each method invocation in the chain evaluates to the PyObject reference returned by the previous method. Since 'self' is returned, the next method is resolved against the same instance's dictionary.",
         "Standard pattern in database ORMs (Django QuerySet, SQLAlchemy Query), data manipulation libraries (Pandas), and HTTP client builders.",
         ["What are the debugging disadvantages of long method chains?", "How does method chaining differ from function composition?"],
         ["Forgetting to 'return self', causing the next chained method to fail with an AttributeError: 'NoneType' object has no attribute ..."],
         "Point out the trade-off: method chaining creates concise, expressive code, but makes line-by-line debugging and breakpoint inspection more challenging."),

        ("PY-INT-020", "What is the difference between 'getattr()', 'setattr()', and 'hasattr()'?",
         "They are built-in reflection utilities used to dynamically inspect, retrieve, modify, or verify the existence of object attributes using string names.",
         "'getattr(obj, \"name\", default)' retrieves an attribute dynamically, returning a default fallback if it doesn't exist. 'setattr(obj, \"name\", value)' assigns a value to an attribute dynamically. 'hasattr(obj, \"name\")' returns True if the attribute exists, internally calling getattr() and checking if an AttributeError is raised.",
         "class Config:\n    host = 'localhost'\n    port = 8000\n\ncfg = Config()\nattr_name = 'port'\nif hasattr(cfg, attr_name):\n    print('Port:', getattr(cfg, attr_name))\nsetattr(cfg, 'port', 9000)\nprint('Updated Port:', cfg.port)",
         "Dynamically accessing and modifying attributes using reflection.",
         "getattr() and setattr() compile directly to PyObject_GetAttr and PyObject_SetAttr in CPython, dispatching through the class descriptor protocol (tp_getattro / tp_setattro).",
         "Critical in serialization libraries, dynamic ORM field loaders, plugin architectures, and CLI argument parsers that map string names to object properties.",
         ["What was the historical performance bug with hasattr() in older Python versions?", "How does getattr differ from direct dictionary access obj.__dict__['name']?"],
         ["Assuming hasattr() is a cheap check. If a property raises an exception during calculation, hasattr() can mask unexpected errors."],
         "Prefer getattr(obj, 'attr', default) over 'if hasattr(obj, 'attr'): getattr(obj, 'attr')' to avoid double attribute lookup."),

        ("PY-INT-021", "Explain the difference between 'callable()' and '__call__()' in Python.",
         "'callable()' is a built-in function that checks whether an object can be called, while '__call__()' is the dunder method that makes a class instance callable like a regular function.",
         "An object is callable if its class implements the '__call__' dunder method. Functions, lambdas, classes (calling a class invokes its constructor), and methods are all callable. By implementing '__call__' on a custom class, instances can maintain internal state while behaving syntactically like functions.",
         "class RateLimiter:\n    def __init__(self, limit: int):\n        self.limit = limit\n        self.calls = 0\n\n    def __call__(self, client_id: str) -> bool:\n        self.calls += 1\n        return self.calls <= self.limit\n\nlimiter = RateLimiter(limit=2)\nprint('Is callable?', callable(limiter))  # True\nprint('Call 1:', limiter('client_1'))    # True\nprint('Call 2:', limiter('client_1'))    # True\nprint('Call 3:', limiter('client_1'))    # False",
         "Making a class instance callable using __call__ to track state.",
         "The CPython C-struct PyTypeObject contains a tp_call function pointer. If tp_call is non-NULL (which happens when __call__ is defined), PyCallable_Check returns 1 and the CALL opcode executes tp_call.",
         "Extensively used in FastAPI dependency injection, stateful middleware, ML model inference pipelines, and parameterized decorators.",
         ["How do closures compare with callable class instances?", "Can you rebind __call__ on a specific instance at runtime?"],
         ["Rebinding __call__ on an individual instance (instance.__call__ = ...) does not work because CPython looks up dunder methods on the class, not the instance dictionary."],
         "Highlight that callable instances are great for stateful logic, whereas pure functions or closures are preferred for stateless behavior."),

        ("PY-INT-022", "What is the purpose of the 'zip()' function and the 'strict' parameter in Python 3.10?",
         "'zip()' aggregates elements from multiple iterables into tuples; the 'strict=True' parameter (introduced in Python 3.10) ensures all iterables have identical lengths, raising a ValueError otherwise.",
         "Historically, zip() silently truncated iteration to the length of the shortest iterable when passed iterables of unequal length. This caused subtle data loss bugs in production. Python 3.10 introduced 'strict=True' to raise a ValueError if any iterable is exhausted before the others, guaranteeing 1-to-1 parity.",
         "names = ['Alice', 'Bob', 'Charlie']\nscores = [95, 88, 92]\npaired = list(zip(names, scores, strict=True))\nprint('Paired records:', paired)\n\n# unequal_zip = list(zip(['a', 'b'], [1, 2, 3], strict=True))  # Raises ValueError",
         "Safely combining parallel datasets with zip(..., strict=True).",
         "zip returns a zipobject iterator that calls PyIter_Next on each source iterable sequentially. When strict=True is set, after one iterator signals exhaustion, zip checks if any remaining iterators still yield items, raising a ValueError if so.",
         "Used when combining database column headers with row values, transforming matrix coordinates, or pairing inputs with target labels in ML training data.",
         ["What happens with regular zip() without strict=True when iterables have different lengths?", "How does itertools.zip_longest differ from zip(..., strict=True)?"],
         ["Using regular zip() on data pipelines without validating lengths, leading to silent truncation of trailing records."],
         "Mention Python 3.10's 'strict=True' flag as a modern defensive programming best practice for data integrity."),

        ("PY-INT-023", "What is operator overloading and how is it implemented in Python?",
         "Operator overloading is the mechanism of customizing the behavior of standard language operators (+, -, *, ==, <) for user-defined classes by implementing corresponding dunder methods.",
         "Python does not permit creating new operator symbols, but allows existing operators to be overloaded by implementing special methods (e.g., __add__ for +, __sub__ for -, __mul__ for *, __eq__ for ==, __lt__ for <). This makes domain objects intuitive and expressive.",
         "class Money:\n    def __init__(self, amount: float, currency: str):\n        self.amount = amount\n        self.currency = currency\n\n    def __add__(self, other):\n        if not isinstance(other, Money) or self.currency != other.currency:\n            raise ValueError('Cannot add different currencies')\n        return Money(self.amount + other.amount, self.currency)\n\n    def __repr__(self):\n        return f'{self.amount} {self.currency}'\n\nm1 = Money(100.0, 'USD')\nm2 = Money(50.0, 'USD')\nprint('Total:', m1 + m2)  # 150.0 USD",
         "Overloading '+' operator with domain currency validation.",
         "When an expression like 'a + b' is evaluated, CPython checks if type(a) implements tp_as_number->nb_add. If it returns NotImplemented, CPython checks if type(b) implements __radd__ (reflected add).",
         "Used in financial models, mathematical vector libraries (NumPy), and ORM query builders (e.g. constructing SQL WHERE clauses using Python comparison operators).",
         ["What should a comparison dunder method return if it does not support the operand type?", "What is the role of 'NotImplemented' in operator overloading?"],
         ["Raising TypeError directly instead of returning 'NotImplemented', which prevents Python from attempting the reflected operator (e.g. __radd__) on the other operand."],
         "Always return 'NotImplemented' (the singleton object), NOT 'raise NotImplementedError', so Python can try the reflected operator on the right-hand operand."),

        ("PY-INT-024", "What is the difference between 'isinstance()' and '__subclasscheck__'?",
         "'isinstance()' checks if an object is an instance of a class, while '__subclasscheck__' is an internal hook on metaclasses (such as ABCMeta) that customizes virtual subclass detection.",
         "Standard inheritance uses concrete class ancestry. Abstract Base Classes (ABCs) use '__subclasscheck__' and '__instancecheck__' to allow classes to be recognized as virtual subclasses of an interface (via ABC.register()) without explicitly inheriting from it. This powers structural and interface compliance checks.",
         "from collections.abc import Iterable\n\nclass CustomSequence:\n    def __iter__(self):\n        return iter([1, 2, 3])\n\n# CustomSequence never inherited from Iterable, but satisfies its interface\nprint(isinstance(CustomSequence(), Iterable))  # True",
         "Virtual subclass detection using Abstract Base Classes.",
         "When isinstance(x, C) is called, CPython first checks if type(C) defines an __instancecheck__ method. ABCMeta implements this by verifying whether the class or any of its parents are registered in the ABC's virtual subclass cache.",
         "Used in enterprise architectures and framework plugins where loose coupling is required: components satisfy interfaces without rigid inheritance bindings.",
         ["How does ABC.register() work under the hood?", "What is the difference between nominal subtyping and structural subtyping?"],
         ["Assuming that classes must inherit explicitly from a base class to satisfy isinstance() checks against collections.abc interfaces."],
         "Connect this to Python's duck typing philosophy: 'if it walks like a duck and quacks like a duck, it is a duck.'"),

        ("PY-INT-025", "What are Python closures vs lambda functions?",
         "A lambda is an anonymous inline function defined with a single expression, whereas a closure is a function (named or lambda) that captures and retains variables from an enclosing lexical scope.",
         "Lambdas are simply syntactical shortcuts for defining small, throwaway functions restricted to a single expression (e.g., lambda x: x * 2). A closure is an architectural mechanism where an inner function captures free variables from its enclosing scope. A lambda can be a closure if it closes over external variables, but not all lambdas are closures, and most closures are defined using standard 'def' statements.",
         "def create_adder(x: int):\n    return lambda y: x + y  # Lambda acting as a closure over 'x'\n\nadd_five = create_adder(5)\nprint('Add 5 to 10:', add_five(10))  # 15",
         "A lambda function operating as a closure.",
         "Both compile to standard PyCodeObject instances. The only difference is that lambdas are anonymous (their co_name is '<lambda>') and their body syntax is restricted by the compiler to an expression rather than a suite of statements.",
         "Lambdas are commonly used for short key functions in sort operations (sorted(items, key=lambda x: x.price)), while closures are used for middleware factories, decorators, and stateful callbacks.",
         ["Can a lambda function contain statements like 'if-else' or loops?", "Why is 'def' preferred over assigning a lambda to a variable (PEP 8)?"],
         ["Assigning lambdas to variable names (e.g. 'f = lambda x: x + 1') instead of using standard 'def f(x):', which violates PEP 8 and harms traceback clarity."],
         "Mention PEP 8 guidance: always use 'def' when binding a function to a name; reserve lambdas for anonymous inline arguments.")
    ]

    for item in inter_data:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip = item
        qs.append(Question(
            qid=qid, title=title, difficulty="Intermediate", topic="Python Fundamentals",
            one_line=one_line, detailed=detailed, example_code=code, example_desc=desc,
            internal_working=internal, real_world=rw, follow_ups=follow_ups,
            mistakes=mistakes, tip=tip, related=["[fundamentals.md](fundamentals.md)"],
            references=["https://docs.python.org/3/reference/executionmodel.html"]
        ))

    return qs

def get_advanced_questions():
    qs = []
    
    adv_data = [
        ("PY-ADV-001", "Explain the CPython execution loop and how opcodes are dispatched in 'ceval.c'.",
         "CPython evaluates bytecode using a centralized evaluation loop (PyEval_EvalFrameDefault in ceval.c) that dispatches opcodes via computed gotos or large switch-case statements.",
         "When a Python function is executed, CPython creates a PyFrameObject representing its execution context (local variables, value stack, instruction pointer). The virtual machine iterates over the bytecode instructions. In modern CPython (3.11+), specialized and adaptive bytecode optimization replaces generic opcodes with specialized inline opcodes (PEP 659) based on observed runtime types, reducing interpreter overhead.",
         "import dis\n\ndef compute(x, y):\n    return x + y * 2\n\ndis.dis(compute)",
         "Disassembling bytecode to inspect evaluation instructions.",
         "ceval.c maintains an instruction pointer pointing into the bytecode buffer. On compilers supporting GCC extensions, CPython uses computed gotos (threaded code) where each opcode handler jumps directly to the memory address of the next instruction, avoiding CPU branch mispredictions inherent in giant switch statements.",
         "Understanding opcode dispatch is essential when writing C extensions, profiling CPU-bound microservices, or building custom JIT compilers for Python.",
         ["What is PEP 659 (Specializing Adaptive Interpreter)?", "Why is CPython considered a stack-based virtual machine rather than register-based?"],
         ["Assuming Python bytecode translates directly into machine code. Bytecode is interpreted in software by the C evaluation loop."],
         "Mention Python 3.11's Faster CPython project and specializing adaptive interpreter (PEP 659) to demonstrate up-to-date knowledge."),

        ("PY-ADV-002", "What is bytecode specialization and how does the PEP 659 Adaptive Interpreter work?",
         "Bytecode specialization dynamically rewrites generic bytecode instructions into type-specific fast opcodes at runtime based on observed operand types.",
         "Introduced in Python 3.11, the adaptive interpreter identifies 'hot' instructions in loops and functions. Generic opcodes like BINARY_OP are observed over several executions. If operands are consistently integers, the instruction is rewritten in-place to BINARY_OP_ADD_INT, which bypasses generic type dispatch and invokes fast integer addition directly. If type invariants are violated later, the instruction de-optimizes back to generic bytecode.",
         "def add_integers(n: int) -> int:\n    total = 0\n    for i in range(n):\n        total += i  # Specializes to integer addition\n    return total\n\nprint('Total:', add_integers(1000))",
         "Loop that benefits from bytecode specialization.",
         "CPython inserts inline caches (entries in the bytecode stream) right after adaptive opcodes. These cache entries store observed type pointers and struct offsets, allowing memory reads without secondary dictionary lookups.",
         "Explains why pure Python code runs 10-60% faster in Python 3.11+ without requiring external tools like Cython or PyPy.",
         ["How does de-optimization occur when an unexpected type is passed to a specialized opcode?", "What are inline caches in Python 3.11+?"],
         ["Assuming Python requires static type hints to optimize bytecode. PEP 659 specializes strictly based on runtime type observation, ignoring type hints."],
         "Highlight that type hints play NO role in PEP 659 specialization; the engine specializes purely on observed runtime types."),

        ("PY-ADV-003", "How does CPython's frame stack work and how does Python 3.11+ optimize frame allocation?",
         "Execution frames (PyFrameObject) track function state, and Python 3.11+ eliminates heap allocations for most frames by storing them in contiguous thread-stack memory.",
         "Historically, calling a Python function allocated a PyFrameObject on the heap, causing significant memory allocation overhead. Python 3.11 introduced contiguous frame stacks: frames are stored directly inside a pre-allocated stack buffer per thread. Heap PyFrameObject objects are created lazily only if explicitly requested by introspection tools (such as sys._getframe() or tracebacks).",
         "import sys\n\ndef inspect_depth():\n    frame = sys._getframe()\n    print(f'Current function: {frame.f_code.co_name}, Line: {frame.f_lineno}')\n\ninspect_depth()",
         "Introspecting stack frames using sys._getframe().",
         "Each interpreter thread maintains a PyThreadState containing a linked list of _PyInterpreterFrame structs allocated in contiguous chunks. This dramatically improves CPU L1/L2 data cache locality during deep recursion or frequent function calls.",
         "Crucial for high-throughput microservices handling hundreds of nested function calls per request (e.g. complex serialization in DRF or recursive GraphQL resolvers).",
         ["Why does calling sys._getframe() degrade runtime performance in Python 3.11+?", "What information is stored inside an execution frame?"],
         ["Using sys._getframe() or inspect module excessively in hot production code paths, which forces CPython to materialize heavy heap frames."],
         "Warn that calling sys._getframe() de-optimizes CPython's lazy frame evaluation and should be restricted to debuggers."),

        ("PY-ADV-004", "What are code objects (PyCodeObject) and what key attributes do they contain?",
         "A PyCodeObject is an immutable C struct representing compiled executable bytecode along with its associated constants, variable names, and execution metadata.",
         "When CPython compiles a function, module, or class, it produces a PyCodeObject. Unlike function objects, code objects hold no execution state, closures, or default argument values; they contain purely static compile-time artifacts: bytecode instructions (co_code), constants (co_consts), local variable names (co_varnames), free variables (co_freevars), and source line number mappings (co_linetable).",
         "def example_fn(a, b=10):\n    x = a + b\n    return x\n\ncode = example_fn.__code__\nprint('Bytecode:', code.co_code)\nprint('Constants:', code.co_consts)\nprint('Local variables:', code.co_varnames)\nprint('Argument count:', code.co_argcount)",
         "Inspecting internal metadata attributes of a function's code object.",
         "Defined in code.h as PyCodeObject. Because code objects are completely immutable, they can be shared safely across threads, processes, and function invocations without locks.",
         "Used in application profiling engines, dynamic code analyzers, security sandbox validators, and serialization tools (like cloudpickle).",
         ["What is the difference between a PyFunctionObject and a PyCodeObject?", "Why can multiple function objects share the same code object?"],
         ["Confusing functions with code objects. Functions are dynamic wrappers containing __globals__, __defaults__, and __closure__ around an immutable code object."],
         "Summarize: Code objects are the raw static blueprint; Function objects are the live runtime wrappers."),

        ("PY-ADV-005", "Explain the Global Interpreter Lock (GIL) and why it was introduced in CPython.",
         "The GIL is a mutual exclusion lock in CPython that prevents multiple native OS threads from executing Python bytecode simultaneously, preserving thread-safety in memory management.",
         "CPython's memory management relies heavily on reference counting (Py_INCREF and Py_DECREF). Without a global lock, multi-threaded operations on shared objects would cause race conditions and memory corruption unless every individual reference count mutation was guarded by fine-grained locks. Fine-grained locking would introduce massive CPU overhead on single-threaded programs and risk deadlocks. The GIL was chosen as a simple, high-performance solution for single-threaded workloads and easy C-extension integration.",
         "import threading\nimport time\n\ndef cpu_bound(n):\n    while n > 0:\n        n -= 1\n\n# Running two CPU-bound tasks in threads does not utilize 2 cores in CPython\nt1 = threading.Thread(target=cpu_bound, args=(10_000_000,))\nt2 = threading.Thread(target=cpu_bound, args=(10_000_000,))\nt1.start(); t2.start()\nt1.join(); t2.join()",
         "Illustrating that multi-threaded CPU-bound tasks contend on the GIL.",
         "In CPython, threads release the GIL during I/O operations (file, network, sleep) and when executing blocking C extensions. For CPU-bound tasks, CPython forces thread switching periodically based on a configurable interval (sys.getswitchinterval(), default 5ms).",
         "Explains why Python backend applications use process clustering (e.g. Gunicorn with multiple worker processes) rather than pure threading to saturate multi-core cloud servers.",
         ["Why does multi-threading improve I/O-bound tasks but degrade CPU-bound tasks in Python?", "What is PEP 703 (Free-threaded Python)?"],
         ["Claiming Python has no threads. Python uses real native OS threads (pthreads on Linux, WinThreads on Windows), but the GIL serializes bytecode execution across them."],
         "Distinguish clearly between I/O-bound tasks (threading is effective) and CPU-bound tasks (multiprocessing is required)."),

        ("PY-ADV-006", "What is PEP 703 and how does free-threaded (no-GIL) Python work in Python 3.13+?",
         "PEP 703 introduces an experimental build configuration in Python 3.13+ that removes the Global Interpreter Lock by adopting mimalloc, biased reference counting, and immortal objects.",
         "To enable true multi-core parallel execution on native threads without a GIL, PEP 703 replaces standard reference counting with: 1. Biased reference counting (fast, local single-thread increments with thread-safe atomic operations for foreign threads); 2. Immortal objects (constants like None, True, small integers whose reference counts are never modified); 3. Thread-safe memory allocation via mimalloc. This allows CPU-bound Python threads to execute concurrently across multiple CPU cores.",
         "# In Python 3.13t (free-threaded build):\n# import sys\n# print('GIL enabled?', sys._is_gil_enabled())",
         "Checking GIL status in free-threaded Python builds.",
         "Removing the GIL introduces approximately 5-10% performance regression in single-threaded code due to atomic operations, but yields linear multi-core scaling for multi-threaded workloads.",
         "Revolutionizes high-performance AI inference pipelines, real-time audio processing, and high-concurrency Python web servers by eliminating multi-process IPC serialization overhead.",
         ["What are immortal objects and how do they prevent cache invalidation across CPU cores?", "What is biased reference counting?"],
         ["Assuming all existing C-extensions work out-of-the-box with free-threaded Python. C extensions with non-thread-safe global state require updates."],
         "Mention Python 3.13t (the 't' signifies free-threaded build) to demonstrate knowledge of cutting-edge Python developments."),

        ("PY-ADV-007", "How does CPython's cyclic garbage collector detect and collect reference cycles?",
         "CPython uses a generational cyclic garbage collector that isolates container objects, tracks trial reference counts, and eliminates unreachable reference cycles.",
         "Reference counting handles 99% of deallocations immediately when count reaches zero, but cannot free objects that reference each other in a closed loop (e.g., a.b = b; b.a = a). The cyclic GC periodically inspects container objects (lists, dicts, custom class instances). It copies reference counts to a trial counter (gc_refs), decrements trial counts for all references originating from candidate objects, and any objects whose trial count drops to zero without external incoming references are isolated and deallocated.",
         "import gc\n\nclass Node:\n    def __init__(self):\n        self.cycle = self\n\nn = Node()\ndel n  # Reference count is still 1 due to self-reference\nprint('Unreachable objects collected:', gc.collect())",
         "Triggering manual cyclic garbage collection on a self-referencing cycle.",
         "The GC organizes objects into 3 generations (0, 1, 2) based on the weak generational hypothesis (most objects die young). Gen 0 is collected most frequently. Objects surviving collections are promoted to older generations.",
         "Crucial when tuning high-throughput Django or FastAPI services: understanding why cyclic GC pauses cause latency spikes, prompting Instagram/Meta to disable GC on pre-fork worker processes.",
         ["What is the weak generational hypothesis?", "Why did Instagram famously disable Python GC in their Django web workers?"],
         ["Believing cyclic GC manages all Python objects. Primitive immutable types (ints, strings, tuples of ints) are tracked solely by reference counting and never touched by cyclic GC."],
         "Explain that disabling or tuning gc.set_threshold() is a real-world production technique to eliminate latency jitter in pre-fork architectures."),

        ("PY-ADV-008", "What is the descriptor protocol and how does it underpin Python's object model?",
         "The descriptor protocol is an object protocol defined by __get__, __set__, and __delete__ methods that customizes attribute access, assignment, and deletion on classes.",
         "Descriptors provide the foundational mechanism for Python's core features, including properties, bound methods, classmethod, staticmethod, and ORM field mappings. A descriptor is a class attribute whose access behavior is intercepted when looked up on an instance.",
         "class ValidatedNumber:\n    def __init__(self, min_val: int):\n        self.min_val = min_val\n        self.name = None\n\n    def __set_name__(self, owner, name):\n        self.name = name\n\n    def __get__(self, instance, owner):\n        if instance is None:\n            return self\n        return instance.__dict__.get(self.name, self.min_val)\n\n    def __set__(self, instance, value):\n        if value < self.min_val:\n            raise ValueError(f'{self.name} must be >= {self.min_val}')\n        instance.__dict__[self.name] = value\n\nclass Product:\n    price = ValidatedNumber(0)\n\np = Product()\np.price = 100\nprint('Product price:', p.price)",
         "Creating a data descriptor with __set_name__ validation.",
         "When evaluating 'instance.attr', CPython checks: 1. Data descriptors on the class (defining both __get__ and __set__); 2. instance.__dict__; 3. Non-data descriptors on the class (defining only __get__, like methods); 4. class.__dict__.",
         "Foundational to Django Models (CharField, ForeignKey), SQLAlchemy ORM columns, and Pydantic field validators.",
         ["What is the difference between a data descriptor and a non-data descriptor?", "What is the purpose of the __set_name__ method (PEP 487)?"],
         ["Storing instance state directly on the descriptor instance itself (self.val = value), which causes all class instances to share the exact same state."],
         "Emphasize the lookup precedence: Data Descriptors > Instance Dict > Non-data Descriptors > Class Dict."),

        ("PY-ADV-009", "How does Python's Method Resolution Order (MRO) work and what is C3 Linearization?",
         "Python computes class inheritance hierarchies using the C3 Linearization algorithm to guarantee monotonicity and consistent local precedence order without ambiguity.",
         "In multiple inheritance architectures, resolving which method implementation to invoke requires a deterministic search order. Python 2.3+ replaced simple depth-first search with the C3 Linearization algorithm. C3 guarantees two critical properties: 1. Children precede parents; 2. The order of parents listed in the class definition is strictly preserved. If an inheritance structure violates these rules, Python rejects class definition with a TypeError.",
         "class A:\n    pass\n\nclass B(A):\n    pass\n\nclass C(A):\n    pass\n\nclass D(B, C):\n    pass\n\nprint('MRO for D:', [cls.__name__ for cls in D.__mro__])\n# ['D', 'B', 'C', 'A', 'object']",
         "Inspecting the computed C3 Linearization MRO.",
         "C3 merges the linearizations of parents and the list of parents themselves using a head/tail search algorithm. If a class appears in the tail of any list being merged, it cannot be selected as the next candidate, preventing inheritance graph contradictions.",
         "Essential when designing complex mixin hierarchies in Django views or pluggable backend architectures to avoid subtle diamond-inheritance bugs.",
         ["What causes a 'Cannot create a consistent method resolution order (MRO)' TypeError?", "How does super() navigate the MRO dynamically?"],
         ["Assuming super() always calls the direct parent class. super() calls the next sibling class in the computed MRO, not necessarily the parent."],
         "Demonstrate that super() is cooperative and follows the MRO dynamically, which is why all cooperative methods must have consistent signatures."),

        ("PY-ADV-010", "How does 'super()' work internally in Python 3?",
         "'super()' returns a proxy object that delegates method lookups to the next class in the caller instance's Method Resolution Order (MRO).",
         "In Python 3, zero-argument 'super()' automatically inspects the calling frame to determine the current class (__class__) and instance (self). Rather than binding directly to a parent class, 'super()' searches the instance's MRO starting immediately after the class where super() is called, enabling cooperative multiple inheritance.",
         "class Base:\n    def action(self):\n        print('Base action')\n\nclass MixinA(Base):\n    def action(self):\n        print('MixinA action')\n        super().action()\n\nclass MixinB(Base):\n    def action(self):\n        print('MixinB action')\n        super().action()\n\nclass Combined(MixinA, MixinB):\n    def action(self):\n        print('Combined action')\n        super().action()\n\nCombined().action()",
         "Cooperative multiple inheritance execution via super().",
         "In CPython, super() constructs a PySuperObject containing type pointers and instance pointers. When an attribute is accessed on the proxy, super_getattro traverses the instance's tp_mro starting at the index after the current class.",
         "Ubiquitous in Django Class-Based Views (CBVs) and middleware classes to chain functionality across multiple inheritance mixins.",
         ["Why is hardcoding the parent class name (e.g. Base.action(self)) considered an anti-pattern in multiple inheritance?", "What is zero-argument super() and how does it detect the current class?"],
         ["Failing to call super() in intermediate mixin classes, which breaks the cooperative execution chain for remaining classes in the MRO."],
         "Explain that cooperative multiple inheritance requires every method in the chain to call super(), ensuring all mixins execute."),

        ("PY-ADV-011", "What are Python metaclasses and what is the class creation lifecycle?",
         "A metaclass is the class of a class, responsible for intercepting, constructing, and configuring class objects during module compilation.",
         "Just as an ordinary class defines how instances behave, a metaclass defines how classes themselves are constructed. The default metaclass in Python is 'type'. When Python executes a 'class' block, it executes the body in a temporary namespace (__prepare__), passes the resulting attributes to the metaclass's __new__ (to construct the class object), and then invokes __init__ (to initialize the class).",
         "class MetaRegistry(type):\n    registry = {}\n    def __new__(mcs, name, bases, attrs):\n        cls = super().__new__(mcs, name, bases, attrs)\n        if name != 'BaseService':\n            mcs.registry[name] = cls\n        return cls\n\nclass BaseService(metaclass=MetaRegistry):\n    pass\n\nclass PaymentService(BaseService):\n    pass\n\nprint('Registered services:', MetaRegistry.registry)",
         "Auto-registering service classes via a custom metaclass.",
         "CPython evaluates the class header to determine the metaclass (inspecting metaclass=, bases, and global defaults). It calls mcs.__prepare__ to obtain a mapping, executes the class suite into that mapping, and then calls mcs(name, bases, namespace).",
         "Used in Django ORM model declarations, Pydantic v1 model schemas, and dependency injection containers to register plugins and map database fields dynamically.",
         ["How does '__init_subclass__' provide a simpler alternative to metaclasses in Python 3.6+?", "What is the purpose of '__prepare__' in metaclasses?"],
         ["Overusing metaclasses for simple tasks where class decorators or '__init_subclass__' are vastly simpler and more readable."],
         "Quote Tim Peters: 'Metaclasses are deeper magic than 99% of users should ever worry about.' Mention __init_subclass__ as the modern alternative."),

        ("PY-ADV-012", "What is '__init_subclass__' (PEP 487) and when should you prefer it over metaclasses?",
         "'__init_subclass__' is a class hook that automatically executes whenever a class is subclassed, providing class customization without the complexity of metaclasses.",
         "Introduced in Python 3.6, '__init_subclass__' allows base classes to intercept subclass creation, validate subclass attributes, register plugins, and inject behavior cleanly. It completely eliminates the need for full metaclasses in 90% of architectural use cases, while composing cleanly across multiple inheritance hierarchies without metaclass conflicts.",
         "class PluginBase:\n    plugins = {}\n    def __init_subclass__(cls, plugin_name: str, **kwargs):\n        super().__init_subclass__(**kwargs)\n        cls.plugins[plugin_name] = cls\n\nclass StripePlugin(PluginBase, plugin_name='stripe'):\n    pass\n\nprint('Discovered plugins:', PluginBase.plugins)",
         "Automatic plugin registration using __init_subclass__ with keyword arguments.",
         "When a subclass is defined, CPython's type_new invokes the __init_subclass__ hook found on the parent class, passing any extra keyword arguments provided in the class definition header.",
         "Extensively used in modern frameworks like FastAPI, SQLAlchemy 2.0, and Pydantic v2 to validate subclass contracts and register subcomponents.",
         ["How does __init_subclass__ resolve the classic 'metaclass conflict' problem?", "Can __init_subclass__ accept arbitrary keyword arguments?"],
         ["Forgetting to pass '**kwargs' and call 'super().__init_subclass__(**kwargs)', which breaks multiple inheritance chains."],
         "Always recommend '__init_subclass__' before suggesting a custom metaclass in modern Python architecture discussions."),

        ("PY-ADV-013", "How does CPython manage memory under the hood with 'pymalloc'?",
         "CPython manages small object memory allocations using 'pymalloc', a specialized allocator structured into Arenas (256 KB), Pools (4 KB), and Blocks.",
         "To prevent excessive system calls (malloc/free) and fragmentation from allocating millions of small objects (<= 512 bytes), CPython routes small allocations through 'pymalloc'. Pymalloc requests large 256 KB chunks from the OS called Arenas. Each Arena is divided into 4 KB Pools, and each Pool is subdivided into uniform fixed-size Blocks (8 to 512 bytes). Allocations larger than 512 bytes bypass pymalloc and use standard system malloc directly.",
         "import sys\n# Small objects use pymalloc\na = 42\nprint('Small int size:', sys.getsizeof(a))\n# Large allocations (> 512 bytes) bypass pymalloc to system malloc\nlarge_buf = bytearray(1024 * 1024)\nprint('Large buffer size:', sys.getsizeof(large_buf))",
         "Inspecting allocation sizes relative to the pymalloc threshold.",
         "Pymalloc pools are aligned in memory so that finding the pool header from any block address requires a single bitwise AND mask operation. When all blocks in a pool are freed, the pool is recycled within its arena; arenas are released back to the OS only when completely empty.",
         "Explains why long-running Python backend services often appear to retain high resident memory (RSS): freed memory inside partially occupied arenas cannot be returned to the OS.",
         ["Why does Python memory usage often remain high even after deleting millions of objects?", "What is memory fragmentation in pymalloc?"],
         ["Assuming 'del' immediately returns memory to the host operating system. Pymalloc retains pages in its arena pools for future Python allocations."],
         "Explain the Arena -> Pool -> Block hierarchy and mention why memory doesn't immediately shrink in OS activity monitors."),

        ("PY-ADV-014", "What are immortal objects (PEP 683) in Python 3.12+ and why do they matter?",
         "Immortal objects are runtime singletons whose reference counts are permanently fixed at a special constant value so they are never mutated by INCREF or DECREF.",
         "In standard CPython, even read-only operations on shared singletons (like None, True, False, small integers, and built-in type objects) cause cache-line invalidation across CPU cores because reference counting constantly writes to memory (INCREF/DECREF). PEP 683 treats specific core objects as immortal: their reference count has a special bit pattern that the INCREF/DECREF macros skip entirely, leaving memory pages strictly read-only.",
         "import sys\n# In Python 3.12+, core singletons have immortal reference counts\nprint('None ref count is effectively immortal:', sys.getrefcount(None) > 10**8)",
         "Detecting immortal reference counts on core singletons.",
         "CPython's Py_INCREF checks if the reference count is equal to the special immortal sentinel value _Py_IMMORTAL_REFCNT. If true, the memory write is bypassed, keeping CPU L1/L2 caches shared and clean across cores.",
         "Massive win for multi-process pre-fork web servers (like Gunicorn/uWSGI): shared memory pages across worker forks are no longer dirtied by reference count writes, maximizing Copy-on-Write (CoW) memory sharing and drastically reducing container RAM usage.",
         ["How do immortal objects optimize Copy-on-Write (CoW) behavior in multi-process architectures?", "How does PEP 683 pave the way for no-GIL Python?"],
         ["Believing immortal objects can ever be garbage collected. They persist for the entire life of the interpreter process."],
         "Connect immortal objects directly to Linux Copy-on-Write optimization in Gunicorn multi-worker deployments."),

        ("PY-ADV-015", "How does the 'asyncio' event loop schedule and execute tasks cooperatively?",
         "The asyncio event loop is a single-threaded cooperative multitasking scheduler that multiplexes I/O sockets using OS primitives (epoll/kqueue) and drives coroutines via their __await__ protocol.",
         "Asyncio uses non-blocking sockets and OS event demultiplexers (epoll on Linux, kqueue on macOS, I/O Completion Ports on Windows). When a coroutine executes 'await expr', it yields execution back to the event loop. The loop polls active socket file descriptors. When a socket signals readability or writability, the loop wakes the corresponding suspended coroutine task by calling its send() method.",
         "import asyncio\n\nasync def fetch_data(task_id: int):\n    await asyncio.sleep(0.01)  # Yields control to event loop\n    return f'Task {task_id} done'\n\nasync def main():\n    results = await asyncio.gather(*(fetch_data(i) for i in range(3)))\n    print(results)\n\nasyncio.run(main())",
         "Concurrent execution of coroutines via asyncio.gather.",
         "Under the hood, coroutines are state machines. When a Task is created, the event loop registers a callback in its internal ready queue (_ready deque). The event loop executes callbacks in _ready, then invokes selector.select(timeout) to sleep until network events fire.",
         "Forms the core engine of high-performance modern web frameworks like FastAPI, Starlette, Sanic, and aiohttp.",
         ["What happens if a developer places a synchronous blocking call (e.g. time.sleep() or requests.get()) inside an asyncio coroutine?", "How do you run blocking CPU-bound code safely in an asyncio application?"],
         ["Placing blocking synchronous I/O inside async functions, which freezes the entire event loop and starves all concurrent requests."],
         "Always emphasize: cooperative multitasking requires every task to yield control voluntarily; a single blocking call blocks the entire process."),

        ("PY-ADV-016", "What is the difference between an 'asyncio.Task' and a 'coroutine'?",
         "A coroutine is a suspended function object created by calling an 'async def' function, while a Task is an event-loop-managed wrapper that schedules the coroutine for immediate concurrent execution.",
         "Calling an 'async def' function returns a coroutine object that does not execute until it is awaited or scheduled. Wrapping a coroutine in an 'asyncio.Task' (via asyncio.create_task()) registers it with the active event loop, scheduling it to run concurrently in the background as soon as the loop is free.",
         "import asyncio\n\nasync def worker(name):\n    await asyncio.sleep(0.01)\n    return f'{name} finished'\n\nasync def main():\n    # Scheduling coroutines as concurrent tasks\n    task1 = asyncio.create_task(worker('Worker-1'))\n    task2 = asyncio.create_task(worker('Worker-2'))\n    res = await asyncio.gather(task1, task2)\n    print('Results:', res)\n\nasyncio.run(main())",
         "Scheduling coroutines concurrently using asyncio.create_task.",
         "asyncio.Task subclasses asyncio.Future. It wraps the coroutine, registers itself in the loop's ready queue via loop.call_soon(), and coordinates calling coroutine.send(None) and catching StopIteration when finished.",
         "Used in FastAPI background tasks, WebSockets consumers, and parallel microservice client calls.",
         ["Why does calling an 'async def' function not run any code until awaited?", "What happens if a created task raises an unhandled exception?"],
         ["Awaiting coroutines sequentially in a loop instead of wrapping them in tasks or asyncio.gather, losing all concurrency benefits."],
         "Explain that 'await coroutine' runs sequentially in the current task; 'asyncio.create_task(coroutine)' schedules it to run concurrently."),

        ("PY-ADV-017", "What are Context Variables (contextvars) and why are they needed in async Python?",
         "'contextvars' (PEP 567) provides thread-local-like storage that correctly propagates state across asynchronous coroutines and task boundaries.",
         "In synchronous multi-threaded applications, threading.local() isolates per-thread data (like database connections or request IDs). In async applications, thousands of concurrent requests interleave on the exact same thread, causing threading.local() to bleed data across requests. 'contextvars' maintains separate execution contexts per asyncio Task, ensuring isolation across concurrent coroutines.",
         "import asyncio\nimport contextvars\n\nrequest_id_var = contextvars.ContextVar('request_id', default='none')\n\nasync def handle_request(req_id: str):\n    request_id_var.set(req_id)\n    await asyncio.sleep(0.01)\n    # Value is safely isolated despite concurrent interleaving on the same thread\n    print(f'Processed: {request_id_var.get()}')\n\nasync def main():\n    await asyncio.gather(handle_request('REQ-001'), handle_request('REQ-002'))\n\nasyncio.run(main())",
         "Isolating request context across concurrent async tasks.",
         "Each Task has an internal PyContext pointer. When a new Task is spawned, it shallow-copies the current context. ContextVar modifications mutate only the current task's context dictionary without affecting parent or peer tasks.",
         "Used in FastAPI middlewares and logging frameworks to propagate correlation IDs, tracing spans, and authenticated user credentials across asynchronous call chains.",
         ["Why is threading.local() dangerous to use in async frameworks like FastAPI?", "How do contextvars interact with thread pools (loop.run_in_executor)?"],
         ["Using threading.local() in an async web service, causing user A's auth token or tenant ID to leak to user B."],
         "Emphasize: Use threading.local() for threads; use contextvars for async tasks and modern web frameworks."),

        ("PY-ADV-018", "What is structural pattern matching (PEP 634) in Python 3.10+ and how does it differ from a switch-case?",
         "Structural pattern matching ('match-case') is an expressive control-flow construct that matches values against patterns, destructures nested data structures, and binds variables simultaneously.",
         "Unlike traditional C-style switch-case statements that perform simple scalar equality checks, Python's match-case inspects the shape (structure), types, and contents of complex nested objects (sequences, dictionaries, dataclasses). It can unpack data into local variables, apply guard conditions ('if'), and enforce exhaustiveness checks.",
         "def handle_command(cmd):\n    match cmd:\n        case {'action': 'navigate', 'url': str(url)}:\n            return f'Navigating to {url}'\n        case {'action': 'retry', 'attempts': int(n)} if n > 0:\n            return f'Retrying {n} times'\n        case ['quit', *reason]:\n            return f'Quitting: {\" \".join(reason)}'\n        case _:\n            return 'Unknown command'\n\nprint(handle_command({'action': 'navigate', 'url': 'https://python.org'}))\nprint(handle_command(['quit', 'user', 'canceled']))",
         "Destructuring complex dictionaries and lists using match-case with guards.",
         "CPython compiles match statements into specialized testing and destructuring opcodes (MATCH_SEQUENCE, MATCH_MAPPING, MATCH_KEYS). Pattern extraction happens in optimized C code without allocating intermediate slicing objects.",
         "Ideal for parsing polymorphic API payloads, state machines, AST compiler transformations, and complex domain event handlers.",
         ["What is a wildcard pattern ('_') in a match-case block?", "How do guard conditions ('if') work in case statements?"],
         ["Assuming 'case 404:' is just an if-else chain. Match-case performs deep structural validation and variable binding."],
         "Highlight destructuring: match-case extracts and binds internal fields in a single step."),

        ("PY-ADV-019", "How does Python's import system work internally and what role do sys.modules, Finders, and Loaders play?",
         "Python imports modules via a two-phase protocol: Finder objects locate module specs, and Loader objects compile and execute module code, caching results in sys.modules.",
         "When executing 'import foo': 1. Python checks sys.modules (in-memory cache). If cached, it returns immediately; 2. If missing, sys.meta_path is searched sequentially for an import Finder (e.g. PathFinder for disk files); 3. The finder returns a ModuleSpec; 4. The loader creates a new module object, adds it to sys.modules, and executes the module's bytecode inside the new module namespace.",
         "import sys\nimport importlib.util\n\n# Dynamic programmatic import inspection\nspec = importlib.util.find_spec('math')\nprint('Module spec:', spec.name, 'Origin:', spec.origin)\nprint('Is math cached?', 'math' in sys.modules)",
         "Inspecting module specifications and sys.modules cache.",
         "The import system is implemented in importlib._bootstrap (written in frozen Python bytecode). Caching in sys.modules prevents re-execution of top-level module code and protects against infinite loops during circular imports.",
         "Used when building dynamic plugin architectures, auto-discovering API routes, or mocking modules in unit tests.",
         ["What happens during a circular import in Python and why does it cause an ImportError or AttributeError?", "How can you resolve circular imports?"],
         ["Assuming circular imports fail immediately on the import line. They fail when accessing uninitialized attributes in partially loaded modules."],
         "Explain the two remedies for circular imports: refactor shared logic into a separate module, or move imports inside functions (lazy imports)."),

        ("PY-ADV-014", "What are immortal objects (PEP 683) in Python 3.12+ and why do they matter?", # Duplicate QID guard
         "", "", "", "", "", "", [], [], "", [], [])
    ]

    # Replace duplicate entry with real PY-ADV-020 through PY-ADV-025
    adv_data_clean = [
        ("PY-ADV-020", "What are Abstract Base Classes (ABCs) and how does the 'abc' module enforce interfaces?",
         "Abstract Base Classes define interface blueprints that enforce required method implementations on subclasses at instantiation time using the @abstractmethod decorator.",
         "The 'abc' module uses the metaclass ABCMeta. If a class defines methods decorated with @abstractmethod and a subclass fails to provide concrete implementations for all of them, attempting to instantiate the subclass raises a TypeError at runtime. This prevents incomplete objects from ever existing in memory.",
         "from abc import ABC, abstractmethod\n\nclass Repository(ABC):\n    @abstractmethod\n    def get_by_id(self, entity_id: int):\n        pass\n\nclass PostgresRepository(Repository):\n    def get_by_id(self, entity_id: int):\n        return {'id': entity_id, 'data': 'record'}\n\nrepo = PostgresRepository()\nprint('Fetched:', repo.get_by_id(1))",
         "Defining and implementing an abstract repository interface.",
         "ABCMeta tracks abstract methods in an internal set __abstractmethods__. When type_call allocates a new instance, it checks if __abstractmethods__ is non-empty; if so, it aborts instantiation with a TypeError.",
         "Heavily used in enterprise Domain-Driven Design (DDD), Clean Architecture, and repository patterns to enforce dependency inversion.",
         ["Can an abstract method provide a default implementation that subclasses can call via super()?", "What happens if a class defines an abstract property?"],
         ["Attempting to catch missing interface methods at compile-time. In Python, ABCs enforce implementation check at instantiation time (when calling Class())."],
         "Note that abstract methods CAN have default implementations that subclasses call using super()."),

        ("PY-ADV-021", "Explain the generator delegation syntax ('yield from') and how it coordinates bidirectional communication.",
         "'yield from' transparently delegates generator iteration to a subgenerator, establishing a bidirectional channel that passes values, exceptions, and return values directly between caller and subgenerator.",
         "Introduced in PEP 380, 'yield from iterable' does far more than replace an inner loop. It forwards .send(val), .throw(exc), and .close() directly into the subgenerator. Crucially, when the subgenerator returns a value (via 'return val'), 'yield from' captures that returned value as the expression's result.",
         "def subgenerator():\n    yield 'Part 1'\n    yield 'Part 2'\n    return 'Subgenerator Complete'\n\ndef delegating_generator():\n    result = yield from subgenerator()\n    yield f'Result was: {result}'\n\nprint(list(delegating_generator()))",
         "Capturing subgenerator return value via yield from.",
         "The CPython VM executes YIELD_FROM bytecode, which intercepts callers' send() and throw() methods and forwards them directly to the active frame of the subgenerator until a StopIteration exception carries the return value.",
         "Paved the historical way for modern asyncio coroutines before the formal introduction of 'async def' and 'await'.",
         ["How does 'yield from' handle exceptions thrown into the delegator?", "What does StopIteration.value represent?"],
         ["Writing 'for x in subgen(): yield x', which fails to forward .send() or capture the subgenerator's return value."],
         "Explain that 'yield from' was the conceptual and technical precursor to 'await' in Python."),

        ("PY-ADV-022", "How do weak references ('weakref' module) work in Python and when should they be used?",
         "Weak references allow referencing an object without increasing its reference count (ob_refcnt), preventing reference cycles and allowing the target to be garbage collected.",
         "When caching objects or implementing observer patterns, storing strong references prevents referenced objects from ever being deallocated as long as the cache exists. Using weakref.ref(obj) or weakref.WeakValueDictionary allows objects to be reclaimed by memory managers as soon as all external strong references are gone.",
         "import weakref\n\nclass CacheNode:\n    def __init__(self, name):\n        self.name = name\n\nnode = CacheNode('SessionData')\nref = weakref.ref(node)\nprint('Referenced name:', ref().name)\ndel node  # Strong reference destroyed\nprint('After strong deletion:', ref())  # None",
         "Creating a weak reference that resolves to None after the target is destroyed.",
         "Objects supporting weak references contain a pointer (tp_weaklistoffset) to a linked list of weakref objects. When the target's ob_refcnt drops to 0, tp_dealloc clears all associated weak references, notifying callbacks before freeing memory.",
         "Used in in-memory LRU caches, UI widget tree parent-pointers, and event publisher-subscriber systems to prevent massive memory leaks.",
         ["Can all Python objects be weakly referenced? Why can't primitive types like int or tuple have weak references by default?", "What is a WeakValueDictionary?"],
         ["Attempting to create weak references to built-in lists or dicts directly without subclassing."],
         "Recommend WeakValueDictionary for caches: cache items automatically disappear the moment no other part of the app is using them."),

        ("PY-ADV-023", "What is the buffer protocol and how does 'memoryview' provide zero-copy memory access?",
         "The buffer protocol allows Python objects to expose raw internal byte buffers directly, and 'memoryview' wraps those buffers to enable slicing and indexing without copying data.",
         "In high-performance networking and file I/O, copying byte arrays repeatedly causes significant memory and CPU bloat. The C-level buffer protocol (Py_buffer) allows memory-sharing across objects. A 'memoryview' slices underlying memory in-place by updating pointer offsets and strides, achieving true zero-copy data manipulation.",
         "data = bytearray(b'ABCDEFGH')\nview = memoryview(data)\n# Slice without copying raw bytes\nsub_view = view[2:5]\nsub_view[0] = ord('Z')  # Mutates underlying bytearray in-place\nprint('Modified data:', data)  # bytearray(b'ABZDEFGH')",
         "In-place zero-copy byte modification using memoryview.",
         "A memoryview object holds a Py_buffer struct pointing directly to the contiguous memory address of the source object. Slicing increments the internal buffer pointer and adjusts length without invoking memcpy.",
         "Heavily used in high-speed socket programming (asyncio streams), binary data processing (struct, protobuf), and image manipulation.",
         ["Why is socket.send(memoryview(buf)[sent:]) faster than slicing a bytes object directly?", "What is the difference between bytes and bytearray in relation to memoryview?"],
         ["Slicing raw 'bytes' objects repeatedly in network loops, which allocates a new bytes object and performs memcpy on every iteration."],
         "Use memoryview in network streaming questions to demonstrate zero-copy data efficiency."),

        ("PY-ADV-024", "What are type variables (TypeVar) and Generics in Python typing (PEP 484 & PEP 695)?",
         "TypeVar and Generics allow functions, classes, and containers to express parameterized types while enforcing type consistency across inputs and outputs.",
         "Generics enable reusable code that retains strict static type safety. A TypeVar acts as a placeholder for an unknown type that is resolved when the function or class is used. In Python 3.12+ (PEP 695), clean syntax (`def func[T](x: T) -> T:`) eliminates verbose TypeVar declarations.",
         "# Python 3.12+ concise generic syntax (or TypeVar in 3.10)\nfrom typing import TypeVar, List\n\nT = TypeVar('T')\n\ndef get_first(items: List[T]) -> T:\n    return items[0]\n\nval: int = get_first([10, 20, 30])\nprint('First item:', val)",
         "Parameterizing a generic function using TypeVar.",
         "Typing constructs exist purely for static analyzers (Mypy) and IDEs. At runtime, Generic classes implement __class_getitem__ to return a types.GenericAlias object without altering instance allocation.",
         "Crucial in enterprise backend architectures for generic Repository patterns (Repository[User]), API response wrappers (APIResponse[T]), and custom data structures.",
         ["What is the difference between invariant, covariant, and contravariant TypeVars?", "How does Python 3.12's PEP 695 simplify generic syntax?"],
         ["Assuming Generics enforce runtime validation in standard CPython. Generics are purely static unless combined with runtime validators like Pydantic."],
         "Mention covariance (Generic[+T]) and contravariance (Generic[-T]) when discussing advanced library typing."),

        ("PY-ADV-025", "How do you detect, profile, and eliminate memory leaks in production Python services?",
         "Memory leaks in Python are diagnosed by analyzing object reference graphs using 'tracemalloc', 'objgraph', and 'gc' to identify accumulated cycles or dangling references.",
         "While Python has automated GC, memory leaks occur when objects remain referenced by long-lived global collections, circular references with custom finalizers, unclosed connections, or C-extension leaks. To triage: 1. Take snapshots with 'tracemalloc' to locate the exact source lines allocating unreleased memory; 2. Use 'objgraph' to inspect growing object counts; 3. Pinpoint lingering roots with gc.get_referrers().",
         "import tracemalloc\n\ntracemalloc.start()\n# Simulated leaky cache\ncache = []\nfor i in range(1000):\n    cache.append({'id': i, 'payload': 'data' * 10})\n\nsnapshot = tracemalloc.take_snapshot()\ntop_stats = snapshot.statistics('lineno')\nfor stat in top_stats[:3]:\n    print(stat)",
         "Profiling memory allocations line-by-line using tracemalloc.",
         "tracemalloc hooks into CPython's internal memory allocators (PyMem_Malloc) to record memory address, allocation size, and full Python traceback at the time of allocation.",
         "Standard procedure when investigating production pods crashing with OOM (Out of Memory) kills in Kubernetes.",
         ["What are the top 3 causes of memory leaks in Python backend services?", "Why is 'tracemalloc' preferred over external OS memory profilers?"],
         ["Assuming that deleting a variable with 'del' fixes memory leaks when hidden references still exist in global event listeners or caches."],
         "Provide the 3-step investigation process: tracemalloc snapshot -> objgraph object type growth -> gc.get_referrers root identification.")
    ]

    for item in adv_data[:19] + adv_data_clean:
        qid, title, one_line, detailed, code, desc, internal, rw, follow_ups, mistakes, tip = item
        qs.append(Question(
            qid=qid, title=title, difficulty="Advanced", topic="Python Fundamentals",
            one_line=one_line, detailed=detailed, example_code=code, example_desc=desc,
            internal_working=internal, real_world=rw, follow_ups=follow_ups,
            mistakes=mistakes, tip=tip, related=["[fundamentals.md](fundamentals.md)"],
            references=["https://docs.python.org/3/c-api/index.html"]
        ))

    return qs

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_file = os.path.join(repo_root, "01-python", "fundamentals.md")
    
    basic_qs = get_basic_questions()
    inter_qs = get_intermediate_questions()
    adv_qs = get_advanced_questions()
    
    print(f"Generating fundamentals.md: {len(basic_qs)} Basic, {len(inter_qs)} Intermediate, {len(adv_qs)} Advanced (Total: {len(basic_qs)+len(inter_qs)+len(adv_qs)})")
    
    content = render_file(
        title="Python Fundamentals Interview Questions",
        description="Comprehensive technical interview questions covering core Python syntax, execution lifecycle, variable semantics, scopes, error handling, and CPython runtime architecture.",
        basic_qs=basic_qs,
        inter_qs=inter_qs,
        adv_qs=adv_qs
    )
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {out_file}")

if __name__ == "__main__":
    main()
