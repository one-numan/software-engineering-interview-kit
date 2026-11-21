# Django Fundamentals, Architecture & Request Lifecycle

This module covers foundational Django architectural principles, project configuration, settings management, WSGI and ASGI handlers, the request/response lifecycle, and application initialization.

---

## Table of Contents
- [Basic Level (Questions 001–025)](#basic-level)
- [Intermediate Level (Questions 001–025)](#intermediate-level)
- [Advanced Level (Questions 001–025)](#advanced-level)

---

## Basic Level

### DJ-BAS-001: What is Django and What is the MVT Architectural Pattern?
**Difficulty:** Basic | **Topic:** Django Fundamentals

#### 1. One-Line Answer
Django is a high-level, batteries-included Python web framework following the **Model-View-Template (MVT)** design pattern for rapid, secure web development.

#### 2. Detailed Answer
Django's architecture modifies the classic Model-View-Controller (MVC) pattern into **Model-View-Template (MVT)**:
- **Model:** Represents the data layer and business domain models using Django's Object-Relational Mapper (ORM).
- **View:** Acts as the controller/handler; it accepts HTTP requests, invokes models/services, and selects the template or JSON data to return.
- **Template:** The presentation layer rendering dynamic HTML using the Django Template Language (DTL). The framework itself acts as the overall controller handling routing and dispatching.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def home_view(request: HttpRequest) -> HttpResponse:
    """Standard Django Function-Based View (FBV)."""
    context = {"greeting": "Namaste, Welcome to Django Architecture!"}
    return render(request, "home.html", context)
```
*A standard Django view receiving an `HttpRequest` instance and returning an `HttpResponse` rendered from a template.*

#### 4. Internal Working
When a request arrives, Django's `WSGIHandler` initializes an `HttpRequest` object, runs middleware `process_request` hooks, resolves the URL regex via `URLResolver`, and calls the matched view function.

#### 5. Real-World Use Case
Powering monolithic and decoupled architectures in enterprise portals (e.g. Swiggy delivery partner onboarding, TCS employee intranet).

#### 6. Interview Follow-Up Questions
- *How does MVT differ from MVC?* (In MVT, Django framework itself acts as the Controller).
- *What role does `urls.py` play in this pattern?* (It maps URL patterns to view callables).

#### 7. Common Interview Mistakes
- Confusing Django's View with the presentation UI (in Django, View is the business controller; Template is the UI).

#### 8. Interview Tip
State clearly: *"Django is an MVT framework where the framework itself is the controller, the View handles logic, and the Template handles rendering."*

#### 9. Related Concepts
- [Django Models and ORM](models-and-orm.md)
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Django Architecture Overview](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
</details>

---

### DJ-BAS-002: What is the Purpose of `manage.py` in a Django Project?
**Difficulty:** Basic | **Topic:** Project Layout

#### 1. One-Line Answer
`manage.py` is an auto-generated command-line utility wrapping `django-admin` that sets the `DJANGO_SETTINGS_MODULE` environment variable for project-specific commands.

#### 2. Detailed Answer
`manage.py` provides an entry point to run development servers (`runserver`), apply schema migrations (`migrate`, `makemigrations`), open database shells (`dbshell`), run test suites (`test`), and create administrative superusers (`createsuperuser`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```bash
# Running development server on specific IP and port
python manage.py runserver 0.0.0.0:8000

# Generating and applying database migrations
python manage.py makemigrations
python manage.py migrate
```

#### 4. Internal Working
`manage.py` calls `os.environ.setdefault('DJANGO_SETTINGS_MODULE', '<project>.settings')` and invokes `execute_from_command_line(sys.argv)`.

#### 5. Real-World Use Case
Local development automation and CI/CD deployment execution scripts.

#### 6. Interview Follow-Up Questions
- *What is the difference between `manage.py` and `django-admin`?* (`manage.py` automatically binds project settings; `django-admin` requires setting `--settings` manually).

#### 7. Common Interview Mistakes
- Modifying `manage.py` directly for production logic (it should remain untouched).

#### 8. Interview Tip
Mention that `manage.py` delegates to `django.core.management.execute_from_command_line`.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [django-admin and manage.py Documentation](https://docs.djangoproject.com/en/stable/ref/django-admin/)
</details>

---

### DJ-BAS-003: Explain the Structure and Purpose of `settings.py`
**Difficulty:** Basic | **Topic:** Configuration Management

#### 1. One-Line Answer
`settings.py` contains all runtime configurations for a Django installation, including installed applications, middleware stacks, database credentials, security keys, and internationalization settings.

#### 2. Detailed Answer
Key settings include:
- `SECRET_KEY`: Cryptographic salt for sessions, CSRF, and cryptographic signing.
- `DEBUG`: Boolean enabling verbose debug tracebacks (must be `False` in production).
- `ALLOWED_HOSTS`: List of valid domain/host names to defend against HTTP Host header attacks.
- `INSTALLED_APPS`: List of active Django applications and third-party modules.
- `MIDDLEWARE`: Ordered list of middleware classes executed during request/response cycles.
- `DATABASES`: Database connection engine, credentials, and pooling parameters.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security-critical production configuration
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-fallback")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1")
ALLOWED_HOSTS = ["api.example.com", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

#### 4. Internal Working
Django imports settings via `django.conf.settings`, which wraps settings in a lazy proxy `LazySettings` to prevent circular imports during startup.

#### 5. Real-World Use Case
Separating configurations between Development, Staging, and Production environments using environment variables or split settings files.

#### 6. Interview Follow-Up Questions
- *Why is running with `DEBUG = True` in production a critical vulnerability?* (Exposes environment variables, database credentials, and internal code in error tracebacks).

#### 7. Common Interview Mistakes
- Hardcoding `SECRET_KEY` or database credentials in version control.

#### 8. Interview Tip
Always mention Twelve-Factor App principles and loading secrets from environment variables.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Django Settings Reference](https://docs.djangoproject.com/en/stable/ref/settings/)
</details>

---

### DJ-BAS-004: What is a Django App vs a Django Project?
**Difficulty:** Basic | **Topic:** Project Architecture

#### 1. One-Line Answer
A **project** is an entire web application configuration containing settings, URLs, and middleware, while an **app** is a self-contained, reusable Python package providing a specific set of features.

#### 2. Detailed Answer
A project can contain multiple apps (e.g., `accounts`, `billing`, `orders`, `notifications`). A single app can be reused across different Django projects if designed with modular, decoupled dependencies.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```bash
# Create project container
django-admin startproject ecommerce_platform

# Create modular feature applications
cd ecommerce_platform
python manage.py startapp accounts
python manage.py startapp payments
```

#### 4. Internal Working
Every app contains an `apps.py` defining an `AppConfig` class registered in `settings.INSTALLED_APPS`. Django inspects each `AppConfig` on startup to register models, signals, and admin hooks.

#### 5. Real-World Use Case
In large enterprise codebases (e.g. Razorpay, CRED), services are divided into modular apps (`merchants`, `settlements`, `payouts`, `kyc`) under a shared project.

#### 6. Interview Follow-Up Questions
- *How does Django discover models in an app?* (By scanning `models.py` in all `INSTALLED_APPS`).

#### 7. Common Interview Mistakes
- Putting all domain logic into a single monolithic app instead of separating domain boundaries.

#### 8. Interview Tip
Use the analogy: *"A project is the house; apps are individual rooms like the kitchen, bedroom, and bathroom."*

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [Applications Overview](https://docs.djangoproject.com/en/stable/ref/applications/)
</details>

---

### DJ-BAS-005: Explain WSGI vs ASGI in Django
**Difficulty:** Basic | **Topic:** Web Server Gateway Interface

#### 1. One-Line Answer
**WSGI** is a synchronous Python gateway specification executing one thread per request, while **ASGI** is an asynchronous specification supporting async views, WebSockets, and long-lived connections.

#### 2. Detailed Answer
- **WSGI (`wsgi.py`):** Synchronous standard (PEP 3333). Powered by WSGI servers like Gunicorn or uWSGI.
- **ASGI (`asgi.py`):** Asynchronous standard introduced natively in Django 3.0+. Powered by ASGI servers like Uvicorn or Daphne, enabling `async def` views, background task dispatching, and WebSocket protocol handling.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
application = get_asgi_application()
```
*Running with an ASGI server:*
```bash
uvicorn myproject.asgi:application --workers 4 --port 8000
```

#### 4. Internal Working
WSGI handles request-response linearly using blocking I/O. ASGI uses Python's `asyncio` event loop and an async callable `application(scope, receive, send)` handling bidirectional message streams.

#### 5. Real-World Use Case
Using ASGI for live tracking notifications in Swiggy or Zomato while using WSGI for standard REST APIs.

#### 6. Interview Follow-Up Questions
- *Can you run synchronous views under ASGI?* (Yes, Django runs sync views inside threadpools via `sync_to_async`).

#### 7. Common Interview Mistakes
- Believing ASGI automatically makes ORM database queries asynchronous without using async ORM methods (`aquery`, `aget`).

#### 8. Interview Tip
Mention that Django 4.2+ added async ORM support, bridging the gap for pure ASGI pipelines.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [Django ASGI Documentation](https://docs.djangoproject.com/en/stable/howto/deployment/asgi/)
</details>

---

### DJ-BAS-006: What is the Purpose of `__init__.py` in Django Apps?
**Difficulty:** Basic | **Topic:** Python Packaging

#### 1. One-Line Answer
`__init__.py` marks a directory as a Python package, enabling Python to import modules and allowing Django to specify default app configurations.

#### 2. Detailed Answer
In Django apps, `__init__.py` historically declared `default_app_config` to customize application metadata. Since Django 3.2+, Django automatically detects subclasses of `AppConfig`, but `__init__.py` remains essential for Python package discovery and package-level initialization.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# myapp/__init__.py
# Optional package initialization, e.g. Celery app loading
from .celery import app as celery_app

__all__ = ("celery_app",)
```

#### 4. Internal Working
CPython interpreter requires `__init__.py` to treat directories containing submodules as packages in older specifications, and Django uses standard `importlib` to walk directories.

#### 5. Real-World Use Case
Importing Celery app on project initialization so shared tasks bind correctly.

#### 6. Interview Follow-Up Questions
- *What is `default_app_config` and is it still required?* (Deprecated in Django 3.2+; Django auto-discovers `AppConfig`).

#### 7. Common Interview Mistakes
- Deleting `__init__.py` leading to import failures in CI/CD environments.

#### 8. Interview Tip
Keep `__init__.py` clean and avoid heavy database imports to prevent circular dependency bugs.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [Python Package Documentation](https://docs.python.org/3/tutorial/modules.html#packages)
</details>

---

### DJ-BAS-007: What is the `HttpRequest` Object in Django?
**Difficulty:** Basic | **Topic:** Request Processing

#### 1. One-Line Answer
The `HttpRequest` object is instantiated by Django for every incoming HTTP call, containing request headers, query parameters, payload data, session information, and authenticated user state.

#### 2. Detailed Answer
Common attributes of `HttpRequest`:
- `request.method`: HTTP verb (`GET`, `POST`, `PUT`, `DELETE`).
- `request.GET`: QueryDict containing URL query parameters (`?key=val`).
- `request.POST`: QueryDict containing form submission data.
- `request.body`: Raw byte string of the request body (JSON, XML).
- `request.headers`: Case-insensitive dictionary of HTTP headers.
- `request.user`: Current `User` instance populated by `AuthenticationMiddleware`.
- `request.session`: Dictionary-like object representing the user's session.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.http import HttpRequest, JsonResponse

def order_status_view(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    order_id = request.GET.get("order_id")
    user = request.user
    
    return JsonResponse({
        "order_id": order_id,
        "authenticated": user.is_authenticated,
        "client_ip": request.META.get("REMOTE_ADDR")
    })
```

#### 4. Internal Working
Created in `WSGIHandler.get_response` from the WSGI `environ` dictionary using `WSGIRequest` (subclass of `HttpRequest`).

#### 5. Real-World Use Case
Extracting bearer tokens or API client IDs from `request.headers` in custom API views.

#### 6. Interview Follow-Up Questions
- *Why is `request.GET` a `QueryDict` instead of a standard Python `dict`?* (Because a URL can contain multiple values for the same key: `?tag=python&tag=django`).

#### 7. Common Interview Mistakes
- Modifying `request.POST` directly without calling `.copy()` (`QueryDict` is immutable by default).

#### 8. Interview Tip
Emphasize that `request.user` is added dynamically by `AuthenticationMiddleware`.

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [HttpRequest Objects Reference](https://docs.djangoproject.com/en/stable/ref/request-response/#httprequest-objects)
</details>

---

### DJ-BAS-008: What is the `HttpResponse` Object in Django?
**Difficulty:** Basic | **Topic:** Response Processing

#### 1. One-Line Answer
`HttpResponse` is the core object returned by Django views containing HTTP status code, headers, cookies, and the rendered content sent back to the client.

#### 2. Detailed Answer
Django provides specialized subclasses:
- `JsonResponse`: Serializes Python dicts/lists to JSON with `application/json` Content-Type.
- `HttpResponseRedirect` / `HttpResponsePermanentRedirect`: Status 302 and 301 redirects.
- `HttpResponseNotFound`: Status 404 response.
- `HttpResponseForbidden`: Status 403 response.
- `StreamingHttpResponse`: Streams response in chunks for large files.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.http import HttpResponse, JsonResponse

def plaintext_view(request):
    response = HttpResponse("Hello, World!", content_type="text/plain", status=200)
    response["X-Frame-Options"] = "DENY"
    response.set_cookie("visited", "true", max_age=3600, httponly=True)
    return response

def api_view(request):
    return JsonResponse({"status": "SUCCESS", "code": 200})
```

#### 4. Internal Working
`HttpResponse` implements an iterator protocol. When WSGI servers consume the response, they call `iter(response)` to write bytes across the socket.

#### 5. Real-World Use Case
Returning standardized JSON error contracts or setting secure, HTTP-only authentication cookies.

#### 6. Interview Follow-Up Questions
- *When should you use `StreamingHttpResponse` instead of `HttpResponse`?* (When generating multi-megabyte CSV/PDF exports or audio/video streams).

#### 7. Common Interview Mistakes
- Returning a raw Python `dict` or `str` from a view instead of wrapping it in an `HttpResponse`.

#### 8. Interview Tip
Always mention setting `httponly=True` and `secure=True` when setting cookies on an `HttpResponse`.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [HttpResponse Objects Reference](https://docs.djangoproject.com/en/stable/ref/request-response/#httpresponse-objects)
</details>

---

### DJ-BAS-009: What is the Role of `URLconf` and `urls.py` in Django?
**Difficulty:** Basic | **Topic:** URL Routing

#### 1. One-Line Answer
`URLconf` (URL configuration) maps incoming HTTP request URL paths to specific view callables using `path()` or `re_path()` functions.

#### 2. Detailed Answer
When a request arrives:
1. Django inspects `ROOT_URLCONF` in `settings.py`.
2. It evaluates `urlpatterns` sequentially from top to bottom.
3. The first pattern that matches extracts captured path parameters (e.g. `<int:user_id>`) and passes them as keyword arguments to the view.
4. If no pattern matches, an `Http404` exception is raised.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.urls import path, include
from . import views

urlpatterns = [
    path("orders/", views.order_list_view, name="order-list"),
    path("orders/<int:order_id>/", views.order_detail_view, name="order-detail"),
    path("api/v1/", include("api.urls")),
]
```

#### 4. Internal Working
Uses `django.urls.resolvers.URLResolver` which compiles path patterns into regular expressions and parses path converters (`int`, `str`, `slug`, `uuid`).

#### 5. Real-World Use Case
Designing clean, RESTful URL hierarchies for multi-tenant SaaS applications.

#### 6. Interview Follow-Up Questions
- *Why is using the `name` parameter in `path()` considered a best practice?* (Enables reverse URL resolution using `reverse()` or `{% url %}`, eliminating hardcoded URLs).

#### 7. Common Interview Mistakes
- Forgetting leading or trailing slashes according to `APPEND_SLASH` settings.

#### 8. Interview Tip
Highlight the advantage of path converters (`<int:id>`) over raw regex for type safety and automatic validation.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Django URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
</details>

---

### DJ-BAS-010: Explain the Difference Between `path()` and `re_path()`
**Difficulty:** Basic | **Topic:** URL Routing

#### 1. One-Line Answer
`path()` uses simplified path converters (`<str:username>`, `<int:id>`), while `re_path()` uses full regular expressions with named capturing groups (`(?P<id>[0-9]+)`).

#### 2. Detailed Answer
- `path()` is preferred for 95% of standard routes because it is cleaner, self-documenting, and automatically casts extracted parameters to Python types.
- `re_path()` is reserved for complex patterns that standard path converters cannot express (e.g. validating specific alphanumeric patterns, ISBN numbers, or optional route segments).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.urls import path, re_path
from . import views

urlpatterns = [
    # Clean path syntax with built-in converter
    path("article/<int:year>/<slug:slug>/", views.article_detail),
    
    # Complex regex pattern with re_path
    re_path(r"^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$", views.archive_view),
]
```

#### 4. Internal Working
`path()` maps converter tokens to registered `PathConverter` classes (e.g. `IntConverter` regex `[0-9]+` and `to_python` integer conversion).

#### 5. Real-World Use Case
Supporting legacy regex URL patterns during project refactoring.

#### 6. Interview Follow-Up Questions
- *Can you register a custom path converter?* (Yes, using `register_converter()`).

#### 7. Common Interview Mistakes
- Overcomplicating standard integer/string parameters with regex instead of using `path()`.

#### 8. Interview Tip
Show how custom path converters (`register_converter`) keep `urlpatterns` clean and DRY.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [Path Converters Documentation](https://docs.djangoproject.com/en/stable/topics/http/urls/#registering-custom-path-converters)
</details>

---

### DJ-BAS-011: What is the Purpose of `AppConfig` in `apps.py`?
**Difficulty:** Basic | **Topic:** Application Configuration

#### 1. One-Line Answer
`AppConfig` encapsulates application metadata, manages app initialization, and executes startup hooks (such as signal registration) via the `ready()` method.

#### 2. Detailed Answer
Every Django app generated via `startapp` contains an `apps.py` file with an `AppConfig` subclass. It defines:
- `name`: Full Python path to the application.
- `verbose_name`: Human-readable name used in the Django admin.
- `default_auto_field`: Default primary key field type (e.g. `BigAutoField`).
- `ready()`: Callback executed once by the Django application registry upon startup.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# myapp/apps.py
from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    verbose_name = "Merchant Payments & Settlements"

    def ready(self):
        # Register signal handlers on startup
        import payments.signals
```

#### 4. Internal Working
`django.apps.registry.Apps.populate()` imports all `AppConfig` instances, loads models, and invokes `.ready()` in topological order.

#### 5. Real-World Use Case
Connecting Django signals (like `post_save`) safely without triggering circular imports.

#### 6. Interview Follow-Up Questions
- *Why shouldn't you query database models inside `ready()`?* (Because migrations may not have run yet, and it can cause deadlocks during startup).

#### 7. Common Interview Mistakes
- Importing signals at the top of `models.py` instead of inside `AppConfig.ready()`.

#### 8. Interview Tip
Explain that `ready()` is called twice if the auto-reloader runs, so avoid side-effects like spawning threads.

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [AppConfig Documentation](https://docs.djangoproject.com/en/stable/ref/applications/#appconfig-objects)
</details>

---

### DJ-BAS-012: What Does the `reverse()` Function Do in Django?
**Difficulty:** Basic | **Topic:** URL Reversal

#### 1. One-Line Answer
`reverse()` returns the fully qualified URL path for a given view name and arguments, decoupling view logic from hardcoded URL strings.

#### 2. Detailed Answer
Hardcoding URLs (e.g., `"/users/profile/42/"`) makes code fragile. If the URL pattern changes in `urls.py`, hardcoded links break across views and templates.
`reverse()` looks up the URL pattern by its `name` attribute and generates the matching string dynamically.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse

def complete_checkout(request):
    # Process order...
    order_id = 98712
    # Generates: "/orders/detail/98712/"
    target_url = reverse("order-detail", kwargs={"order_id": order_id})
    return redirect(target_url)
```

#### 4. Internal Working
`reverse()` delegates to `django.urls.resolvers.get_resolver().reverse()`, which traverses the cached URL pattern regex tree in reverse.

#### 5. Real-World Use Case
Constructing redirect URLs or webhook return endpoints safely across development, staging, and production environments.

#### 6. Interview Follow-Up Questions
- *What is the template equivalent of `reverse()`?* (The `{% url 'name' arg1 %}` template tag).
- *What is `reverse_lazy()` and when is it required?* (Evaluated lazily; required in class-based view attributes like `success_url` before URLconf is loaded).

#### 7. Common Interview Mistakes
- Using `reverse()` in class-level attributes where URL patterns have not loaded yet (use `reverse_lazy()` instead).

#### 8. Interview Tip
Contrast `reverse()` (returns string path) with `redirect()` (returns `HttpResponseRedirect` object).

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Reverse Resolution of URLs](https://docs.djangoproject.com/en/stable/topics/http/urls/#reverse-resolution-of-urls)
</details>

---

### DJ-BAS-013: What is the Role of `django.contrib` Packages?
**Difficulty:** Basic | **Topic:** Django Fundamentals

#### 1. One-Line Answer
`django.contrib` contains official, built-in applications providing standard web capabilities like authentication, admin panels, sessions, messages, and static file handling.

#### 2. Detailed Answer
Standard `django.contrib` packages:
- `django.contrib.auth`: User models, password hashing, and permission systems.
- `django.contrib.admin`: Auto-generated CRUD administration interface.
- `django.contrib.contenttypes`: Generic foreign keys and framework introspection.
- `django.contrib.sessions`: Multi-backend session storage (DB, Cache, Signed Cookies).
- `django.contrib.messages`: Flash notifications displayed across page redirects.
- `django.contrib.staticfiles`: Static asset collection and management.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom apps
    "accounts",
    "orders",
]
```

#### 4. Internal Working
Each `django.contrib` module is an independent Django app containing models, migrations, views, and middleware that integrate seamlessly with the framework core.

#### 5. Real-World Use Case
Leveraging `django.contrib.admin` to give internal support and operations teams instant back-office tooling without custom frontend code.

#### 6. Interview Follow-Up Questions
- *Can you disable `django.contrib.admin` in an API-only service?* (Yes, remove it from `INSTALLED_APPS` and `urls.py` to reduce attack surface and memory).

#### 7. Common Interview Mistakes
- Modifying files inside `site-packages/django/contrib/` instead of overriding templates or extending models.

#### 8. Interview Tip
Mention that Django's "batteries-included" reputation stems directly from the robustness of `django.contrib`.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Django Contrib Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/)
</details>

---

### DJ-BAS-014: What is the Purpose of `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT`?
**Difficulty:** Basic | **Topic:** Static Assets

#### 1. One-Line Answer
`STATIC_URL` is the public URL prefix for assets; `STATICFILES_DIRS` defines development asset locations; `STATIC_ROOT` is the target deployment directory populated by `collectstatic`.

#### 2. Detailed Answer
- **`STATIC_URL`:** The public HTTP path browser requests (e.g., `"/static/"`).
- **`STATICFILES_DIRS`:** Additional local directories containing development assets (CSS, JS, images) outside app folders.
- **`STATIC_ROOT`:** The single absolute filesystem directory where Django copies all static files from apps and `STATICFILES_DIRS` when `python manage.py collectstatic` runs in production.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
STATIC_URL = "/static/"

# Development source folders
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "static",
]

# Production target destination for Nginx / WhiteNoise
STATIC_ROOT = BASE_DIR / "staticfiles"
```

#### 4. Internal Working
`collectstatic` iterates over configured `STATICFILES_FINDERS` (`FileSystemFinder`, `AppDirectoriesFinder`), copies files to `STATIC_ROOT`, and hashes filenames if using `ManifestStaticFilesStorage`.

#### 5. Real-World Use Case
Serving static assets via Nginx or AWS S3 and CloudFront in containerized Docker deployments.

#### 6. Interview Follow-Up Questions
- *Why shouldn't `STATIC_ROOT` and `STATICFILES_DIRS` point to the same directory?* (It causes circular copying and file overwrite errors during `collectstatic`).

#### 7. Common Interview Mistakes
- Running `runserver` in production expecting Django to serve static files efficiently (use Nginx or WhiteNoise).

#### 8. Interview Tip
Highlight WhiteNoise as the standard Python library for serving compressed, cache-controlled static files directly from Gunicorn/Uvicorn.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [Managing Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)
</details>

---

### DJ-BAS-015: What is the Difference Between Static Files and Media Files in Django?
**Difficulty:** Basic | **Topic:** Asset Management

#### 1. One-Line Answer
**Static files** are code-versioned assets created by developers (CSS, JS, logos), while **media files** are user-uploaded assets created at runtime (profile avatars, invoices, documents).

#### 2. Detailed Answer
| Property | Static Files | Media Files |
|---|---|---|
| **Created By** | Developers & UI designers | End-users / API consumers |
| **Storage Settings** | `STATIC_URL`, `STATIC_ROOT` | `MEDIA_URL`, `MEDIA_ROOT` |
| **Version Controlled** | Yes (committed in Git) | No (never committed in Git) |
| **Production Target** | CDN, Nginx, or WhiteNoise | Object Storage (AWS S3, Google Cloud Storage) |

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# models.py
from django.db import models

class UserProfile(models.Model):
    avatar = models.ImageField(upload_to="avatars/%Y/%m/")
```

#### 4. Internal Working
When a user uploads a file, Django's `FileUploadHandler` streams chunks to `MEDIA_ROOT` or an external S3 backend using `django-storages`.

#### 5. Real-World Use Case
Storing customer KYC documents and invoice PDFs securely in AWS S3 buckets with pre-signed access URLs.

#### 6. Interview Follow-Up Questions
- *Why is storing media files on local container disks an anti-pattern in Docker/Kubernetes?* (Containers are ephemeral; restarting a container deletes all uploaded files).

#### 7. Common Interview Mistakes
- Committing the `media/` directory into Git version control.

#### 8. Interview Tip
Mention security controls: never execute uploaded media files, and validate MIME types using `python-magic`.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [File Uploads Documentation](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)
</details>

---

### DJ-BAS-016: What is `APPEND_SLASH` in Django and How Does it Work?
**Difficulty:** Basic | **Topic:** URL Routing

#### 1. One-Line Answer
`APPEND_SLASH` is a boolean setting (default `True`) that causes Django to issue an HTTP 301/302 redirect with a trailing slash if an incoming URL does not match any URLconf pattern but would match with a slash appended.

#### 2. Detailed Answer
If a client requests `GET /api/v1/orders` and `urlpatterns` only defines `path('api/v1/orders/', ...)`, `CommonMiddleware` intercepts the 404, checks if adding a `/` yields a valid pattern, and redirects the client to `GET /api/v1/orders/`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
APPEND_SLASH = True  # Standard Django convention
```
*Client interaction:*
```
Request:  GET /dashboard
Response: HTTP 301 Moved Permanently -> Location: /dashboard/
Request:  GET /dashboard/
Response: HTTP 200 OK
```

#### 4. Internal Working
Implemented in `django.middleware.common.CommonMiddleware.process_response()`.

#### 5. Real-World Use Case
Ensuring canonical URLs for SEO and preventing duplicate content penalties.

#### 6. Interview Follow-Up Questions
- *What happens if a client sends a `POST` request without a trailing slash when `APPEND_SLASH = True`?* (The 301/302 redirect converts the `POST` to a `GET`, dropping the payload body; use 307 or disable `APPEND_SLASH` for APIs).

#### 7. Common Interview Mistakes
- Relying on `APPEND_SLASH` for REST APIs (API clients should send exact URLs).

#### 8. Interview Tip
Highlight that in REST APIs, trailing slash conventions should be strictly enforced to avoid lost POST payloads during redirects.

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [APPEND_SLASH Setting Reference](https://docs.djangoproject.com/en/stable/ref/settings/#append-slash)
</details>

---

### DJ-BAS-017: What is the Purpose of `CSRF_TRUSTED_ORIGINS` in Django 4.0+?
**Difficulty:** Basic | **Topic:** Security Configuration

#### 1. One-Line Answer
`CSRF_TRUSTED_ORIGINS` lists the complete hostnames (including protocol, e.g. `https://*.example.com`) authorized to send unsafe HTTP requests (POST, PUT, DELETE) across domains.

#### 2. Detailed Answer
Starting in Django 4.0, Django's CSRF verification checks the `Origin` header against `CSRF_TRUSTED_ORIGINS` for all cross-origin requests. If the Origin does not match, Django rejects the request with HTTP 403 Forbidden (`CSRF verification failed: Origin checking failed`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    "https://checkout.razorpay.com",
    "https://app.example.com",
    "https://*.example.com",
]
```

#### 4. Internal Working
`CsrfViewMiddleware` extracts the `Origin` header (or `Referer` if Origin is absent) and compares it against trusted scheme-and-domain tuples.

#### 5. Real-World Use Case
Allowing webhook callbacks from payment gateways (Razorpay, Cashfree) or separate Single-Page Applications (SPAs).

#### 6. Interview Follow-Up Questions
- *Why must entries in `CSRF_TRUSTED_ORIGINS` include the scheme (`https://`)?* (Django 4.0+ enforces scheme verification to prevent protocol downgrade attacks).

#### 7. Common Interview Mistakes
- Omitting `https://` in Django 4.0+ entries, causing CSRF validation to fail silently.

#### 8. Interview Tip
Explain that this was the most common breaking change encountered by teams upgrading from Django 3.2 to Django 4.x.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [CSRF Trusted Origins Reference](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins)
</details>

---

### DJ-BAS-018: Explain the Function of `django.contrib.messages`
**Difficulty:** Basic | **Topic:** User Notifications

#### 1. One-Line Answer
The messages framework provides temporary, single-use notifications stored in sessions or cookies that display to users on their subsequent request.

#### 2. Detailed Answer
When a user submits a form and is redirected (Post/Redirect/Get pattern), standard request-scoped data is lost. `messages` stores alert strings (with severity levels: `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`) in the session or signed cookie and purges them once rendered in a template.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.contrib import messages
from django.shortcuts import redirect, render

def update_profile(request):
    if request.method == "POST":
        # Save profile...
        messages.success(request, "Your profile was updated successfully!")
        return redirect("profile-view")
    return render(request, "profile.html")
```

#### 4. Internal Working
Uses `MessageMiddleware` and `django.contrib.messages.storage.fallback.FallbackStorage` (stores in signed cookies first, falling back to sessions if too large).

#### 5. Real-World Use Case
Displaying flash alerts ("Payment confirmed", "Invalid password") across HTTP redirects in server-rendered applications.

#### 6. Interview Follow-Up Questions
- *What is the Post/Redirect/Get (PRG) pattern?* (A design pattern preventing accidental duplicate form submissions on browser refresh).

#### 7. Common Interview Mistakes
- Storing massive binary data or sensitive tokens in the messages framework.

#### 8. Interview Tip
Mention that the messages framework supports customizable storage backends (SessionStorage, CookieStorage).

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [The Messages Framework](https://docs.djangoproject.com/en/stable/ref/contrib/messages/)
</details>

---

### DJ-BAS-019: What is `QueryDict` in Django?
**Difficulty:** Basic | **Topic:** Request Processing

#### 1. One-Line Answer
`QueryDict` is a dictionary-like subclass customized to handle multiple values for the same key, used by Django to parse HTTP GET and POST parameters.

#### 2. Detailed Answer
Standard Python dictionaries map each key to a single value. In HTTP query strings, a key can appear repeatedly (e.g. `?category=electronics&category=appliances`).
`QueryDict` stores values as lists internally:
- `qd["key"]` returns the *last* value.
- `qd.getlist("key")` returns a Python list of *all* values.
- `QueryDict` instances on `request.GET` and `request.POST` are immutable by default.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.http import QueryDict

qd = QueryDict("category=books&category=tech&page=1")
print(qd["category"])            # Outputs: 'tech' (last value)
print(qd.getlist("category"))    # Outputs: ['books', 'tech']

# Making mutable for modifications
mutable_qd = qd.copy()
mutable_qd["page"] = "2"
print(mutable_qd.urlencode())    # Outputs: 'category=books&category=tech&page=2'
```

#### 4. Internal Working
Subclasses `django.utils.datastructures.MultiValueDict`.

#### 5. Real-World Use Case
Handling multi-select filter checkboxes in e-commerce search APIs (e.g. Flipkart filter bars).

#### 6. Interview Follow-Up Questions
- *How do you mutate `request.POST` data?* (Call `request.POST.copy()` to obtain a mutable clone).

#### 7. Common Interview Mistakes
- Using `request.GET.get()` when multiple values are expected, inadvertently dropping all but the last parameter.

#### 8. Interview Tip
Mention `urlencode()` as the standard method to serialize `QueryDict` back into query string format.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [QueryDict Objects Reference](https://docs.djangoproject.com/en/stable/ref/request-response/#querydict-objects)
</details>

---

### DJ-BAS-020: What is the Purpose of `django-admin`?
**Difficulty:** Basic | **Topic:** CLI Tooling

#### 1. One-Line Answer
`django-admin` is Django's global command-line utility for administrative tasks like starting new projects and creating new applications before project settings exist.

#### 2. Detailed Answer
While `manage.py` is created inside a specific project, `django-admin` is installed globally in the Python environment. It provides commands like `startproject` to bootstrap new codebases and can execute any `manage.py` command if passed the `--settings` argument.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```bash
# Bootstrap new project directory
django-admin startproject my_fintech_app

# Check installed Django version
django-admin --version
```

#### 4. Internal Working
`django-admin` invokes `django.core.management.execute_from_command_line(sys.argv)`.

#### 5. Real-World Use Case
Project scaffolding and system-wide automation scripts in Docker base images.

#### 6. Interview Follow-Up Questions
- *How does `manage.py` invoke `django-admin` code?* (Both execute the same underlying `ManagementUtility` class).

#### 7. Common Interview Mistakes
- Running `django-admin runserver` without defining `DJANGO_SETTINGS_MODULE`.

#### 8. Interview Tip
Keep it simple: `django-admin` is global without context; `manage.py` is project-local and pre-configured.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [django-admin Reference](https://docs.djangoproject.com/en/stable/ref/django-admin/)
</details>

---

### DJ-BAS-021: What is the Difference Between `GET` and `POST` in Django Views?
**Difficulty:** Basic | **Topic:** Request Processing

#### 1. One-Line Answer
`GET` requests retrieve data without modifying server state (idempotent and safe), while `POST` requests submit data that modifies server state or creates database records.

#### 2. Detailed Answer
- **`GET`:** Parameters are visible in the URL query string (`request.GET`). Cached by browsers and proxies. Never used for destructive operations.
- **`POST`:** Parameters are transmitted in the HTTP request body (`request.POST`). Protected against CSRF in Django. Used for creating or modifying resources.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.shortcuts import render, redirect
from myapp.models import Item

def item_view(request):
    if request.method == "POST":
        # State-modifying operation
        name = request.POST.get("name")
        Item.objects.create(name=name)
        return redirect("item-list")
    
    # Safe read operation
    items = Item.objects.all()
    return render(request, "items.html", {"items": items})
```

#### 4. Internal Working
Django's `CsrfViewMiddleware` strictly checks CSRF tokens on `POST`, `PUT`, `PATCH`, and `DELETE`, but permits `GET` requests to pass through without token validation.

#### 5. Real-World Use Case
E-commerce search queries use `GET`; placing an order uses `POST`.

#### 6. Interview Follow-Up Questions
- *Why is executing state mutations in a GET request a critical vulnerability?* (Web crawlers, pre-fetchers, and CSRF attacks can trigger destructive changes automatically).

#### 7. Common Interview Mistakes
- Deleting database objects in a `GET` request endpoint.

#### 8. Interview Tip
State the HTTP RFC standards: `GET` is safe and idempotent; `POST` is non-idempotent.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Writing Views](https://docs.djangoproject.com/en/stable/topics/http/views/)
</details>

---

### DJ-BAS-022: What is the Purpose of `get_object_or_404()` in Django?
**Difficulty:** Basic | **Topic:** Views and Shortcuts

#### 1. One-Line Answer
`get_object_or_404()` is a shortcut that executes `get()` on a model or QuerySet, catching `DoesNotExist` and raising an `Http404` exception automatically.

#### 2. Detailed Answer
Without this shortcut, views must explicitly wrap model queries in `try...except Model.DoesNotExist` and return an `HttpResponseNotFound`.
`get_object_or_404()` provides clean, idiomatic error handling that integrates with Django's 404 handler templates.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.shortcuts import get_object_or_404, render
from myapp.models import Order

def order_detail(request, order_id: int):
    # Automatically raises Http404 if record does not exist
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/detail.html", {"order": order})
```

#### 4. Internal Working
```python
# Simplified Django implementation:
def get_object_or_404(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404(f"No {queryset.model._meta.object_name} matches the given query.")
```

#### 5. Real-World Use Case
Fetching user-scoped entities (orders, invoices) and preventing information disclosure if the resource ID is invalid.

#### 6. Interview Follow-Up Questions
- *What sister shortcut exists for QuerySets?* (`get_list_or_404()` returns a non-empty list or raises `Http404`).

#### 7. Common Interview Mistakes
- Calling `get_object_or_404()` without user ownership filtering, exposing other users' private records (IDOR vulnerability).

#### 8. Interview Tip
Always pass ownership filters (`user=request.user`) directly into `get_object_or_404()` to enforce authorization.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Django Shortcuts Reference](https://docs.djangoproject.com/en/stable/topics/http/shortcuts/#get-object-or-404)
</details>

---

### DJ-BAS-023: What Does `DEFAULT_AUTO_FIELD` Do in Django 3.2+?
**Difficulty:** Basic | **Topic:** Configuration Management

#### 1. One-Line Answer
`DEFAULT_AUTO_FIELD` configures the default primary key field type (`BigAutoField` 64-bit vs `AutoField` 32-bit) used for models that do not define an explicit primary key.

#### 2. Detailed Answer
Prior to Django 3.2, primary keys defaulted to `models.AutoField` (32-bit signed integer, maximum 2.14 billion rows). High-scale databases frequently exhausted this range, crashing production tables.
Django 3.2 introduced `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` (64-bit integer, maximum 9.22 quintillion rows).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# models.py - Automatically receives a 64-bit BigAutoField 'id' column
class Transaction(models.Model):
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2)
```

#### 4. Internal Working
When a model class is created by metaclass `ModelBase`, Django checks if any field has `primary_key=True`. If not, it instantiates the class referenced in `DEFAULT_AUTO_FIELD`.

#### 5. Real-World Use Case
Preventing integer overflow on high-velocity audit logs, clickstream events, and payment ledger tables.

#### 6. Interview Follow-Up Questions
- *Can you override `DEFAULT_AUTO_FIELD` on a per-app basis?* (Yes, in `apps.py` on the `AppConfig` class).

#### 7. Common Interview Mistakes
- Omitting `DEFAULT_AUTO_FIELD` in older projects, causing noisy migration generation warnings across dependencies.

#### 8. Interview Tip
Mention that 64-bit integers take 8 bytes instead of 4 bytes, a trivial cost for the safety of never running out of IDs.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Default Auto Field Documentation](https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field)
</details>

---

### DJ-BAS-024: What is the Purpose of `django.core.exceptions.ImproperlyConfigured`?
**Difficulty:** Basic | **Topic:** Exception Handling

#### 1. One-Line Answer
`ImproperlyConfigured` is raised by Django on startup when required settings are missing, mutually incompatible, or improperly formatted.

#### 2. Detailed Answer
Django uses fail-fast principles on startup. If an essential configuration (such as database credentials, missing template engines, or an invalid middleware path) is missing, Django raises `ImproperlyConfigured` immediately rather than failing mid-request in production.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name: str) -> str:
    """Fail-fast environment variable getter."""
    try:
        return os.environ[var_name]
    except KeyError:
        raise ImproperlyConfigured(f"Mandatory environment variable '{var_name}' is not set.")

# In settings.py:
DATABASE_PASSWORD = get_env_variable("PROD_DB_PASSWORD")
```

#### 4. Internal Working
Inherits from standard `Exception` and is raised by core components during system check frameworks (`manage.py check`).

#### 5. Real-World Use Case
Validating mandatory third-party credentials (AWS keys, Razorpay secrets) before the web server begins accepting traffic.

#### 6. Interview Follow-Up Questions
- *How does the Django System Check Framework work?* (Executes registered check functions to inspect models, admin, and settings for configuration errors).

#### 7. Common Interview Mistakes
- Allowing missing secrets to fall back to empty strings silently instead of raising `ImproperlyConfigured`.

#### 8. Interview Tip
Mention the Twelve-Factor App principle: applications must fail immediately if mandatory configurations are absent.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [Django Core Exceptions](https://docs.djangoproject.com/en/stable/ref/exceptions/#improperlyconfigured)
</details>

---

### DJ-BAS-025: How Does Django Locate Template Files?
**Difficulty:** Basic | **Topic:** Templates

#### 1. One-Line Answer
Django locates templates using loaders specified in `TEMPLATES['OPTIONS']['loaders']`, primarily `filesystem.Loader` (configured in `DIRS`) and `app_directories.Loader` (searching `templates/` folders inside `INSTALLED_APPS`).

#### 2. Detailed Answer
In `settings.py`, the `TEMPLATES` configuration defines:
- **`DIRS`:** Absolute paths to global project-level template folders.
- **`APP_DIRS = True`:** Enables `app_directories.Loader`, causing Django to automatically inspect `<app>/templates/` for every active app in `INSTALLED_APPS`.
- When resolving a template, Django searches directories in sequential order, returning the first matching filename.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]
```

#### 4. Internal Working
Uses `django.template.loaders.cached.Loader` in production to cache compiled template trees in RAM, avoiding disk reads on every request.

#### 5. Real-World Use Case
Namespacing templates (`orders/templates/orders/detail.html`) to prevent one app's template from unintentionally overriding another app's template.

#### 6. Interview Follow-Up Questions
- *Why should app templates be placed in `<app>/templates/<app>/name.html` instead of `<app>/templates/name.html`?* (Template namespacing prevents collision when multiple apps have templates named `list.html` or `detail.html`).

#### 7. Common Interview Mistakes
- Forgetting to namespace templates, leading to unpredictable template rendering order.

#### 8. Interview Tip
Always mention template namespacing as a sign of architectural maturity in Django.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Django Template Configuration](https://docs.djangoproject.com/en/stable/ref/settings/#templates)
</details>

---

## Intermediate Level

### DJ-INT-001: Explain the Django Request-Response Lifecycle in Complete Sequence
**Difficulty:** Intermediate | **Topic:** Architecture & Internals

#### 1. One-Line Answer
The request enters via WSGI/ASGI, wraps into `WSGIRequest`, flows through middleware `process_request` hooks, resolves URLs via `URLResolver`, executes view and ORM logic, passes through response middleware, and returns as HTTP bytes.

#### 2. Detailed Answer
1. **Socket Ingestion:** Web server (Nginx -> Gunicorn) receives HTTP request and passes environment dictionary to `WSGIHandler.__call__()`.
2. **Request Construction:** `WSGIHandler` instantiates `WSGIRequest(environ)`.
3. **Middleware Inbound:** The request traverses the middleware chain in top-to-bottom order (`SecurityMiddleware`, `SessionMiddleware`, `AuthenticationMiddleware`, `CsrfViewMiddleware`).
4. **URL Resolution:** `URLResolver` matches `request.path_info` against `urlpatterns`.
5. **View Execution:** Middleware `process_view` hooks execute, followed by the view callable returning an `HttpResponse`.
6. **Exception Handling:** If an unhandled exception occurs, `process_exception` hooks or standard error handlers (`handler500`, `handler404`) fire.
7. **Middleware Outbound:** The response flows through middleware in reverse order (bottom-to-top) executing `process_response` (setting cookies and security headers).
8. **Socket Transmission:** WSGI handler yields response bytes back to the server socket.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Conceptual representation of Django middleware stack execution
class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Inbound phase (Before View)
        print(f"Inbound Request: {request.path}")
        
        response = self.get_response(request) # Calls next middleware or View
        
        # 2. Outbound phase (After View)
        print(f"Outbound Response Status: {response.status_code}")
        return response
```

#### 4. Internal Working
`BaseHandler.load_middleware()` builds an "onion-like" nested callable chain using Python closures.

#### 5. Real-World Use Case
Tracing latency bottlenecks by injecting APM tracers (Datadog, OpenTelemetry) at the top of the middleware stack.

#### 6. Interview Follow-Up Questions
- *What happens if an early middleware returns an `HttpResponse` immediately?* (Execution short-circuits: subsequent middleware and the view are bypassed; response flows straight back up).

#### 7. Common Interview Mistakes
- Believing URL resolution happens before middleware (Session and Security middleware execute *before* URL resolution).

#### 8. Interview Tip
Draw or describe the "Onion Architecture" of Django middleware to demonstrate senior understanding.

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [Django Request-Response Cycle](https://docs.djangoproject.com/en/stable/ref/request-response/)
</details>

---

### DJ-INT-002: How Does Django's System Check Framework Function?
**Difficulty:** Intermediate | **Topic:** Framework Internals

#### 1. One-Line Answer
The System Check Framework executes static inspection checks across models, admin, databases, and security configurations on startup, raising `Warning` or `Error` objects to catch misconfigurations before deployment.

#### 2. Detailed Answer
Executed via `manage.py check`, the check framework runs registered validation functions tagged with categories (`models`, `security`, `database`, `admin`, `signals`).
- **`CheckMessage.DEBUG` / `INFO`:** Informational.
- **`CheckMessage.WARNING`:** Potential problem, but allows execution.
- **`CheckMessage.ERROR`:** Severe problem; prevents `runserver` or `migrate` from proceeding.
- **`CheckMessage.CRITICAL`:** Fatal framework failure.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.core.checks import Error, register, Tags

@register(Tags.security)
def check_production_secret_key(app_configs, **kwargs):
    from django.conf import settings
    errors = []
    if not settings.DEBUG and settings.SECRET_KEY == "insecure-dev-key":
        errors.append(
            Error(
                "Production SECRET_KEY cannot be set to insecure default!",
                id="my_security.E001",
                hint="Set the DJANGO_SECRET_KEY environment variable.",
            )
        )
    return errors
```

#### 4. Internal Working
Uses `django.core.checks.registry.registry.run_checks()` to aggregate messages.

#### 5. Real-World Use Case
Running `python manage.py check --deploy` in CI/CD pipelines to block deployments with security misconfigurations (e.g. `SECURE_SSL_REDIRECT = False`).

#### 6. Interview Follow-Up Questions
- *What does `python manage.py check --deploy` inspect?* (HSTS headers, secure cookies, SSL redirect, and debug status).

#### 7. Common Interview Mistakes
- Bypassing check failures with `--silenced-checks` without understanding the security implications.

#### 8. Interview Tip
Mention writing custom system checks in large enterprise teams to enforce internal architectural rules.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [System Check Framework](https://docs.djangoproject.com/en/stable/topics/checks/)
</details>

---

### DJ-INT-003: How to Manage Multi-Environment Settings Cleanly in Django?
**Difficulty:** Intermediate | **Topic:** Configuration Architecture

#### 1. One-Line Answer
Use a split-settings directory structure (`base.py`, `development.py`, `production.py`) combined with environment variables for secrets, adhering to Twelve-Factor principles.

#### 2. Detailed Answer
Replace the single `settings.py` file with a `settings/` package:
- `base.py`: Shared configurations (INSTALLED_APPS, MIDDLEWARE, TEMPLATES).
- `development.py`: `DEBUG = True`, SQLite/local PostgreSQL, Console email backend, relaxed CORS.
- `production.py`: `DEBUG = False`, connection pooling, S3 storage, Redis caching, strict security headers.
Secrets are read from environment variables using `django-environ` or `decouple`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/base.py
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# settings/production.py
import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
```

#### 4. Internal Working
Deployment commands set `DJANGO_SETTINGS_MODULE=myproject.settings.production`.

#### 5. Real-World Use Case
Deploying separate staging and production ECS/Kubernetes containers from the same Git branch without changing code.

#### 6. Interview Follow-Up Questions
- *Why is using `from .base import *` controversial, and how do modern tools solve it?* (Namespace pollution; modern approaches use pure environment variables with a single settings file).

#### 7. Common Interview Mistakes
- Committing separate `settings_prod.py` files with production passwords in plain text.

#### 8. Interview Tip
Mention that modern best practices favor a **single `settings.py` parameterized entirely by environment variables**.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [Twelve-Factor App: Config](https://12factor.net/config)
</details>

---

### DJ-INT-004: How Does Django Handle Custom Context Processors?
**Difficulty:** Intermediate | **Topic:** Templates

#### 1. One-Line Answer
A context processor is a Python function taking an `HttpRequest` and returning a dictionary of variables automatically merged into every template rendered via `RequestContext`.

#### 2. Detailed Answer
Standard context processors inject user auth (`request.user`), messages, and debug state into all templates.
Custom context processors allow developers to inject site-wide metadata (e.g. current year, feature flags, global currency settings, shopping cart count) without passing them manually in every view's context dictionary.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# core/context_processors.py
from django.conf import settings

def global_ecommerce_context(request):
    """Injects business context into every template."""
    return {
        "SUPPORT_PHONE": "+91 80 1234 5678",
        "CURRENCY_SYMBOL": "₹",
        "APP_VERSION": getattr(settings, "APP_VERSION", "1.0.0"),
        "CART_COUNT": request.session.get("cart_count", 0),
    }

# settings.py
TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            # ... standard processors ...
            "core.context_processors.global_ecommerce_context",
        ]
    }
}]
```

#### 4. Internal Working
`django.template.context.RequestContext` calls each registered context processor callable sequentially and updates its internal context dictionary before rendering.

#### 5. Real-World Use Case
Injecting current tenant metadata or active theme preferences in multi-tenant SaaS dashboards.

#### 6. Interview Follow-Up Questions
- *What is the performance danger of heavy queries inside context processors?* (Because they run on **every single template render**, a slow database query inside a context processor degrades response time across the entire site).

#### 7. Common Interview Mistakes
- Executing un-cached, heavy database queries inside context processors.

#### 8. Interview Tip
Emphasize caching: *"Context processors must remain ultra-lightweight; always cache database lookups inside them."*

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Context Processors Documentation](https://docs.djangoproject.com/en/stable/ref/templates/api/#writing-your-own-context-processors)
</details>

---

### DJ-INT-005: Explain How Django Handles File Upload Handlers
**Difficulty:** Intermediate | **Topic:** File Management

#### 1. One-Line Answer
Django uses a chain of file upload handlers (`MemoryFileUploadHandler` and `TemporaryFileUploadHandler`) to stream uploads into RAM or disk based on `FILE_UPLOAD_MAX_MEMORY_SIZE`.

#### 2. Detailed Answer
When a file is uploaded:
1. If the file size is below `FILE_UPLOAD_MAX_MEMORY_SIZE` (default 2.5 MB), Django's `MemoryFileUploadHandler` keeps the entire file in an in-memory `InMemoryUploadedFile`.
2. If file size exceeds 2.5 MB, Django delegates to `TemporaryFileUploadHandler`, streaming chunks to a temporary file on disk (`TemporaryUploadedFile`).
3. This prevents large file uploads (e.g. 500 MB videos) from causing server Out-Of-Memory (OOM) crashes.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
# Uploads up to 10MB stay in RAM; larger stream to disk
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# views.py
from django.http import HttpResponse

def upload_view(request):
    if request.method == "POST" and request.FILES.get("document"):
        uploaded_file = request.FILES["document"]
        # Reads in 64KB chunks to maintain flat memory profile
        for chunk in uploaded_file.chunks(chunk_size=65536):
            # Process or stream chunk to S3
            pass
        return HttpResponse("Uploaded successfully")
```

#### 4. Internal Working
Uses `django.core.files.uploadhandler.FileUploadHandler` hooks: `new_file()`, `receive_data_chunk()`, and `file_complete()`.

#### 5. Real-World Use Case
Handling KYC document and invoice uploads in FinTech applications.

#### 6. Interview Follow-Up Questions
- *Can you write a custom upload handler to stream uploads directly to S3 without hitting local disk?* (Yes, by implementing a custom `FileUploadHandler`).

#### 7. Common Interview Mistakes
- Calling `uploaded_file.read()` on large files, defeating the streaming architecture and loading the entire file into RAM.

#### 8. Interview Tip
Mention using `.chunks()` when reading uploaded files to prevent memory spikes.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [File Upload Handlers](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/#upload-handlers)
</details>

---

### DJ-INT-006: What is the Purpose of `django.utils.functional.cached_property`?
**Difficulty:** Intermediate | **Topic:** Performance & Internals

#### 1. One-Line Answer
`cached_property` transforms a class method into a property whose return value is computed once and cached on the instance as a normal attribute for its entire lifespan.

#### 2. Detailed Answer
Standard `@property` decorators recompute their logic on every attribute access.
`@cached_property` computes the result on the first call, writes the value directly into the instance's `__dict__`, and on subsequent accesses, Python's attribute lookup finds the value in `__dict__` without invoking the method again.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.utils.functional import cached_property
from myapp.models import Order

class Customer:
    def __init__(self, customer_id: int):
        self.customer_id = customer_id

    @cached_property
    def total_lifetime_spend_inr(self) -> float:
        """Expensive database aggregation computed exactly once per instance."""
        orders = Order.objects.filter(customer_id=self.customer_id)
        return sum(order.total_amount for order in orders)

# Usage:
cust = Customer(42)
print(cust.total_lifetime_spend_inr)  # Executes DB query
print(cust.total_lifetime_spend_inr)  # Instant lookup from __dict__ (0 DB queries)
```

#### 4. Internal Working
Implements the non-data descriptor protocol:
```python
class cached_property:
    def __init__(self, func):
        self.func = func
    def __get__(self, instance, cls=None):
        if instance is None: return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res
```

#### 5. Real-World Use Case
Caching parsed permission trees or complex calculations on Django models within the scope of a single HTTP request.

#### 6. Interview Follow-Up Questions
- *How do you invalidate a `@cached_property` on an instance?* (Delete the attribute from instance `__dict__`: `del instance.attribute_name`).

#### 7. Common Interview Mistakes
- Assuming `@cached_property` caches values across different HTTP requests or processes (it only caches on that specific in-memory object instance).

#### 8. Interview Tip
Compare `@cached_property` to `functools.cached_property` (standard in Python 3.8+).

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [cached_property Documentation](https://docs.djangoproject.com/en/stable/ref/utils/#django.utils.functional.cached_property)
</details>

---

### DJ-INT-007: How Does Django Support Internationalization (i18n) and Localization (l10n)?
**Difficulty:** Intermediate | **Topic:** Internationalization

#### 1. One-Line Answer
Django uses GNU `gettext` for text translation (`gettext_lazy`, `_()`), locale middleware (`LocaleMiddleware`), and translation catalogs (`.po` / `.mo` files) to format numbers, dates, and text per user locale.

#### 2. Detailed Answer
- **`i18n` (Internationalization):** Writing code with translation hooks (`gettext_lazy("_('Welcome')")`) and activating `LocaleMiddleware`.
- **`l10n` (Localization):** Formatting dates, currencies, and numbers according to local conventions (e.g. `₹ 1,00,000.00` in Indian numbering vs `$ 100,000.00` in US).
- Translations are extracted via `django-admin makemessages` into `.po` files and compiled into binary `.mo` files via `django-admin compilemessages`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.utils.translation import gettext_lazy as _
from django.db import models

class Product(models.Model):
    # Translated in admin and forms lazily
    title = models.CharField(max_length=200, verbose_name=_("Product Title"))
    description = models.TextField(verbose_name=_("Product Description"))
```

#### 4. Internal Working
`LocaleMiddleware` inspects: 1) URL language prefix (`/en/`, `/hi/`), 2) Session language, 3) Cookie language, 4) HTTP `Accept-Language` header, and activates the matching thread-local translation catalog.

