"""
adv_py_inter.py
===============
Intermediate Advanced Python Questions: PY-INT-176 to PY-INT-200 (25 questions)
"""

inter_data = [
    # PY-INT-176
    (
        "PY-INT-176",
        "Metaclasses and the Role of type",
        "A Metaclass is the class of a class, responsible for intercepting and customizing the creation of class objects; `type` is Python's default built-in metaclass.",
        "In Python, everything is an object, including classes themselves. If an instance is created from a class (`obj = Class()`), then what creates the class? A metaclass. By default, all classes in Python are instances of the built-in metaclass `type`. Calling `type(name, bases, dict)` dynamically constructs and returns a new class object at runtime. By subclassing `type`, developers can create custom metaclasses (`class Meta(type):`) to intercept, validate, modify, or register classes at definition time.",
        "# Dynamic class creation using type as metaclass:\n# type(class_name, bases_tuple, attributes_dict)\nDynamicUser = type('DynamicUser', (), {\n    'role': 'standard',\n    'get_role': lambda self: self.role\n})\n\nu = DynamicUser()\nprint('Dynamic class instance created:', u.get_role())\nprint('Class of DynamicUser is type:', type(DynamicUser) is type)",
        "Constructing a functional class dynamically at runtime using type directly.",
        "When Python encounters a `class` statement, it collects the namespace dictionary and calls `metaclass(name, bases, namespace)`. In CPython, `type.__call__` executes `metaclass->tp_new` followed by `tp_init` to allocate the `PyTypeObject`.",
        "Developing ORM frameworks (SQLAlchemy, Django ORM) where metaclasses inspect class declarations and construct database table schemas automatically.",
        ["What are the three arguments passed to `type()` when creating a class dynamically?", "How does an instance differ from a class in terms of its type?"],
        ["Using metaclasses for simple tasks where class decorators or `__init_subclass__` are simpler and cleaner.", "Confusing the class of an object with the base class of an object."],
        "Quote Tim Peters: 'Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't.'",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#metaclasses"]
    ),

    # PY-INT-177
    (
        "PY-INT-177",
        "Metaclass Lifecycle: __prepare__, __new__, and __init__",
        "Metaclass execution follows a strict three-phase lifecycle: `__prepare__` creates the initial namespace mapping, `__new__` allocates the class object, and `__init__` initializes it.",
        "When a class with a custom metaclass is defined: 1) `__prepare__(mcs, name, bases, **kw)`: Invoked before the class body is evaluated. Returns a mapping (e.g. an `OrderedDict` or custom tracking dictionary) used to populate the class namespace. 2) Class Body Evaluation: Python executes the statements in the class body, populating the prepared namespace. 3) `__new__(mcs, name, bases, namespace, **kw)`: Allocates and returns the newly created `PyTypeObject`. 4) `__init__(cls, name, bases, namespace, **kw)`: Initializes the newly created class object after it has been created.",
        "class CustomNamespace(dict):\n    def __setitem__(self, key, value):\n        # Custom validation during class body execution\n        super().__setitem__(key, value)\n\nclass ValidatingMeta(type):\n    @classmethod\n    def __prepare__(mcs, name, bases, **kwargs):\n        return CustomNamespace()\n    \n    def __new__(mcs, name, bases, namespace, **kwargs):\n        # Inspect or transform namespace before class creation\n        namespace['validated'] = True\n        return super().__new__(mcs, name, bases, namespace)\n\nclass AppConfig(metaclass=ValidatingMeta):\n    port = 8080\n\nprint('AppConfig validated flag added by metaclass:', AppConfig.validated)",
        "Demonstrating the metaclass lifecycle using __prepare__ and __new__.",
        "`__prepare__` must be a `@classmethod`. In `typeobject.c`, `type_new()` receives the populated namespace dictionary and constructs the `PyTypeObject` struct with descriptor offsets.",
        "Building declarative serialization frameworks where `__prepare__` preserves field declaration order, or enforcing naming conventions across API models.",
        ["Why must `__prepare__` be decorated with `@classmethod`?", "What is the difference between returning a class from `__new__` vs modifying it in `__init__`?"],
        ["Forgetting to call `super().__new__()` inside a metaclass's `__new__` method.", "Attempting to return a custom namespace from `__new__` instead of `__prepare__`."],
        "Remember the order: `__prepare__` creates the dict -> Body executes -> `__new__` creates the class -> `__init__` initializes it.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#metaclass-example"]
    ),

    # PY-INT-178
    (
        "PY-INT-178",
        "Class Customization with __init_subclass__ (PEP 487)",
        "`__init_subclass__` is a class method hook introduced in PEP 487 that allows base classes to customize and validate subclass creation without needing complex metaclasses.",
        "Historically, modifying or registering child classes required authoring a custom metaclass, which often led to difficult metaclass conflicts in multiple inheritance. PEP 487 introduced `__init_subclass__`. When a class subclasses a base class, the base class's `__init_subclass__` is invoked automatically with the newly created subclass as its first argument, along with any arbitrary keyword arguments passed in the class declaration line.",
        "class PluginBase:\n    registry = {}\n    \n    def __init_subclass__(cls, plugin_name: str = '', **kwargs):\n        super().__init_subclass__(**kwargs)\n        name = plugin_name or cls.__name__.lower()\n        cls.registry[name] = cls\n        print(f'Registered plugin: {name} -> {cls.__name__}')\n\nclass AuthPlugin(PluginBase, plugin_name='oauth2'):\n    pass\n\nclass CachePlugin(PluginBase, plugin_name='redis'):\n    pass\n\nprint('Final Plugin Registry:', list(PluginBase.registry.keys()))",
        "Automatic subclass registration and keyword argument handling with __init_subclass__.",
        "`__init_subclass__` is implicitly a `@classmethod`. In `typeobject.c`, `type_new()` looks up `__init_subclass__` on base classes and executes it immediately after the subclass `PyTypeObject` is initialized.",
        "Building pluggable microservice architectures, ORM model registries, and enforcing subclass attribute contracts without metaclass conflicts.",
        ["How does `__init_subclass__` prevent metaclass conflicts?", "Why should you always call `super().__init_subclass__(**kwargs)`?"],
        ["Forgetting `super().__init_subclass__(**kwargs)`, which breaks cooperative multiple inheritance.", "Using a complex metaclass when `__init_subclass__` achieves the exact same goal in 5 lines."],
        "Best practice: Always prefer `__init_subclass__` over metaclasses for class customization and registration.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0487/"]
    ),

    # PY-INT-179
    (
        "PY-INT-179",
        "Automatic Descriptor Naming with __set_name__ (PEP 487)",
        "`__set_name__(self, owner, name)` is a descriptor method introduced in PEP 487 that is called automatically during class creation to inform the descriptor of the attribute name it was assigned to.",
        "Prior to Python 3.6, descriptors could not determine what attribute name they were assigned to in the class dictionary without explicitly receiving it as an `__init__` argument (`field = Descriptor('field')`), leading to redundant, error-prone code. With PEP 487, CPython automatically invokes `descriptor.__set_name__(owner_class, attribute_name)` on every descriptor defined in a class body as soon as the class is created, allowing descriptors to bind storage names transparently.",
        "class ValidatedField:\n    def __set_name__(self, owner, name):\n        # Automatically called during owner class creation\n        self.storage_name = f'_{name}'\n        self.name = name\n    \n    def __get__(self, instance, owner):\n        if instance is None: return self\n        return getattr(instance, self.storage_name, None)\n    \n    def __set__(self, instance, value):\n        if not isinstance(value, str):\n            raise TypeError(f'{self.name} must be a string')\n        setattr(instance, self.storage_name, value)\n\nclass User:\n    # No need to pass 'username' or 'email' to ValidatedField()!\n    username = ValidatedField()\n    email = ValidatedField()\n\nu = User()\nu.username = 'antigravity'\nprint('Username set successfully:', u.username)",
        "Using __set_name__ in a descriptor for automatic attribute name detection.",
        "In `typeobject.c`, during class finalization, CPython iterates through the class `__dict__` and calls `_PyObject_CallMethodIdOneArg(val, &PyId___set_name__, type, key)` for any attribute implementing the slot.",
        "Developing ORM column descriptors, Pydantic field validators, and dependency injection property decorators.",
        ["When is `__set_name__` called during the object lifecycle?", "Does `__set_name__` get called if a descriptor is added dynamically to a class after creation?"],
        ["Manually passing attribute names into descriptor constructors.", "Assuming `__set_name__` is called when dynamically attaching descriptors to instances."],
        "Note: `__set_name__` is called only for descriptors defined in the class body at class definition time.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0487/"]
    ),

    # PY-INT-180
    (
        "PY-INT-180",
        "Data Descriptors vs Non-Data Descriptors",
        "A Data Descriptor defines `__set__` and/or `__delete__` and takes precedence over instance `__dict__`, whereas a Non-Data Descriptor defines only `__get__` and can be overridden by instance attributes.",
        "Descriptors customize attribute access. The presence of `__set__` fundamentally alters attribute resolution precedence: 1) Data Descriptors: Define `__set__` (or `__delete__`). When accessing `obj.attr`, Python prioritizes the data descriptor over any entry in `obj.__dict__`. Even if you assign `obj.__dict__['attr'] = 123`, `obj.attr` still invokes the descriptor's `__get__`. 2) Non-Data Descriptors: Define only `__get__` (e.g. normal methods). If an attribute with the same name exists in `obj.__dict__`, the instance dictionary overrides the descriptor.",
        "class NonDataDesc:\n    def __get__(self, instance, owner):\n        return 'Descriptor Value'\n\nclass DataDesc:\n    def __get__(self, instance, owner):\n        return 'Data Descriptor Value'\n    def __set__(self, instance, value):\n        pass\n\nclass Demo:\n    nd = NonDataDesc()\n    dd = DataDesc()\n\nd = Demo()\n# Shadow both descriptors in instance __dict__\nd.__dict__['nd'] = 'Shadowed in instance'\nd.__dict__['dd'] = 'Shadowed in instance'\n\nprint('Non-data descriptor shadowed by instance dict:', d.nd)\nprint('Data descriptor takes precedence over instance dict:', d.dd)",
        "Contrasting resolution precedence between Data and Non-Data descriptors.",
        "In `typeobject.c`, `_PyObject_GenericGetAttrWithDict()` checks if the class descriptor is a data descriptor. If true, it calls descriptor `__get__` immediately, bypassing `instance->__dict__` entirely.",
        "Understanding method binding: methods are non-data descriptors, which is why assigning `obj.my_method = custom_func` can monkey-patch an individual instance's method.",
        ["What methods must a descriptor implement to be considered a Data Descriptor?", "Why are normal Python functions and methods non-data descriptors?"],
        ["Defining only `__get__` when writing an attribute validator (without `__set__`, instance dict can shadow the descriptor).", "Confusing descriptor precedence rules during caching implementations."],
        "Rule to memorize: Data Descriptors > Instance `__dict__` > Non-Data Descriptors.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/howto/descriptor.html"]
    ),

    # PY-INT-181
    (
        "PY-INT-181",
        "Complete Attribute Lookup Resolution Order",
        "CPython resolves `obj.attr` following a strict hierarchy: Data Descriptors > Instance `__dict__` > Non-Data Descriptors > Class `__dict__` > `__getattr__`.",
        "When an attribute lookup `obj.attr` is evaluated, CPython executes `_PyObject_GenericGetAttrWithDict()` in `typeobject.c`: 1) Search the class MRO for an attribute matching `attr`. If found and it is a Data Descriptor (has `__set__` or `__delete__`), call its `__get__` and return the result. 2) If not a data descriptor, search the instance's own `obj.__dict__`. If present, return it. 3) If not in instance dictionary, check the attribute found in the class MRO in step 1. If it is a Non-Data Descriptor (has `__get__`), call its `__get__`; if it is a standard class attribute, return it. 4) If not found anywhere in steps 1-3, call `obj.__getattr__(attr)` if implemented. 5) If `__getattr__` is not defined or raises `AttributeError`, raise `AttributeError`.",
        "class CustomAttr:\n    def __getattr__(self, name):\n        return f'Fallback for {name}'\n\nc = CustomAttr()\nprint(c.missing_property)  # Step 4: Falls back to __getattr__",
        "Demonstrating fallback to __getattr__ when prior lookup stages yield no attribute.",
        "Bytecode emits `LOAD_ATTR`. In CPython, `tp_getattro` implements this multi-step lookup, checking MRO dictionaries and caching type tags for inline caches.",
        "Building dynamic RPC clients, mock libraries, or ORM lazy-loading proxies that intercept attribute resolution safely.",
        ["What is the difference between `__getattr__` and `__getattribute__`?", "Where do `__slots__` descriptors fit into this resolution order?"],
        ["Overriding `__getattribute__` without calling `super().__getattribute__`, causing infinite recursion.", "Confusing `__getattr__` (called only on failure) with `__getattribute__` (called on every access)."],
        "Golden rule: `__getattr__` is called only as a fallback when the attribute is not found; `__getattribute__` intercepts every single access unconditionally.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access"]
    ),

    # PY-INT-182
    (
        "PY-INT-182",
        "How @property is Implemented as a Data Descriptor",
        "`@property` is a built-in Python class that implements `__get__`, `__set__`, and `__delete__`, turning decorated methods into a full data descriptor.",
        "The `@property` decorator is not syntactic sugar; it is a concrete C-level descriptor type (`property`). When a function is decorated with `@property`, an instance of `property` is created with the getter function stored in its `fget` slot. Because `property` defines a `__set__` method (even if no setter is provided, in which case `__set__` raises `AttributeError: can't set attribute`), it acts as a Data Descriptor. This guarantees that an instance dictionary assignment can never shadow or override a property.",
        "class Temperature:\n    def __init__(self, celsius: float):\n        self._celsius = celsius\n    \n    @property\n    def celsius(self) -> float:\n        return self._celsius\n    \n    @celsius.setter\n    def celsius(self, value: float):\n        if value < -273.15:\n            raise ValueError('Below absolute zero!')\n        self._celsius = value\n\nt = Temperature(25.0)\nprint('Property getter:', t.celsius)\nt.celsius = 30.0\nprint('Property setter updated:', t.celsius)",
        "Defining a property with getter and setter using @property data descriptor.",
        "In `descrobject.c`, `property_descr_get` invokes `PyObject_CallOneArg(prop->prop_get, obj)`. `property_descr_set` checks if `prop->prop_set` is set; if null, it raises an attribute error.",
        "Encapsulating internal state with validation guards while presenting a clean attribute interface in public APIs.",
        ["Why is `@property` considered a data descriptor even if no setter is defined?", "What is the return value of `@prop.setter`?"],
        ["Trying to override a read-only property by assigning to `obj.__dict__['prop']` (data descriptor still takes precedence).", "Writing heavy database queries or network I/O inside properties (violates user expectation of fast attribute access)."],
        "API guideline: Properties should be fast and side-effect free; use explicit methods for heavy operations.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/howto/descriptor.html#properties"]
    ),

    # PY-INT-183
    (
        "PY-INT-183",
        "typing.ParamSpec and Concatenate (PEP 612)",
        "`typing.ParamSpec` captures the exact parameter specifications of a callable, and `typing.Concatenate` prepends arguments, enabling type-safe higher-order decorator annotations.",
        "Prior to Python 3.10 (PEP 612), annotating a decorator that preserved function arguments required `Callable[..., R]`, which destroyed all static type checking on the wrapped function's parameters. `ParamSpec('P')` captures parameter signatures (both positional and keyword). Combined with `Concatenate[FirstArg, P]`, decorators that inject parameters (like dependency injection or passing `self`/`request`) maintain complete static type safety for all caller arguments.",
        "from typing import Callable, TypeVar, ParamSpec, Concatenate\n\nP = ParamSpec('P')\nR = TypeVar('R')\n\ndef timing_decorator(func: Callable[P, R]) -> Callable[P, R]:\n    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:\n        return func(*args, **kwargs)\n    return wrapper\n\n@timing_decorator\ndef greet(name: str, repeat: int = 1) -> str:\n    return f'Hello {name}! ' * repeat\n\n# Type checkers strictly enforce signature (name: str, repeat: int) on greet!\nprint(greet('Antigravity', 2))",
        "Writing a type-safe decorator preserving parameter signatures using ParamSpec.",
        "Static type checkers map `P.args` to `Tuple[Any, ...]` and `P.kwargs` to `Dict[str, Any]` at runtime, while preserving exact type associations during static analysis.",
        "Annotating authentication decorators, retry handlers, and ASGI middleware in modern FastAPI and Django applications.",
        ["What problem does `ParamSpec` solve that `TypeVar` cannot?", "How does `Concatenate` inject an argument into a function signature?"],
        ["Using `Callable[..., R]` for decorators in modern Python codebases.", "Attempting to instantiate `ParamSpec` at runtime like a class."],
        "Emphasize: Use `ParamSpec` whenever authoring decorators to preserve function signature validation.",
        ["[Decorators & Generators](decorators-and-generators.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0612/"]
    ),

    # PY-INT-184
    (
        "PY-INT-184",
        "Type Narrowing with TypeGuard and TypeIs",
        "`typing.TypeGuard` and `typing.TypeIs` (PEP 647/742) allow user-defined boolean functions to inform static type checkers of precise type narrowing inside conditional branches.",
        "Standard `isinstance()` checks narrow types automatically in static type checkers (`if isinstance(x, str): ...`). However, if validation logic is extracted into a helper function (`is_string(x)`), type checkers lose track of the narrowing. Annotating the helper's return type as `TypeGuard[str]` instructs type checkers that returning `True` narrows the argument's type to `str` inside the `if` block. Python 3.13's `TypeIs` refines this by providing two-way narrowing (narrows both the `if` branch and the `else` branch).",
        "from typing import TypeGuard\n\ndef is_string_list(val: list[object]) -> TypeGuard[list[str]]:\n    return all(isinstance(x, str) for x in val)\n\nitems: list[object] = ['alpha', 'beta', 'gamma']\nif is_string_list(items):\n    # Type checker narrows items to list[str] inside this block!\n    print('Joined strings:', ', '.join(items))",
        "Using TypeGuard to validate and narrow a heterogeneous list to a homogeneous list of strings.",
        "`TypeGuard` functions evaluate standard boolean logic at runtime; the type annotation is consumed by static type checkers to update the symbol table type state within the conditional scope.",
        "Validating untrusted external JSON data, parsing polymorphic API responses, and checking complex custom data model invariants.",
        ["How does `TypeIs` (PEP 742) improve upon `TypeGuard` (PEP 647)?", "Does `TypeGuard` perform runtime validation automatically?"],
        ["Writing a `TypeGuard` function whose runtime check does not accurately match the claimed type annotation.", "Assuming `TypeGuard` narrows the `else` branch (only `TypeIs` narrows the `else` branch)."],
        "Tip: Use `TypeGuard` when you need custom validation functions that static type checkers can understand.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0647/"]
    ),

    # PY-INT-185
    (
        "PY-INT-185",
        "typing.Self for Fluent Interfaces (PEP 673)",
        "`typing.Self` (PEP 673) annotates methods that return an instance of the current enclosing class, maintaining correct subclass return types in method chaining and fluent APIs.",
        "In fluent interfaces or builder patterns, methods return `self` (`builder.set_name().set_age()`). Historically, typing the return type as the base class name meant that calling chained methods on a subclass returned the base class type according to static type checkers, losing subclass-specific methods. PEP 673 introduced `Self` (Python 3.11+). When a method is annotated with `-> Self`, type checkers automatically resolve the return type to the exact subclass on which the method was invoked.",
        "from typing import Self\n\nclass QueryBuilder:\n    def __init__(self):\n        self.query = ''\n    \n    def select(self, table: str) -> Self:\n        self.query += f'SELECT * FROM {table} '\n        return self\n    \n    def where(self, condition: str) -> Self:\n        self.query += f'WHERE {condition}'\n        return self\n\nqb = QueryBuilder().select('users').where('active = 1')\nprint('Generated Query:', qb.query)",
        "Implementing a type-safe fluent query builder using typing.Self.",
        "`Self` represents an implicit `TypeVar('Self', bound='CurrentClass')`. In static type checkers, `Self` covariant resolution binds dynamically to the receiving instance's type.",
        "Designing builder patterns, ORM query interfaces, and immutable data transformation methods in domain models.",
        ["What problem does `typing.Self` solve in class inheritance hierarchies?", "How did developers annotate fluent interfaces before `typing.Self`?"],
        ["Hard-coding the base class name as return type in inheritable fluent methods.", "Using `Self` outside of class method annotations."],
        "Emphasize: Use `Self` whenever a method returns `self` or a clone of `self` to support seamless subclass chaining.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0673/"]
    ),

    # PY-INT-186
    (
        "PY-INT-186",
        "Generic Type Variance: Covariance, Contravariance, and Invariance",
        "Variance defines how subtyping between complex generic types relates to subtyping between their component types: Invariant (default), Covariant (`covariant=True`), or Contravariant (`contravariant=True`).",
        "Understanding type variance: 1) Invariant: If `Dog` is a subtype of `Animal`, `Box[Dog]` is NOT a subtype of `Box[Animal]`. Mutable containers (like `list`) must be invariant because adding a `Cat` into a `Box[Animal]` would violate the `Dog` constraint. 2) Covariant (`covariant=True`): If `Dog` is a subtype of `Animal`, `Reader[Dog]` IS a subtype of `Reader[Animal]`. Read-only producers (like immutable sequences) can be covariant. 3) Contravariant (`contravariant=True`): If `Dog` is a subtype of `Animal`, `Consumer[Animal]` IS a subtype of `Consumer[Dog]`. Write-only consumers (like sinks or argument handlers) are contravariant.",
        "from typing import TypeVar, Generic\n\n# Covariant TypeVar: Read-only container / producer\nT_co = TypeVar('T_co', covariant=True)\n\nclass ReadOnlyStream(Generic[T_co]):\n    def __init__(self, data: T_co):\n        self._data = data\n    def read(self) -> T_co:\n        return self._data\n\nprint('ReadOnlyStream is covariant: stream of Dog can be safely passed where stream of Animal is expected.')",
        "Defining a covariant generic type variable for a read-only producer class.",
        "Static type checkers enforce variance rules: Covariant type variables can only appear in return positions; Contravariant type variables can only appear in argument positions.",
        "Designing enterprise plugin architectures, event bus subscribers, and repository interfaces with sound mathematical type safety.",
        ["Why must mutable collections like `list` be invariant?", "In what position can a contravariant type variable appear in a method signature?"],
        ["Making a mutable container covariant, allowing invalid types to be inserted at runtime.", "Assuming all generics in Python are covariant by default (they are invariant by default)."],
        "Rule to remember: Producer = Covariant (return types); Consumer = Contravariant (argument types); Mutable = Invariant.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://peps.python.org/pep-0484/#covariance-and-contravariance"]
    ),

    # PY-INT-187
    (
        "PY-INT-187",
        "Class Patterns and __match_args__ in Pattern Matching",
        "`__match_args__` is a class-level tuple of attribute names that defines the positional pattern matching order when matching custom class instances inside `match-case` blocks.",
        "Python 3.10 introduced Structural Pattern Matching (PEP 634). When matching custom class instances positionally (`case Point(x, y):`), CPython needs to know which attributes map to the first and second positional arguments. By defining `__match_args__ = ('x', 'y')`, a class declares this mapping. Dataclasses automatically generate `__match_args__` matching their field declaration order.",
        "class GeoCoordinate:\n    __match_args__ = ('lat', 'lon')\n    def __init__(self, lat: float, lon: float):\n        self.lat = lat\n        self.lon = lon\n\ndef route(coord):\n    match coord:\n        case GeoCoordinate(0.0, 0.0):\n            return 'Null Island'\n        case GeoCoordinate(lat, lon):\n            return f'Navigating to {lat}, {lon}'\n        case _:\n            return 'Invalid coordinate'\n\nprint(route(GeoCoordinate(37.77, -122.41)))",
        "Defining __match_args__ on a custom class to enable positional pattern matching.",
        "During bytecode evaluation of `MATCH_CLASS`, CPython inspects `cls.__match_args__`. It reads attributes by name from the matched instance and binds them to pattern variables.",
        "Parsing AST trees, processing financial transactions, building compilers, and implementing command dispatch pipelines.",
        ["What happens if a class does not define `__match_args__` and is matched positionally?", "Does `@dataclass` generate `__match_args__` automatically?"],
        ["Attempting positional class matching on standard classes without `__match_args__` (raises `TypeError`).", "Confusing structural pattern matching with a standard switch-case statement."],
        "Tip: Dataclasses automatically generate `__match_args__` for you.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0634/"]
    ),

    # PY-INT-188
    (
        "PY-INT-188",
        "Guard Clauses in Structural Pattern Matching",
        "A guard clause (`if condition`) appends an arbitrary boolean condition to a `case` pattern; the pattern branch matches only if both the structural pattern matches and the guard evaluates to true.",
        "Structural pattern matching separates shape matching from boolean logic. In a `case` clause, appending `if <expression>` creates a guard. Python first verifies that the target matches the structural pattern (destructuring values and binding variables). Then, it evaluates the guard expression. If the guard evaluates to `False`, pattern variables are unbound and Python falls through to test subsequent `case` branches.",
        "def process_order(order: dict) -> str:\n    match order:\n        case {'status': 'pending', 'total': amount} if amount > 1000:\n            return 'High-value order requires manager approval'\n        case {'status': 'pending', 'total': amount}:\n            return f'Standard order auto-approved: ${amount}'\n        case {'status': 'cancelled'}:\n            return 'Order cancelled'\n        case _:\n            return 'Unknown status'\n\nprint(process_order({'status': 'pending', 'total': 2500}))\nprint(process_order({'status': 'pending', 'total': 150}))",
        "Using guard clauses in pattern matching to route high-value pending orders.",
        "In `compile.c`, the compiler emits conditional branch instructions after pattern destructuring. If the guard test fails, control jumps directly to the next pattern candidate block.",
        "Business rule routing engines, financial fraud detection, and complex authorization decision trees.",
        ["Can you reference variables bound in the pattern inside the guard expression?", "What happens if a guard expression raises an unhandled exception?"],
        ["Writing complex nested `if-else` blocks inside the match body instead of using guard clauses.", "Assuming guards run before the structural pattern matches."],
        "Emphasize: Pattern variables are bound *before* the guard evaluates, so you can use them directly in the guard condition.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0636/"]
    ),

    # PY-INT-189
    (
        "PY-INT-189",
        "AsyncExitStack for Dynamic Asynchronous Resources",
        "`contextlib.AsyncExitStack` manages a dynamic collection of asynchronous and synchronous context managers, ensuring all resources are safely finalized in LIFO order upon async scope exit.",
        "In modern asynchronous applications (FastAPI/Starlette), services often acquire multiple asynchronous resources whose quantity is determined dynamically (e.g. acquiring N Redis connection locks or opening multiple async file streams). Standard `async with` cannot manage dynamic collections. `AsyncExitStack` provides `enter_async_context()` and `push_async_callback()`. When the stack exits, all asynchronous and synchronous cleanups are awaited and executed in reverse order, even if tasks are cancelled.",
        "import asyncio\nfrom contextlib import AsyncExitStack\n\nclass AsyncResource:\n    def __init__(self, name: str):\n        self.name = name\n    async def __aenter__(self):\n        print(f'[AENTER] Acquired {self.name}')\n        return self\n    async def __aexit__(self, exc_type, exc_val, exc_tb):\n        print(f'[AEXIT] Released {self.name}')\n\nasync def main():\n    async with AsyncExitStack() as stack:\n        res1 = await stack.enter_async_context(AsyncResource('DB_Conn'))\n        res2 = await stack.enter_async_context(AsyncResource('Redis_Lock'))\n        print('All async resources active in stack.')\n    print('All async resources safely unwound.')\n\nasyncio.run(main())",
        "Managing dynamic asynchronous resources with AsyncExitStack in LIFO order.",
        "`AsyncExitStack` maintains an internal stack of async and sync exit callbacks. During `__aexit__`, it awaits each async finalizer sequentially, preserving exception context via exception chaining.",
        "Lifespan handlers in FastAPI applications managing database connection pools, HTTP client sessions, and message consumer lifecycles.",
        ["Can `AsyncExitStack` manage synchronous context managers as well as asynchronous ones?", "How does `AsyncExitStack` handle cancellation during cleanup?"],
        ["Attempting to use synchronous `ExitStack` to manage async context managers (raises `TypeError`).", "Forgetting that `enter_async_context()` must be awaited."],
        "Remember: Always `await stack.enter_async_context(resource)` inside `AsyncExitStack`.",
        ["[Concurrency & Parallelism](concurrency-and-parallelism.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/contextlib.html#contextlib.AsyncExitStack"]
    ),

    # PY-INT-190
    (
        "PY-INT-190",
        "functools.singledispatchmethod for Class Methods",
        "`functools.singledispatchmethod` implements single-dispatch function overloading on methods within classes, dispatching based on the type of the first argument after `self`.",
        "While `functools.singledispatch` dispatches on the very first positional argument, applying it to an instance method causes it to dispatch on `self` (the instance itself), rendering it useless for method overloading. `functools.singledispatchmethod` solves this by ignoring `self` (or `cls` for classmethods) and dispatching execution based on the runtime type of the *first actual parameter* passed to the method.",
        "from functools import singledispatchmethod\n\nclass DataSerializer:\n    @singledispatchmethod\n    def serialize(self, data):\n        raise NotImplementedError(f'Cannot serialize {type(data)}')\n    \n    @serialize.register(str)\n    def _(self, data: str) -> str:\n        return f'STRING:\"{data}\"'\n    \n    @serialize.register(int)\n    def _(self, data: int) -> str:\n        return f'INTEGER:{data}'\n\ns = DataSerializer()\nprint(s.serialize('hello'))\nprint(s.serialize(42))",
        "Overloading an instance method based on argument type using singledispatchmethod.",
        "`singledispatchmethod` wraps a descriptor that returns a bound dispatch function. When called, it extracts `args[1]` (the argument after `self`) and performs the dictionary type lookup.",
        "Building serializers, event handlers, and data transformation services inside object-oriented enterprise domain layers.",
        ["Why doesn't `@functools.singledispatch` work directly on instance methods?", "Can `singledispatchmethod` be used with `@classmethod`?"],
        ["Decorating instance methods with `@singledispatch` instead of `@singledispatchmethod`.", "Expecting `singledispatchmethod` to dispatch based on multiple arguments."],
        "Emphasize: Use `singledispatchmethod` on methods so Python skips `self` when determining the dispatch type.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/functools.html#functools.singledispatchmethod"]
    ),

    # PY-INT-191
    (
        "PY-INT-191",
        "dataclasses.__post_init__ Validation and Derived State",
        "`__post_init__` is an optional method in dataclasses called immediately after the auto-generated `__init__` finishes, allowing attribute validation and initialization of derived fields.",
        "While `@dataclass` automatically generates the constructor, developers often need to perform validation (e.g. ensuring `age >= 0`) or calculate derived values based on supplied parameters (e.g. computing `full_name` from `first_name` and `last_name`). The generated `__init__` automatically calls `self.__post_init__()` as its final step, providing the exact hook required to enforce invariants and set computed attributes.",
        "from dataclasses import dataclass, field\n\n@dataclass\nclass UserAccount:\n    first_name: str\n    last_name: str\n    full_name: str = field(init=False)  # Excluded from __init__ args\n    \n    def __post_init__(self):\n        if not self.first_name or not self.last_name:\n            raise ValueError('Names cannot be empty')\n        self.full_name = f'{self.first_name} {self.last_name}'\n\nu = UserAccount('John', 'Doe')\nprint('Computed full name:', u.full_name)",
        "Using __post_init__ to compute derived fields and enforce attribute validation.",
        "The compiled `__init__` function emits `self.__post_init__()` if the method exists on the class. Fields with `init=False` are not included in the `__init__` parameter list, allowing `__post_init__` to assign them.",
        "Validating entity constraints, generating cryptographic hashes, and configuring internal connection handles during entity construction.",
        ["How do you define a dataclass field that is initialized only in `__post_init__` and not in `__init__`?", "How does `__post_init__` work in frozen dataclasses?"],
        ["Attempting direct assignment (`self.x = y`) inside `__post_init__` on a `frozen=True` dataclass (requires `object.__setattr__`).", "Forgetting `init=False` on computed fields, forcing callers to supply dummy values."],
        "Frozen tip: In frozen dataclasses, use `object.__setattr__(self, 'attr', value)` inside `__post_init__`.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/dataclasses.html#post-init-processing"]
    ),

    # PY-INT-192
    (
        "PY-INT-192",
        "Dynamic Class Creation with types.new_class",
        "`types.new_class(name, bases, kwds, exec_body)` dynamically constructs classes at runtime while ensuring proper metaclass calculation and invoking `__prepare__` hooks correctly.",
        "While calling `type(name, bases, dict)` creates simple classes dynamically, it fails to handle advanced class creation mechanics: it cannot resolve metaclass conflicts across multiple base classes, skips `__prepare__` hooks, and ignores keyword arguments like `metaclass=...`. The `types.new_class()` function is the official, complete standard library mechanism for creating classes dynamically, exactly mirroring the behavior of the CPython `class` statement.",
        "import types\n\ndef populate_class(ns):\n    ns['version'] = '2.0'\n    ns['greet'] = lambda self: f'System v{self.version}'\n\n# Dynamically construct class with full metaclass resolution\nServiceClass = types.new_class('DynamicService', (), {}, populate_class)\n\ns = ServiceClass()\nprint('Dynamic class invocation:', s.greet())",
        "Creating a fully compliant dynamic class using types.new_class and a namespace population callback.",
        "`types.new_class()` resolves the most derived metaclass using `_PyType_CalculateMetaclass()`, calls `__prepare__`, executes the callback to populate the namespace, and invokes `metaclass.__new__`.",
        "Building dynamic ORM models from database schemas at runtime, deserializing protobuf/thrift schemas into live Python classes, and plugin engines.",
        ["What advantages does `types.new_class` have over direct `type(name, bases, dict)`?", "What role does the `exec_body` callback play in `types.new_class`?"],
        ["Using raw `type()` when base classes employ custom metaclasses (triggers metaclass conflict errors).", "Populating namespaces after class creation instead of inside the `exec_body` callback."],
        "Recommendation: Always use `types.new_class()` instead of `type()` when programmatically synthesizing classes with bases or metaclasses.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/types.html#types.new_class"]
    ),

    # PY-INT-193
    (
        "PY-INT-193",
        "Read-Only Dictionary Views with MappingProxyType",
        "`types.MappingProxyType` creates an immutable, read-only proxy view of a dictionary that reflects changes in the underlying dictionary but prevents direct modification.",
        "In Python, returning an internal dictionary (`return self._config`) exposes internal state to external mutation. Copying the dictionary (`return self._config.copy()`) protects the state but allocates new memory on every access and does not reflect future internal updates. `types.MappingProxyType(dict)` provides a zero-allocation read-only wrapper: clients can read keys with standard dictionary syntax, but any attempt to mutate keys (`proxy['key'] = val`) raises `TypeError`.",
        "from types import MappingProxyType\n\n_internal_state = {'api_key': 'secret_123', 'timeout': 30}\n# Expose read-only proxy\npublic_view = MappingProxyType(_internal_state)\n\nprint('Read via proxy:', public_view['api_key'])\n\ntry:\n    public_view['timeout'] = 60  # Raises TypeError\nexcept TypeError as e:\n    print(f'Mutation blocked as expected: {e}')\n\n# Underlying updates are immediately reflected in proxy without copying\n_internal_state['timeout'] = 45\nprint('Updated value reflected in proxy:', public_view['timeout'])",
        "Demonstrating read-only dictionary encapsulation using MappingProxyType.",
        "In `descrobject.c`, `mappingproxy` implements mapping slots (`mp_subscript`) by forwarding read calls directly to the underlying `PyDictObject`. It leaves mutation slots (`mp_ass_subscript`) null, guaranteeing immutability.",
        "Protecting internal module configurations, class attribute dictionaries (`__dict__` is exposed as a `mappingproxy`), and shared caches.",
        ["What is the difference between `MappingProxyType(d)` and `d.copy()`?", "Does `MappingProxyType` prevent modifying mutable objects *stored inside* the dictionary?"],
        ["Assuming `MappingProxyType` makes nested objects immutable (shallow protection only).", "Copying large dictionaries repeatedly instead of returning a lightweight `MappingProxyType`."],
        "Interview insight: Python uses `MappingProxyType` internally to expose `cls.__dict__` safely without allowing accidental mutation.",
        ["[Data Types & Collections](data-types-and-collections.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/types.html#types.MappingProxyType"]
    ),

    # PY-INT-194
    (
        "PY-INT-194",
        "Duck-Typed Subclassing with __subclasshook__",
        "`__subclasshook__(cls, subclass)` allows an Abstract Base Class to dynamically customize `issubclass()` and `isinstance()` checks based purely on method inspection without explicit inheritance or registration.",
        "Normally, `issubclass(Candidate, ABC)` is true only if `Candidate` explicitly inherits from `ABC` or was registered via `ABC.register()`. By implementing `__subclasshook__` on an ABC, developers can define custom duck-typing rules: if the candidate class defines specific required method names anywhere in its MRO, `issubclass()` returns `True` automatically. This is how Python's built-in `collections.abc.Iterable` and `Sized` recognize any class with `__iter__` or `__len__` as instances without explicit inheritance.",
        "from abc import ABCMeta\n\nclass SizedInterface(metaclass=ABCMeta):\n    @classmethod\n    def __subclasshook__(cls, subclass):\n        if cls is SizedInterface:\n            # If subclass has __len__ anywhere in its MRO, it is a virtual subclass\n            if any('__len__' in B.__dict__ for B in subclass.__mro__):\n                return True\n        return NotImplemented\n\nclass CustomCollection:\n    def __len__(self):\n        return 10\n\n# Automatically satisfies issubclass without explicit inheritance!\nprint('Is CustomCollection a subclass of SizedInterface?', issubclass(CustomCollection, SizedInterface))\nprint('Is instance recognized?', isinstance(CustomCollection(), SizedInterface))",
        "Implementing a dynamic duck-typed interface using __subclasshook__.",
        "`ABCMeta.__subclasscheck__` calls `__subclasshook__`. If it returns `True` or `False`, that decision is final; if it returns `NotImplemented`, standard inheritance checking resumes.",
        "Authoring framework protocol checks that recognize third-party classes adhering to interface conventions without requiring decorators or registrations.",
        ["What must `__subclasshook__` return if it cannot determine subclass relationship?", "Why must `__subclasshook__` inspect `subclass.__mro__` rather than just `subclass.__dict__`?"],
        ["Returning `False` instead of `NotImplemented` from `__subclasshook__`, which prevents standard subclassing from working.", "Forgetting that `__subclasshook__` must be a `@classmethod`."],
        "Critical rule: Return `NotImplemented` from `__subclasshook__` when your check does not match, so standard inheritance checks can proceed.",
        ["[OOP Concepts](oop.md)", "[Python Fundamentals](fundamentals.md)"],
        ["https://docs.python.org/3/library/abc.html#abc.ABCMeta.__subclasshook__"]
    ),

    # PY-INT-195
    (
        "PY-INT-195",
        "Custom Import Hooks with sys.meta_path",
        "`sys.meta_path` is a list of meta path finder objects searched by Python during module imports; appending custom finders allows intercepting, redirecting, or virtualizing module imports.",
        "When an `import foo` statement executes, CPython traverses `sys.meta_path`. Each finder's `find_spec(fullname, path, target)` method is called. Built-in finders resolve built-in modules, frozen modules, and filesystem path modules. By prepending a custom finder to `sys.meta_path`, developers can intercept module loading: importing modules directly from remote HTTP URLs, loading encrypted `.pyc` files from memory, or dynamically generating synthetic modules on the fly.",
        "import sys\nfrom importlib.abc import MetaPathFinder\nfrom importlib.machinery import ModuleSpec\nimport types\n\nclass VirtualModuleFinder(MetaPathFinder):\n    def find_spec(self, fullname, path, target=None):\n        if fullname == 'virtual_config':\n            # Synthesize module spec on the fly\n            mod = types.ModuleType(fullname)\n            mod.API_KEY = 'DYNAMICALLY_LOADED_KEY'\n            spec = ModuleSpec(fullname, loader=None)\n            spec.loader = types.SimpleNamespace(create_module=lambda s: mod, exec_module=lambda m: None)\n            return spec\n        return None\n\nsys.meta_path.insert(0, VirtualModuleFinder())\n\nimport virtual_config\nprint('Imported synthetic module value:', virtual_config.API_KEY)\n\nsys.meta_path.pop(0)  # Cleanup",
        "Intercepting import statements using a custom MetaPathFinder on sys.meta_path.",
        "CPython's `PyImport_ImportModuleLevelObject()` iterates through `sys.meta_path`. If a finder returns a valid `ModuleSpec`, Python uses its loader to initialize the module and caches it in `sys.modules`.",
        "Plugin architectures, loading modules from encrypted containers or database blobs, and implementing multi-tenant virtual sandboxes.",
        ["What are the default finders present in `sys.meta_path`?", "What is the difference between `sys.meta_path` and `sys.path_hooks`?"],
        ["Returning `False` from `find_spec` instead of `None` when a module is not found.", "Forgetting to register loaded modules in `sys.modules`, which causes repeated re-importing."],
        "Convention: Return `None` from `find_spec()` if your finder does not handle the requested module.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/sys.html#sys.meta_path"]
    ),

    # PY-INT-196
    (
        "PY-INT-196",
        "Module Finders vs Module Loaders in importlib",
        "A Module Finder determines whether a module exists and returns a `ModuleSpec`, whereas a Module Loader uses that `ModuleSpec` to create the module object and execute its code.",
        "Python's import system separates discovery from execution: 1) Finder (`MetaPathFinder`): Implements `find_spec(fullname, path, target)`. It searches locations (filesystems, network, zip archives) and, if found, returns a `ModuleSpec` describing the module's origin and loader. 2) Loader (`Loader`): Implements `create_module(spec)` (allocates the `types.ModuleType` object) and `exec_module(module)` (executes the compiled bytecode inside the module's `__dict__`). Separating finding from loading enables clean caching and modular import customization.",
        "from importlib.machinery import ModuleSpec\nimport types\n\n# Demonstration of loader responsibilities\nclass StringLoader:\n    def __init__(self, code_str: str):\n        self.code_str = code_str\n        \n    def create_module(self, spec):\n        return None  # Default module creation\n        \n    def exec_module(self, module):\n        exec(self.code_str, module.__dict__)\n\nspec = ModuleSpec('dynamic_math', StringLoader('def add(a, b): return a + b'))\nmod = types.ModuleType(spec.name)\nspec.loader.exec_module(mod)\n\nprint('Dynamically loaded function result:', mod.add(10, 20))",
        "Demonstrating ModuleSpec and Loader executing synthetic module code.",
        "The import machinery defined in PEP 451 unifies finders and loaders under `ModuleSpec`. `sys.modules` caches the module immediately before `exec_module` runs to handle circular imports safely.",
        "Building hot-reloading development servers, dynamic plugin systems, and serverless execution environments that run Python code from memory strings.",
        ["Why does CPython insert the module into `sys.modules` *before* calling `exec_module`?", "What does returning `None` from `create_module` signify?"],
        ["Implementing legacy `find_module` and `load_module` instead of modern `find_spec` and `exec_module` (PEP 451).", "Failing to handle circular imports in custom loaders."],
        "Emphasize: Use modern PEP 451 `find_spec` and `exec_module` APIs, not legacy Python 2/3.3 `find_module`/`load_module`.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://peps.python.org/pep-0451/"]
    ),

    # PY-INT-197
    (
        "PY-INT-197",
        "importlib.reload() Mechanics and Caveats",
        "`importlib.reload(module)` re-reads and re-executes a module's source code in-place, updating its existing module dictionary while leaving existing instance references and imported bindings pointing to old objects.",
        "During live development or REPL sessions, `importlib.reload(mod)` reloads a module without restarting Python. It re-parses and re-executes the file, updating `mod.__dict__` in-place. However, it has significant caveats: 1) Any client code that previously executed `from module import ClassName` retains pointers to the *old* class object. 2) Instances created before the reload remain instances of the old class (`isinstance(old_instance, reloaded_module.ClassName)` evaluates to `False`). 3) Removed attributes in the new source code are not deleted from the module dictionary.",
        "import importlib\nimport math\n\n# Reloading an existing module\nreloaded_math = importlib.reload(math)\nprint('Math reloaded successfully:', reloaded_math.pi)\nprint('Caveat: Old object references in other namespaces are NOT updated by reload().')",
        "Demonstrating module reloading via importlib.reload().",
        "`reload()` does not wipe `module.__dict__`; it executes the new code inside the existing dictionary, overwriting existing keys and adding new ones. Old classes and functions persist if renamed or deleted.",
        "Hot-reloading web development servers (Uvicorn `--reload`, Django runserver) detecting code edits and refreshing handlers without restarting worker processes.",
        ["Why does `isinstance(old_obj, reloaded_mod.Class)` evaluate to `False` after a reload?", "What happens to variables that were deleted from the source file upon reload?"],
        ["Relying on `importlib.reload()` for production hot-patching without restarting processes.", "Assuming `from mod import func` updates automatically when `mod` is reloaded (it does not)."],
        "Warning: Never use `importlib.reload()` as a substitute for restarting production services; reference fragmentation will cause subtle bugs.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/importlib.html#importlib.reload"]
    ),

    # PY-INT-198
    (
        "PY-INT-198",
        "ctypes Foreign Function Interface",
        "`ctypes` is Python's built-in foreign function library that loads native C dynamic shared libraries (`.so`, `.dll`, `.dylib`) and invokes C functions using explicit argument and return type definitions.",
        "`ctypes` provides direct C interoperability without compilation: 1) `ctypes.CDLL(path)` loads a shared library. 2) Function signatures must be declared using `func.argtypes = [c_int, c_char_p]` and `func.restype = c_double` to ensure Python data types are converted to matching C binary formats. 3) Calling the function executes native C machine code directly. If `argtypes` is omitted, `ctypes` defaults arguments to integers, which risks memory corruption or segmentation faults when passing pointers.",
        "import ctypes\nimport sys\n\n# Accessing standard C library across platforms\nif sys.platform == 'win32':\n    libc = ctypes.cdll.msvcrt\nelse:\n    libc = ctypes.CDLL('libc.so.6')\n\n# Configure function signature\nlibc.puts.argtypes = [ctypes.c_char_p]\nlibc.puts.restype = ctypes.c_int\n\n# Invoke native C function directly\nresult = libc.puts(b'Hello from native C via ctypes!')\nprint('C puts returned status code:', result)",
        "Loading standard C library and invoking puts via ctypes with strict argtypes.",
        "`ctypes` uses `libffi` under the hood to construct native CPU calling conventions (cdecl/stdcall). Python integers, floats, and bytes are converted into raw memory buffers corresponding to C scalar types.",
        "Interfacing with system hardware drivers, cryptographic libraries, or legacy shared libraries where compiling a full C extension is undesirable.",
        ["Why is setting `argtypes` and `restype` mandatory for stability in ctypes?", "What is the difference between `ctypes.CDLL` and `ctypes.WinDLL` on Windows?"],
        ["Passing Python strings directly to `c_char_p` without encoding to bytes (`b'string'`).", "Omitting `restype` on 64-bit systems when a function returns a 64-bit pointer (defaults to 32-bit int, truncating the pointer address)."],
        "Crucial safety rule: Always explicitly declare `argtypes` and `restype` on all `ctypes` functions to avoid memory corruption.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://docs.python.org/3/library/ctypes.html"]
    ),

    # PY-INT-199
    (
        "PY-INT-199",
        "CFFI vs ctypes Architecture",
        "CFFI parses raw C header declarations (`cdef`) directly to generate type-safe, compiled C extensions (API mode) that run significantly faster than `ctypes`'s dynamic runtime reflection.",
        "While `ctypes` requires manually translating C struct definitions into Python classes (`class MyStruct(ctypes.Structure):`), CFFI (C Foreign Function Interface) allows pasting standard C declarations directly: `ffi.cdef('int add(int, int);')`. Furthermore, CFFI operates in two modes: 1) ABI Mode: Dynamic runtime reflection similar to `ctypes`. 2) API Mode (Out-of-Line): Generates a C file at build time that is compiled by GCC/Clang into a native C extension. This eliminates runtime `libffi` call overhead, verifies C struct alignments at compile time, and achieves 5x-10x faster calling performance than `ctypes`.",
        "import sys\n\n# Conceptual comparison between CFFI and ctypes:\n# CFFI parses raw C headers directly:\n# ffi.cdef('int calculate_hash(const char *data, size_t len);')\n# lib = ffi.dlopen('libcrypto.so')\nprint('CFFI parses C headers natively and compiles to high-performance C extensions in API mode.')",
        "Conceptual overview of CFFI direct C header parsing.",
        "In API mode, CFFI generates C wrapper code that includes the library's official headers (`#include <crypto.h>`), allowing the C compiler to verify macro constants, struct field alignments, and type definitions automatically.",
        "Writing production-grade Python wrappers for cryptographic libraries (e.g. `cryptography` package uses CFFI), high-speed networking engines, and multimedia decoders.",
        ["What is the difference between CFFI ABI mode and API mode?", "Why does CFFI API mode provide greater stability across OS updates?"],
        ["Using `ctypes` for performance-critical inner loops where call overhead dominates.", "Manually hard-coding C struct padding and alignment offsets in `ctypes` instead of using CFFI."],
        "Industry standard: Python's `cryptography` library switched from `ctypes` to CFFI to eliminate architecture-specific struct layout bugs.",
        ["[Python Fundamentals](fundamentals.md)", "[OOP Concepts](oop.md)"],
        ["https://cffi.readthedocs.io/"]
    ),

    # PY-INT-200
    (
        "PY-INT-200",
        "Dual-Mode Sync and Async Decorators",
        "A dual-mode decorator inspects whether the wrapped target is a coroutine function using `inspect.iscoroutinefunction()`, dispatching to an async wrapper or a synchronous wrapper accordingly.",
        "In modern Python libraries supporting both synchronous (Flask/Django) and asynchronous (FastAPI/Starlette) execution, writing separate `@log_sync` and `@log_async` decorators is repetitive and poor API design. A dual-mode decorator inspects the target callable at decoration time using `inspect.iscoroutinefunction(func)`. If the target is an async coroutine, it returns an `async def wrapper(*args, **kwargs)` that awaits the result; otherwise, it returns a standard `def wrapper(*args, **kwargs)` that executes synchronously.",
        "import asyncio\nimport functools\nimport inspect\n\ndef universal_logger(func):\n    if inspect.iscoroutinefunction(func):\n        @functools.wraps(func)\n        async def async_wrapper(*args, **kwargs):\n            print(f'[ASYNC] Running {func.__name__}')\n            return await func(*args, **kwargs)\n        return async_wrapper\n    else:\n        @functools.wraps(func)\n        def sync_wrapper(*args, **kwargs):\n            print(f'[SYNC] Running {func.__name__}')\n            return func(*args, **kwargs)\n        return sync_wrapper\n\n@universal_logger\ndef sync_add(a: int, b: int) -> int:\n    return a + b\n\n@universal_logger\nasync def async_add(a: int, b: int) -> int:\n    return a + b\n\nprint('Sync result:', sync_add(10, 20))\nprint('Async result:', asyncio.run(async_add(10, 20)))",
        "Implementing a dual-mode universal decorator that supports both sync functions and async coroutines.",
        "`inspect.iscoroutinefunction(func)` inspects the `CO_COROUTINE` bit flag on `func.__code__.co_flags`. Checking this at decoration time ensures zero overhead during repeated runtime invocations.",
        "Authoring cross-framework middleware, caching decorators, database transaction retry handlers, and metrics tracking libraries.",
        ["Why must the check `inspect.iscoroutinefunction` be executed at decoration time rather than call time?", "How does `functools.wraps` preserve function metadata across both wrappers?"],
        ["Awaiting a synchronous function or calling an async coroutine without `await` inside the wrapper.", "Checking `asyncio.iscoroutine(func)` instead of `inspect.iscoroutinefunction(func)` (the former checks instances; the latter checks functions)."],
        "Crucial check: Use `inspect.iscoroutinefunction(func)` on the function object, not `asyncio.iscoroutine()`.",
        ["[Decorators & Generators](decorators-and-generators.md)", "[Concurrency & Parallelism](concurrency-and-parallelism.md)"],
        ["https://docs.python.org/3/library/inspect.html#inspect.iscoroutinefunction"]
    )
]
