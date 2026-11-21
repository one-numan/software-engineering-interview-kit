"""
fa_mid_basic.py
===============
Basic FastAPI Middleware & Exception Handling Questions: FA-BAS-151 to FA-BAS-175 (25 questions)
"""

basic_data = [
    # FA-BAS-151
    (
        "FA-BAS-151",
        "What is Middleware in FastAPI and How Request/Response Processing Works",
        "Middleware in FastAPI is software that wraps the application to intercept, inspect, and modify every incoming HTTP request and outgoing HTTP response.",
        "Middleware acts as a bidirectional filter surrounding FastAPI endpoints. When a client sends an HTTP request: 1) The request first traverses through the middleware stack from outermost to innermost; 2) The middleware can inspect headers, log metadata, authenticate tokens, or reject the request before it reaches any route handler; 3) The route handler executes business logic and returns a response; 4) The response flows backward through the middleware stack from innermost to outermost, allowing middleware to add security headers, compress bodies, or log latency before returning bytes to the client.",
        "import time\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def add_process_time_header(request: Request, call_next):\n    start_time = time.perf_counter()\n    # Forward request down the stack to the route handler\n    response = await call_next(request)\n    # Modify the outgoing response before sending to client\n    process_time = time.perf_counter() - start_time\n    response.headers['X-Process-Time'] = f'{process_time:.6f}'\n    return response\n\n@app.get('/ping')\nasync def ping():\n    return {'status': 'pong'}",
        "Demonstrating request interception, execution timing, and response header modification via HTTP middleware.",
        "FastAPI middleware wraps Starlette's ASGI pipeline. Incoming requests pass through an onion-like stack of callables. `call_next(request)` is an awaitable that yields execution to the next layer in the chain, returning the downstream `Response` object.",
        "Adding global execution timers, injecting correlation IDs for distributed tracing, and enforcing cross-cutting security headers.",
        ["In what order do multiple middleware execute on requests vs responses?", "What happens if a middleware does not return the response returned by `call_next`?"],
        ["Performing heavy synchronous CPU computation inside `async def` middleware, blocking the event loop for all requests.", "Assuming middleware only runs on successful requests (it also wraps exception handlers)."],
        "Describe middleware using the 'onion layer' analogy: requests travel inward to the core; responses travel outward to the client.",
        ["[ASGI vs WSGI](fundamentals.md)", "[Execution Order](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/middleware/"]
    ),

    # FA-BAS-152
    (
        "FA-BAS-152",
        "Adding Middleware with `@app.middleware('http')`",
        "The `@app.middleware('http')` decorator provides a convenient syntax for declaring custom HTTP middleware functions that receive `request` and `call_next`.",
        "FastAPI provides the `@app.middleware('http')` decorator to quickly wrap route execution without writing raw ASGI classes. The decorated function must accept two parameters: `request` (a Starlette `Request` instance) and `call_next` (an asynchronous function that delegates to the remainder of the ASGI pipeline). The middleware function must await `call_next(request)` and return a `Response` object.",
        "from fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def custom_header_middleware(request: Request, call_next) -> Response:\n    # Pre-processing: inspect or validate request\n    user_agent = request.headers.get('user-agent', 'unknown')\n    \n    response: Response = await call_next(request)\n    \n    # Post-processing: set custom security headers\n    response.headers['X-Server-Version'] = '1.0.0'\n    response.headers['X-Client-Agent'] = user_agent\n    return response\n\n@app.get('/')\nasync def home():\n    return {'message': 'Hello World'}",
        "Defining an HTTP middleware using the @app.middleware('http') decorator.",
        "Under the hood, `@app.middleware('http')` wraps the function in Starlette's `BaseHTTPMiddleware` class and inserts it into `app.user_middleware`. When requests arrive, Starlette manages the coroutine task context and pipes the request stream to `call_next`.",
        "Lightweight request logging, injecting audit headers, and simple request/response inspection.",
        ["What class does `@app.middleware('http')` use internally in Starlette?", "Why can `BaseHTTPMiddleware` cause performance overhead on streaming responses?"],
        ["Forgetting `await` on `call_next(request)`, which produces an unawaited coroutine error.", "Modifying the request body stream without resetting it, causing downstream route handlers to receive empty bodies."],
        "Remember: `@app.middleware('http')` is great for simple tasks, but high-throughput streaming endpoints should use pure ASGI middleware.",
        ["[Pure ASGI Middleware](middleware-and-exception-handling.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/middleware/#create-a-middleware"]
    ),

    # FA-BAS-153
    (
        "FA-BAS-153",
        "The `call_next` Function and Asynchronous Request Forwarding",
        "`call_next` is an asynchronous callable passed to HTTP middleware that invokes the next middleware or route handler and returns the generated `Response`.",
        "In FastAPI's HTTP middleware model, `call_next` represents the continuation of the HTTP pipeline. When a middleware invokes `response = await call_next(request)`, Starlette passes the request down to subsequent middleware layers until reaching the matched APIRouter endpoint. Once the endpoint finishes executing, the resulting `Response` is passed back up through `call_next` so outer middleware can inspect or alter it before it is dispatched to the client.",
        "from fastapi import FastAPI, Request, Response\nimport logging\n\nlogger = logging.getLogger('api')\napp = FastAPI()\n\n@app.middleware('http')\nasync def logging_middleware(request: Request, call_next):\n    logger.info(f'Incoming request: {request.method} {request.url.path}')\n    \n    # Delegate to next middleware or route handler\n    response: Response = await call_next(request)\n    \n    logger.info(f'Outgoing response: status {response.status_code}')\n    return response",
        "Logging request entry and response status by wrapping call_next.",
        "`call_next` internally runs the downstream ASGI app inside an AnyIO task group. It translates the incoming ASGI `http.request` events into the `Request` object and intercepts the downstream `http.response.start` and `http.response.body` events to construct the returned `Response`.",
        "Structured access logging, distributed request tracing, and latency monitoring.",
        ["What happens if a middleware raises an exception before calling `call_next`?", "Can you call `call_next(request)` multiple times inside the same middleware?"],
        ["Calling `call_next` multiple times to retry failed requests (this is invalid; the request body stream has already been consumed).", "Failing to return the `Response` object returned by `call_next`."],
        "Emphasize: `call_next` can only be invoked ONCE per incoming request because HTTP request/response streams cannot be replayed without buffering.",
        ["[Streaming Responses](async-and-concurrency.md)", "[Logging Middleware](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/middleware/#basehttpmiddleware"]
    ),

    # FA-BAS-154
    (
        "FA-BAS-154",
        "Measuring Request Execution Time and Adding `X-Process-Time` Header",
        "Request duration is calculated by taking monotonic timestamps before and after `await call_next(request)` and attaching the elapsed time to the response headers.",
        "Measuring endpoint latency is crucial for detecting performance regressions and monitoring Service Level Objectives (SLOs). Using `time.perf_counter()` (which is monotonic and unaffected by system clock resets), the middleware records the timestamp immediately upon request arrival. After awaiting `call_next(request)`, it computes `elapsed = time.perf_counter() - start_time` and appends `X-Process-Time` to `response.headers`.",
        "import time\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def measure_execution_time(request: Request, call_next):\n    # Record high-resolution monotonic start time\n    start_time = time.perf_counter()\n    \n    response = await call_next(request)\n    \n    # Calculate total round-trip duration in milliseconds\n    duration_ms = (time.perf_counter() - start_time) * 1000\n    response.headers['X-Process-Time-Ms'] = f'{duration_ms:.2f}'\n    return response\n\n@app.get('/compute')\nasync def compute():\n    return {'result': sum(i * i for i in range(10000))}",
        "Measuring end-to-end request latency using time.perf_counter and attaching X-Process-Time-Ms header.",
        "`time.perf_counter()` uses the CPU's high-resolution performance counter, providing sub-microsecond precision. Attaching the header to `response.headers` mutates the Starlette `Headers` mapping before headers are serialized to HTTP wire format.",
        "API performance auditing, client-side latency debugging, and SLA verification in staging environments.",
        ["Why is `time.perf_counter()` preferred over `time.time()` for latency measurement?", "Does `X-Process-Time` measure network transit time between client and server?"],
        ["Using `time.time()`, which is susceptible to NTP time synchronization jumps and daylight saving adjustments.", "Assuming `X-Process-Time` includes the client's network upload/download latency (it only measures server-side processing)."],
        "Highlight: Always use `time.perf_counter()` for intervals and elapsed benchmarks; use `time.time()` only for wall-clock dates.",
        ["[Python Performance Optimization](../01-python/internals-and-performance.md)", "[HTTP Headers](../07-api-engineering/http-and-https.md)"],
        ["https://fastapi.tiangolo.com/tutorial/middleware/"]
    ),

    # FA-BAS-155
    (
        "FA-BAS-155",
        "Configuring Built-In `CORSMiddleware` in FastAPI",
        "FastAPI provides `CORSMiddleware` to manage Cross-Origin Resource Sharing, allowing web browsers on different domains to access API resources safely.",
        "Browsers enforce the Same-Origin Policy (SOP), blocking client-side JavaScript on `https://frontend.com` from reading responses from `https://api.domain.com` unless the API explicitly sends CORS headers. FastAPI includes Starlette's `CORSMiddleware`. Key configuration parameters include: `allow_origins` (list of permitted frontend domains), `allow_credentials` (allows cookies and Authorization headers), `allow_methods` (`['GET', 'POST', ...]` or `['*']`), and `allow_headers`.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI()\n\n# Configure CORS origins\norigins = [\n    'http://localhost:3000',\n    'https://app.example.com',\n]\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=origins,             # Specific trusted domains\n    allow_credentials=True,           # Support cookies and Authorization headers\n    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],  # Allowed HTTP verbs\n    allow_headers=['Authorization', 'Content-Type', 'X-Requested-With'],\n    max_age=600,                      # Cache preflight OPTIONS responses for 10 minutes\n)\n\n@app.get('/data')\nasync def get_data():\n    return {'data': 'secure_payload'}",
        "Configuring CORSMiddleware with explicit origin whitelists, allowed methods, and preflight caching.",
        "`CORSMiddleware` intercepts incoming HTTP `OPTIONS` requests (preflight checks). If the `Origin` header matches `allow_origins`, it responds immediately with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Max-Age` without forwarding the request to the route handler.",
        "Single Page Applications (React, Vue, Angular) and mobile web clients consuming backend APIs hosted on different domains.",
        ["What is an HTTP preflight OPTIONS request?", "Why is setting `allow_origins=['*']` dangerous when `allow_credentials=True`?"],
        ["Setting `allow_origins=['*']` alongside `allow_credentials=True` (browsers reject wildcard origins when credentials like cookies are enabled).", "Forgetting to include custom headers in `allow_headers`, causing preflight requests to fail."],
        "Emphasize: In production, never use `allow_origins=['*']`; always specify the exact frontend domain names.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Authentication](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/cors/"]
    ),

    # FA-BAS-156
    (
        "FA-BAS-156",
        "Enforcing HTTPS with `HTTPSRedirectMiddleware`",
        "`HTTPSRedirectMiddleware` automatically redirects all incoming plain unencrypted HTTP requests to secure HTTPS URLs with an HTTP 307 or 301 redirect.",
        "Transport Layer Security (TLS/HTTPS) is mandatory for modern APIs to protect credentials, tokens, and payloads against interception. While reverse proxies (Nginx, Traefik, AWS ALB) typically handle TLS termination and redirection, FastAPI provides `HTTPSRedirectMiddleware` to enforce HTTPS at the application layer. Any request arriving via `http://` or with `x-forwarded-proto: http` is immediately redirected to `https://`.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware\n\napp = FastAPI()\n\n# Enforce HTTPS redirect for all requests\napp.add_middleware(HTTPSRedirectMiddleware)\n\n@app.get('/secure-data')\nasync def secure_endpoint():\n    return {'status': 'secure_connection'}",
        "Adding HTTPSRedirectMiddleware to enforce HTTPS across all incoming API requests.",
        "`HTTPSRedirectMiddleware` inspects the request URL scheme (or `x-forwarded-proto` header). If the scheme is `'http'`, it constructs the equivalent `'https'` URL and returns an immediate `307 Temporary Redirect` response without calling downstream handlers.",
        "Enforcing encryption standards in cloud environments where internal reverse proxies might forward unencrypted traffic.",
        ["What HTTP status code does `HTTPSRedirectMiddleware` use for redirects (307)?", "Why is HTTPS redirection usually handled at the reverse proxy (Nginx) level in production?"],
        ["Enabling `HTTPSRedirectMiddleware` behind an SSL-terminating reverse proxy without configuring `X-Forwarded-Proto`, causing infinite redirect loops.", "Assuming `HTTPSRedirectMiddleware` provides TLS certificates (it only redirects; Uvicorn or Nginx must terminate TLS)."],
        "Warn about infinite redirect loops: Ensure reverse proxies pass `X-Forwarded-Proto: https` so the middleware knows HTTPS was already terminated.",
        ["[Nginx Configuration](../11-devops/nginx.md)", "[HTTP & HTTPS](../07-api-engineering/http-and-https.md)"],
        ["https://www.starlette.io/middleware/#httpsredirectmiddleware"]
    ),

    # FA-BAS-157
    (
        "FA-BAS-157",
        "Mitigating Host Header Attacks with `TrustedHostMiddleware`",
        "`TrustedHostMiddleware` guards against HTTP Host header injection and cache poisoning attacks by enforcing that incoming requests specify an allowed `Host` header domain.",
        "Attackers can manipulate the HTTP `Host` header (e.g. sending `Host: attacker.com`) to cause web applications to generate malicious password reset links or poison shared reverse-proxy caches. Starlette's `TrustedHostMiddleware` verifies the incoming `Host` header against an explicit list of allowed domain patterns. If the header does not match, the middleware aborts the request immediately with an HTTP 400 Bad Request.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.trustedhost import TrustedHostMiddleware\n\napp = FastAPI()\n\n# Enforce allowed Host domains\napp.add_middleware(\n    TrustedHostMiddleware,\n    allowed_hosts=[\n        'api.example.com',\n        '*.example.com',\n        'localhost',\n        '127.0.0.1',\n    ]\n)\n\n@app.get('/info')\nasync def info():\n    return {'status': 'trusted_host'}",
        "Configuring TrustedHostMiddleware to whitelist trusted host domains and wildcard subdomains.",
        "`TrustedHostMiddleware` inspects `request.headers.get('host')`. It evaluates the domain against the whitelist using regex wildcard matching. Non-matching hosts are rejected with `Response('Invalid host header', status_code=400)` before any routing logic runs.",
        "Protecting password reset generation endpoints, OAuth redirect URI generators, and preventing cache poisoning.",
        ["What is an HTTP Host Header Poisoning attack?", "Can `TrustedHostMiddleware` support wildcard subdomains like `*.example.com`?"],
        ["Setting `allowed_hosts=['*']` in production, which completely disables host validation security.", "Forgetting to include local testing hosts (`localhost`, `testserver`) in test suites, causing tests to fail with 400."],
        "Emphasize: Always configure `allowed_hosts` in production to prevent password reset poisoning and SSRF vulnerabilities.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Security Architecture](../12-security/application-security.md)"],
        ["https://www.starlette.io/middleware/#trustedhostmiddleware"]
    ),

    # FA-BAS-158
    (
        "FA-BAS-158",
        "Built-In `GZipMiddleware` and Response Compression Trade-Offs",
        "`GZipMiddleware` automatically compresses HTTP responses that exceed a specified byte size threshold using gzip compression, reducing bandwidth consumption.",
        "Sending large JSON payloads or text responses consumes network bandwidth and increases download times for mobile clients. `GZipMiddleware` intercepts outgoing responses. If the client includes `Accept-Encoding: gzip` in its request headers and the response body size exceeds `minimum_size` (default 500 bytes), the middleware compresses the payload with gzip, sets `Content-Encoding: gzip`, and updates `Content-Length`.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.gzip import GZipMiddleware\n\napp = FastAPI()\n\n# Compress responses larger than 1000 bytes\napp.add_middleware(GZipMiddleware, minimum_size=1000)\n\n@app.get('/large-dataset')\nasync def get_large_dataset():\n    # This large list will automatically be gzip-compressed over the wire\n    return {'items': [{'id': i, 'name': f'Item_{i}'} for i in range(500)]}",
        "Adding GZipMiddleware with a 1000-byte minimum compression threshold.",
        "`GZipMiddleware` evaluates the response body size. If larger than `minimum_size`, it pipes the response body through Python's `gzip.compress()`, replaces the body with compressed bytes, and attaches `Content-Encoding: gzip`.",
        "Data-heavy APIs returning large catalog listings, analytics tables, or GeoJSON files.",
        ["Why shouldn't responses smaller than 500 bytes be gzip-compressed?", "What is the BREACH security vulnerability associated with HTTP compression over HTTPS?"],
        ["Setting `minimum_size` too low (compressing tiny 50-byte payloads actually increases their size due to gzip header overhead).", "Compressing secrets and reflection tokens alongside user input over HTTPS (vulnerable to BREACH attack)."],
        "Rule of thumb: Keep `minimum_size` around 1000 bytes; let edge CDNs (Cloudflare/CloudFront) handle compression when possible.",
        ["[Production Optimization](production-and-performance.md)", "[API Security](../07-api-engineering/api-security.md)"],
        ["https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware"]
    ),

    # FA-BAS-159
    (
        "FA-BAS-159",
        "Raising `HTTPException` in FastAPI with Status Codes and Details",
        "`HTTPException` is FastAPI's primary mechanism for terminating request processing and returning client-friendly error responses with specific HTTP status codes.",
        "When business logic fails (e.g., entity not found, invalid credentials, insufficient funds), route handlers raise `HTTPException(status_code=..., detail=...)`. Unlike standard Python exceptions that result in an unhandled 500 crash, FastAPI's default exception handler catches `HTTPException` and serializes it into a JSON response formatted as `{'detail': ...}` with the appropriate HTTP status code.",
        "from fastapi import FastAPI, HTTPException, status\n\napp = FastAPI()\n\nDATABASE = {'item_1': 'Laptop', 'item_2': 'Keyboard'}\n\n@app.get('/items/{item_id}')\nasync def get_item(item_id: str):\n    if item_id not in DATABASE:\n        raise HTTPException(\n            status_code=status.HTTP_404_NOT_FOUND,\n            detail=f'Item with ID {item_id} does not exist',\n            headers={'X-Error-Reason': 'ResourceNotFound'}\n        )\n    return {'item_id': item_id, 'name': DATABASE[item_id]}",
        "Raising HTTPException with status code, custom detail message, and error headers.",
        "When `raise HTTPException(...)` executes, Python unwinds the call stack. FastAPI's `ExceptionMiddleware` catches the exception, extracts the `status_code`, `detail`, and `headers`, and returns a Starlette `JSONResponse`.",
        "Standard error signaling across all REST API endpoints for 400, 401, 403, 404, and 409 errors.",
        ["Can the `detail` parameter of `HTTPException` be a dictionary or list instead of a string?", "How does raising `HTTPException` differ from returning a `JSONResponse(status_code=404)`?"],
        ["Returning `HTTPException` instead of raising it (e.g., `return HTTPException(...)` sends HTTP 200 with an exception object).", "Using generic 500 status codes for client-side input errors that should be 400 or 422."],
        "Golden rule: Always `raise` HTTPException; never `return` it.",
        ["[Handling Errors](middleware-and-exception-handling.md)", "[HTTP Status Codes](../07-api-engineering/http-and-https.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]
    ),

    # FA-BAS-160
    (
        "FA-BAS-160",
        "Custom Headers in `HTTPException` (e.g. `WWW-Authenticate`)",
        "`HTTPException` accepts a `headers` dictionary to attach protocol-mandated response headers, such as `WWW-Authenticate` on HTTP 401 Unauthorized errors.",
        "Certain HTTP error status codes require accompanying HTTP response headers according to RFC specifications. Most notably, RFC 6750 dictates that when returning HTTP 401 Unauthorized for OAuth2/Bearer token failures, the server MUST include a `WWW-Authenticate: Bearer` header indicating the required authentication scheme. FastAPI allows passing a dictionary of custom headers to `HTTPException(headers={...})`.",
        "from fastapi import FastAPI, HTTPException, status\n\napp = FastAPI()\n\n@app.get('/protected-resource')\nasync def access_resource(api_key: str | None = None):\n    if api_key != 'super-secret-key':\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Invalid or missing authentication credentials',\n            headers={'WWW-Authenticate': 'Bearer realm=\"api\", error=\"invalid_token\"'}\n        )\n    return {'data': 'confidential_payload'}",
        "Attaching RFC-compliant WWW-Authenticate header to an HTTP 401 HTTPException.",
        "FastAPI's exception handler reads the `headers` attribute from the `HTTPException` instance and merges them into the final `JSONResponse` headers before sending the response to the client.",
        "OAuth2 token validation, rate-limit rejection responses with `Retry-After: 60`, and caching directives on errors.",
        ["What does RFC 6750 require when returning HTTP 401 Unauthorized?", "How do you pass a `Retry-After` header when returning HTTP 429 Too Many Requests?"],
        ["Omitting `WWW-Authenticate` on 401 responses, causing compliance failures with automated OAuth2 client libraries.", "Confusing 401 Unauthorized (unauthenticated) with 403 Forbidden (authenticated, but lacking permissions)."],
        "Remember: 401 Unauthorized MUST include `WWW-Authenticate`; 403 Forbidden does NOT require it.",
        ["[Authentication & Security](authentication-and-security.md)", "[OAuth2 Scopes](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#raise-the-exception"]
    ),

    # FA-BAS-161
    (
        "FA-BAS-161",
        "Handling `RequestValidationError` from Pydantic Input Failures",
        "`RequestValidationError` is raised by FastAPI when an incoming request body, query parameter, or path parameter fails Pydantic validation schemas.",
        "When a client submits malformed JSON, missing required fields, or data that violates type constraints (e.g. sending `'abc'` for an integer field), FastAPI intercepts the error before the route handler is invoked and raises `fastapi.exceptions.RequestValidationError`. By default, FastAPI converts this into an HTTP 422 Unprocessable Entity response containing a structured breakdown of each invalid field, location (`body`, `query`), and error reason.",
        "from fastapi import FastAPI\nfrom fastapi.exceptions import RequestValidationError\nfrom pydantic import BaseModel, EmailStr\n\napp = FastAPI()\n\nclass UserSignup(BaseModel):\n    username: str\n    email: EmailStr\n    age: int\n\n@app.post('/signup')\nasync def signup(user: UserSignup):\n    return {'status': 'user_created', 'username': user.username}\n\n# Example invalid request body:\n# {'username': 'alice', 'email': 'not-an-email', 'age': 'twenty'}\n# Returns HTTP 422 Unprocessable Entity with validation details automatically",
        "Pydantic input validation triggering RequestValidationError and HTTP 422 responses automatically.",
        "FastAPI's dependency and parameter solving pipeline runs Pydantic's `TypeAdapter` on incoming data. If validation raises a Pydantic `ValidationError`, FastAPI catches it, wraps it in `RequestValidationError`, and dispatches it to the default validation exception handler.",
        "Input sanitization, boundary defense, and user input validation across all POST/PUT/PATCH endpoints.",
        ["What HTTP status code does FastAPI return for validation errors by default (422)?", "How does `RequestValidationError` differ from a standard Pydantic `ValidationError`?"],
        ["Attempting to catch `RequestValidationError` inside route handlers (it is raised BEFORE the route handler is reached).", "Confusing HTTP 400 Bad Request with HTTP 422 Unprocessable Entity."],
        "Explain that 422 indicates syntactically valid JSON that fails semantic schema rules (e.g. invalid email format).",
        ["[Pydantic Validation](pydantic-and-validation.md)", "[Custom Validation Handlers](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#use-the-requestvalidationerror-body"]
    ),

    # FA-BAS-162
    (
        "FA-BAS-162",
        "Customizing Validation Error Response JSON Formatting",
        "Default 422 validation error responses can be customized by registering a custom exception handler for `RequestValidationError` using `@app.exception_handler()`.",
        "The default FastAPI 422 error JSON can be verbose for frontend clients. Teams often prefer a simplified, standardized error envelope (e.g. `{'success': false, 'errors': [...]}`). By overriding the `RequestValidationError` handler, you can iterate over `exc.errors()`, format error messages into clean key-value pairs, and return a customized `JSONResponse`.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.exceptions import RequestValidationError\nfrom fastapi.responses import JSONResponse\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass ProfileSchema(BaseModel):\n    name: str\n    score: int\n\n@app.exception_handler(RequestValidationError)\nasync def custom_validation_handler(request: Request, exc: RequestValidationError):\n    # Transform Pydantic errors into a simplified client-friendly dictionary\n    cleaned_errors = {}\n    for error in exc.errors():\n        field = error['loc'][-1]\n        cleaned_errors[str(field)] = error['msg']\n        \n    return JSONResponse(\n        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,\n        content={\n            'status': 'error',\n            'error_code': 'VALIDATION_FAILED',\n            'details': cleaned_errors\n        }\n    )\n\n@app.post('/profile')\nasync def create_profile(profile: ProfileSchema):\n    return profile",
        "Overriding RequestValidationError handler to return a simplified, structured error payload.",
        "`@app.exception_handler(RequestValidationError)` registers the custom coroutine in FastAPI's internal exception mapping dictionary. When a validation failure occurs, FastAPI bypasses the default Starlette handler and invokes the custom coroutine.",
        "Frontend API consistency, mobile SDK integration, and enterprise error-envelope standardization.",
        ["What information does `exc.errors()` provide for each validation error?", "How can you access the raw unparsed request body inside the validation handler via `exc.body`?"],
        ["Returning strings instead of JSON dictionaries from custom exception handlers.", "Overwriting the handler without logging the error, making client debugging difficult."],
        "Mention that `exc.body` contains the raw input payload that failed validation, which is invaluable for debugging.",
        ["[Pydantic Validation](pydantic-and-validation.md)", "[Global Exception Handlers](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#override-request-validation-exceptions"]
    ),

    # FA-BAS-163
    (
        "FA-BAS-163",
        "Global Custom Exception Handler with `@app.exception_handler(ExceptionClass)`",
        "FastAPI allows registering custom exception handlers for any Python exception class using `@app.exception_handler(CustomException)` to return clean JSON responses.",
        "Rather than littering route handlers with repetitive `try/except` blocks, domain-driven FastAPI applications define custom domain exceptions (e.g., `EntityNotFoundException`, `InsufficientFundsException`). When raised anywhere in the service layer, FastAPI catches the exception at the application boundary and invokes the registered handler to serialize a standardized HTTP response.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Custom Domain Exception\nclass ItemOutOfStockException(Exception):\n    def __init__(self, item_name: str, requested: int):\n        self.item_name = item_name\n        self.requested = requested\n\n# Register Global Exception Handler\n@app.exception_handler(ItemOutOfStockException)\nasync def item_stock_handler(request: Request, exc: ItemOutOfStockException):\n    return JSONResponse(\n        status_code=status.HTTP_409_CONFLICT,\n        content={\n            'error': 'OUT_OF_STOCK',\n            'message': f'Item {exc.item_name} does not have {exc.requested} units in stock'\n        }\n    )\n\n@app.post('/checkout')\nasync def checkout(item: str, quantity: int):\n    if quantity > 5:\n        raise ItemOutOfStockException(item_name=item, requested=quantity)\n    return {'status': 'order_confirmed'}",
        "Defining a custom domain exception and registering a global exception handler in FastAPI.",
        "When an unhandled exception escapes a route handler, FastAPI checks its exception handler registry. If an exact class match (or subclass match) exists, it dispatches the request and exception to the custom handler function, returning the generated `JSONResponse`.",
        "Domain-Driven Design (DDD) microservices where business logic layers are decoupled from HTTP transport concerns.",
        ["How does exception inheritance work in `@app.exception_handler`?", "Why is raising domain exceptions cleaner than raising `HTTPException` directly in database service functions?"],
        ["Catching custom domain exceptions in every route handler with duplicate `try/except` boilerplate.", "Failing to inherit custom exceptions from Python's base `Exception` class."],
        "Emphasize: Raising domain exceptions in service classes keeps business logic decoupled from HTTP status codes and web frameworks.",
        ["[Exception Handling](middleware-and-exception-handling.md)", "[Layered Architecture](../10-system-design/fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers"]
    ),

    # FA-BAS-164
    (
        "FA-BAS-164",
        "Handling Internal 500 Exceptions Gracefully Without Leaking Tracebacks",
        "Unhandled internal server errors must be caught by a global `Exception` handler to log the stack trace internally while returning a sanitized generic 500 message to clients.",
        "Allowing unhandled Python exceptions (e.g. `ZeroDivisionError`, `KeyError`, `psycopg2.OperationalError`) to reach the client exposes internal file paths, library versions, and database schemas in stack traces, creating severe security vulnerabilities. Registering a global handler for `Exception` captures all uncaught exceptions, logs the full stack trace to monitoring systems (Sentry, DataDog), and returns a sanitized JSON response: `{'error': 'Internal server error', 'request_id': ...}`.",
        "import logging\nimport uuid\nfrom fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\nlogger = logging.getLogger('api_errors')\napp = FastAPI()\n\n@app.exception_handler(Exception)\nasync def global_exception_handler(request: Request, exc: Exception):\n    error_id = str(uuid.uuid4())\n    # Log full traceback internally for developer investigation\n    logger.error(f'Unhandled error [ID: {error_id}] on {request.url.path}: {exc}', exc_info=True)\n    \n    # Return sanitized generic response to client (zero internal leak)\n    return JSONResponse(\n        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n        content={\n            'error': 'Internal Server Error',\n            'message': 'An unexpected error occurred. Please contact support.',\n            'error_reference_id': error_id,\n        }\n    )\n\n@app.get('/crash')\nasync def deliberate_crash():\n    return 1 / 0  # Triggers ZeroDivisionError",
        "Catching uncaught exceptions globally, logging the traceback with an error ID, and returning sanitized 500 responses.",
        "The global handler intercepts all exceptions derived from Python's `Exception` class that were not handled by more specific exception handlers, preventing Starlette's raw debug traceback page from leaking in production.",
        "Production security hardening across all external and internal API deployments.",
        ["Why must internal stack traces never be displayed to API clients in production?", "What is an Error Reference ID / Correlation ID?"],
        ["Running FastAPI with `debug=True` in production, which renders interactive HTML tracebacks to external users.", "Catching `BaseException` instead of `Exception` (can intercept system exit and cancel signals)."],
        "Golden rule: Never show stack traces to clients; log traces internally with a UUID reference ID returned to the user.",
        ["[API Security](../07-api-engineering/api-security.md)", "[Logging Middleware](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]
    ),

    # FA-BAS-165
    (
        "FA-BAS-165",
        "Starlette's `HTTPException` vs FastAPI's `HTTPException`",
        "FastAPI's `HTTPException` inherits from Starlette's `HTTPException` but adds support for complex data types (dicts, lists) in the `detail` parameter.",
        "While both exceptions signal HTTP errors, there is an important distinction: 1) Starlette's `HTTPException` (`starlette.exceptions.HTTPException`) only accepts a string for `detail`; 2) FastAPI's `HTTPException` (`fastapi.HTTPException`) accepts any JSON-serializable Python data type (strings, dictionaries, lists of objects). When building FastAPI applications, developers should always import `HTTPException` from `fastapi` rather than `starlette.exceptions` to allow structured error details.",
        "from fastapi import FastAPI, HTTPException, status\n\napp = FastAPI()\n\n@app.get('/validate-account')\nasync def validate_account(age: int):\n    if age < 18:\n        # FastAPI's HTTPException supports rich dictionary details\n        raise HTTPException(\n            status_code=status.HTTP_400_BAD_REQUEST,\n            detail={\n                'code': 'AGE_REQUIREMENT',\n                'minimum_required': 18,\n                'provided': age,\n                'resolution': 'Parental consent required'\n            }\n        )\n    return {'status': 'eligible'}",
        "Using FastAPI's HTTPException with a structured dictionary detail payload.",
        "FastAPI's exception handler uses `jsonable_encoder` on the `detail` parameter before serializing the response, whereas Starlette's handler renders `detail` as a plain string.",
        "Returning structured machine-readable error codes and validation contexts to API consumers.",
        ["What happens if you pass a dictionary to Starlette's `HTTPException`?", "Which `HTTPException` should be imported in FastAPI codebases?"],
        ["Importing `from starlette.exceptions import HTTPException` accidentally, losing support for dictionary details.", "Catching `fastapi.HTTPException` with a handler registered only for `starlette.exceptions.HTTPException`."],
        "Always import `from fastapi import HTTPException` across all FastAPI router and service modules.",
        ["[Exception Handling](middleware-and-exception-handling.md)", "[Pydantic Serialization](pydantic-and-validation.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception"]
    ),

    # FA-BAS-166
    (
        "FA-BAS-166",
        "Order of Middleware Execution in the ASGI Onion Stack",
        "Middleware executes in 'First Added, Last Executed on Request' (or reverse registration order) in Starlette, forming an onion-like wrapping hierarchy.",
        "In Starlette and FastAPI, when you register middleware using `app.add_middleware(MiddlewareA)` followed by `app.add_middleware(MiddlewareB)`: 1) MiddlewareB wraps MiddlewareA; 2) For incoming requests, the LAST added middleware executes FIRST (Outer -> Inner); 3) For outgoing responses, the execution order reverses (Inner -> Outer). Understanding this onion stack is critical when middleware depends on state set by earlier middleware (e.g. CORS or Authentication before Logging).",
        "from fastapi import FastAPI, Request\n\napp = FastAPI()\n\n# Execution sequence:\n# Request in:  Middleware 2 -> Middleware 1 -> Route\n# Response out: Route -> Middleware 1 -> Middleware 2\n\n@app.middleware('http')\nasync def middleware_one(request: Request, call_next):\n    print('1. Middleware One Request IN')\n    response = await call_next(request)\n    print('4. Middleware One Response OUT')\n    return response\n\n@app.middleware('http')\nasync def middleware_two(request: Request, call_next):\n    print('2. Middleware Two Request IN')\n    response = await call_next(request)\n    print('3. Middleware Two Response OUT')\n    return response\n\n@app.get('/test')\nasync def test():\n    return {'msg': 'ok'}",
        "Demonstrating the LIFO execution order of HTTP middleware layers in FastAPI.",
        "Each call to `add_middleware()` or `@app.middleware()` wraps the existing ASGI application callable inside a new outer callable: `app = Middleware2(Middleware1(original_app))`. Hence, `Middleware2` intercepts incoming requests first.",
        "Designing middleware pipelines where security verification must execute before logging, or compression must execute after all headers are set.",
        ["Why does the last-added middleware execute first on incoming requests?", "Where should `CORSMiddleware` be placed in the middleware stack?"],
        ["Registering authentication middleware after middleware that assumes authenticated users already exist.", "Placing GZip middleware inside middleware that inspects uncompressed response bodies."],
        "Remember: Middleware wraps like an onion: The last added is on the outside, receiving incoming requests first.",
        ["[ASGI Specification](middleware-and-exception-handling.md)", "[CORS Middleware](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/middleware/#ordering"]
    ),

    # FA-BAS-167
    (
        "FA-BAS-167",
        "Adding Middleware Using `app.add_middleware(MiddlewareClass, **options)`",
        "`app.add_middleware()` is the standard programmatic method for registering class-based ASGI middleware and third-party middleware packages in FastAPI.",
        "While `@app.middleware('http')` works for simple functions, enterprise middleware is organized as reusable classes that accept configuration options. The `app.add_middleware()` method accepts a middleware class and keyword arguments forwarded to the class constructor. This is the required mechanism for adding built-in middleware (`CORSMiddleware`, `GZipMiddleware`) as well as third-party packages (e.g. `PrometheusFastApiMiddleware`, `SentryAsgiMiddleware`).",
        "from fastapi import FastAPI\nfrom starlette.middleware.sessions import SessionMiddleware\nfrom starlette.middleware.gzip import GZipMiddleware\n\napp = FastAPI()\n\n# Register class-based middleware with keyword arguments\napp.add_middleware(GZipMiddleware, minimum_size=1000)\napp.add_middleware(\n    SessionMiddleware,\n    secret_key='super-secret-cryptographic-key',\n    session_cookie='session_id',\n    max_age=3600,\n)\n\n@app.get('/session-data')\nasync def read_session():\n    return {'status': 'middleware_active'}",
        "Registering class-based GZip and Session middleware using app.add_middleware.",
        "`add_middleware` stores a tuple of `(middleware_class, options)` in `app.user_middleware`. When the FastAPI application boots up, it compiles the middleware list into a nested ASGI callable chain.",
        "Configuring production middleware stacks including session cookies, CORS policies, Prometheus metrics, and rate limiters.",
        ["Can you call `app.add_middleware()` after the application has started handling requests?", "How does `app.add_middleware()` pass configuration arguments to the middleware class?"],
        ["Attempting to call `app.add_middleware()` dynamically inside route handlers (middleware stack is immutable once application starts).", "Passing positional arguments instead of keyword options to `app.add_middleware()`."],
        "Emphasize: All middleware must be registered during application initialization before the server starts accepting requests.",
        ["[CORS Configuration](middleware-and-exception-handling.md)", "[ASGI Architecture](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/middleware/"]
    ),

    # FA-BAS-168
    (
        "FA-BAS-168",
        "Passing Request State Using `request.state` Across Middleware and Routes",
        "`request.state` is a Starlette namespace object for storing arbitrary per-request attributes shared across middleware, dependencies, and route handlers.",
        "When middleware extracts or generates data needed downstream (such as a decoded JWT user ID, correlation ID, tenant schema name, or rate-limit counter), storing it as a global variable would cause race conditions between concurrent requests. `request.state` provides a thread-safe, request-scoped namespace where middleware can attach attributes (e.g. `request.state.tenant_id = 'org_123'`) that can be accessed by route handlers or dependencies.",
        "import uuid\nfrom fastapi import FastAPI, Request, Depends\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def attach_request_context(request: Request, call_next):\n    # Generate and attach request-scoped state\n    request.state.correlation_id = str(uuid.uuid4())\n    request.state.tenant_id = request.headers.get('x-tenant-id', 'default')\n    \n    response = await call_next(request)\n    response.headers['X-Correlation-ID'] = request.state.correlation_id\n    return response\n\n@app.get('/context')\nasync def get_context(request: Request):\n    # Access state populated by middleware\n    return {\n        'correlation_id': request.state.correlation_id,\n        'tenant_id': request.state.tenant_id,\n    }",
        "Populating and reading request-scoped metadata via request.state.",
        "`request.state` is an instance of `starlette.datastructures.State`, which wraps an internal dictionary. Each incoming HTTP request receives a new `Request` instance, guaranteeing complete isolation between concurrent async tasks.",
        "Passing correlation IDs, authenticated user tokens, geolocation metadata, and tenant IDs down to route handlers.",
        ["Why shouldn't global variables be used to store request metadata in async FastAPI?", "What exception is raised if you access an undefined attribute on `request.state`?"],
        ["Using module-level global variables for request state, causing concurrent requests to overwrite each other's data.", "Assuming attributes on `request.state` persist after the HTTP response has completed."],
        "Highlight: `request.state` is the official, safe mechanism for request-scoped data sharing in Starlette and FastAPI.",
        ["[Dependencies Injection](routing-and-dependencies.md)", "[Correlation IDs](middleware-and-exception-handling.md)"],
        ["https://www.starlette.io/requests/#other-state"]
    ),

    # FA-BAS-169
    (
        "FA-BAS-169",
        "Logging Incoming Requests and Client IP Addresses in Middleware",
        "HTTP middleware logs incoming request paths, HTTP methods, status codes, and client IP addresses by inspecting `request.client.host` and `X-Forwarded-For`.",
        "Access logging is essential for security audits, traffic analysis, and detecting denial-of-service attempts. In middleware, developers inspect `request.method`, `request.url.path`, and the client's IP address. Because production applications typically sit behind reverse proxies or load balancers, the real client IP is extracted from the `X-Forwarded-For` header rather than the immediate proxy connection IP (`request.client.host`).",
        "import logging\nfrom fastapi import FastAPI, Request\n\nlogger = logging.getLogger('access_log')\nlogging.basicConfig(level=logging.INFO)\n\napp = FastAPI()\n\ndef get_client_ip(request: Request) -> str:\n    forwarded = request.headers.get('x-forwarded-for')\n    if forwarded:\n        # First IP in X-Forwarded-For is the original client\n        return forwarded.split(',')[0].strip()\n    return request.client.host if request.client else 'unknown'\n\n@app.middleware('http')\nasync def access_logging_middleware(request: Request, call_next):\n    client_ip = get_client_ip(request)\n    logger.info(f'REQUEST START: {request.method} {request.url.path} from IP: {client_ip}')\n    \n    response = await call_next(request)\n    \n    logger.info(f'REQUEST END: {request.method} {request.url.path} - Status: {response.status_code}')\n    return response\n\n@app.get('/ping')\nasync def ping():\n    return {'status': 'pong'}",
        "Extracting client IP via X-Forwarded-For and logging request lifecycle in HTTP middleware.",
        "`request.client` returns an `Address(host, port)` named tuple representing the immediate TCP socket peer. In proxy environments, `request.headers.get('x-forwarded-for')` contains the comma-separated chain of client and intermediate proxy IPs.",
        "Security incident response, rate-limiting audits, and access logging compliance.",
        ["Why is `request.client.host` often the internal IP of an Nginx load balancer rather than the real client?", "What is IP spoofing and how can untrusted `X-Forwarded-For` headers be exploited?"],
        ["Blindly trusting `X-Forwarded-For` from untrusted clients without verifying the proxy is stripping spoofed client headers.", "Logging sensitive request body data (like passwords or credit card numbers) in access logs."],
        "Caution: Only trust `X-Forwarded-For` if your edge reverse proxy is configured to strip or overwrite untrusted incoming forwarded headers.",
        ["[Nginx Reverse Proxy](../11-devops/nginx.md)", "[API Security](../07-api-engineering/api-security.md)"],
        ["https://www.starlette.io/requests/#client-address"]
    ),

    # FA-BAS-170
    (
        "FA-BAS-170",
        "Inspecting URL Paths and Query Parameters in Middleware",
        "URL components are inspected in middleware via `request.url.path`, `request.query_params`, and boolean path matching functions.",
        "Middleware often needs to execute logic selectively (e.g. bypassing authentication on `/docs`, `/openapi.json`, or `/healthz`). The `request.url` object provides access to `path`, `query`, `scheme`, and `netloc`. Query parameters can be accessed via the mapping `request.query_params` (e.g. `request.query_params.get('filter')`).",
        "from fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\nEXEMPT_PATHS = {'/healthz', '/docs', '/openapi.json'}\n\n@app.middleware('http')\nasync def path_filtering_middleware(request: Request, call_next):\n    # Skip processing for exempt documentation or health-check paths\n    if request.url.path in EXEMPT_PATHS or request.url.path.startswith('/static'):\n        return await call_next(request)\n        \n    # Inspect query parameters\n    debug_mode = request.query_params.get('debug') == 'true'\n    \n    response: Response = await call_next(request)\n    if debug_mode:\n        response.headers['X-Debug-Mode'] = 'enabled'\n    return response\n\n@app.get('/healthz')\nasync def health():\n    return {'status': 'healthy'}\n\n@app.get('/data')\nasync def get_data():\n    return {'data': 42}",
        "Bypassing middleware logic for documentation endpoints and reading query parameters.",
        "`request.url.path` returns a normalized string of the URL path without query arguments. `request.query_params` parses the raw query string into an immutable `QueryParams` multidict structure.",
        "Exempting health check probes and OpenAPI documentation from authentication or rate-limiting middleware.",
        ["What is the difference between `request.url.path` and `request.scope['path']`?", "How do you handle query parameters that appear multiple times (e.g. `?tag=a&tag=b`)?"],
        ["Hardcoding exact path checks (e.g. `request.url.path == '/docs'`) without handling trailing slashes (`/docs/`).", "Attempting to modify `request.query_params` directly (it is an immutable data structure)."],
        "Tip: Use `request.query_params.getlist('param')` when query parameters can contain multiple values.",
        ["[Routing Basics](routing-and-dependencies.md)", "[OpenAPI Documentation](fundamentals.md)"],
        ["https://www.starlette.io/requests/#url"]
    ),

    # FA-BAS-171
    (
        "FA-BAS-171",
        "Reading and Setting Cookies Inside Middleware",
        "Cookies are read from incoming requests via `request.cookies.get()` and attached to outgoing responses using `response.set_cookie()`.",
        "HTTP cookies are key-value pairs stored in the client browser, used for session identifiers and tracking tokens. Inside middleware, `request.cookies` exposes an immutable dictionary of received cookies. To set or update cookies on the client, middleware invokes `response.set_cookie()` with security flags like `httponly=True`, `secure=True`, and `samesite='lax'`.",
        "from fastapi import FastAPI, Request, Response\nimport uuid\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def tracking_cookie_middleware(request: Request, call_next) -> Response:\n    # Read existing tracking cookie\n    visitor_id = request.cookies.get('visitor_id')\n    is_new = False\n    if not visitor_id:\n        visitor_id = str(uuid.uuid4())\n        is_new = True\n        \n    response = await call_next(request)\n    \n    # If new visitor, attach Set-Cookie header to response\n    if is_new:\n        response.set_cookie(\n            key='visitor_id',\n            value=visitor_id,\n            httponly=True,   # Inaccessible to JavaScript (prevents XSS theft)\n            secure=True,     # Only sent over HTTPS\n            samesite='lax',  # Mitigates CSRF\n            max_age=86400 * 30  # 30-day expiration\n        )\n    return response\n\n@app.get('/visit')\nasync def visit(request: Request):\n    return {'visitor_id': request.cookies.get('visitor_id', 'new_assigned')}",
        "Reading cookies from request and setting secure HttpOnly cookies on the outgoing response in middleware.",
        "`response.set_cookie()` appends a standard RFC 6265 `Set-Cookie` header to the response. Browsers store the value and automatically send it in subsequent request `Cookie` headers matching the domain and path.",
        "Guest shopping cart sessions, A/B test variant assignment, and web analytics tracking.",
        ["What security protection does the `HttpOnly` flag provide?", "Why is `SameSite='Lax'` or `'Strict'` recommended for cookie defense against CSRF?"],
        ["Setting cookies without `HttpOnly=True`, allowing cross-site scripting (XSS) scripts to steal session tokens.", "Setting `secure=True` during local HTTP development without TLS, preventing browsers from storing the cookie."],
        "Emphasize: Always set `httponly=True`, `secure=True`, and `samesite='lax'` for sensitive cookies.",
        ["[Authentication Security](authentication-and-security.md)", "[Cookie Debugging](../12-security/web-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/response-cookies/"]
    ),

    # FA-BAS-172
    (
        "FA-BAS-172",
        "Handling 404 Not Found Globally via Custom Exception Handlers",
        "Global 404 handling allows capturing all unmapped URLs to return branded, structured JSON error payloads instead of default plaintext responses.",
        "When an incoming request URL does not match any registered route in FastAPI, Starlette raises a `starlette.exceptions.HTTPException(status_code=404)`. By registering an exception handler for `starlette.exceptions.HTTPException` (or checking for status code 404), the API can return a consistent JSON schema informing clients of available resources or API documentation links.",
        "from fastapi import FastAPI, Request\nfrom fastapi.responses import JSONResponse\nfrom starlette.exceptions import HTTPException as StarletteHTTPException\n\napp = FastAPI()\n\n@app.exception_handler(StarletteHTTPException)\nasync def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):\n    if exc.status_code == 404:\n        return JSONResponse(\n            status_code=404,\n            content={\n                'error': 'ROUTE_NOT_FOUND',\n                'message': f'The requested path {request.url.path} does not exist.',\n                'documentation_url': '/docs'\n            }\n        )\n    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})\n\n@app.get('/valid')\nasync def valid():\n    return {'status': 'ok'}",
        "Catching StarletteHTTPException to customize 404 Not Found responses with documentation links.",
        "FastAPI routes unmapped endpoints to an internal 404 responder that raises `StarletteHTTPException(status_code=404)`. The custom exception handler intercepts this exception before response rendering.",
        "Public API gateways, developer portals, and microservices requiring strict error formatting standards.",
        ["Why must you catch `StarletteHTTPException` rather than `FastAPI.HTTPException` for unmapped route 404s?", "How can you log 404 anomalies to detect directory traversal scans?"],
        ["Catching only `fastapi.HTTPException`, which fails to intercept unmapped routes generated by Starlette's router.", "Returning HTML error pages instead of JSON in JSON-only REST APIs."],
        "Key insight: Unmapped routes trigger `starlette.exceptions.HTTPException(404)`, so register your handler against `StarletteHTTPException`.",
        ["[Exception Handlers](middleware-and-exception-handling.md)", "[Routing Basics](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#override-the-httpexception-handler"]
    ),

    # FA-BAS-173
    (
        "FA-BAS-173",
        "Converting Domain Business Exceptions into HTTP Error Responses",
        "Business domain exceptions raised in repositories or service layers are converted into clean HTTP responses using centralized exception handlers.",
        "Clean architecture mandates that business domain logic must know nothing about HTTP transport concepts (no status codes, no headers, no `HTTPException`). A payment service simply raises `InsufficientBalanceError` or `AccountLockedError`. FastAPI's exception handler acts as an adapter, translating domain exceptions into appropriate HTTP status codes (e.g. 402 Payment Required or 423 Locked) and JSON payloads.",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI()\n\n# Domain Exceptions (Pure Python; Zero HTTP/FastAPI dependencies)\nclass DomainException(Exception):\n    pass\n\nclass InsufficientFundsError(DomainException):\n    def __init__(self, current_balance: float, required_amount: float):\n        self.current_balance = current_balance\n        self.required_amount = required_amount\n\n# HTTP Translation Adapter\n@app.exception_handler(InsufficientFundsError)\nasync def handle_insufficient_funds(request: Request, exc: InsufficientFundsError):\n    return JSONResponse(\n        status_code=status.HTTP_402_PAYMENT_REQUIRED,\n        content={\n            'error_code': 'INSUFFICIENT_FUNDS',\n            'balance': exc.current_balance,\n            'amount_needed': exc.required_amount,\n        }\n    )\n\n@app.post('/transfer')\nasync def transfer(amount: float):\n    current_balance = 50.0\n    if amount > current_balance:\n        raise InsufficientFundsError(current_balance=current_balance, required_amount=amount)\n    return {'status': 'success'}",
        "Mapping pure domain exceptions to HTTP 402 Payment Required responses cleanly at the API boundary.",
        "The service layer remains 100% testable in unit tests without mocking HTTP contexts. When invoked in FastAPI, unhandled domain exceptions bubble up to the ASGI boundary where FastAPI's exception registry dispatches to the mapped handler.",
        "Enterprise architectures, financial ledgers, and systems following Hexagonal or Clean Architecture.",
        ["Why is raising `HTTPException` inside a database repository considered an architectural smell?", "How does exception translation preserve the Single Responsibility Principle?"],
        ["Coupling business domain modules directly to `fastapi.HTTPException`.", "Creating dozens of identical exception handlers rather than using a common base domain exception hierarchy."],
        "Emphasize: Core business domain code should never import `fastapi` or `HTTPException`.",
        ["[Clean Architecture](../10-system-design/fundamentals.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers"]
    ),

    # FA-BAS-174
    (
        "FA-BAS-174",
        "Differences Between Route Dependencies and HTTP Middleware",
        "Dependencies run per-route with access to parsed parameters and typing, whereas middleware runs globally for all requests before routing occurs.",
        "FastAPI provides two primary mechanisms for cross-cutting logic: 1) Middleware: Executes globally across every request, operates on raw ASGI scopes before routing and parameter validation, has access to `call_next`, and cannot access parsed Pydantic models; 2) Dependencies (`Depends`): Executes per-route (or per-router), runs after routing and parameter validation, has full access to typed parameters and sub-dependencies, but cannot wrap response headers after endpoint execution (unless using `yield`).",
        "# Comparison matrix:\n# Feature               | Middleware                   | Dependency (Depends)\n# Scope                 | Global (All routes)          | Per-route / Per-router\n# Execution Time        | Before routing               | After route matching\n# Parameter Access      | Raw URL/Headers only         | Parsed Pydantic models\n# OpenAPI Documentation | NOT included in schema       | Automatically documented\n# Response Wrapping     | Full access to call_next     | yield cleanup only",
        "Conceptual comparison matrix between FastAPI middleware and route dependencies.",
        "Middleware wraps the outer ASGI application callable. Dependencies are evaluated during FastAPI's internal endpoint execution graph after Starlette's router matches the endpoint URL.",
        "Choosing the right architecture when designing authentication, rate limiting, and request logging.",
        ["Can a middleware access the matched route parameters (e.g. `user_id`) directly?", "Why are dependencies better suited for endpoint authorization than middleware?"],
        ["Using middleware for role-based authorization where route-specific permissions are required (difficult to inspect route endpoints in middleware).", "Using dependencies when response compression or global execution timing is required across all routes."],
        "Rule of thumb: Global request/response modification = Middleware; Route-specific authorization and data fetching = Dependency.",
        ["[Dependencies Basics](routing-and-dependencies.md)", "[Middleware Setup](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/"]
    ),

    # FA-BAS-175
    (
        "FA-BAS-175",
        "When to Use Dependencies vs Middleware for Authentication and Logging",
        "Use middleware for global logging, correlation IDs, and CORS; use dependencies for user authentication, permission scopes, and database sessions.",
        "Authentication and observability often blur the lines between middleware and dependencies: 1) Logging: Global access logging (IP, method, path, latency) belongs in Middleware because it must record 404s, unhandled 500s, and documentation requests; 2) Authentication: Route-level authentication belongs in Dependencies (`Depends(get_current_user)`) because different routes require different permissions (e.g. public endpoints vs admin endpoints), and dependencies inject the validated `User` object directly into route arguments with full OpenAPI documentation.",
        "from fastapi import FastAPI, Depends, HTTPException, status, Request\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\n\napp = FastAPI()\nsecurity = HTTPBearer()\n\n# 1. Global Middleware: Cross-cutting latency & access logging\n@app.middleware('http')\nasync def global_access_log(request: Request, call_next):\n    response = await call_next(request)\n    return response\n\n# 2. Scoped Dependency: Authenticated User with OpenAPI documentation\nasync def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):\n    if creds.credentials != 'valid_token':\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')\n    return {'user_id': 42, 'role': 'admin'}\n\n@app.get('/admin/dashboard')\nasync def admin_dashboard(user: dict = Depends(get_current_user)):\n    return {'status': 'authorized', 'user': user}",
        "Combining global logging middleware with route-specific authentication dependencies.",
        "The dependency integrates into OpenAPI/Swagger docs, rendering the 'Authorize' lock icon in the UI. Middleware runs before authentication, ensuring access logs capture failed 401 requests.",
        "Production enterprise API architecture combining global observability with granular security scopes.",
        ["Why doesn't global middleware show authentication requirements in Swagger UI?", "Can an authentication dependency access state set by earlier middleware?"],
        ["Enforcing authentication in global middleware, making it difficult to exclude public endpoints like `/login` or `/healthz`.", "Putting access logging in dependencies, which misses logging 404 Not Found requests."],
        "Emphasize: Middleware for universal transport plumbing; Dependencies for domain-aware authorization and typing.",
        ["[Authentication & Security](authentication-and-security.md)", "[Dependencies](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/"]
    ),
]
