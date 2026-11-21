# Python Object-Oriented Programming & Metaprogramming Interview Questions

Comprehensive technical interview questions covering classes, inheritance, MRO / C3 linearization, polymorphism, encapsulation, dunder methods, ABCs, dataclasses, descriptors, metaclasses, and CPython object model internals.

## Table of Contents
- [Basic Level (25 Questions)](#basic-level)
  - [PY-BAS-051: What is Object-Oriented Programming (OOP) in Python and what are its four core pillars?](#py-bas-051-what-is-object-oriented-programming-oop-in-python-and-what-are-its-four-core-pillars)
  - [PY-BAS-052: What is the difference between a class and an instance (object) in Python?](#py-bas-052-what-is-the-difference-between-a-class-and-an-instance-object-in-python)
  - [PY-BAS-053: What is '__init__' and how does it differ from a constructor in C++ or Java?](#py-bas-053-what-is-'__init__'-and-how-does-it-differ-from-a-constructor-in-c++-or-java)
  - [PY-BAS-054: Why must methods explicitly receive 'self' as their first parameter in Python?](#py-bas-054-why-must-methods-explicitly-receive-'self'-as-their-first-parameter-in-python)
  - [PY-BAS-055: What is the difference between class attributes and instance attributes?](#py-bas-055-what-is-the-difference-between-class-attributes-and-instance-attributes)
  - [PY-BAS-056: How does single inheritance work in Python and how do you call the parent method with 'super()'?](#py-bas-056-how-does-single-inheritance-work-in-python-and-how-do-you-call-the-parent-method-with-'super')
  - [PY-BAS-057: How does encapsulation work in Python (public, protected '_', private '__' name mangling)?](#py-bas-057-how-does-encapsulation-work-in-python-public-protected-'_'-private-'__'-name-mangling)
  - [PY-BAS-058: What is polymorphism in Python and how does duck typing achieve it without formal interfaces?](#py-bas-058-what-is-polymorphism-in-python-and-how-does-duck-typing-achieve-it-without-formal-interfaces)
  - [PY-BAS-059: What is the difference between '@staticmethod' and '@classmethod'?](#py-bas-059-what-is-the-difference-between-'@staticmethod'-and-'@classmethod')
  - [PY-BAS-060: What is the '@property' decorator and how does it implement getters, setters, and deleters?](#py-bas-060-what-is-the-'@property'-decorator-and-how-does-it-implement-getters-setters-and-deleters)
  - [PY-BAS-061: What is the difference between '__str__' and '__repr__' and when should each be implemented?](#py-bas-061-what-is-the-difference-between-'__str__'-and-'__repr__'-and-when-should-each-be-implemented)
  - [PY-BAS-062: What are dunder (double underscore) / magic methods and why are they used?](#py-bas-062-what-are-dunder-double-underscore--magic-methods-and-why-are-they-used)
  - [PY-BAS-063: What does 'isinstance()' do and why is it preferred over 'type(obj) is Class'?](#py-bas-063-what-does-'isinstance'-do-and-why-is-it-preferred-over-'typeobj-is-class')
  - [PY-BAS-064: What does 'issubclass()' do and how does it evaluate class hierarchies?](#py-bas-064-what-does-'issubclass'-do-and-how-does-it-evaluate-class-hierarchies)
  - [PY-BAS-065: How does operator overloading work in Python (e.g. '__add__', '__sub__', '__mul__')?](#py-bas-065-how-does-operator-overloading-work-in-python-e.g.-'__add__'-'__sub__'-'__mul__')
  - [PY-BAS-066: How do comparison dunder methods work ('__eq__', '__lt__', etc.) and what is '@functools.total_ordering'?](#py-bas-066-how-do-comparison-dunder-methods-work-'__eq__'-'__lt__'-etc.-and-what-is-'@functools.total_ordering')
  - [PY-BAS-067: What is '__len__' and '__getitem__' and how do they make a custom class act like a sequence?](#py-bas-067-what-is-'__len__'-and-'__getitem__'-and-how-do-they-make-a-custom-class-act-like-a-sequence)
  - [PY-BAS-068: What is '__call__' and how does it make an instance callable like a function?](#py-bas-068-what-is-'__call__'-and-how-does-it-make-an-instance-callable-like-a-function)
  - [PY-BAS-069: What is composition vs inheritance, and why is 'favor composition over inheritance' recommended in Python?](#py-bas-069-what-is-composition-vs-inheritance-and-why-is-'favor-composition-over-inheritance'-recommended-in-python)
  - [PY-BAS-070: What are Python dataclasses ('@dataclass') and what boilerplate do they eliminate?](#py-bas-070-what-are-python-dataclasses-'@dataclass'-and-what-boilerplate-do-they-eliminate)
  - [PY-BAS-071: How do default attribute values and field defaults work in dataclasses ('field(default_factory=...)')?](#py-bas-071-how-do-default-attribute-values-and-field-defaults-work-in-dataclasses-'fielddefault_factory=...')
  - [PY-BAS-072: What is '__dict__' on an object and how does attribute lookup interact with it?](#py-bas-072-what-is-'__dict__'-on-an-object-and-how-does-attribute-lookup-interact-with-it)
  - [PY-BAS-073: What happens when an attribute is not found: how does '__getattr__' differ from '__getattribute__'?](#py-bas-073-what-happens-when-an-attribute-is-not-found-how-does-'__getattr__'-differ-from-'__getattribute__')
  - [PY-BAS-074: What is the 'del' statement when applied to an attribute ('del obj.attr') and what dunder method does it trigger?](#py-bas-074-what-is-the-'del'-statement-when-applied-to-an-attribute-'del-obj.attr'-and-what-dunder-method-does-it-trigger)
  - [PY-BAS-075: What is '__slots__' and how does it reduce memory consumption for millions of instances?](#py-bas-075-what-is-'__slots__'-and-how-does-it-reduce-memory-consumption-for-millions-of-instances)
- [Intermediate Level (25 Questions)](#intermediate-level)
  - [PY-INT-051: What is Multiple Inheritance in Python and what is the 'Diamond Problem'?](#py-int-051-what-is-multiple-inheritance-in-python-and-what-is-the-'diamond-problem')
  - [PY-INT-052: How does Method Resolution Order (MRO) work and what is the C3 Linearization algorithm?](#py-int-052-how-does-method-resolution-order-mro-work-and-what-is-the-c3-linearization-algorithm)
  - [PY-INT-053: How does 'super()' actually work under the hood (bound proxy, cooperative multiple inheritance)?](#py-int-053-how-does-'super'-actually-work-under-the-hood-bound-proxy-cooperative-multiple-inheritance)
  - [PY-INT-054: What are Python Descriptors, and what is the difference between data descriptors and non-data descriptors?](#py-int-054-what-are-python-descriptors-and-what-is-the-difference-between-data-descriptors-and-non-data-descriptors)
  - [PY-INT-055: How are '@property', '@classmethod', and regular functions implemented as descriptors?](#py-int-055-how-are-'@property'-'@classmethod'-and-regular-functions-implemented-as-descriptors)
  - [PY-INT-056: What is '__new__' vs '__init__' and how does '__new__' control instance creation (Singleton, immutable subclasses)?](#py-int-056-what-is-'__new__'-vs-'__init__'-and-how-does-'__new__'-control-instance-creation-singleton-immutable-subclasses)
  - [PY-INT-057: What are Abstract Base Classes ('abc.ABC', '@abstractmethod') and how do they enforce interfaces at instantiation time?](#py-int-057-what-are-abstract-base-classes-'abc.abc'-'@abstractmethod'-and-how-do-they-enforce-interfaces-at-instantiation-time)
  - [PY-INT-058: What is virtual subclass registration ('ABC.register()') and structural subtyping via '__subclasshook__'?](#py-int-058-what-is-virtual-subclass-registration-'abc.register'-and-structural-subtyping-via-'__subclasshook__')
  - [PY-INT-059: What are Protocol classes in 'typing.Protocol' (PEP 544) and how do they implement static duck typing?](#py-int-059-what-are-protocol-classes-in-'typing.protocol'-pep-544-and-how-do-they-implement-static-duck-typing)
  - [PY-INT-060: What is '__init_subclass__' (PEP 487) and how does it provide class customization without metaclasses?](#py-int-060-what-is-'__init_subclass__'-pep-487-and-how-does-it-provide-class-customization-without-metaclasses)
  - [PY-INT-061: What is '__set_name__' (PEP 487) and how does it allow descriptors to capture their attribute names automatically?](#py-int-061-what-is-'__set_name__'-pep-487-and-how-does-it-allow-descriptors-to-capture-their-attribute-names-automatically)
  - [PY-INT-062: How do frozen dataclasses ('@dataclass(frozen=True)') achieve immutability and hashability?](#py-int-062-how-do-frozen-dataclasses-'@dataclassfrozen=true'-achieve-immutability-and-hashability)
  - [PY-INT-063: What is '__post_init__' in dataclasses and how is it used for validation or computed attributes?](#py-int-063-what-is-'__post_init__'-in-dataclasses-and-how-is-it-used-for-validation-or-computed-attributes)
  - [PY-INT-064: How does Python implement dynamic attribute delegation (Proxy pattern) using '__getattr__'?](#py-int-064-how-does-python-implement-dynamic-attribute-delegation-proxy-pattern-using-'__getattr__')
  - [PY-INT-065: What is the difference between shallow copy and deep copy on custom classes, and how do '__copy__' and '__deepcopy__' work?](#py-int-065-what-is-the-difference-between-shallow-copy-and-deep-copy-on-custom-classes-and-how-do-'__copy__'-and-'__deepcopy__'-work)
  - [PY-INT-066: How do context managers ('__enter__' and '__exit__') work as class methods, and how do they handle exceptions?](#py-int-066-how-do-context-managers-'__enter__'-and-'__exit__'-work-as-class-methods-and-how-do-they-handle-exceptions)
  - [PY-INT-067: What is the difference between '@functools.cached_property' and '@property'?](#py-int-067-what-is-the-difference-between-'@functools.cached_property'-and-'@property')
  - [PY-INT-068: How does attribute lookup order work in Python (Data descriptor -> Instance __dict__ -> Non-data descriptor -> Class __dict__ -> Base classes -> __getattr__)?](#py-int-068-how-does-attribute-lookup-order-work-in-python-data-descriptor-->-instance-__dict__-->-non-data-descriptor-->-class-__dict__-->-base-classes-->-__getattr__)
  - [PY-INT-069: How can you implement the Singleton pattern safely in Python using '__new__', module caching, or decorators?](#py-int-069-how-can-you-implement-the-singleton-pattern-safely-in-python-using-'__new__'-module-caching-or-decorators)
  - [PY-INT-070: What is the Factory pattern in Python and how do class methods provide alternative constructors?](#py-int-070-what-is-the-factory-pattern-in-python-and-how-do-class-methods-provide-alternative-constructors)
  - [PY-INT-071: What is monkey-patching in Python, how does it work, and what are its production risks?](#py-int-071-what-is-monkey-patching-in-python-how-does-it-work-and-what-are-its-production-risks)
  - [PY-INT-072: How does 'hasattr()' work internally, and why did it catch unexpected exceptions in older Python versions?](#py-int-072-how-does-'hasattr'-work-internally-and-why-did-it-catch-unexpected-exceptions-in-older-python-versions)
  - [PY-INT-073: How do you implement custom container classes adhering to 'collections.abc.Sequence' or 'collections.abc.MutableMapping'?](#py-int-073-how-do-you-implement-custom-container-classes-adhering-to-'collections.abc.sequence'-or-'collections.abc.mutablemapping')
  - [PY-INT-074: What is the Borg / Monostate pattern in Python and how does it differ from a Singleton?](#py-int-074-what-is-the-borg--monostate-pattern-in-python-and-how-does-it-differ-from-a-singleton)
  - [PY-INT-075: How does 'weakref.finalize' provide safer cleanup for class instances compared to '__del__'?](#py-int-075-how-does-'weakref.finalize'-provide-safer-cleanup-for-class-instances-compared-to-'__del__')
- [Advanced Level (25 Questions)](#advanced-level)
  - [PY-ADV-051: What is a Metaclass in Python, how does 'type' act as the default metaclass, and what is the class instantiation lifecycle?](#py-adv-051-what-is-a-metaclass-in-python-how-does-'type'-act-as-the-default-metaclass-and-what-is-the-class-instantiation-lifecycle)
  - [PY-ADV-052: How does C3 Linearization mathematically resolve inconsistent inheritance hierarchies, and what causes an 'Inconsistent Hierarchy (MRO)' TypeError?](#py-adv-052-how-does-c3-linearization-mathematically-resolve-inconsistent-inheritance-hierarchies-and-what-causes-an-'inconsistent-hierarchy-mro'-typeerror)
  - [PY-ADV-053: How does CPython implement attribute lookup at the C level ('_PyObject_GenericGetAttrWithDict', 'tp_getattro', 'tp_descr_get')?](#py-adv-053-how-does-cpython-implement-attribute-lookup-at-the-c-level-'_pyobject_genericgetattrwithdict'-'tp_getattro'-'tp_descr_get')
  - [PY-ADV-054: How do you build an ORM-style declarative model system using metaclasses or '__init_subclass__'?](#py-adv-054-how-do-you-build-an-orm-style-declarative-model-system-using-metaclasses-or-'__init_subclass__')
  - [PY-ADV-055: What is the exact C-level mechanism of '__slots__': how does it replace '__dict__' with member descriptors and what are the inheritance pitfalls?](#py-adv-055-what-is-the-exact-c-level-mechanism-of-'__slots__'-how-does-it-replace-'__dict__'-with-member-descriptors-and-what-are-the-inheritance-pitfalls)
  - [PY-ADV-056: How do Split-Table Dictionaries (PEP 412) optimize memory for class instances sharing identical attribute keys?](#py-adv-056-how-do-split-table-dictionaries-pep-412-optimize-memory-for-class-instances-sharing-identical-attribute-keys)
  - [PY-ADV-057: How does CPython implement bound methods vs unbound methods ('PyMethodDescr_Type', 'PyMethod_Type'), and how does method caching optimize access?](#py-adv-057-how-does-cpython-implement-bound-methods-vs-unbound-methods-'pymethoddescr_type'-'pymethod_type'-and-how-does-method-caching-optimize-access)
  - [PY-ADV-058: What are the risks and mechanics of '__del__' (finalizers), resurrection of objects, and why '__del__' historically interfered with cyclic garbage collection?](#py-adv-058-what-are-the-risks-and-mechanics-of-'__del__'-finalizers-resurrection-of-objects-and-why-'__del__'-historically-interfered-with-cyclic-garbage-collection)
  - [PY-ADV-059: How do you implement a stateful, thread-safe Object Pool in Python for expensive resources (e.g. database connections, socket handles)?](#py-adv-059-how-do-you-implement-a-stateful-thread-safe-object-pool-in-python-for-expensive-resources-e.g.-database-connections-socket-handles)
  - [PY-ADV-060: How does dynamic class generation with 'type(name, bases, dict)' work, and how can classes be constructed programmatically at runtime?](#py-adv-060-how-does-dynamic-class-generation-with-'typename-bases-dict'-work-and-how-can-classes-be-constructed-programmatically-at-runtime)
  - [PY-ADV-061: What is '__prepare__' in metaclasses and how does it enable class definitions with custom namespaces?](#py-adv-061-what-is-'__prepare__'-in-metaclasses-and-how-does-it-enable-class-definitions-with-custom-namespaces)
  - [PY-ADV-062: How does Python 3.10+ match-case class pattern matching interact with '__match_args__' and positional pattern decomposition?](#py-adv-062-how-does-python-3.10+-match-case-class-pattern-matching-interact-with-'__match_args__'-and-positional-pattern-decomposition)
  - [PY-ADV-063: How do you implement a Dependency Injection (DI) container with autowiring using Python type hints and class introspection?](#py-adv-063-how-do-you-implement-a-dependency-injection-di-container-with-autowiring-using-python-type-hints-and-class-introspection)
  - [PY-ADV-064: What is the Visitor pattern in Python and how does 'ast.NodeVisitor' / 'ast.NodeTransformer' use dynamic method dispatch?](#py-adv-064-what-is-the-visitor-pattern-in-python-and-how-does-'ast.nodevisitor'--'ast.nodetransformer'-use-dynamic-method-dispatch)
  - [PY-ADV-065: How can you intercept and instrument all method calls on a class dynamically using metaclasses or class decorators (AOP)?](#py-adv-065-how-can-you-intercept-and-instrument-all-method-calls-on-a-class-dynamically-using-metaclasses-or-class-decorators-aop)
  - [PY-ADV-066: How do abstract properties and abstract class methods interact in ABCs, and how does 'abc.ABCMeta' validate them?](#py-adv-066-how-do-abstract-properties-and-abstract-class-methods-interact-in-abcs-and-how-does-'abc.abcmeta'-validate-them)
  - [PY-ADV-067: What is the internal memory difference between standard class instances, '@dataclass(slots=True)', and 'typing.NamedTuple'?](#py-adv-067-what-is-the-internal-memory-difference-between-standard-class-instances-'@dataclassslots=true'-and-'typing.namedtuple')
  - [PY-ADV-068: How do you implement a custom descriptor that enforces runtime type validation and database constraints?](#py-adv-068-how-do-you-implement-a-custom-descriptor-that-enforces-runtime-type-validation-and-database-constraints)
  - [PY-ADV-069: What are the architectural trade-offs between Metaclasses vs '__init_subclass__' vs Class Decorators?](#py-adv-069-what-are-the-architectural-trade-offs-between-metaclasses-vs-'__init_subclass__'-vs-class-decorators)
  - [PY-ADV-070: How does Python handle multiple inheritance when mixing cooperative 'super()' classes with non-cooperative legacy third-party classes?](#py-adv-070-how-does-python-handle-multiple-inheritance-when-mixing-cooperative-'super'-classes-with-non-cooperative-legacy-third-party-classes)
  - [PY-ADV-071: How do you prevent subclassing of a class (final classes) using 'typing.final' and runtime metaclass enforcement?](#py-adv-071-how-do-you-prevent-subclassing-of-a-class-final-classes-using-'typing.final'-and-runtime-metaclass-enforcement)
  - [PY-ADV-072: What is the Flyweight design pattern and how do you implement it in Python using '__new__' and weak references to minimize memory?](#py-adv-072-what-is-the-flyweight-design-pattern-and-how-do-you-implement-it-in-python-using-'__new__'-and-weak-references-to-minimize-memory)
  - [PY-ADV-073: How does CPython's specialized bytecode interpreter (PEP 659 / PEP 709) optimize method calls via inline caches?](#py-adv-073-how-does-cpython's-specialized-bytecode-interpreter-pep-659--pep-709-optimize-method-calls-via-inline-caches)
  - [PY-ADV-074: How do you implement a distributed Event Bus / Observer pattern with asynchronous subscriber handlers and weak references to prevent subscriber leaks?](#py-adv-074-how-do-you-implement-a-distributed-event-bus--observer-pattern-with-asynchronous-subscriber-handlers-and-weak-references-to-prevent-subscriber-leaks)
  - [PY-ADV-075: How do you safely serialize and deserialize complex polymorphic class hierarchies with circular references using 'pickle' or custom JSON encoders?](#py-adv-075-how-do-you-safely-serialize-and-deserialize-complex-polymorphic-class-hierarchies-with-circular-references-using-'pickle'-or-custom-json-encoders)

---

## Basic Level

### PY-BAS-051: What is Object-Oriented Programming (OOP) in Python and what are its four core pillars?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Object-Oriented Programming is a paradigm that models software around data (objects) and behaviors (methods); its four pillars are Encapsulation, Abstraction, Inheritance, and Polymorphism.

#### 2. Detailed Answer
Encapsulation bundles data and the methods that operate on that data within a single unit (class) while restricting direct external access to internal state. Abstraction hides complex implementation details and exposes only necessary interfaces. Inheritance allows a new class to inherit attributes and methods from an existing class to foster reusability. Polymorphism enables entities of different classes to respond to the same method invocation in their own specific ways.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self._balance = balance  # Encapsulation (protected)

    def deposit(self, amount: float):
        if amount > 0:
            self._balance += amount

    def get_balance(self) -> float:
        return self._balance

account = BankAccount('Alice', 1000.0)
account.deposit(250.0)
print('Account balance:', account.get_balance())
```
*Demonstrating encapsulation and methods in a basic class.*

#### 4. Internal Working
In Python, everything is an object, including functions, modules, and primitive types. Classes themselves are instances of `type`. When an object is instantiated, Python allocates a PyObject struct containing `ob_refcnt`, a pointer to its class `PyTypeObject`, and an instance attribute dictionary `__dict__`.

#### 5. Real-World Use Case
Structuring domain entities in enterprise backend applications, such as User, Order, Payment, and Invoice models.

#### 6. Interview Follow-Up Questions
- How does Python implement abstraction without native interface keywords like Java?
- Why is Python considered a multi-paradigm language rather than purely object-oriented?

#### 7. Common Interview Mistakes
- Assuming Python enforces strict private variables with compiler errors; Python relies on naming conventions (`_`) and name mangling (`__`).

#### 8. Interview Tip
Emphasize that Python achieves abstraction and polymorphism primarily through duck typing rather than strict type inheritance.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/tutorial/classes.html

</details>

---

### PY-BAS-052: What is the difference between a class and an instance (object) in Python?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A class is a blueprint or template defining attributes and methods; an instance is a concrete realization of that class residing at a specific memory location.

#### 2. Detailed Answer
A class defines the structure, behavior, and shared state for a concept. When you instantiate a class (`obj = MyClass()`), Python allocates a new object in memory with its own identity (`id(obj)`), type pointer pointing back to `MyClass`, and an independent instance namespace (`__dict__`). Multiple instances can be spawned from a single class blueprint.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ServerNode:
    cluster_name = 'us-east-prod'  # Class attribute (shared)

    def __init__(self, node_id: str):
        self.node_id = node_id     # Instance attribute (unique)

node1 = ServerNode('node-101')
node2 = ServerNode('node-102')

print('Same class?', type(node1) is type(node2))  # True
print('Different identities?', id(node1) != id(node2))  # True
print('Distinct instance IDs:', node1.node_id, node2.node_id)
```
*Distinguishing class identity from individual instance states.*

#### 4. Internal Working
The class object is created once when the module loads and is stored as an instance of `type`. Instances are allocated on the heap dynamically via `type.__call__`, which invokes `MyClass.__new__` and then `MyClass.__init__`.

#### 5. Real-World Use Case
Modeling distributed cluster nodes, microservice configurations, and database entity rows.

#### 6. Interview Follow-Up Questions
- How does modifying a class attribute affect existing instances?
- What is stored in a class's `__dict__` versus an instance's `__dict__`?

#### 7. Common Interview Mistakes
- Overwriting a class attribute on an instance (`node1.cluster_name = 'new'`), which creates a shadowed instance attribute instead of mutating the class variable.

#### 8. Interview Tip
Remember: `instance.__dict__` stores instance-specific attributes; `Class.__dict__` stores shared methods and class variables.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#classes

</details>

---

### PY-BAS-053: What is '__init__' and how does it differ from a constructor in C++ or Java?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__init__' is an initializer method that configures an already-allocated instance; the actual constructor in Python is '__new__', which creates and returns the raw instance.

#### 2. Detailed Answer
In C++ or Java, the constructor both allocates memory and initializes fields in a single step. In Python, instance creation is a two-step process: `__new__(cls)` is the static constructor that allocates and returns the new instance object, and `__init__(self)` is the initializer called immediately afterward to populate attributes onto the newly created `self`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class DatabaseConnection:
    def __init__(self, host: str, port: int = 5432):
        self.host = host
        self.port = port
        self.is_connected = False
        print(f'Initialized connection to {host}:{port}')

conn = DatabaseConnection('postgres.prod', 5432)
print('Connection host:', conn.host)
```
*Initializing object attributes inside __init__.*

#### 4. Internal Working
When executing `obj = Class(*args, **kwargs)`, Python calls `Class.__call__`. This method executes `self = Class.__new__(Class, *args, **kwargs)` and, if `isinstance(self, Class)` is true, invokes `Class.__init__(self, *args, **kwargs)`. `__init__` must always return `None`.

#### 5. Real-World Use Case
Setting up initial database handles, injecting dependencies, and validating configuration parameters on startup.

#### 6. Interview Follow-Up Questions
- What happens if __init__ returns a value other than None?
- When must you override __new__ instead of __init__?

#### 7. Common Interview Mistakes
- Returning a value from `__init__` (e.g. `return self`), which raises a TypeError: __init__() should return None.

#### 8. Interview Tip
Always clarify: `__new__` creates the object; `__init__` initializes it.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#basic-customization

</details>

---

### PY-BAS-054: Why must methods explicitly receive 'self' as their first parameter in Python?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'self' represents the instance upon which the method is called, making attribute binding explicit and avoiding hidden scope lookups, consistent with the Zen of Python ('Explicit is better than implicit').

#### 2. Detailed Answer
In languages like Java or C++, the instance pointer `this` is implicitly available in method bodies. Python requires `self` to be declared explicitly in method signatures. When calling `obj.method(arg)`, Python's descriptor protocol automatically translates the call into `Class.method(obj, arg)`, passing the calling instance as the first argument.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Worker:
    def __init__(self, name: str):
        self.name = name

    def perform_task(self, task_name: str):
        return f'Worker {self.name} is executing {task_name}'

w = Worker('Bob')
# Calling via instance (Python injects 'w' as 'self')
print(w.perform_task('data migration'))
# Calling via class explicitly demonstrates how 'self' is passed
print(Worker.perform_task(w, 'data migration'))
```
*Calling methods via instance and class to demonstrate self injection.*

#### 4. Internal Working
Python functions define a `__get__` descriptor method. When accessed via an instance (`obj.perform_task`), `function.__get__` binds the function to the instance, producing a `MethodType` object that prepends `self` to the argument list when called.

#### 5. Real-World Use Case
Understanding `self` is essential when implementing decorators that wrap instance methods without dropping the instance argument.

#### 6. Interview Follow-Up Questions
- Can 'self' be renamed to something else, and why shouldn't you?
- How does the descriptor protocol convert a function into a bound method?

#### 7. Common Interview Mistakes
- Forgetting `self` in instance method declarations (`def my_method():`), causing a TypeError when invoked with arguments.

#### 8. Interview Tip
While `self` is not a reserved keyword (any name works), PEP 8 strictly mandates using `self` for instance methods.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/faq/programming.html#why-must-self-be-used-explicitly-in-method-definitions-and-calls

</details>

---

### PY-BAS-055: What is the difference between class attributes and instance attributes?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Class attributes are shared by all instances of a class and defined directly in the class body; instance attributes are unique to each instance and bound to 'self' inside methods.

#### 2. Detailed Answer
A class attribute belongs to the class namespace (`Class.__dict__`). All instances reference this shared attribute unless an instance shadows it by assigning a value with the same name. An instance attribute lives in that specific object's namespace (`instance.__dict__`). Modifying a mutable class attribute (like a list) affects all instances that read it.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Team:
    shared_tools = ['Git', 'Docker']  # Class attribute (shared)

    def __init__(self, name: str):
        self.name = name              # Instance attribute (unique)

t1 = Team('Backend')
t2 = Team('Frontend')

# Mutating shared class attribute mutates it for all instances!
t1.shared_tools.append('Kubernetes')
print('t2 sees the updated tool:', t2.shared_tools)  # ['Git', 'Docker', 'Kubernetes']

# Shadowing class attribute on an instance
t1.shared_tools = ['Terraform']  # Creates instance attribute on t1 only
print('t1 shadowed:', t1.shared_tools)
print('t2 still sees class attribute:', t2.shared_tools)
```
*Demonstrating shared mutable class attributes and instance shadowing.*

#### 4. Internal Working
Attribute lookup follows the MRO: when accessing `obj.attr`, Python first checks `obj.__dict__`. If absent, it checks `type(obj).__dict__` and then base classes. Assigning `obj.attr = val` writes directly to `obj.__dict__` without modifying the class attribute.

#### 5. Real-World Use Case
Shared connection pools, configuration constants, or thread pools defined at the class level; unique user IDs and tenant IDs at the instance level.

#### 6. Interview Follow-Up Questions
- What dangerous bug occurs when using a mutable object as a class attribute?
- How can you check if an attribute belongs to an instance or its class?

#### 7. Common Interview Mistakes
- Defining a mutable default (like `items = []`) as a class attribute, causing all instances to unintentionally share and mutate the same list.

#### 8. Interview Tip
Watch out for mutable class attributes: if instances append to it, all instances share the side effects.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables

</details>

---

### PY-BAS-056: How does single inheritance work in Python and how do you call the parent method with 'super()'?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Single inheritance allows a child class to inherit attributes and methods from a single parent class; 'super()' returns a proxy object that delegates method calls to the parent class.

#### 2. Detailed Answer
Inheritance promotes code reuse by establishing an 'is-a' relationship. The derived class specifies its parent in parentheses `class Child(Parent):`. When overriding a parent method, calling `super().__init__(*args)` or `super().method_name()` executes the parent's implementation, allowing the child to extend behavior without duplicating initialization code.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Service:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_running = False

    def start(self):
        self.is_running = True
        print(f'{self.service_name} started.')

class EmailService(Service):
    def __init__(self, service_name: str, smtp_host: str):
        super().__init__(service_name)  # Delegate to parent
        self.smtp_host = smtp_host

    def start(self):
        super().start()                 # Call parent start
        print(f'Connected to SMTP host: {self.smtp_host}')

svc = EmailService('MailerDaemon', 'smtp.mail.com')
svc.start()
```
*Extending parent initialization and methods using super().*

#### 4. Internal Working
`super()` does not simply refer to the direct parent class; it inspects the Method Resolution Order (MRO) of the calling instance (`type(self).__mro__`) and invokes the next class in the chain.

#### 5. Real-World Use Case
Building specialized API controllers, custom Django models, and extensible authentication handlers.

#### 6. Interview Follow-Up Questions
- What is the difference between `super().__init__()` and `Parent.__init__(self)`?
- Why is `super()` mandatory in multiple inheritance scenarios?

#### 7. Common Interview Mistakes
- Calling `Parent.__init__(self)` in multiple inheritance, which can cause parent initializers to run multiple times.

#### 8. Interview Tip
Always prefer zero-argument `super()` in Python 3; it automatically resolves the enclosing class and instance.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/tutorial/classes.html#inheritance

</details>

---

### PY-BAS-057: How does encapsulation work in Python (public, protected '_', private '__' name mangling)?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Python enforces encapsulation through naming conventions rather than strict access modifiers: public (no prefix), protected ('_prefix' convention), and private ('__prefix' with name mangling).

#### 2. Detailed Answer
Python adheres to the philosophy: 'We are all consenting adults here.' An attribute without an underscore is public. A single leading underscore (`_protected`) signals to other developers and linters that the attribute is internal and should not be accessed outside the class. A double leading underscore (`__private`) triggers name mangling: CPython rewrites the attribute name to `_ClassName__attribute` to prevent accidental name collisions in subclasses.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class PaymentGateway:
    def __init__(self, api_key: str):
        self.gateway_name = 'Stripe'     # Public
        self._retry_limit = 3           # Protected (convention)
        self.__api_key = api_key        # Private (name-mangled)

    def get_masked_key(self):
        return f'***{self.__api_key[-4:]}'

gw = PaymentGateway('sk_live_secret123456')
print('Public:', gw.gateway_name)
print('Protected (accessible):', gw._retry_limit)

try:
    print(gw.__api_key)  # Fails with AttributeError
except AttributeError as e:
    print('Direct private access blocked:', e)

# Accessing via mangled name proves it is not truly hidden
print('Mangled access:', gw._PaymentGateway__api_key)
```
*Demonstrating public, protected, and private name mangling in Python.*

#### 4. Internal Working
During compilation, the AST transformer detects attributes beginning with two or more underscores and ending with at most one underscore, prepending `_ClassName`. This is solely intended to avoid attribute overriding in subclasses, not to enforce security.

#### 5. Real-World Use Case
Preventing accidental overrides of internal state in complex framework base classes and library designs.

#### 6. Interview Follow-Up Questions
- Is private name mangling a security mechanism for hiding secrets in memory?
- Why does an attribute named `__dunder__` not get name-mangled?

#### 7. Common Interview Mistakes
- Treating `__private` attributes as secure encryption; any code can access them via `_ClassName__attr`.

#### 8. Interview Tip
Clarify: `_single` is a developer convention; `__double` is name mangling to prevent subclass collision, not security.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/tutorial/classes.html#private-variables

</details>

---

### PY-BAS-058: What is polymorphism in Python and how does duck typing achieve it without formal interfaces?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Polymorphism allows different classes to be treated through a uniform interface; duck typing achieves this dynamically: 'If it walks like a duck and quacks like a duck, it's a duck.'

#### 2. Detailed Answer
In statically typed languages, polymorphism requires classes to explicitly inherit from a common base class or implement an interface. In Python, an operation or function simply invokes expected methods on an object. As long as the object implements the required methods at runtime, the code works regardless of the object's class hierarchy.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class PostgresExporter:
    def export(self, data: list):
        return f'Exported {len(data)} rows to PostgreSQL'

class S3Exporter:
    def export(self, data: list):
        return f'Uploaded {len(data)} objects to AWS S3 bucket'

def run_pipeline(exporter, records: list):
    # Polymorphic dispatch via duck typing
    return exporter.export(records)

print(run_pipeline(PostgresExporter(), [1, 2, 3]))
print(run_pipeline(S3Exporter(), [1, 2, 3]))
```
*Achieving polymorphism via duck typing without common inheritance.*

#### 4. Internal Working
Python executes the `CALL_METHOD` or `LOAD_METHOD` opcode. It looks up the method name in the object's type dictionary at runtime. If present, it binds and calls it; if missing, it raises an `AttributeError`.

#### 5. Real-World Use Case
Pluggable logging transports, multi-cloud storage adaptors, and custom database drivers in backend services.

#### 6. Interview Follow-Up Questions
- What happens if an object passed to a polymorphic function does not implement the expected method?
- How does typing.Protocol enable static duck typing?

#### 7. Common Interview Mistakes
- Enforcing rigid class inheritance solely to achieve polymorphism; in Python, shared interface behavior is sufficient.

#### 8. Interview Tip
State the duck typing principle: focus on what an object can DO, not what class it inherits from.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/glossary.html#term-duck-typing

</details>

---

### PY-BAS-059: What is the difference between '@staticmethod' and '@classmethod'?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'@classmethod' receives the class object ('cls') as its first parameter and can access or modify class state; '@staticmethod' receives neither 'self' nor 'cls' and behaves like a plain function scoped inside the class.

#### 2. Detailed Answer
A `@classmethod` is typically used for alternative constructors (factory methods) and operations that need to modify class-level state or support inheritance polymorphism. A `@staticmethod` does not know about the class or instance; it is attached to the class namespace purely for logical grouping and code organization.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Config:
    default_env = 'production'

    def __init__(self, env: str, timeout: int):
        self.env = env
        self.timeout = timeout

    @classmethod
    def from_env_string(cls, env_str: str):
        # Factory constructor receiving class 'cls'
        return cls(env=env_str, timeout=30)

    @staticmethod
    def is_valid_port(port: int) -> bool:
        # Utility function without self or cls
        return 1 <= port <= 65535

cfg = Config.from_env_string('staging')
print('Constructed from classmethod:', cfg.env, cfg.timeout)
print('Staticmethod check:', Config.is_valid_port(8080))
```
*Using classmethod as an alternative constructor and staticmethod as a utility.*

#### 4. Internal Working
Both are implemented as descriptors. `classmethod.__get__` binds the function's first argument to the calling class (`cls`). `staticmethod.__get__` returns the underlying function as-is without binding any arguments.

#### 5. Real-World Use Case
Alternative constructors (`User.from_dict()`, `Date.from_timestamp()`), and isolated utility validators.

#### 6. Interview Follow-Up Questions
- Why is `@classmethod` preferred over `@staticmethod` when building alternative constructors in inheritable classes?
- Can a staticmethod be overridden in a subclass?

#### 7. Common Interview Mistakes
- Hardcoding class names inside classmethods (`return Config(...)`) instead of using `cls(...)`, which breaks subclass inheritance.

#### 8. Interview Tip
Remember: `@classmethod` receives `cls` and supports subclass polymorphism; `@staticmethod` receives no implicit arguments.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#classmethod

</details>

---

### PY-BAS-060: What is the '@property' decorator and how does it implement getters, setters, and deleters?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The '@property' decorator turns a method into a managed attribute (getter), allowing read/write access via attribute syntax while enabling validation, encapsulation, and computed properties.

#### 2. Detailed Answer
Using getter and setter methods (`get_age()`, `set_age()`) clutters client code. The `@property` decorator allows attributes to be accessed like normal fields (`obj.age`). When decorated with `@property`, the method acts as the getter. Companion decorators `@prop.setter` and `@prop.deleter` define corresponding setter and deleter logic for data validation.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class UserAccount:
    def __init__(self, username: str, age: int):
        self.username = username
        self._age = age

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if value < 0 or value > 150:
            raise ValueError('Invalid age provided')
        self._age = value

u = UserAccount('Alice', 25)
print('Property read:', u.age)
u.age = 26  # Calls age.setter
print('Property updated:', u.age)
```
*Defining getters and setters with validation using @property.*

#### 4. Internal Working
`property` is a built-in data descriptor class implementing `__get__`, `__set__`, and `__delete__`. Accessing `obj.age` invokes `property.__get__`, which calls the getter function. Assigning `obj.age = val` invokes `property.__set__`.

#### 5. Real-World Use Case
Data validation in domain models, computed fields (e.g. `full_name` from `first_name` and `last_name`), and lazy evaluation.

#### 6. Interview Follow-Up Questions
- What happens if you define a @property without a @prop.setter and attempt to assign to it?
- How is `@property` implemented using Python's descriptor protocol?

#### 7. Common Interview Mistakes
- Forgetting to store data in a private backing variable (like `self._age`), causing infinite recursion by calling `self.age = value` inside `age.setter`.

#### 8. Interview Tip
Watch for infinite recursion in setters: assign to `self._attr`, never to `self.attr` inside the setter.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#property

</details>

---

### PY-BAS-061: What is the difference between '__str__' and '__repr__' and when should each be implemented?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__str__' provides an informal, human-readable string representation for end users; '__repr__' provides an unambiguous, technical string representation primarily for developers and debugging.

#### 2. Detailed Answer
When printing an object (`print(obj)`) or converting via `str(obj)`, Python calls `__str__`. When inspecting an object in an interactive shell, logging, or within container reprs (`[obj1, obj2]`), Python calls `__repr__`. Ideally, `__repr__` should look like a valid Python expression that could recreate the object (e.g. `Class(arg1, arg2)`). If `__str__` is not defined, Python falls back to `__repr__`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Transaction:
    def __init__(self, tx_id: str, amount: float):
        self.tx_id = tx_id
        self.amount = amount

    def __repr__(self) -> str:
        # Unambiguous representation for developers
        return f'Transaction(tx_id={self.tx_id!r}, amount={self.amount!r})'

    def __str__(self) -> str:
        # Human-friendly representation for users
        return f'Transaction #{self.tx_id}: ${self.amount:.2f}'

tx = Transaction('TX-9901', 149.5)
print('User output (str):', str(tx))
print('Debug output (repr):', repr(tx))
print('List display uses repr:', [tx])
```
*Implementing both __str__ and __repr__ for clear debugging and user output.*

#### 4. Internal Working
`print()` and `str()` call `PyObject_Str()`, which looks for `tp_str`. The interactive REPL and `repr()` call `PyObject_Repr()`, which looks for `tp_repr`. Containers (lists, dicts) always display their elements using `__repr__`.

#### 5. Real-World Use Case
Logging structured API errors, debugging failed database queries, and rendering clean CLI outputs.

#### 6. Interview Follow-Up Questions
- Why do lists and dictionaries print their elements using __repr__ instead of __str__?
- What is the golden rule for formatting __repr__ strings?

#### 7. Common Interview Mistakes
- Implementing only `__str__` and leaving `__repr__` as the default `<Object at 0x...>`, making container debugging painful.

#### 8. Interview Tip
Rule of thumb: Always implement `__repr__` first; if you need a friendlier format for users, add `__str__` second.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#object.__repr__

</details>

---

### PY-BAS-062: What are dunder (double underscore) / magic methods and why are they used?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Dunder (Double UNDERscore) methods are special methods with leading and trailing double underscores that Python invokes behind the scenes to perform built-in operations like indexing, arithmetic, iteration, and representation.

#### 2. Detailed Answer
Dunder methods allow custom classes to integrate seamlessly with Python's syntax and standard library. Instead of calling named methods like `obj.add(other)` or `obj.get_size()`, implementing `__add__` allows `obj + other` and implementing `__len__` allows `len(obj)`. This creates intuitive, idiomatic APIs following Python's data model.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item: str):
        self.items.append(item)

    def __len__(self):
        # Enables len(cart)
        return len(self.items)

    def __contains__(self, item):
        # Enables 'item in cart'
        return item in self.items

c = Cart()
c.add_item('Laptop')
print('Cart size via len():', len(c))
print('Membership check via in:', 'Laptop' in c)
```
*Enabling built-in operators on custom classes using dunder methods.*

#### 4. Internal Working
Dunder methods are bound directly to function pointers in the class's C-level `PyTypeObject` struct (e.g. `tp_as_sequence->sq_length` for `__len__`). CPython bypasses instance attribute lookups and fetches type slots directly for performance.

#### 5. Real-World Use Case
Creating domain-specific collections, ORM query builders, math vector libraries, and custom context managers.

#### 6. Interview Follow-Up Questions
- Why does CPython look up dunder methods on the class rather than on the instance?
- Can you invent your own arbitrary dunder methods (e.g. `__my_method__`)?

#### 7. Common Interview Mistakes
- Inventing custom dunder method names; Python reserves all `__xxx__` names for future language expansion.

#### 8. Interview Tip
Never invent custom dunder names; use standard method names unless implementing documented Python protocols.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#special-method-names

</details>

---

### PY-BAS-063: What does 'isinstance()' do and why is it preferred over 'type(obj) is Class'?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'isinstance(obj, Class)' checks if an object is an instance of Class OR any subclass inheriting from it; 'type(obj) is Class' checks only exact class equality, breaking polymorphism and inheritance.

#### 2. Detailed Answer
When writing reusable functions, you generally want to accept instances of derived classes as well as the base class (Liskov Substitution Principle). `isinstance()` traverses the inheritance tree and returns True for any derived class. `type(obj) is Class` matches only the exact type, rejecting valid subclasses and breaking duck typing and virtual subclassing.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Animal: pass
class Dog(Animal): pass

d = Dog()

# isinstance supports inheritance hierarchy
print('isinstance(d, Animal):', isinstance(d, Animal))  # True
print('isinstance(d, Dog):', isinstance(d, Dog))        # True

# type() check breaks inheritance
print('type(d) is Animal:', type(d) is Animal)          # False (Breaks polymorphism!)
```
*Comparing isinstance() inheritance traversal vs rigid type() check.*

#### 4. Internal Working
`isinstance()` inspects `type(obj).__mro__`. It also supports checking against a tuple of types (`isinstance(x, (int, float))`) and honors virtual subclasses registered with Abstract Base Classes via `__instancecheck__`.

#### 5. Real-World Use Case
Type validation in API serializers, input sanitization in data pipelines, and error handling in middleware.

#### 6. Interview Follow-Up Questions
- How can isinstance() be customized using __instancecheck__?
- Can isinstance() take a tuple or union of types?

#### 7. Common Interview Mistakes
- Using `type(x) == int` instead of `isinstance(x, int)`, which breaks if someone subclasses `int` (like `bool`).

#### 8. Interview Tip
Always prefer `isinstance()` over `type()` to support polymorphism and derived subclasses.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#isinstance

</details>

---

### PY-BAS-064: What does 'issubclass()' do and how does it evaluate class hierarchies?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'issubclass(Derived, Base)' checks if class 'Derived' is a direct or indirect subclass of class 'Base', or if it is registered as a virtual subclass.

#### 2. Detailed Answer
Unlike `isinstance()`, which evaluates an object instance against a class, `issubclass()` operates strictly on class objects. A class is considered a subclass of itself (`issubclass(A, A)` is True). It also supports checking against a tuple of target base classes.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class BaseRepository: pass
class SqlRepository(BaseRepository): pass
class PostgresRepository(SqlRepository): pass

print('Direct subclass:', issubclass(SqlRepository, BaseRepository))        # True
print('Indirect subclass:', issubclass(PostgresRepository, BaseRepository))  # True
print('Self subclass:', issubclass(BaseRepository, BaseRepository))          # True
print('Unrelated check:', issubclass(str, BaseRepository))                   # False
```
*Evaluating class inheritance trees using issubclass().*

#### 4. Internal Working
`issubclass()` inspects the class's `__mro__` (Method Resolution Order). It also invokes `__subclasscheck__` on metaclasses, allowing Abstract Base Classes (like `collections.abc.Iterable`) to recognize unregistered classes that implement required protocol methods.

#### 5. Real-World Use Case
Plugin discovery systems, ORM model registry validation, and dependency injection container type-binding.

#### 6. Interview Follow-Up Questions
- What is the difference between issubclass() and isinstance()?
- How does issubclass() evaluate virtual subclasses registered with ABC.register()?

#### 7. Common Interview Mistakes
- Passing an instance to `issubclass()` (`issubclass(obj, Class)`), which raises a TypeError: issubclass() arg 1 must be a class.

#### 8. Interview Tip
Remember: `isinstance(obj, Class)` takes an instance first; `issubclass(Sub, Base)` takes two classes.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#issubclass

</details>

---

### PY-BAS-065: How does operator overloading work in Python (e.g. '__add__', '__sub__', '__mul__')?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Operator overloading allows custom classes to define behavior for standard operators (+, -, *, /) by implementing corresponding dunder methods like __add__, __sub__, and __mul__.

#### 2. Detailed Answer
When Python evaluates `a + b`, it calls `a.__add__(b)`. If `a` does not implement `__add__` or returns `NotImplemented`, Python falls back to calling `b.__radd__(a)` (reflected or right-hand addition). This allows custom classes to interoperate cleanly with built-in numeric and sequence types.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f'Vector2D({self.x}, {self.y})'

v1 = Vector2D(1.5, 2.0)
v2 = Vector2D(3.0, 4.0)
v3 = v1 + v2
print('Vector addition result:', v3)
```
*Overloading the addition operator (+) on a custom Vector class.*

#### 4. Internal Working
Returning `NotImplemented` (not raising an exception) signals to CPython that the operation cannot be completed by the left operand. Python then attempts the reflected method on the right operand (`__radd__`) before finally raising a `TypeError`.

#### 5. Real-World Use Case
Custom numeric types (Complex, Matrix, Financial Currency), vector math, and query filtering expressions in ORMs (`col == val`).

#### 6. Interview Follow-Up Questions
- Why should you return `NotImplemented` instead of raising a `TypeError` in operator methods?
- What is the difference between `__add__` and `__iadd__`?

#### 7. Common Interview Mistakes
- Raising a `TypeError` directly instead of returning `NotImplemented`, preventing the right-hand operand's reflected method from running.

#### 8. Interview Tip
Crucial best practice: return `NotImplemented` when an incompatible type is passed to an operator method.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types

</details>

---

### PY-BAS-066: How do comparison dunder methods work ('__eq__', '__lt__', etc.) and what is '@functools.total_ordering'?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Comparison methods (__eq__, __lt__, __le__, __gt__, __ge__) define how instances are ordered and compared; '@functools.total_ordering' automatically generates all remaining comparison methods given __eq__ and one ordering method.

#### 2. Detailed Answer
Writing all six comparison dunder methods manually is repetitive and error-prone. By decorating a class with `@functools.total_ordering` and implementing `__eq__` plus one ordering method (e.g. `__lt__`), Python automatically synthesizes the other four (`__le__`, `__gt__`, `__ge__`, `__ne__`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from functools import total_ordering

@total_ordering
class PriorityTask:
    def __init__(self, priority: int, name: str):
        self.priority = priority
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, PriorityTask): return NotImplemented
        return self.priority == other.priority

    def __lt__(self, other):
        if not isinstance(other, PriorityTask): return NotImplemented
        return self.priority < other.priority

t1 = PriorityTask(1, 'Urgent')
t2 = PriorityTask(2, 'Normal')
print('t1 < t2:', t1 < t2)    # True (via __lt__)
print('t1 <= t2:', t1 <= t2)  # True (synthesized by total_ordering)
print('t1 > t2:', t1 > t2)    # False (synthesized by total_ordering)
```
*Using @total_ordering to generate comparison methods from __eq__ and __lt__.*

#### 4. Internal Working
`total_ordering` dynamically adds wrapper methods to the class. For example, `__le__` is implemented as `not self > other` or `self < other or self == other`. While convenient, synthesized methods incur a slight performance overhead compared to direct implementations.

#### 5. Real-World Use Case
Sorting domain entities, priority queue elements in task dispatchers, and semver version comparisons.

#### 6. Interview Follow-Up Questions
- What is the performance trade-off of `@total_ordering` versus writing all methods manually?
- What happens if __lt__ returns NotImplemented?

#### 7. Common Interview Mistakes
- Implementing only `__lt__` without `__eq__` when using `@total_ordering`, which raises a ValueError.

#### 8. Interview Tip
Remember: `@total_ordering` requires `__eq__` PLUS one of `__lt__`, `__le__`, `__gt__`, or `__ge__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functools.html#functools.total_ordering

</details>

---

### PY-BAS-067: What is '__len__' and '__getitem__' and how do they make a custom class act like a sequence?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Implementing '__len__' and '__getitem__' satisfies Python's sequence protocol, allowing custom classes to support len(), square-bracket indexing, slicing, and for-loop iteration.

#### 2. Detailed Answer
Python relies on protocol-based polymorphism. If an object implements `__len__(self)` (returning a non-negative integer) and `__getitem__(self, index)` (handling integer offsets and slice objects), it behaves as an immutable sequence. Even without defining `__iter__`, Python can iterate over the object using `for x in obj:` by evaluating `obj[0], obj[1], obj[2]...` until `IndexError` is raised.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Deck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']

    def __init__(self):
        self._cards = [(rank, suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

deck = Deck()
print('Deck length:', len(deck))              # 52
print('First card:', deck[0])                 # ('2', 'spades')
print('Slicing deck:', deck[:3])              # Slicing works automatically!
print('Iteration supported:', ('A', 'spades') in deck)  # Membership works!
```
*Building a custom sequence supporting indexing, slicing, and iteration via __len__ and __getitem__.*

#### 4. Internal Working
The sequence protocol is checked in CPython via `tp_as_sequence`. Slicing passes a `slice` object into `__getitem__`. If `__getitem__` delegates to an internal list, slicing works out of the box.

#### 5. Real-World Use Case
Custom dataset loaders, pagination wrappers over database cursors, and matrix data structures.

#### 6. Interview Follow-Up Questions
- Why does implementing `__getitem__` automatically provide `in` membership testing without `__contains__`?
- How does `__setitem__` convert an immutable sequence into a mutable sequence?

#### 7. Common Interview Mistakes
- Raising `StopIteration` instead of `IndexError` in `__getitem__` when indexing out of bounds.

#### 8. Interview Tip
Sequence iteration stops on `IndexError`, not `StopIteration`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#emulating-container-types

</details>

---

### PY-BAS-068: What is '__call__' and how does it make an instance callable like a function?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The '__call__' dunder method allows class instances to be invoked like functions ('instance(*args)'), enabling stateful callable objects, closures, and class-based decorators.

#### 2. Detailed Answer
Functions in Python are simply objects that implement the `__call__` method. By implementing `__call__(self, *args, **kwargs)` in a custom class, instances can maintain internal state across invocations while presenting a clean function-call interface. `callable(obj)` returns True for any object whose class defines `__call__`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class RateLimiter:
    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.current_calls = 0

    def __call__(self, client_id: str) -> bool:
        if self.current_calls >= self.max_requests:
            return False
        self.current_calls += 1
        return True

limiter = RateLimiter(max_requests=2)
print('Is limiter callable?', callable(limiter))  # True
print('Call 1:', limiter('client-1'))            # True
print('Call 2:', limiter('client-1'))            # True
print('Call 3 (exceeded):', limiter('client-1'))  # False
```
*Implementing a stateful rate limiter using __call__.*

#### 4. Internal Working
When executing `obj()`, CPython checks `type(obj)->tp_call`. If the slot is populated, it invokes the function with `obj` as `self`. This is faster than normal method lookup because it bypasses `__getattribute__`.

#### 5. Real-World Use Case
Class-based decorators (with arguments), stateful API client interceptors, and mathematical function evaluators.

#### 6. Interview Follow-Up Questions
- What is the difference between a stateful function closure and a callable class instance with __call__?
- How can a callable class instance be used as a decorator?

#### 7. Common Interview Mistakes
- Assuming `__call__` must be defined as a static method; it is a regular instance method receiving `self`.

#### 8. Interview Tip
Callable instances are ideal when a function needs to maintain rich internal state or expose management methods alongside invocation.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#emulating-callable-objects

</details>

---

### PY-BAS-069: What is composition vs inheritance, and why is 'favor composition over inheritance' recommended in Python?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Inheritance models an 'is-a' relationship by subclassing; composition models a 'has-a' relationship by combining independent objects as components; composition is favored because it avoids rigid class hierarchies and fragile base class bugs.

#### 2. Detailed Answer
Deep inheritance hierarchies create tight coupling: changes to a base class can break subclasses in unexpected ways (the Fragile Base Class problem). Composition constructs complex systems by injecting small, interchangeable components. In Python, duck typing makes composition especially flexible because components only need to provide expected methods without sharing a class hierarchy.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Logger:
    def log(self, msg: str):
        print(f'[LOG] {msg}')

class Database:
    def query(self, sql: str):
        return f'Data for {sql}'

# Composition: OrderService HAS-A Logger and HAS-A Database
class OrderService:
    def __init__(self, db: Database, logger: Logger):
        self._db = db
        self._logger = logger

    def process_order(self, order_id: int):
        self._logger.log(f'Processing order {order_id}')
        return self._db.query(f'SELECT * FROM orders WHERE id={order_id}')

service = OrderService(Database(), Logger())
print(service.process_order(101))
```
*Building a loosely-coupled service using composition and dependency injection.*

#### 4. Internal Working
Composition avoids C3 linearization complexity and reduces memory coupling. Components can be mocked or swapped out easily during unit tests without complex subclassing.

#### 5. Real-World Use Case
Enterprise clean architecture, repository patterns, microservice clients, and dependency injection.

#### 6. Interview Follow-Up Questions
- What is the 'Fragile Base Class' problem and how does composition solve it?
- When is inheritance genuinely appropriate over composition?

#### 7. Common Interview Mistakes
- Creating deep multi-level inheritance hierarchies (`Manager -> Employee -> Person -> LivingEntity -> Object`) that become impossible to maintain.

#### 8. Interview Tip
Quote the classic rule: 'Favor object composition over class inheritance.' Use inheritance only for strict 'is-a' taxonomy.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://en.wikipedia.org/wiki/Composition_over_inheritance

</details>

---

### PY-BAS-070: What are Python dataclasses ('@dataclass') and what boilerplate do they eliminate?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The '@dataclass' decorator (PEP 557) automatically generates special methods like __init__, __repr__, __eq__, and comparison methods from type-annotated class attributes, eliminating tedious boilerplate.

#### 2. Detailed Answer
Before Python 3.7, creating a simple data container required writing repetitive `__init__`, `__repr__`, and `__eq__` methods. `@dataclass` inspects type annotations in the class definition and auto-synthesizes these methods at class creation time. It produces standard Python classes that support inheritance and custom methods.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from dataclasses import dataclass

@dataclass
class Product:
    sku: str
    name: str
    price: float
    in_stock: bool = True

p1 = Product('SKU-100', 'Mechanical Keyboard', 89.99)
p2 = Product('SKU-100', 'Mechanical Keyboard', 89.99)

print('Auto-generated repr:', p1)
print('Auto-generated equality:', p1 == p2)  # True
```
*Defining a clean data model with auto-generated __repr__ and __eq__ using @dataclass.*

#### 4. Internal Working
`@dataclass` is a class decorator that inspects `cls.__annotations__`. It generates Python code strings for `__init__`, `__repr__`, etc., and compiles them onto the class using `exec()`, achieving the same runtime performance as hand-written methods.

#### 5. Real-World Use Case
Data Transfer Objects (DTOs), API request/response models, database query output structures, and configuration objects.

#### 6. Interview Follow-Up Questions
- What is the difference between a dataclass and a NamedTuple?
- Can a dataclass be made immutable and hashable?

#### 7. Common Interview Mistakes
- Omitting type annotations on dataclass fields; fields without type annotations are ignored by `@dataclass`.

#### 8. Interview Tip
Remember: every field in a `@dataclass` MUST have a type annotation (even if just `: Any`).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/dataclasses.html

</details>

---

### PY-BAS-071: How do default attribute values and field defaults work in dataclasses ('field(default_factory=...)')?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
In dataclasses, mutable default values (like lists or dicts) must be defined using 'field(default_factory=...)'; assigning a mutable default directly raises a ValueError to prevent shared state bugs.

#### 2. Detailed Answer
If Python allowed `items: list = []` as a field default, every instance would share the exact same list object in memory. To prevent this, `@dataclass` requires `field(default_factory=list)`, which calls the factory function to create a fresh container instance whenever a new object is initialized.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from dataclasses import dataclass, field

@dataclass
class UserProfile:
    username: str
    # default_factory generates a brand new list for each instance
    roles: list = field(default_factory=lambda: ['viewer'])
    metadata: dict = field(default_factory=dict)

u1 = UserProfile('Alice')
u2 = UserProfile('Bob')
u1.roles.append('admin')

print('Alice roles:', u1.roles)       # ['viewer', 'admin']
print('Bob roles (unaffected):', u2.roles)  # ['viewer']
```
*Preventing shared mutable state using field(default_factory=...).*

#### 4. Internal Working
The `field()` function returns a `Field` descriptor object storing metadata, default value, default factory, repr inclusion flags, and comparison rules. During `__init__` code generation, the factory is called if no argument is passed.

#### 5. Real-World Use Case
Representing JSON schema models with default empty arrays, user role assignments, and nested configuration maps.

#### 6. Interview Follow-Up Questions
- Why does `@dataclass` disallow non-default fields after default fields?
- How do you exclude a sensitive field (like a password) from the auto-generated __repr__?

#### 7. Common Interview Mistakes
- Assigning `roles: list = []` directly in a dataclass definition, crashing with a ValueError at module import time.

#### 8. Interview Tip
To hide fields in repr: `field(default=..., repr=False)` (e.g. for API tokens or passwords).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/dataclasses.html#dataclasses.field

</details>

---

### PY-BAS-072: What is '__dict__' on an object and how does attribute lookup interact with it?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__dict__' is a dictionary (or mapping proxy) that stores an object's writable attributes; attribute lookup checks the instance '__dict__' before falling back to class attributes.

#### 2. Detailed Answer
Every standard Python instance and class maintains an internal `__dict__` dictionary mapping attribute names (strings) to their values. When you evaluate `obj.x`, Python checks if `'x'` exists in `obj.__dict__`. If not, it traverses up to `type(obj).__dict__` and then follows the class MRO. Assigning `obj.x = 42` directly inserts `'x': 42` into `obj.__dict__`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Server:
    default_port = 8080  # Lives in Server.__dict__

    def __init__(self, host: str):
        self.host = host  # Lives in self.__dict__

s = Server('localhost')
print('Instance __dict__:', s.__dict__)  # {'host': 'localhost'}

# Dynamic attribute injection writes to __dict__
s.__dict__['timeout'] = 30
print('Directly accessed injected attribute:', s.timeout)
```
*Inspecting and manipulating the underlying instance __dict__.*

#### 4. Internal Working
In CPython, `PyObject` has an offset `tp_dictoffset` that locates the pointer to the `PyDictObject`. When descriptors or `__slots__` are used, attribute lookup bypasses `__dict__` to read directly from fixed C offsets.

#### 5. Real-World Use Case
Dynamic serialization (e.g. converting model to JSON), debugging attribute states, and implementing dynamic proxies.

#### 6. Interview Follow-Up Questions
- How does using `__slots__` eliminate `__dict__` to save memory?
- Why is `Class.__dict__` a MappingProxyType while `instance.__dict__` is a standard dict?

#### 7. Common Interview Mistakes
- Assuming all Python objects have a `__dict__`; objects using `__slots__` or built-in types (like `int`, `list`) do not have a `__dict__`.

#### 8. Interview Tip
Explain that instance attributes live in `instance.__dict__`, while class attributes and methods live in `Class.__dict__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#object.__dict__

</details>

---

### PY-BAS-073: What happens when an attribute is not found: how does '__getattr__' differ from '__getattribute__'?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__getattribute__' is called unconditionally for EVERY attribute access; '__getattr__' is called ONLY as a fallback when the attribute is NOT found in the instance or class hierarchy.

#### 2. Detailed Answer
Every attribute lookup `obj.name` first invokes `obj.__getattribute__('name')`. It checks descriptors, instance `__dict__`, and class hierarchy. If all checks fail and raise an `AttributeError`, Python catches it and invokes `obj.__getattr__('name')` as a fallback. Overriding `__getattribute__` is dangerous because any attribute read inside it can cause infinite recursion.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class DynamicSettings:
    def __init__(self):
        self.env = 'production'  # Normal attribute

    def __getattr__(self, name):
        # Called ONLY when attribute is missing
        print(f'__getattr__ called for missing attribute: {name}')
        return f'default_val_for_{name}'

s = DynamicSettings()
print('Existing attribute:', s.env)      # Does NOT trigger __getattr__
print('Missing attribute:', s.timeout)   # Triggers __getattr__
```
*Demonstrating fallback attribute resolution via __getattr__.*

#### 4. Internal Working
If you override `__getattribute__`, you must call `super().__getattribute__(name)` to retrieve attributes; accessing `self.name` directly inside it calls `__getattribute__` again, triggering infinite recursion and `RecursionError`.

#### 5. Real-World Use Case
Dynamic API clients (e.g. `client.users.get()`), lazy loading database attributes, and mock objects in testing.

#### 6. Interview Follow-Up Questions
- Why does accessing `self.attr` inside `__getattribute__` trigger a RecursionError?
- How do dynamic RPC libraries use `__getattr__` to route remote function calls?

#### 7. Common Interview Mistakes
- Confusing `__getattr__` with `__getattribute__`; `__getattr__` is safe and only runs on missing attributes.

#### 8. Interview Tip
Mnemonic: `__getattribute__` = ALWAYS called; `__getattr__` = FALLBACK when missing.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access

</details>

---

### PY-BAS-074: What is the 'del' statement when applied to an attribute ('del obj.attr') and what dunder method does it trigger?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'del obj.attr' deletes an attribute from an object's namespace, triggering the '__delattr__' dunder method or '__delete__' if managed by a descriptor.

#### 2. Detailed Answer
When executing `del obj.attr`, Python invokes `obj.__delattr__('attr')`. For standard objects, this removes the key `'attr'` from `obj.__dict__`. If the attribute is managed by a descriptor, it invokes `descriptor.__delete__(obj)`. If the attribute does not exist, an `AttributeError` is raised.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ConfigNode:
    def __init__(self, key: str, val: str):
        self.key = key
        self.val = val

    def __delattr__(self, name):
        print(f'Intercepting deletion of attribute: {name}')
        super().__delattr__(name)

node = ConfigNode('host', '127.0.0.1')
print('Before del:', hasattr(node, 'val'))  # True
del node.val                                # Triggers __delattr__
print('After del:', hasattr(node, 'val'))   # False
```
*Intercepting attribute deletion with __delattr__.*

#### 4. Internal Working
In CPython, `del` opcode `DELETE_ATTR` calls `PyObject_SetAttr(obj, name, NULL)`. Passing `NULL` as the value signals deletion in the internal C API.

#### 5. Real-World Use Case
Cleaning up cache entries, resetting cached properties, and invalidating state in state machine entities.

#### 6. Interview Follow-Up Questions
- What is the difference between `del obj` (deleting a variable) and `del obj.attr` (deleting an attribute)?
- What happens if you delete an attribute that exists on the class but not on the instance?

#### 7. Common Interview Mistakes
- Attempting to delete a class attribute via an instance (`del instance.class_attr`), which raises an AttributeError; class attributes must be deleted via `del Class.attr`.

#### 8. Interview Tip
Remember: `del obj.attr` removes from `instance.__dict__`; it cannot delete class-level attributes.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access

</details>

---

### PY-BAS-075: What is '__slots__' and how does it reduce memory consumption for millions of instances?

**Difficulty:** Basic | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__slots__' is a class-level declaration that replaces the per-instance '__dict__' with a fixed-size array of attribute descriptors, reducing instance memory by 60-70% and preventing dynamic attribute creation.

#### 2. Detailed Answer
Normally, every Python object allocates a `__dict__` dictionary to allow dynamic attribute assignment, consuming substantial memory overhead (typically 150-200 bytes per instance). When `__slots__ = ('x', 'y')` is defined, CPython reserves exact C pointer offsets for those attributes and skips allocating `__dict__` and `__weakref__`, drastically reducing memory overhead.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import sys

class StandardPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p_std = StandardPoint(10, 20)
p_slot = SlottedPoint(10, 20)

print('Standard point size (with __dict__):', sys.getsizeof(p_std) + sys.getsizeof(p_std.__dict__))
print('Slotted point size (no __dict__):', sys.getsizeof(p_slot))

# Dynamic assignment is blocked on slotted instances
try:
    p_slot.z = 30
except AttributeError as e:
    print('Dynamic attribute assignment blocked:', e)
```
*Comparing memory consumption and dynamic assignment between standard and slotted classes.*

#### 4. Internal Working
For each slot name, CPython generates a `member_descriptor` on the class object. Accessing `p_slot.x` reads directly from a fixed C offset within the instance struct, bypassing hash table lookup.

#### 5. Real-World Use Case
Optimizing memory in microservices processing millions of graph nodes, geometric coordinate streams, or database rows in memory.

#### 6. Interview Follow-Up Questions
- What happens if a class with `__slots__` is subclassed by a class that does NOT declare `__slots__`?
- Can a slotted class have a `__dict__` if desired?

#### 7. Common Interview Mistakes
- Assuming subclasses automatically inherit the memory savings of `__slots__`; if a subclass does not define `__slots__`, it allocates a `__dict__` anyway.

#### 8. Interview Tip
State the primary benefit: `__slots__` reduces memory usage significantly by eliminating the per-instance `__dict__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#slots

</details>

---

## Intermediate Level

### PY-INT-051: What is Multiple Inheritance in Python and what is the 'Diamond Problem'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Multiple inheritance allows a class to inherit from more than one parent class; the Diamond Problem occurs when two parent classes inherit from the same grandparent, creating ambiguity about which parent method executes first.

#### 2. Detailed Answer
In a diamond hierarchy, class A is inherited by both B and C, and class D inherits from both B and C (`class D(B, C)`). If both B and C override a method from A, calling that method on an instance of D could be ambiguous. In Python 3, this ambiguity is resolved deterministically using the C3 Linearization algorithm to compute a strict, monotonic Method Resolution Order (MRO).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class A:
    def ping(self):
        return 'A'

class B(A):
    def ping(self):
        return 'B'

class C(A):
    def ping(self):
        return 'C'

class D(B, C):
    pass

d = D()
print('Resolved method call:', d.ping())  # Returns 'B' (B precedes C in MRO)
print('MRO sequence:', [cls.__name__ for cls in D.__mro__])
```
*Resolving the diamond problem using Python's deterministic MRO.*

#### 4. Internal Working
Python constructs the MRO of class D by evaluating `L(D) = D + merge(L(B), L(C), (B, C))`. Because B appears before C in D's inheritance tuple, B and its overrides precede C in the resolution order.

#### 5. Real-World Use Case
Django mixin architectures (e.g. `class MyView(LoginRequiredMixin, ListView)`), and pluggable middleware pipelines.

#### 6. Interview Follow-Up Questions
- What happens if the inheritance hierarchy violates C3 linearization monotonicity?
- Why must mixins generally precede the base class in the class definition header?

#### 7. Common Interview Mistakes
- Hardcoding parent method calls (`B.ping(self)`), which circumvents the cooperative MRO chain.

#### 8. Interview Tip
Remember: Mixins must always appear BEFORE the main base class in the class declaration.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://www.python.org/download/releases/2.3/mro/

</details>

---

### PY-INT-052: How does Method Resolution Order (MRO) work and what is the C3 Linearization algorithm?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Method Resolution Order (MRO) defines the exact sequence in which Python searches base classes during attribute lookup; C3 Linearization mathematically ensures local precedence order and monotonicity.

#### 2. Detailed Answer
Prior to Python 2.3, Python used a depth-first search that produced anomalies in diamond diagrams. C3 Linearization replaced this with an algorithm based on two rules: 1. Children precede parents; 2. The order of parent classes in the class header is preserved (local precedence); 3. Monotonicity: if class X precedes class Y in any base class's MRO, X must precede Y in all derived MROs. If an inheritance graph cannot satisfy these rules, Python raises a `TypeError: Cannot create a consistent method resolution order`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class O: pass
class A(O): pass
class B(O): pass
class C(A, B): pass
class D(B, A): pass

# Consistent MRO for C: [C, A, B, O, object]
print('C MRO:', [cls.__name__ for cls in C.__mro__])

# Attempting to combine C and D causes conflicting ordering of A and B:
try:
    class Conflict(C, D): pass
except TypeError as e:
    print('C3 Linearization conflict detected:', e)
```
*Inspecting MRO and triggering an inconsistent MRO TypeError.*

#### 4. Internal Working
The C3 algorithm computes `L[C(B1...Bn)] = C + merge(L[B1], ..., L[Bn], B1...Bn)`. The merge selects the first head of a list that does not appear in the tail of any other list. Once selected, it is removed from all candidate lists and appended to the MRO.

#### 5. Real-World Use Case
Designing complex enterprise plugin systems and validating multi-tenant base class hierarchies.

#### 6. Interview Follow-Up Questions
- What does 'monotonicity' mean in the context of C3 Linearization?
- How can you programmatically inspect a class's MRO using `__mro__` or `.mro()`?

#### 7. Common Interview Mistakes
- Creating circular or contradictory inheritance orders (e.g. `class Child(Base, SubclassOfBase)`), crashing at class definition time.

#### 8. Interview Tip
Explain the 3 core invariants of C3: child before parent, local precedence order, and monotonicity.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://www.python.org/download/releases/2.3/mro/

</details>

---

### PY-INT-053: How does 'super()' actually work under the hood (bound proxy, cooperative multiple inheritance)?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'super()' returns a dynamic proxy object that delegates attribute lookup to the next class in the caller instance's MRO, enabling cooperative multiple inheritance where every class is visited exactly once.

#### 2. Detailed Answer
Many developers mistakenly believe `super()` simply calls the immediate parent class. In reality, `super()` does not point to a fixed class; it dynamically inspects `type(self).__mro__`. In multiple inheritance, calling `super().method()` in class B calls class C if C follows B in the instance's MRO. For cooperative inheritance to work, every class in the chain must use `super()` and accept `**kwargs`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Base:
    def action(self):
        print('Base action')

class Step1(Base):
    def action(self):
        print('Step1 start')
        super().action()  # Next in MRO, not necessarily Base!
        print('Step1 end')

class Step2(Base):
    def action(self):
        print('Step2 start')
        super().action()  # Next in MRO
        print('Step2 end')

class Pipeline(Step1, Step2):
    pass

p = Pipeline()
p.action()
```
*Cooperative multi-class execution chain orchestrated by super().*

#### 4. Internal Working
When executing `super()`, the Python compiler injects a zero-argument cell variable `__class__`. `super()` resolves to `super(__class__, self)`. The proxy object implements `__getattribute__` by finding `__class__` in `self.__mro__` and resuming search starting from the very next class index.

#### 5. Real-World Use Case
Building composable middleware stacks, logging decorators, and Django class-based views.

#### 6. Interview Follow-Up Questions
- Why does calling `Parent.__init__(self)` break cooperative multiple inheritance?
- What is the zero-argument `super()` introduced in Python 3 and how does the `__class__` cell work?

#### 7. Common Interview Mistakes
- Mixing `super()` with direct parent calls (`Parent.method(self)`), causing base methods to run multiple times or skip classes entirely.

#### 8. Interview Tip
Emphasize: `super()` resolves to the next class in the INSTANCE'S MRO, not the parent of the defining class.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://rhettinger.wordpress.com/2011/05/26/super-considered-super/

</details>

---

### PY-INT-054: What are Python Descriptors, and what is the difference between data descriptors and non-data descriptors?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A descriptor is an object that defines '__get__', '__set__', or '__delete__'; data descriptors define '__set__' or '__delete__' and take precedence over instance __dict__, while non-data descriptors define only '__get__' and are shadowed by instance __dict__.

#### 2. Detailed Answer
Descriptors customize how attributes are accessed and mutated. When accessing `obj.attr`, if `attr` is a data descriptor (has `__set__`), Python invokes `attr.__get__(obj, type(obj))` even if an attribute with the same name exists in `obj.__dict__`. If it is a non-data descriptor (only has `__get__`, like a regular method), an entry in `obj.__dict__` overrides it.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class NonDataDescriptor:
    def __get__(self, obj, objtype=None):
        return 'Non-Data Value'

class DataDescriptor:
    def __get__(self, obj, objtype=None):
        return 'Data Value'
    def __set__(self, obj, value):
        print(f'Setting {value}')

class Sample:
    nd = NonDataDescriptor()
    dd = DataDescriptor()

s = Sample()
s.__dict__['nd'] = 'Overridden!'
s.__dict__['dd'] = 'Shadow Attempt!'

print('Non-data descriptor shadowed by __dict__:', s.nd)  # 'Overridden!'
print('Data descriptor takes precedence over __dict__:', s.dd)  # 'Data Value'
```
*Demonstrating precedence difference between data and non-data descriptors.*

#### 4. Internal Working
The descriptor protocol is implemented in CPython's `_PyObject_GenericGetAttrWithDict`. The lookup precedence is: 1. Data descriptor; 2. Instance `__dict__`; 3. Non-data descriptor; 4. Class `__dict__` and MRO; 5. `__getattr__`.

#### 5. Real-World Use Case
ORM field definitions (Django Model fields, SQLAlchemy Column), validation libraries, and caching decorators.

#### 6. Interview Follow-Up Questions
- Why are methods considered non-data descriptors?
- How does defining `__set__` that raises an AttributeError create a read-only data descriptor?

#### 7. Common Interview Mistakes
- Assuming `@property` is a non-data descriptor; `@property` defines `__set__`, making it a data descriptor that overrides instance `__dict__`.

#### 8. Interview Tip
Memorize the lookup priority: Data Descriptors > Instance `__dict__` > Non-Data Descriptors.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/howto/descriptor.html

</details>

---

### PY-INT-055: How are '@property', '@classmethod', and regular functions implemented as descriptors?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
All three are descriptors: regular functions implement '__get__' to bind 'self', '@classmethod' implements '__get__' to bind 'cls', and '@property' is a data descriptor implementing '__get__', '__set__', and '__delete__'.

#### 2. Detailed Answer
Every Python function is a non-data descriptor. When you define `def foo(self):` in a class and access `instance.foo`, Python invokes `function.__get__(instance, Class)`, returning a bound `MethodType` that binds `self`. `@classmethod` wraps a function in a descriptor whose `__get__` binds the class object (`cls`). `@property` wraps getter, setter, and deleter callables in a data descriptor struct.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Demo:
    def standard_method(self):
        return 'hello'

d = Demo()
# Accessing via class yields raw function descriptor
raw_fn = Demo.standard_method
print('Raw class attribute is function:', type(raw_fn))

# Accessing via instance triggers __get__ returning bound method
bound_method = d.standard_method
print('Instance attribute is bound method:', type(bound_method))
print('Bound method holds self pointer:', bound_method.__self__ is d)
```
*Revealing how function descriptors transform into bound methods upon attribute access.*

#### 4. Internal Working
In CPython, `function` implements `func_descr_get`. If `instance` is not NULL, it returns `PyMethod_New(func, instance)`. If `instance` is NULL (accessed via class `Demo.standard_method`), it returns the function itself.

#### 5. Real-World Use Case
Understanding framework internals, implementing custom method binding, and debugging serialization errors with methods.

#### 6. Interview Follow-Up Questions
- What does `method.__self__` and `method.__func__` point to on a bound method?
- Why is a function accessed via a class unbound in Python 3, unlike Python 2?

#### 7. Common Interview Mistakes
- Thinking methods and functions are distinct types in class definitions; methods are simply functions wrapped by `__get__` at access time.

#### 8. Interview Tip
Core insight: 'Methods are just functions acting as descriptors that bind `self` when accessed from an instance.'

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/howto/descriptor.html#functions-and-methods

</details>

---

### PY-INT-056: What is '__new__' vs '__init__' and how does '__new__' control instance creation (Singleton, immutable subclasses)?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__new__' is a static method that allocates and returns a new object instance; '__init__' initializes that instance; overriding '__new__' allows intercepting allocation, returning cached singletons, or subclassing immutable types.

#### 2. Detailed Answer
`__new__(cls, *args, **kwargs)` must return a valid object instance (typically via `super().__new__(cls)`). If `__new__` returns an instance of `cls`, Python automatically calls `__init__(self, *args, **kwargs)`. If `__new__` returns an instance of a different class or an existing cached instance, `__init__` may be skipped or re-run. Overriding `__new__` is mandatory when subclassing immutable built-in types (like `int`, `str`, `tuple`) because their values cannot be modified in `__init__`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class UppercaseTuple(tuple):
    # Subclassing immutable tuple requires overriding __new__
    def __new__(cls, iterable):
        upper_items = (str(x).upper() for x in iterable)
        return super().__new__(cls, upper_items)

t = UppercaseTuple(['apple', 'banana', 'cherry'])
print('Custom immutable tuple:', t)  # ('APPLE', 'BANANA', 'CHERRY')
```
*Subclassing immutable tuple by modifying arguments inside __new__.*

#### 4. Internal Working
`type.__call__` executes `obj = cls.__new__(cls, *args, **kwargs)`. If `isinstance(obj, cls)` is true, it calls `obj.__init__(*args, **kwargs)` and returns `obj`.

#### 5. Real-World Use Case
Implementing the Singleton pattern, object pooling, factory constructors, and custom immutable domain types.

#### 6. Interview Follow-Up Questions
- Why can't you initialize values of an `int` or `tuple` subclass inside `__init__`?
- What happens if `__new__` returns an instance of a completely different class?

#### 7. Common Interview Mistakes
- Attempting to set immutable state in `__init__` when subclassing `str` or `int`; by then, the immutable value is already fixed.

#### 8. Interview Tip
Rule: Use `__new__` to control object creation and immutable types; use `__init__` for standard mutable state setup.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#object.__new__

</details>

---

### PY-INT-057: What are Abstract Base Classes ('abc.ABC', '@abstractmethod') and how do they enforce interfaces at instantiation time?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Abstract Base Classes define required interface contracts; if a derived class fails to implement every method decorated with '@abstractmethod', attempting to instantiate it raises a TypeError at runtime.

#### 2. Detailed Answer
Python does not have a native `interface` keyword. The `abc` module provides `ABC` and `@abstractmethod`. When a class inherits from `ABC` and defines abstract methods, Python's metaclass `ABCMeta` tracks those methods in `__abstractmethods__`. Any attempt to instantiate a subclass with a non-empty `__abstractmethods__` set raises a `TypeError`, preventing incomplete objects from existing.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from abc import ABC, abstractmethod

class StorageDriver(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write(self, path: str, data: bytes) -> bool:
        pass

class S3Driver(StorageDriver):
    def read(self, path: str) -> bytes:
        return b'file content'
    # Missing 'write' implementation!

try:
    driver = S3Driver()  # Instantiation fails
except TypeError as e:
    print('Instantiation blocked by ABC:', e)
```
*Enforcing interface implementation with ABC and @abstractmethod.*

#### 4. Internal Working
In CPython, `ABCMeta`'s type constructor checks if `__abstractmethods__` is set. When `type_call` executes, it verifies that `__abstractmethods__` is empty; if non-empty, it raises `TypeError: Can't instantiate abstract class with abstract methods...`.

#### 5. Real-World Use Case
Establishing clean architecture boundaries (Repositories, Services, Drivers) in enterprise microservices.

#### 6. Interview Follow-Up Questions
- Can an abstract method have a body that subclasses can invoke via `super()`?
- What is the difference between an Abstract Base Class and a typing.Protocol?

#### 7. Common Interview Mistakes
- Assuming abstract methods cannot provide code; an `@abstractmethod` can define a default implementation that subclasses call with `super()`.

#### 8. Interview Tip
Mention that ABCs enforce contracts at INSTANTIATION time, not at class declaration time.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/abc.html

</details>

---

### PY-INT-058: What is virtual subclass registration ('ABC.register()') and structural subtyping via '__subclasshook__'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Virtual subclassing allows an independent class to be recognized as a subclass of an ABC via 'ABC.register(Class)' or dynamic inspection with '__subclasshook__', without inheriting from the ABC.

#### 2. Detailed Answer
Inheriting from an ABC creates tight class hierarchy coupling. With virtual subclassing, you can register a third-party class as a subclass (`MyABC.register(ThirdPartyClass)`). `issubclass(ThirdPartyClass, MyABC)` and `isinstance(instance, MyABC)` evaluate to True, even though `MyABC` is not in `ThirdPartyClass.__mro__`. Furthermore, `__subclasshook__` allows ABCs to dynamically verify method signatures, recognizing any class that implements the interface.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from abc import ABC, abstractmethod

class Greeter(ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        # Any class with a callable 'greet' method is a virtual subclass
        return any('greet' in B.__dict__ and callable(B.__dict__['greet']) for B in subclass.__mro__)

class IndependentBot:
    def greet(self):
        return 'Beep Boop'

bot = IndependentBot()
print('Virtual subclass recognized:', issubclass(IndependentBot, Greeter))  # True
print('Instance recognized:', isinstance(bot, Greeter))                 # True
print('Greeter in MRO?', Greeter in IndependentBot.__mro__)              # False
```
*Dynamic structural subtyping using __subclasshook__.*

#### 4. Internal Working
`issubclass(C, B)` first calls `B.__subclasscheck__(C)`. For ABCs, this checks the registered virtual classes set and executes `__subclasshook__`. If it returns True, the check succeeds without inspecting the MRO.

#### 5. Real-World Use Case
How `collections.abc.Iterable` recognizes any class defining `__iter__` as an Iterable without explicit inheritance.

#### 6. Interview Follow-Up Questions
- Why does a virtual subclass not inherit default concrete methods defined in an ABC?
- What are the return values permitted from __subclasshook__ (True, False, NotImplemented)?

#### 7. Common Interview Mistakes
- Expecting a virtual subclass to inherit helper methods from the ABC; virtual subclasses inherit ZERO implementation code.

#### 8. Interview Tip
Crucial distinction: virtual subclasses satisfy `isinstance()` and `issubclass()` checks, but inherit NO code or MRO entries.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/abc.html#abc.ABCMeta.register

</details>

---

### PY-INT-059: What are Protocol classes in 'typing.Protocol' (PEP 544) and how do they implement static duck typing?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'typing.Protocol' defines structural types (interfaces) that are satisfied by any class providing the matching attributes and method signatures, checked statically by Mypy and optionally at runtime via '@runtime_checkable'.

#### 2. Detailed Answer
Nominal subtyping (like ABCs) requires classes to be explicitly declared as subclasses. Structural subtyping (`typing.Protocol`) allows static type checkers to verify compatibility based on the shape of the class. If a class implements all methods defined in the Protocol, Mypy considers it a valid subtype without requiring any explicit inheritance.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> str:
        ...

# Does not inherit from Serializable
class UserPayload:
    def serialize(self) -> str:
        return '{"user": "alice"}'

def process_item(item: Serializable):
    return item.serialize()

u = UserPayload()
print('Runtime checkable works:', isinstance(u, Serializable))  # True
print('Processed item:', process_item(u))
```
*Using typing.Protocol for static and runtime-checkable structural duck typing.*

#### 4. Internal Working
When decorated with `@runtime_checkable`, `Protocol` implements `__subclasshook__` to inspect whether target classes define matching method names. Static type checkers (Mypy, Pyright) inspect AST types without running code.

#### 5. Real-World Use Case
Defining decoupled component interfaces in microservice architectures, replacing third-party dependencies with mocks in tests.

#### 6. Interview Follow-Up Questions
- What is the performance overhead of `@runtime_checkable` on `isinstance()` checks?
- Can a Protocol define expected attributes as well as methods?

#### 7. Common Interview Mistakes
- Relying on `@runtime_checkable` to validate method signatures and type annotations at runtime; it only checks method existence.

#### 8. Interview Tip
Emphasize: `typing.Protocol` brings the safety of static typing together with the flexibility of Python's duck typing.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0544/

</details>

---

### PY-INT-060: What is '__init_subclass__' (PEP 487) and how does it provide class customization without metaclasses?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__init_subclass__' is a class method hook introduced in Python 3.6 that is called whenever a class is subclassed, allowing parents to customize, register, or validate subclasses without complex metaclasses.

#### 2. Detailed Answer
Before Python 3.6, automatically registering subclasses (like plugin architectures or ORM models) required writing a custom metaclass with `__init__` or `__new__`. With PEP 487, any parent class can implement `def __init_subclass__(cls, **kwargs):`. When a subclass is defined, Python automatically calls the parent's `__init_subclass__` with the new subclass as `cls`, allowing clean validation and registration.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class PluginBase:
    registry = {}

    def __init_subclass__(cls, plugin_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__.lower()
        cls.registry[name] = cls
        print(f'Registered plugin: {name} -> {cls}')

class AuthPlugin(PluginBase, plugin_name='oauth2'):
    pass

class MetricsPlugin(PluginBase, plugin_name='prometheus'):
    pass

print('Active registry:', list(PluginBase.registry.keys()))
```
*Automating plugin registration using __init_subclass__ with keyword arguments.*

#### 4. Internal Working
When `type.__new__` finishes constructing the new class, it scans the base classes and invokes `__init_subclass__`. Calling `super().__init_subclass__(**kwargs)` ensures that cooperative multiple inheritance chains are not broken.

#### 5. Real-World Use Case
Auto-registering API view endpoints, plugin frameworks, and validating database table names on model declaration.

#### 6. Interview Follow-Up Questions
- Why should `super().__init_subclass__(**kwargs)` always be called inside `__init_subclass__`?
- When is a metaclass still required despite the availability of `__init_subclass__`?

#### 7. Common Interview Mistakes
- Using a complex metaclass for simple subclass registration when `__init_subclass__` is far simpler and cleaner.

#### 8. Interview Tip
Quote PEP 487: `__init_subclass__` eliminates the need for 90% of custom metaclasses in modern Python.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0487/

</details>

---

### PY-INT-061: What is '__set_name__' (PEP 487) and how does it allow descriptors to capture their attribute names automatically?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__set_name__' is a descriptor callback called automatically by Python when the enclosing class is constructed, informing the descriptor of the attribute name it was assigned to in the class namespace.

#### 2. Detailed Answer
Before Python 3.6, descriptors could not know their assigned attribute name unless it was passed manually to `Descriptor('name')` or extracted via metaclasses. PEP 487 added `__set_name__(self, owner, name)`. When the owning class is created, CPython iterates over its attributes and calls `__set_name__` on any descriptor, allowing it to store the attribute name internally.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ValidatedString:
    def __set_name__(self, owner, name):
        # Automatically captures 'username' or 'email'
        self.name = name
        self.storage_name = f'_{name}'

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self.storage_name, '')

    def __set__(self, obj, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError(f'{self.name} must be a non-empty string')
        setattr(obj, self.storage_name, value)

class User:
    # No need to write ValidatedString('username')!
    username = ValidatedString()
    email = ValidatedString()

u = User()
u.username = 'alice'
print('Stored via __set_name__:', u.username, '| Backing store:', u._username)
```
*Automatic attribute name capture in descriptors using __set_name__.*

#### 4. Internal Working
`type.__new__` calls `descr.__set_name__(cls, name)` on all descriptors present in the class namespace during class construction, before `__init_subclass__` executes.

#### 5. Real-World Use Case
Writing clean ORM column descriptors (`id = IntegerField()`, `title = CharField()`) without redundant string naming.

#### 6. Interview Follow-Up Questions
- What happens if a descriptor is dynamically added to a class after class construction?
- What parameters are passed to `__set_name__`?

#### 7. Common Interview Mistakes
- Adding a descriptor to a class dynamically (`Class.attr = Desc()`) and expecting `__set_name__` to run automatically; it only runs during class creation.

#### 8. Interview Tip
Highlight: `__set_name__` eliminated the primary historical reason for using metaclasses with descriptors.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#object.__set_name__

</details>

---

### PY-INT-062: How do frozen dataclasses ('@dataclass(frozen=True)') achieve immutability and hashability?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'@dataclass(frozen=True)' overrides __setattr__ and __delattr__ to raise a FrozenInstanceError on mutation attempts, and generates a valid __hash__ method based on field values.

#### 2. Detailed Answer
When `frozen=True` is specified, `@dataclass` generates `__setattr__` and `__delattr__` methods that immediately raise `dataclasses.FrozenInstanceError`. Because instances cannot be modified, `@dataclass` also auto-synthesizes a `__hash__` method derived from all fields, making instances usable as dictionary keys and set members.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    path: str
    method: str = 'GET'

r1 = Route('/api/v1/users')
r2 = Route('/api/v1/users')

# Usable in sets and dict keys because it is frozen and hashable
route_handlers = {r1: 'UserListController'}
print('Handler lookup:', route_handlers[r2])

try:
    r1.method = 'POST'  # Mutation blocked
except Exception as e:
    print('Mutation blocked by frozen dataclass:', type(e).__name__)
```
*Creating an immutable, hashable domain object with frozen dataclasses.*

#### 4. Internal Working
During initialization, `@dataclass` bypasses its own frozen `__setattr__` by setting attributes using `object.__setattr__(self, name, value)`. This slight overhead means frozen dataclasses take marginally longer to instantiate than mutable ones.

#### 5. Real-World Use Case
Defining immutable Value Objects in Domain-Driven Design, route definitions, and cache keys.

#### 6. Interview Follow-Up Questions
- How can you bypass the immutability of a frozen dataclass using `object.__setattr__`?
- What happens if a frozen dataclass contains a mutable field (like a list)?

#### 7. Common Interview Mistakes
- Assuming a frozen dataclass makes mutable fields deeply immutable; a list inside a frozen dataclass can still be mutated in-place.

#### 8. Interview Tip
Watch out: if a frozen dataclass contains a list, `__hash__` will fail with TypeError: unhashable type.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/dataclasses.html#frozen-instances

</details>

---

### PY-INT-063: What is '__post_init__' in dataclasses and how is it used for validation or computed attributes?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__post_init__' is an optional method called automatically by a dataclass's generated __init__ immediately after field assignment, used for validating invariants and calculating derived fields.

#### 2. Detailed Answer
Standard dataclasses assign passed parameters directly to fields. When you need to validate input constraints (e.g. `age > 0`), normalize data (e.g. `email.lower()`), or calculate dependent values (e.g. `full_name = f'{first} {last}'`), implementing `__post_init__(self)` runs your custom logic immediately after the auto-generated initialization completes.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from dataclasses import dataclass, field

@dataclass
class OrderItem:
    product: str
    unit_price: float
    quantity: int
    total_price: float = field(init=False)  # Exclude from __init__ args

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError('Quantity must be greater than zero')
        # Compute derived field
        self.total_price = round(self.unit_price * self.quantity, 2)

item = OrderItem('SSD Drive', 99.99, 3)
print('Computed total price:', item.total_price)
```
*Validating fields and computing derived values in __post_init__.*

#### 4. Internal Working
In the auto-generated `__init__` code, Python ends with `self.__post_init__()` (or passes `InitVar` arguments if defined). For frozen dataclasses, assigning inside `__post_init__` must use `object.__setattr__(self, 'total_price', val)`.

#### 5. Real-World Use Case
Validating request schemas, computing cryptographic hashes on data records, and initializing derived database state.

#### 6. Interview Follow-Up Questions
- How do you set attributes in `__post_init__` when using a frozen dataclass?
- What is `dataclasses.InitVar` and how does it pass arguments into `__post_init__` without creating fields?

#### 7. Common Interview Mistakes
- Assigning to `self.field` inside a frozen dataclass's `__post_init__`, which triggers a `FrozenInstanceError`.

#### 8. Interview Tip
For frozen dataclasses, remember to use `object.__setattr__(self, 'field', val)` inside `__post_init__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/dataclasses.html#post-init-processing

</details>

---

### PY-INT-064: How does Python implement dynamic attribute delegation (Proxy pattern) using '__getattr__'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The Proxy pattern transparently delegates attribute and method calls to an underlying wrapped object by intercepting missing lookups in '__getattr__' and forwarding them via 'getattr()'.

#### 2. Detailed Answer
When wrapping an object (e.g. to add logging, caching, or access control), writing boilerplate forwarding methods for every attribute is unmaintainable. By implementing `__getattr__(self, name)`, any attribute or method not explicitly defined on the proxy is dynamically retrieved from the wrapped target using `getattr(self._wrapped, name)`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class AuditedServiceProxy:
    def __init__(self, target_service):
        self._target = target_service

    def __getattr__(self, name):
        attr = getattr(self._target, name)
        if callable(attr):
            def logged_wrapper(*args, **kwargs):
                print(f'[AUDIT] Executing method: {name}')
                return attr(*args, **kwargs)
            return logged_wrapper
        return attr

class CoreService:
    def process_payment(self, amount: float):
        return f'Processed ${amount}'

proxy = AuditedServiceProxy(CoreService())
print(proxy.process_payment(500.0))
```
*Implementing an auditing proxy using dynamic attribute delegation in __getattr__.*

#### 4. Internal Working
Because `__getattr__` only runs when an attribute is missing on the proxy, attributes explicitly defined on the proxy (like `self._target`) take priority and avoid delegation. Dunder methods (like `__len__`, `__iter__`) bypass `__getattr__` in CPython and must be defined explicitly on the proxy.

#### 5. Real-World Use Case
Database connection pooling wrappers, circuit breakers, and lazy-loading ORM relationship proxies.

#### 6. Interview Follow-Up Questions
- Why do dunder methods (like `__len__`) fail to delegate through `__getattr__`?
- How can accessing `self._target` inside `__getattr__` cause a RecursionError if `_target` was never initialized?

#### 7. Common Interview Mistakes
- Accessing `self._target` before initialization inside `__getattr__`, causing infinite recursion.

#### 8. Interview Tip
Caution: Dunder methods bypass `__getattr__` due to C-level type slot caching; define them explicitly on proxies.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access

</details>

---

### PY-INT-065: What is the difference between shallow copy and deep copy on custom classes, and how do '__copy__' and '__deepcopy__' work?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A shallow copy duplicates the instance but shares references to internal attributes; '__copy__' and '__deepcopy__' dunder methods allow classes to customize this behavior and protect internal resources.

#### 2. Detailed Answer
When a custom class is copied using `copy.copy(obj)`, Python allocates a new empty instance via `__new__` and shallow-copies `obj.__dict__`. Implementing `__copy__(self)` overrides this logic. When `copy.deepcopy(obj, memo)` is called, Python recursively duplicates all referenced objects; implementing `__deepcopy__(self, memo)` allows custom classes to serialize or duplicate complex states without copying uncopyable handles like open sockets.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import copy

class Session:
    def __init__(self, user: str, tokens: list):
        self.user = user
        self.tokens = tokens  # Mutable list

    def __deepcopy__(self, memo):
        # Custom deep copy logic ensuring tokens list is cloned safely
        cls = self.__class__
        cloned = cls.__new__(cls)
        memo[id(self)] = cloned
        cloned.user = self.user
        cloned.tokens = copy.deepcopy(self.tokens, memo)
        return cloned

s1 = Session('Alice', ['tok-1', 'tok-2'])
s2 = copy.deepcopy(s1)
s2.tokens.append('tok-3')

print('Original tokens unaffected:', s1.tokens)  # ['tok-1', 'tok-2']
print('Cloned tokens updated:', s2.tokens)        # ['tok-1', 'tok-2', 'tok-3']
```
*Customizing deep copy behavior and updating memo dictionary in __deepcopy__.*

#### 4. Internal Working
`copy.deepcopy` passes a `memo` dictionary. In custom `__deepcopy__`, you MUST record `memo[id(self)] = cloned` before recursing into children to prevent infinite recursion on self-referencing circular graphs.

#### 5. Real-World Use Case
Copying complex computational graphs, game board states, and cloning transaction contexts in backend systems.

#### 6. Interview Follow-Up Questions
- Why must you populate `memo[id(self)]` in `__deepcopy__` before copying child attributes?
- What happens if an object contains an uncopyable attribute like a thread Lock or open file?

#### 7. Common Interview Mistakes
- Failing to pass `memo` to nested `copy.deepcopy()` calls inside `__deepcopy__`, breaking cycle prevention.

#### 8. Interview Tip
Always update `memo[id(self)] = clone` before copying internal child references in `__deepcopy__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/copy.html

</details>

---

### PY-INT-066: How do context managers ('__enter__' and '__exit__') work as class methods, and how do they handle exceptions?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A class-based context manager implements '__enter__' to acquire resources and '__exit__' to guarantee resource cleanup; returning True from '__exit__' suppresses any exception that occurred within the 'with' block.

#### 2. Detailed Answer
When entering a `with Manager() as val:` block, Python calls `manager.__enter__()`, binding its return value to `val`. When exiting the block, `manager.__exit__(exc_type, exc_val, exc_tb)` is executed with any exception details (or `(None, None, None)` on clean exit). If an exception occurred and `__exit__` returns `True`, Python suppresses the exception; returning `False` or `None` allows the exception to propagate.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ManagedConnection:
    def __init__(self, conn_id: str):
        self.conn_id = conn_id

    def __enter__(self):
        print(f'Acquiring connection {self.conn_id}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'Closing connection {self.conn_id}')
        if exc_type is ValueError:
            print(f'Suppressing handled ValueError: {exc_val}')
            return True  # Suppress exception!
        return False     # Let all other exceptions bubble up

with ManagedConnection('PG-101') as conn:
    raise ValueError('Simulated non-fatal query error')

print('Execution resumed normally after suppressed exception!')
```
*Implementing a robust resource manager with selective exception suppression in __exit__.*

#### 4. Internal Working
The `with` statement compiles to `SETUP_WITH` or `WITH_EXCEPT_START` opcodes. CPython guarantees that `__exit__` runs even if an unhandled exception or `return` statement occurs inside the block.

#### 5. Real-World Use Case
Managing database transactions (auto-commit/rollback), locking mutexes (`threading.Lock`), temporary file cleanup, and mocking contexts.

#### 6. Interview Follow-Up Questions
- What are the exact three arguments passed to `__exit__` when an exception occurs?
- Why is returning `True` from `__exit__` dangerous if not done with caution?

#### 7. Common Interview Mistakes
- Returning a truthy value accidentally from `__exit__`, silently masking fatal bugs and unexpected exceptions.

#### 8. Interview Tip
Caution: Only return `True` from `__exit__` if you explicitly intend to suppress the exception.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#context-managers

</details>

---

### PY-INT-067: What is the difference between '@functools.cached_property' and '@property'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'@property' executes its getter function on every single attribute access; '@functools.cached_property' computes the value on the first access and caches it directly in the instance '__dict__', making subsequent reads instantaneous.

#### 2. Detailed Answer
`@property` is a data descriptor (`__set__` defined), meaning Python evaluates the method body every time `obj.attr` is referenced. `@functools.cached_property` (Python 3.8+) is a non-data descriptor (no `__set__`). On the first read, it computes the value and writes it directly to `obj.__dict__['attr']`. Subsequent reads find the attribute directly in the instance dictionary, bypassing the descriptor method entirely.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import time
from functools import cached_property

class DatasetReport:
    def __init__(self, records: list):
        self.records = records

    @cached_property
    def heavy_aggregation(self) -> int:
        print('Calculating heavy aggregation (runs once)...')
        return sum(x ** 2 for x in self.records)

report = DatasetReport(range(100))
print('First read:', report.heavy_aggregation)   # Triggers calculation
print('Second read:', report.heavy_aggregation)  # Instantaneous cached read

# Cache invalidation is simple: delete from __dict__
del report.heavy_aggregation
print('After invalidation:', report.heavy_aggregation)  # Recalculates!
```
*Caching expensive calculations and demonstrating cache invalidation with cached_property.*

#### 4. Internal Working
`cached_property` uses a threading lock during calculation to prevent race conditions in multi-threaded environments. Because it writes to `__dict__`, it does NOT work on classes declaring `__slots__` without `'__dict__'`. Furthermore, it can introduce memory leaks if instances are long-lived.

#### 5. Real-World Use Case
Parsing complex database payloads, calculating expensive statistical summaries, and memoizing API connection handshakes.

#### 6. Interview Follow-Up Questions
- Why does `@functools.cached_property` require the instance to have a `__dict__`?
- How do you invalidate or refresh a cached_property on an active instance?

#### 7. Common Interview Mistakes
- Using `cached_property` on an object with mutable attributes where data updates without invalidating the cached value.

#### 8. Interview Tip
To invalidate a `cached_property`, simply call `del instance.attr`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functools.html#functools.cached_property

</details>

---

### PY-INT-068: How does attribute lookup order work in Python (Data descriptor -> Instance __dict__ -> Non-data descriptor -> Class __dict__ -> Base classes -> __getattr__)?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Python follows a strict 6-stage attribute lookup hierarchy: 1. Data descriptors; 2. Instance __dict__; 3. Non-data descriptors; 4. Class __dict__ / MRO; 5. Base class lookups; 6. __getattr__ fallback.

#### 2. Detailed Answer
When evaluating `obj.attr`, CPython executes `_PyObject_GenericGetAttrWithDict`. It first inspects the class MRO for a data descriptor (has `__set__`); if found, it invokes `__get__`. Next, it checks the instance's own `__dict__`. If missing, it checks for a non-data descriptor in the class MRO (like a method) and calls its `__get__`. If still missing, it checks plain class attributes. If all fail, it raises `AttributeError` and falls back to `obj.__getattr__('attr')`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Demonstrating lookup hierarchy:
class DataDesc:
    def __get__(self, obj, cls): return '1. Data Descriptor'
    def __set__(self, obj, val): pass

class NonDataDesc:
    def __get__(self, obj, cls): return '3. Non-Data Descriptor'

class LookupTarget:
    dd = DataDesc()
    nd = NonDataDesc()
    plain = '4. Class Attribute'

    def __getattr__(self, name):
        return '6. __getattr__ Fallback'

t = LookupTarget()
t.__dict__['dd'] = 'shadow'
t.__dict__['nd'] = '2. Instance Dict'

print('Data descriptor beats instance dict:', t.dd)
print('Instance dict beats non-data descriptor:', t.nd)
print('Class attribute resolved:', t.plain)
print('Missing triggers fallback:', t.nonexistent)
```
*Verifying the 6-stage attribute resolution precedence hierarchy.*

#### 4. Internal Working
Understanding this hierarchy is vital when debugging metaprogramming bugs, custom descriptors, and dynamic ORM proxies.

#### 5. Real-World Use Case
Building custom serialization libraries, dynamic ORMs, and debugging shadow attribute collisions in complex frameworks.

#### 6. Interview Follow-Up Questions
- Why does a data descriptor take precedence over an attribute with the same name in instance `__dict__`?
- Where does `__getattribute__` fit into this hierarchy?

#### 7. Common Interview Mistakes
- Assuming instance attributes always override class descriptors; data descriptors override instance dictionary entries.

#### 8. Interview Tip
Memorize the sequence: Data Descriptor > Instance Dict > Non-Data Descriptor > Class Dict > __getattr__.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access

</details>

---

### PY-INT-069: How can you implement the Singleton pattern safely in Python using '__new__', module caching, or decorators?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A Singleton can be implemented via module caching (idiomatic Pythonic approach), overriding '__new__' with an allocation lock, or using a class decorator; module-level caching is preferred because Python modules are singletons by design.

#### 2. Detailed Answer
In Python, importing a module executes it once and caches it in `sys.modules`. Creating a single instance at module level (`db_client = DatabaseClient()`) provides a clean, thread-safe singleton without boilerplate. When class-level enforcement is required, overriding `__new__` with a `threading.Lock` ensures that only one instance is allocated even under concurrent multi-threaded execution.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                # Double-checked locking pattern
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

s1 = ThreadSafeSingleton()
s2 = ThreadSafeSingleton()
print('Singletons are identical instances:', s1 is s2)  # True
```
*Implementing a thread-safe singleton using double-checked locking in __new__.*

#### 4. Internal Working
Be aware that with `__new__` singletons, Python calls `__init__` EVERY time `Class()` is invoked unless `__init__` guards against re-initialization. Module-level instances avoid this issue entirely.

#### 5. Real-World Use Case
Global configuration registries, thread pools, database connection pools, and hardware device managers.

#### 6. Interview Follow-Up Questions
- Why does `__init__` run multiple times on a `__new__` singleton unless guarded?
- Why are Python modules considered the most idiomatic way to achieve singleton behavior?

#### 7. Common Interview Mistakes
- Implementing a naive `__new__` singleton without thread locking, resulting in race conditions under high concurrent load.

#### 8. Interview Tip
Best practice answer: 'Python modules are already singletons by design; prefer module-level instances over complex `__new__` patterns.'

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/faq/programming.html#how-do-i-share-global-variables-across-modules

</details>

---

### PY-INT-070: What is the Factory pattern in Python and how do class methods provide alternative constructors?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The Factory pattern centralizes object creation without exposing instantiation logic; in Python, '@classmethod' methods provide idiomatic alternative constructors (e.g. from_dict, from_json) that support inheritance polymorphism.

#### 2. Detailed Answer
Unlike languages where constructors must have the same name as the class, Python allows arbitrary named factory methods via `@classmethod`. By taking `cls` as the first argument and returning `cls(...)`, factory methods dynamically construct instances of derived classes when inherited, enabling polymorphic deserialization.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import json

class UserDTO:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    @classmethod
    def from_dict(cls, data: dict):
        # Factory method parsing dictionary
        return cls(username=data['username'], email=data['email'])

    @classmethod
    def from_json(cls, json_str: str):
        # Factory method parsing JSON string
        payload = json.loads(json_str)
        return cls.from_dict(payload)

u = UserDTO.from_json('{"username": "alice", "email": "alice@example.com"}')
print('Constructed from JSON factory:', u.username, u.email)
```
*Implementing alternative constructors using classmethod factories.*

#### 4. Internal Working
Because factory methods return `cls(...)` rather than `UserDTO(...)`, any subclass inheriting these factories will automatically return instances of the subclass without needing to override the factory methods.

#### 5. Real-World Use Case
Parsing API requests into domain DTOs, loading configuration from files/environment variables, and ORM deserialization.

#### 6. Interview Follow-Up Questions
- Why should factory classmethods return `cls(...)` rather than explicitly naming the parent class?
- How does the Abstract Factory pattern differ from simple factory methods?

#### 7. Common Interview Mistakes
- Hardcoding class names inside classmethods (`return UserDTO(...)`), breaking subclass polymorphism.

#### 8. Interview Tip
Always return `cls(...)` in factory classmethods to support subclassing.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#classmethod

</details>

---

### PY-INT-071: What is monkey-patching in Python, how does it work, and what are its production risks?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Monkey-patching is the dynamic modification of a class, function, or module at runtime without altering the original source code, widely used in unit testing for mocks but hazardous in production.

#### 2. Detailed Answer
Because Python's classes and modules are mutable objects in memory, you can rebind attributes at runtime (`TargetClass.method = custom_func`). While useful in test suites (e.g. `unittest.mock.patch`) or hotfixing third-party library bugs, monkey-patching in production creates invisible side effects, race conditions across threads, and makes debugging nearly impossible.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class PaymentService:
    def charge(self, amount: float):
        return f'Charged ${amount} via production gateway'

# Dynamic monkey-patching (e.g. for testing)
def mock_charge(self, amount: float):
    return f'[MOCK] Simulated charge of ${amount}'

# Patching the method on the class at runtime
PaymentService.charge = mock_charge

svc = PaymentService()
print(svc.charge(100.0))  # Calls patched implementation
```
*Monkey-patching a class method dynamically at runtime.*

#### 4. Internal Working
Rebinding a class attribute mutates `Class.__dict__`. Any instance accessing that attribute resolves the newly patched method through normal MRO lookup. Libraries like `gevent` use monkey-patching to replace standard library sockets with greenlet-cooperative sockets.

#### 5. Real-World Use Case
Mocking external HTTP calls in unit tests, instrumentation and profiling (e.g. New Relic, Datadog APM tracing).

#### 6. Interview Follow-Up Questions
- How does `unittest.mock.patch` ensure monkey-patched methods are restored after tests complete?
- Why does gevent monkey-patching need to run as early as possible in application startup?

#### 7. Common Interview Mistakes
- Monkey-patching classes in production without thread synchronization, causing non-deterministic race conditions.

#### 8. Interview Tip
Rule of thumb: use monkey-patching for testing and profiling; strictly avoid it in production business logic.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/unittest.mock.html

</details>

---

### PY-INT-072: How does 'hasattr()' work internally, and why did it catch unexpected exceptions in older Python versions?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'hasattr(obj, name)' evaluates whether an attribute exists by calling 'getattr(obj, name)' and checking if an AttributeError is raised; prior to Python 3.2, it caught and suppressed ALL exceptions.

#### 2. Detailed Answer
Historically, `hasattr()` caught all exceptions (including `KeyError`, `IndexError`, and even `KeyboardInterrupt` or memory errors occurring inside `@property` getters), masking fatal bugs. In Python 3.2+, `hasattr()` specifically catches only `AttributeError`. If an underlying property raises a `ValueError` or custom exception, it now bubbles up as expected.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class DangerousProperty:
    @property
    def status(self):
        raise RuntimeError('Internal hardware failure!')

obj = DangerousProperty()

try:
    # In Python 3.2+, non-AttributeError exceptions are NOT suppressed by hasattr
    hasattr(obj, 'status')
except RuntimeError as e:
    print('hasattr correctly let RuntimeError bubble up:', e)
```
*Demonstrating exception bubbling through hasattr() in modern Python.*

#### 4. Internal Working
`hasattr()` compiles to `PyObject_HasAttrWithError()`. It calls `PyObject_GetAttr()`. If NULL is returned, it inspects `PyErr_Occurred()`. If the exception matches `PyExc_AttributeError`, it clears the error and returns 0; otherwise, it allows the exception to propagate.

#### 5. Real-World Use Case
Defensive programming when inspecting dynamic plugin capabilities or duck-typed API payloads.

#### 6. Interview Follow-Up Questions
- Why did `hasattr()` historically cause bugs in properties with errors?
- What is the difference between `hasattr(obj, 'x')` and `'x' in obj.__dict__`?

#### 7. Common Interview Mistakes
- Relying on `hasattr()` to check dictionary keys instead of using the `in` operator.

#### 8. Interview Tip
Remember: `hasattr()` executes property getters; use `'attr' in obj.__dict__` if you want to check existence without executing code.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#hasattr

</details>

---

### PY-INT-073: How do you implement custom container classes adhering to 'collections.abc.Sequence' or 'collections.abc.MutableMapping'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Inheriting from 'collections.abc' Abstract Base Classes provides rich collection functionality by requiring only a minimal set of core abstract methods while automatically generating all remaining mixin methods.

#### 2. Detailed Answer
Writing a custom mapping from scratch requires implementing over a dozen methods (`keys`, `values`, `items`, `get`, `pop`, `setdefault`, `__contains__`, etc.). By inheriting from `collections.abc.MutableMapping` and implementing only 5 core abstract methods (`__getitem__`, `__setitem__`, `__delitem__`, `__iter__`, `__len__`), Python auto-synthesizes all remaining dictionary methods.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from collections.abc import MutableMapping

class UpperKeyDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self._store[key.upper()]
    def __setitem__(self, key, value):
        self._store[key.upper()] = value
    def __delitem__(self, key):
        del self._store[key.upper()]
    def __iter__(self):
        return iter(self._store)
    def __len__(self):
        return len(self._store)

ud = UpperKeyDict({'a': 1})
# All standard mapping mixin methods work automatically!
ud.setdefault('b', 2)
print('Keys view:', list(ud.keys()))
print('Values view:', list(ud.values()))
print('Pop working:', ud.pop('A'))
```
*Building a custom dictionary with minimal code via collections.abc.MutableMapping.*

#### 4. Internal Working
The ABC uses mixin templates. For example, `get(key, default=None)` is implemented as `try: return self[key] except KeyError: return default`. This guarantees behavioral consistency with standard Python collections.

#### 5. Real-World Use Case
Building custom cache stores (Redis-backed dictionaries, disk-backed sequences), encrypted databases, and audited collections.

#### 6. Interview Follow-Up Questions
- What are the 5 minimal abstract methods required by `collections.abc.MutableMapping`?
- What is the difference between inheriting `collections.abc.MutableMapping` vs `collections.UserDict`?

#### 7. Common Interview Mistakes
- Reimplementing `.keys()`, `.values()`, `.get()`, etc., manually when `collections.abc` generates them for free.

#### 8. Interview Tip
State the design pattern: 'collections.abc provides Mixin methods that save boilerplate and ensure standard protocol compliance.'

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/collections.abc.html

</details>

---

### PY-INT-074: What is the Borg / Monostate pattern in Python and how does it differ from a Singleton?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The Borg (Monostate) pattern allows multiple distinct class instances to be created while sharing the exact same internal state by pointing their '__dict__' to a shared class-level dictionary.

#### 2. Detailed Answer
While a Singleton enforces that only one object instance exists in memory (`id(a) == id(b)`), the Borg pattern emphasizes shared behavior and state over shared identity. All instances of a Borg class have distinct memory addresses (`a is not b`), but they all share the exact same `__dict__`. Mutating an attribute on any instance instantly modifies the state for all instances.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Borg:
    _shared_state = {}

    def __init__(self):
        # Point instance __dict__ to class shared dictionary
        self.__dict__ = self._shared_state

b1 = Borg()
b2 = Borg()

b1.service_status = 'ONLINE'
print('Different identities:', id(b1) != id(b2))  # True
print('Shared state observed:', b2.service_status)  # 'ONLINE'
```
*Sharing internal state across distinct instances using the Borg pattern.*

#### 4. Internal Working
Because `self.__dict__ = self._shared_state`, any attribute access `obj.attr` reads directly from the shared dictionary. This avoids tricky constructor overriding issues seen in `__new__` singletons.

#### 5. Real-World Use Case
Shared logging configuration, global service status monitors, and application settings registries.

#### 6. Interview Follow-Up Questions
- What are the advantages of the Borg pattern over a traditional Singleton?
- What happens if a Borg subclass defines its own `__init__`?

#### 7. Common Interview Mistakes
- Assuming Borg instances have the same identity; `b1 is b2` evaluates to False, but `b1.__dict__ is b2.__dict__` is True.

#### 8. Interview Tip
Highlight Alex Martelli's philosophy: 'Developers care about shared state and behavior, not object identity.'

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html

</details>

---

### PY-INT-075: How does 'weakref.finalize' provide safer cleanup for class instances compared to '__del__'?

**Difficulty:** Intermediate | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'weakref.finalize' registers a cleanup callback that runs when an object is garbage collected without the dangerous resurrection and cyclic GC traps associated with '__del__'.

#### 2. Detailed Answer
Defining `__del__` on classes is dangerous: if an object with `__del__` is part of a reference cycle, older Python versions could not garbage collect it. Furthermore, accessing attributes inside `__del__` during interpreter shutdown often fails because global modules are already cleared. `weakref.finalize(obj, callback, *args)` associates a standalone callback that holds only weak references, ensuring clean finalization without blocking cyclic garbage collection.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import weakref

class TempFileResource:
    def __init__(self, filename: str):
        self.filename = filename
        # Register cleanup callback using weakref.finalize
        self._finalizer = weakref.finalize(self, self._cleanup_file, self.filename)

    @staticmethod
    def _cleanup_file(name: str):
        print(f'Resource finalizer: Deleted temporary file {name}')

# Create resource and destroy strong reference
res = TempFileResource('temp_data.bin')
del res  # Finalizer runs automatically upon GC!
```
*Registering safe object cleanup callbacks via weakref.finalize.*

#### 4. Internal Working
`weakref.finalize` attaches to the object's weak reference list (`tp_weaklistoffset`). When the object's reference count drops to 0, CPython invokes the finalizer before deallocation without resurrecting the instance.

#### 5. Real-World Use Case
Cleaning up OS file descriptors, network sockets, shared memory segments, and temporary disk files.

#### 6. Interview Follow-Up Questions
- Why must the cleanup function passed to `weakref.finalize` NOT be a bound method of `self`?
- What happens if a class defines both `__del__` and `weakref.finalize`?

#### 7. Common Interview Mistakes
- Passing a bound method `self.cleanup` to `weakref.finalize`, which creates a strong reference back to `self` and prevents garbage collection.

#### 8. Interview Tip
Important rule: always pass static methods or module functions to `weakref.finalize` to avoid keeping `self` alive.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/weakref.html#weakref.finalize

</details>

---

## Advanced Level

### PY-ADV-051: What is a Metaclass in Python, how does 'type' act as the default metaclass, and what is the class instantiation lifecycle?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A metaclass is the class of a class, defining how classes themselves are constructed; 'type' is Python's default metaclass, and the class creation lifecycle executes metaclass.__prepare__, metaclass.__new__, and metaclass.__init__.

#### 2. Detailed Answer
In Python, classes are runtime objects. Just as an ordinary object is an instance of a class, every class is an instance of a metaclass (`type(MyClass)` is `type`). When Python encounters a `class` statement, it: 1. Evaluates `metaclass.__prepare__(name, bases)` to get a namespace mapping; 2. Executes the class body inside that namespace; 3. Calls `metaclass.__new__(mcls, name, bases, namespace)` to allocate the `PyTypeObject`; 4. Calls `metaclass.__init__(cls, name, bases, namespace)` to initialize the class.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ValidatingMeta(type):
    def __new__(mcls, name, bases, namespace):
        # Enforce that every service defines an execute method
        if name != 'BaseService' and 'execute' not in namespace:
            raise TypeError(f'Class {name} must define an execute() method')
        return super().__new__(mcls, name, bases, namespace)

class BaseService(metaclass=ValidatingMeta):
    pass

class PaymentService(BaseService):
    def execute(self):
        return 'Payment executed'

print('PaymentService instantiated successfully:', PaymentService().execute())
```
*Creating a custom metaclass to validate subclass method contracts at class definition time.*

#### 4. Internal Working
When an instance is created (`obj = Class()`), Python invokes `type(Class).__call__` (the metaclass's `__call__`), which in turn calls `Class.__new__` and `Class.__init__`. Overriding `__call__` on a metaclass allows complete interception of instance creation (e.g. Singleton pattern).

#### 5. Real-World Use Case
Building declarative ORMs (Django models, SQLAlchemy), serializer registries (Pydantic, Marshmallow), and RPC interface generators.

#### 6. Interview Follow-Up Questions
- What is the difference between `metaclass.__new__` and `metaclass.__init__`?
- How does overriding `__call__` on a metaclass allow implementing a Singleton?

#### 7. Common Interview Mistakes
- Using a metaclass when a simple class decorator or `__init_subclass__` would suffice; metaclasses introduce inheritance friction and complexity.

#### 8. Interview Tip
Quote Tim Peters: 'Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't.'

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#metaclasses

</details>

---

### PY-ADV-052: How does C3 Linearization mathematically resolve inconsistent inheritance hierarchies, and what causes an 'Inconsistent Hierarchy (MRO)' TypeError?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
C3 Linearization merges class inheritance lists using head-and-tail comparisons to guarantee monotonicity; an inconsistent hierarchy TypeError is raised when a cycle or contradictory ordering prevents finding a valid merge candidate.

#### 2. Detailed Answer
At each step in C3, the algorithm searches candidate inheritance lists for a 'good head': a class that is at the head of a list and does NOT appear in the tail (any position after index 0) of any other candidate list. If every candidate head appears in the tail of another list, the merge deadlocks in a cycle, proving that no ordering can preserve both local precedence and monotonicity. CPython then aborts with `TypeError: Cannot create a consistent method resolution order (MRO)`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class X: pass
class Y: pass
class A(X, Y): pass
class B(Y, X): pass  # Inverted order of X and Y!

try:
    # Combining A and B creates an irreconcilable conflict between X and Y
    class Deadlock(A, B): pass
except TypeError as e:
    print('MRO Deadlock caught:', e)
```
*Triggering an MRO cycle conflict where no consistent linearization exists.*

#### 4. Internal Working
Monotonicity means: if class A appears before class B in the MRO of any parent class, class A MUST appear before class B in the MRO of any derived class. Python strictly enforces this to prevent subtle method resolution bugs.

#### 5. Real-World Use Case
Architecting large multi-tenant enterprise software systems with extensive mixin compositions.

#### 6. Interview Follow-Up Questions
- Why did Python switch from its pre-2.3 MRO algorithm to C3 Linearization?
- Can changing the order of classes in a multiple-inheritance declaration resolve an MRO TypeError?

#### 7. Common Interview Mistakes
- Assuming changing declaration order cannot fix MRO errors; swapping `class D(A, B)` to `class D(B, A)` often resolves local precedence conflicts.

#### 8. Interview Tip
Cite the definition of a 'good head' in C3: the head of a list that does not appear in the tail of any other list being merged.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://www.python.org/download/releases/2.3/mro/

</details>

---

### PY-ADV-053: How does CPython implement attribute lookup at the C level ('_PyObject_GenericGetAttrWithDict', 'tp_getattro', 'tp_descr_get')?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
CPython routes attribute lookups through the type slot 'tp_getattro' to '_PyObject_GenericGetAttrWithDict', which coordinates descriptor checks, instance dictionary lookups, and MRO traversal via fast C pointer dereferencing.

#### 2. Detailed Answer
When executing bytecode `LOAD_ATTR`, CPython calls `PyObject_GetAttr(v, name)`. This delegates to `v->ob_type->tp_getattro`. In `_PyObject_GenericGetAttrWithDict`: 1. The type's MRO dictionary is inspected. If a descriptor is found and its `tp_descr_set` is non-NULL (data descriptor), its `tp_descr_get` function is called immediately; 2. Otherwise, `v`'s instance dictionary (`tp_dictoffset`) is probed; 3. If missing from instance dict, any non-data descriptor's `tp_descr_get` is called; 4. If all fail, `PyErr_SetObject(PyExc_AttributeError, name)` is set.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Mental model of CPython C-level attribute lookup:
# 1. descr = _PyType_Lookup(tp, name)
# 2. if descr has tp_descr_set: return descr->tp_descr_get(descr, obj, type)
# 3. if obj->dict has name: return obj->dict[name]
# 4. if descr has tp_descr_get: return descr->tp_descr_get(descr, obj, type)
# 5. if descr: return descr
# 6. raise AttributeError -> fallback to tp_getattr (__getattr__)

class Sample:
    class_val = 'Found in class'

s = Sample()
print('Attribute resolved via C-level MRO lookup:', s.class_val)
```
*Tracing the C-level attribute resolution path in CPython.*

#### 4. Internal Working
CPython optimizes this with an internal method cache (MRO cache). `_PyType_Lookup` uses a global cache keyed by type and attribute name to avoid traversing the MRO tuple on every attribute read.

#### 5. Real-World Use Case
Understanding attribute access latency in performance-critical inner loops; explaining why local variables (`LOAD_FAST`) are faster than attribute lookups (`LOAD_ATTR`).

#### 6. Interview Follow-Up Questions
- Why is accessing a local variable significantly faster than accessing `self.attr` in CPython?
- What is the role of `tp_dictoffset` in PyTypeObject?

#### 7. Common Interview Mistakes
- Caching attributes manually in instance dictionaries without realizing data descriptors bypass the instance dictionary entirely.

#### 8. Interview Tip
Contrast `LOAD_FAST` (direct array indexing in C frame) with `LOAD_ATTR` (descriptor checks, hash lookups, and MRO traversal).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://github.com/python/cpython/blob/main/Objects/object.c

</details>

---

### PY-ADV-054: How do you build an ORM-style declarative model system using metaclasses or '__init_subclass__'?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
An ORM declarative model framework inspects class attributes during class creation, extracts Field descriptors, maps them to database column definitions, and generates a schema mapping.

#### 2. Detailed Answer
In frameworks like Django ORM or SQLAlchemy, models are declared declaratively (`name = CharField()`). When the class is defined, a metaclass (or `__init_subclass__`) iterates through the namespace, identifies all instances of `Field`, records their database column mappings in an internal `_fields` dictionary, and registers table metadata.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.column_name = name.lower()

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj._data.get(self.name)

    def __set__(self, obj, value):
        obj._data[self.name] = value

class Model:
    def __init_subclass__(cls, table_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._table = table_name or cls.__name__.lower() + 's'
        cls._fields = {k: v for k, v in cls.__dict__.items() if isinstance(v, Field)}

    def __init__(self, **kwargs):
        self._data = {}
        for k, v in kwargs.items():
            setattr(self, k, v)

class User(Model, table_name='auth_users'):
    username = Field()
    email = Field()

u = User(username='alice', email='alice@corp.com')
print('Table name:', User._table)
print('Mapped fields:', list(User._fields.keys()))
print('User attributes:', u.username, u.email)
```
*Building a lightweight declarative ORM model using __init_subclass__ and Field descriptors.*

#### 4. Internal Working
By combining `Field` descriptors with `__init_subclass__`, each field captures its attribute name via `__set_name__`, and the model compiles metadata without requiring metaclasses.

#### 5. Real-World Use Case
Building custom data access layers, database abstractions, and declarative configuration parsers.

#### 6. Interview Follow-Up Questions
- How do Django and SQLAlchemy handle model inheritance (abstract base models vs multi-table inheritance)?
- How does `__set_name__` simplify ORM field naming?

#### 7. Common Interview Mistakes
- Modifying class attributes during instance `__init__` rather than registering them once during class construction.

#### 8. Interview Tip
Demonstrate using `__init_subclass__` instead of a metaclass to showcase modern Python 3.6+ idioms.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#customizing-class-creation

</details>

---

### PY-ADV-055: What is the exact C-level mechanism of '__slots__': how does it replace '__dict__' with member descriptors and what are the inheritance pitfalls?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__slots__' instructs CPython to omit '__dict__' from the instance struct and instead reserve fixed memory offsets within the PyObject body, managed by 'member_descriptor' objects.

#### 2. Detailed Answer
A standard PyObject consists of `PyObject_HEAD` followed by pointers. When `__slots__ = ('x', 'y')` is declared, the type allocator computes memory offsets for `x` and `y` immediately following the header. CPython installs a `member_descriptor` for each slot on the class. Reading `obj.x` uses raw C pointer arithmetic (`*(PyObject**)((char*)obj + offset)`), completely bypassing dictionary hashing. However, if a subclass does not declare `__slots__`, it allocates a `__dict__`, negating memory savings.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ParentSlotted:
    __slots__ = ('x',)

class ChildUnslotted(ParentSlotted):
    # Forgets to declare __slots__!
    pass

class ChildSlotted(ParentSlotted):
    __slots__ = ('y',)

cu = ChildUnslotted()
cs = ChildSlotted()

print('Child without slots has __dict__:', hasattr(cu, '__dict__'))  # True (Memory wasted!)
print('Child with slots has NO __dict__:', hasattr(cs, '__dict__'))  # False (Memory saved!)
```
*Illustrating the inheritance pitfall where subclasses re-introduce __dict__ if __slots__ is omitted.*

#### 4. Internal Working
Multiple inheritance with slotted classes is strictly prohibited if more than one base class has non-empty `__slots__` because CPython cannot resolve conflicting memory layout offsets in a single C struct (`TypeError: multiple bases have instance lay-out conflict`).

#### 5. Real-World Use Case
High-frequency algorithmic trading systems, 3D graphics engines, and graph data structures with tens of millions of nodes.

#### 6. Interview Follow-Up Questions
- Why does multiple inheritance fail with `TypeError: multiple bases have instance lay-out conflict` when mixing slotted classes?
- Can a slotted class be weakly referenced by default?

#### 7. Common Interview Mistakes
- Subclassing a slotted class and assuming memory savings propagate automatically; every subclass must explicitly declare `__slots__`.

#### 8. Interview Tip
Remember: Slotted classes cannot support `weakref` unless `'__weakref__'` is explicitly included in `__slots__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/datamodel.html#slots

</details>

---

### PY-ADV-056: How do Split-Table Dictionaries (PEP 412) optimize memory for class instances sharing identical attribute keys?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
PEP 412 shares a single PyDictKeysObject between all instances of a class, storing only instance values in a compact split-value array as long as instances populate attributes in identical order.

#### 2. Detailed Answer
In an application with 500,000 instances of class `Order`, all instances share the exact same attribute keys (`id`, `customer`, `status`, `total`). Under PEP 412, the type's `tp_dict` holds a shared `PyDictKeysObject`. Each instance dictionary is allocated as a 'split table' containing only a flat array of `ma_values` pointers. This saves over 60% of dictionary memory without requiring `__slots__`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Order:
    def __init__(self, order_id: int, total: float):
        # Initializing attributes in the exact same order preserves split tables
        self.order_id = order_id
        self.total = total

o1 = Order(1, 99.5)
o2 = Order(2, 149.0)

print('o1 attributes:', o1.__dict__)
print('o2 attributes:', o2.__dict__)
# Both instances share key table layout behind the scenes!
```
*Preserving split-table optimization by consistently initializing attributes in __init__.*

#### 4. Internal Working
If an instance assigns an attribute outside `__init__`, deletes an attribute, or sets attributes in a different order, CPython breaks the split table for that instance and converts it to a combined dictionary, incurring higher memory overhead.

#### 5. Real-World Use Case
Optimizing memory in web applications with hundreds of thousands of active ORM instances (Django, SQLAlchemy).

#### 6. Interview Follow-Up Questions
- What actions cause an instance dictionary to de-optimize from a split table to a combined table?
- Why must attributes be initialized in the exact same order in `__init__`?

#### 7. Common Interview Mistakes
- Assigning dynamic attributes outside `__init__`, silently breaking split-table sharing across instances.

#### 8. Interview Tip
Best practice: Always initialize all instance attributes inside `__init__` in consistent order to retain PEP 412 split tables.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0412/

</details>

---

### PY-ADV-057: How does CPython implement bound methods vs unbound methods ('PyMethodDescr_Type', 'PyMethod_Type'), and how does method caching optimize access?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
In Python 3, unbound methods are plain functions; bound methods are lightweight 'PyMethod_Type' wrappers created on demand by function descriptors that bind the instance pointer.

#### 2. Detailed Answer
When a function is accessed through an instance (`obj.method`), the function's `__get__` descriptor creates a new `PyMethodObject` wrapping `obj` (`im_self`) and the function (`im_func`). In high-frequency loops, repeatedly creating these bound method objects creates allocation overhead. CPython 3.11+ optimizes this using the `LOAD_METHOD` and `CALL_METHOD` bytecode instructions, which look up the method and instance on the stack without allocating an intermediate `PyMethodObject` unless the method is stored in a variable.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Processor:
    def process(self, value: int) -> int:
        return value * 2

p = Processor()
# Bound method allocated because it is bound to a variable
bound = p.process
print('Bound method instance pointer:', bound.__self__ is p)  # True
print('Underlying function pointer:', bound.__func__ is Processor.process)  # True
```
*Inspecting bound method pointers and function descriptors.*

#### 4. Internal Working
`LOAD_METHOD` checks if the attribute is a function on the class. If so, it pushes the function and `self` onto the evaluation stack directly. `CALL_METHOD` executes the call with zero intermediate object allocations.

#### 5. Real-World Use Case
Writing high-throughput data processing loops and understanding bytecode execution efficiency.

#### 6. Interview Follow-Up Questions
- Why did Python 3 eliminate Python 2's 'unbound method' type?
- How does `LOAD_METHOD` / `CALL_METHOD` avoid allocating a PyMethodObject?

#### 7. Common Interview Mistakes
- Extracting bound methods inside high-frequency loops (`fn = obj.method`) unnecessarily instead of calling directly.

#### 8. Interview Tip
Mention PEP 590 (Vectorcall) and `LOAD_METHOD`: modern CPython avoids allocating `PyMethodObject` for direct calls.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/c-api/method.html

</details>

---

### PY-ADV-058: What are the risks and mechanics of '__del__' (finalizers), resurrection of objects, and why '__del__' historically interfered with cyclic garbage collection?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__del__' is a finalizer called when an object's reference count drops to zero; if an object references itself in '__del__', it can resurrect itself, and historically, cycles containing '__del__' could not be garbage collected (resolved in PEP 442).

#### 2. Detailed Answer
Historically (pre-Python 3.4), if two objects referenced each other and either defined `__del__`, CPython could not determine which finalizer to call first without potentially passing a dangling pointer to the other. Python labeled the cycle uncollectable and dumped it into `gc.garbage`. PEP 442 resolved this by allowing cyclic GC to break cycles after running finalizers in an arbitrary order. However, if `__del__` assigns `self` to a global variable (object resurrection), the object's reference count rises from 0 and it remains alive.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
resurrected_instances = []

class ImmortalZombie:
    def __init__(self, name: str):
        self.name = name

    def __del__(self):
        print(f'Finalizer called for {self.name}; resurrecting!')
        # Object resurrection: storing reference prevents deallocation!
        resurrected_instances.append(self)

z = ImmortalZombie('Lazarus')
del z  # Triggers __del__, but object is resurrected!
print('Object survived destruction:', resurrected_instances[0].name)
```
*Demonstrating dangerous object resurrection inside __del__.*

#### 4. Internal Working
Resurrection is hazardous: CPython does not invoke `__del__` a second time when the resurrected object is eventually destroyed, leading to resource leaks. Exceptions raised inside `__del__` are ignored and printed to `sys.stderr`.

#### 5. Real-World Use Case
Managing low-level C extension handles, file locks, and socket cleanups.

#### 6. Interview Follow-Up Questions
- How did PEP 442 resolve the cyclic garbage collection issue with `__del__`?
- Why is `weakref.finalize` preferred over `__del__` for resource cleanup?

#### 7. Common Interview Mistakes
- Relying on `__del__` for deterministic resource release; use context managers (`with`) instead.

#### 8. Interview Tip
Never use `__del__` for deterministic cleanup: use context managers (`with`) or `weakref.finalize`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0442/

</details>

---

### PY-ADV-059: How do you implement a stateful, thread-safe Object Pool in Python for expensive resources (e.g. database connections, socket handles)?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
An Object Pool manages a fixed set of reusable resources using a thread-safe queue (queue.Queue) and context managers, checking out resources on demand and returning them safely after use.

#### 2. Detailed Answer
Creating and destroying expensive resources (such as database connections or TLS sockets) introduces latency. An Object Pool pre-allocates a fixed pool of connections. Worker threads check out an available resource in thread-safe O(1) time using `queue.Queue.get()`. A context manager ensures that even if an exception occurs during execution, the resource is safely returned to the pool via `queue.Queue.put()`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from queue import Queue
from contextlib import contextmanager

class Connection:
    def __init__(self, conn_id: int):
        self.conn_id = conn_id
    def query(self, sql: str):
        return f'[Conn {self.conn_id}] Result for: {sql}'

class ConnectionPool:
    def __init__(self, size: int):
        self._pool = Queue(maxsize=size)
        for i in range(size):
            self._pool.put(Connection(i + 1))

    @contextmanager
    def acquire(self):
        conn = self._pool.get(block=True, timeout=5)
        try:
            yield conn
        finally:
            self._pool.put(conn)

pool = ConnectionPool(size=2)
with pool.acquire() as c:
    print(c.query('SELECT 1'))
```
*Implementing a robust thread-safe connection pool using Queue and contextmanager.*

#### 4. Internal Working
`queue.Queue` internally uses `threading.Condition` and `collections.deque` to guarantee thread safety without manual mutex locking. If all resources are checked out, calling threads block until a connection is returned or a timeout expires.

#### 5. Real-World Use Case
Database connection pooling in SQLAlchemy/Django, HTTP connection reuse in `urllib3`/`requests`, and worker thread pools.

#### 6. Interview Follow-Up Questions
- What happens if an acquired connection crashes or becomes invalid while checked out?
- How do you handle pool exhaustion when all connections are busy?

#### 7. Common Interview Mistakes
- Failing to return connections to the pool when exceptions occur, exhausting the pool and causing deadlock.

#### 8. Interview Tip
Always wrap pool acquisition in a context manager to guarantee resource return in the `finally` block.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/queue.html

</details>

---

### PY-ADV-060: How does dynamic class generation with 'type(name, bases, dict)' work, and how can classes be constructed programmatically at runtime?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Calling 'type(name, bases, dict)' dynamically creates and returns a new class object at runtime, allowing programmatic construction of types without 'class' syntax.

#### 2. Detailed Answer
The `type` builtin acts as both a type inspection function (with 1 argument) and a class constructor (with 3 arguments): `type(name: str, bases: tuple, dict: dict)`. By passing the class name, a tuple of base classes, and a dictionary of class attributes and methods, you can construct fully functional classes dynamically.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Dynamic function to attach as a method
def dynamic_greet(self):
    return f'Hello, I am {self.name}'

# Construct class dynamically using type()
DynamicUser = type(
    'DynamicUser',
    (object,),
    {
        'role': 'standard_user',
        '__init__': lambda self, name: setattr(self, 'name', name),
        'greet': dynamic_greet
    }
)

u = DynamicUser('Alice')
print('Class name:', u.__class__.__name__)
print('Role attribute:', u.role)
print('Method call:', u.greet())
```
*Programmatically creating a class using the 3-argument form of type().*

#### 4. Internal Working
When `type(name, bases, dict)` is called, CPython executes `type_new()`. It allocates a `PyTypeObject`, initializes its `tp_dict`, resolves the MRO via C3 linearization, and returns the newly minted class.

#### 5. Real-World Use Case
Dynamic schema generation in ORMs, converting OpenAPI/JSON Schema specs into Python classes, and code generation frameworks.

#### 6. Interview Follow-Up Questions
- How do you specify a custom metaclass when using `type()` dynamically?
- How does `namedtuple` internally use dynamic class construction?

#### 7. Common Interview Mistakes
- Passing a list instead of a tuple for `bases` in `type()`, raising a TypeError.

#### 8. Interview Tip
Remember: `bases` must be a tuple: `(BaseClass,)`, not `BaseClass` or `[BaseClass]`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/functions.html#type

</details>

---

### PY-ADV-061: What is '__prepare__' in metaclasses and how does it enable class definitions with custom namespaces?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'__prepare__' is a class method on a metaclass that returns a custom mapping (namespace) used to store class body attributes while the class body is being executed.

#### 2. Detailed Answer
Normally, Python evaluates class bodies inside a standard dictionary. By defining `@classmethod def __prepare__(mcls, name, bases, **kwargs):`, a metaclass can return a custom mapping (like `collections.OrderedDict` or a tracking dictionary). As Python parses each line of the class body, assignments write directly into this custom mapping, allowing capture of declaration order or duplicate attribute definitions.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class DuplicateTrackingNamespace(dict):
    def __setitem__(self, key, value):
        if key in self:
            print(f'[WARN] Duplicate attribute definition detected: {key}')
        super().__setitem__(key, value)

class StrictMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases):
        # Return custom namespace for class body execution
        return DuplicateTrackingNamespace()

    def __new__(mcls, name, bases, namespace):
        return super().__new__(mcls, name, bases, dict(namespace))

class Config(metaclass=StrictMeta):
    timeout = 30
    timeout = 60  # Triggers duplicate warning!
```
*Using __prepare__ to detect duplicate attribute declarations in a class body.*

#### 4. Internal Working
CPython invokes `__prepare__` before compiling the class body AST. The returned mapping is passed to `PyEval_EvalCode` as the local namespace.

#### 5. Real-World Use Case
Used in `enum.Enum` to record member declaration order and in serialization frameworks to enforce schema ordering.

#### 6. Interview Follow-Up Questions
- Why did Enum historically require `__prepare__` before Python 3.7 guaranteed dictionary insertion order?
- Can `__prepare__` accept keyword arguments passed in the class definition header?

#### 7. Common Interview Mistakes
- Returning a non-mapping from `__prepare__`, which raises a TypeError.

#### 8. Interview Tip
Mention `enum.Enum`: it was the classic motivating use case for PEP 3115 `__prepare__`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-3115/

</details>

---

### PY-ADV-062: How does Python 3.10+ match-case class pattern matching interact with '__match_args__' and positional pattern decomposition?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Structural pattern matching maps positional arguments in class patterns ('case Point(x, y):') to attribute names defined in the class's '__match_args__' tuple.

#### 2. Detailed Answer
When matching instances of user-defined classes in `match-case`, Python supports keyword patterns (`case Point(x=10, y=20):`) by default. To support concise positional patterns (`case Point(10, 20):`), the class must define `__match_args__ = ('x', 'y')`. Python maps positional pattern parameters to the attribute names listed in `__match_args__` in order. Dataclasses generate `__match_args__` automatically.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class GeoPoint:
    __match_args__ = ('lat', 'lon')
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

def analyze_location(point):
    match point:
        case GeoPoint(0.0, 0.0):
            return 'Equator / Prime Meridian Intersection'
        case GeoPoint(lat, lon) if lat > 0:
            return f'Northern Hemisphere: {lat}, {lon}'
        case _:
            return 'Other Location'

print(analyze_location(GeoPoint(0.0, 0.0)))
print(analyze_location(GeoPoint(45.5, -73.5)))
```
*Pattern matching custom classes using positional __match_args__.*

#### 4. Internal Working
The compiler emits bytecode checking `isinstance(obj, GeoPoint)`. It then extracts attributes named in `__match_args__` and matches them against the pattern guards.

#### 5. Real-World Use Case
Abstract Syntax Tree (AST) node transformations, domain event dispatching, and algebraic data type decomposition.

#### 6. Interview Follow-Up Questions
- What does `@dataclass` automatically generate for `__match_args__`?
- What happens if a positional pattern provides more arguments than defined in `__match_args__`?

#### 7. Common Interview Mistakes
- Omitting `__match_args__` on custom classes and attempting positional pattern matching, causing a TypeError.

#### 8. Interview Tip
Note: `@dataclass` auto-generates `__match_args__` based on field declaration order.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/reference/compound_stmts.html#class-patterns

</details>

---

### PY-ADV-063: How do you implement a Dependency Injection (DI) container with autowiring using Python type hints and class introspection?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A DI container inspects class constructor type annotations using 'inspect.signature()' and automatically instantiates and injects registered dependencies recursively.

#### 2. Detailed Answer
Modern backend frameworks (like FastAPI) rely on Dependency Injection to decouple components. An autowiring DI container maintains a registry of services. When a class is requested, the container inspects its `__init__` parameters via `inspect.signature()`, resolves each parameter's type annotation against its registry, recursively instantiates any child dependencies, and injects them into the constructor.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import inspect

class Container:
    def __init__(self):
        self._services = {}

    def register(self, cls):
        self._services[cls] = cls

    def resolve(self, cls):
        if cls not in self._services:
            raise ValueError(f'Service {cls} not registered')
        sig = inspect.signature(cls.__init__)
        dependencies = {}
        for name, param in sig.parameters.items():
            if name == 'self': continue
            dep_cls = param.annotation
            dependencies[name] = self.resolve(dep_cls)
        return cls(**dependencies)

class Database: pass
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

container = Container()
container.register(Database)
container.register(UserRepository)
repo = container.resolve(UserRepository)
print('Successfully autowired repo with db:', isinstance(repo.db, Database))
```
*Building an autowiring Dependency Injection container using inspect.signature.*

#### 4. Internal Working
`inspect.signature(cls)` extracts parameter names and their evaluated `param.annotation` objects. The container recursively resolves the dependency graph using topological sort or depth-first instantiation.

#### 5. Real-World Use Case
Underlying architecture of modern web frameworks (FastAPI dependency system), enterprise DDD services, and test harness mocks.

#### 6. Interview Follow-Up Questions
- How do you resolve circular dependencies in a Dependency Injection container?
- How does `typing.get_type_hints()` handle forward references (strings like `'Database'`)?

#### 7. Common Interview Mistakes
- Using `cls.__annotations__` directly instead of `inspect.signature()` or `typing.get_type_hints()`, which fails on inherited constructors.

#### 8. Interview Tip
Always use `inspect.signature()` or `typing.get_type_hints()` for robust dependency introspection.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/inspect.html#inspect.signature

</details>

---

### PY-ADV-064: What is the Visitor pattern in Python and how does 'ast.NodeVisitor' / 'ast.NodeTransformer' use dynamic method dispatch?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The Visitor pattern separates an algorithm from the object structure it operates on; in Python, it uses dynamic method dispatch ('getattr(self, f'visit_{node_type}')') to route processing based on node type.

#### 2. Detailed Answer
When processing complex heterogeneous object trees (like an Abstract Syntax Tree or document node tree), writing giant `if-elif` type-checking chains violates the Open/Closed Principle. In Python's `ast.NodeVisitor`, the base visitor's `visit(node)` method dynamically looks up and invokes a method named `f'visit_{type(node).__name__}'`. Subclasses simply define methods for the specific node types they care about.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class Node:
    pass
class HeaderNode(Node):
    def __init__(self, text): self.text = text
class ParagraphNode(Node):
    def __init__(self, text): self.text = text

class MarkdownExporter:
    def visit(self, node):
        # Dynamic dispatch based on class name
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return f'[UNHANDLED: {type(node).__name__}]'

    def visit_HeaderNode(self, node):
        return f'# {node.text}'

    def visit_ParagraphNode(self, node):
        return f'{node.text}\n'

exporter = MarkdownExporter()
print(exporter.visit(HeaderNode('Welcome')))
print(exporter.visit(ParagraphNode('Content body')))
```
*Dynamic method dispatch implementing the Visitor pattern in Python.*

#### 4. Internal Working
`getattr()` performs fast C-level dictionary lookup. If a specialized visitor method is found, it is called; otherwise, `generic_visit` recursively visits child nodes.

#### 5. Real-World Use Case
Python's `ast` module (AST linters like Flake8, Ruff), compiler transformations, code formatting tools (Black), and document conversion engines.

#### 6. Interview Follow-Up Questions
- What is the difference between `ast.NodeVisitor` (read-only) and `ast.NodeTransformer` (modifies AST)?
- Why is dynamic method dispatch in Python cleaner than the double-dispatch required in Java/C++?

#### 7. Common Interview Mistakes
- Failing to call `generic_visit(node)` in custom AST visitors, causing child nodes to be skipped during traversal.

#### 8. Interview Tip
Contrast Python's simple dynamic dispatch via `getattr()` with Java's complex double-dispatch visitor pattern.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/ast.html#ast.NodeVisitor

</details>

---

### PY-ADV-065: How can you intercept and instrument all method calls on a class dynamically using metaclasses or class decorators (AOP)?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Aspect-Oriented Programming (AOP) intercepts method calls to inject cross-cutting concerns (logging, timing, tracing); in Python, a class decorator or metaclass iterates over attributes and wraps callables with decorators.

#### 2. Detailed Answer
Cross-cutting concerns like execution timing, distributed tracing, and permission checks shouldn't be duplicated inside every method. A class decorator inspects the class attributes during definition time, identifies all callable methods, and wraps them in a timing/logging decorator transparently.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import time
from functools import wraps

def instrument_methods(cls):
    for name, attr in cls.__dict__.items():
        if callable(attr) and not name.startswith('__'):
            @wraps(attr)
            def timed_wrapper(*args, method_name=name, func=attr, **kwargs):
                t0 = time.perf_counter()
                res = func(*args, **kwargs)
                elapsed = (time.perf_counter() - t0) * 1000
                print(f'[METRICS] {cls.__name__}.{method_name} took {elapsed:.2f}ms')
                return res
            setattr(cls, name, timed_wrapper)
    return cls

@instrument_methods
class CalculationService:
    def compute_sum(self, n: int) -> int:
        return sum(range(n))

svc = CalculationService()
print('Result:', svc.compute_sum(100_000))
```
*Auto-instrumenting all class methods with execution timing via a class decorator.*

#### 4. Internal Working
Iterating over `cls.__dict__.items()` targets attributes defined directly on the class. To avoid breaking method binding, decorators wrap methods and rebind them onto the class using `setattr(cls, name, wrapper)`.

#### 5. Real-World Use Case
Distributed tracing in APM tools (Datadog, OpenTelemetry, New Relic), automatic database retry policies, and authorization checks.

#### 6. Interview Follow-Up Questions
- Why is a class decorator usually preferred over a metaclass for method instrumentation?
- How do you handle `@classmethod` and `@staticmethod` when auto-instrumenting class methods?

#### 7. Common Interview Mistakes
- Wrapping attributes without checking `callable(attr)`, which breaks non-callable properties and attributes.

#### 8. Interview Tip
Always check `callable(attr)` and ignore dunder methods (`not name.startswith('__')`) when auto-wrapping.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/glossary.html#term-decorator

</details>

---

### PY-ADV-066: How do abstract properties and abstract class methods interact in ABCs, and how does 'abc.ABCMeta' validate them?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
In ABCs, '@abstractmethod' must be placed as the innermost decorator directly above the method definition when combining with '@property' or '@classmethod'; ABCMeta validates that all abstract descriptors are implemented before allowing instantiation.

#### 2. Detailed Answer
When defining an abstract property or abstract classmethod, decorator stacking order matters. `@property` or `@classmethod` must be the outer decorator, and `@abstractmethod` must be the innermost decorator: `@property 
 @abstractmethod`. `ABCMeta` scans the class namespace, identifies all descriptors marked with `__isabstractmethod__ = True`, and collects them in `__abstractmethods__`. If any remain unimplemented in a subclass, instantiation is blocked.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from abc import ABC, abstractmethod

class BaseConfig(ABC):
    @property
    @abstractmethod
    def database_url(self) -> str:
        """Abstract property that must be provided by subclasses."""
        pass

class ProdConfig(BaseConfig):
    @property
    def database_url(self) -> str:
        return 'postgresql://user:pass@db.prod.internal:5432/app'

cfg = ProdConfig()
print('Abstract property implemented:', cfg.database_url)
```
*Declaring and implementing abstract properties in an ABC.*

#### 4. Internal Working
The `@abstractmethod` decorator sets the function attribute `__isabstractmethod__ = True`. When wrapped by `@property`, the property object propagates this flag to its own `__isabstractmethod__` attribute. `ABCMeta` checks this attribute on descriptors.

#### 5. Real-World Use Case
Enforcing configuration models, read-only hardware drivers, and standardized microservice identity properties.

#### 6. Interview Follow-Up Questions
- What happens if you invert the decorator order (`@abstractmethod 
 @property`)?
- Can an abstract property define both an abstract getter and an abstract setter?

#### 7. Common Interview Mistakes
- Placing `@abstractmethod` outside `@property`, which fails to set `__isabstractmethod__` correctly in older Python versions.

#### 8. Interview Tip
Remember decorator order: `@property` on the outside, `@abstractmethod` on the inside.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/abc.html#abc.abstractmethod

</details>

---

### PY-ADV-067: What is the internal memory difference between standard class instances, '@dataclass(slots=True)', and 'typing.NamedTuple'?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Standard classes store attributes in a heap '__dict__' with pointer indirection (~152 bytes); '@dataclass(slots=True)' uses C struct member offsets without '__dict__' (~48 bytes); 'typing.NamedTuple' is an immutable tuple allocated in a single contiguous C block (~48 bytes).

#### 2. Detailed Answer
In a standard class, memory includes: 1. `PyObject` header (16 bytes); 2. Pointer to `__dict__` (8 bytes); 3. The `PyDictObject` (100+ bytes); 4. The actual attribute pointers. `@dataclass(slots=True)` (Python 3.10+) eliminates `__dict__` and `__weakref__`, placing pointers directly in the instance struct. `NamedTuple` is a tuple subclass that embeds values directly in the `ob_item` array of the tuple.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import sys
from dataclasses import dataclass
from typing import NamedTuple

class StandardUser:
    def __init__(self, uid: int, score: float):
        self.uid, self.score = uid, score

@dataclass(slots=True)
class SlottedUser:
    uid: int
    score: float

class TupleUser(NamedTuple):
    uid: int
    score: float

u_std = StandardUser(1, 98.5)
u_slot = SlottedUser(1, 98.5)
u_tup = TupleUser(1, 98.5)

print('Standard class memory (with __dict__):', sys.getsizeof(u_std) + sys.getsizeof(u_std.__dict__), 'bytes')
print('Slotted dataclass memory:', sys.getsizeof(u_slot), 'bytes')
print('NamedTuple memory:', sys.getsizeof(u_tup), 'bytes')
```
*Measuring exact memory differences across class architectures.*

#### 4. Internal Working
While `SlottedUser` and `TupleUser` have similar memory footprints, `SlottedUser` allows mutable fields while `TupleUser` is strictly immutable. Both avoid hash table overhead during attribute lookup.

#### 5. Real-World Use Case
Architecting high-scale backend services processing millions of events or records in RAM.

#### 6. Interview Follow-Up Questions
- Why does `@dataclass(slots=True)` outperform NamedTuple when field mutability is required?
- Can you add new attributes dynamically to a `@dataclass(slots=True)` instance?

#### 7. Common Interview Mistakes
- Using standard classes to hold 10,000,000 records in memory, consuming gigabytes of RAM due to `__dict__` overhead.

#### 8. Interview Tip
For modern Python 3.10+: recommend `@dataclass(slots=True)` as the default choice for high-performance domain models.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass

</details>

---

### PY-ADV-068: How do you implement a custom descriptor that enforces runtime type validation and database constraints?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
A custom data descriptor validates types and values inside '__set__' before persisting them to a private instance attribute, and uses '__set_name__' to bind to the attribute name dynamically.

#### 2. Detailed Answer
Instead of repeating type-checking boilerplate in every setter, you can write reusable descriptor validators. When an assignment occurs (`obj.attr = val`), the descriptor's `__set__` method checks type constraints (e.g. `isinstance(val, int)`), range limits (e.g. `val > 0`), and custom invariants, raising a `TypeError` or `ValueError` if validation fails.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class IntegerField:
    def __init__(self, min_val: int = None, max_val: int = None):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.storage_name = f'_{name}'

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError(f'Attribute must be an int, got {type(value).__name__}')
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f'Value must be >= {self.min_val}')
        setattr(obj, self.storage_name, value)

class InventoryItem:
    stock = IntegerField(min_val=0)

item = InventoryItem()
item.stock = 15
print('Valid stock assignment:', item.stock)

try:
    item.stock = -5  # Triggers validation
except ValueError as e:
    print('Validation successfully blocked invalid value:', e)
```
*Building a reusable validation descriptor with type and range enforcement.*

#### 4. Internal Working
Because `IntegerField` defines `__set__`, it is a data descriptor. It takes precedence over `obj.__dict__`. Storing the value under `self.storage_name` (`_stock`) prevents infinite recursion.

#### 5. Real-World Use Case
Enforcing domain invariants in clean architecture models, custom ORMs, and settings validation.

#### 6. Interview Follow-Up Questions
- Why must the descriptor store the validated value in the instance (`getattr/setattr`), rather than on `self`?
- What happens if a descriptor stores data on `self` when multiple instances of the class exist?

#### 7. Common Interview Mistakes
- Storing instance values on `self` inside the descriptor (`self.val = val`), causing all instances to share the exact same value.

#### 8. Interview Tip
Golden rule of descriptors: Never store instance-specific data in the descriptor itself; store it in the target instance (`obj`).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/howto/descriptor.html#complete-practical-example

</details>

---

### PY-ADV-069: What are the architectural trade-offs between Metaclasses vs '__init_subclass__' vs Class Decorators?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Class decorators are the simplest and modify classes post-creation; '__init_subclass__' cleanly hooks subclass creation without metaclass conflict; Metaclasses provide maximum control (custom namespaces, __new__) but suffer from metaclass conflict in multiple inheritance.

#### 2. Detailed Answer
Class decorators cannot be inherited by subclasses automatically. `__init_subclass__` is inherited automatically down the entire inheritance hierarchy and provides clean keyword arguments without metaclass complexity. Metaclasses are necessary ONLY when you must customize the class namespace (`__prepare__`), intercept class allocation before the class object exists (`__new__`), or customize instance creation via `metaclass.__call__`. However, combining classes with different metaclasses causes `TypeError: metaclass conflict`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Comparison Summary:
# Class Decorator:   Post-creation mutation, NOT inherited, simple.
# __init_subclass__: Inherited automatically, no conflicts, ideal for 90% of frameworks.
# Metaclass:         Custom namespace (__prepare__), pre-creation allocation, high complexity.

class Parent:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registered = True

class Child(Parent): pass
print('__init_subclass__ inherited by child:', Child.registered)  # True
```
*Comparing metaprogramming mechanisms in Python architecture.*

#### 4. Internal Working
Metaclass conflict occurs when class C inherits from A (metaclass M1) and B (metaclass M2), where neither M1 nor M2 is a subclass of the other. Resolving it requires synthesizing a hybrid metaclass.

#### 5. Real-World Use Case
Designing extensible open-source libraries, API frameworks, and SDKs.

#### 6. Interview Follow-Up Questions
- What is a 'metaclass conflict' and how can it be resolved?
- Why can't class decorators affect classes created dynamically via inheritance?

#### 7. Common Interview Mistakes
- Choosing a metaclass when `__init_subclass__` can achieve the exact same goal without inheritance friction.

#### 8. Interview Tip
Hierarchy of choice: 1. Class decorator -> 2. `__init_subclass__` -> 3. Metaclass (only if `__prepare__` or `__call__` is required).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0487/

</details>

---

### PY-ADV-070: How does Python handle multiple inheritance when mixing cooperative 'super()' classes with non-cooperative legacy third-party classes?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Mixing cooperative classes with non-cooperative classes breaks the MRO chain; resolving it requires creating an Adapter wrapper class that calls super() and swallows excess kwargs.

#### 2. Detailed Answer
In cooperative multiple inheritance, every class in the chain must call `super().method(*args, **kwargs)` to forward execution to the next class in the MRO. If a third-party class does not use `super()` or accepts only specific positional arguments, the chain terminates prematurely. The solution is the Adapter pattern: create an intermediate adapter class that intercepts the call, converts arguments, calls the third-party method, and explicitly calls `super()` to keep the chain alive.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
class ThirdPartyWorker:
    def execute(self, task_id: int):  # Non-cooperative: no super(), rigid args
        print(f'ThirdPartyWorker executed {task_id}')

class WorkerAdapter(ThirdPartyWorker):
    def execute(self, task_id: int, **kwargs):
        # Call non-cooperative parent
        super().execute(task_id)
        # Resume cooperative chain for remaining classes in MRO
        next_in_mro = super(ThirdPartyWorker, self)
        if hasattr(next_in_mro, 'execute'):
            next_in_mro.execute(**kwargs)

print('Adapter bridges cooperative and non-cooperative MRO chains successfully.')
```
*Building an adapter class to prevent broken cooperative inheritance chains.*

#### 4. Internal Working
Cooperation requires that the terminal class (`object`) defines the method or that a base class consumes `**kwargs` to prevent `TypeError: object.__init__() takes exactly one argument`.

#### 5. Real-World Use Case
Integrating third-party GUI or database packages into modern cooperative backend architectures.

#### 6. Interview Follow-Up Questions
- Why does `object.__init__` raise a TypeError if `**kwargs` are passed to it?
- What is the role of `**kwargs` in cooperative multiple inheritance?

#### 7. Common Interview Mistakes
- Failing to consume `**kwargs` before `super()` reaches `object.__init__`, causing runtime crashes.

#### 8. Interview Tip
Always design cooperative base classes to accept `**kwargs` and pass them to `super()`.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://rhettinger.wordpress.com/2011/05/26/super-considered-super/

</details>

---

### PY-ADV-071: How do you prevent subclassing of a class (final classes) using 'typing.final' and runtime metaclass enforcement?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
'typing.final' (PEP 591) statically informs type checkers that a class or method cannot be subclassed or overridden; runtime enforcement requires a metaclass or '__init_subclass__' that raises a TypeError if subclassed.

#### 2. Detailed Answer
Python has no built-in `final` keyword. The `@typing.final` decorator signals to static analyzers (Mypy, Pyright) that subclassing is prohibited. To enforce this at runtime, the class can implement `__init_subclass__` that unconditionally raises a `TypeError` whenever any class inherits from it.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from typing import final

class SealedBase:
    def __init_subclass__(cls, **kwargs):
        raise TypeError(f'Subclassing {cls.__name__} is strictly prohibited (Final class)')

@final
class SecurityContext(SealedBase):
    def __init__(self, token: str):
        self.token = token

# Instantiation works
ctx = SecurityContext('valid_token')
print('Final class instantiated:', ctx.token)

try:
    # Subclassing triggers runtime error
    class MaliciousSubclass(SecurityContext):
        pass
except TypeError as e:
    print('Subclassing successfully blocked at runtime:', e)
```
*Enforcing final classes statically with @final and at runtime via __init_subclass__.*

#### 4. Internal Working
`@typing.final` sets `__final__ = True` on the decorated class. Metaclasses can inspect this attribute during `__new__` and abort class creation if a parent class has `__final__ = True`.

#### 5. Real-World Use Case
Security tokens, cryptographic key contexts, and immutable system primitives that must never be altered by inheritance.

#### 6. Interview Follow-Up Questions
- Why is static enforcement via `@final` preferred over runtime metaclass blocking in performance-critical code?
- Can individual methods be marked final using `@final`?

#### 7. Common Interview Mistakes
- Assuming `@final` blocks subclassing at runtime by itself; `@final` is purely a static type-checker hint without runtime enforcement.

#### 8. Interview Tip
Combine `@typing.final` (for Mypy/IDE) with `__init_subclass__` (for runtime enforcement).

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0591/

</details>

---

### PY-ADV-072: What is the Flyweight design pattern and how do you implement it in Python using '__new__' and weak references to minimize memory?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
The Flyweight pattern shares immutable state across thousands of fine-grained objects by maintaining a factory or cache in '__new__' that returns existing identical instances, using weak references to allow unused instances to be collected.

#### 2. Detailed Answer
When an application manages hundreds of thousands of objects that share identical intrinsic state (e.g. font glyphs, tree types in a game, currency representations), allocating distinct instances wastes memory. By overriding `__new__` and querying a `weakref.WeakValueDictionary`, the class returns an existing instance if one with matching parameters is already in memory.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import weakref

class FlyweightColor:
    _pool = weakref.WeakValueDictionary()

    def __new__(cls, r: int, g: int, b: int):
        key = (r, g, b)
        instance = cls._pool.get(key)
        if instance is None:
            instance = super().__new__(cls)
            instance.r, instance.g, instance.b = r, g, b
            cls._pool[key] = instance
        return instance

c1 = FlyweightColor(255, 0, 0)
c2 = FlyweightColor(255, 0, 0)
print('Identical instance reused:', c1 is c2)  # True
print('Total pool size:', len(FlyweightColor._pool))  # 1
```
*Implementing the Flyweight pattern with WeakValueDictionary in __new__.*

#### 4. Internal Working
`WeakValueDictionary` ensures that when all external references to a Flyweight object are dropped, the cache entry is automatically deleted, preventing the pool from leaking memory.

#### 5. Real-World Use Case
Game engines (rendering millions of terrain tiles or bullets), text processing editors (formatting characters), and astronomical data simulations.

#### 6. Interview Follow-Up Questions
- Why is `weakref.WeakValueDictionary` critical to prevent memory leaks in Flyweight pools?
- How does Flyweight differ from the Singleton pattern?

#### 7. Common Interview Mistakes
- Using a standard dictionary for the flyweight pool, which keeps every object alive forever and causes memory leaks.

#### 8. Interview Tip
Always use `weakref.WeakValueDictionary` for flyweight caches so unreferenced objects are automatically garbage collected.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://en.wikipedia.org/wiki/Flyweight_pattern

</details>

---

### PY-ADV-073: How does CPython's specialized bytecode interpreter (PEP 659 / PEP 709) optimize method calls via inline caches?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Python 3.11+ introduces an Adaptive Specializing Interpreter (PEP 659) that dynamically replaces generic opcodes (like LOAD_ATTR) with specialized quickened opcodes (like LOAD_ATTR_METHOD) using inline caches.

#### 2. Detailed Answer
In Python 3.11+, bytecodes start in a generic state. When an instruction like `LOAD_ATTR` executes repeatedly at a specific code offset, the interpreter profiles the target type. If the type is stable, CPython overwrites the instruction with specialized opcodes (`LOAD_ATTR_INSTANCE_VALUE`, `LOAD_ATTR_MODULE`, `LOAD_ATTR_METHOD`). Inline cache entries store the exact dictionary offset and type version tag, allowing attribute and method lookups to bypass hash table searches and execute in 1-2 CPU instructions.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import dis

class MathService:
    def add(self, a: int, b: int) -> int:
        return a + b

def benchmark_loop(svc, n: int):
    total = 0
    for _ in range(n):
        total = svc.add(total, 1)  # Adaptive interpreter optimizes this method call!
    return total

# Running loop warms up specialized inline caches
svc = MathService()
print('Loop result:', benchmark_loop(svc, 10_000))
print('Disassembly reveals optimized bytecode caching:')
dis.dis(benchmark_loop)
```
*Observing bytecode structure optimized by Python's adaptive specializing interpreter.*

#### 4. Internal Working
Each specialized instruction has associated inline cache entries (`_PyAdaptiveInterpreterCache`). If the type version tag changes (e.g. monkey-patching or passing an unexpected class), the instruction de-optimizes back to generic execution.

#### 5. Real-World Use Case
Explaining why Python 3.11 and 3.12 are 25-50% faster than Python 3.10 for standard object-oriented code.

#### 6. Interview Follow-Up Questions
- What happens when an inline cache encounters a type mismatch (de-optimization)?
- How do specialized opcodes verify that a class attribute has not been mutated?

#### 7. Common Interview Mistakes
- Assuming Python bytecode is completely static; modern CPython bytecodes adaptively mutate at runtime.

#### 8. Interview Tip
Mention PEP 659 'Specializing Adaptive Interpreter' and inline caching as the core engine behind Python 3.11+ speedups.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://peps.python.org/pep-0659/

</details>

---

### PY-ADV-074: How do you implement a distributed Event Bus / Observer pattern with asynchronous subscriber handlers and weak references to prevent subscriber leaks?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
An Event Bus coordinates decoupled event publication and subscription; using 'weakref.WeakMethod' ensures that subscriber objects can be garbage collected without lingering references in the event registry.

#### 2. Detailed Answer
In event-driven architectures, subscribers register callbacks with a central Event Bus. If the Event Bus stores standard strong references to bound methods (`subscriber.on_event`), the subscriber instance can NEVER be garbage collected as long as the Event Bus lives (Lapsed Listener problem). Wrapping callbacks in `weakref.WeakMethod` allows subscribers to be deallocated naturally, and dead callbacks are automatically pruned.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import weakref

class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type: str, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        # Use WeakMethod for bound instance methods to prevent memory leaks
        self._subscribers[event_type].append(weakref.WeakMethod(callback))

    def publish(self, event_type: str, data):
        if event_type not in self._subscribers:
            return
        live_callbacks = []
        for ref in self._subscribers[event_type]:
            cb = ref()
            if cb is not None:
                cb(data)
                live_callbacks.append(ref)
        # Prune dead subscribers
        self._subscribers[event_type] = live_callbacks

class AuditListener:
    def handle(self, event):
        print(f'Audited event: {event}')

bus = EventBus()
listener = AuditListener()
bus.subscribe('user_login', listener.handle)
bus.publish('user_login', {'user': 'alice'})

del listener  # Listener collected; EventBus will auto-prune!
bus.publish('user_login', {'user': 'bob'})
```
*Building a leak-free Event Bus using weakref.WeakMethod and automatic pruning.*

#### 4. Internal Working
`weakref.WeakMethod` is specialized for bound methods, tracking both the underlying function and the instance weakly. Standard `weakref.ref` on a bound method immediately dies because the bound method object is temporary.

#### 5. Real-World Use Case
UI component communication, microservice domain event publishing, and background telemetry collection.

#### 6. Interview Follow-Up Questions
- Why does `weakref.ref(instance.method)` fail while `weakref.WeakMethod(instance.method)` succeeds?
- What is the 'Lapsed Listener' problem in long-running services?

#### 7. Common Interview Mistakes
- Storing bound methods in a global event registry with strong references, causing massive memory leaks in long-running applications.

#### 8. Interview Tip
Key distinction: Always use `weakref.WeakMethod` (not `weakref.ref`) when weakly referencing instance methods.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/weakref.html#weakref.WeakMethod

</details>

---

### PY-ADV-075: How do you safely serialize and deserialize complex polymorphic class hierarchies with circular references using 'pickle' or custom JSON encoders?

**Difficulty:** Advanced | **Topic:** Object-Oriented Programming

#### 1. One-Line Answer
Custom serialization of complex hierarchies is achieved by implementing '__reduce__' or '__getstate__' / '__setstate__' for pickle, or a custom Type-Tagged JSON Encoder/Decoder that preserves class metadata.

#### 2. Detailed Answer
Standard `json.dumps()` fails on custom class instances. `pickle` handles arbitrary Python objects and circular references natively by recording opcode instructions that reconstruct object graphs. To customize pickle serialization (e.g. omitting sensitive keys, database connections), implement `__getstate__` and `__setstate__` or `__reduce__`. For interoperable JSON, custom encoders embed a type tag (`__type__: 'ClassName'`) that the decoder uses to instantiate the proper class.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import json

class Entity:
    def __init__(self, entity_id: int, name: str):
        self.entity_id = entity_id
        self.name = name

class EntityJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return {'__type__': obj.__class__.__name__, 'entity_id': obj.entity_id, 'name': obj.name}
        return super().default(obj)

def entity_decoder(dct):
    if '__type__' in dct and dct['__type__'] == 'Entity':
        return Entity(dct['entity_id'], dct['name'])
    return dct

e = Entity(101, 'OrderAggregate')
serialized = json.dumps(e, cls=EntityJSONEncoder)
print('Serialized JSON with type tag:', serialized)

restored = json.loads(serialized, object_hook=entity_decoder)
print('Restored polymorphic entity:', restored.name, type(restored).__name__)
```
*Serializing and deserializing polymorphic domain entities using type-tagged JSON.*

#### 4. Internal Working
`pickle`'s `__reduce__` protocol returns a tuple containing a callable and arguments: `(cls, (*args,))`. During unpickling, Python invokes the callable to recreate the object without calling `__init__`, resolving circular pointers via memoization tables.

#### 5. Real-World Use Case
Distributed caching (Celery task arguments, Redis object caching), inter-process communication, and event sourcing event stores.

#### 6. Interview Follow-Up Questions
- Why is `pickle` insecure for deserializing untrusted user inputs (arbitrary code execution)?
- What is the role of `__reduce__` in customizing pickle serialization?

#### 7. Common Interview Mistakes
- Using `pickle.loads()` on untrusted API request payloads; an attacker can execute arbitrary remote shell commands via `__reduce__`.

#### 8. Interview Tip
Security warning: NEVER use `pickle` on untrusted input; use type-tagged JSON with strict schema validation instead.

#### 9. Related Concepts
- [oop.md](oop.md)

#### 10. References
- https://docs.python.org/3/library/pickle.html#object.__reduce__

</details>

---
