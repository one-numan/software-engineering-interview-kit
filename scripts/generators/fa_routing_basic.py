"""
fa_routing_basic.py
===================
Basic FastAPI Routing & Dependencies Questions: FA-BAS-026 to FA-BAS-050 (25 questions)
"""

basic_data = [
    # FA-BAS-026
    (
        "FA-BAS-026",
        "APIRouter Basics and Modular Application Structure",
        "`APIRouter` allows developers to modularize a FastAPI application into distinct, reusable endpoint collections that can be organized across multiple files and mounted onto the main app.",
        "In enterprise software architecture, keeping all API endpoints in a single file causes maintenance bottlenecks and high merge conflicts. FastAPI provides `APIRouter`, which acts like a mini-`FastAPI` application without running its own ASGI server. You define route operations on an `APIRouter` instance, configure common path prefixes, tags, and dependencies, and then mount it onto the root application instance via `app.include_router(router)`. This separation enables clean domain-driven design (DDD) where each domain module (e.g., users, billing, products) owns its routes, schemas, and services.",
        "from fastapi import FastAPI, APIRouter\n\n# users_router.py\nusers_router = APIRouter(prefix='/users', tags=['users'])\n\n@users_router.get('/')\ndef list_users():\n    return [{'id': 1, 'username': 'alice'}, {'id': 2, 'username': 'bob'}]\n\n# main.py\napp = FastAPI(title='Enterprise API')\napp.include_router(users_router)",
        "Creating a modular APIRouter with prefix and tags and mounting it onto the root application.",
        "When `app.include_router()` is invoked, FastAPI copies the route definitions from the `APIRouter` into the main `FastAPI.routes` list, applying router prefixes, tags, and router-level dependencies to each underlying `Route` object.",
        "Structuring multi-team enterprise microservices where separate teams maintain separate domains (auth, inventory, orders) in independent Python packages.",
        ["Can an `APIRouter` include another `APIRouter`?", "What is the difference between `app.include_router()` and `app.mount()`?"],
        ["Attempting to run `uvicorn users_router:users_router` directly instead of targeting the main `FastAPI` instance.", "Forgetting leading slashes in router prefixes or endpoint paths causing unexpected concatenated paths."],
        "Highlight that `APIRouter` is FastAPI's equivalent of Flask Blueprints or Django URL patterns, but with native OpenAPI tag aggregation and dependency scoping.",
        ["[FastAPI Overview](fundamentals.md)", "[Dependency Injection Basics](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]
    ),

    # FA-BAS-027
    (
        "FA-BAS-027",
        "Path Parameters and Automatic Type Casting",
        "Path parameters capture dynamic URL segments declared in path strings with curly braces and automatically parse and validate them into Python types based on type hints.",
        "Path parameters represent dynamic values embedded directly in the HTTP request URL path. In FastAPI, declaring a path parameter is as simple as adding `{param_name}` in the route decorator and adding a matching parameter name with a type annotation in the handler function signature. FastAPI inspects the type hint (such as `int`, `str`, `uuid.UUID`, or `float`), extracts the string segment from Starlette's route match, and validates and converts it automatically. If a client sends a non-conforming value (e.g. string 'abc' for an `int`), FastAPI automatically returns a structured HTTP 422 Unprocessable Entity error.",
        "from uuid import UUID\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/items/{item_id}')\ndef get_item(item_id: int):\n    # item_id is guaranteed to be an integer here\n    return {'item_id': item_id, 'doubled': item_id * 2}\n\n@app.get('/orders/{order_id}')\ndef get_order(order_id: UUID):\n    # Automatically parsed into a standard library UUID object\n    return {'order_id': str(order_id), 'version': order_id.version}",
        "Demonstrating integer and UUID path parameter validation and automatic type coercion.",
        "Starlette matches the incoming URL against compiled regex patterns. Once the URL path variable is matched as a string, FastAPI passes it to Pydantic's type validation engine, which casts the string to the annotated type or raises a `RequestValidationError`.",
        "Retrieving specific database resources by primary key (`/users/{user_id}`) or standard UUID identifiers in RESTful APIs.",
        ["What happens if the client passes `/items/foo` to `item_id: int`?", "Can you use custom types or Pydantic models directly as path parameters?"],
        ["Parsing path parameters manually using `int(item_id)` inside the function body instead of declaring the type hint.", "Using mismatched names between the route URL template `{item_id}` and the function parameter name."],
        "Emphasize that type annotations in FastAPI are not merely documentation—they actively drive parsing, validation, and error reporting.",
        ["[Query Parameters](routing-and-dependencies.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/path-params/"]
    ),

    # FA-BAS-028
    (
        "FA-BAS-028",
        "Query Parameters and Optional Defaults",
        "Function parameters not declared in the route path URL template are automatically recognized by FastAPI as URL query parameters with support for default values and optional types.",
        "Query parameters are key-value pairs appended after the `?` separator in an HTTP URL. In FastAPI, any function parameter that does not appear in the route path decorator (e.g. `@app.get('/items')`) is interpreted as a query parameter. You can specify default values by assigning them in the parameter signature. If a parameter has no default value and is not typed with an optional hint, it becomes a required query parameter. Optional query parameters are declared using `str | None = None` (or `Optional[str] = None`).",
        "from typing import Optional\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/items')\ndef list_items(\n    skip: int = 0,\n    limit: int = 10,\n    search: Optional[str] = None,\n    active_only: bool = False\n):\n    return {\n        'skip': skip,\n        'limit': limit,\n        'search': search,\n        'active_only': active_only\n    }",
        "Defining required, default, optional, and boolean query parameters.",
        "FastAPI parses the query string from the ASGI `scope['query_string']` byte array into a mapping. It maps the query parameter names against the function signature, performing type coercion (e.g. converting `'true'`, `'1'`, `'yes'` into Python `True` for boolean types).",
        "Implementing pagination, filtering, searching, and sorting across tabular dashboard datasets.",
        ["How does FastAPI parse boolean values from query parameters?", "What occurs when a client omits a query parameter that has no default value?"],
        ["Assuming boolean query parameters only accept 'True' and 'False' (FastAPI accepts '1', 'true', 'on', 'yes', '0', 'false', 'off', 'no').", "Using mutable default values (like `items: list = []`) in query parameters."],
        "Explain that FastAPI automatically distinguishes path from query parameters purely by checking if the parameter name appears in the route template.",
        ["[Path Parameters](routing-and-dependencies.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/query-params/"]
    ),

    # FA-BAS-029
    (
        "FA-BAS-029",
        "Combining Path and Query Parameters in a Single Route",
        "FastAPI enables combining path parameters, required query parameters, and optional query parameters in any signature order by matching against the path template.",
        "In RESTful API design, hierarchical resource identification is expressed via path parameters (e.g. `/users/{user_id}/orders/{order_id}`), while filtering, pagination, and presentation options are expressed via query parameters (e.g. `?include_details=true`). FastAPI allows declaring both in the same endpoint function signature. FastAPI detects which parameters are path variables by inspecting the path string and treats all remaining scalar parameters as query variables, regardless of their position in the function argument list.",
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/users/{user_id}/orders/{order_id}')\ndef get_user_order(\n    user_id: int,\n    order_id: int,\n    format: str = 'summary',\n    include_items: bool = True\n):\n    return {\n        'user_id': user_id,\n        'order_id': order_id,\n        'format': format,\n        'include_items': include_items\n    }",
        "Extracting multiple path parameters alongside optional query parameters in a single route handler.",
        "During startup, FastAPI inspects the endpoint signature via `inspect.signature`. It compiles the route path to extract path parameter keys. During request dispatch, it extracts path values from Starlette's `scope['path_params']` and query values from Starlette's `request.query_params`, assembling them into the kwargs dictionary.",
        "Fetching specific sub-resources in multi-tenant SaaS platforms (e.g. `/organizations/{org_id}/projects/{project_id}?status=active`).",
        ["Does the order of arguments in the Python function signature matter to FastAPI?", "Can a parameter have the same name as both a path parameter and a query parameter?"],
        ["Placing non-default arguments after default arguments in Python signatures without using keyword-only markers `*`.", "Assuming query parameters must precede path parameters or vice versa."],
        "Remind the interviewer that FastAPI uses Python's standard argument semantics: name matching determines parameter origin, while type annotations determine validation.",
        ["[Path Parameters](routing-and-dependencies.md)", "[Query Parameters](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/query-params/"]
    ),

    # FA-BAS-030
    (
        "FA-BAS-030",
        "Introduction to Dependency Injection with Depends()",
        "FastAPI's `Depends()` function declares dependencies on reusable callables, enabling automated sharing of logic, database connections, security checks, and request parsing.",
        "Dependency Injection (DI) is a software design pattern where an object or function receives other services it depends on, rather than instantiating them internally. FastAPI provides a built-in DI system via `Depends()`. You declare a parameter with `Depends(dependency_callable)`. Before executing the route handler, FastAPI automatically invokes the dependency callable, passes any arguments it requires, and injects the return value into your route parameter. Dependencies can be standard functions, generator functions, or classes.",
        "from fastapi import FastAPI, Depends\n\napp = FastAPI()\n\ndef common_pagination(skip: int = 0, limit: int = 50):\n    return {'skip': skip, 'limit': limit}\n\n@app.get('/users')\ndef list_users(pagination: dict = Depends(common_pagination)):\n    return {'resource': 'users', 'pagination': pagination}\n\n@app.get('/items')\ndef list_items(pagination: dict = Depends(common_pagination)):\n    return {'resource': 'items', 'pagination': pagination}",
        "Sharing reusable pagination logic across multiple route handlers using Depends().",
        "FastAPI builds a dependency graph for each route at startup. When a request arrives, `fastapi.dependencies.utils.solve_dependencies` executes the dependency tree sequentially or concurrently, resolves sub-dependencies, and caches results within the request context.",
        "Extracting authentication tokens, sharing database session pools, enforcing permission scopes, and injecting configuration settings.",
        ["Can a dependency itself declare dependencies?", "What happens if two dependencies in the same route depend on the same sub-dependency?"],
        ["Calling the dependency manually inside `Depends(my_func())` instead of passing the callable `Depends(my_func)`.", "Thinking `Depends()` is only for database sessions (it can execute any Python callable)."],
        "Mention that `Depends()` implements Inversion of Control (IoC), drastically simplifying unit testing through dependency overrides.",
        ["[Sub-dependencies](routing-and-dependencies.md)", "[Dependency Caching](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/"]
    ),

    # FA-BAS-031
    (
        "FA-BAS-031",
        "Header() Parameter Extraction and Auto-Conversion",
        "`Header()` extracts HTTP request headers by parameter name, automatically converting kebab-case HTTP header names to snake_case Python variable names.",
        "HTTP header keys are case-insensitive and conventionally separated by hyphens (e.g. `User-Agent`, `X-Api-Key`, `Accept-Language`). However, hyphens are illegal characters in Python identifiers. FastAPI solves this by providing `Header()`. When you declare a parameter like `user_agent: str = Header()`, FastAPI automatically translates the underscore `_` to a hyphen `-` and performs a case-insensitive search in incoming HTTP headers. You can disable this conversion by passing `convert_underscores=False`.",
        "from typing import Optional\nfrom fastapi import FastAPI, Header\n\napp = FastAPI()\n\n@app.get('/info')\ndef get_client_info(\n    user_agent: Optional[str] = Header(default=None),\n    x_trace_id: str = Header(default='default-trace')\n):\n    # Maps automatically from 'User-Agent' and 'X-Trace-Id' headers\n    return {'User-Agent': user_agent, 'X-Trace-Id': x_trace_id}",
        "Reading HTTP headers with automatic underscore-to-hyphen conversion.",
        "FastAPI inspects Starlette's `scope['headers']` (a list of raw byte two-tuples) and maps matching header names to the declared parameters, decoding ASCII/UTF-8 values.",
        "Extracting distributed tracing correlation IDs (`X-Correlation-ID`), client agent metadata, and custom gateway routing flags.",
        ["How do you receive custom headers containing underscores without hyphen conversion?", "How can you extract a header that can appear multiple times in a single request?"],
        ["Naming a header parameter `x-token` (syntax error in Python function signatures).", "Assuming headers are case-sensitive in FastAPI."],
        "Note the convenience feature: `convert_underscores=True` by default converts `x_custom_header` into `X-Custom-Header` automatically.",
        ["[Cookie Parameters](routing-and-dependencies.md)", "[API Security](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/header-params/"]
    ),

    # FA-BAS-032
    (
        "FA-BAS-032",
        "Cookie() Parameter Extraction",
        "`Cookie()` declares and extracts browser cookie values directly into route parameters with type checking, default values, and validation.",
        "Browser clients transmit session identifiers, tracking tokens, and authentication cookies in the HTTP `Cookie` header as semicolon-separated key-value pairs. FastAPI provides the `Cookie()` parameter function to read specific cookies without manually parsing the raw header string. Just like `Query()` and `Header()`, `Cookie()` supports default values, optionality, and validation constraints.",
        "from typing import Optional\nfrom fastapi import FastAPI, Cookie\n\napp = FastAPI()\n\n@app.get('/session')\ndef read_session(session_id: Optional[str] = Cookie(default=None)):\n    if not session_id:\n        return {'status': 'anonymous', 'session_id': None}\n    return {'status': 'authenticated', 'session_id': session_id}",
        "Reading session cookies using Cookie() parameter injection.",
        "FastAPI parses Starlette's `request.cookies` dictionary (which decodes the raw `Cookie` header) and extracts the requested cookie key, passing it to Pydantic for validation.",
        "Validating session tokens in browser-based web applications, CSRF token validation, and reading UI theme preferences.",
        ["How do you set a cookie in the response from a FastAPI endpoint?", "What is the difference between `HttpOnly` cookies and regular cookies in security terms?"],
        ["Assuming `Cookie()` sets cookies (it only reads incoming cookies; setting requires `Response.set_cookie()`).", "Failing to mark session cookies as `Optional` when user authentication is optional."],
        "Differentiate clearly: `Cookie()` reads incoming cookies from the client; `response.set_cookie()` writes cookies to the client.",
        ["[Header Extraction](routing-and-dependencies.md)", "[Response Mutation](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/cookie-params/"]
    ),

    # FA-BAS-033
    (
        "FA-BAS-033",
        "Route Prefixing and Tags in APIRouter",
        "Configuring `prefix` and `tags` on an `APIRouter` groups related routes under a common URL path namespace and clusters them visually in OpenAPI Swagger UI.",
        "When designing structured REST APIs, endpoints are logically partitioned by entity (e.g. `/api/v1/orders`, `/api/v1/customers`). Instead of repeating `/api/v1/orders` on every route decorator, `APIRouter(prefix='/api/v1/orders', tags=['orders'])` defines the base path once. The `tags` parameter groups endpoints inside Swagger UI and ReDoc documentation under clear, collapsible category headers.",
        "from fastapi import FastAPI, APIRouter\n\norders_router = APIRouter(prefix='/orders', tags=['Orders'])\n\n@orders_router.get('/')\ndef list_orders():\n    return [{'order_id': 101, 'status': 'shipped'}]\n\n@orders_router.get('/{order_id}')\ndef get_order(order_id: int):\n    return {'order_id': order_id, 'status': 'shipped'}\n\napp = FastAPI()\napp.include_router(orders_router)",
        "Configuring router prefixes and Swagger UI documentation tags.",
        "FastAPI joins the router's prefix string to each route's path during registration. In OpenAPI schema generation, it aggregates tags across routers and endpoints into the OpenAPI `paths` and `tags` objects.",
        "Organizing enterprise APIs into self-contained micro-domains with clean API documentation for external SDK consumers.",
        ["What happens if both the router and the endpoint specify tags?", "Can router prefixes include path parameters, such as `/organizations/{org_id}`?"],
        ["Including trailing slashes in prefixes (e.g. `/orders/`) causing double slashes (`//101`) on child routes.", "Confusing tags with URL prefixes (tags affect only OpenAPI documentation grouping)."],
        "Point out that prefixes can be nested when including routers within routers, keeping URL schemas DRY (Don't Repeat Yourself).",
        ["[APIRouter Basics](routing-and-dependencies.md)", "[FastAPI Overview](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]
    ),

    # FA-BAS-034
    (
        "FA-BAS-034",
        "Response Status Codes and HTTP Status Constants",
        "FastAPI routes configure default HTTP response status codes via the `status_code` parameter in route decorators, using `fastapi.status` or `http.HTTPStatus` constants.",
        "RESTful services must communicate accurate HTTP semantics (e.g. 200 OK for reads, 201 Created for resource creation, 204 No Content for deletions). In FastAPI, the default status code for any endpoint is 200 OK. You can change this by supplying `status_code=status.HTTP_201_CREATED` to the route decorator. Using the `status` module avoids magic numbers, improves readability, and documents expected status codes in the OpenAPI schema.",
        "from fastapi import FastAPI, status\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass ItemCreate(BaseModel):\n    name: str\n    price: float\n\n@app.post('/items', status_code=status.HTTP_201_CREATED)\ndef create_item(item: ItemCreate):\n    return {'message': 'Item created successfully', 'data': item.model_dump()}\n\n@app.delete('/items/{item_id}', status_code=status.HTTP_204_NO_CONTENT)\ndef delete_item(item_id: int):\n    # 204 No Content must return an empty response body\n    return None",
        "Setting 201 Created and 204 No Content status codes using status constants.",
        "Starlette inspects the route's configured `status_code` attribute when serializing the final ASGI response message, setting the HTTP status line accordingly.",
        "Adhering to standard REST RFC conventions across CRUD microservice endpoints.",
        ["What should an endpoint return when configured with status code 204 No Content?", "How can you dynamically alter the status code from inside a route handler function?"],
        ["Hardcoding integer status codes like `status_code=201` instead of using `status.HTTP_201_CREATED`.", "Returning a JSON body when using `HTTP_204_NO_CONTENT` (violates HTTP RFC 7231)."],
        "Always recommend using `from fastapi import status` for self-documenting code and OpenAPI specification fidelity.",
        ["[Response Mutation](routing-and-dependencies.md)", "[HTTP Protocols](../07-api-engineering/rest-api.md)"],
        ["https://fastapi.tiangolo.com/tutorial/response-status-code/"]
    ),

    # FA-BAS-035
    (
        "FA-BAS-035",
        "Including Routers with app.include_router()",
        "`app.include_router()` registers an `APIRouter` instance into the application, optionally applying extra prefixes, tags, dependencies, and responses.",
        "`include_router()` is the primary mechanism to assemble a distributed FastAPI codebase. Beyond simple inclusion, it allows the parent application or parent router to override or augment settings. For example, `app.include_router(orders_router, prefix='/v1', dependencies=[Depends(verify_api_key)])` dynamically adds an extra path segment and mandates an API key check across every route inside `orders_router` without modifying the router's source file.",
        "from fastapi import FastAPI, APIRouter, Depends\n\ndef global_audit_check():\n    return True\n\nitems_router = APIRouter(prefix='/items', tags=['items'])\n\n@items_router.get('/')\ndef list_items():\n    return [{'id': 1, 'name': 'Widget'}]\n\napp = FastAPI()\n# Mounting router with additional prefix and top-level dependency\napp.include_router(items_router, prefix='/api/v1', dependencies=[Depends(global_audit_check)])",
        "Mounting a sub-router with additional versioning prefixes and security dependencies.",
        "FastAPI iterates over the routes registered in the router, prepends the new prefix, appends additional tags and dependencies to each route's definition, and registers them into the application's ASGI route table.",
        "Implementing API versioning (e.g. `/api/v1` and `/api/v2`) pointing to different router modules while sharing common core logic.",
        ["Can you include the same APIRouter multiple times with different prefixes?", "What is the order of execution between router dependencies and included router dependencies?"],
        ["Registering routes on the router AFTER `app.include_router()` has already been called.", "Forgetting that `include_router` copies routes at invocation time."],
        "Emphasize that `include_router()` is composable: you can build trees of routers mounted into routers, culminating in the root application.",
        ["[APIRouter Basics](routing-and-dependencies.md)", "[Global Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]
    ),

    # FA-BAS-036
    (
        "FA-BAS-036",
        "Sub-dependencies: Dependencies that Depend on Other Dependencies",
        "FastAPI supports hierarchical sub-dependencies where a dependency function can itself declare parameters with `Depends()`, creating a resolved dependency tree.",
        "In non-trivial applications, dependencies often require other services. For example, a `get_current_active_user` dependency requires `get_current_user`, which in turn requires `get_db_session` and `get_token`. FastAPI natively supports sub-dependencies to arbitrary depth. You simply declare `Depends()` in the parameters of a dependency function. FastAPI resolves all dependencies recursively before calling the main route handler.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\ndef get_token_header(x_token: str = 'secret-token'):\n    if x_token != 'secret-token':\n        raise HTTPException(status_code=400, detail='Invalid X-Token header')\n    return x_token\n\ndef get_current_user(token: str = Depends(get_token_header)):\n    # Sub-dependency: get_current_user depends on get_token_header\n    return {'username': 'admin', 'token': token}\n\n@app.get('/admin')\ndef admin_dashboard(user: dict = Depends(get_current_user)):\n    return {'message': f'Welcome {user[\"username\"]}'}",
        "Demonstrating hierarchical sub-dependencies resolving an auth token into a user object.",
        "FastAPI constructs a Directed Acyclic Graph (DAG) of dependencies during startup. At runtime, it traverses the graph from leaf nodes to root nodes, executing sub-dependencies and caching results per request.",
        "Layered authentication architectures where raw headers -> validated tokens -> database user records -> role-based permission checks.",
        ["What happens if circular dependencies exist between two dependency functions?", "How does dependency caching behave across a deep sub-dependency tree?"],
        ["Manually invoking sub-dependencies inside the function body instead of declaring them via `Depends()`.", "Deeply nesting dependencies beyond 5-6 levels leading to hard-to-debug stack traces."],
        "Explain that sub-dependencies allow writing small, single-responsibility functions that compose cleanly into sophisticated pipelines.",
        ["[Dependency Injection Basics](routing-and-dependencies.md)", "[Dependency Caching](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/"]
    ),

    # FA-BAS-037
    (
        "FA-BAS-037",
        "Query Parameter Validation with Query()",
        "`Query()` provides explicit metadata, length constraints, regex pattern enforcement, and deprecation flags for query parameters.",
        "While type hints (e.g. `q: str`) provide basic type coercion, production APIs often require string length limits, numerical boundaries, or regex pattern constraints. FastAPI's `Query()` parameter function exposes validation keywords such as `min_length`, `max_length`, `pattern` (or `regex` in Pydantic v1), `title`, `description`, and `deprecated`. Violations automatically trigger standard 422 validation errors with clear error messages.",
        "from typing import Optional\nfrom fastapi import FastAPI, Query\n\napp = FastAPI()\n\n@app.get('/search')\ndef search_items(\n    q: Optional[str] = Query(\n        default=None,\n        min_length=3,\n        max_length=50,\n        pattern='^[a-zA-Z0-9_-]+$',\n        title='Search Query',\n        description='Search keyword containing only alphanumeric characters'\n    )\n):\n    return {'query': q}",
        "Enforcing min_length, max_length, and regex pattern constraints on query parameters with Query().",
        "Under the hood, `Query()` creates a `FieldInfo` instance recognized by FastAPI's parameter analysis. When requests arrive, Pydantic's string validator tests the string against the configured constraints before calling the handler.",
        "Preventing ReDoS (Regular Expression Denial of Service) and SQL wildcard abuse by constraining search query lengths and characters.",
        ["How do you make a query parameter mandatory when using `Query()`?", "What is the difference between `Query(...)` (Ellipsis) and omitting the default in Python 3.10+?"],
        ["Using `regex=` instead of `pattern=` in modern Pydantic v2 codebases.", "Setting `min_length` without considering empty string query parameters like `?q=`."],
        "In Pydantic v2 / modern FastAPI, use `pattern=` instead of the deprecated `regex=` parameter.",
        ["[Query Parameters](routing-and-dependencies.md)", "[Path Validation](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/query-params-str-validations/"]
    ),

    # FA-BAS-038
    (
        "FA-BAS-038",
        "Path Parameter Validation with Path()",
        "`Path()` declares numeric constraints, string patterns, and documentation metadata specifically for URL path parameters.",
        "Just as `Query()` validates query parameters, `Path()` enforces constraints on path parameters. Because path parameters are embedded in the URL, they are always required (using a default value in `Path()` is a syntax contradiction). `Path()` allows specifying numerical boundaries such as `gt` (greater than), `ge` (greater than or equal to), `lt` (less than), `le` (less than or equal to), as well as string patterns and descriptive OpenAPI metadata.",
        "from fastapi import FastAPI, Path\n\napp = FastAPI()\n\n@app.get('/items/{item_id}')\ndef get_item(\n    item_id: int = Path(\n        ...,\n        title='Item Identifier',\n        description='The numeric primary key of the item',\n        ge=1,\n        le=1000000\n    )\n):\n    return {'item_id': item_id}",
        "Enforcing numerical boundaries (1 <= item_id <= 1000000) on a path parameter using Path().",
        "FastAPI maps the matched path string to `Path()` specifications, and Pydantic evaluates numeric comparison constraints. If a client requests `/items/0`, a 422 response is returned stating that the value must be greater than or equal to 1.",
        "Sanitizing database primary key identifiers to prevent integer overflow or negative IDs from querying the database layer.",
        ["Can a path parameter have a default value such as `item_id: int = Path(default=1)`?", "How does `Path()` differ from `Field()` in Pydantic models?"],
        ["Attempting to make a path parameter optional with `None` default (path parameters are inherently mandatory).", "Using `gt` and `lt` on non-numeric types like strings without specifying `pattern` or `min_length`."],
        "Emphasize that `Path()` parameters are always mandatory; the first argument is either `...` (Ellipsis) or omitted in modern typing.",
        ["[Path Parameters](routing-and-dependencies.md)", "[Query Validation](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/"]
    ),

    # FA-BAS-039
    (
        "FA-BAS-039",
        "Dependency Caching Behavior with use_cache=True",
        "By default (`use_cache=True`), FastAPI executes a dependency callable only once per incoming HTTP request and reuses its return value across all sub-dependencies in that same request.",
        "When an endpoint and its sub-dependencies depend on the same callable (for example, `get_db` or `get_current_user`), executing that function multiple times per request would cause duplicate database queries and performance degradation. To solve this, FastAPI's `Depends()` has a `use_cache=True` parameter by default. FastAPI memoizes the dependency's return value within the request context. If you need a dependency to execute afresh every single time it is called within the same request (e.g. generating a unique request step timestamp), you set `Depends(my_dep, use_cache=False)`.",
        "from fastapi import FastAPI, Depends\nimport time\n\napp = FastAPI()\n\ndef get_timestamp():\n    return time.time()\n\n@app.get('/cached')\ndef cached_endpoint(\n    t1: float = Depends(get_timestamp, use_cache=True),\n    t2: float = Depends(get_timestamp, use_cache=True)\n):\n    # t1 and t2 will be strictly identical (cached per request)\n    return {'t1': t1, 't2': t2, 'identical': t1 == t2}\n\n@app.get('/uncached')\ndef uncached_endpoint(\n    t1: float = Depends(get_timestamp, use_cache=False),\n    t2: float = Depends(get_timestamp, use_cache=False)\n):\n    # t1 and t2 can differ as get_timestamp is invoked twice\n    return {'t1': t1, 't2': t2, 'identical': t1 == t2}",
        "Demonstrating memoization with use_cache=True vs re-execution with use_cache=False.",
        "During request dependency resolution, FastAPI maintains an internal `async_exit_stack` and an `in_threadpool` dependency cache dictionary keyed by the dependency callable and its sub-signature. If the key exists and `use_cache=True`, the cached result is returned immediately.",
        "Preventing duplicate database queries when five different sub-dependencies require access to the authenticated `User` record.",
        ["Does `use_cache=True` cache values across different requests or different users?", "What happens to generator dependencies when `use_cache=True` is active?"],
        ["Believing `use_cache=True` is a global cache across multiple HTTP requests (it is strictly scoped to the lifecycle of a single request).", "Setting `use_cache=False` on database session dependencies, causing multiple uncoordinated transactions."],
        "Crucial interview point: Dependency caching is request-scoped, not application-scoped. It prevents duplicate work within one request.",
        ["[Dependency Injection Basics](routing-and-dependencies.md)", "[Sub-dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/"]
    ),

    # FA-BAS-040
    (
        "FA-BAS-040",
        "Class-Based Dependencies (__call__ vs __init__)",
        "Classes can serve as FastAPI dependencies, using `__init__` for parameterized instantiation or `__call__` for callable instances.",
        "Functions are not the only callables supported by `Depends()`. Python classes can be used as dependencies in two powerful ways: 1) Passing the class directly: `Depends(MyClass)` invokes `MyClass.__init__` with request parameters, returning an instance. 2) Using a callable instance: Creating an instance of a class that implements `__call__`, allowing configuration state to be passed during startup (like required permission roles) while request parameters are evaluated during `__call__`.",
        "from fastapi import FastAPI, Depends\n\napp = FastAPI()\n\n# Pattern 1: Class as dependency\nclass PaginationParams:\n    def __init__(self, skip: int = 0, limit: int = 100):\n        self.skip = skip\n        self.limit = limit\n\n# Pattern 2: Callable class instance for role checks\nclass RoleChecker:\n    def __init__(self, allowed_role: str):\n        self.allowed_role = allowed_role\n\n    def __call__(self, user_role: str = 'admin'):\n        return user_role == self.allowed_role\n\nrequire_admin = RoleChecker(allowed_role='admin')\n\n@app.get('/items')\ndef get_items(\n    pagination: PaginationParams = Depends(PaginationParams),\n    is_admin: bool = Depends(require_admin)\n):\n    return {'skip': pagination.skip, 'limit': pagination.limit, 'is_admin': is_admin}",
        "Using class constructors and callable instances as structured dependencies.",
        "FastAPI uses Python's `callable()` check. If a class is passed, it inspects `__init__` parameters. If an instance is passed, it inspects `__call__` parameters, extracting request parameters just like standard functions.",
        "Implementing reusable permission checkers, rate limiters, or parameter containers across enterprise codebases.",
        ["What is the advantage of using a class over a plain function for dependencies?", "How does `use_cache=True` handle callable class instances?"],
        ["Storing mutable request-specific state on `self` in a long-lived callable instance, causing race conditions across concurrent requests.", "Passing uninstantiated classes when configuration arguments were expected."],
        "Highlight that callable classes allow passing configuration at app startup (e.g. `RoleChecker('manager')`) while resolving request data at runtime.",
        ["[Dependency Injection Basics](routing-and-dependencies.md)", "[Yield Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/"]
    ),

    # FA-BAS-041
    (
        "FA-BAS-041",
        "Yield Dependencies for Resource Cleanup",
        "Dependencies that use the `yield` keyword execute setup logic before the route handler and guaranteed teardown logic after the response is sent.",
        "Many dependencies require resource management: opening a database session, acquiring a lock, or streaming a file, followed by closing or committing after the request is finished. In FastAPI, defining a generator dependency using `yield` provides built-in context management. Code before the `yield` executes before the route handler, the yielded value is injected into the route, and code after the `yield` executes after the response is generated, even if exceptions occurred.",
        "from fastapi import FastAPI, Depends\n\napp = FastAPI()\n\ndef get_db():\n    db_connection = {'status': 'connected', 'id': 101}\n    print('-> DB session opened')\n    try:\n        yield db_connection\n    finally:\n        print('<- DB session closed and returned to pool')\n\n@app.get('/data')\ndef read_data(db: dict = Depends(get_db)):\n    return {'db_id': db['id'], 'data': 'sample_records'}",
        "Managing database connection acquisition and guaranteed cleanup with yield dependencies.",
        "FastAPI wraps yield dependencies inside an internal `contextlib.AsyncExitStack`. When the response finishes transmitting or if an unhandled exception occurs, the exit stack unwinds and resumes execution after the `yield` statement.",
        "Managing SQLAlchemy database sessions (`SessionLocal`), Redis connection checkouts, and transactional rollback on route errors.",
        ["What happens if an unhandled exception occurs inside the route handler?", "Can a yield dependency catch exceptions raised by the route handler?"],
        ["Writing code after `yield` without a `finally` block, risking resource leaks if exceptions occur.", "Yielding more than once inside a generator dependency (causes a runtime error)."],
        "Always emphasize: code before `yield` = setup; `yield` = injection; code after `yield` = teardown/cleanup.",
        ["[Dependency Injection Basics](routing-and-dependencies.md)", "[Database Integration](database-integration.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/"]
    ),

    # FA-BAS-042
    (
        "FA-BAS-042",
        "Global Dependencies on FastAPI Applications",
        "Global dependencies declared on `FastAPI(dependencies=[Depends(...)])` execute on every single incoming HTTP request across the entire application.",
        "Certain cross-cutting concerns must apply universally without relying on individual developers remembering to add `Depends()` to every route. Examples include enterprise API key validation, security header enforcement, maintenance mode checks, and rate limiting. FastAPI allows declaring a list of dependencies at application instantiation: `app = FastAPI(dependencies=[Depends(my_global_guard)])`. These dependencies execute for every registered route, and their return values do not need to be captured in route parameters.",
        "from fastapi import FastAPI, Depends, HTTPException, Header\n\ndef verify_api_key(x_api_key: str = Header(...)):\n    if x_api_key != 'master-secret-key':\n        raise HTTPException(status_code=403, detail='Forbidden: Invalid Global API Key')\n\n# Apply verify_api_key to every route in the application\napp = FastAPI(dependencies=[Depends(verify_api_key)])\n\n@app.get('/users')\ndef get_users():\n    return [{'id': 1, 'name': 'Alice'}]\n\n@app.get('/health')\ndef health():\n    return {'status': 'healthy'}",
        "Enforcing an application-wide API key requirement using global dependencies.",
        "FastAPI appends the global dependencies list to the dependency tree of every route registered in the application, executing them before any route-specific or router-specific dependencies.",
        "Enforcing zero-trust API authentication across internal microservices, or blocking all requests during scheduled database maintenance.",
        ["How do global dependencies differ from HTTP middleware?", "Can a specific route be exempted from a global dependency?"],
        ["Using global dependencies for logic that should exempt public endpoints like `/health` or `/docs` (use router dependencies instead).", "Expecting global dependency return values to be automatically injected into route parameters."],
        "Architectural distinction: Middleware operates on raw ASGI scopes; global dependencies have full access to FastAPI's parameter parsing and DI engine.",
        ["[Router-level Dependencies](routing-and-dependencies.md)", "[Middleware](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/"]
    ),

    # FA-BAS-043
    (
        "FA-BAS-043",
        "Router-Level Dependencies on APIRouter",
        "Configuring `dependencies=[Depends(...)]` on an `APIRouter` enforces dependencies across all endpoints mounted on that specific router.",
        "While global dependencies apply to the entire app and path dependencies apply to single routes, router-level dependencies provide the ideal middle ground: scoping security and validation to a cohesive domain. For example, an `/admin` router can enforce admin authentication across all 20 admin endpoints, while leaving `/public` routes accessible to unauthenticated users. This eliminates repetitive dependency declarations.",
        "from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header\n\ndef verify_admin_role(x_role: str = Header(default='user')):\n    if x_role != 'admin':\n        raise HTTPException(status_code=403, detail='Admin role required')\n\nadmin_router = APIRouter(prefix='/admin', dependencies=[Depends(verify_admin_role)])\n\n@admin_router.get('/metrics')\ndef get_metrics():\n    return {'cpu': '12%', 'memory': '45%'}\n\n@admin_router.post('/restart')\ndef restart_service():\n    return {'status': 'restarting'}\n\napp = FastAPI()\napp.include_router(admin_router)",
        "Enforcing role verification across all endpoints in an admin APIRouter.",
        "FastAPI prepends the router's dependency list to the dependency graph of each route belonging to that router during `include_router` registration.",
        "Securing admin panels, partner API sub-domains, and multi-tenant department routes with distinct access policies.",
        ["What is the order of execution between global, router, and endpoint dependencies?", "Can an included router inherit dependencies from the parent router?"],
        ["Assuming router dependencies pass their return values into route arguments (they execute for side-effects and validation only).", "Declaring authentication dependencies on public routers accidentally."],
        "Emphasize that router dependencies execute for side effects (validation, authentication, logging) rather than parameter value injection.",
        ["[Global Dependencies](routing-and-dependencies.md)", "[Path-Level Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]
    ),

    # FA-BAS-044
    (
        "FA-BAS-044",
        "Path-Level Dependencies on Route Decorators",
        "Declaring `dependencies=[Depends(...)]` inside route decorators runs dependencies for side effects or validation without binding their return values to function arguments.",
        "Often, an endpoint needs to execute an authentication check, rate limit, or request validation, but the route function itself has no need for the resulting data object. Instead of adding an unused argument to the function signature (e.g. `_auth: None = Depends(verify)`), FastAPI allows passing `dependencies=[Depends(...)]` directly inside the route decorator `@app.get('/route', dependencies=[...])`.",
        "from fastapi import FastAPI, Depends, HTTPException, Header\n\napp = FastAPI()\n\ndef verify_csrf_token(x_csrf: str = Header(default='')):\n    if x_csrf != 'valid-csrf-secret':\n        raise HTTPException(status_code=400, detail='Invalid CSRF token')\n\n# Endpoint executes verify_csrf_token without needing the token value in the handler\n@app.post('/transfer', dependencies=[Depends(verify_csrf_token)])\ndef transfer_funds():\n    return {'status': 'transfer completed'}",
        "Using path-level dependencies on a route decorator for CSRF protection.",
        "FastAPI includes the dependency in the route's execution graph. If the dependency raises an `HTTPException`, request processing halts immediately and returns an error response.",
        "Enforcing CSRF tokens on write operations, checking feature flags before executing beta endpoints, and triggering audit logs.",
        ["How do you capture the return value of a dependency declared in the `dependencies` decorator list?", "Can you combine decorator dependencies with signature dependencies?"],
        ["Attempting to access return values from decorator dependencies in the route function (decorator dependencies do not inject values).", "Using decorator dependencies when the route handler actually needs the user or database session object."],
        "Rule of thumb: If the route handler needs the returned object, use parameter `Depends()`. If the route only needs the check to pass, use decorator `dependencies=[...]`.",
        ["[Router-level Dependencies](routing-and-dependencies.md)", "[Global Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/"]
    ),

    # FA-BAS-045
    (
        "FA-BAS-045",
        "Direct Request Object Injection in Route Handlers",
        "Declaring a parameter of type `Request` injects Starlette's raw request instance, providing direct access to the ASGI scope, client IP, raw headers, and state.",
        "While FastAPI's high-level parameter extractors (`Query`, `Path`, `Body`, `Header`) handle most needs, certain operations require direct access to the raw underlying HTTP request. Declaring `request: Request` from `starlette.requests` or `fastapi` instructs FastAPI to inject the current request object without attempting to parse it as a body or query parameter. Through `request`, you can access `request.client.host`, `request.headers`, `request.scope`, `request.cookies`, and `request.state`.",
        "from fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.get('/client-info')\ndef get_client_info(request: Request):\n    return {\n        'client_ip': request.client.host if request.client else 'unknown',\n        'method': request.method,\n        'url': str(request.url),\n        'headers_count': len(request.headers)\n    }",
        "Accessing raw HTTP request attributes including client IP and URL using Request injection.",
        "FastAPI checks if any parameter is annotated with `Request`. If so, it passes the existing Starlette `Request(scope, receive, send)` instance directly from the ASGI context.",
        "Extracting client IP addresses for geolocation, reading custom state set by middleware (`request.state`), and inspecting raw request URLs.",
        ["What is the performance implication of reading `await request.body()` manually?", "How does `Request` injection interact with Pydantic body validation?"],
        ["Annotating a parameter as `request: Request` but forgetting to import `Request` from `fastapi` or `starlette.requests`.", "Reading `request.stream()` after another dependency or Pydantic has already consumed the request body stream."],
        "Emphasize that `Request` is Starlette's core HTTP connection abstraction, exposing low-level socket and connection metadata.",
        ["[Response Object Injection](routing-and-dependencies.md)", "[Middleware](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/advanced/using-request-directly/"]
    ),

    # FA-BAS-046
    (
        "FA-BAS-046",
        "Direct Response Object Injection for Mutating Headers and Cookies",
        "Declaring a parameter of type `Response` allows route handlers to set custom HTTP response headers, status codes, and cookies dynamically on the outgoing response.",
        "In many scenarios, an endpoint returns standard serializable data (like a Pydantic model or dict) but also needs to set a custom header (e.g. `X-Process-Time`) or an HTTP-only cookie. Rather than manually constructing a `JSONResponse` and losing automatic Pydantic serialization, you can declare `response: Response` in your function arguments. FastAPI passes in the response template, allowing you to set headers and cookies while returning regular data.",
        "from fastapi import FastAPI, Response\n\napp = FastAPI()\n\n@app.post('/login')\ndef login(response: Response):\n    # Set an HTTP-Only secure cookie on the outgoing response\n    response.set_cookie(\n        key='session_token',\n        value='xyz_token_secret',\n        httponly=True,\n        secure=True,\n        samesite='lax'\n    )\n    # Set a custom response header\n    response.headers['X-Server-ID'] = 'node-04'\n    return {'message': 'Logged in successfully'}",
        "Setting cookies and custom headers on the injected Response object while returning a normal dict.",
        "FastAPI creates a `Response` instance and injects it into the handler. When the handler returns, FastAPI merges any headers and cookies set on this object into the final ASGI response message.",
        "Issuing authentication session cookies, returning pagination headers (`X-Total-Count`, `Link`), and setting cache-control directives.",
        ["Can you change `response.status_code` dynamically using the injected `Response` object?", "What happens if you return a new `Response` object while also modifying the injected `response` parameter?"],
        ["Attempting to set cookies on the request object instead of the response object.", "Overwriting the entire `response.headers` dictionary instead of assigning individual keys."],
        "Highlight the elegance: Injected `Response` allows setting cookies and headers without losing automatic model serialization or OpenAPI schema generation.",
        ["[Cookie Extraction](routing-and-dependencies.md)", "[Request Object Injection](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/advanced/response-cookies/"]
    ),

    # FA-BAS-047
    (
        "FA-BAS-047",
        "Deprecating Routes and Parameters in OpenAPI",
        "Setting `deprecated=True` on route decorators or parameter definitions flags them as deprecated in OpenAPI specifications and Swagger UI documentation.",
        "As APIs evolve, endpoints and specific query parameters are phased out in favor of newer versions. Removing them immediately breaks backwards compatibility for existing clients. FastAPI enables marking endpoints as deprecated by passing `deprecated=True` in the path operation decorator, or marking individual parameters with `Query(deprecated=True)`. In Swagger UI, deprecated routes are visually struck through, alerting developers to migrate.",
        "from typing import Optional\nfrom fastapi import FastAPI, Query\n\napp = FastAPI()\n\n# Entire route marked as deprecated\n@app.get('/api/v1/legacy-users', deprecated=True)\ndef get_legacy_users():\n    return [{'id': 1, 'name': 'Legacy User'}]\n\n# Specific parameter marked as deprecated\n@app.get('/api/v2/users')\ndef get_users(\n    old_filter: Optional[str] = Query(default=None, deprecated=True),\n    status: str = 'active'\n):\n    return {'status': status, 'old_filter_used': old_filter is not None}",
        "Marking an entire endpoint and an individual query parameter as deprecated.",
        "FastAPI sets the `deprecated: true` boolean field in the generated OpenAPI 3.1 JSON document under the corresponding operation or parameter object.",
        "Managing graceful API version deprecation cycles across enterprise mobile and web client releases.",
        ["Does setting `deprecated=True` prevent clients from calling the endpoint?", "How can you programmatically log warnings when clients access deprecated endpoints?"],
        ["Assuming `deprecated=True` disables the route (it is strictly metadata for documentation and client SDKs).", "Forgetting to provide an alternative route or sunset date in the endpoint description."],
        "Emphasize that API deprecation in FastAPI is clear communication: it signals upcoming sunsets in documentation without breaking existing integrations.",
        ["[APIRouter Basics](routing-and-dependencies.md)", "[FastAPI Overview](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/path-operation-configuration/#deprecate-a-path-operation"]
    ),

    # FA-BAS-048
    (
        "FA-BAS-048",
        "Enums as Path Parameters for Strict Choice Validation",
        "Using Python `enum.Enum` classes as path parameter type hints restricts valid URL path segments to a predefined set of choices with automatic Swagger UI dropdowns.",
        "When an API endpoint only supports a fixed set of options (such as model names, sorting orders, or payment providers), accepting free-form strings requires manual `if/else` validation. By defining a Python `str, Enum` class and using it as a path parameter type annotation, FastAPI enforces that only predefined enum values are accepted. In Swagger UI, this automatically renders an interactive dropdown selector.",
        "from enum import Enum\nfrom fastapi import FastAPI\n\nclass Environment(str, Enum):\n    DEVELOPMENT = 'development'\n    STAGING = 'staging'\n    PRODUCTION = 'production'\n\napp = FastAPI()\n\n@app.get('/deployments/{env}')\ndef get_deployment(env: Environment):\n    # env is an instance of Environment enum\n    if env == Environment.PRODUCTION:\n        return {'env': env.value, 'replicas': 10}\n    return {'env': env.value, 'replicas': 2}",
        "Restricting path parameter values to a strict set of choices using str Enum.",
        "FastAPI passes the string path segment to the Enum constructor. If the value does not match any enum member, Pydantic raises a validation error listing all allowed values.",
        "Constraining environment selectors, status filters (`active`, `pending`, `archived`), and supported currency codes.",
        ["Why must the Enum inherit from both `str` and `Enum`?", "What error status code is returned if an invalid enum value is passed?"],
        ["Creating an Enum without inheriting from `str` (`class Env(Enum):`), preventing proper OpenAPI string documentation.", "Comparing enum instances using string literals instead of enum members or `.value`."],
        "Best practice: Always inherit from `str, Enum` (`class ModelName(str, Enum):`) so FastAPI renders it as a string enum in OpenAPI.",
        ["[Path Parameters](routing-and-dependencies.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/path-params/#predefined-values"]
    ),

    # FA-BAS-049
    (
        "FA-BAS-049",
        "Handling Query Parameter Lists and Multiple Values",
        "Declaring query parameters as `list[str] = Query(default=[])` allows clients to supply multiple values for the same query parameter key in the URL.",
        "Standard HTTP allows repeating query parameter keys to transmit lists of items (e.g. `?tags=python&tags=fastapi&tags=docker`). In FastAPI, typing a parameter as `list[str]` or `List[int]` using `Query()` tells FastAPI to collect all occurrences into a Python list. If a client passes only a single occurrence (`?tags=python`), FastAPI automatically wraps it in a single-element list.",
        "from typing import List\nfrom fastapi import FastAPI, Query\n\napp = FastAPI()\n\n@app.get('/articles')\ndef filter_articles(\n    tags: List[str] = Query(default=['python', 'backend']),\n    ids: List[int] = Query(default=[])\n):\n    return {'selected_tags': tags, 'selected_ids': ids}",
        "Accepting multiple query values using list typing with Query().",
        "FastAPI accesses Starlette's `request.query_params.getlist(key)`, which retrieves all values associated with the query key and feeds the list to Pydantic for element-by-element type validation.",
        "Multi-select filtering on e-commerce categories, multi-tag search engines, and bulk resource deletion endpoints.",
        ["How does FastAPI handle query lists formatted as comma-separated values like `?tags=python,fastapi`?", "What happens if a non-integer is passed inside `ids: List[int]`?"],
        ["Typing as `tags: list` without element type annotations (`List[str]`), losing element validation.", "Forgetting `Query()` when declaring list parameters (FastAPI might expect a JSON body instead)."],
        "Tip: Always use `= Query(...)` when expecting list query parameters; otherwise FastAPI might treat it as a JSON request body.",
        ["[Query Parameters](routing-and-dependencies.md)", "[Query Validation](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#query-parameter-list-multiple-values"]
    ),

    # FA-BAS-050
    (
        "FA-BAS-050",
        "Route Order Precedence and Matching in Starlette/FastAPI",
        "FastAPI evaluates routes sequentially in the exact order they are registered, meaning static routes must be defined before parameterized dynamic routes to avoid accidental path capture.",
        "Because HTTP routers evaluate URL patterns in registration order, a route like `/users/{user_id}` will match the path `/users/me` and interpret `'me'` as a `user_id` parameter. If `/users/me` is defined AFTER `/users/{user_id}`, the dynamic route intercepts the request, attempting to cast `'me'` to an integer and failing with a 422 error. To ensure correct routing, static fixed endpoints must always be declared before dynamic parameterized routes.",
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n# 1. Fixed static path MUST come first\n@app.get('/users/me')\ndef get_current_user_profile():\n    return {'user_id': 0, 'username': 'current_authenticated_user'}\n\n# 2. Dynamic parameterized path MUST come second\n@app.get('/users/{user_id}')\ndef get_user_by_id(user_id: int):\n    return {'user_id': user_id, 'username': f'user_{user_id}'}",
        "Defining static path operations before dynamic path operations to ensure correct route precedence.",
        "Starlette maintains an ordered list of `Route` instances. When dispatching requests, Starlette iterates from first to last, executing the first route whose regex pattern matches the request path.",
        "Designing RESTful user endpoints where `/users/me`, `/users/export`, and `/users/stats` coexist with `/users/{user_id}`.",
        ["What error occurs if `/users/me` is requested when `/users/{user_id: int}` is registered first?", "How does Starlette's radix tree router handle route ordering in ASGI?"],
        ["Placing `/users/{user_id}` above `/users/me`, causing `/users/me` to fail with a 422 Unprocessable Entity error.", "Assuming modern frameworks automatically prioritize static routes over parameterized routes (Starlette is strictly sequential)."],
        "Golden rule: Always declare specific, static routes before general, parameterized routes in FastAPI.",
        ["[Path Parameters](routing-and-dependencies.md)", "[APIRouter Basics](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/path-params/#order-matters"]
    ),
]
