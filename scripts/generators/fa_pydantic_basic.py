"""
fa_pydantic_basic.py
====================
Basic FastAPI Pydantic & Validation Questions: FA-BAS-051 to FA-BAS-075 (25 questions)
"""

basic_data = [
    # FA-BAS-051
    (
        "FA-BAS-051",
        "Pydantic v2 Core Architecture and Role in FastAPI",
        "Pydantic is the data validation and settings management library powering FastAPI, rebuilt in version 2 around a compiled Rust validation engine (`pydantic-core`) for 5x to 50x performance gains.",
        "In modern web services, parsing, validating, and converting unstructured client input into strongly typed Python objects is fundamental. FastAPI utilizes Pydantic as its primary data layer. Rather than writing manual validation logic or regex checks, developers define declarative schemas inheriting from `BaseModel`. Pydantic handles type coercion, enforces constraints, generates JSON Schema definitions for OpenAPI documentation, and serializes Python data structures back to client responses.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\nclass UserProfile(BaseModel):\n    username: str\n    age: int\n    is_active: bool = True\n\napp = FastAPI()\n\n@app.post('/users')\ndef register_user(user: UserProfile):\n    # user is guaranteed to be a valid UserProfile instance\n    return {'message': f'User {user.username} registered with age {user.age}'}",
        "Defining a simple Pydantic model for automatic request body parsing and validation.",
        "When a request reaches FastAPI, raw JSON bytes are passed to Pydantic's Rust core (`pydantic-core`). The Rust engine parses the JSON string, validates types, performs automatic coercion, and instantiates the Python `UserProfile` object in compiled C/Rust speed.",
        "Ensuring data integrity at the API boundary across fintech transaction gateways, e-commerce checkouts, and microservice communication.",
        ["What is `pydantic-core` and what language is it written in?", "How does Pydantic v2 differ in speed from Pydantic v1?"],
        ["Thinking Pydantic is only used for JSON serialization (it handles deep validation, coercion, and schema generation).", "Assuming Pydantic requires custom validation code for basic types like dates, UUIDs, or integers."],
        "Emphasize the dual benefit: Pydantic guarantees runtime type safety for your application while automatically producing standards-compliant OpenAPI JSON schemas.",
        ["[Pydantic BaseModel](pydantic-and-validation.md)", "[Pydantic v2 Core](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/"]
    ),

    # FA-BAS-052
    (
        "FA-BAS-052",
        "BaseModel Fundamentals and Field Declarations",
        "`BaseModel` is the foundational base class in Pydantic; attributes declared with Python type hints on a `BaseModel` subclass become validated model fields.",
        "To define a schema in Pydantic, you subclass `BaseModel` and declare class attributes with standard Python type annotations. Fields without default values are required by default. Fields with default values (e.g. `is_active: bool = True`) are optional in client requests. When instantiated, `BaseModel` verifies all inputs, casting types where safe (e.g. `'42'` to `42`), and raises a `ValidationError` containing structured error details if data violates the schema.",
        "from pydantic import BaseModel, ValidationError\n\nclass Product(BaseModel):\n    id: int\n    name: str\n    price: float\n    in_stock: bool = True\n\n# Valid data with type coercion\nprod = Product(id='101', name='Mechanical Keyboard', price='89.99')\nassert prod.id == 101 and prod.price == 89.99\n\n# Invalid data triggers ValidationError\ntry:\n    Product(id='abc', name='Mouse', price=19.99)\nexcept ValidationError as exc:\n    print(f'Validation failed cleanly: {len(exc.errors())} error(s)')",
        "Declaring a BaseModel subclass and verifying successful type coercion and error handling.",
        "`BaseModel` uses a custom metaclass `ModelMetaclass` that inspects `__annotations__` at class definition time, constructing field descriptors and linking them to Rust validation schemas.",
        "Modeling domain transfer objects (DTOs), API contracts, and configuration settings across backend systems.",
        ["What happens if an undeclared attribute is passed to a `BaseModel`?", "Can `BaseModel` instances be compared for equality (`==`)?"],
        ["Using standard `__init__` methods inside `BaseModel` subclasses (breaks Pydantic's internal initialization).", "Assigning mutable default values directly like `tags: list = []` instead of using `Field(default_factory=list)`."],
        "Highlight that `BaseModel` provides out-of-the-box immutability options, equality checking (`__eq__`), and clean string representations (`__repr__`).",
        ["[Field Parameters](pydantic-and-validation.md)", "[Request Body Parsing](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/"]
    ),

    # FA-BAS-053
    (
        "FA-BAS-053",
        "Request Body Parsing with Pydantic Models",
        "Declaring a parameter with a `BaseModel` type annotation instructs FastAPI to read, parse, and validate the incoming JSON request body against that schema.",
        "In REST APIs, POST, PUT, and PATCH methods commonly carry JSON data in the HTTP request body. In FastAPI, you declare the request body by simply annotating a function parameter with your Pydantic `BaseModel` class. FastAPI reads the raw request bytes, decodes the JSON, validates it against the schema, and passes the validated model instance into the route handler. If the request body is missing or malformed, FastAPI returns a 422 Unprocessable Entity error immediately.",
        "from fastapi import FastAPI, status\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass OrderCreate(BaseModel):\n    product_id: int\n    quantity: int\n    shipping_address: str\n\n@app.post('/orders', status_code=status.HTTP_201_CREATED)\ndef create_order(order: OrderCreate):\n    # order is validated OrderCreate instance\n    return {'order_id': 991, 'total_items': order.quantity}",
        "Accepting and validating a structured JSON request body using a Pydantic model.",
        "FastAPI detects that `OrderCreate` is a `BaseModel` subclass. It generates an OpenAPI `requestBody` schema and configures Starlette to stream the request body, passing parsed JSON into the model's validator.",
        "Creating new records in database tables, submitting forms, and ingesting API webhook payloads.",
        ["What happens if the client sends extra fields not defined on `OrderCreate`?", "How can a route accept an optional request body?"],
        ["Attempting to read `await request.json()` manually inside the route instead of declaring the Pydantic model.", "Forgetting the `Content-Type: application/json` header in client requests, leading to 422 errors."],
        "Emphasize simplicity: No manual JSON decoding or parameter checking—FastAPI and Pydantic handle the entire pipeline declaratively.",
        ["[Pydantic BaseModel](pydantic-and-validation.md)", "[Nested Models](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body/"]
    ),

    # FA-BAS-054
    (
        "FA-BAS-054",
        "Field() Parameters and Constraints (gt, lt, description, title)",
        "`Field()` attaches validation constraints (like numeric ranges, string lengths, and regex patterns) and documentation metadata directly to model attributes.",
        "While basic type hints define what type of data is accepted, business rules require fine-grained constraints. Pydantic's `Field()` function allows specifying: 1) Numeric bounds: `gt` (greater than), `ge` (greater than or equal to), `lt`, `le`. 2) String bounds: `min_length`, `max_length`, `pattern`. 3) Metadata: `title`, `description`, `examples`, `deprecated`. In FastAPI, these constraints are enforced at runtime and documented automatically in the OpenAPI schema.",
        "from pydantic import BaseModel, Field\n\nclass Employee(BaseModel):\n    name: str = Field(min_length=2, max_length=50, description='Full legal name')\n    salary: float = Field(gt=0, description='Annual salary must be positive')\n    department: str = Field(default='Engineering', title='Department Name')\n    age: int = Field(ge=18, le=70, description='Legal working age')",
        "Enforcing numeric ranges, string length constraints, and documentation metadata with Field().",
        "`Field()` constructs a `FieldInfo` object. During model compilation, Pydantic's Rust core configures validators directly matching these constraints for single-pass evaluation.",
        "Preventing business logic corruption, such as negative product quantities, zero pricing bugs, or buffer overflows in downstream databases.",
        ["What is the difference between `Field(default=...)` and `Field(default_factory=...)`?", "How does `Field()` in Pydantic compare to `Query()` and `Path()` in FastAPI?"],
        ["Using `Field(default=[])` with mutable objects instead of `Field(default_factory=list)`.", "Confusing `gt` (strictly greater than) with `ge` (greater than or equal to)."],
        "Tip: Use `Field()` to document your API models thoroughly—descriptions and examples render directly in Swagger UI for your API consumers.",
        ["[Pydantic BaseModel](pydantic-and-validation.md)", "[Query Validation](routing-and-dependencies.md)"],
        ["https://docs.pydantic.dev/latest/concepts/fields/"]
    ),

    # FA-BAS-055
    (
        "FA-BAS-055",
        "response_model vs Function Return Type Annotations",
        "`response_model` defines the output serialization schema, data filtering, and OpenAPI documentation contract independently of internal Python function return types.",
        "FastAPI provides two ways to declare response models: 1) The decorator parameter `@app.get('/items', response_model=ItemOut)`: Specifically defines the public schema, filters out private fields (like hashed passwords), and formats OpenAPI responses. 2) Python return type hint `def get_items() -> ItemOut`: In modern FastAPI, return type hints automatically populate `response_model`. However, using `response_model` explicitly remains standard when the route returns a database ORM instance or internal model that must be serialized into a different public DTO.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n# Internal database representation (contains private password)\nclass UserDB(BaseModel):\n    id: int\n    username: str\n    hashed_password: str\n\n# Public API response schema (excludes private password)\nclass UserOut(BaseModel):\n    id: int\n    username: str\n\n@app.get('/users/{user_id}', response_model=UserOut)\ndef get_user(user_id: int):\n    # Returning UserDB object; FastAPI automatically filters it down to UserOut\n    return UserDB(id=user_id, username='alice', hashed_password='argon2_secret_hash')",
        "Filtering sensitive fields using response_model to prevent password leakage.",
        "FastAPI passes the returned object to the `response_model`'s serializer (`TypeAdapter.dump_python()`). Only fields declared on `response_model` are included in the emitted JSON response.",
        "Preventing accidental leakage of internal fields (e.g. password hashes, internal IDs, billing secrets) to API clients.",
        ["What is the security risk of omitting `response_model` when returning ORM models directly?", "How does `response_model` interact with status code 204 No Content?"],
        ["Assuming Python return type hints always filter fields (in older FastAPI versions, return type hints did not filter data without `response_model`).", "Returning data that does not match the `response_model` schema, resulting in 500 Internal Server Errors."],
        "Security golden rule: Always use `response_model` or strict return type annotations to prevent leaking sensitive internal fields.",
        ["[Response Filtering](routing-and-dependencies.md)", "[Pydantic BaseModel](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/response-model/"]
    ),

    # FA-BAS-056
    (
        "FA-BAS-056",
        "Optional Fields and Nullability (str | None = None vs Optional[str])",
        "Declaring fields as `str | None = None` makes them optional in client payloads and allows explicit `null` values in JSON.",
        "In Python 3.10+, `str | None = None` is the modern, idiomatic syntax for optional fields, replacing `Optional[str] = None` from `typing`. It communicates two things: 1) Type Hint: The field can hold a `str` or `None`. 2) Default Value: If the client omits the key from the JSON payload, it defaults to `None`. If a field is typed as `str | None` WITHOUT a default value (`= None`), the client MUST send the key, but its value may be `null`.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass ItemUpdate(BaseModel):\n    name: str | None = None          # Optional key; defaults to None if omitted\n    description: str | None = None   # Can be null or string\n    price: float                     # Required key; cannot be omitted or null\n\n@app.patch('/items/{item_id}')\ndef update_item(item_id: int, item: ItemUpdate):\n    return {'item_id': item_id, 'updated': item.model_dump(exclude_unset=True)}",
        "Defining optional and nullable fields using modern union syntax str | None = None.",
        "Pydantic parses the union schema. If the incoming value is JSON `null` or omitted, it assigns `None`. If a string is provided, it validates the string normally.",
        "Implementing PATCH endpoints where clients only supply fields they wish to modify, omitting untouched fields.",
        ["What is the difference between `str | None = None` and `str | None` without `= None`?", "How does `exclude_unset=True` distinguish omitted fields from fields explicitly sent as `null`?"],
        ["Writing `Optional[str]` without assigning `= None`, mistakenly thinking `Optional` makes the default value `None`.", "Using `null` in Python code instead of `None`."],
        "Syntax tip: In Python 3.10+, always use `T | None = None` instead of `Optional[T] = None` for cleaner, modern code.",
        ["[BaseModel](pydantic-and-validation.md)", "[PATCH Updates](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body/#optional-fields"]
    ),

    # FA-BAS-057
    (
        "FA-BAS-057",
        "Nested Pydantic Models for Complex JSON Hierarchies",
        "Pydantic models can be embedded as field types inside other Pydantic models, enabling deep validation of nested JSON objects and lists.",
        "Real-world data payloads are rarely flat; orders contain items, customers have billing addresses, and invoices contain line-item arrays. Pydantic handles arbitrary nesting seamlessly. You declare a field whose type annotation is another `BaseModel` subclass (or a `list[ChildModel]`). Pydantic validates the entire hierarchy recursively, producing clear error paths (e.g. `body.address.zip_code`) if nested validation fails.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\nclass Address(BaseModel):\n    street: str\n    city: str\n    zip_code: str\n\nclass Customer(BaseModel):\n    name: str\n    email: str\n    billing_address: Address\n    shipping_addresses: list[Address] = []\n\napp = FastAPI()\n\n@app.post('/customers')\ndef create_customer(customer: Customer):\n    return {'status': 'created', 'customer_city': customer.billing_address.city}",
        "Defining and validating nested Pydantic models for hierarchical customer data.",
        "Pydantic compiles a tree of validators. During deserialization, it invokes the child model's validator for the corresponding sub-dictionary, ensuring recursive type safety.",
        "Managing complex domain entities in e-commerce, banking transactions, and cloud infrastructure resource definitions.",
        ["What happens if a single nested field inside a deeply nested model fails validation?", "Can nested models reference circular relationships?"],
        ["Using plain `dict` annotations instead of nested `BaseModel` classes, losing schema validation for nested fields.", "Deeply nesting models beyond 6-7 levels without considering JSON parsing performance."],
        "Highlight that nested models provide full dot-notation access (`customer.billing_address.city`) and generate structured Swagger UI schemas.",
        ["[BaseModel](pydantic-and-validation.md)", "[List Fields](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body-nested-models/"]
    ),

    # FA-BAS-058
    (
        "FA-BAS-058",
        "List and Set Fields in Pydantic Models",
        "Typing fields as `list[T]` or `set[T]` validates sequences of items, with `set[T]` automatically deduplicating repeated items.",
        "APIs frequently accept collections of items, such as arrays of tags, image URLs, or product IDs. Annotating a field as `list[str]` ensures the incoming JSON array contains only strings (or coercible types). Annotating as `set[int]` not only validates that all elements are integers but also automatically eliminates duplicate values, converting the JSON array into a Python `set`.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel, Field\n\nclass Article(BaseModel):\n    title: str\n    tags: set[str] = Field(default_factory=set, description='Unique tags')\n    view_counts: list[int] = []\n\napp = FastAPI()\n\n@app.post('/articles')\ndef publish_article(article: Article):\n    # article.tags is a set: duplicates in incoming JSON are automatically removed\n    return {'title': article.title, 'unique_tag_count': len(article.tags)}",
        "Using list and set fields to validate collections with automatic deduplication.",
        "Pydantic iterates over the JSON array in Rust, validating each item against type `T`. For sets, it inserts items into a hash table, guaranteeing uniqueness.",
        "Accepting unique tags for blog posts, validating batch IDs, and processing multi-select form submissions.",
        ["What happens if a non-integer is passed inside a `list[int]`?", "How does OpenAPI render `set[str]` in Swagger documentation?"],
        ["Typing as `tags: list` without element type annotations (`list[str]`), losing element-level validation.", "Using mutable default arguments like `tags: list = []` instead of `Field(default_factory=list)`."],
        "Best practice: Use `set[T]` whenever incoming data must be unique—Pydantic deduplicates elements automatically.",
        ["[Nested Models](pydantic-and-validation.md)", "[Field Parameters](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body-nested-models/#list-fields"]
    ),

    # FA-BAS-059
    (
        "FA-BAS-059",
        "model_dump() vs model_dump_json() in Pydantic v2",
        "`model_dump()` serializes a Pydantic model into a Python dictionary, whereas `model_dump_json()` serializes it directly into a JSON-formatted string in compiled Rust.",
        "In Pydantic v1, models used `.dict()` and `.json()`. Pydantic v2 replaced them with `.model_dump()` and `.model_dump_json()`. The difference is crucial for performance: 1) `model_dump()`: Allocates intermediate Python dictionaries, lists, and scalar objects in Python memory. 2) `model_dump_json()`: Serializes model fields directly into a UTF-8 JSON string inside Rust (`pydantic-core`), bypassing intermediate Python dictionary allocation entirely and running 5x to 10x faster.",
        "from pydantic import BaseModel\n\nclass Event(BaseModel):\n    name: str\n    attendees: int\n\nevent = Event(name='PyCon', attendees=2500)\n\n# 1. Python dictionary representation\ndict_data = event.model_dump()\nassert isinstance(dict_data, dict)\n\n# 2. JSON string representation (serialized in compiled Rust)\njson_str = event.model_dump_json(indent=2)\nassert isinstance(json_str, str)",
        "Comparing dictionary serialization via model_dump() with direct Rust JSON serialization via model_dump_json().",
        "`model_dump()` converts Rust structs to `PyDict` objects. `model_dump_json()` uses `serde_json` in Rust to emit string bytes directly, avoiding Python memory allocator overhead.",
        "Serializing database records for caching in Redis (`model_dump_json()`) vs feeding data into ORM models (`model_dump()`).",
        ["What are the arguments supported by `model_dump()` (e.g. `exclude_unset`, `include`, `mode`)?", "Why is `model.dict()` deprecated in modern Pydantic v2 codebases?"],
        ["Using `.dict()` or `.json()` in new Pydantic v2 projects (deprecated in favor of `model_dump()` and `model_dump_json()`).", "Calling `json.dumps(model.model_dump())` instead of using `model.model_dump_json()` directly."],
        "Performance rule: If you need a JSON string (e.g. for caching or network responses), always call `model_dump_json()` directly.",
        ["[Pydantic v2 Core](pydantic-and-validation.md)", "[Production & Performance](production-and-performance.md)"],
        ["https://docs.pydantic.dev/latest/concepts/serialization/"]
    ),

    # FA-BAS-060
    (
        "FA-BAS-060",
        "Automatic Type Coercion in Pydantic",
        "Pydantic performs safe, bidirectional type coercion by default, converting compatible inputs (like numeric strings to integers) into target annotated types.",
        "In HTTP APIs, incoming data often arrives as strings (from query parameters, headers, or form data). Rather than requiring strict type purity from clients, Pydantic automatically coerces compatible types: `'123'` becomes `123` for `int`, `'true'` or `'1'` becomes `True` for `bool`, and ISO date strings become `datetime` objects. If conversion would cause data loss or ambiguity, Pydantic rejects the value with a `ValidationError`.",
        "from pydantic import BaseModel\n\nclass Config(BaseModel):\n    port: int\n    debug: bool\n    rate: float\n\n# Strings and ints are coerced safely\ncfg = Config(port='8080', debug='yes', rate=42)\nassert cfg.port == 8080\nassert cfg.debug is True\nassert cfg.rate == 42.0",
        "Demonstrating Pydantic's automatic type coercion across integers, booleans, and floats.",
        "In lax mode (default), Pydantic's Rust core attempts well-defined type conversions before raising errors. In strict mode (`strict=True`), type coercion is disabled and exact types are enforced.",
        "Parsing web form submissions and URL query strings where all client input arrives over the wire as strings.",
        ["How do you disable type coercion if your API requires strict types?", "What boolean representations does Pydantic recognize as `True` and `False`?"],
        ["Assuming Pydantic performs JavaScript-style loose type coercion (e.g. `[]` does NOT coerce to `False` or `0`).", "Relying on type coercion when strict types are required by financial specifications."],
        "Mention that Pydantic supports strict mode per model (`model_config = ConfigDict(strict=True)`) or per field if coercion is undesirable.",
        ["[BaseModel](pydantic-and-validation.md)", "[Strict Mode](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/strict_mode/"]
    ),

    # FA-BAS-061
    (
        "FA-BAS-061",
        "Handling Date and Datetime Validation (datetime.date vs datetime.datetime)",
        "Annotating fields with standard `datetime.date` or `datetime.datetime` types automatically parses ISO 8601 strings and Unix epoch timestamps into Python datetime objects.",
        "Handling date and time formats across distributed systems is notoriously error-prone. Pydantic natively parses ISO 8601 strings (e.g. `'2026-11-21T03:30:00Z'`), RFC 2822 dates, and integer/float Unix timestamps into standard library `datetime.date` or `datetime.datetime` objects. It also validates calendar validity (rejecting invalid dates like February 30th) and normalizes time zones.",
        "from datetime import datetime, date\nfrom pydantic import BaseModel\n\nclass FlightBooking(BaseModel):\n    flight_number: str\n    departure_date: date\n    booked_at: datetime\n\n# Parses ISO 8601 string dates automatically\nbooking = FlightBooking(\n    flight_number='AA-104',\n    departure_date='2026-12-25',\n    booked_at='2026-11-21T08:30:00Z'\n)\nassert booking.departure_date.year == 2026\nassert booking.booked_at.hour == 8",
        "Parsing ISO 8601 date and datetime strings into Python datetime objects.",
        "Pydantic uses Rust's `speedate` library within `pydantic-core`, which parses date and time strings in nanoseconds without Python regular expression overhead.",
        "Scheduling calendar appointments, recording database audit timestamps, and validating flight reservations.",
        ["How does Pydantic handle timezone-naive vs timezone-aware datetime objects?", "What happens if a Unix timestamp integer is passed to a `datetime` field?"],
        ["Writing custom regex string validators to parse dates instead of using standard `datetime` annotations.", "Comparing timezone-naive datetimes with timezone-aware datetimes in downstream logic."],
        "Always use standard `datetime.date` and `datetime.datetime` type hints; Pydantic parses ISO strings and generates RFC-compliant OpenAPI formats.",
        ["[BaseModel](pydantic-and-validation.md)", "[Field Validation](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#dates-and-times"]
    ),

    # FA-BAS-062
    (
        "FA-BAS-062",
        "Email Validation using EmailStr and pydantic[email]",
        "`EmailStr` validates email addresses against RFC 5322 specifications, verifying username structure, '@' symbols, and domain validity.",
        "Validating email addresses with simplistic regular expressions is a classic software engineering mistake that either rejects valid emails or accepts malformed inputs. Pydantic provides the `EmailStr` type (powered by `email-validator`). It verifies syntax, checks for valid top-level domains, strips trailing whitespace, and normalizes internationalized domain names (IDN) into ASCII punycode.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel, EmailStr\n\napp = FastAPI()\n\nclass UserRegistration(BaseModel):\n    username: str\n    email: EmailStr\n\n@app.post('/register')\ndef register(user: UserRegistration):\n    # user.email is guaranteed to be a valid, normalized RFC 5322 email string\n    return {'status': 'success', 'email': user.email}",
        "Validating email addresses using Pydantic's EmailStr type annotation.",
        "When `EmailStr` is validated, Pydantic invokes `email-validator` to parse the address, checking local-part syntax, domain labels, and length limits (max 254 characters).",
        "User registration flows, email notification systems, and authentication gateways.",
        ["What library must be installed to support `EmailStr` (`pip install \"pydantic[email]\"`)?", "Does `EmailStr` check if the email's MX record actually exists on DNS servers?"],
        ["Writing brittle custom regex patterns for email validation instead of using `EmailStr`.", "Forgetting that `EmailStr` requires installing `email-validator` in the environment."],
        "Emphasize: Use `EmailStr` for production reliability; never write hand-crafted regex for email verification.",
        ["[BaseModel](pydantic-and-validation.md)", "[URL Validation](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#emails"]
    ),

    # FA-BAS-063
    (
        "FA-BAS-063",
        "URL and HttpUrl Validation with Pydantic Networks",
        "`HttpUrl` validates web URLs, enforcing valid URL schemes (`http` or `https`), hostnames, and maximum length limits.",
        "APIs that accept webhook targets, avatar image URLs, or OAuth redirect URIs must validate that client inputs are legitimate HTTP/HTTPS URLs. Pydantic provides `HttpUrl` (as well as `AnyUrl` and `FileUrl`). It validates that the string contains a valid scheme, host, and optional port/path, parsing it into a structured URL object that exposes `.host`, `.scheme`, `.port`, and `.path` properties.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel, HttpUrl\n\napp = FastAPI()\n\nclass WebhookConfig(BaseModel):\n    event_name: str\n    target_url: HttpUrl\n\n@app.post('/webhooks')\ndef register_webhook(config: WebhookConfig):\n    # config.target_url is a validated HttpUrl instance\n    return {\n        'event': config.event_name,\n        'host': config.target_url.host,\n        'url': str(config.target_url)\n    }",
        "Validating target webhook URLs using Pydantic HttpUrl.",
        "Pydantic parses the URL using Rust-based URL parsing utilities, verifying RFC 3986 compliance and ensuring scheme is strictly `http` or `https`.",
        "Webhook registration systems, third-party callback URLs, and image hosting services.",
        ["What is the difference between `HttpUrl` and `AnyUrl`?", "Why does `HttpUrl` require converting to `str()` when saving to database text columns?"],
        ["Accepting unvalidated strings for webhook URLs, exposing internal endpoints to SSRF (Server-Side Request Forgery).", "Passing a relative path like `/callback` to `HttpUrl` (raises validation error; URLs must be absolute)."],
        "Security reminder: Pair `HttpUrl` validation with internal IP blocklists to prevent SSRF vulnerabilities.",
        ["[Email Validation](pydantic-and-validation.md)", "[API Security](authentication-and-security.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#urls"]
    ),

    # FA-BAS-064
    (
        "FA-BAS-064",
        "Multiple Request Body Parameters in a Single Route",
        "Declaring multiple `BaseModel` parameters in a route handler instructs FastAPI to expect a combined JSON body where each model is keyed by its parameter name.",
        "In many API designs, an endpoint must receive multiple distinct domain objects in a single request (e.g. an `item` and a `user`). In FastAPI, if you declare multiple Pydantic model parameters in a route function signature, FastAPI expects a single top-level JSON request body with keys matching the parameter names: `{\"item\": {...}, \"user\": {...}}`.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Item(BaseModel):\n    name: str\n    price: float\n\nclass User(BaseModel):\n    username: str\n    email: str\n\n# Client sends: {\"item\": {\"name\": \"Pen\", \"price\": 1.5}, \"user\": {\"username\": \"bob\", \"email\": \"b@x.com\"}}\n@app.post('/purchase')\ndef purchase(item: Item, user: User, priority: int = 1):\n    return {'buyer': user.username, 'item_name': item.name, 'priority': priority}",
        "Accepting multiple Pydantic models in a single combined JSON request body.",
        "FastAPI detects multiple body parameters and automatically wraps them in a synthesized composite Pydantic schema, generating an OpenAPI payload schema containing `item`, `user`, and `priority` fields.",
        "Multi-entity transactions, such as checkout operations receiving payment info and cart items simultaneously.",
        ["How does the required JSON structure change when a route transitions from one body model to two?", "Can a scalar value like `priority: int` be included in the body alongside models?"],
        ["Sending flat JSON when multiple body models are declared (causes 422 error because top-level keys are expected).", "Forgetting that scalar parameters default to query params unless wrapped in `Body()`."],
        "Notice the structural shift: A single model expects a flat JSON body; multiple models expect a keyed dictionary matching parameter names.",
        ["[Request Body Parsing](pydantic-and-validation.md)", "[Embedded Body Parameters](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body-multiple-params/"]
    ),

    # FA-BAS-065
    (
        "FA-BAS-065",
        "Embedding Single Request Body Parameters with Body(embed=True)",
        "`Body(embed=True)` forces a single Pydantic request model to be wrapped inside a top-level JSON key matching the parameter name.",
        "By default, when an endpoint has only one Pydantic model parameter (e.g. `item: Item`), FastAPI expects a flat JSON body: `{\"name\": \"Widget\", \"price\": 10.0}`. However, certain API style guidelines or existing frontend clients structure payloads under a root key: `{\"item\": {\"name\": \"Widget\", \"price\": 10.0}}`. Passing `item: Item = Body(embed=True)` instructs FastAPI to expect the payload wrapped in the parameter key.",
        "from fastapi import FastAPI, Body\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Item(BaseModel):\n    name: str\n    price: float\n\n# Client MUST send: {\"item\": {\"name\": \"Hammer\", \"price\": 19.99}}\n@app.post('/items')\ndef create_item(item: Item = Body(embed=True)):\n    return {'item': item.model_dump()}",
        "Requiring a top-level key wrapper using Body(embed=True).",
        "FastAPI creates an internal composite wrapper model where the single field `item` is expected at the root of the JSON body.",
        "Matching legacy frontend client JSON contracts or adhering to JSON:API specifications requiring root entity keys.",
        ["What error is returned if a client sends a flat JSON object to an endpoint configured with `embed=True`?", "Can `embed=True` be used with primitive scalar parameters like `token: str = Body(embed=True)`?"],
        ["Sending flat JSON to an `embed=True` endpoint, resulting in a 422 'Field required' error.", "Using `embed=True` inconsistently across CRUD endpoints in the same API."],
        "Design tip: Use `Body(embed=True)` when maintaining consistency with endpoints that accept multiple body parameters.",
        ["[Multiple Body Parameters](pydantic-and-validation.md)", "[Request Body Parsing](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body-multiple-params/#embed-a-single-body-parameter"]
    ),

    # FA-BAS-066
    (
        "FA-BAS-066",
        "Field Examples and OpenAPI Schema Documentation",
        "`examples` on `Field()` or model `json_schema_extra` populates interactive sample payloads in Swagger UI documentation.",
        "Well-documented APIs accelerate developer integration by providing concrete sample payloads in interactive documentation. In Pydantic v2 and modern FastAPI, you provide examples using the `examples` argument on `Field(examples=[...])` or by defining `json_schema_extra` in the model's `model_config`. Swagger UI automatically pre-populates these examples in the interactive 'Try it out' console.",
        "from pydantic import BaseModel, Field, ConfigDict\n\nclass Device(BaseModel):\n    serial_number: str = Field(\n        description='Unique factory serial number',\n        examples=['SN-9982-A']\n    )\n    firmware_version: str = Field(examples=['v2.4.1'])\n\n    # Model-level example payload for Swagger UI\n    model_config = ConfigDict(\n        json_schema_extra={\n            'examples': [\n                {'serial_number': 'SN-0012-X', 'firmware_version': 'v3.0.0'}\n            ]\n        }\n    )",
        "Documenting field-level and model-level examples for OpenAPI Swagger UI.",
        "FastAPI extracts `examples` and injects them into the generated OpenAPI 3.1 schema under the `examples` array of the schema object.",
        "Building developer-facing public APIs where interactive documentation serves as primary developer onboarding.",
        ["Why was `example` (singular) replaced with `examples` (plural list) in OpenAPI 3.1 and Pydantic v2?", "How do examples affect runtime data validation?"],
        ["Assuming examples are validated at runtime (examples are purely documentation metadata; Pydantic does not validate examples during execution).", "Using Pydantic v1 `schema_extra` inside class `Config` instead of modern `model_config = ConfigDict(json_schema_extra=...)`."],
        "Documentation tip: Always provide realistic model-level examples so frontend engineers can test APIs in Swagger UI with one click.",
        ["[Field Parameters](pydantic-and-validation.md)", "[Pydantic ConfigDict](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/schema-extra-example/"]
    ),

    # FA-BAS-067
    (
        "FA-BAS-067",
        "Secret Types (SecretStr and SecretBytes) for Sensitive Credentials",
        "`SecretStr` and `SecretBytes` wrap sensitive strings, masking values in `str()`, `repr()`, and logs to prevent accidental credential leakage.",
        "Logging or printing passwords, API keys, or database secrets is a major security vulnerability. Pydantic provides `SecretStr` and `SecretBytes`. When printed, logged, or serialized, a `SecretStr` displays as `'**********'`. To retrieve the raw secret value in code, you must explicitly call `secret.get_secret_value()`, ensuring credentials are only exposed when deliberately requested.",
        "from pydantic import BaseModel, SecretStr\n\nclass DatabaseCredentials(BaseModel):\n    username: str\n    password: SecretStr\n\ncreds = DatabaseCredentials(username='admin', password='super_secret_password_123')\n\n# Safe: repr and str mask the secret\nprint(f'Credentials object: {creds}')  # Output: password=SecretStr('**********')\n\n# Explicit access when connecting to database\nraw_password = creds.password.get_secret_value()\nassert raw_password == 'super_secret_password_123'",
        "Masking sensitive passwords using SecretStr and retrieving via get_secret_value().",
        "`SecretStr` overrides `__str__` and `__repr__` to return masked asterisks. In JSON serialization (`model_dump()`), it also returns the masked representation unless explicit serialization mode is configured.",
        "Storing API tokens, OAuth client secrets, private encryption keys, and database passwords in settings models.",
        ["What does `creds.model_dump()` output for a `SecretStr` field?", "How does `SecretBytes` differ from `SecretStr`?"],
        ["Attempting to use `creds.password` directly in database connection strings without calling `.get_secret_value()`.", "Using plain `str` for passwords in configuration models, leading to plain-text leakage in log aggregators."],
        "Security mandate: Always wrap API keys and passwords in `SecretStr` to eliminate plain-text credential leaks in logs.",
        ["[BaseModel](pydantic-and-validation.md)", "[API Security](authentication-and-security.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#secret-types"]
    ),

    # FA-BAS-068
    (
        "FA-BAS-068",
        "Constrained Types vs Annotated[T, Field(...)]",
        "In modern Pydantic v2, `Annotated[T, Field(...)]` is the recommended standard replacing legacy constrained types like `conint` and `constr`.",
        "In Pydantic v1, constrained types like `conint(gt=0, le=100)` and `constr(min_length=3)` were common. In Pydantic v2 and modern Python 3.9+, standard `typing.Annotated` paired with `Field()` is the preferred, idiomatic syntax. It provides superior static type analysis, better IDE autocompletion, and full compatibility with standard Python linters like Mypy and Ruff.",
        "from typing import Annotated\nfrom pydantic import BaseModel, Field\n\n# Modern, idiomatic constrained types using Annotated\nPositiveInt = Annotated[int, Field(gt=0, description='Must be strictly positive')]\nUsername = Annotated[str, Field(min_length=3, max_length=20, pattern='^[a-z0-9_]+$')]\n\nclass Account(BaseModel):\n    user_id: PositiveInt\n    username: Username\n    balance: Annotated[float, Field(ge=0.0)] = 0.0",
        "Defining reusable, validated type aliases with typing.Annotated and Field().",
        "Pydantic parses `Annotated` metadata at model compilation time, extracting `FieldInfo` constraints and compiling them into Rust validation hooks without creating bespoke wrapper classes.",
        "Building reusable domain types (e.g. `UserId`, `PostalCode`, `Percentage`) shared across multiple microservice models.",
        ["Why does `Annotated` work better with static type checkers than `conint`?", "Can you attach multiple metadata objects inside a single `Annotated` definition?"],
        ["Using deprecated `conint` and `constr` in greenfield Pydantic v2 applications.", "Forgetting that `Annotated` type aliases can be imported and shared across multiple modules."],
        "Best practice: Always use `Annotated[T, Field(...)]` for constrained types in modern Python 3.10+ codebases.",
        ["[Field Parameters](pydantic-and-validation.md)", "[Reusable Parameter Annotations](routing-and-dependencies.md)"],
        ["https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints"]
    ),

    # FA-BAS-069
    (
        "FA-BAS-069",
        "UUID Field Validation with uuid.UUID",
        "Annotating fields with standard `uuid.UUID` validates 128-bit Universally Unique Identifiers in hex strings or URN formats, casting them into Python `UUID` objects.",
        "UUIDs are standard identifiers in distributed architectures because they can be generated independently without centralized database coordination. Pydantic natively supports `uuid.UUID`. Clients can submit UUIDs in standard 36-character hyphenated format, 32-character hex strings, or URN format (`urn:uuid:...`). Pydantic validates the format, verifies hex digits, and converts the input into a standard Python `uuid.UUID` instance.",
        "from uuid import UUID\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Transaction(BaseModel):\n    tx_id: UUID\n    amount: float\n\n@app.post('/transactions')\ndef record_tx(tx: Transaction):\n    # tx.tx_id is an instance of uuid.UUID\n    return {'uuid_version': tx.tx_id.version, 'tx_hex': tx.tx_id.hex}",
        "Validating UUID strings and accessing native UUID attributes.",
        "Pydantic checks string length and invokes Python's `uuid.UUID(value)` in Rust. If the format or hex characters are invalid, a `ValidationError` is raised.",
        "Validating distributed entity primary keys, idempotency keys, and payment gateway transaction references.",
        ["How does OpenAPI represent `uuid.UUID` fields in the generated JSON Schema (`format: uuid`)?", "What is the difference between UUIDv4 (random) and UUIDv7 (time-ordered) in database indexing?"],
        ["Typing UUID fields as plain `str`, allowing malformed identifiers to query database indexes.", "Calling `str(tx.tx_id)` repeatedly when the UUID object can be used directly in database drivers."],
        "Design tip: Use `UUID` annotations to ensure database primary keys are validated at the API boundary before reaching queries.",
        ["[BaseModel](pydantic-and-validation.md)", "[Path Parameters](routing-and-dependencies.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#standard-library-types"]
    ),

    # FA-BAS-070
    (
        "FA-BAS-070",
        "Literal Types for Strict Allowed Value Sets",
        "`typing.Literal` restricts a field's valid values to an exact set of predefined strings, numbers, or booleans, providing strict choice validation with zero enum overhead.",
        "When an API field only allows a few fixed values (e.g. `'credit_card' | 'paypal' | 'crypto'`), defining a full Python `Enum` class can sometimes be unnecessary boilerplate. Python's `typing.Literal` allows declaring allowed values directly in the type annotation. Pydantic validates that the incoming data matches one of the specified literal values exactly and documents it as an enum in OpenAPI schemas.",
        "from typing import Literal\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass PaymentRequest(BaseModel):\n    amount: float\n    payment_method: Literal['credit_card', 'paypal', 'apple_pay']\n    currency: Literal['USD', 'EUR', 'GBP'] = 'USD'\n\n@app.post('/checkout')\ndef checkout(req: PaymentRequest):\n    return {'status': 'processed', 'method': req.payment_method}",
        "Constraining fields to fixed choice sets using typing.Literal.",
        "Pydantic compiles `Literal` types into an exact value match lookup in Rust. If the input does not match any literal item, it returns an 'input should be one of...' error.",
        "Specifying order sorting directions (`Literal['asc', 'desc']`), payment methods, and API feature modes.",
        ["How does `Literal` differ from Python's standard `Enum` in OpenAPI schema generation?", "Can `Literal` combine multiple data types, like `Literal['auto', 0, 1]`?"],
        ["Using free-form `str` and validating choices manually with `if/else` inside route handlers.", "Forgetting that `Literal` values are case-sensitive by default."],
        "Clean code tip: Use `Literal` for simple fixed options; use `Enum` when options carry additional logic or member mappings.",
        ["[BaseModel](pydantic-and-validation.md)", "[Enum Parameters](routing-and-dependencies.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#literal-types"]
    ),

    # FA-BAS-071
    (
        "FA-BAS-071",
        "Dictionary Fields with Typed Keys and Values (dict[str, float])",
        "Annotating fields as `dict[KeyType, ValueType]` validates dynamic key-value mappings where property keys are unknown in advance.",
        "Not all JSON objects have fixed property names. For example, localization dictionaries (`{'en': 'Hello', 'fr': 'Bonjour'}`), product inventory counts (`{'sku_101': 50}`), or financial exchange rates (`{'EUR': 1.08}`) have dynamic keys. Pydantic supports `dict[KeyType, ValueType]`, validating that all keys match `KeyType` and all values conform to `ValueType`.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass ExchangeRates(BaseModel):\n    base_currency: str\n    rates: dict[str, float]  # Dynamic currency codes to numeric conversion rates\n\n@app.post('/rates')\ndef update_rates(rates_data: ExchangeRates):\n    usd_rate = rates_data.rates.get('USD', 1.0)\n    return {'total_currencies': len(rates_data.rates), 'usd': usd_rate}",
        "Validating dynamic JSON mappings using typed dictionaries dict[str, float].",
        "Pydantic iterates over incoming JSON key-value pairs in Rust, applying key validation and value validation independently before assembling the Python dictionary.",
        "Dynamic key-value metadata storage, multi-language localization mappings, and configuration dictionaries.",
        ["What happens if a non-float value is passed in the `rates` dictionary?", "How does OpenAPI document `dict[str, float]` in Swagger UI (`additionalProperties`)?"],
        ["Using untyped `dict` annotations, which allows arbitrary unvalidated nested objects to enter your application.", "Attempting to use non-string types for JSON object keys (JSON object keys are strictly strings under RFC 8259)."],
        "OpenAPI insight: Typed dictionaries generate `additionalProperties: { type: 'number' }` in OpenAPI JSON Schemas.",
        ["[BaseModel](pydantic-and-validation.md)", "[Nested Models](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#standard-library-types"]
    ),

    # FA-BAS-072
    (
        "FA-BAS-072",
        "Excluding Fields from Serialization with Field(exclude=True)",
        "`Field(exclude=True)` permanently excludes an attribute from `model_dump()`, `model_dump_json()`, and API response serialization.",
        "Certain model attributes are strictly for internal computation, temporary caching, or sensitive processing and must never be emitted in outgoing JSON responses or serialized payloads. Setting `Field(exclude=True)` instructs Pydantic to omit the field during all serialization passes, guaranteeing that internal state remains private.",
        "from pydantic import BaseModel, Field\n\nclass AccountLedger(BaseModel):\n    account_id: str\n    balance: float\n    internal_risk_score: float = Field(exclude=True)  # Never serialized\n\nledger = AccountLedger(account_id='AC-441', balance=1500.50, internal_risk_score=9.4)\n\n# internal_risk_score is excluded from model_dump and JSON output\nserialized = ledger.model_dump()\nassert 'internal_risk_score' not in serialized\nassert serialized == {'account_id': 'AC-441', 'balance': 1500.50}",
        "Permanently excluding internal risk score from serialization with Field(exclude=True).",
        "Pydantic's serialization compiler marks the field with an exclusion flag in the compiled Rust schema, bypassing the attribute during dictionary and JSON generation.",
        "Hiding internal calculation scores, temporary decryption keys, and backend audit flags from public API clients.",
        ["Can you temporarily include an excluded field during `model_dump(include={...})`?", "How does `Field(exclude=True)` compare to using `response_model`?"],
        ["Relying solely on `Field(exclude=True)` for password security without using `SecretStr` (plain strings can still be inspected via `__repr__`).", "Forgetting that `exclude=True` also excludes the field when serializing to database cache dictionaries."],
        "Defense-in-depth: Combine `SecretStr` and `Field(exclude=True)` for sensitive credentials to prevent leaks in both logging and serialization.",
        ["[Secret Types](pydantic-and-validation.md)", "[Response Model vs Return Type](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/fields/#field-exclusion"]
    ),

    # FA-BAS-073
    (
        "FA-BAS-073",
        "Custom Error Messages in Pydantic Field Validation",
        "Configuring `json_schema_extra` or using custom validators allows tailoring user-friendly error messages that replace generic Pydantic validation errors.",
        "By default, Pydantic produces precise but technical error messages (e.g. `'String should match pattern ^[A-Z]{3}$'`). For customer-facing APIs, you often need intuitive, localized, or business-specific messages (e.g. `'Airport code must consist of exactly 3 uppercase letters'`). In Pydantic v2, custom error messages can be supplied via custom validators or configured error mappings.",
        "from pydantic import BaseModel, Field, field_validator\n\nclass Flight(BaseModel):\n    airport_code: str = Field(min_length=3, max_length=3)\n\n    @field_validator('airport_code')\n    @classmethod\n    def validate_airport(cls, v: str) -> str:\n        if not v.isupper() or not v.isalpha():\n            raise ValueError('Airport code must consist of exactly 3 uppercase letters (e.g. JFK, LHR)')\n        return v",
        "Providing clear, domain-specific validation error messages using field_validator.",
        "When a validator raises `ValueError` or `AssertionError`, Pydantic intercepts the exception message and embeds it into the `msg` field of the structured validation error response.",
        "Delivering actionable error feedback on consumer checkout forms, credit card validation, and identity verification portals.",
        ["How does FastAPI format Pydantic validation errors in the final HTTP 422 JSON response?", "Can error messages be localized into different languages dynamically?"],
        ["Raising generic `Exception` instead of `ValueError` inside validators (may cause 500 errors instead of 422).", "Writing vague error messages like 'Invalid input' that fail to explain how the client can correct the request."],
        "Interview tip: Always raise `ValueError('Descriptive message')` inside Pydantic validators—FastAPI maps it cleanly to HTTP 422 with your exact message.",
        ["[Field Validation](pydantic-and-validation.md)", "[422 Error Structure](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/validators/"]
    ),

    # FA-BAS-074
    (
        "FA-BAS-074",
        "ConfigDict and Model Configuration in Pydantic v2",
        "`model_config = ConfigDict(...)` defines model-wide behavioral settings in Pydantic v2, replacing the legacy inner `class Config` from Pydantic v1.",
        "In Pydantic v1, model configuration was specified using an inner class: `class Config: ...`. Pydantic v2 modernized this by introducing `ConfigDict`, an explicit typed dictionary assigned to `model_config = ConfigDict(...)`. It configures global model behavior, including: `extra` ('ignore', 'allow', 'forbid'), `frozen` (immutability), `str_strip_whitespace`, `from_attributes` (ORM mode), and `populate_by_name`.",
        "from pydantic import BaseModel, ConfigDict\n\nclass ImmutableSettings(BaseModel):\n    # Model-wide configuration via ConfigDict\n    model_config = ConfigDict(\n        frozen=True,                # Model instances are immutable and hashable\n        str_strip_whitespace=True,  # Automatically strip leading/trailing whitespace\n        extra='forbid'              # Disallow extra fields not declared in schema\n    )\n    app_name: str\n    max_workers: int = 4\n\nsettings = ImmutableSettings(app_name='  InventoryApp  ')\n# Whitespace was stripped automatically\nassert settings.app_name == 'InventoryApp'",
        "Configuring model-wide immutability, whitespace stripping, and extra field rejection via ConfigDict.",
        "Pydantic compiles `model_config` settings directly into the model's Rust schema at class creation time, ensuring zero runtime lookup overhead.",
        "Enforcing strict security boundaries by forbidding unexpected extra fields, and ensuring thread-safe immutable configuration objects.",
        ["Why is `model_config = ConfigDict(...)` superior to the inner `class Config:`?", "What happens if a field is modified on a model with `frozen=True`?"],
        ["Using the deprecated Pydantic v1 `class Config:` in new Pydantic v2 applications.", "Setting `extra='allow'` unintentionally, allowing clients to inject unvalidated arbitrary data into models."],
        "Migration rule: Always use `model_config = ConfigDict(...)` in Pydantic v2; it provides full IDE type-checking and autocompletion for all configuration flags.",
        ["[Pydantic v2 Core](pydantic-and-validation.md)", "[Extra Attributes](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/config/"]
    ),

    # FA-BAS-075
    (
        "FA-BAS-075",
        "Common Pydantic Validation Errors and HTTP 422 Response Structure",
        "When incoming data violates Pydantic schemas, FastAPI catches the `RequestValidationError` and returns an HTTP 422 Unprocessable Entity response containing structured field error details.",
        "Unlike generic 400 Bad Request responses, FastAPI's HTTP 422 responses provide machine-readable error diagnostics. The response body is a JSON object with a `detail` array. Each item in `detail` contains: 1) `loc`: Tuple specifying the exact location of the error (e.g. `['body', 'user', 'email']`). 2) `msg`: Human-readable error description. 3) `type`: Machine-readable error identifier (e.g. `'value_error.missing'`, `'string_too_short'`). 4) `input`: The invalid value provided by the client.",
        "from fastapi import FastAPI\nfrom fastapi.testclient import TestClient\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\nclass Item(BaseModel):\n    name: str = Field(min_length=3)\n    price: float = Field(gt=0)\n\n@app.post('/items')\ndef create_item(item: Item):\n    return item\n\nclient = TestClient(app)\n# Send invalid payload: name too short, price negative\nresponse = client.post('/items', json={'name': 'a', 'price': -10.0})\nassert response.status_code == 422\nprint('HTTP 422 Error Details:', response.json())",
        "Demonstrating FastAPI's structured HTTP 422 Unprocessable Entity validation response.",
        "When Pydantic raises a `ValidationError`, FastAPI's exception handler intercepts it, wraps it in a `RequestValidationError`, and serializes the error list into Starlette's `JSONResponse` with status 422.",
        "Enabling modern frontend single-page apps (React, Vue) to map validation errors directly to specific form input fields highlighted in red.",
        ["How can you customize the default HTTP 422 error response structure across your entire API?", "What is the difference between HTTP 400 and HTTP 422 in REST standards?"],
        ["Catching `ValidationError` manually inside route handlers instead of letting FastAPI handle it automatically.", "Assuming 422 errors mean the server crashed (422 is a client error indicating invalid input payload)."],
        "REST standard insight: 400 indicates malformed HTTP syntax (e.g. invalid JSON bytes); 422 indicates syntactically valid JSON that violates domain semantic rules.",
        ["[BaseModel](pydantic-and-validation.md)", "[Exception Handling](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]
    ),
]
