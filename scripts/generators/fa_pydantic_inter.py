"""
fa_pydantic_inter.py
====================
Intermediate FastAPI Pydantic & Validation Questions: FA-INT-051 to FA-INT-075 (25 questions)
"""

inter_data = [
    # FA-INT-051
    (
        "FA-INT-051",
        "field_validator in Pydantic v2 (mode='before' vs mode='after')",
        "`@field_validator` validates and transforms individual model fields, executing either before Pydantic's internal type parsing (`mode='before'`) or after type coercion has succeeded (`mode='after'`).",
        "In Pydantic v2, `@field_validator` replaces the legacy `@validator` decorator. The execution phase is determined by the `mode` parameter: 1) `mode='after'` (default): Runs after Pydantic has coerced the raw input into the declared Python type. The validator receives the already-cast object (e.g. integer or datetime) and validates domain constraints. 2) `mode='before'`: Runs before Pydantic performs any type conversion. The validator receives raw client input (such as an unparsed string, comma-separated values, or raw dictionary) and can preprocess or sanitize it before type validation runs.",
        "from pydantic import BaseModel, field_validator\n\nclass UserRegistration(BaseModel):\n    username: str\n    phone_number: str\n\n    # mode='before': Preprocesses raw unformatted phone strings\n    @field_validator('phone_number', mode='before')\n    @classmethod\n    def clean_phone(cls, v: str) -> str:\n        # Strip spaces, hyphens, and parentheses\n        return ''.join(c for c in str(v) if c.isdigit())\n\n    # mode='after': Validates username after string conversion\n    @field_validator('username', mode='after')\n    @classmethod\n    def validate_username(cls, v: str) -> str:\n        if 'admin' in v.lower():\n            raise ValueError('Username cannot contain \"admin\"')\n        return v",
        "Demonstrating mode='before' for string sanitization and mode='after' for business logic validation.",
        "Validators are compiled into the model's Rust schema pipeline. In `mode='before'`, the validator is placed at the front of the Rust validation pipeline; in `mode='after'`, it executes immediately after Rust type conversion succeeds.",
        "Sanitizing raw user phone numbers, normalizing uppercase country codes, and enforcing domain constraints on usernames.",
        ["Why must `@field_validator` methods be decorated with `@classmethod` in Pydantic v2?", "What happens if a `mode='before'` validator returns a type incompatible with the field's annotation?"],
        ["Forgetting `@classmethod` on `@field_validator` methods (causes runtime errors in Pydantic v2).", "Performing heavy string preprocessing in `mode='after'` when the raw input was already rejected by type validation."],
        "Key distinction: Use `mode='before'` to massage raw untyped client data; use `mode='after'` (default) to validate strongly-typed Python values.",
        ["[BaseModel](pydantic-and-validation.md)", "[Model Validator](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/validators/#field-validators"]
    ),

    # FA-INT-052
    (
        "FA-INT-052",
        "model_validator for Multi-Field Cross-Validation (mode='after')",
        "`@model_validator(mode='after')` executes cross-field validation after all individual fields have been validated and coerced, operating directly on `self`.",
        "Many business validation rules depend on interactions between multiple fields (e.g. `end_date` must be after `start_date`, or `confirm_password` must match `password`). Individual field validators cannot reliably check other fields because execution order between fields is not guaranteed. `@model_validator(mode='after')` runs after all fields are independently validated. It operates as an instance method on `self`, allowing comprehensive cross-field consistency checks.",
        "from datetime import date\nfrom pydantic import BaseModel, model_validator\n\nclass DateRange(BaseModel):\n    start_date: date\n    end_date: date\n\n    # Validates relationship across multiple fields\n    @model_validator(mode='after')\n    def verify_date_order(self) -> 'DateRange':\n        if self.end_date <= self.start_date:\n            raise ValueError('end_date must be strictly after start_date')\n        return self\n\n# Valid range\nr = DateRange(start_date='2026-01-01', end_date='2026-01-10')\nassert r.end_date > r.start_date",
        "Enforcing that end_date is after start_date using @model_validator(mode='after').",
        "Pydantic instantiates the model once all field-level validators pass, then passes the newly created instance to `@model_validator(mode='after')`. The method must return `self`.",
        "Validating password confirmation matches, checking date range validity in booking engines, and conditional field requirements.",
        ["Why must `@model_validator(mode='after')` return `self`?", "What is the difference between `@model_validator(mode='after')` and legacy Pydantic v1 `@root_validator`?"],
        ["Forgetting `return self` at the end of `@model_validator(mode='after')`, which causes the model to become `None`.", "Using field validators for multi-field logic where fields might not have been validated yet."],
        "Critical rule: In `@model_validator(mode='after')`, the method is an instance method (`def func(self)`) and MUST return `self`.",
        ["[Field Validator](pydantic-and-validation.md)", "[Raw Input Normalization](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/validators/#model-validators"]
    ),

    # FA-INT-053
    (
        "FA-INT-053",
        "model_validator(mode='before') for Raw Input Normalization",
        "`@model_validator(mode='before')` intercepts the raw input data dictionary before any field parsing begins, allowing restructuring of legacy or malformed JSON payloads.",
        "When an API must support legacy client payloads or heterogeneous third-party webhooks where field names or structures do not match your clean domain model, modifying individual fields is insufficient. `@model_validator(mode='before')` receives the raw dictionary (or object) before Pydantic touches any field. It allows renaming keys, collapsing nested structures, or setting dynamic defaults before schema validation commences.",
        "from typing import Any\nfrom pydantic import BaseModel, model_validator\n\nclass CleanPayment(BaseModel):\n    amount: float\n    currency: str\n    customer_id: str\n\n    # Normalizes legacy external webhook format\n    @model_validator(mode='before')\n    @classmethod\n    def normalize_legacy_keys(cls, data: Any) -> Any:\n        if isinstance(data, dict):\n            # Map legacy 'amt' and 'cust_ref' to modern schema keys\n            if 'amt' in data and 'amount' not in data:\n                data['amount'] = data.pop('amt')\n            if 'cust_ref' in data and 'customer_id' not in data:\n                data['customer_id'] = data.pop('cust_ref')\n        return data\n\n# Client sends legacy keys: 'amt' and 'cust_ref'\np = CleanPayment.model_validate({'amt': 99.50, 'currency': 'USD', 'cust_ref': 'CUST-101'})\nassert p.amount == 99.50 and p.customer_id == 'CUST-101'",
        "Normalizing legacy webhook dictionary keys before schema validation with mode='before'.",
        "Pydantic routes raw input to the `mode='before'` classmethod. The transformed dictionary is then fed into Pydantic's Rust validation core, which parses and checks types against model field annotations.",
        "Ingesting messy third-party webhooks (e.g. Stripe, PayPal, Salesforce) with inconsistent naming conventions without complicating internal domain models.",
        ["Why must `@model_validator(mode='before')` be a `@classmethod` while `mode='after'` is an instance method?", "What happens if incoming data is not a dictionary (e.g. an ORM object or primitive)?"],
        ["Mutating input dictionaries in-place without checking `isinstance(data, dict)` first.", "Raising `KeyError` manually instead of returning data and allowing Pydantic to report standard missing field errors."],
        "Design principle: Use `mode='before'` to adapt external data to your schema; use `mode='after'` to enforce business rules on validated models.",
        ["[Model Validator After](pydantic-and-validation.md)", "[Pydantic v1 vs v2](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/validators/#model-validators"]
    ),

    # FA-INT-054
    (
        "FA-INT-054",
        "Pydantic v1 to Pydantic v2 Migration: Key Changes and Breaking Differences",
        "Pydantic v2 rebuilt the validation engine in Rust, introducing major breaking changes: `.dict()` became `.model_dump()`, `@validator` became `@field_validator`, and `class Config` became `ConfigDict`.",
        "Upgrading FastAPI applications from Pydantic v1 to Pydantic v2 is one of the most common modernization tasks in Python backend engineering. Major breaking changes include: 1) Serialization: `model.dict()` -> `model.model_dump()`, `model.json()` -> `model.model_dump_json()`. 2) Parsing: `Model.parse_obj()` -> `Model.model_validate()`, `Model.parse_raw()` -> `Model.model_validate_json()`. 3) Validators: `@validator` -> `@field_validator(@classmethod)`, `@root_validator` -> `@model_validator`. 4) Configuration: `class Config: orm_mode=True` -> `model_config = ConfigDict(from_attributes=True)`. 5) Regex: `regex=` -> `pattern=`.",
        "# Pydantic v1 (LEGACY - DO NOT USE)\n# class LegacyUser(BaseModel):\n#     name: str\n#     class Config:\n#         orm_mode = True\n\n# Pydantic v2 (MODERN & IDIOMATIC)\nfrom pydantic import BaseModel, ConfigDict, field_validator\n\nclass ModernUser(BaseModel):\n    name: str\n    model_config = ConfigDict(from_attributes=True)\n\n    @field_validator('name')\n    @classmethod\n    def validate_name(cls, v: str) -> str:\n        return v.strip().title()",
        "Illustrating modern Pydantic v2 syntax replacing legacy Pydantic v1 conventions.",
        "Pydantic v2 maintains a legacy shim module (`pydantic.v1`) for backwards compatibility during gradual migrations, but modern FastAPI strictly targets v2 core APIs.",
        "Refactoring legacy FastAPI microservices to Pydantic v2 to eliminate technical debt and unlock 10x throughput gains.",
        ["What is `pydantic.v1` and when should it be used during migration?", "How do custom root types change between v1 (`__root__`) and v2 (`RootModel`)?"],
        ["Leaving Pydantic v1 `class Config` in new codebases, which causes deprecation warnings or silent ignored configurations.", "Writing `@field_validator` without `@classmethod`, triggering errors during class creation."],
        "Executive summary: Remember the three big renames: `model_dump()`, `@field_validator`, and `ConfigDict(from_attributes=True)`.",
        ["[BaseModel](pydantic-and-validation.md)", "[Pydantic v2 Core](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/migration/"]
    ),

    # FA-INT-055
    (
        "FA-INT-055",
        "from_attributes=True for ORM Model Serialization (formerly orm_mode)",
        "`from_attributes=True` enables Pydantic models to read data directly from object attributes (e.g. `user.id`) rather than dictionary keys (`user['id']`), simplifying ORM integration.",
        "By default, Pydantic models expect input data to be dictionaries (`data['field']`). However, database ORMs like SQLAlchemy and Django return model instances where fields are accessed as Python attributes (`data.field`). In Pydantic v1, this was called `orm_mode = True`. In Pydantic v2, it was renamed to `from_attributes = True` on `model_config = ConfigDict(from_attributes=True)`. With this setting enabled, you can pass SQLAlchemy ORM objects directly into `Model.model_validate(orm_obj)` or return them from FastAPI routes.",
        "from pydantic import BaseModel, ConfigDict\n\n# Simulated SQLAlchemy ORM class (attributes, not dict keys)\nclass UserORM:\n    def __init__(self, id: int, username: str, email: str):\n        self.id = id\n        self.username = username\n        self.email = email\n\n# Pydantic Response DTO\nclass UserRead(BaseModel):\n    id: int\n    username: str\n    email: str\n    # Enables reading from ORM object attributes\n    model_config = ConfigDict(from_attributes=True)\n\norm_instance = UserORM(id=1, username='alice', email='a@example.com')\n# Serializes directly from ORM instance\nuser_dto = UserRead.model_validate(orm_instance)\nassert user_dto.id == 1 and user_dto.username == 'alice'",
        "Serializing SQLAlchemy ORM instance directly into Pydantic DTO using from_attributes=True.",
        "When `from_attributes=True` is enabled, Pydantic's Rust core attempts `getattr(obj, field_name)` whenever dictionary key lookup fails, extracting attributes directly from Python memory.",
        "Returning SQLAlchemy or Tortoise-ORM database models directly from FastAPI endpoints without manual dictionary conversion.",
        ["What error occurs if you try to serialize an ORM model without `from_attributes=True`?", "How does `from_attributes=True` handle lazy-loaded relationships in SQLAlchemy?"],
        ["Using the deprecated Pydantic v1 `orm_mode = True` in Pydantic v2 codebases.", "Accessing lazy-loaded SQLAlchemy relationships that trigger unexpected N+1 database queries during serialization."],
        "Integration rule: Always add `model_config = ConfigDict(from_attributes=True)` to any Pydantic model designed to serialize ORM entities.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[Database Integration](database-integration.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances"]
    ),

    # FA-INT-056
    (
        "FA-INT-056",
        "Recursive Schemas and Self-Referencing Models with model_rebuild()",
        "Pydantic supports self-referencing and recursive data structures (like category trees and comment threads) through forward references and `Model.model_rebuild()`.",
        "Hierarchical data structures frequently reference their own type. For example, a navigation menu item contains sub-items of the same type, or a comment has nested replies. Because the class is not fully defined when its fields are being parsed, you use string annotations (e.g. `sub_categories: list['Category'] = []`). In Pydantic v2, calling `Category.model_rebuild()` resolves forward references and compiles the recursive validation graph.",
        "from pydantic import BaseModel\n\nclass CategoryNode(BaseModel):\n    id: int\n    title: str\n    # Forward reference to self\n    children: list['CategoryNode'] = []\n\n# Resolve recursive forward references\nCategoryNode.model_rebuild()\n\n# Build recursive tree\ntree = CategoryNode(\n    id=1,\n    title='Electronics',\n    children=[\n        CategoryNode(id=2, title='Laptops', children=[]),\n        CategoryNode(id=3, title='Phones', children=[])\n    ]\n)\nassert len(tree.children) == 2",
        "Constructing and resolving a recursive self-referencing CategoryNode model.",
        "Pydantic parses the stringified type hint and registers a placeholder schema. Calling `model_rebuild()` resolves the type against the module's namespace and updates the Rust validator definition with recursive pointer links.",
        "Modeling comment threads, nested organizational hierarchies, file system folder trees, and JSON AST nodes.",
        ["Why is `model_rebuild()` necessary for self-referencing models in Python?", "What happens if a recursive model contains circular object references at runtime?"],
        ["Forgetting to call `model_rebuild()` when forward references are defined across circular module imports.", "Creating infinite loops by passing cyclical data structures to recursive models (causes recursion depth errors)."],
        "Tip: In Python 3.11+ or with `from __future__ import annotations`, `model_rebuild()` cleanly resolves self-referential schemas.",
        ["[Nested Models](pydantic-and-validation.md)", "[Discriminated Unions](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#self-referencing-models"]
    ),

    # FA-INT-057
    (
        "FA-INT-057",
        "Discriminated Unions with Field(discriminator='type') for Polymorphic JSON",
        "Discriminated unions route polymorphic JSON payloads to the exact matching Pydantic model based on a shared tag or discriminator field, eliminating ambiguity.",
        "APIs often accept or return polymorphic data: for example, a notification endpoint may accept `EmailNotification`, `SMSNotification`, or `PushNotification`. A standard union (`Union[Email, SMS, Push]`) attempts to match each model sequentially, which is slow and can misidentify models with overlapping fields. By adding a discriminator field (e.g. `type: Literal['email']`) and declaring `Field(discriminator='type')`, Pydantic performs an instant O(1) tag lookup to select the exact model.",
        "from typing import Literal, Union, Annotated\nfrom pydantic import BaseModel, Field\n\nclass EmailMessage(BaseModel):\n    type: Literal['email']\n    recipient_email: str\n    subject: str\n\nclass SMSMessage(BaseModel):\n    type: Literal['sms']\n    phone_number: str\n    body: str\n\n# Tagged discriminated union\nNotificationPayload = Annotated[\n    Union[EmailMessage, SMSMessage],\n    Field(discriminator='type')\n]\n\nclass DispatchEvent(BaseModel):\n    event_id: str\n    message: NotificationPayload\n\n# Parses SMSMessage directly based on 'type': 'sms'\nevent = DispatchEvent.model_validate({\n    'event_id': 'EV-101',\n    'message': {'type': 'sms', 'phone_number': '+15551234', 'body': 'Your code is 1234'}\n})\nassert isinstance(event.message, SMSMessage)",
        "Routing polymorphic notification payloads using discriminated unions.",
        "Pydantic inspects the discriminator key `'type'` in the incoming JSON dictionary and jumps directly to the corresponding Rust validation schema, bypassing trial-and-error sequential matching.",
        "Processing heterogeneous webhook events (e.g. Stripe `payment_intent.succeeded` vs `charge.refunded`), message bus event dispatching, and polymorphic API schemas.",
        ["How does a discriminated union improve validation performance over a plain union?", "How are discriminated unions documented in OpenAPI and Swagger UI (`oneOf` + `discriminator`)?"],
        ["Omitting the `Literal` type on the discriminator field in child models.", "Using a plain union for models with similar fields, leading to incorrect schema selection."],
        "Architecture rule: Always use discriminated unions for polymorphic JSON; it provides O(1) parsing speed and unambiguous OpenAPI schemas.",
        ["[Literal Types](pydantic-and-validation.md)", "[Pydantic BaseModel](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions"]
    ),

    # FA-INT-058
    (
        "FA-INT-058",
        "Computed Fields with @computed_field for Derived Properties",
        "`@computed_field` marks a property method to be included in model serialization (`model_dump()`, JSON output) and OpenAPI documentation as a read-only field.",
        "Models often contain attributes derived from other fields (e.g. calculating `total_price` from `price * quantity`, or formatting `full_name` from `first_name` and `last_name`). In Pydantic v1, property getters were excluded from serialization. Pydantic v2 introduced `@computed_field`. When applied to a `@property` method, Pydantic includes the property in `model_dump()`, `model_dump_json()`, and the generated OpenAPI schema as a `readOnly` field.",
        "from pydantic import BaseModel, computed_field\n\nclass InvoiceItem(BaseModel):\n    description: str\n    unit_price: float\n    quantity: int\n\n    # Automatically serialized as a JSON field and documented in OpenAPI\n    @computed_field\n    @property\n    def total_cost(self) -> float:\n        return round(self.unit_price * self.quantity, 2)\n\nitem = InvoiceItem(description='Widget', unit_price=19.99, quantity=3)\nserialized = item.model_dump()\nassert serialized['total_cost'] == 59.97\nassert 'total_cost' in item.model_dump_json()",
        "Serializing derived calculations into JSON responses using @computed_field.",
        "Pydantic records the computed field descriptor in the model's schema. During serialization, it evaluates the property getter and injects the returned value into the output dictionary or JSON string.",
        "Returning calculated invoice totals, generating dynamic image URLs, and exposing formatted user display names.",
        ["Why must `@computed_field` methods include a return type annotation?", "Can clients supply values for a `@computed_field` in incoming JSON request bodies?"],
        ["Forgetting the return type annotation on `@computed_field` (causes errors because Pydantic needs the type for OpenAPI schema generation).", "Executing expensive database queries or blocking network I/O inside computed field properties."],
        "Best practice: Always add return type annotations to `@computed_field` so OpenAPI documents the correct data type in Swagger UI.",
        ["[BaseModel](pydantic-and-validation.md)", "[Serialization](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/fields/#computed-fields"]
    ),

    # FA-INT-059
    (
        "FA-INT-059",
        "Custom Serializers with @field_serializer and @model_serializer",
        "`@field_serializer` and `@model_serializer` define custom Python logic for converting model fields or entire models into JSON-compatible outputs during serialization.",
        "While validators control how data enters your application, serializers control how data leaves your application. In Pydantic v2, `@field_serializer` allows transforming a specific field during `model_dump()` or `model_dump_json()` (e.g. formatting a `datetime` to a custom string, or masking numbers). `@model_serializer` provides complete control over how the entire model instance is converted to an outgoing dictionary or primitive.",
        "from datetime import datetime\nfrom pydantic import BaseModel, field_serializer\n\nclass AuditLog(BaseModel):\n    action: str\n    timestamp: datetime\n\n    # Custom serializer for the timestamp field\n    @field_serializer('timestamp')\n    def serialize_timestamp(self, ts: datetime, _info) -> str:\n        # Format as custom human-readable string\n        return ts.strftime('%Y-%m-%d %H:%M:%S UTC')\n\nlog = AuditLog(action='USER_LOGIN', timestamp=datetime(2026, 11, 21, 3, 30))\noutput = log.model_dump()\nassert output['timestamp'] == '2026-11-21 03:30:00 UTC'",
        "Formatting datetime fields during serialization with @field_serializer.",
        "Pydantic injects the custom serializer into the output formatting pipeline. In `mode='plain'`, the custom function replaces the default serializer entirely; in `mode='wrap'`, it can call default serialization logic before or after custom processing.",
        "Converting complex internal data types (like NumPy arrays or Pandas DataFrames) into JSON-compatible representations for API responses.",
        ["What is the difference between `mode='plain'` and `mode='wrap'` in `@field_serializer`?", "How does `@model_serializer` differ from `@field_serializer`?"],
        ["Performing data validation inside a serializer (serializers only run when dumping data, not during input validation).", "Returning non-serializable objects (like raw file handles) from custom serializers."],
        "Symmetry tip: Use validators (`@field_validator`) for incoming data; use serializers (`@field_serializer`) for outgoing data.",
        ["[Field Validator](pydantic-and-validation.md)", "[Computed Fields](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/serialization/#custom-serializers"]
    ),

    # FA-INT-060
    (
        "FA-INT-060",
        "TypeAdapter for Validating Non-BaseModel Types",
        "`TypeAdapter` provides Pydantic validation, serialization, and JSON schema generation for arbitrary Python types (primitives, lists, dicts, unions) without creating a `BaseModel`.",
        "Frequently, APIs receive or process data that is not a dictionary matching a `BaseModel`—such as a top-level JSON array of integers (`list[int]`), a union of primitive types (`int | str`), or a standalone validated string (`EmailStr`). In Pydantic v1, developers were forced to create dummy wrapper models or use `parse_obj_as`. In Pydantic v2, `TypeAdapter(Type)` creates a standalone validation and serialization interface for any valid Python type hint.",
        "from typing import List\nfrom pydantic import TypeAdapter, EmailStr\n\n# Create a standalone validator for a list of email addresses\nemail_list_adapter = TypeAdapter(List[EmailStr])\n\nraw_data = ['alice@example.com', 'bob@test.org']\n# Validates list of emails directly\nvalidated_emails = email_list_adapter.validate_python(raw_data)\nassert len(validated_emails) == 2\n\n# Direct JSON dumping without a BaseModel wrapper\njson_bytes = email_list_adapter.dump_json(validated_emails)\nassert b'alice@example.com' in json_bytes",
        "Validating and serializing a list of emails using TypeAdapter without a BaseModel.",
        "`TypeAdapter` instantiates Pydantic's Rust validation core for the target type hint. Methods like `validate_python()`, `validate_json()`, and `dump_json()` interact directly with Rust validation schemas.",
        "Validating message queue payloads, deserializing raw lists from Redis, and validating standalone function arguments.",
        ["Why is `TypeAdapter` faster than legacy Pydantic v1 `parse_obj_as`?", "Can `TypeAdapter` generate JSON Schema for non-model types?"],
        ["Instantiating `TypeAdapter(type)` inside loops repeatedly instead of creating it once at the module level.", "Wrapping primitive lists in dummy `BaseModel` classes unnecessarily."],
        "Performance rule: Instantiate `TypeAdapter` once at module level and reuse it to avoid recompiling Rust schemas.",
        ["[Pydantic v2 Core](pydantic-and-validation.md)", "[Batch Processing](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/type_adapter/"]
    ),

    # FA-INT-061
    (
        "FA-INT-061",
        "Extra Attributes Handling (extra='forbid', 'ignore', 'allow')",
        "`extra` in `model_config = ConfigDict(extra='...')` controls how Pydantic handles unmapped fields passed in incoming client payloads.",
        "When a client sends unexpected keys in a JSON request body, Pydantic's behavior is dictated by the `extra` configuration setting: 1) `'ignore'` (default): Silently discards extra fields; they are not saved on the model. 2) `'forbid'`: Strictly rejects requests containing undeclared fields with a 422 validation error. 3) `'allow'`: Stores extra attributes on the model, accessible via `model.__pydantic_extra__` or dot-notation. In security-sensitive environments, `extra='forbid'` prevents parameter injection vulnerabilities.",
        "from pydantic import BaseModel, ConfigDict, ValidationError\n\nclass StrictRegistration(BaseModel):\n    model_config = ConfigDict(extra='forbid')\n    username: str\n    password: str\n\n# Attempting to send extra 'is_admin' field triggers validation failure\ntry:\n    StrictRegistration(username='eve', password='secret', is_admin=True)\nexcept ValidationError as exc:\n    print('Extra field rejected cleanly:', exc.errors()[0]['type'])\n    assert exc.errors()[0]['type'] == 'extra_forbidden'",
        "Rejecting unexpected extra payload attributes with extra='forbid'.",
        "In `extra='forbid'`, Pydantic's Rust deserializer checks whether input dictionary keys exceed declared schema keys, raising an `extra_forbidden` error immediately upon encountering an unmapped key.",
        "Preventing mass assignment vulnerabilities where attackers submit unauthorized fields (e.g. `role='admin'`, `balance=1000000`) into data models.",
        ["Why is `extra='ignore'` the default behavior in Pydantic?", "What is a Mass Assignment vulnerability and how does `extra='forbid'` mitigate it?"],
        ["Assuming `extra='ignore'` rejects unexpected data (it quietly drops extra fields).", "Using `extra='forbid'` on webhook ingestion models where third-party providers regularly add new fields without warning."],
        "Security recommendation: Set `extra='forbid'` on user registration and billing models to prevent mass assignment attacks.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[API Security](authentication-and-security.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#extra-fields"]
    ),

    # FA-INT-062
    (
        "FA-INT-062",
        "Immutability and Frozen Models with frozen=True",
        "`frozen=True` creates immutable model instances whose attributes cannot be modified after instantiation, making models hashable and thread-safe.",
        "In concurrent and multi-threaded architectures, mutable shared objects are a primary source of race conditions and state corruption bugs. Setting `model_config = ConfigDict(frozen=True)` makes a Pydantic model immutable. Any attempt to modify an attribute (e.g. `model.status = 'inactive'`) raises a `ValidationError`. Furthermore, frozen models automatically implement `__hash__`, allowing them to be used as keys in dictionaries or stored in Python sets.",
        "from pydantic import BaseModel, ConfigDict, ValidationError\n\nclass ImmutablePoint(BaseModel):\n    model_config = ConfigDict(frozen=True)\n    x: int\n    y: int\n\npt = ImmutablePoint(x=10, y=20)\n\n# Attempting to mutate raises error\ntry:\n    pt.x = 99\nexcept ValidationError as exc:\n    print('Mutation blocked:', exc.errors()[0]['type'])\n\n# Hashable: Can be used in sets and dict keys\npoint_set = {pt}\nassert pt in point_set",
        "Creating immutable, hashable models using frozen=True.",
        "`frozen=True` overrides `__setattr__` and `__delattr__` on the class, causing any assignment to raise a `ValidationError`. It also generates a `__hash__` method derived from all field values.",
        "Creating thread-safe configuration objects, domain value objects (DDD), and using model instances as cache keys in dictionaries.",
        ["Why can't standard (non-frozen) Pydantic models be used as dictionary keys?", "How does `frozen=True` interact with nested mutable structures like lists?"],
        ["Mutating model state after validation instead of creating new instances via `model.model_copy(update={...})`.", "Assuming `frozen=True` prevents modification of nested mutable containers (use frozen sets or tuples for deep immutability)."],
        "Clean architecture tip: Use `frozen=True` for Domain-Driven Design (DDD) Value Objects to enforce immutability guarantees.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[Extra Attributes](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#faux-immutability"]
    ),

    # FA-INT-063
    (
        "FA-INT-063",
        "Dynamic Field Population and Default Factories",
        "`default_factory` accepts a callable that is invoked dynamically each time a model is instantiated, preventing shared mutable default bugs.",
        "A classic Python anti-pattern is assigning mutable defaults like `tags: list = []` or `timestamp = datetime.now()`, which evaluates once at module load time and shares the same object across all instances. Pydantic solves this via `Field(default_factory=callable)`. The factory callable is evaluated afresh for every single instance created, ensuring dynamic timestamps and unique container instances.",
        "import uuid\nfrom datetime import datetime, timezone\nfrom pydantic import BaseModel, Field\n\nclass AuditRecord(BaseModel):\n    # Evaluated dynamically on EVERY instantiation\n    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))\n    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))\n    tags: list[str] = Field(default_factory=list)\n\nr1 = AuditRecord()\nr2 = AuditRecord()\n# Guaranteed unique UUIDs and separate list objects\nassert r1.record_id != r2.record_id\nassert r1.tags is not r2.tags",
        "Generating dynamic UUIDs, timestamps, and isolated lists using default_factory.",
        "During model instantiation, if an attribute is omitted from the input dictionary, Pydantic invokes the assigned `default_factory` callable and assigns the returned value to the field.",
        "Generating automatic timestamps for database records, assigning unique request IDs, and creating isolated mutable containers.",
        ["Why does `created_at = datetime.now()` freeze the timestamp at server boot time?", "Can a `default_factory` accept arguments from other model fields?"],
        ["Using `default=datetime.now()` instead of `default_factory=datetime.now` (creates identical timestamps for all requests).", "Passing `default_factory=my_func()` (calling the function) instead of `default_factory=my_func` (passing the callable)."],
        "Golden rule: Always use `default_factory` for mutable objects (`list`, `dict`) and dynamic values (`datetime.now`, `uuid.uuid4`).",
        ["[Field Parameters](pydantic-and-validation.md)", "[BaseModel](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/fields/#default-values"]
    ),

    # FA-INT-064
    (
        "FA-INT-064",
        "String Stripping and Whitespace Normalization",
        "`str_strip_whitespace=True` on `model_config = ConfigDict(str_strip_whitespace=True)` automatically strips leading and trailing whitespace from all string fields across the model.",
        "Accidental leading or trailing whitespace in form submissions or API requests (e.g. `' user@example.com '` or `' Alice '`) causes duplicate records, search mismatches, and database pollution. Manually calling `.strip()` on every string field in validators is tedious. Setting `model_config = ConfigDict(str_strip_whitespace=True)` instructs Pydantic to automatically strip leading and trailing whitespace from all string fields in the model before validation runs.",
        "from pydantic import BaseModel, ConfigDict\n\nclass CleanUser(BaseModel):\n    model_config = ConfigDict(str_strip_whitespace=True)\n    username: str\n    email: str\n\nu = CleanUser(username='   john_doe   ', email='  john@example.com  ')\n# Whitespace is automatically stripped\nassert u.username == 'john_doe'\nassert u.email == 'john@example.com'",
        "Automatically stripping leading and trailing whitespace using str_strip_whitespace=True.",
        "Pydantic's Rust string validator trims ASCII and Unicode whitespace characters before checking string length constraints (`min_length`, `max_length`) or regex patterns.",
        "Sanitizing user registration inputs, search keywords, and form fields to ensure clean database storage.",
        ["Does `str_strip_whitespace` strip whitespace between words in the middle of a string?", "How does `str_strip_whitespace` affect string length validations?"],
        ["Writing redundant `@field_validator` functions to strip strings manually.", "Assuming `str_strip_whitespace` removes internal spaces (it only trims leading and trailing whitespace)."],
        "Production tip: Always enable `str_strip_whitespace=True` on user input models to prevent trailing space bugs in authentication and search.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[Field Validator](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/config/#str_strip_whitespace"]
    ),

    # FA-INT-065
    (
        "FA-INT-065",
        "Custom JSON Encoders and Decoders in Pydantic v2",
        "Pydantic v2 customizes JSON encoding and decoding through `@field_serializer(mode='plain')` and `model_dump_json()`, replacing Pydantic v1's `json_encoders` dictionary.",
        "In Pydantic v1, custom serialization of specific types (like Decimal, UUID, or custom classes) was configured using a `json_encoders` dictionary in class `Config`. In Pydantic v2, `json_encoders` is deprecated in favor of `@field_serializer` or custom serializers registered via `Annotated[Type, PlainSerializer(...)]`. This modern pattern integrates directly with Pydantic's Rust serialization engine.",
        "from decimal import Decimal\nfrom typing import Annotated\nfrom pydantic import BaseModel, PlainSerializer\n\n# Custom serializer converting Decimal to formatted currency string\nCurrency = Annotated[\n    Decimal,\n    PlainSerializer(lambda d: f'${d:.2f}', return_type=str, when_used='json')\n]\n\nclass TransactionRecord(BaseModel):\n    tx_id: str\n    amount: Currency\n\ntx = TransactionRecord(tx_id='TX-99', amount=Decimal('1250.5'))\n# Serializes Decimal to '$1250.50' in JSON\nassert '\"$1250.50\"' in tx.model_dump_json()",
        "Formatting custom Decimal serialization using PlainSerializer in Pydantic v2.",
        "`PlainSerializer` compiles directly into Rust's `serde_json` serializer for that field, avoiding Python dictionary translation overhead.",
        "Formatting currency values, encoding geospatial geometries to GeoJSON, and serializing custom scientific types.",
        ["Why was `json_encoders` deprecated in Pydantic v2?", "What is the role of `when_used='json'` vs `when_used='always'` in `PlainSerializer`?"],
        ["Attempting to use legacy `class Config: json_encoders = {...}` in Pydantic v2 (ignored or deprecated).", "Serializing floating point numbers for currency instead of `Decimal`."],
        "Migration rule: Replace Pydantic v1 `json_encoders` with `PlainSerializer` or `@field_serializer` for clean v2 serialization.",
        ["[Custom Serializers](pydantic-and-validation.md)", "[Pydantic v1 vs v2](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/serialization/#custom-types"]
    ),

    # FA-INT-066
    (
        "FA-INT-066",
        "Schema Inheritance and Model Composition Patterns",
        "Structuring Pydantic models with inheritance (Base -> Create -> Update -> Read) avoids code duplication while maintaining distinct validation rules across CRUD operations.",
        "In RESTful API design, different operations on the same entity have different constraints: 1) Creation (`ItemCreate`): Requires `name` and `price`; `id` is not present because the DB hasn't generated it yet. 2) Update (`ItemUpdate`): All fields are optional. 3) Read (`ItemRead`): `id` and `created_at` are required; sensitive fields are omitted. Using class inheritance allows sharing common fields on `ItemBase` while tailoring subclasses for specific CRUD operations.",
        "from pydantic import BaseModel, ConfigDict\n\n# Shared attributes\nclass ItemBase(BaseModel):\n    title: str\n    description: str | None = None\n    price: float\n\n# Schema for incoming POST requests\nclass ItemCreate(ItemBase):\n    pass\n\n# Schema for incoming PATCH requests (all fields optional)\nclass ItemUpdate(BaseModel):\n    title: str | None = None\n    description: str | None = None\n    price: float | None = None\n\n# Schema for outgoing GET responses (includes DB generated fields)\nclass ItemRead(ItemBase):\n    id: int\n    model_config = ConfigDict(from_attributes=True)",
        "Implementing clean CRUD schema hierarchy with inheritance.",
        "Pydantic merges field annotations from parent classes in Method Resolution Order (MRO), allowing subclasses to add new fields or override existing constraints.",
        "Standardizing API contracts across enterprise CRUD microservices with clean separation between internal state and public DTOs.",
        ["How do you override a field constraint in a subclass?", "Why shouldn't `ItemRead` be used for request body validation in POST endpoints?"],
        ["Using a single monolithic model for both input validation and output serialization, leading to optional `id` fields everywhere.", "Allowing clients to pass `id` or `created_at` in POST requests."],
        "Enterprise pattern: Always use the quartet: `EntityBase`, `EntityCreate`, `EntityUpdate`, and `EntityRead`.",
        ["[BaseModel](pydantic-and-validation.md)", "[from_attributes](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/extra-models/"]
    ),

    # FA-INT-067
    (
        "FA-INT-067",
        "Partial Updates and PATCH Validation Patterns with exclude_unset",
        "Combining optional model fields with `model_dump(exclude_unset=True)` allows implementing idempotent PATCH endpoints that only update fields explicitly sent by the client.",
        "In HTTP semantics, PUT replaces an entire resource, while PATCH modifies only specified fields. Implementing PATCH in FastAPI requires distinguishing between: 1) A field omitted by the client (should NOT be updated). 2) A field explicitly set to `null` by the client (should be set to `None` in the database). By typing fields as `str | None = None` and calling `update_data.model_dump(exclude_unset=True)`, only keys actually transmitted by the client are included in the update dictionary.",
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass ProfileUpdate(BaseModel):\n    bio: str | None = None\n    website: str | None = None\n\n# Simulated DB entity\ndb_user = {'id': 1, 'bio': 'Original bio', 'website': 'https://example.com'}\n\n@app.patch('/profile')\ndef patch_profile(update: ProfileUpdate):\n    # Client sends: {\"bio\": \"Updated bio\"} (website omitted)\n    update_fields = update.model_dump(exclude_unset=True)\n    # update_fields is: {'bio': 'Updated bio'}\n    db_user.update(update_fields)\n    return db_user",
        "Updating only explicitly provided fields using model_dump(exclude_unset=True).",
        "Pydantic tracks field assignment in `model.__pydantic_fields_set__`. When `exclude_unset=True` is passed, it filters out any field not present in `__pydantic_fields_set__`.",
        "Implementing partial updates for user settings, profile updates, and status toggles.",
        ["What is the difference between `exclude_unset=True` and `exclude_none=True`?", "How can a client explicitly clear a field to null using `exclude_unset=True`?"],
        ["Using `exclude_none=True` instead of `exclude_unset=True`, making it impossible for clients to clear a field by sending `null`.", "Updating database records with `model.model_dump()` without `exclude_unset=True`, accidentally overwriting untouched fields with `None`."],
        "Crucial interview tip: `exclude_unset=True` preserves explicit `null` values while dropping omitted fields; `exclude_none=True` strips both.",
        ["[Optional Fields](pydantic-and-validation.md)", "[model_dump](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch"]
    ),

    # FA-INT-068
    (
        "FA-INT-068",
        "Handling Arbitrary Types with arbitrary_types_allowed=True",
        "`arbitrary_types_allowed=True` allows Pydantic models to accept custom classes or third-party objects that do not have built-in Pydantic validation.",
        "By default, Pydantic raises a `PydanticSchemaGenerationError` if a field is annotated with a type it does not know how to validate (such as a database connection pool, a PyTorch model, or a custom C-extension class). Setting `model_config = ConfigDict(arbitrary_types_allowed=True)` disables this restriction, validating only that incoming values are instances of the specified class via `isinstance` checks.",
        "from pydantic import BaseModel, ConfigDict\n\n# Custom class without Pydantic integration\nclass CustomConnectionPool:\n    def __init__(self, host: str):\n        self.host = host\n\nclass ServerContext(BaseModel):\n    model_config = ConfigDict(arbitrary_types_allowed=True)\n    pool: CustomConnectionPool\n    port: int\n\n# Successfully accepts custom instance\npool_obj = CustomConnectionPool(host='localhost')\nctx = ServerContext(pool=pool_obj, port=8000)\nassert ctx.pool.host == 'localhost'",
        "Allowing arbitrary third-party types in Pydantic models with arbitrary_types_allowed=True.",
        "When `arbitrary_types_allowed=True` is enabled, Pydantic's schema generator generates an `is-instance` Rust validator for that field instead of attempting to construct a recursive schema.",
        "Passing heavy ML model weights, active database connection objects, or thread locks through application context models.",
        ["What are the limitations of `arbitrary_types_allowed` when serializing to JSON (`model_dump_json()`)?", "Why is `arbitrary_types_allowed` disabled by default in Pydantic?"],
        ["Using arbitrary types in models designed for public API JSON input (arbitrary types cannot be parsed from raw JSON strings).", "Failing to define a custom serializer when an arbitrary type model needs to be dumped to JSON."],
        "Architecture note: Use `arbitrary_types_allowed` for internal dependency and context containers, not for public HTTP request/response schemas.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[Custom Serializers](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/config/#arbitrary_types_allowed"]
    ),

    # FA-INT-069
    (
        "FA-INT-069",
        "Generic Pydantic Models for Standardized API Wrappers (Generic[T])",
        "Subclassing `Generic[T]` allows creating reusable envelope models (like paginated responses or standard API envelopes) that preserve strong typing for any inner data type.",
        "In enterprise APIs, responses are often wrapped in a standardized envelope: `{'status': 'success', 'data': [...], 'meta': {...}}`. Rather than defining separate pagination models for every domain entity (`UserPagination`, `ItemPagination`), Python's `typing.Generic[T]` enables creating a single generic `PaginatedResponse[T]` model. When typed as `PaginatedResponse[UserRead]`, Pydantic generates exact OpenAPI schemas and validates items against `UserRead`.",
        "from typing import Generic, TypeVar, List\nfrom pydantic import BaseModel\n\nT = TypeVar('T')\n\nclass PaginatedResponse(BaseModel, Generic[T]):\n    items: List[T]\n    total_count: int\n    page: int\n    page_size: int\n\nclass User(BaseModel):\n    id: int\n    username: str\n\n# Concrete parameterized generic model\nresponse = PaginatedResponse[User](\n    items=[User(id=1, username='alice')],\n    total_count=1,\n    page=1,\n    page_size=20\n)\nassert response.items[0].username == 'alice'",
        "Defining reusable generic pagination envelopes with Generic[T].",
        "Pydantic creates a specialized subclass at runtime when `PaginatedResponse[User]` is evaluated, substituting `T` with `User` in the compiled Rust schema.",
        "Standardizing API response envelopes, paginated collections, and error payload structures across all company services.",
        ["How does OpenAPI represent generic models in Swagger UI?", "Can multiple TypeVars be used in a single generic Pydantic model (`Generic[T, E]`)?"],
        ["Omitting `Generic[T]` from the class inheritance list (`class Model(BaseModel, Generic[T]):`).", "Using untyped `list[Any]` for generic response models, losing API documentation fidelity in Swagger UI."],
        "Design best practice: Standardize all paginated endpoints using a single `PaginatedResponse[T]` generic model.",
        ["[BaseModel](pydantic-and-validation.md)", "[Nested Models](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#generic-models"]
    ),

    # FA-INT-070
    (
        "FA-INT-070",
        "Masking Sensitive Fields in Logs vs Serialized JSON",
        "Combining `SecretStr` with custom field serializers allows masking sensitive values in standard application logs while conditionally exposing them to authorized encrypted vaults.",
        "In financial and healthcare applications, sensitive data (like credit card numbers, Social Security Numbers, or auth tokens) must never be displayed in plain text in logs or error traces. However, legitimate authorized processes (like payment gateways) still need access to the decrypted value. By using `SecretStr` or custom serializers, you can enforce that `repr()` displays masked values (`'****-****-****-1234'`) while providing explicit getter methods for secure processing.",
        "from pydantic import BaseModel, SecretStr, field_serializer\n\nclass CardPayment(BaseModel):\n    cardholder: str\n    card_number: SecretStr\n\n    # Custom serializer to format masked output in public JSON\n    @field_serializer('card_number')\n    def mask_card(self, v: SecretStr) -> str:\n        raw = v.get_secret_value()\n        return f'****-****-****-{raw[-4:]}'\n\npayment = CardPayment(cardholder='Alice Smith', card_number='4111222233334444')\n# Safe representation in logs\nprint(f'Safe log output: {payment.model_dump()}')\nassert payment.model_dump()['card_number'] == '****-****-****-4444'",
        "Masking credit card numbers in logs and JSON dumps while storing securely.",
        "`SecretStr` hides the string in `__repr__`. The `@field_serializer` formats the last 4 digits for outgoing JSON responses, while `.get_secret_value()` remains accessible for the payment processor.",
        "PCI-DSS compliance for payment processing, HIPAA compliance for medical identifiers, and audit logging.",
        ["What is PCI-DSS and how does masking card data in logs support compliance?", "How can you ensure sensitive fields are never written to unencrypted log files?"],
        ["Printing raw model instances containing plain `str` credit cards to standard output or log aggregators.", "Storing decrypted secrets in global variables where they can be captured in memory dumps."],
        "Security rule: Never log raw card numbers or passwords; use `SecretStr` and explicit masking serializers to guarantee compliance.",
        ["[Secret Types](pydantic-and-validation.md)", "[API Security](authentication-and-security.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#secret-types"]
    ),

    # FA-INT-071
    (
        "FA-INT-071",
        "Alias Generators for Snake_case to CamelCase Conversion",
        "`alias_generator = to_camel` automatically bridges Python snake_case conventions with JavaScript camelCase frontend conventions across all model fields.",
        "Python PEP 8 mandates `snake_case` variable naming (e.g. `user_first_name`), whereas JavaScript and frontend JSON conventions overwhelmingly favor `camelCase` (e.g. `userFirstName`). Manually adding `Field(alias='userFirstName')` to every field across dozens of models is tedious and error-prone. In Pydantic v2, setting `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` automates this conversion across the entire model.",
        "from pydantic import BaseModel, ConfigDict\nfrom pydantic.alias_generators import to_camel\n\nclass CamelModel(BaseModel):\n    model_config = ConfigDict(\n        alias_generator=to_camel,\n        populate_by_name=True  # Allows instantiating with either snake_case or camelCase\n    )\n    first_name: str\n    order_count: int\n\n# Client sends camelCase JSON\nu = CamelModel.model_validate({'firstName': 'Alice', 'orderCount': 5})\nassert u.first_name == 'Alice'\n\n# Dumps to camelCase JSON for frontend consumption\nassert '\"firstName\":\"Alice\"' in u.model_dump_json(by_alias=True)",
        "Automating snake_case to camelCase mapping using to_camel alias generator.",
        "`alias_generator` executes during model schema compilation, dynamically generating `alias` strings for every field in the Rust validation and serialization tables.",
        "Building seamless full-stack web applications where TypeScript/React frontends communicate with Python backends without naming friction.",
        ["Why must `populate_by_name=True` be enabled alongside `alias_generator`?", "What happens if a field already specifies an explicit `alias`?"],
        ["Forgetting `by_alias=True` in `model_dump()`, causing the output to revert to Python snake_case.", "Omitting `populate_by_name=True`, preventing internal Python code from initializing models using snake_case kwargs."],
        "Clean integration tip: Create a shared `CamelCaseBaseModel` with `alias_generator=to_camel` and inherit from it across all API response models.",
        ["[Parameter Aliasing](routing-and-dependencies.md)", "[Pydantic ConfigDict](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/alias/"]
    ),

    # FA-INT-072
    (
        "FA-INT-072",
        "Validating IP Addresses and Networks (IPvAnyAddress, IPvAnyNetwork)",
        "`IPvAnyAddress` and `IPvAnyNetwork` validate IPv4 and IPv6 addresses and CIDR subnets, parsing them into standard library `ipaddress` objects.",
        "APIs that manage firewall configurations, network interfaces, or IP-based geolocation require rigorous IP validation. Pydantic provides `IPvAnyAddress`, `IPvAnyNetwork`, `IPvAnyInterface` (as well as specific `IPv4Address` and `IPv6Address` types). These types validate address formatting, reject invalid octets (e.g. `256.0.0.1`), and convert inputs into Python's native `ipaddress.IPv4Address` or `ipaddress.IPv6Address` objects.",
        "from pydantic import BaseModel, IPvAnyAddress, IPvAnyNetwork\n\nclass FirewallRule(BaseModel):\n    rule_name: str\n    client_ip: IPvAnyAddress\n    allowed_subnet: IPvAnyNetwork\n\n# Parses valid IPv4 and IPv6 addresses and CIDR networks\nrule = FirewallRule(\n    rule_name='Allow-VPN',\n    client_ip='192.168.1.100',\n    allowed_subnet='10.0.0.0/24'\n)\nassert rule.client_ip.version == 4\nassert rule.allowed_subnet.num_addresses == 256",
        "Validating IPv4/IPv6 addresses and CIDR subnets using IPvAnyAddress and IPvAnyNetwork.",
        "Pydantic passes the string to Python's standard `ipaddress.ip_address` or `ipaddress.ip_network` parser in Rust, verifying valid IP octets and prefix lengths.",
        "Cloud infrastructure automation, VPN configuration APIs, and IP allowlist management.",
        ["What error occurs if an IP address contains octets greater than 255?", "How does `IPvAnyAddress` handle IPv6 compressed representations like `::1`?"],
        ["Using plain `str` with custom regex to validate IP addresses (often failing on complex IPv6 compressed notation).", "Forgetting to convert the `ipaddress` object back to `str` before serializing to standard databases."],
        "Standard library advantage: Pydantic's IP types yield real `ipaddress` objects, allowing direct subnet containment checks (`client_ip in allowed_subnet`).",
        ["[BaseModel](pydantic-and-validation.md)", "[URL Validation](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/types/#network-types"]
    ),

    # FA-INT-073
    (
        "FA-INT-073",
        "Validation Context Passing with ValidationInfo",
        "`ValidationInfo` provides validators with execution context, such as runtime configuration, user roles, or parent field data, passed via `context={...}`.",
        "Standard field validators only receive the field value being validated. However, certain validation decisions require external runtime context (e.g. validating a currency against the current user's country, or toggling strict validation flags during bulk imports). Pydantic v2 supports context passing: developers pass `Model.model_validate(data, context={'role': 'admin'})`, and validators receive this dictionary via the `info: ValidationInfo` argument.",
        "from pydantic import BaseModel, Field, ValidationInfo, field_validator\n\nclass Document(BaseModel):\n    title: str\n    content: str\n\n    @field_validator('content')\n    @classmethod\n    def validate_content_length(cls, v: str, info: ValidationInfo) -> str:\n        # Access runtime context dictionary\n        if info.context and info.context.get('strict_length'):\n            if len(v) < 100:\n                raise ValueError('In strict mode, content must be at least 100 characters')\n        return v\n\n# Standard validation passes\nDoc = Document.model_validate({'title': 'Draft', 'content': 'Short'}, context={'strict_length': False})\nassert Doc.title == 'Draft'",
        "Passing runtime context into field validators using ValidationInfo.",
        "`ValidationInfo` is a struct passed by Pydantic's Rust validation engine into validator callables. It contains `info.context`, `info.data` (sibling fields validated so far), and `info.field_name`.",
        "Executing conditional validation during batch imports vs single-item updates, and role-sensitive field validation.",
        ["What attributes are available on the `ValidationInfo` object in Pydantic v2?", "Can context be passed to Pydantic models inside FastAPI route handlers?"],
        ["Attempting to access sibling fields via `values` dict as in Pydantic v1 (use `info.data` instead).", "Relying on global variables to pass validation context instead of using `ValidationInfo`."],
        "Migration tip: In Pydantic v2, replace `values` dictionary in `@validator` with `info: ValidationInfo` and `info.data`.",
        ["[Field Validator](pydantic-and-validation.md)", "[Model Validator](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/validators/#validation-info"]
    ),

    # FA-INT-074
    (
        "FA-INT-074",
        "Custom Base Classes for Enterprise Model Consistency",
        "Creating an abstract enterprise base model establishes organization-wide standards for whitespace trimming, camelCase aliasing, and ORM attribute loading.",
        "In large engineering teams, repeating `model_config = ConfigDict(...)` across hundreds of models leads to inconsistencies and configuration drift. The enterprise best practice is to define a customized base class (e.g. `AppBaseModel(BaseModel)`) with organization-wide default configurations. All application models then inherit from this enterprise base class, ensuring uniform behavior.",
        "from pydantic import BaseModel, ConfigDict\nfrom pydantic.alias_generators import to_camel\n\nclass EnterpriseBaseModel(BaseModel):\n    model_config = ConfigDict(\n        from_attributes=True,        # Support ORM loading everywhere\n        str_strip_whitespace=True,  # Strip whitespace globally\n        alias_generator=to_camel,   # Standardize on camelCase for API clients\n        populate_by_name=True,      # Support snake_case in Python code\n        extra='forbid'              # Prevent parameter injection\n    )\n\n# All application models inherit unified standards\nclass UserProfile(EnterpriseBaseModel):\n    user_name: str\n    user_email: str",
        "Defining an EnterpriseBaseModel to standardize configurations across all application schemas.",
        "Subclasses inherit `model_config` settings from parent classes. Pydantic merges configurations, allowing subclasses to extend or selectively override settings when necessary.",
        "Standardizing API contracts and security rules across dozens of microservices maintained by different development teams.",
        ["Can a subclass override a specific configuration setting set by `EnterpriseBaseModel`?", "How does enterprise base class inheritance affect OpenAPI schema generation?"],
        ["Allowing individual developers to define unconfigured `BaseModel` classes, leading to inconsistent JSON naming across microservices.", "Overriding `model_config` in a subclass without merging parent configuration attributes."],
        "Architecture rule: Never inherit directly from `BaseModel` in enterprise production code; always inherit from a curated `EnterpriseBaseModel`.",
        ["[Pydantic ConfigDict](pydantic-and-validation.md)", "[Alias Generators](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/concepts/models/#model-inheritance"]
    ),

    # FA-INT-075
    (
        "FA-INT-075",
        "Performance Profiling: Pydantic v2 Rust Engine (pydantic-core) Speedups",
        "Pydantic v2 achieves 5x to 50x validation and serialization speedups by compiling schemas into Rust validators that run outside Python's GIL and memory allocator.",
        "In Pydantic v1, validation was implemented in pure Python, executing hundreds of Python bytecode instructions per field and suffering significant CPU overhead. Pydantic v2 rewritten around `pydantic-core` (in Rust) compiles schema trees into Rust structs. JSON parsing, date/time decoding, regex matching, and dictionary allocation are performed in compiled machine code, yielding dramatic latency reductions and higher request throughput in FastAPI services.",
        "import time\nfrom pydantic import BaseModel, TypeAdapter\n\nclass BenchmarkRecord(BaseModel):\n    id: int\n    name: str\n    score: float\n\nadapter = TypeAdapter(list[BenchmarkRecord])\npayload = [{'id': i, 'name': f'item_{i}', 'score': i * 1.5} for i in range(10000)]\n\nstart = time.perf_counter()\n# Validates 10,000 records in compiled Rust in a few milliseconds\nvalidated = adapter.validate_python(payload)\nduration = time.perf_counter() - start\nprint(f'Validated 10,000 items in: {duration*1000:.2f} ms')\nassert len(validated) == 10000",
        "Benchmarking high-speed batch validation of 10,000 items with Pydantic v2.",
        "`pydantic-core` executes validation loops in compiled Rust without acquiring Python's GIL for intermediate steps, releasing Python objects directly into pre-allocated memory.",
        "Processing high-frequency IoT telemetry, financial ledger audits, and high-throughput microservice pipelines.",
        ["Why is `model_dump_json()` significantly faster than `json.dumps(model.model_dump())`?", "What role does SIMD (Single Instruction Multiple Data) play in modern JSON parsers?"],
        ["Assuming Python bottlenecks in FastAPI are always network I/O (in v1, JSON validation CPU overhead was often the dominant bottleneck).", "Using manual dictionary conversions that bypass Pydantic v2's compiled Rust pathways."],
        "Benchmark takeaway: Pydantic v2 moves CPU-intensive validation into compiled Rust, making FastAPI competitive with Go and Node.js frameworks.",
        ["[Pydantic v2 Core](pydantic-and-validation.md)", "[TypeAdapter](pydantic-and-validation.md)"],
        ["https://docs.pydantic.dev/latest/blog/pydantic-v2/"]
    ),
]