#### 5. Real-World Use Case
Supporting regional Indian languages (Hindi, Tamil, Telugu, Kannada) on e-commerce platforms like Meesho or JioMart.

#### 6. Interview Follow-Up Questions
- *Why must you use `gettext_lazy` instead of `gettext` in model definitions?* (Models are evaluated on application startup before user request locales are known; lazy evaluation translates at rendering time).

#### 7. Common Interview Mistakes
- Using eager `gettext` in models or class attributes, causing text to be frozen in the server's default language.

#### 8. Interview Tip
Always emphasize the distinction between eager `gettext` (in view functions) and lazy `gettext_lazy` (in models, forms, and global declarations).

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Translation in Django](https://docs.djangoproject.com/en/stable/topics/i18n/translation/)
</details>

---

### DJ-INT-008: What is `django.utils.timezone` and Why Should You Never Use `datetime.now()`?
**Difficulty:** Intermediate | **Topic:** Timezone Handling

#### 1. One-Line Answer
`django.utils.timezone.now()` returns aware UTC datetimes conforming to `USE_TZ = True`, whereas naive `datetime.now()` lacks timezone awareness and causes silent database corruption across daylight savings and server migrations.

#### 2. Detailed Answer
When `USE_TZ = True` in `settings.py`:
- Django stores all timestamps in the database in **UTC**.
- `timezone.now()` creates timezone-aware datetimes (`datetime(..., tzinfo=ZoneInfo("UTC"))`).
- When templates or forms render, Django automatically converts UTC timestamps into the user's active timezone (e.g. `Asia/Kolkata` / IST).
- Naive datetimes from `datetime.now()` trigger runtime `RuntimeWarning: DateTimeField received a naive datetime` and corrupt historical comparisons.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from datetime import datetime
from django.utils import timezone

# BAD: Naive datetime without timezone awareness
bad_timestamp = datetime.now()

# GOOD: Timezone-aware UTC datetime
good_timestamp = timezone.now()

# Convert to specific business timezone (e.g. IST for Indian accounting)
import zoneinfo
ist_time = timezone.localtime(good_timestamp, zoneinfo.ZoneInfo("Asia/Kolkata"))
```

#### 4. Internal Working
Django uses Python 3.9+ `zoneinfo` under the hood to manage aware datetimes and database adapter conversions.

#### 5. Real-World Use Case
Generating accurate midnight-to-midnight GST invoices in Indian Standard Time (IST) while storing UTC records.

#### 6. Interview Follow-Up Questions
- *How does PostgreSQL store timezone-aware timestamps?* (Using `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`)).

#### 7. Common Interview Mistakes
- Comparing a naive datetime with an aware datetime (raises `TypeError: can't compare offset-naive and offset-aware datetimes`).

#### 8. Interview Tip
Rule of thumb: *"Store in UTC, display in local time."*

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Timezones in Django](https://docs.djangoproject.com/en/stable/topics/i18n/timezones/)
</details>

---

### DJ-INT-009: Explain the Purpose of the `Sites` Framework (`django.contrib.sites`)
**Difficulty:** Intermediate | **Topic:** Multi-Domain Architecture

#### 1. One-Line Answer
The `Sites` framework associates database records with specific domain names, allowing a single Django installation and database to serve multiple distinct websites.

#### 2. Detailed Answer
Configured via `SITE_ID = 1` in `settings.py` and the `django.contrib.sites` app:
- A `Site` model stores `(id, domain, name)`.
- Models link to `Site` via a `ForeignKey` to partition content per domain.
- Utilities like `Site.objects.get_current()` return the active domain for building absolute URLs in outgoing transactional emails and password resets.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site

def send_invitation_email(request, user):
    current_site = get_current_site(request)
    domain = current_site.domain  # e.g. "portal.example.in" or "enterprise.example.com"
    invite_url = f"https://{domain}/accept-invite/{user.token}/"
```

#### 4. Internal Working
Uses `CurrentSiteMiddleware` to evaluate domain names dynamically from the `Host` header if `SITE_ID` is not hardcoded.

#### 5. Real-World Use Case
Running both B2C and B2B storefronts on the same codebase and database with distinct branding.

#### 6. Interview Follow-Up Questions
- *What is the difference between `Site.objects.get_current()` and `get_current_site(request)`?* (`get_current_site` falls back to the HTTP `Host` header if `SITE_ID` isn't fixed).

#### 7. Common Interview Mistakes
- Forgetting to update the default `example.com` domain in the database after deployment.

#### 8. Interview Tip
Mention how the Sites framework powers multi-tenant email links and sitemap generators.

#### 9. Related Concepts
- [Django Fundamentals](fundamentals.md)

#### 10. References
- [The "sites" Framework](https://docs.djangoproject.com/en/stable/ref/contrib/sites/)
</details>

---

### DJ-INT-010: How Does Django Handle Custom Model Managers?
**Difficulty:** Intermediate | **Topic:** ORM Architecture

#### 1. One-Line Answer
A custom `models.Manager` encapsulates table-level query logic, providing domain-specific QuerySet helper methods and custom base query filtering.

#### 2. Detailed Answer
Models default to `objects = models.Manager()`. Custom managers allow:
1. **Modifying the base QuerySet:** E.g. a `SoftDeleteManager` that filters out `is_deleted=True` automatically.
2. **Adding domain query methods:** E.g. `Order.objects.pending()`, `User.objects.active_subscribers()`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import models

class ActiveUserManager(models.Manager):
    def get_queryset(self):
        # Automatically excludes deactivated users from all queries
        return super().get_queryset().filter(is_active=True)

    def verified(self):
        return self.get_queryset().filter(is_email_verified=True)

class AppUser(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    # Custom manager
    objects = ActiveUserManager()
    # Unfiltered manager for admin / background audits
    all_objects = models.Manager()
```

#### 4. Internal Working
When `AppUser.objects.filter()` is called, the manager creates a fresh `QuerySet` instance bound to the model and passes parameters to it.

#### 5. Real-World Use Case
Implementing transparent soft-deletions and multi-tenant organization scoping.

#### 6. Interview Follow-Up Questions
- *How can you chain custom manager methods?* (Define a custom `models.QuerySet` and call `as_manager()`).

#### 7. Common Interview Mistakes
- Modifying the base QuerySet on the default manager without providing a fallback unfiltered manager for administrative operations.

#### 8. Interview Tip
Recommend `QuerySet.as_manager()` over subclassing `models.Manager` directly to enable method chaining.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Custom Managers](https://docs.djangoproject.com/en/stable/topics/db/managers/)
</details>

---

### DJ-INT-011: What is the Purpose of `django.core.signing`?
**Difficulty:** Intermediate | **Topic:** Cryptography & Security

#### 1. One-Line Answer
`django.core.signing` provides cryptographic signing utilities to generate tamper-proof signed strings and timestamps using HMAC-SHA256 and `SECRET_KEY`.

#### 2. Detailed Answer
Used to send data to untrusted environments (e.g. query parameters in email verification links, password reset tokens, signed cookies) without database storage.
If a malicious user tampers with the signed token, verification fails and raises `BadSignature` or `SignatureExpired`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.core import signing

# 1. Sign data with an expiration timestamp
payload = {"user_id": 1042, "action": "verify_email"}
token = signing.dumps(payload, salt="email-verification")

# 2. Verify and decode token with a 48-hour max age
try:
    data = signing.loads(token, salt="email-verification", max_age=172800)
    print(f"Verified user: {data['user_id']}")
except signing.SignatureExpired:
    print("Token has expired! Please request a new one.")
except signing.BadSignature:
    print("Tampered token detected! Security alert logged.")
```

#### 4. Internal Working
Uses `hmac` with SHA256 and base64 URL-safe encoding, concatenating payload and signature with a colon separator.

#### 5. Real-World Use Case
Stateless email verification tokens and unsubscribe links that require no database rows.

#### 6. Interview Follow-Up Questions
- *Does `signing.dumps()` encrypt the data?* (No! It signs the data for integrity; the payload is only base64-encoded and can be read by anyone unless explicitly encrypted).

#### 7. Common Interview Mistakes
- Confusing cryptographic signing (tamper detection) with encryption (confidentiality).

#### 8. Interview Tip
Always mention `TimestampSigner` and enforcing `max_age` on verification tokens.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Cryptographic Signing Documentation](https://docs.djangoproject.com/en/stable/topics/signing/)
</details>

---

### DJ-INT-012: How Does Django Support Database Routing?
**Difficulty:** Intermediate | **Topic:** Database Architecture

#### 1. One-Line Answer
Database routers define rules controlling which database executes read, write, relation, and migration operations across multiple database configurations.

#### 2. Detailed Answer
Configured via `DATABASE_ROUTERS = ['path.to.Router']`, a router class implements four methods:
- `db_for_read(model, **hints)`: Returns database alias for read queries.
- `db_for_write(model, **hints)`: Returns database alias for write queries.
- `allow_relation(obj1, obj2, **hints)`: Determines whether relationships between objects across databases are allowed.
- `allow_migrate(db, app_label, **hints)`: Controls whether an app's migrations run on a specific database.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# routers.py
class PrimaryReplicaRouter:
    """Routes writes to primary and reads to read-replicas."""
    def db_for_read(self, model, **hints):
        return "replica"  # Read-only replica database

    def db_for_write(self, model, **hints):
        return "default"  # Primary read-write database

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        return db == "default"
```

#### 4. Internal Working
Django's ORM consults the router chain sequentially when compiling SQL compilers for QuerySets.

#### 5. Real-World Use Case
Offloading heavy read traffic (analytics, reporting, catalog browsing) to Amazon RDS read-replicas while reserving the primary for transactions.

#### 6. Interview Follow-Up Questions
- *What is replication lag and how does it cause read-your-own-writes inconsistency?* (If a user writes to primary and immediately reads from replica before replication completes, new data is missing).

#### 7. Common Interview Mistakes
- Allowing migrations to run against read-replicas, causing deployment failures.

#### 8. Interview Tip
Explain pinning reads to the primary database for 5 seconds after a user write to prevent replication lag anomalies.

#### 9. Related Concepts
- [Caching and Performance](caching-and-performance.md)

#### 10. References
- [Multiple Databases in Django](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
</details>

---

### DJ-INT-013: What is the Purpose of `select_related()` vs `prefetch_related()`?
**Difficulty:** Intermediate | **Topic:** ORM Optimization

#### 1. One-Line Answer
`select_related()` executes a SQL `JOIN` in a single query for single-valued relationships, while `prefetch_related()` executes separate SQL `IN` queries and joins in Python memory for multi-valued relationships.

#### 2. Detailed Answer
- **`select_related`:** Best for `ForeignKey` and `OneToOneField`. Creates an SQL `INNER JOIN` or `LEFT OUTER JOIN`. Eliminates N+1 queries in a single database round-trip.
- **`prefetch_related`:** Best for `ManyToManyField` and reverse `ForeignKey` (1-to-many). Executes 2 queries: one for primary objects and one for related objects (`WHERE id IN (...)`), stitching them together in Python memory.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# 1. select_related for single-valued ForeignKey: Exactly 1 SQL query with JOIN
orders = Order.objects.select_related("customer", "shipping_address").all()
for o in orders:
    print(o.customer.name)  # 0 additional queries!

# 2. prefetch_related for ManyToMany: Exactly 2 SQL queries
orders = Order.objects.prefetch_related("items__product").all()
for o in orders:
    for item in o.items.all():  # 0 additional queries!
        print(item.product.name)
```

#### 4. Internal Working
`select_related` modifies the SQL `SELECT` clause to include related table columns. `prefetch_related` instances populate Django's `_prefetched_objects_cache` dictionary on each model.

#### 5. Real-World Use Case
Eliminating N+1 queries in e-commerce checkout APIs, dropping endpoint latency from 4.2 seconds to 45 milliseconds.

#### 6. Interview Follow-Up Questions
- *Can you filter a prefetch?* (Yes, using the `Prefetch()` object with a custom `queryset`).

#### 7. Common Interview Mistakes
- Using `select_related` on a `ManyToManyField` (Django raises a runtime error).

#### 8. Interview Tip
The golden rule: *"Single relationship -> `select_related` (SQL JOIN); Multiple relationship -> `prefetch_related` (SQL IN)"*.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)
- [Caching and Performance](caching-and-performance.md)

#### 10. References
- [QuerySet API: select_related](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-related)
</details>

---

### DJ-INT-014: How Does Django Support Asynchronous Views (`async def`)?
**Difficulty:** Intermediate | **Topic:** Async Concurrency

#### 1. One-Line Answer
Django supports native `async def` views running directly on the ASGI event loop, allowing non-blocking HTTP requests and external API calls via `httpx` or `aiohttp`.

#### 2. Detailed Answer
Starting in Django 3.1, views can be defined with `async def`. Under an ASGI server (Uvicorn/Daphne):
- Async views run concurrently on a single OS thread without blocking worker processes.
- Synchronous calls (like legacy ORM queries) must be wrapped using `sync_to_async` to prevent blocking the event loop.
- Django 4.2+ introduced native async ORM methods (`QuerySet.afirst()`, `QuerySet.acount()`, `Model.asave()`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import httpx
from django.http import JsonResponse
from myapp.models import Merchant

async def merchant_metrics_view(request):
    # 1. Native async ORM query in Django 4.2+
    merchant = await Merchant.objects.filter(id=42).afirst()
    if not merchant:
        return JsonResponse({"error": "Not found"}, status=404)

    # 2. Non-blocking asynchronous third-party HTTP call
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://bank-gateway.example/balance/{merchant.account_number}")
        balance_data = resp.json()

    return JsonResponse({"merchant": merchant.name, "balance": balance_data})
```

#### 4. Internal Working
`django.core.handlers.asgi.ASGIHandler` dispatches `async def` views natively via `asyncio.create_task()`.

#### 5. Real-World Use Case
Aggregating data from multiple third-party banking APIs in parallel without consuming threadpool threads.

#### 6. Interview Follow-Up Questions
- *What happens if you run synchronous blocking code inside an `async def` Django view?* (It stalls the entire event loop, freezing all concurrent requests).

#### 7. Common Interview Mistakes
- Running standard sync ORM methods (`Merchant.objects.get()`) directly inside an `async def` view without `await` or `sync_to_async` (raises `SynchronousOnlyOperation`).

#### 8. Interview Tip
Mention `asgiref.sync.sync_to_async` as the bridge between sync ORM operations and async views.

#### 9. Related Concepts
- [FastAPI Async Concurrency](../02-fastapi/async-and-concurrency.md)
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Asynchronous Support in Django](https://docs.djangoproject.com/en/stable/topics/async/)
</details>

---

### DJ-INT-015: What is `SynchronousOnlyOperation` and How Do You Fix It?
**Difficulty:** Intermediate | **Topic:** Async Concurrency

#### 1. One-Line Answer
`SynchronousOnlyOperation` is an exception raised when a synchronous Django method (like standard ORM queries) is invoked from an asynchronous thread without explicit threadpool delegation.

#### 2. Detailed Answer
Django ORM code was designed synchronously. If executed directly inside an `asyncio` event loop thread, blocking database queries would freeze the loop for all users.
Django's safety checks detect event loop execution and raise `SynchronousOnlyOperation` to protect application health.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# FAILING CODE:
async def my_view(request):
    user = User.objects.get(id=1) # Raises SynchronousOnlyOperation!
    return HttpResponse(user.username)

# FIXED CODE: Option A - Async ORM (Django 4.2+)
async def my_view_fixed(request):
    user = await User.objects.aget(id=1) # Safe native async
    return HttpResponse(user.username)

# FIXED CODE: Option B - sync_to_async adapter
from asgiref.sync import sync_to_async

async def my_view_legacy(request):
    get_user = sync_to_async(User.objects.get, thread_sensitive=True)
    user = await get_user(id=1)
    return HttpResponse(user.username)
```

#### 4. Internal Working
Uses `asgiref.local.Local` and `asyncio.get_running_loop()` inspection in `django.db.models.query.QuerySet`.

#### 5. Real-World Use Case
Integrating legacy Django models with FastAPI, Celery async tasks, or Django Channels consumers.

#### 6. Interview Follow-Up Questions
- *What does `thread_sensitive=True` do in `sync_to_async`?* (Enforces that the synchronous code executes on the single main thread, preserving thread-local storage like database connections).

#### 7. Common Interview Mistakes
- Using `os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"` in production (only permitted in interactive Jupyter shells).

#### 8. Interview Tip
Always explain *why* Django throws this error: to protect the single-threaded event loop from starvation.

#### 9. Related Concepts
- [Async and Concurrency](fundamentals.md)

#### 10. References
- [Async-Safety Documentation](https://docs.djangoproject.com/en/stable/topics/async/#async-safety)
</details>

---

### DJ-INT-016: How Does Django Handle Custom Form Validation?
**Difficulty:** Intermediate | **Topic:** Forms & Validation

#### 1. One-Line Answer
Django validates forms through a three-stage pipeline: field-level `clean_<fieldname>()` methods, multi-field form-level `clean()`, and database model validators.

#### 2. Detailed Answer
When `form.is_valid()` is called:
1. **Field Cleaning:** Individual fields validate type constraints (e.g. `EmailField` regex).
2. **Custom Field Cleaners:** Methods named `clean_<fieldname>()` execute, returning cleaned data or raising `ValidationError`.
3. **Cross-Field Validation:** The `clean()` method executes, validating cross-field business logic (e.g. `password` must match `confirm_password`, `end_date` must be after `start_date`).
4. **Cleaned Data Dictionary:** Validated attributes populate `form.cleaned_data`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django import forms
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    gstin = forms.CharField(max_length=15)

    def clean_gstin(self):
        """Single-field validation."""
        gstin = self.cleaned_data["gstin"].upper()
        if len(gstin) != 15 or not gstin[:2].isdigit():
            raise ValidationError("Invalid Indian GSTIN structure.")
        return gstin

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if pwd and confirm and pwd != confirm:
            raise ValidationError("Passwords do not match!")
        return cleaned_data
```

#### 4. Internal Working
`BaseForm.full_clean()` catches all `ValidationError` instances and aggregates them into `form.errors`.

#### 5. Real-World Use Case
Validating merchant onboarding documents and bank account verification forms.

#### 6. Interview Follow-Up Questions
- *Why must `clean_<fieldname>()` always return the cleaned value?* (If it returns `None`, the field in `cleaned_data` will be overwritten with `None`).

#### 7. Common Interview Mistakes
- Forgetting to return `self.cleaned_data[fieldname]` at the end of `clean_<fieldname>()`.

#### 8. Interview Tip
Mention that `ModelForm` automatically derives validators from database model constraints.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [Form and Field Validation](https://docs.djangoproject.com/en/stable/ref/forms/validation/)
</details>

---

### DJ-INT-017: What is the Purpose of `transaction.atomic()` in Django?
**Difficulty:** Intermediate | **Topic:** Database Transactions

#### 1. One-Line Answer
`transaction.atomic()` wraps database operations in a transaction block, ensuring ACID atomicity so that if any error occurs, all changes are rolled back automatically.

#### 2. Detailed Answer
Can be used as a decorator or context manager:
- Automatically issues `BEGIN` at the start of the block and `COMMIT` at successful completion.
- If an unhandled exception is raised, it issues `ROLLBACK`.
- **Savepoints:** Nested `transaction.atomic()` blocks create database savepoints, allowing inner operations to roll back without aborting the entire outer transaction.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import transaction
from myapp.models import Wallet, LedgerEntry

def transfer_funds(sender_id: int, receiver_id: int, amount: float):
    """Atomic wallet balance transfer preventing double-spend or money loss."""
    with transaction.atomic():
        sender_wallet = Wallet.objects.select_for_update().get(id=sender_id)
        receiver_wallet = Wallet.objects.select_for_update().get(id=receiver_id)

        if sender_wallet.balance < amount:
            raise ValueError("Insufficient balance!")

        sender_wallet.balance -= amount
        sender_wallet.save()

        receiver_wallet.balance += amount
        receiver_wallet.save()

        LedgerEntry.objects.create(sender=sender_wallet, receiver=receiver_wallet, amount=amount)
    # Automatically committed here if no exception raised
```

#### 4. Internal Working
Uses `django.db.connection.set_autocommit(False)` and manages PostgreSQL savepoints (`SAVEPOINT "s1"`).

#### 5. Real-World Use Case
Processing payment debits, credits, and ledger updates in FinTech apps (Razorpay, PhonePe).

#### 6. Interview Follow-Up Questions
- *Why should you keep `transaction.atomic()` blocks as short as possible?* (Long transactions hold database locks, causing lock contention and connection pool exhaustion).

#### 7. Common Interview Mistakes
- Catching exceptions inside the `atomic` block without letting the block roll back, corrupting transaction state.

#### 8. Interview Tip
Always mention combining `transaction.atomic()` with `select_for_update()` to prevent race conditions during updates.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Database Transactions in Django](https://docs.djangoproject.com/en/stable/topics/db/transactions/)
</details>

---

### DJ-INT-018: What is `transaction.on_commit()` and Why is it Critical for Celery Tasks?
**Difficulty:** Intermediate | **Topic:** Concurrency & Transactions

#### 1. One-Line Answer
`transaction.on_commit()` registers a callback function that executes only after the currently active outer database transaction successfully commits to disk.

#### 2. Detailed Answer
When a Celery task is dispatched via `task.delay()` inside a database transaction, the task message is published to RabbitMQ/Redis immediately.
If the Celery worker picks up the task before the web thread commits the transaction, the worker queries the database and raises `Model.DoesNotExist` because the row is not yet committed.
`transaction.on_commit()` guarantees the worker runs only *after* the data physically exists in the database.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import transaction
from myapp.models import Order
from myapp.tasks import send_order_confirmation_sms

def place_order(request):
    with transaction.atomic():
        order = Order.objects.create(user=request.user, total=1500)
        
        # SAFE: Dispatched ONLY after transaction commits to PostgreSQL
        transaction.on_commit(lambda: send_order_confirmation_sms.delay(order.id))
        
    return JsonResponse({"order_id": order.id, "status": "PLACED"})
```

#### 4. Internal Working
`django.db.connection.run_on_commit` maintains a list of callback functions, executing them sequentially in the `commit()` hook.

#### 5. Real-World Use Case
Dispatching order confirmation notifications and courier booking webhooks in high-throughput e-commerce backends.

#### 6. Interview Follow-Up Questions
- *What happens to `on_commit` callbacks if the transaction rolls back?* (They are discarded and never executed).

#### 7. Common Interview Mistakes
- Disagreeing with using `on_commit` and trying to use `sleep(1)` inside the Celery worker (an unreliable antipattern).

#### 8. Interview Tip
This is the single most tested Celery+Django interview question. State: *"Never dispatch asynchronous tasks before transaction commit; always use `transaction.on_commit()`."*

#### 9. Related Concepts
- [Celery Integration](celery-integration.md)

#### 10. References
- [Performing Code After Commit](https://docs.djangoproject.com/en/stable/topics/db/transactions/#django.db.transaction.on_commit)
</details>

---

### DJ-INT-019: How Does Django Prevent SQL Injection by Default?
**Difficulty:** Intermediate | **Topic:** Security & ORM

#### 1. One-Line Answer
Django's ORM uses parameterized SQL queries exclusively, transmitting query structure and user input values separately to the database engine.

#### 2. Detailed Answer
In parameterized queries:
1. The database driver compiles the SQL query template first (e.g. `SELECT * FROM users WHERE username = %s`).
2. User parameters are passed separately as literal data values, never interpreted as executable SQL syntax.
3. Raw SQL methods (`raw()`, `extra()`) remain vulnerable if developers use Python string formatting (`f"SELECT * WHERE id = {val}"`) instead of parameter tuples.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from myapp.models import User

# SAFE: Automatically parameterized by Django ORM
users = User.objects.filter(username=user_input)

# VULNERABLE: Direct f-string interpolation into raw SQL!
# User.objects.raw(f"SELECT * FROM myapp_user WHERE username = '{user_input}'")

# SAFE: Parameterized raw SQL execution
safe_users = User.objects.raw(
    "SELECT * FROM myapp_user WHERE username = %s", 
    [user_input]
)
```

#### 4. Internal Working
Django's SQL compiler delegates parameter binding to Python DB-API 2.0 adapters (`psycopg2`, `mysqlclient`), which escape values at the protocol level.

#### 5. Real-World Use Case
Defending against data exfiltration and credential dumping attacks on login and search endpoints.

#### 6. Interview Follow-Up Questions
- *What is the security danger of `QuerySet.extra()`?* (`extra()` allows raw SQL clauses and is deprecated due to SQL injection risks; use `annotate()` with `RawSQL` or expressions instead).

#### 7. Common Interview Mistakes
- Assuming raw SQL queries in Django are automatically protected regardless of how they are constructed.

#### 8. Interview Tip
Mention that Django ORM is immune to standard SQL injection unless developers deliberately bypass parameterization using raw string concatenation.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [SQL Injection Protection](https://docs.djangoproject.com/en/stable/topics/security/#sql-injection-protection)
</details>

---

### DJ-INT-020: What is the Purpose of `django-environ` / `python-decouple`?
**Difficulty:** Intermediate | **Topic:** Configuration Management

#### 1. One-Line Answer
These libraries parse `.env` files and operating system environment variables, casting strings into native Python types (booleans, lists, integers, database URLs) for strict 12-factor configuration.

#### 2. Detailed Answer
Standard `os.environ.get()` returns strings, forcing developers to manually write fragile parsing logic for booleans (`DEBUG = os.environ.get("DEBUG") == "True"`) and database dictionaries.
`django-environ` provides clean type-casting and converts unified database strings (`DATABASE_URL=postgres://user:pass@host:5432/db`) directly into Django's nested `DATABASES` dictionary.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost"]),
)

environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
DATABASES = {"default": env.db("DATABASE_URL")}
CACHES = {"default": env.cache("CACHE_URL", "redis://localhost:6379/1")}
```

#### 4. Internal Working
Parses standard URI schemes (`postgres://`, `mysql://`, `redis://`, `sqlite://`) using regex and maps them to Django backend drivers.

#### 5. Real-World Use Case
Managing configuration drift between Kubernetes dev, staging, and production clusters with `.env` and ConfigMaps.

#### 6. Interview Follow-Up Questions
- *Why is a `.env` file never committed to Git?* (Contains sensitive credentials, API secrets, and encryption keys).

#### 7. Common Interview Mistakes
- Hardcoding default passwords inside `settings.py` as fallbacks.

#### 8. Interview Tip
Always mention providing a sanitized `.env.example` file in the repository root for onboarding new developers.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [django-environ Documentation](https://django-environ.readthedocs.io/)
</details>

---

### DJ-INT-021: What is the Role of `django.contrib.humanize`?
**Difficulty:** Intermediate | **Topic:** Localization & Formatting

#### 1. One-Line Answer
`django.contrib.humanize` is a template filter library providing human-friendly formatting for numbers, dates, times, and file sizes.

#### 2. Detailed Answer
Common filters:
- `naturaltime`: Formats timestamps relative to now (`"3 minutes ago"`, `"yesterday"`).
- `naturalday`: Formats dates as `"today"`, `"yesterday"`, or `"tomorrow"`.
- `intcomma`: Converts numbers to comma-separated strings (`1000000` -> `"1,000,000"`).
- `intword`: Converts large numbers into words (`1000000` -> `"1.0 million"`).
- `filesizeformat`: Formats bytes into readable units (`1048576` -> `"1.0 MB"`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```html
<!-- Inside Django Template -->
{% load humanize %}

<p>Last active: {{ user.last_login|naturaltime }}</p>
<p>Total Revenue: ₹ {{ invoice.total_inr|intcomma }}</p>
<p>Attachment size: {{ document.file_size_bytes|filesizeformat }}</p>
```

#### 4. Internal Working
Calculates timedelta from `timezone.now()` and applies localized grammar dictionaries.

#### 5. Real-World Use Case
Rendering intuitive user activity feeds and order history tables.

#### 6. Interview Follow-Up Questions
- *How do you activate humanize in a template?* (Add `'django.contrib.humanize'` to `INSTALLED_APPS` and declare `{% load humanize %}` in the template).

#### 7. Common Interview Mistakes
- Writing custom Python date formatting functions in views instead of using built-in template filters.

#### 8. Interview Tip
Mention that `humanize` respects active locale settings.

#### 9. Related Concepts
- [Views and Templates](views-and-templates.md)

#### 10. References
- [django.contrib.humanize Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/humanize/)
</details>

---

### DJ-INT-022: How Does Django Support Custom Database Migrations?
**Difficulty:** Intermediate | **Topic:** Database Migrations

#### 1. One-Line Answer
Developers write custom data migrations using `migrations.RunPython` or raw SQL migrations using `migrations.RunSQL` to transform database data safely without altering table schema.

#### 2. Detailed Answer
While schema migrations alter table structures (adding/removing columns), **data migrations** populate, sanitize, or transform existing data.
Created using `python manage.py makemigrations --empty <app_name>`, data migrations use historical model versions (`apps.get_model()`) to avoid depending on current Python model definitions.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# 0002_populate_customer_uuid.py
import uuid
from django.db import migrations

def backfill_uuid(apps, schema_editor):
    Customer = apps.get_model("billing", "Customer")
    for customer in Customer.objects.all():
        customer.uuid = uuid.uuid4()
        customer.save(update_fields=["uuid"])

def reverse_backfill(apps, schema_editor):
    pass  # No-op on rollback

class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(backfill_uuid, reverse_code=reverse_backfill),
    ]
```

#### 4. Internal Working
`apps.get_model()` instantiates a frozen, historical version of the model matching the exact database schema state at that migration dependency point.

#### 5. Real-World Use Case
Backfilling UUIDs or splitting full names into `first_name` and `last_name` across millions of legacy user rows.

#### 6. Interview Follow-Up Questions
- *Why must you NEVER import models directly (`from myapp.models import Customer`) inside a migration?* (Direct imports load the latest model code, which will fail if future migrations add or remove fields).

#### 7. Common Interview Mistakes
- Directly importing model classes in migrations, breaking the migration history when future schema changes occur.

#### 8. Interview Tip
Always provide a reversible `reverse_code` callable to allow zero-downtime rollbacks.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Data Migrations in Django](https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations)
</details>

---

### DJ-INT-023: Explain the Difference Between `null=True` and `blank=True` in Models
**Difficulty:** Intermediate | **Topic:** Models & Validation

#### 1. One-Line Answer
`null=True` sets database-level `NULL` column constraints, while `blank=True` sets form-level validation rules allowing empty inputs.

#### 2. Detailed Answer
- **`null=True`:** Modifies the database column definition (`NULL` vs `NOT NULL`). Determines whether the database table stores `NULL` when no value is provided.
- **`blank=True`:** Modifies Django form and model validation (`is_valid()`). Determines whether the field is required in HTML forms and Django admin.
- **Text-based fields (`CharField`, `TextField`):** Best practice is to **avoid `null=True`** on strings, using `blank=True` only to store empty strings `""` rather than having two distinct representations of "no data" (`NULL` and `""`).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import models

class UserProfile(models.Model):
    # Optional text: NEVER use null=True on strings!
    bio = models.TextField(blank=True, default="")
    
    # Optional integer/date: REQUIRES null=True and blank=True
    birth_date = models.DateField(null=True, blank=True)
    referred_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
```

#### 4. Internal Working
`blank=True` is evaluated by `Field.clean()` in Python. `null=True` generates `ALTER TABLE ... DROP NOT NULL` in SQL.

#### 5. Real-World Use Case
Designing clean relational schemas without ambiguous null strings.

#### 6. Interview Follow-Up Questions
- *Why is having both `NULL` and empty string `""` in a text column problematic?* (Queries must check `WHERE bio IS NULL OR bio = ''`, breaking unique constraints and complicating indexing).

#### 7. Common Interview Mistakes
- Adding `null=True` to `CharField` without a specific business requirement (e.g. unique constraint with sparse values).

#### 8. Interview Tip
State clearly: *"For strings, use `blank=True, default=''`. For integers, dates, booleans, and foreign keys, use `null=True, blank=True`."*

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Model Field Reference: null](https://docs.djangoproject.com/en/stable/ref/models/fields/#null)
</details>

---

### DJ-INT-024: What is the Purpose of `django.core.cache` and Cache Backends?
**Difficulty:** Intermediate | **Topic:** Caching Architecture

#### 1. One-Line Answer
`django.core.cache` provides a unified in-memory caching API (`get`, `set`, `delete`, `add`) backed by interchangeable storage engines (Redis, Memcached, Database, LocMem).

#### 2. Detailed Answer
Django abstracts caching operations through `caches['default']`.
Supported backends:
- `RedisCache` (Django 4.0+ built-in) / `django-redis`: Distributed in-memory cache supporting persistence and atomic operations.
- `PyMemcacheCache`: High-speed ephemeral key-value store.
- `DatabaseCache`: Stores cached data in relational tables (useful when no Redis/Memcached cluster is available).
- `LocMemCache`: In-process per-worker memory cache for local development.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.core.cache import cache
from myapp.models import Product

def get_product_details(product_id: int):
    cache_key = f"product:detail:{product_id}"
    
    # Check cache (1ms)
    product = cache.get(cache_key)
    if product is None:
        # Cache miss: query database (25ms)
        product = Product.objects.select_related("seller").get(id=product_id)
        # Store in Redis for 10 minutes
        cache.set(cache_key, product, timeout=600)
        
    return product
```

#### 4. Internal Working
Serializes Python objects using `pickle` (or JSON via `django-redis`) and transmits keys over TCP sockets to the cache server.

#### 5. Real-World Use Case
Implementing the Cache-Aside pattern on product catalogs and user authorization profiles.

#### 6. Interview Follow-Up Questions
- *What is Cache Stampede and how do you prevent it?* (When an expensive key expires, thousands of threads query the database simultaneously; prevent using mutex locks or probabilistic early recomputation).

#### 7. Common Interview Mistakes
- Caching raw model QuerySets directly without evaluation, inadvertently caching lazy generator objects that still execute SQL queries later.

#### 8. Interview Tip
Mention that Django 4.0 introduced native Redis cache support (`django.core.cache.backends.redis.RedisCache`).

#### 9. Related Concepts
- [Caching and Performance](caching-and-performance.md)

#### 10. References
- [Django's Cache Framework](https://docs.djangoproject.com/en/stable/topics/cache/)
</details>

---

### DJ-INT-025: What is `SECURE_SSL_REDIRECT` and HSTS in Django?
**Difficulty:** Intermediate | **Topic:** Security Configuration

#### 1. One-Line Answer
`SECURE_SSL_REDIRECT` redirects all HTTP traffic to HTTPS, while HTTP Strict Transport Security (HSTS) instructs browsers to refuse unencrypted connections for a defined duration.

#### 2. Detailed Answer
Managed by `SecurityMiddleware`:
- `SECURE_SSL_REDIRECT = True`: Issues HTTP 301/302 redirects from `http://` to `https://`.
- `SECURE_HSTS_SECONDS = 31536000`: Adds `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` header, defending against SSL-stripping man-in-the-middle attacks.
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`: Enforces HTTPS across all subdomains.
- `SECURE_HSTS_PRELOAD = True`: Allows domain inclusion in browser HSTS preload lists.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS settings (1 year)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookie flags
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 4. Internal Working
`SecurityMiddleware` inspects `request.is_secure()` (which checks SSL headers from reverse proxies like Nginx/ALB).

#### 5. Real-World Use Case
Achieving enterprise security compliance (PCI-DSS, SOC 2, ISO 27001) in FinTech web applications.

#### 6. Interview Follow-Up Questions
- *Why is `SECURE_PROXY_SSL_HEADER` needed behind Nginx or an AWS ALB?* (Because the reverse proxy terminates SSL and forwards plain HTTP to Gunicorn; Django needs the header to know the original client used HTTPS).

#### 7. Common Interview Mistakes
- Enabling HSTS with a large timeout before verifying HTTPS works properly, locking users out if certificates fail.

#### 8. Interview Tip
Always mention pairing `SECURE_SSL_REDIRECT` with `SESSION_COOKIE_SECURE = True` to prevent token leakage.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [SecurityMiddleware Reference](https://docs.djangoproject.com/en/stable/ref/middleware/#security-middleware)
</details>

---

## Advanced Level

### DJ-ADV-001: Deep Dive into Django's Model Metaclass Architecture (`ModelBase`)
**Difficulty:** Advanced | **Topic:** Framework Internals

#### 1. One-Line Answer
Django models use the custom metaclass `ModelBase` to intercept class declaration, convert field descriptors into relational attributes, configure `_meta` options, and register models into the application registry.

#### 2. Detailed Answer
When Python compiles a model class inheriting from `models.Model`:
1. `ModelBase.__new__` intercepts class definition before the class object is created.
2. It strips declared `Field` instances from class namespace and places them into an `Options` instance (`model._meta`).
3. It sets up property descriptors for fields, foreign keys, and managers (`objects`).
4. It sets up inheritance: concrete multi-table inheritance creates a hidden `OneToOneField` pointer; abstract base classes inject fields directly into the subclass.
5. It registers the model with `apps.register_model()`.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Demonstrating _meta introspection generated by ModelBase
from django.contrib.auth import get_user_model

User = get_user_model()

# Accessing fields compiled by ModelBase
for field in User._meta.get_fields():
    print(f"Field Name: {field.name}, Type: {field.get_internal_type()}")
```

#### 4. Internal Working
`ModelBase` lives in `django.db.models.base.py`. It overrides `__new__` to transform the declarative Python syntax into an operational relational descriptor tree.

#### 5. Real-World Use Case
Building dynamic ORM introspection tools, generic serializer generators, or multi-tenant field injection libraries.

#### 6. Interview Follow-Up Questions
- *What is the difference between an abstract model and a concrete model in `ModelBase`?* (Abstract models set `_meta.abstract = True` and do not generate database tables; fields are copied to child classes).

#### 7. Common Interview Mistakes
- Attempting to inspect model fields via `__dict__` instead of the official `_meta` API.

#### 8. Interview Tip
Mention `_meta` (`django.db.models.options.Options`) as the official, stable introspection API for Django models.

#### 9. Related Concepts
- [Python Metaprogramming](../01-python/advanced-python.md)
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Model _meta API Documentation](https://docs.djangoproject.com/en/stable/ref/models/meta/)
</details>

---

### DJ-ADV-002: How Does Django ORM Compile and Execute SQL Under the Hood?
**Difficulty:** Advanced | **Topic:** ORM Internals

#### 1. One-Line Answer
The ORM translates high-level QuerySet calls into an internal `Query` AST tree, which a database-specific `SQLCompiler` compiles into raw SQL with parameter placeholders.

#### 2. Detailed Answer
The compilation pipeline:
1. **Query Construction:** `Model.objects.filter(x=1)` builds a `QuerySet` wrapping a `django.db.models.sql.query.Query` instance. No database calls occur (lazy).
2. **Clause Generation:** Filter arguments are parsed into `WhereNode` trees of `Lookup` expressions.
3. **Execution Trigger:** When the QuerySet is evaluated (iteration, `list()`, `repr()`), `QuerySet._fetch_all()` executes.
4. **Compiler Invocation:** The query calls `query.get_compiler(using=db_alias)`.
5. **SQL Generation:** `SQLCompiler.as_sql()` produces the SQL string (`SELECT ... FROM ... WHERE ...`) and parameter tuple.
6. **Execution:** Database backend cursor executes `cursor.execute(sql, params)` via the underlying DB driver.
7. **Model Instantiation:** Rows are converted into model instances via `from_db()` factory methods.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from myapp.models import Order

qs = Order.objects.filter(status="PAID", amount_inr__gte=5000)

# Inspect internal compiled SQL and parameters without executing
compiler = qs.query.get_compiler(using="default")
sql, params = compiler.as_sql()
print(f"Compiled SQL: {sql}")
print(f"Parameters: {params}")
```

#### 4. Internal Working
Uses database-specific compilers (e.g. `postgresql.compiler.SQLCompiler`) to format vendor-specific dialect features (like `RETURNING` or JSONB operators).

#### 5. Real-World Use Case
Diagnosing unexpected table locks or sequential scans by inspecting the compiled SQL directly.

#### 6. Interview Follow-Up Questions
- *How does `QuerySet.iterator()` optimize memory during million-row processing?* (Bypasses QuerySet caching and uses server-side cursors to stream records in batches).

#### 7. Common Interview Mistakes
- Assuming `qs.query.__str__()` returns exact production SQL (it does not quote or parameterize properly; use `as_sql()` for accurate analysis).

#### 8. Interview Tip
Walk the interviewer through the chain: `QuerySet` -> `Query` -> `SQLCompiler` -> `CursorWrapper` -> `Database Engine`.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [QuerySet Internals](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
</details>

---

### DJ-ADV-003: Memory Leak Debugging in Long-Running Django Processes
**Difficulty:** Advanced | **Topic:** Memory & Performance

#### 1. One-Line Answer
Memory accumulation in long-running processes (Celery workers, management commands) is typically caused by `django.db.connection.queries` storing query history when `DEBUG = True`, or QuerySet caching in persistent objects.

#### 2. Detailed Answer
Two primary culprits in production:
1. **`connection.queries` Retention:** If `DEBUG = True` is accidentally active in a background worker, Django appends the SQL and timing of *every query executed* to an in-memory list (`connection.queries`), consuming gigabytes of RAM within hours.
2. **QuerySet Evaluation Caching:** Storing an evaluated QuerySet (`items = list(Order.objects.all())`) on a singleton or long-lived task instance retains thousands of `Model` objects in memory.
3. **Circular References & Closures:** Signal handlers and closures capturing `self` prevent Python's cyclic garbage collector from releasing generations promptly.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# management/commands/process_large_dataset.py
from django.core.management.base import BaseCommand
from django.db import reset_queries
from myapp.models import Transaction

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. Use iterator() with chunk_size to avoid caching millions of objects
        queryset = Transaction.objects.all().iterator(chunk_size=2000)
        
        for idx, tx in enumerate(queryset):
            # Process transaction...
            
            # 2. Prevent query log accumulation if DEBUG is active
            if idx % 1000 == 0:
                reset_queries()
```

#### 4. Internal Working
`django.db.reset_queries()` clears `connection.queries.clear()`. Using `.iterator()` bypasses `QuerySet._result_cache`.

#### 5. Real-World Use Case
Fixing Linux Out-Of-Memory (`OOMKilled`) crashes on Celery workers processing nightly GST reconciliation exports.

#### 6. Interview Follow-Up Questions
- *How do you configure Celery to defend against memory fragmentation?* (Set `CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000` to recycle worker processes).

#### 7. Common Interview Mistakes
- Blaming Python's garbage collector instead of checking for `DEBUG = True` or in-memory QuerySet caching.

#### 8. Interview Tip
Mention using `tracemalloc` or `filprofiler` to identify memory growth in Python workers.

#### 9. Related Concepts
- [Debugging Exercises](../13-coding-exercises/debugging-exercises.md)
- [Celery Integration](celery-integration.md)

#### 10. References
- [django.db.connection.queries](https://docs.djangoproject.com/en/stable/faq/models/#how-can-i-see-the-raw-sql-queries-django-is-running)
</details>

---

### DJ-ADV-004: How Does Django Support Zero-Downtime Database Migrations?
**Difficulty:** Advanced | **Topic:** Production Engineering

#### 1. One-Line Answer
Zero-downtime migrations follow the **Expand-and-Contract (Blue-Green) pattern**, splitting breaking schema changes into backward-compatible multi-phase releases.

#### 2. Detailed Answer
Running `ALTER TABLE` locks tables and breaks active application instances if a column is deleted or renamed while older app code is still running.
The 3-phase zero-downtime workflow for renaming or altering a column:
1. **Phase 1 (Expand):** Add the new column as nullable (`new_column = models.CharField(null=True)`). Deploy code that writes to *both* old and new columns, reading from the old column.
2. **Phase 2 (Backfill):** Run a background migration to copy historical data from old column to new column. Switch application code to read from the new column.
3. **Phase 3 (Contract):** Remove references to the old column in code. In a subsequent release, drop the old column from the database.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Phase 1: Add new field alongside old field without breaking running containers
class Merchant(models.Model):
    # Old field (kept for backward compatibility with running app instances)
    phone = models.CharField(max_length=15, db_index=True)
    
    # New field: nullable initially
    phone_e164 = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Dual-write during migration phase
        if self.phone and not self.phone_e164:
            self.phone_e164 = f"+91{self.phone}"
        super().save(*args, **kwargs)
```

#### 4. Internal Working
PostgreSQL 11+ adds columns with default values instantaneously without table rewrites (`constant metadata change`).

#### 5. Real-World Use Case
Running continuous deployments at Swiggy or Razorpay without scheduled maintenance windows.

#### 6. Interview Follow-Up Questions
- *Why is adding a non-nullable column without a default dangerous in PostgreSQL?* (Prior to Postgres 11, it rewrote the entire table, acquiring an `ACCESS EXCLUSIVE` lock that blocked all reads and writes).

#### 7. Common Interview Mistakes
- Renaming a column in a single migration (`migrations.RenameField`), which causes immediate downtime while code deploys.

#### 8. Interview Tip
Mention using `SeparateDatabaseAndState` when renaming database tables or fields transparently.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Writing Safe Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/)
</details>

---

### DJ-ADV-005: Deep Dive into Django's Authentication Backend Architecture
**Difficulty:** Advanced | **Topic:** Security Internals

#### 1. One-Line Answer
Django's authentication system uses a pluggable list of backend classes defined in `AUTHENTICATION_BACKENDS`, evaluating credentials sequentially via `authenticate()` until one succeeds.

#### 2. Detailed Answer
Standard default is `django.contrib.auth.backends.ModelBackend`.
A custom authentication backend implements:
- `authenticate(request, **credentials)`: Validates credentials (e.g. email/password, LDAP, SAML, OTP, OAuth2) and returns a `User` instance or `None`.
- `get_user(user_id)`: Fetches user instance from session `_auth_user_id` on subsequent requests.
Multiple backends allow users to authenticate via multiple identity providers (e.g. Email + Password, Google SSO, Phone + OTP).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneOTPAuthenticationBackend(BaseBackend):
    """Custom backend enabling login via phone number and verified OTP."""
    def authenticate(self, request, phone_number=None, otp_code=None, **kwargs):
        if not phone_number or not otp_code:
            return None
        
        # Verify OTP against Redis cache
        from django.core.cache import cache
        cached_otp = cache.get(f"otp:{phone_number}")
        
        if cached_otp and cached_otp == otp_code:
            try:
                user = User.objects.get(phone_number=phone_number)
                return user
            except User.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
```

#### 4. Internal Working
`django.contrib.auth.authenticate()` loops over `AUTHENTICATION_BACKENDS`, catches `PermissionDenied`, and stores the backend path string in `request.session['_auth_user_backend']`.

#### 5. Real-World Use Case
Powering passwordless mobile login (Phone + OTP) for Indian consumers on Flipkart, Swiggy, and Blinkit.

#### 6. Interview Follow-Up Questions
- *Why does Django store the backend string in session data?* (So on subsequent requests, `get_user()` knows which backend to consult for permissions without re-evaluating all backends).

#### 7. Common Interview Mistakes
- Writing login logic inside views instead of encapsulating it in an `AuthenticationBackend`.

#### 8. Interview Tip
Mention how `ModelBackend` handles object-level and model-level permissions via `has_perm()`.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Custom Authentication Backends](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#specifying-authentication-backends)
</details>

---

### DJ-ADV-006: High-Scale Session Management Architecture in Django
**Difficulty:** Advanced | **Topic:** Session Engineering

#### 1. One-Line Answer
Django supports swappable session backends, with cached-database (`cached_db`) and pure Redis backends providing optimal throughput for high-concurrency architectures.

#### 2. Detailed Answer
Standard `db` backend (`django.contrib.sessions.backends.db`) executes a database query on every authenticated request, saturating database I/O.
High-scale alternatives:
- **`cached_db`:** Reads from Redis/Memcached. If a cache miss occurs, falls back to PostgreSQL and populates cache. Writes hit both cache and database. Provides speed with durability.
- **`cache` (Pure Redis):** Fastest; sessions live exclusively in Redis. Requires Redis persistence (AOF/RDB) to prevent user logouts on Redis restart.
- **`signed_cookies`:** Stateless; sessions stored encrypted in client cookies. Eliminates server-side storage entirely, but data size is capped at 4KB.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/production.py
# High-scale resilient session architecture
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# Security hardening
SESSION_COOKIE_AGE = 86400 * 7   # 7 days
SESSION_COOKIE_HTTPONLY = True    # Prevent XSS extraction
SESSION_COOKIE_SECURE = True      # HTTPS transmission only
SESSION_COOKIE_SAMESITE = "Lax"   # CSRF protection
SESSION_SAVE_EVERY_REQUEST = False # Prevent write serialization on every GET
```

#### 4. Internal Working
`SessionMiddleware` lazy-loads `request.session` from `request.COOKIES[SESSION_COOKIE_NAME]` using cryptographic HMAC verification.

#### 5. Real-World Use Case
Supporting 100,000 active concurrent users during festive sales without database connection exhaustion.

#### 6. Interview Follow-Up Questions
- *What is the risk of enabling `SESSION_SAVE_EVERY_REQUEST = True`?* (It forces an expensive write/update to Redis or database on every single page view, killing throughput).

#### 7. Common Interview Mistakes
- Using database-backed sessions in microservice clusters without considering connection pool overhead.

#### 8. Interview Tip
Recommend `cached_db` as the industry sweet spot between raw Redis speed and database persistence.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [Session Engine Configuration](https://docs.djangoproject.com/en/stable/topics/http/sessions/#configuring-the-session-engine)
</details>

---

### DJ-ADV-007: How Does Django Support Database Connection Pooling?
**Difficulty:** Advanced | **Topic:** Database Infrastructure

#### 1. One-Line Answer
Django supports persistent connections via `CONN_MAX_AGE` and native connection pooling (Django 5.1+ / `django-db-geventpool`), but high-scale deployments rely on external connection poolers like **PgBouncer**.

#### 2. Detailed Answer
By default, Django opens and closes a new database TCP connection for every single HTTP request (`CONN_MAX_AGE = 0`). Under high QPS, SSL handshakes and connection setup exhaust database CPU and socket descriptors.
- **`CONN_MAX_AGE`:** Keeps database connections open across requests on the same worker process.
- **PgBouncer:** External transaction-level connection pooler sitting between Gunicorn/Uvicorn workers and PostgreSQL, allowing 5,000 application workers to share 100 actual PostgreSQL backend connections.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/production.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "production_db",
        "USER": "app_user",
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": "pgbouncer.internal", # Connect via PgBouncer
        "PORT": "6432",
        # Keep connections alive for 10 minutes per Gunicorn worker
        "CONN_MAX_AGE": 600,
        # Re-check connection health before executing query
        "CONN_HEALTH_CHECKS": True, # Django 4.1+
    }
}
```

#### 4. Internal Working
`django.db.close_old_connections()` executes at the start and end of every request cycle, closing connections that exceeded `CONN_MAX_AGE` or failed health checks.

#### 5. Real-World Use Case
Scaling Django to 50,000 QPS on AWS ECS while preventing `FATAL: remaining connection slots are reserved` on Amazon RDS.

#### 6. Interview Follow-Up Questions
- *Why is PgBouncer in Transaction Pooling mode incompatible with `django.db.connection.prepare()` or temporary tables?* (Because consecutive queries in the same HTTP request may be executed across different PostgreSQL server connections).

#### 7. Common Interview Mistakes
- Setting `CONN_MAX_AGE = None` in serverless/AWS Lambda environments, leaving orphaned open connections that exhaust database limits.

#### 8. Interview Tip
Mention `CONN_HEALTH_CHECKS = True` (introduced in Django 4.1) to eliminate 500 errors caused by dropped idle firewall connections.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)
- [Databases & SQL](../05-databases/postgresql.md)

#### 10. References
- [Persistent Database Connections](https://docs.djangoproject.com/en/stable/ref/databases/#persistent-connections)
</details>

---

### DJ-ADV-008: Custom Django Middleware: Architecture, Reentrancy, and Thread Safety
**Difficulty:** Advanced | **Topic:** Middleware Internals

#### 1. One-Line Answer
Modern Django middleware uses callable factories instantiated once on server startup, requiring strict thread-safety and reentrancy since a single middleware instance handles concurrent requests across threads.

#### 2. Detailed Answer
Middleware structure:
```python
class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time initialization on server startup

    def __call__(self, request):
        # Code executed per-request before view
        response = self.get_response(request)
        # Code executed per-request after view
        return response
```
Because `__init__` runs once, **storing request-specific state in `self` causes severe data corruption race conditions** across concurrent threads in multi-threaded servers (e.g. Gunicorn with gthread workers). All request-scoped data must be stored on the `request` object.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
import time
import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class RequestProfilingMiddleware:
    """Thread-safe request latency profiling middleware."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        
        # Attach request-scoped timestamp to request object (Thread-Safe!)
        request._start_time = start_time
        
        response = self.get_response(request)
        
        duration = time.monotonic() - start_time
        response["X-Response-Time-Ms"] = f"{duration * 1000:.2f}"
        
        if duration > 1.0:
            logger.warning(f"Slow request detected: {request.path} took {duration:.2f}s")
            
        return response
```

#### 4. Internal Working
`django.core.handlers.base.BaseHandler.load_middleware()` builds the execution chain wrapping each callable in reverse.

#### 5. Real-World Use Case
Injecting distributed tracing headers (`X-Trace-Id`) and logging slow queries in microservice fabrics.

#### 6. Interview Follow-Up Questions
- *How do you make a custom middleware compatible with both synchronous and asynchronous views?* (Declare `async_capable = True` and `sync_capable = True`, handling coroutines in `__call__`).

#### 7. Common Interview Mistakes
- Writing `self.request = request` inside `__call__`, corrupting state across concurrent threads.

#### 8. Interview Tip
Always emphasize: *"Middleware instances are singletons per worker process; never store request-specific state on `self`."*

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [Writing Your Own Middleware](https://docs.djangoproject.com/en/stable/topics/http/middleware/#writing-your-own-middleware)
</details>

---

### DJ-ADV-009: How Does Django Support Signals and What are Their Architectural Trade-offs?
**Difficulty:** Advanced | **Topic:** Event-Driven Architecture

#### 1. One-Line Answer
Django signals provide a synchronous Publish-Subscribe mechanism to decouple application components, but excessive use obscures code flow, complicates debugging, and degrades transaction performance.

#### 2. Detailed Answer
- **Mechanism:** `Signal.send()` executes all registered receiver functions sequentially in the **same thread and same database transaction** as the caller. Signals are **synchronous**, not background tasks.
- **Core Built-in Signals:** `pre_save`, `post_save`, `pre_delete`, `post_delete`, `m2m_changed`, `request_started`, `request_finished`.
- **Architectural Drawbacks:** Hidden side-effects, implicit execution order, recursion loops (e.g. `save()` triggering `post_save` which calls `save()`), and difficulty in tracing errors during code audits.
- **Best Practice:** Prefer explicit service functions (`services.create_user()`) or model `save()` overrides over signals whenever possible. Reserve signals for cross-app decoupling (e.g. third-party audit logging apps).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from myapp.models import UserProfile

User = get_user_model()

# Weak reference prevents memory leaks
@receiver(post_save, sender=User, dispatch_uid="create_user_profile_signal")
def create_profile_on_user_creation(sender, instance, created, **kwargs):
    """Automatically instantiates Profile when new User is created."""
    if created:
        UserProfile.objects.create(user=instance)
```

#### 4. Internal Working
Uses `django.dispatch.dispatcher.Signal`, maintaining a list of weak references to receivers identified by `dispatch_uid`.

#### 5. Real-World Use Case
Invalidating external Redis caches whenever a core entity model is updated.

#### 6. Interview Follow-Up Questions
- *Why is `dispatch_uid` important when registering signal receivers?* (Prevents duplicate receiver registration if the signal module is imported multiple times).

#### 7. Common Interview Mistakes
- Assuming Django signals run asynchronously in the background like Celery tasks (they run synchronously in the web request thread).

#### 8. Interview Tip
Senior engineering advice: *"Signals should be used sparingly; explicit is better than implicit. Prefer domain service functions over signals for business logic."*

#### 9. Related Concepts
- [Middleware and Signals](middleware-and-signals.md)

#### 10. References
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
</details>

---

### DJ-ADV-010: Advanced Content Security Policy (CSP) Implementation in Django
**Difficulty:** Advanced | **Topic:** Application Security

#### 1. One-Line Answer
Content Security Policy (CSP) is implemented using `django-csp` middleware to restrict resource origins (scripts, styles, images, iframes), eliminating Cross-Site Scripting (XSS) and data injection vulnerabilities.

#### 2. Detailed Answer
CSP headers instruct modern browsers which domains and hashes are permitted to execute code.
Essential CSP directives:
- `default-src 'self'`: Disallows loading any resource from third-party domains unless explicitly permitted.
- `script-src 'self' 'nonce-...'`: Blocks inline `<script>` tags and `eval()`, requiring cryptographic nonces.
- `frame-ancestors 'none'`: Blocks embedding in iframes, preventing clickjacking.
- `object-src 'none'`: Blocks Flash and Java plugins.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/production.py
MIDDLEWARE = [
    # ...
    "csp.middleware.CSPMiddleware",
]

# Strict Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://checkout.razorpay.com",
    "https://cdn.jsdelivr.net",
)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https://s3.ap-south-1.amazonaws.com")
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_REPORT_ONLY = False
CSP_REPORT_URI = "https://sentry.example.com/api/security-report"
```

#### 4. Internal Working
`CSPMiddleware.process_response()` compiles directives into the `Content-Security-Policy` header.

#### 5. Real-World Use Case
Securing financial payment checkout pages against third-party script injection and credential theft.

#### 6. Interview Follow-Up Questions
- *What is `CSP_REPORT_ONLY = True` used for?* (Tests policy without blocking resources; violations are logged to a reporting endpoint to detect breaking changes before hard enforcement).

#### 7. Common Interview Mistakes
- Enabling `unsafe-inline` or `unsafe-eval` in `script-src`, completely negating XSS protection.

#### 8. Interview Tip
Mention starting with `Content-Security-Policy-Report-Only` to monitor real user traffic before switching to strict blocking mode.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)
- [Application Security](../12-security/application-security.md)

#### 10. References
- [django-csp Documentation](https://django-csp.readthedocs.io/)
</details>

---

### DJ-ADV-011: Multi-Tenant Architecture Strategies in Django
**Difficulty:** Advanced | **Topic:** System Architecture

#### 1. One-Line Answer
Django supports three primary multi-tenant patterns: **Shared Database with Shared Schema** (tenant ID column), **Shared Database with Separate Schemas** (`django-tenants` PostgreSQL schemas), and **Isolated Database per Tenant**.

#### 2. Detailed Answer
| Strategy | Isolation Level | Hardware Cost | Operational Complexity | Best Fit |
|---|---|---|---|---|
| **Shared Schema (Tenant ID column)** | Low (logical filtering) | Lowest | Low | High-volume B2C, low-cost SaaS |
| **Separate PostgreSQL Schemas** | Medium (schema-level) | Medium | Medium | B2B enterprise SaaS (Zoho, Freshworks) |
| **Database per Tenant** | Highest (physical) | Highest | Highest | Banking, healthcare, strict compliance |

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Strategy 1: Tenant Model Base with Automatic Filtering
from django.db import models

class TenantModel(models.Model):
    tenant_id = models.CharField(max_length=64, db_index=True)

    class Meta:
        abstract = True

# Thread-local tenant context set by middleware
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_header = request.headers.get("X-Tenant-ID")
        request.tenant_id = tenant_header
        return self.get_response(request)
```

#### 4. Internal Working
In PostgreSQL schema-based isolation (`django-tenants`), middleware sets `SET search_path TO tenant_name, public` at the start of each request.

#### 5. Real-World Use Case
Hosting thousands of school portals or merchant dashboards on a unified Django codebase.

#### 6. Interview Follow-Up Questions
- *What is the risk of shared-schema tenancy?* (A missed `filter(tenant=...)` in a query can leak another customer's confidential data; prevent using custom managers or row-level security (RLS)).

#### 7. Common Interview Mistakes
- Relying entirely on developers remembering to add `tenant_id` to every query without automated middleware or custom manager enforcement.

#### 8. Interview Tip
Mention PostgreSQL **Row-Level Security (RLS)** as the modern standard for enforcing tenant boundaries directly at the database engine level.

#### 9. Related Concepts
- [System Design Fundamentals](../10-system-design/fundamentals.md)

#### 10. References
- [django-tenants Documentation](https://django-tenants.readthedocs.io/)
</details>

---

### DJ-ADV-012: How Does Django Support Custom Admin Customization and Performance Hardening?
**Difficulty:** Advanced | **Topic:** Admin Internals

#### 1. One-Line Answer
Django admin performance is optimized by overriding `get_queryset()` with `select_related`/`prefetch_related`, using `raw_id_fields` or `autocomplete_fields` for foreign keys, and disabling expensive `COUNT(*)` queries on multi-million row tables.

#### 2. Detailed Answer
By default, the Django admin executes an unbounded `SELECT COUNT(*)` on changelist pages, which causes full sequential table scans and 10+ second timeouts on tables with 10M+ rows.
Hardening strategies:
- **`raw_id_fields` / `autocomplete_fields`:** Prevents rendering dropdowns that load 100,000 foreign key rows into an HTML `<select>` tag.
- **`show_full_result_count = False`:** Disables full table counting when filtered.
- **Custom Paginator:** Overrides `Paginator.count` with PostgreSQL `reltuples` estimate (`EXPLAIN` estimate) for instant page rendering.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.contrib import admin
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from myapp.models import Transaction

class FastLargeTablePaginator(Paginator):
    """Overrides expensive COUNT(*) with PostgreSQL statistics estimate."""
    @cached_property
    def count(self):
        with self.object_list.db.cursor() as cursor:
            cursor.execute("SELECT reltuples::BIGINT FROM pg_class WHERE relname = %s", [self.object_list.model._meta.db_table])
            estimate = cursor.fetchone()[0]
            return estimate if estimate and estimate > 0 else 1000

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    paginator = FastLargeTablePaginator
    show_full_result_count = False
    list_display = ("id", "merchant", "amount_inr", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "merchant__business_name")
    raw_id_fields = ("merchant",) # Prevents rendering 50,000 merchants in dropdown

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("merchant")
```

#### 4. Internal Working
`ModelAdmin.get_changelist_instance()` instantiates `ChangeList` which invokes the configured paginator and querysets.

#### 5. Real-World Use Case
Allowing operations teams to browse transaction tables containing 50 million records without crashing PostgreSQL.

#### 6. Interview Follow-Up Questions
- *Why is `search_fields` with foreign keys (`merchant__business_name`) dangerous without indexes?* (It generates expensive `JOIN` and `LIKE` queries that trigger full table scans).

#### 7. Common Interview Mistakes
- Putting foreign keys in `list_display` without `select_related` in `get_queryset`, causing 100+ queries per page.

#### 8. Interview Tip
Mention `raw_id_fields` or `autocomplete_fields` immediately when asked how to scale Django admin for large datasets.

#### 9. Related Concepts
- [Caching and Performance](caching-and-performance.md)

#### 10. References
- [The Django Admin Site](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
</details>

---

### DJ-ADV-013: Explain Django's Content Types Framework and Generic Foreign Keys
**Difficulty:** Advanced | **Topic:** ORM Architecture

#### 1. One-Line Answer
`django.contrib.contenttypes` tracks all models installed in a project, enabling **Generic Foreign Keys (GFKs)** that can link a single record to an arbitrary row in *any* database table.

#### 2. Detailed Answer
A standard `ForeignKey` links to a specific target model.
A `GenericForeignKey` uses two columns:
1. `content_type`: A foreign key to `ContentType` model storing the target table name.
2. `object_id`: A positive integer or UUID storing the primary key of the target row.
This allows universal features (comments, audit activity logs, tags, attachments) to attach to any entity (`Product`, `Order`, `Customer`, `Article`) without writing separate foreign keys for every table.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AuditActivityLog(models.Model):
    user_id = models.IntegerField()
    action = models.CharField(max_length=50) # e.g. "UPDATED", "DELETED"
    timestamp = models.DateTimeField(auto_now_add=True)

    # Generic Foreign Key components
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

# Usage:
from myapp.models import Order, Customer

order = Order.objects.get(id=101)
log = AuditActivityLog.objects.create(user_id=1, action="REFUNDED", content_object=order)
```

#### 4. Internal Working
`GenericForeignKey` is a virtual field implementing the descriptor protocol; it does not create a database column itself, but queries `ContentType` and the target model dynamically on access.

#### 5. Real-World Use Case
Building centralized compliance audit trails and notification engines across disparate business models.

#### 6. Interview Follow-Up Questions
- *What is the database integrity trade-off of using Generic Foreign Keys?* (Because target tables vary, relational databases cannot enforce physical database-level foreign key constraints or cascading deletes at the SQL engine level).

#### 7. Common Interview Mistakes
- Overusing GFKs for standard relationships, sacrificing SQL referential integrity and query joining performance.

#### 8. Interview Tip
State the trade-off: *"Generic Foreign Keys provide maximum modeling flexibility at the expense of database-level foreign key integrity and JOIN query performance."*

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [The Contenttypes Framework](https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/)
</details>

---

### DJ-ADV-014: High-Concurrency Pessimistic Locking with `select_for_update()`
**Difficulty:** Advanced | **Topic:** Concurrency & Transactions

#### 1. One-Line Answer
`select_for_update()` executes SQL `SELECT ... FOR UPDATE`, acquiring exclusive row-level locks on queried rows until the enclosing transaction commits, preventing race conditions and lost updates.

#### 2. Detailed Answer
In high-concurrency environments (e.g. inventory decrements, wallet deductions):
1. **The Race Condition:** Two threads read balance as 1,000 INR simultaneously. Both deduct 600 INR. Both write 400 INR. The account is debited 1,200 INR but only reduced by 600 INR.
2. **The Fix:** `select_for_update()` locks the row. Thread 2 blocks until Thread 1 commits. Thread 2 then reads the updated balance (400 INR) and fails the balance check.
3. **Parameters:**
   - `nowait=True`: Raises `DatabaseError` immediately instead of blocking if the row is already locked.
   - `skip_locked=True`: Skips locked rows, returning only unlocked rows (ideal for job queue processing).

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import transaction
from myapp.models import InventoryItem

def reserve_inventory(item_id: int, quantity: int) -> bool:
    with transaction.atomic():
        # Acquires row-level ExclusiveLock on the item
        item = InventoryItem.objects.select_for_update().get(id=item_id)
        
        if item.available_stock < quantity:
            return False  # Insufficient stock
            
        item.available_stock -= quantity
        item.save()
        return True
```

#### 4. Internal Working
PostgreSQL sets a row-level `ExclusiveLock` on the tuple in shared memory, releasing it upon `COMMIT` or `ROLLBACK`.

#### 5. Real-World Use Case
Flash-sale inventory reservations on Flipkart Big Billion Days and wallet balance deductions on Paytm/PhonePe.

#### 6. Interview Follow-Up Questions
- *How does `skip_locked=True` allow building job queues in PostgreSQL?* (Multiple workers can execute `select_for_update(skip_locked=True).first()` simultaneously, each claiming a unique job without blocking each other).

#### 7. Common Interview Mistakes
- Calling `select_for_update()` outside of `transaction.atomic()`, which raises a `TransactionManagementError`.

#### 8. Interview Tip
Mention deadlocks: if locking multiple rows, **always sort IDs in ascending order** to eliminate circular wait conditions.

#### 9. Related Concepts
- [Backend Practical Tasks](../13-coding-exercises/backend-practical-tasks.md)
- [Models and ORM](models-and-orm.md)

#### 10. References
- [QuerySet API: select_for_update](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update)
</details>

---

### DJ-ADV-015: How Does Django Support Custom Database Expressions (`Func`, `F`, `Subquery`)?
**Difficulty:** Advanced | **Topic:** ORM Expressions

#### 1. One-Line Answer
Database expressions allow executing calculations, database functions, and subqueries directly on the database server without fetching rows into Python memory.

#### 2. Detailed Answer
- **`F()` Expressions:** References database column values directly in SQL. Enables atomic in-database updates (`F('stock') - 1`) and row-level comparisons (`filter(likes__gt=F('dislikes'))`).
- **`Func()`:** Executes native database functions (e.g. `MD5()`, `COALESCE()`, `DATE_TRUNC()`).
- **`Subquery()` & `OuterRef()`:** Embeds explicit correlated SQL subqueries inside a parent QuerySet, eliminating multi-stage Python loops.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db.models import F, Subquery, OuterRef
from myapp.models import Product, OrderItem

# 1. Atomic decrement preventing race conditions: UPDATE product SET stock = stock - 1
Product.objects.filter(id=101).update(stock=F("stock") - 1)

# 2. Correlated Subquery: Annotate each product with its latest order price
latest_price = OrderItem.objects.filter(
    product=OuterRef("pk")
).order_by("-created_at").values("unit_price")[:1]

products = Product.objects.annotate(last_sale_price=Subquery(latest_price))
```

#### 4. Internal Working
Expressions implement `as_sql(compiler, connection)`, compiling directly into SQL AST nodes.

#### 5. Real-World Use Case
Updating view counters and tracking high-velocity stock changes without race conditions or memory overhead.

#### 6. Interview Follow-Up Questions
- *Why is `save()` after an `F()` expression dangerous if the instance is reused?* (The in-memory instance attribute retains the `F()` expression object, causing subsequent `save()` calls to evaluate the expression again; reload via `.refresh_from_db()`).

#### 7. Common Interview Mistakes
- Reusing a model instance after an `F()` update without calling `refresh_from_db()`.

#### 8. Interview Tip
Highlight that `F()` updates avoid race conditions because the database serializes the update at the storage engine level.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Query Expressions Documentation](https://docs.djangoproject.com/en/stable/ref/models/expressions/)
</details>

---

### DJ-ADV-016: Designing Multi-Database High-Availability Architectures in Django
**Difficulty:** Advanced | **Topic:** High Availability & Scaling

#### 1. One-Line Answer
A high-availability Django deployment pairs multi-worker application nodes with an active-standby primary database and multiple read-replicas routed via custom database routers with automatic replication-lag hedging.

#### 2. Detailed Answer
Architecture components:
1. **Stateless App Nodes:** Gunicorn/Uvicorn workers scaled horizontally behind an AWS Application Load Balancer.
2. **Database Cluster:** 1 Primary PostgreSQL (Read/Write) + 2 Read Replicas (Streaming Replication).
3. **PgBouncer:** Connection poolers deployed as sidecars or a centralized cluster.
4. **Router Pinning:** When a user executes a write (POST/PUT), the session is pinned to the primary database for reads for 5 seconds using cookies or cache flags, guaranteeing read-your-own-writes consistency.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Pinning reads to primary database after write operations
import time

class ReplicationLagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user performed recent write
        pinned_until = request.session.get("pin_to_primary_until", 0)
        request.force_primary_db = time.time() < pinned_until
        
        response = self.get_response(request)
        
        # If user submitted unsafe HTTP method, pin for 5 seconds
        if request.method in ("POST", "PUT", "PATCH", "DELETE") and response.status_code < 400:
            request.session["pin_to_primary_until"] = time.time() + 5.0
            
        return response
```

#### 4. Internal Working
Database router checks `request.force_primary_db` to return `'default'` instead of `'replica'`.

#### 5. Real-World Use Case
Preventing user complaints on social media or e-commerce platforms where profile updates or reviews appear missing immediately after submission.

#### 6. Interview Follow-Up Questions
- *What is asynchronous vs synchronous replication in PostgreSQL?* (Asynchronous does not wait for replicas to acknowledge writes, yielding higher throughput with potential replication lag; synchronous guarantees zero data loss at the cost of write latency).

#### 7. Common Interview Mistakes
- Directing all read traffic to replicas without accounting for replication lag.

#### 8. Interview Tip
Mention this pattern as standard practice at major internet companies (Instagram, Pinterest, Swiggy).

#### 9. Related Concepts
- [System Design Distributed Systems](../10-system-design/distributed-systems.md)

#### 10. References
- [Multiple Databases in Django](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
</details>

---

### DJ-ADV-017: How Does Django Secure CSRF Tokens Against BREACH and Compression Attacks?
**Difficulty:** Advanced | **Topic:** Cryptography & Security

#### 1. One-Line Answer
Django masks CSRF tokens on every HTTP response using a randomized one-time pad (secret XOR masking), preventing BREACH attacks from guessing the underlying secret through HTTP gzip compression ratio analysis.

#### 2. Detailed Answer
- **The BREACH Attack:** An attacker observing compressed HTTP responses with static secret tokens can deduce the secret character by character by measuring response size variations when injecting guesses.
- **Django's Defense:** Django generates a static 32-character secret stored in `request.session` or the `csrftoken` cookie.
- When generating form tokens (`{% csrf_token %}`), Django picks 32 random characters as a one-time pad, XORs the secret with the pad, and concatenates `pad + masked_secret` into a 64-character token.
- Every response renders a visually different 64-character string, completely neutralizing BREACH compression analysis while remaining decryptable by the server.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Demonstrating CSRF Token Masking in Python
import secrets
import string

CHARS = string.ascii_letters + string.digits

def mask_token(secret: str) -> str:
    """Simplified view of Django's CSRF token scrambling."""
    mask = "".join(secrets.choice(CHARS) for _ in range(32))
    # Secret is scrambled with the mask
    scrambled = "".join(chr(ord(s) ^ ord(m)) for s, m in zip(secret, mask))
    return mask + scrambled # 64-character token changes every render!
```

#### 4. Internal Working
Implemented in `django.middleware.csrf._mask_cipher_secret()` and `_unmask_cipher_token()`.

#### 5. Real-World Use Case
Defending enterprise portals and banking dashboards against side-channel compression attacks.

#### 6. Interview Follow-Up Questions
- *Why is a CSRF token not required on `GET` requests?* (Because `GET` requests must be safe and idempotent, having zero side-effects on server state).

#### 7. Common Interview Mistakes
- Assuming CSRF tokens change because the user's session secret changed (the secret is identical; only the mask changes).

#### 8. Interview Tip
Explaining the BREACH attack and XOR masking demonstrates world-class security depth that sets senior candidates apart.

#### 9. Related Concepts
- [Authentication and Security](authentication-and-security.md)

#### 10. References
- [CSRF Protection in Django](https://docs.djangoproject.com/en/stable/howto/csrf/)
</details>

---

### DJ-ADV-018: Deep Dive into Django's Static Files Manifest Storage and Cache Busting
**Difficulty:** Advanced | **Topic:** Asset Performance

#### 1. One-Line Answer
`ManifestStaticFilesStorage` appends an MD5 hash of file contents to every static asset filename, enabling infinite browser caching (`max-age=31536000, immutable`) with zero-downtime cache busting on code deployments.

#### 2. Detailed Answer
When `python manage.py collectstatic` runs:
1. Django reads all static files (CSS, JS, images).
2. It computes an MD5 checksum of each file's content and renames the file (e.g. `main.css` -> `main.bf49092823a2.css`).
3. It recursively parses CSS files, updating internal references (e.g. `url('bg.png')` -> `url('bg.8123acfa12.png')`).
4. It compiles a JSON map `staticfiles.json` storing `{ "main.css": "main.bf49092823a2.css" }`.
5. In templates, `{% static 'main.css' %}` queries `staticfiles.json` in memory and outputs the hashed URL.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# settings/production.py
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Template:
# Output: <link rel="stylesheet" href="/static/css/app.e48291a134cf.css">
# Browser Cache-Control header: "public, max-age=31536000, immutable"
```

#### 4. Internal Working
Inherits from `HashedFilesMixin` in `django.contrib.staticfiles.storage`.

#### 5. Real-World Use Case
Eliminating browser caching issues where users see broken UI styles after a frontend deployment.

#### 6. Interview Follow-Up Questions
- *What happens if a CSS file contains a broken `url('non-existent.png')` reference during `collectstatic`?* (`ManifestStaticFilesStorage` raises `ValueError: Missing staticfiles manifest entry`, halting the build; prevent using `manifest_strict = False` or fixing broken paths).

#### 7. Common Interview Mistakes
- Deploying without hashed static files, forcing users to perform hard browser refreshes (Ctrl+F5) to clear cached CSS/JS.

#### 8. Interview Tip
Mention combining `ManifestStaticFilesStorage` with Nginx or CloudFront `Cache-Control: public, max-age=31536000, immutable` headers.

#### 9. Related Concepts
- [Production Deployment](production-deployment.md)

#### 10. References
- [ManifestStaticFilesStorage Reference](https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#manifeststaticfilesstorage)
</details>

---

### DJ-ADV-019: Implementing PostgreSQL Full-Text Search in Django
**Difficulty:** Advanced | **Topic:** PostgreSQL Integration

#### 1. One-Line Answer
Django's `django.contrib.postgres.search` module exposes PostgreSQL's native full-text search capabilities using `SearchVector`, `SearchQuery`, `SearchRank`, and GIN indexes, eliminating the need for external search clusters (like Elasticsearch) for medium-scale search workloads.

#### 2. Detailed Answer
Components:
- **`SearchVector`:** Combines multiple text columns (title, description) into a lexeme document vector.
- **`SearchQuery`:** Parses user search terms, applying stemming, word normalization, and stop-word elimination.
- **`SearchRank`:** Scores search results based on frequency and proximity of matching terms.
- **`SearchHeadline`:** Generates search result snippets with matched keywords highlighted in HTML (`<b>keyword</b>`).
- **GIN Index:** Accelerates vector search from full table scans to sub-millisecond B-Tree equivalent lookups.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from myapp.models import Article

def search_articles(user_query: str):
    # 1. Stem and normalize query
    query = SearchQuery(user_query, config="english")
    
    # 2. Build vector with weighted importance (Title weight A, Body weight B)
    vector = SearchVector("title", weight="A") + SearchVector("content", weight="B")
    
    # 3. Query, Rank, and Highlight matches
    results = (
        Article.objects.annotate(rank=SearchRank(vector, query))
        .filter(rank__gte=0.2)
        .order_by("-rank")
        .annotate(headline=SearchHeadline("content", query))
    )
    return results
```

#### 4. Internal Working
Compiles to PostgreSQL `to_tsvector()`, `to_tsquery()`, and `ts_rank()` operators using GIN indexes (`CREATE INDEX ON article USING gin(to_tsvector('english', title || ' ' || content))`).

#### 5. Real-World Use Case
Powering search bars on documentation sites, product catalogs, and news portals up to millions of rows without the infrastructure cost of maintaining an Elasticsearch or OpenSearch cluster.

#### 6. Interview Follow-Up Questions
- *How does a GIN (Generalized Inverted Index) work?* (Maps individual words/lexemes to a list of row pointers where that word appears).

#### 7. Common Interview Mistakes
- Executing full-text search without a GIN index on large tables, causing sequential table scans.

#### 8. Interview Tip
Position native PostgreSQL FTS as the cost-effective, operationally simple precursor to Elasticsearch for startups and mid-size companies.

#### 9. Related Concepts
- [Databases & SQL](../05-databases/postgresql.md)

#### 10. References
- [PostgreSQL Full Text Search](https://docs.djangoproject.com/en/stable/ref/contrib/postgres/search/)
</details>

---

### DJ-ADV-020: How Does Django Prevent Deadlocks in Distributed Queue & Consumer Workflows?
**Difficulty:** Advanced | **Topic:** Database Concurrency & Deadlocks

#### 1. One-Line Answer
Prevent database deadlocks by enforcing deterministic ascending lock acquisition order, using `select_for_update(skip_locked=True)` for worker queues, and keeping transactional boundaries strictly bounded.

#### 2. Detailed Answer
- **The Deadlock Condition:** Worker A locks Order 101, then requests Order 202. Worker B locks Order 202, then requests Order 101. Both block forever; PostgreSQL deadlock detector kills one after `deadlock_timeout` (1s).
- **Prevention Rules:**
  1. **Deterministic Lock Ordering:** When locking multiple rows, always sort IDs in ascending order: `Order.objects.filter(id__in=sorted_ids).order_by('id').select_for_update()`.
  2. **Worker Queue Decoupling:** Use `skip_locked=True`. Workers skip rows already locked by concurrent workers rather than queuing behind them.
  3. **No External I/O inside Transactions:** Never make HTTP calls or wait on network sockets inside a `transaction.atomic()` block.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import transaction
from myapp.models import BackgroundJob

def claim_next_job(worker_id: str):
    """Worker job claim using SKIP LOCKED to eliminate lock contention."""
    with transaction.atomic():
        job = (
            BackgroundJob.objects.select_for_update(skip_locked=True)
            .filter(status="PENDING")
            .order_by("created_at")
            .first()
        )
        if job:
            job.status = "PROCESSING"
            job.assigned_worker = worker_id
            job.save()
            return job
    return None
```

#### 4. Internal Working
PostgreSQL `FOR UPDATE SKIP LOCKED` checks tuple header locks; if locked, it advances the table cursor immediately without waiting.

#### 5. Real-World Use Case
Building resilient background task consumers and webhook dispatchers without Redis or RabbitMQ.

#### 6. Interview Follow-Up Questions
- *What is the difference between `NOWAIT` and `SKIP LOCKED`?* (`NOWAIT` immediately raises an error if a row is locked; `SKIP LOCKED` cleanly bypasses the locked row and returns other available rows).

#### 7. Common Interview Mistakes
- Ordering QuerySets arbitrarily before acquiring pessimistic locks, leading to intermittent deadlocks under load.

#### 8. Interview Tip
Mention this pattern as the standard implementation behind relational queue engines like Celery's database broker and Django-Q.

#### 9. Related Concepts
- [Backend Practical Tasks](../13-coding-exercises/backend-practical-tasks.md)
- [Debugging Exercises](../13-coding-exercises/debugging-exercises.md)

#### 10. References
- [Row-Level Locking in PostgreSQL](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS)
</details>

---

### DJ-ADV-021: Deep Dive into Custom Model Field Implementation in Django
**Difficulty:** Advanced | **Topic:** ORM Extensibility

#### 1. One-Line Answer
Custom model fields subclass `models.Field`, implementing `db_type()` for database column creation, `to_python()` for deserialization, and `get_prep_value()` for serialization before SQL compilation.

#### 2. Detailed Answer
Core methods when authoring a custom field:
- `db_type(connection)`: Returns the SQL data type (e.g. `'VARCHAR(15)'`, `'BYTEA'`) based on database engine.
- `to_python(value)`: Converts database or form values into the native Python object (e.g. string to custom object).
- `from_db_value(value, expression, connection)`: Converts data loaded directly from the database into Python type.
- `get_prep_value(value)`: Serializes Python object into database-compatible format prior to query compilation.
- `deconstruct()`: Serializes field parameters for migration file generation.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db import models
import json

class JSONCoordinatesField(models.Field):
    """Custom field storing (lat, lng) tuples as JSON strings."""
    description = "Stores latitude/longitude tuples"

    def db_type(self, connection):
        return "VARCHAR(64)"

    def from_db_value(self, value, expression, connection):
        if value is None: return None
        data = json.loads(value)
        return (data["lat"], data["lng"])

    def to_python(self, value):
        if isinstance(value, tuple) or value is None:
            return value
        data = json.loads(value)
        return (data["lat"], data["lng"])

    def get_prep_value(self, value):
        if value is None: return None
        return json.dumps({"lat": value[0], "lng": value[1]})
```

#### 4. Internal Working
Django's migration engine inspects `.deconstruct()` to write Python representations of custom fields into migration files.

#### 5. Real-World Use Case
Encrypting sensitive fields (Aadhaar number, PAN, credit card tokens) transparently at the ORM layer using AES-256 before writing to disk.

#### 6. Interview Follow-Up Questions
- *What is the purpose of `from_db_value()` vs `to_python()`?* (`from_db_value` is called exclusively when loading from the database cursor; `to_python` is also called during form validation and deserialization).

#### 7. Common Interview Mistakes
- Forgetting `deconstruct()`, which causes migrations to crash with un-serializable field errors.

#### 8. Interview Tip
Mention `django-cryptography` as a real-world example of custom model fields for transparent field-level encryption.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Writing Custom Model Fields](https://docs.djangoproject.com/en/stable/howto/custom-model-fields/)
</details>

---

### DJ-ADV-022: How Does Django Support Real-Time WebSockets via Django Channels?
**Difficulty:** Advanced | **Topic:** Real-Time Architecture

#### 1. One-Line Answer
Django Channels extends Django beyond HTTP by wrapping ASGI, handling WebSockets, MQTT, and long-lived connections via asynchronous event consumers and Redis channel layers.

#### 2. Detailed Answer
Architecture of Django Channels:
1. **ASGI Protocol Router:** Inspects incoming connection protocol (`http` vs `websocket`). HTTP requests route to standard Django views; WebSocket requests route to Channels `Consumer` classes.
2. **Channel Consumers:** Event-driven classes (like `AsyncWebsocketConsumer`) that implement `connect()`, `disconnect()`, and `receive()` hooks.
3. **Channel Layer (Redis):** A distributed message bus (`channels_redis`) allowing consumers to communicate across different worker processes using group broadcasts.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveDeliveryTracker(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f"delivery_{self.order_id}"

        # Join order tracking channel group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def delivery_update(self, event):
        """Receive broadcast from Redis channel layer and push to mobile client."""
        await self.send(text_data=json.dumps(event["location_data"]))
```

#### 4. Internal Working
Daphne or Uvicorn terminates WebSocket connections and communicates with worker instances via the Redis Channel Layer using message serialization.

#### 5. Real-World Use Case
Live delivery rider GPS tracking on Swiggy and Zomato, real-time customer support chat, and live stock market tickers.

#### 6. Interview Follow-Up Questions
- *How does Channels authenticate WebSocket connections?* (Using `AuthMiddlewareStack`, which reads session cookies and populates `scope['user']`).

#### 7. Common Interview Mistakes
- Running blocking database queries inside `AsyncWebsocketConsumer` methods without `database_sync_to_async`.

#### 8. Interview Tip
Mention using `database_sync_to_async` inside channel consumers when interacting with the Django ORM.

#### 9. Related Concepts
- [API Engineering WebSockets](../07-api-engineering/websockets.md)

#### 10. References
- [Django Channels Documentation](https://channels.readthedocs.io/)
</details>

---

### DJ-ADV-023: Profiling and Benchmarking Django Performance using Silk and cProfile
**Difficulty:** Advanced | **Topic:** Profiling & Observability

#### 1. One-Line Answer
Django application performance is benchmarked using in-depth profilers like **Django Silk** for intercepting SQL queries and request timelines, and Python's native **cProfile** to locate CPU execution bottlenecks.

#### 2. Detailed Answer
- **Django Silk:** Profiling middleware that records execution time, database queries, memory consumption, and template rendering for every HTTP request, exposing an interactive dashboard.
- **cProfile & Py-Spy:** C-level deterministic profiling tracking function call counts and cumulative execution times (`cumtime`), exposing GIL bottlenecks and CPU-heavy algorithms.
- **SQL Analysis:** Logs query count, identifies identical duplicate queries (classic N+1), and flags missing indexes.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# Profiling a slow view programmatically with cProfile
import cProfile
import pstats
import io
from django.http import HttpResponse

def profile_heavy_view(request):
    profiler = cProfile.Profile()
    profiler.enable()

    # Heavy domain computation or query
    # ... execute logic ...

    profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(15) # Print top 15 time-consuming functions
    print(s.getvalue())
    
    return HttpResponse("Profile completed")
```

#### 4. Internal Working
Silk hooks into `django.db.backends.utils.CursorWrapper` to intercept `cursor.execute()`, logging queries to database or memory.

#### 5. Real-World Use Case
Auditing checkout APIs before festive sales to eliminate hidden ORM overhead and serializer latency.

#### 6. Interview Follow-Up Questions
- *Why must Silk be strictly disabled in production environments?* (It intercepts and writes every query to disk, adding 20–40% latency overhead).

#### 7. Common Interview Mistakes
- Leaving profiling tools enabled in production, leading to severe latency degradation.

#### 8. Interview Tip
Mention **Py-Spy** as a low-overhead, sampling-based profiler safe to run against live production Python processes without modifying code.

#### 9. Related Concepts
- [Caching and Performance](caching-and-performance.md)

#### 10. References
- [Django Silk Documentation](https://github.com/jazzband/django-silk)
</details>

---

### DJ-ADV-024: How Does Django Support Custom Migration Operations?
**Difficulty:** Advanced | **Topic:** Database Migrations

#### 1. One-Line Answer
Custom migration operations subclass `django.db.migrations.operations.base.Operation`, providing `database_forwards()`, `database_backwards()`, and `state_forwards()` to execute specialized database engine extensions.

#### 2. Detailed Answer
While built-in operations handle standard DDL (`CreateModel`, `AddField`), complex enterprise systems require database-specific operations:
- Creating PostgreSQL triggers and stored procedures.
- Managing TimescaleDB hypertables.
- Configuring PostgreSQL GiST / GIN indexes and custom extension operators.
- Creating and partitioning tables dynamically.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
from django.db.migrations.operations.base import Operation

class CreatePostgresExtension(Operation):
    """Custom migration operation enabling PostgreSQL extensions."""
    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass # No change to Django model state

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(f"CREATE EXTENSION IF NOT EXISTS {self.name};")

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(f"DROP EXTENSION IF EXISTS {self.name};")

    def describe(self):
        return f"Enables PostgreSQL extension: {self.name}"
```

#### 4. Internal Working
`MigrationExecutor` builds a dependency graph of migrations and invokes `database_forwards` passing `schema_editor` for DDL execution.

#### 5. Real-World Use Case
Enabling `pg_trgm` (trigram matching) and `postgis` extensions in geospatial applications.

#### 6. Interview Follow-Up Questions
- *What is the role of `state_forwards()`?* (It updates Django's in-memory ProjectState model tree so subsequent migration operations in the same migration know about schema changes).

#### 7. Common Interview Mistakes
- Forgetting to implement `database_backwards()`, making migrations irreversible during deployment rollbacks.

#### 8. Interview Tip
Mention that Django's built-in `django.contrib.postgres.operations.BtreeGinExtension` is implemented using this exact custom operation pattern.

#### 9. Related Concepts
- [Models and ORM](models-and-orm.md)

#### 10. References
- [Writing Custom Migration Operations](https://docs.djangoproject.com/en/stable/ref/migration-operations/#writing-your-own-operations)
</details>

---

### DJ-ADV-025: Advanced Database Sharding & Partitioning Strategies in Django
**Difficulty:** Advanced | **Topic:** Database Architecture & Big Data

#### 1. One-Line Answer
Django supports multi-billion row scale through **declarative database partitioning** (PostgreSQL Range/List/Hash partitioning on timestamps or tenant IDs) and **application-level horizontal sharding** using dynamic routers.

#### 2. Detailed Answer
When tables exceed 100 million rows:
1. **Declarative Partitioning (PostgreSQL):** Partition the table by date (`PARTITION BY RANGE (created_at)`). PostgreSQL automatically routes inserts and prunes partitions during queries (`constraint exclusion`), while Django treats the table as a single model.
2. **Horizontal Sharding (Application Layer):** Shard by user ID (`user_id % num_shards`). Django routes queries dynamically to database shards (`shard_0`, `shard_1`, `shard_2`) using a custom database router.
3. **Partition Maintenance:** Automated background workers create next month's partition tables and detach or archive historical partitions older than 3 years to S3.

<details>
<summary><b>Deep Dive: Practical Example, Internals & Interview Insights</b></summary>

#### 3. Practical Example
```python
# models.py - Model representing partitioned PostgreSQL table
from django.db import models

class OrderPartitioned(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(db_index=True)
    customer_id = models.IntegerField()
    total_inr = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False  # Schema DDL managed via raw partition migration
        db_table = "orders_partitioned"

# Migration executing native PostgreSQL declarative partition DDL
# CREATE TABLE orders_partitioned (
#     order_id BIGSERIAL,
#     created_at TIMESTAMPTZ NOT NULL,
#     customer_id INT,
#     total_inr NUMERIC(12, 2),
#     PRIMARY KEY (order_id, created_at)
# ) PARTITION BY RANGE (created_at);
```

#### 4. Internal Working
PostgreSQL optimizer checks the query `WHERE created_at >= '2026-11-01'` and scans *only* the matching monthly partition table, skipping all other historical partitions.

#### 5. Real-World Use Case
Handling payment transactions and delivery tracking pings at Flipkart, PhonePe, and Swiggy where tables grow by millions of records weekly.

#### 6. Interview Follow-Up Questions
- *Why must the partition key be part of the primary key in partitioned tables?* (PostgreSQL requires unique and primary key constraints to include all partition key columns to enforce uniqueness across partitions).

#### 7. Common Interview Mistakes
- Sharding too early when standard composite B-Tree indexes, partial indexing, or caching would solve the latency problem for 95% of workloads.

#### 8. Interview Tip
Demonstrate seniority by discussing operational trade-offs: *"Partitioning improves query pruning and VACUUM performance, but increases operational complexity. Only partition when table size exceeds memory cache boundaries."*

#### 9. Related Concepts
- [Databases & SQL](../05-databases/postgresql.md)
- [System Design Distributed Systems](../10-system-design/distributed-systems.md)

#### 10. References
- [PostgreSQL Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
</details>
