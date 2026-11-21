"""
adv_py_basic.py
===============
Basic Advanced Python Questions: PY-BAS-176 to PY-BAS-200 (25 questions)
"""

basic_data = [
    # PY-BAS-176
    (
        "PY-BAS-176",
        "Dynamic Typing and Duck Typing in Python",
        "Dynamic typing means variable types are bound at runtime rather than compile time; duck typing means an object's suitability is determined by the presence of specific methods and attributes rather than its explicit inheritance hierarchy.",
        "In Python, variables are untyped references to typed heap objects. The type of a variable can change dynamically upon reassignment. Duck typing encapsulates the philosophy: 'If it walks like a duck and quacks like a duck, it's a duck.' Rather than checking `isinstance(obj, ExpectedClass)`, Python code simply invokes the required method or attribute (e.g. `obj.read()`). If the object implements the expected interface, execution succeeds regardless of whether the object inherits from a specific base class.",
        "class FileLogger:\n    def write(self, msg: str):\n        print(f'File write: {msg}')\n\nclass SocketLogger:\n    def write(self, msg: str):\n        print(f'Socket write: {msg}')\n\ndef record_event(target, message: str):\n    # Duck typing: Accepts any object with a .write() method\n    target.write(message)\n\nrecord_event(FileLogger(), 'System startup')\nrecord_event(SocketLogger(), 'Packet received')",
        "Demonstrating duck typing where distinct classes satisfy an interface without common inheritance.",
        "CPython resolves attribute lookups dynamically via `tp_getattro` at runtime. If the requested method exists, it is called; if not, an `AttributeError` is raised.",
        "Designing modular software components where mock objects, file-like streams (e.g. `io.StringIO`), and production objects can be substituted interchangeably.",
        ["What is the difference between dynamic typing and duck typing?", "How does Python handle an object that fails to satisfy a duck-typed method call?"],
        ["Overusing `isinstance()` checks everywhere, defeating the flexibility of duck typing.", "Failing to document expected object interfaces when relying on duck typing."],
        "Emphasize: Duck typing prioritizes behavior over nominal inheritance hierarchy.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/glossary.html#term-duck-typing"]
    ),

    # PY-BAS-177
    (
        "PY-BAS-177",
        "Abstract Base Classes (ABCs)",
        "Abstract Base Classes (`abc.ABC`) define formal interfaces and blueprint contracts that derived classes must fulfill, preventing instantiation of incomplete implementations.",
        "While duck typing allows informal contracts, enterprise architectures often require formal interface enforcement. Python provides the `abc` module. By inheriting from `abc.ABC` and decorating required methods with `@abc.abstractmethod`, a class establishes an abstract contract. If a subclass fails to implement even one abstract method, CPython raises a `TypeError` at instantiation time, catching incomplete implementations early during application initialization.",
        "from abc import ABC, abstractmethod\n\nclass PaymentGateway(ABC):\n    @abstractmethod\n    def process_payment(self, amount: float) -> bool:\n        pass\n\nclass StripeGateway(PaymentGateway):\n    def process_payment(self, amount: float) -> bool:\n        print(f'Processing ${amount} via Stripe')\n        return True\n\ngateway = StripeGateway()\ngateway.process_payment(100.0)",
        "Defining an Abstract Base Class and implementing a concrete subclass.",
        "`abc.ABC` uses `abc.ABCMeta` as its metaclass. During instantiation (`type.__call__`), CPython checks if `__abstractmethods__` is non-empty. If any abstract method names remain, instantiation is aborted with `TypeError`.",
        "Defining pluggable provider architectures (payment gateways, cloud storage drivers, database adapters) where concrete implementations must satisfy strict API contracts.",
        ["Can an abstract class define concrete methods with default implementations?", "When does CPython verify that abstract methods are implemented?"],
        ["Instantiating an abstract class directly (raises `TypeError`).", "Assuming abstract method checks happen during class definition (they happen during instance creation)."],
        "Tip: Abstract classes can provide concrete default implementations that subclasses can call via `super()`.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/abc.html"]
    ),

    # PY-BAS-178
    (
        "PY-BAS-178",
        "@abstractmethod and Instantiation Enforcement",
        "`@abstractmethod` marks a method as mandatory for subclasses; attempting to instantiate a subclass that omits any `@abstractmethod` raises an immediate `TypeError`.",
        "The `@abstractmethod` decorator attaches a boolean attribute `__isabstractmethod__ = True` to the function. When a class is constructed, `ABCMeta` scans the class dictionary and MRO, compiling a set of all methods where this attribute is true into `cls.__abstractmethods__`. When `Subclass()` is called, CPython inspects this set; if non-empty, instantiation halts with `TypeError: Can't instantiate abstract class with abstract methods`.",
        "from abc import ABC, abstractmethod\n\nclass Repository(ABC):\n    @abstractmethod\n    def get_by_id(self, item_id: int):\n        pass\n\nclass IncompleteRepo(Repository):\n    pass  # Fails to implement get_by_id\n\ntry:\n    r = IncompleteRepo()  # Raises TypeError\nexcept TypeError as e:\n    print(f'Instantiation blocked as expected: {e}')",
        "Demonstrating TypeError when attempting to instantiate an incomplete abstract subclass.",
        "`ABCMeta.__new__` computes `abstracts = {name for name, value in ... if getattr(value, '__isabstractmethod__', False)}`. It updates `__abstractmethods__` as a frozen set on the class.",
        "Enforcing strict data access repository patterns across engineering teams to prevent runtime `NotImplementedError` crashes in production.",
        ["Can `@abstractmethod` be combined with `@classmethod` or `@staticmethod`?", "What happens if a subclass implements an abstract method with a different signature?"],
        ["Placing `@abstractmethod` outside `@property` (correct order is `@property` outside, `@abstractmethod` inside).", "Using `raise NotImplementedError` instead of `@abstractmethod` for interface enforcement."],
        "Remember decorator ordering: `@property` goes on top, `@abstractmethod` goes on bottom.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/abc.html#abc.abstractmethod"]
    ),

    # PY-BAS-179
    (
        "PY-BAS-179",
        "Virtual Subclasses via ABC.register()",
        "`ABC.register(cls)` registers an existing class as a 'virtual subclass' of an ABC, satisfying `isinstance()` and `issubclass()` checks without modifying the registered class's inheritance hierarchy.",
        "Sometimes a third-party class already implements all required methods of an interface, but cannot be modified to inherit directly from your ABC. `ABC.register(ThirdPartyClass)` marks the target class as a virtual subclass. While the registered class does not inherit any concrete methods or appear in the ABC's MRO, `isinstance(obj, ABC)` and `issubclass(ThirdPartyClass, ABC)` evaluate to `True`, enabling seamless polymorphism across decoupled libraries.",
        "from abc import ABC, abstractmethod\n\nclass Serializable(ABC):\n    @abstractmethod\n    def serialize(self) -> str:\n        pass\n\nclass LegacyPayload:\n    def serialize(self) -> str:\n        return 'serialized_legacy_data'\n\n# Register LegacyPayload as virtual subclass of Serializable\nSerializable.register(LegacyPayload)\n\nobj = LegacyPayload()\nprint('isinstance check:', isinstance(obj, Serializable))  # True\nprint('issubclass check:', issubclass(LegacyPayload, Serializable))  # True\nprint('MRO excludes ABC:', LegacyPayload.__mro__)",
        "Registering a virtual subclass with ABC.register() and verifying isinstance support.",
        "`ABCMeta.register()` adds the class weak reference to `_abc_registry`. When `isinstance()` executes, CPython's `PyObject_IsInstance` queries `__subclasscheck__` which checks this registry.",
        "Integrating third-party libraries (e.g. NumPy arrays or Django models) into internal interface validation systems without subclassing or wrapping them.",
        ["Does a virtual subclass inherit default method implementations from the ABC?", "Why isn't the ABC present in the virtual subclass's `__mro__`?"],
        ["Expecting `super()` to resolve methods in the ABC from a virtual subclass (virtual subclasses share no MRO with the ABC).", "Assuming `register()` enforces that the registered class actually implements the abstract methods (it does not enforce at registration time)."],
        "Crucial nuance: Virtual subclasses satisfy `isinstance()` but inherit zero code from the ABC.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/abc.html#abc.ABCMeta.register"]
    ),

    # PY-BAS-180
    (
        "PY-BAS-180",
        "Structural Subtyping with typing.Protocol",
        "`typing.Protocol` (PEP 544) defines static and runtime structural interfaces (duck typing for type checkers), where any class that implements the required attributes is considered a valid subtype without explicit inheritance.",
        "Traditional ABCs rely on nominal subtyping: a class must explicitly inherit from the ABC or be registered. `typing.Protocol` introduces structural subtyping (static duck typing). If a class defines matching methods and type signatures, static type checkers (Mypy, Pyright) treat it as a valid subtype automatically. When decorated with `@typing.runtime_checkable`, protocols also support runtime `isinstance()` and `issubclass()` checks.",
        "from typing import Protocol, runtime_checkable\n\n@runtime_checkable\nclass Closable(Protocol):\n    def close(self) -> None:\n        ...\n\nclass CustomConnection:\n    def close(self) -> None:\n        print('Connection closed')\n\nconn = CustomConnection()\n# Satisfies protocol without inheriting from Closable\nprint('Runtime checkable protocol:', isinstance(conn, Closable))",
        "Defining a runtime checkable Protocol and verifying an implicit structural implementation.",
        "When `@runtime_checkable` is applied, `Protocol` overrides `__subclasscheck__` to inspect whether all non-dunder attributes and callables declared on the protocol exist on the candidate class.",
        "Defining lightweight interface boundaries between microservice layers and external SDKs where forcing nominal inheritance creates unwanted coupling.",
        ["What is the difference between nominal subtyping and structural subtyping?", "What are the limitations of `@runtime_checkable` (does it check argument types at runtime)?"],
        ["Assuming `@runtime_checkable` verifies method argument signatures and return types at runtime (it only verifies attribute existence).", "Using nominal ABCs when structural protocols provide looser coupling."],
        "Warning: `@runtime_checkable` only checks method existence at runtime, not type signature compliance.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0544/"]
    ),

    # PY-BAS-181
    (
        "PY-BAS-181",
        "Nominal vs Structural Subtyping",
        "Nominal subtyping (ABCs) requires explicit class declaration (`class Dog(Animal)`), whereas structural subtyping (`Protocol`) establishes compatibility based purely on matching method and attribute shapes.",
        "In nominal subtyping (standard inheritance, ABCs), relationship is declared by name. Even if `ClassA` and `ClassB` have identical methods, `ClassA` is not an instance of `ClassB` unless explicitly declared in its inheritance tree. In structural subtyping (`typing.Protocol`, Go interfaces, TypeScript interfaces), compatibility is determined by structure: if `ClassA` has the same methods and properties required by `ProtocolB`, it is automatically compatible everywhere `ProtocolB` is expected.",
        "from typing import Protocol\nfrom abc import ABC, abstractmethod\n\n# Nominal: Must inherit explicitly\nclass NominalReader(ABC):\n    @abstractmethod\n    def read(self) -> str: pass\n\n# Structural: Any class with .read() -> str satisfies this\nclass StructuralReader(Protocol):\n    def read(self) -> str: ...\n\nclass SimpleStream:\n    def read(self) -> str: return 'data'\n\n# SimpleStream satisfies StructuralReader statically, but NOT NominalReader\nprint('Structural subtyping provides compile-time duck typing.')",
        "Contrasting nominal inheritance requirements against structural protocol conformance.",
        "Nominal subtyping checks `tp_mro` in C. Structural subtyping is evaluated statically by type checkers using attribute map intersection, and at runtime via attribute introspection in `_ProtocolMeta`.",
        "Architecting clean public SDK APIs: exposing protocols rather than ABCs allows library consumers to pass their own classes without inheriting from your SDK base classes.",
        ["Why is structural subtyping often preferred for library API design?", "How does TypeScript's type system compare to Python's Protocol?"],
        ["Forcing users of an open-source library to subclass rigid nominal ABCs.", "Assuming structural subtyping degrades runtime execution speed (it is primarily static type checking)."],
        "Design principle: Use ABCs when sharing concrete implementation code; use Protocols when defining pure interfaces.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0544/"]
    ),

    # PY-BAS-182
    (
        "PY-BAS-182",
        "TypeVar and Generic Programming",
        "`typing.TypeVar` defines generic type variables that preserve type identity across function arguments, return values, and generic classes.",
        "Without generics, a function that returns the same type it receives must be typed as `def identity(x: Any) -> Any`, losing all static type safety. `T = TypeVar('T')` creates a parameterized placeholder. When annotated as `def identity(x: T) -> T:`, static type checkers bind `T` to the exact type of the argument passed, ensuring that passing an `int` guarantees an `int` return type. Generic classes inherit from `typing.Generic[T]` to manage typed collections or wrappers.",
        "from typing import TypeVar, Generic\n\nT = TypeVar('T')\n\nclass Box(Generic[T]):\n    def __init__(self, item: T):\n        self._item = item\n    \n    def get(self) -> T:\n        return self._item\n\nint_box = Box[int](42)\nstr_box = Box[str]('Python Generics')\n\nprint('Int box holds:', int_box.get())\nprint('Str box holds:', str_box.get())",
        "Defining a generic container class using TypeVar and Generic.",
        "`Generic[T]` overrides `__class_getitem__` on `_GenericAlias`. Instantiating `Box[int]` creates a parameterized generic alias that retains runtime type metadata in `__args__` without altering the underlying class struct.",
        "Building reusable data structures (repositories, cache managers, API response wrappers) with end-to-end static type safety in FastAPI and Pydantic.",
        ["What is the difference between an unbounded TypeVar and a constrained TypeVar?", "What is `TypeVar('T', bound=BaseClass)`?"],
        ["Using `TypeVar` as an actual runtime type check inside `isinstance(x, T)` (raises `TypeError`).", "Re-using the same `TypeVar` across unrelated functions expecting different constraints."],
        "Remember: `TypeVar` is a static type hinting construct; it does not exist as a concrete class at runtime.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/typing.html#typing.TypeVar"]
    ),

    # PY-BAS-183
    (
        "PY-BAS-183",
        "Union Types and the Pipe Operator (PEP 604)",
        "`typing.Union[A, B]` indicates a value can be of type `A` or `B`; Python 3.10 introduced the cleaner `|` pipe syntax (`A | B`) for union type expressions.",
        "Prior to Python 3.10, expressing that a function accepts either an integer or a string required importing `Union` and writing `def parse(val: Union[int, str])`. PEP 604 introduced the union operator `|` directly on types: `def parse(val: int | str)`. This syntax is more concise, improves readability, and avoids unnecessary imports from `typing`. It can also be used directly in `isinstance(val, int | str)` starting in Python 3.10.",
        "def process_id(identifier: int | str) -> str:\n    return f'ID: {identifier}'\n\nprint(process_id(101))\nprint(process_id('USR-554'))\n\n# Pipe operator also works in isinstance() in Python 3.10+\nprint('Is valid identifier type?', isinstance(101, int | str))",
        "Demonstrating PEP 604 union type annotations and runtime isinstance checks with the pipe operator.",
        "The `|` operator invokes `types.UnionType.__or__`. It constructs a `types.UnionType` object storing the operand types in its `__args__` tuple.",
        "Annotating database primary keys, configuration values, or API request payloads that accept polymorphic input types.",
        ["How does `int | str` compare to `Union[int, str]` in performance?", "Can `|` be used for runtime `isinstance` checks in Python 3.9?"],
        ["Using `|` in Python 3.9 or earlier without `from __future__ import annotations` (causes runtime `TypeError`).", "Creating deeply nested unions that obscure clean function contracts."],
        "Tip: Use `from __future__ import annotations` to use `A | B` syntax in Python 3.7+ codebases.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0604/"]
    ),

    # PY-BAS-184
    (
        "PY-BAS-184",
        "Optional[T] and T | None",
        "`typing.Optional[T]` represents a value that can be of type `T` or `None`, which is functionally identical to `Union[T, None]` and modern `T | None` syntax.",
        "A frequent misconception is that `Optional[T]` means an argument has a default value or is optional to pass. In Python type theory, `Optional[T]` means the value can either be of type `T` or explicitly `None` (nullable). In modern Python 3.10+, writing `str | None` is preferred over `Optional[str]` for clarity and consistency.",
        "def find_user(email: str) -> str | None:\n    if email == 'admin@example.com':\n        return 'Administrator'\n    return None\n\nprint('Found user:', find_user('admin@example.com'))\nprint('Missing user:', find_user('unknown@example.com'))",
        "Annotating a nullable return type using the modern str | None syntax.",
        "`Optional[T]` is an alias for `Union[T, type(None)]`. The type checker enforces null-checking before accessing attributes on optional return values.",
        "Annotating database queries that might not find a matching record, optional configuration settings, or nullable JSON fields in API models.",
        ["Does `Optional[int]` imply the function argument defaults to `None`?", "How do static type checkers enforce null safety on `T | None`?"],
        ["Assuming `def func(x: Optional[int])` allows calling `func()` with no arguments (default value `= None` is still required).", "Forgetting to perform `if val is not None:` checks before accessing attributes on optional values."],
        "Emphasize: `Optional[T]` means *nullable*, not *optional to supply as an argument*.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/typing.html#typing.Optional"]
    ),

    # PY-BAS-185
    (
        "PY-BAS-185",
        "typing.Literal for Restricted Values",
        "`typing.Literal` restricts a type annotation to exact, specific scalar values (e.g. strings, integers, booleans), enabling static validation of fixed parameter choices.",
        "When a function accepts a parameter that must match a predefined set of choices (e.g. HTTP methods or file modes), annotating with `str` is too permissive. `Literal['GET', 'POST', 'PUT']` instructs static type checkers to flag any argument that does not match one of those exact string literals. This provides enum-like compile-time safety without requiring callers to instantiate formal `Enum` classes.",
        "from typing import Literal\n\ndef open_channel(mode: Literal['r', 'w', 'a']) -> str:\n    return f'Channel opened in mode: {mode}'\n\nprint(open_channel('r'))\n# open_channel('x')  # Static type checkers flag this as an invalid argument!",
        "Restricting function parameters to exact literal string choices using typing.Literal.",
        "`Literal` constructs a `_LiteralGenericAlias` holding allowed values in `__args__`. At runtime, Python does not automatically raise exceptions on mismatches; static type checkers enforce it during type checking.",
        "Validating configuration flags, API request parameters, or database transaction isolation levels in framework interfaces.",
        ["How does `typing.Literal` compare to `enum.Enum`?", "Can you use integers or booleans inside `Literal`?"],
        ["Expecting `Literal` to raise runtime validation errors automatically (requires Pydantic or manual runtime checks).", "Using `Literal` for unbounded or dynamically generated string sets."],
        "Interview distinction: `Literal` provides lightweight compile-time choice restrictions without runtime Enum object overhead.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0586/"]
    ),

    # PY-BAS-186
    (
        "PY-BAS-186",
        "typing.TypedDict for Schema Validation",
        "`typing.TypedDict` enables type annotations for standard Python dictionaries, declaring expected string keys and their corresponding value types for static type checkers.",
        "Standard dictionaries are typed as `dict[str, Any]`, losing specific key-value type validation. `TypedDict` defines a dictionary schema where each key has an exact type. At runtime, an instance of `TypedDict` remains a regular, lightweight Python `dict` with zero performance overhead. Static type checkers verify that required keys exist and prevent misspelled key accesses.",
        "from typing import TypedDict\n\nclass UserProfile(TypedDict):\n    username: str\n    age: int\n    is_active: bool\n\n# Standard Python dictionary adhering to TypedDict schema\nuser: UserProfile = {\n    'username': 'antigravity',\n    'age': 30,\n    'is_active': True\n}\n\nprint('User profile dictionary:', user)\nprint('Is standard dict at runtime?', isinstance(user, dict))",
        "Declaring and instantiating a TypedDict schema.",
        "At runtime, `TypedDict` is a regular dict subclass whose `__init__` delegates to `dict`. It populates `__annotations__`, `__required_keys__`, and `__optional_keys__` for static analysis.",
        "Typing raw JSON payloads, API response dictionaries, and Redis hash representations without introducing heavyweight ORM models.",
        ["What is the difference between `total=True` and `total=False` in `TypedDict`?", "Does `TypedDict` perform runtime data validation like Pydantic?"],
        ["Assuming `TypedDict` validates data types at runtime (it does not perform runtime casting or validation).", "Using `TypedDict` when class instances with methods are needed."],
        "Clarify: `TypedDict` is purely for static type checking; for runtime schema validation, use Pydantic.",
        ["[Data Types & Collections](data-types-and-collections.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0589/"]
    ),

    # PY-BAS-187
    (
        "PY-BAS-187",
        "typing.Any vs object",
        "`Any` disables static type checking completely, allowing arbitrary operations, whereas `object` is the root of all Python classes and allows only operations common to every object.",
        "While both `Any` and `object` accept any value, their type semantics are polar opposites: 1) `Any`: An escape hatch from the type system. A variable typed as `Any` allows arbitrary attribute accesses, method calls, and assignments without type checker warnings. 2) `object`: The top type in Python's class hierarchy. A variable typed as `object` signals: 'This can be anything, but you cannot call methods or access attributes on it without first verifying its type via `isinstance()`.'",
        "from typing import Any\n\ndef process_any(val: Any):\n    # Type checker permits anything on Any (no static safety)\n    val.arbitrary_method_call()\n\ndef process_object(val: object):\n    # val.arbitrary_method_call()  # Static type checker BLOCKS this!\n    # Must narrow type first:\n    if isinstance(val, str):\n        print('Length of string:', len(val))\n\nprint('Any opts out of type checking; object enforces explicit type narrowing.')",
        "Contrasting permissive typing of Any with safe type narrowing required for object.",
        "`Any` is treated as both a top-type and bottom-type in gradual typing theory. `object` is strictly the nominal top-type.",
        "Using `object` when writing generic deserializers or decorators that forward values without inspecting them, preserving type safety.",
        ["Why is `object` preferred over `Any` for defensive library APIs?", "What does gradual typing mean in Python?"],
        ["Sprinkling `Any` everywhere to silence type errors instead of defining proper types.", "Assuming `object` behaves like `Any` in static type analysis."],
        "Rule of thumb: Avoid `Any` in production code; prefer `object` combined with `isinstance()` type narrowing.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/typing.html#the-any-type"]
    ),

    # PY-BAS-188
    (
        "PY-BAS-188",
        "NoReturn vs Never in Type Annotations",
        "`NoReturn` and `Never` represent the bottom type in Python, indicating functions that never return normally (because they raise an unhandled exception or run an infinite loop).",
        "When a function terminates by raising an exception, calling `sys.exit()`, or executing an infinite event loop (`while True:`), it never returns a value to its caller. Annotating its return type with `None` is incorrect because `None` implies normal function completion. `NoReturn` (and its Python 3.11 alias `Never`) explicitly signals that the function will never return normally. Type checkers use this for unreachable code detection and exhaustive pattern matching verification.",
        "from typing import NoReturn\n\ndef abort_service(reason: str) -> NoReturn:\n    raise SystemExit(f'Fatal error: {reason}')\n\ndef calculate(val: int) -> int:\n    if val < 0:\n        abort_service('Value must be non-negative')\n    return val * 2  # Type checker knows val >= 0 if this line is reached",
        "Using NoReturn to annotate a function that terminates execution via an exception.",
        "In type theory, `Never` is the bottom type having zero values. If an expression evaluates to `Never`, the compiler knows that control flow can never reach that point.",
        "Implementing exhaustive `match-case` branches: asserting that an unhandled enum branch has type `Never` catches unhandled cases at compile time.",
        ["What is the difference between `NoReturn` and `Never`?", "How is `Never` used for exhaustive pattern matching validation?"],
        ["Annotating functions that return `None` implicitly with `NoReturn` (they should be annotated with `None`).", "Assuming `NoReturn` suppresses exceptions at runtime."],
        "Key distinction: `def f() -> None` returns the value `None`; `def f() -> NoReturn` never returns at all.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0654/"]
    ),

    # PY-BAS-189
    (
        "PY-BAS-189",
        "Dynamic Inspection with the inspect Module",
        "The `inspect` module provides runtime introspection tools to examine live objects, retrieve function signatures, extract docstrings, and analyze execution stack frames.",
        "CPython exposes runtime reflection via `inspect`. Using `inspect.signature(func)`, developers can inspect parameter names, default values, type annotations, and parameter kinds (positional-only, keyword-only). Using `inspect.iscoroutinefunction()`, frameworks differentiate between async and sync handlers dynamically. Functions like `inspect.getsource()` retrieve original source code text, and `inspect.getmro()` retrieves class inheritance orders.",
        "import inspect\n\ndef calculate_tax(income: float, rate: float = 0.15) -> float:\n    \"\"\"Calculates tax amount.\"\"\"\n    return income * rate\n\nsig = inspect.signature(calculate_tax)\nprint('Function Signature:', sig)\nfor name, param in sig.parameters.items():\n    print(f'  Param: {name} | Default: {param.default} | Annotation: {param.annotation}')",
        "Inspecting function parameters and default values dynamically with inspect.signature.",
        "`inspect.signature` parses `__annotations__`, `__code__.co_varnames`, and `__defaults__` into structured `Parameter` and `Signature` objects, providing binding validation via `sig.bind()`.",
        "Building FastAPI/Pydantic dependency injection containers, web routing decorators, and automatic OpenAPI schema generators.",
        ["How does `sig.bind(*args, **kwargs)` validate function call arguments reflectively?", "What is the performance overhead of calling `inspect.signature` in request paths?"],
        ["Calling `inspect.signature()` repeatedly on every HTTP request (cache the signature at startup).", "Assuming `inspect.getsource()` works on C built-in functions."],
        "Performance tip: `inspect.signature` is computationally expensive; always cache signature metadata during application startup.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/inspect.html"]
    ),

    # PY-BAS-190
    (
        "PY-BAS-190",
        "contextlib.contextmanager Generator Pattern",
        "`@contextlib.contextmanager` transforms a generator function containing a single `yield` into a context manager, executing code before the yield on `__enter__` and code after on `__exit__`.",
        "Writing a custom context manager traditionally requires defining a class with `__enter__` and `__exit__` boilerplate. The `@contextlib.contextmanager` decorator simplifies this: code preceding the `yield` statement executes upon entering the `with` block; the yielded value is bound to the `as` target; code inside the `finally` block following the `yield` is guaranteed to execute upon exit, even if exceptions occur inside the `with` block.",
        "from contextlib import contextmanager\n\n@contextmanager\ndef temporary_state():\n    print('[ENTER] Setup temporary resource')\n    try:\n        yield 'ACTIVE_STATE'\n    finally:\n        print('[EXIT] Clean up temporary resource')\n\nwith temporary_state() as state:\n    print(f'Inside with block with: {state}')",
        "Creating a custom context manager using generator syntax and contextlib.contextmanager.",
        "The decorator wraps the generator in a `_GeneratorContextManager` class. Calling `__enter__` advances the generator via `next()`. Calling `__exit__` resumes the generator with `gen.throw()` if an exception occurred, or `next()` if successful.",
        "Managing database connection checkouts, temporarily overriding environment variables, and holding distributed Redis locks.",
        ["Why must you always wrap the `yield` in a `try...finally` block inside `@contextmanager`?", "How do you suppress exceptions inside a generator context manager?"],
        ["Omitting the `try...finally` block, causing cleanup code to be skipped if an error occurs inside the `with` block.", "Yielding more than once inside the generator (raises `RuntimeError`)."],
        "Crucial rule: Always wrap `yield` in a `try-finally` block to guarantee cleanup execution.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager"]
    ),

    # PY-BAS-191
    (
        "PY-BAS-191",
        "contextlib.suppress vs Empty try-except",
        "`contextlib.suppress(*exceptions)` cleanly suppresses specified exceptions within a `with` block, replacing noisy, un-Pythonic `try-except pass` constructs.",
        "In many cleanup and file-handling operations, certain exceptions are completely benign and expected (e.g. `FileNotFoundError` when deleting a temporary file that might not exist). Writing `try: os.remove(f); except FileNotFoundError: pass` requires five lines of verbose boilerplate. `with contextlib.suppress(FileNotFoundError): os.remove(f)` achieves the exact same behavior in two clean lines while making developer intent explicit.",
        "import os\nfrom contextlib import suppress\n\n# Safely attempt removing a file that does not exist without crashing\nwith suppress(FileNotFoundError):\n    os.remove('non_existent_temporary_file.tmp')\n\nprint('Execution continued smoothly with suppressed FileNotFoundError.')",
        "Demonstrating clean exception suppression using contextlib.suppress.",
        "`suppress` implements `__exit__` by checking `if exc_type is not None and issubclass(exc_type, self._exceptions): return True`. Returning `True` instructs Python to swallow the exception.",
        "Deleting temporary files, closing optional network handles, or ignoring duplicate key errors in non-critical cache warm-ups.",
        ["Can `contextlib.suppress` catch multiple different exception types simultaneously?", "What does returning `True` from `__exit__` indicate to the Python runtime?"],
        ["Suppressing broad exceptions like `Exception` or `BaseException` (swallows bugs silently).", "Using `suppress` when the exception needs to be logged or handled with fallback logic."],
        "Interview tip: Returning `True` from any `__exit__` method swallows the exception; returning `False` allows it to propagate.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/contextlib.html#contextlib.suppress"]
    ),

    # PY-BAS-192
    (
        "PY-BAS-192",
        "contextlib.ExitStack for Dynamic Resources",
        "`contextlib.ExitStack` manages a dynamic or programmatically determined number of context managers and cleanup callbacks, guaranteeing LIFO unwind upon scope exit.",
        "When the number of resources to manage is fixed, nested `with open() as f1, open() as f2:` statements suffice. However, when managing a dynamic list of files (e.g. 50 files determined at runtime) or conditionally acquired locks, standard `with` statements cannot express dynamic scope. `ExitStack` allows calling `stack.enter_context(cm)` or `stack.callback(cleanup_func)` inside loops. When the `ExitStack` block exits, all registered cleanups execute in strict reverse (LIFO) order.",
        "from contextlib import ExitStack\n\nclass MockResource:\n    def __init__(self, name: str):\n        self.name = name\n    def __enter__(self):\n        print(f'Acquired {self.name}')\n        return self\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        print(f'Released {self.name}')\n\n# Manage dynamic list of resources\nnames = ['DB_Pool', 'Redis_Lock', 'Socket_Conn']\nwith ExitStack() as stack:\n    resources = [stack.enter_context(MockResource(n)) for n in names]\n    print('All resources acquired and active inside ExitStack.')\nprint('All resources unwound in LIFO order upon exit.')",
        "Managing a dynamic list of resources with ExitStack unwound in LIFO order.",
        "`ExitStack` maintains an internal stack of `__exit__` callback descriptors. If an exception occurs during exit unwinding, `ExitStack` chains subsequent exceptions together cleanly.",
        "Merging multiple dynamic file streams, combining arbitrary pytest fixtures, or managing transactional multi-resource rollbacks.",
        ["In what order does `ExitStack` execute registered cleanups?", "How does `stack.callback()` differ from `stack.enter_context()`?"],
        ["Attempting to manually nest dozens of `with` statements for dynamic collections.", "Forgetting that `ExitStack` also catches and chains exceptions during cleanup unwinding."],
        "Emphasize: `ExitStack` is the canonical solution for managing dynamic, runtime-determined collections of context managers.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack"]
    ),

    # PY-BAS-193
    (
        "PY-BAS-193",
        "Function Overloading with functools.singledispatch",
        "`functools.singledispatch` transforms a generic function into a single-dispatch overloaded function, dispatching execution to specialized implementations based on the runtime type of the first argument.",
        "Python does not support traditional static function overloading where multiple functions share the same name with different parameter signatures. The `@singledispatch` decorator provides runtime polymorphism based on the type of the first positional argument. Developers register type-specific handlers using `@func.register(TargetType)`. This eliminates ugly `if isinstance(arg, int): ... elif isinstance(arg, str): ...` branching chains.",
        "from functools import singledispatch\n\n@singledispatch\ndef format_data(arg):\n    return f'Generic: {arg}'\n\n@format_data.register(int)\ndef _(arg: int):\n    return f'Integer: {arg * 10}'\n\n@format_data.register(list)\ndef _(arg: list):\n    return f'List of {len(arg)} items'\n\nprint(format_data('hello'))\nprint(format_data(5))\nprint(format_data([1, 2, 3]))",
        "Implementing clean function overloading based on argument type with singledispatch.",
        "`singledispatch` maintains a dispatch dictionary mapping types to functions, caching MRO lookups in a dispatch cache for fast repeated resolution.",
        "Custom serializers, pretty-printers, and AST visitor implementations where behavior varies cleanly by data type.",
        ["Why is `singledispatch` limited to dispatching on the first argument only?", "What decorator is used for overloading class methods?"],
        ["Attempting to dispatch based on multiple arguments (requires third-party multipledispatch).", "Using `isinstance()` chains instead of `singledispatch` in extensible frameworks."],
        "Note: For class methods, use `@functools.singledispatchmethod` instead of `@singledispatch`.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/functools.html#functools.singledispatch"]
    ),

    # PY-BAS-194
    (
        "PY-BAS-194",
        "dataclasses.dataclass and Generated Dunder Methods",
        "`@dataclasses.dataclass` automatically generates standard boilerplate dunder methods (`__init__`, `__repr__`, `__eq__`, `__hash__`) by inspecting class type annotations.",
        "Writing classes that primarily store state involves repetitive boilerplate: assigning attributes in `__init__`, writing formatted strings in `__repr__`, and comparing attributes in `__eq__`. The `@dataclass` decorator inspects the class's `__annotations__` dictionary and automatically synthesizes these methods into the class at definition time. It produces clean, standard Python classes with zero runtime performance penalty compared to hand-written classes.",
        "from dataclasses import dataclass\n\n@dataclass\nclass Product:\n    name: str\n    price: float\n    in_stock: bool = True\n\np1 = Product('Mechanical Keyboard', 120.0)\np2 = Product('Mechanical Keyboard', 120.0)\n\nprint('Auto-generated repr:', p1)\nprint('Auto-generated eq:', p1 == p2)",
        "Demonstrating auto-generated __repr__ and __eq__ in a dataclass.",
        "At class creation, `@dataclass` generates Python function source strings dynamically and compiles them into the class dictionary using `exec()`, ensuring generated methods execute at native CPython speeds.",
        "Modeling domain entities, API data transfer objects (DTOs), and configuration schemas across backend applications.",
        ["What dunder methods does `@dataclass` generate by default?", "How does `@dataclass` differ from `namedtuple`?"],
        ["Mutating fields on a dataclass when immutability was intended (use `frozen=True`).", "Assuming dataclasses perform runtime data type validation (they do not validate types at runtime)."],
        "Emphasize: Dataclasses eliminate boilerplate code; they do not enforce runtime data validation.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/dataclasses.html"]
    ),

    # PY-BAS-195
    (
        "PY-BAS-195",
        "dataclasses.field and default_factory",
        "`dataclasses.field(default_factory=...)` is required when defining mutable default values (like lists or dicts) in dataclasses to prevent shared mutable state across instances.",
        "In Python, default arguments are evaluated once at class definition time. If a dataclass declared `tags: list = []`, every instance of that class would share the exact same list in memory. Python dataclasses explicitly prevent this bug: attempting to assign a mutable default directly raises `ValueError: mutable default <class 'list'> is not allowed`. Instead, developers must provide a callable via `field(default_factory=list)`, which invokes the factory to allocate a brand new instance on each initialization.",
        "from dataclasses import dataclass, field\n\n@dataclass\nclass UserAccount:\n    username: str\n    roles: list[str] = field(default_factory=list)\n\nu1 = UserAccount('alice')\nu2 = UserAccount('bob')\nu1.roles.append('admin')\n\nprint('Alice roles:', u1.roles)\nprint('Bob roles (isolated):', u2.roles)",
        "Using field(default_factory=list) to guarantee isolated mutable defaults across instances.",
        "During code generation of `__init__`, `@dataclass` emits code that calls `default_factory()` when the parameter is not supplied, binding the newly generated object to `self.attr`.",
        "Defining schemas and entity models with default collections, timestamp factories (`default_factory=datetime.utcnow`), or unique ID generators (`default_factory=uuid.uuid4`).",
        ["Why does Python raise an error if you assign `field: list = []` in a dataclass?", "What other parameters does `dataclasses.field` accept?"],
        ["Passing `default_factory=list()` (with parentheses, which evaluates immediately) instead of `default_factory=list`.", "Forgetting `field(compare=False)` when excluding transient fields from equality checks."],
        "Remember: Pass the factory callable itself (`default_factory=list`), not the result of calling it.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/dataclasses.html#dataclasses.field"]
    ),

    # PY-BAS-196
    (
        "PY-BAS-196",
        "Frozen Dataclasses and Hashability",
        "`@dataclass(frozen=True)` creates an immutable class by intercepting `__setattr__` and `__delattr__` to raise `FrozenInstanceError`, automatically generating an attribute-based `__hash__` method.",
        "By default, standard dataclasses are mutable and therefore unhashable (`__hash__ = None`), preventing them from being stored in sets or used as dictionary keys. Declaring `@dataclass(frozen=True)` makes instances immutable: any attempt to assign or delete an attribute raises `dataclasses.FrozenInstanceError`. Because instances cannot be modified after creation, `@dataclass` synthesizes a `__hash__` method derived from all fields, allowing instances to be used as dictionary keys and set elements safely.",
        "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass CacheKey:\n    endpoint: str\n    user_id: int\n\nk1 = CacheKey('/api/v1/profile', 101)\nk2 = CacheKey('/api/v1/profile', 101)\n\n# Usable in sets and dict keys\ncache_store = {k1: 'cached_profile_data'}\nprint('Retrieved from cache with identical key:', cache_store[k2])\n\ntry:\n    k1.user_id = 999  # Raises FrozenInstanceError\nexcept Exception as e:\n    print(f'Mutation blocked: {type(e).__name__}')",
        "Demonstrating immutable frozen dataclass usable as dictionary key.",
        "`frozen=True` overrides `__setattr__` with a method that raises `FrozenInstanceError`. Inside `__init__`, it assigns attributes using `object.__setattr__(self, name, value)` to bypass the frozen guard during initialization.",
        "Defining immutable domain value objects (e.g. money amounts, coordinate points, cache keys) in Domain-Driven Design (DDD).",
        ["How does `__init__` set attributes on a frozen dataclass without triggering `FrozenInstanceError`?", "Can a frozen dataclass contain a mutable list?"],
        ["Assuming a frozen dataclass makes nested mutable objects (like lists) immutable (it only freezes direct attribute references).", "Forgetting that all fields in a frozen dataclass must themselves be hashable for the dataclass to be hashable."],
        "Caution: If a frozen dataclass contains a mutable list, calling `hash()` on it will still fail at runtime.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/dataclasses.html#frozen-instances"]
    ),

    # PY-BAS-197
    (
        "PY-BAS-197",
        "dataclasses.KW_ONLY Parameters (Python 3.10+)",
        "`dataclasses.KW_ONLY` marks all subsequent dataclass fields as keyword-only, allowing subclasses to add required fields after base classes with default values.",
        "In Python, positional arguments with defaults cannot precede positional arguments without defaults. This created a major limitation when subclassing dataclasses: if a base class defined a field with a default value, child classes could not add any required fields without raising a `TypeError`. Python 3.10 introduced `KW_ONLY`: any field defined after `_: KW_ONLY` must be passed as a keyword argument upon instantiation, solving the inheritance ordering conflict cleanly.",
        "from dataclasses import dataclass, KW_ONLY\n\n@dataclass\nclass BaseEntity:\n    created_at: str = '2026-01-01'\n    _: KW_ONLY\n    id: int  # Keyword-only required field after a default field!\n\nentity = BaseEntity(id=505)\nprint('Entity initialized with KW_ONLY required id:', entity)",
        "Using KW_ONLY sentinel to allow required fields after defaults in dataclasses.",
        "The dataclass compiler treats `KW_ONLY` as a sentinel. When generating the `__init__` signature, it inserts a `*` parameter before the keyword-only fields, emitting `def __init__(self, created_at='...', *, id):`.",
        "Building extensible base models and ORM entities where base classes define standard defaults (like timestamps) and subclasses define specific required attributes.",
        ["What problem does `KW_ONLY` solve in dataclass inheritance?", "Can you mark individual fields as keyword-only without using the `KW_ONLY` sentinel?"],
        ["Attempting to pass keyword-only fields as positional arguments at instantiation time.", "Using `KW_ONLY` in Python versions earlier than 3.10."],
        "Tip: Individual fields can also be marked keyword-only using `field(kw_only=True)`.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/dataclasses.html#keyword-only-parameters"]
    ),

    # PY-BAS-198
    (
        "PY-BAS-198",
        "Enum vs IntEnum vs StrEnum",
        "`Enum` provides type-safe enumerations compared by identity/equality; `IntEnum` and `StrEnum` subclass `int` and `str` respectively, allowing seamless comparison and serialization with native primitive types.",
        "Python's `enum` module provides distinct enumeration classes: 1) `Enum`: Strict enumeration. Members do not compare equal to raw integers or strings (`Status.ACTIVE != 1`), ensuring strict type safety. 2) `IntEnum`: Subclasses `int`. Members compare directly with integers (`Priority.HIGH == 1`) and can be used as list indices. 3) `StrEnum` (Python 3.11+): Subclasses `str`. Members compare directly with strings (`Role.ADMIN == 'admin'`), serializing cleanly to JSON without custom serializer encoders.",
        "from enum import Enum, IntEnum\n\nclass StrictStatus(Enum):\n    PENDING = 'pending'\n\nclass CompatiblePriority(IntEnum):\n    LOW = 1\n    HIGH = 2\n\nprint('Strict Enum comparison with string:', StrictStatus.PENDING == 'pending')  # False\nprint('IntEnum comparison with int:', CompatiblePriority.HIGH == 2)             # True",
        "Contrasting strict Enum identity against IntEnum value equivalence.",
        "`EnumMeta` constructs unique singleton instances for each enum member during class creation, overriding `__repr__`, `__eq__`, and hashing to prevent duplicate members.",
        "Using `StrEnum` for FastAPI endpoint query parameters or JSON API schemas where incoming string payloads must match enum members seamlessly.",
        ["Why doesn't a standard `Enum` compare equal to its underlying value?", "What happens if two enum members have the same value?"],
        ["Expecting `Enum.MEMBER == 'value'` to evaluate to `True` (use `StrEnum` or compare `Enum.MEMBER.value`).", "Using `IntEnum` when strict type isolation between different enums is required."],
        "Best practice: Use `StrEnum` for API schemas and JSON payloads; use strict `Enum` for internal business logic state machines.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/enum.html"]
    ),

    # PY-BAS-199
    (
        "PY-BAS-199",
        "Automatic Enum Values with enum.auto()",
        "`enum.auto()` generates sequential or customized enum values automatically, eliminating manual value assignment when exact values do not matter.",
        "When defining an enumeration representing states or flags, developers often do not care about the underlying value (e.g. whether `Color.RED` is 1 or 2). Assigning manual integers is tedious and error-prone. Calling `enum.auto()` instructs Python to generate values sequentially starting from 1. By overriding `_generate_next_value_()`, classes can customize automatic value generation (e.g. generating lowercase member names automatically).",
        "from enum import Enum, auto\n\nclass AutoNameEnum(Enum):\n    def _generate_next_value_(name, start, count, last_values):\n        return name.lower()  # Custom auto generator\n\nclass TaskState(AutoNameEnum):\n    QUEUED = auto()\n    RUNNING = auto()\n    COMPLETED = auto()\n\nprint('TaskState.QUEUED value:', TaskState.QUEUED.value)\nprint('TaskState.RUNNING value:', TaskState.RUNNING.value)",
        "Using enum.auto() with custom _generate_next_value_ to generate string values automatically.",
        "`EnumMeta.__new__` detects instances of `auto` and calls `_generate_next_value_()` to resolve the concrete value before member registration.",
        "State machines, command dispatchers, and workflow engines where enum member identity is all that matters.",
        ["What is the default value generated by `enum.auto()` in standard `Enum` vs `StrEnum`?", "Can you mix `auto()` with manual values in the same Enum?"],
        ["Assuming `auto()` generates cryptographically unique UUIDs (it generates sequential integers by default).", "Mixing `auto()` and manual values haphazardly, risking value collisions."],
        "Tip: In `StrEnum` (Python 3.11+), `auto()` automatically generates the lowercase member name by default.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/enum.html#enum.auto"]
    ),

    # PY-BAS-200
    (
        "PY-BAS-200",
        "Controlling Public APIs with __all__",
        "`__all__` is a module-level list of strings defining the explicit public interface exported when client code executes `from module import *`.",
        "By default, `from module import *` imports all names that do not begin with an underscore `_`. This pollutes the importer's namespace with imported sub-modules, internal helper functions, and temporary variables. Defining `__all__ = ['PublicClass', 'public_function']` in `__init__.py` or module files explicitly restricts wildcard imports to only those listed names. Furthermore, documentation generators (Sphinx) and IDE auto-complete engines use `__all__` to determine the official public API surface.",
        "# Inside my_package/__init__.py\n__all__ = ['Client', 'connect']\n\nclass Client:\n    pass\n\ndef connect():\n    return 'connected'\n\ndef _internal_helper():\n    pass  # Not exported\n\nprint('Module __all__ defined:', __all__)\nprint('Wildcard import from module import * will export only Client and connect.')",
        "Defining __all__ to declare explicit public API boundaries.",
        "CPython's `IMPORT_STAR` bytecode instruction inspects the target module's `__dict__`. If `\"__all__\"` exists, it iterates strictly through the names in `__all__`; if omitted, it copies all keys not starting with `_`.",
        "Building public libraries, packages, and frameworks where internal implementation details must be hidden from external consumers.",
        ["Does `__all__` prevent someone from explicitly importing an unlisted function (`from module import _internal`)?", "What happens if `__all__` contains a string name that does not exist in the module?"],
        ["Believing `__all__` enforces security or prevents access to unlisted attributes (it only controls `import *`).", "Defining `__all__` as a tuple or set when tools expect a mutable list."],
        "Emphasize: `__all__` is an API design contract controlling wildcard imports and documentation; it is not a security boundary.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/tutorial/modules.html#importing-from-a-package"]
    )
]
