# Django Caching & Performance Optimization Guide

## Module Overview
This module covers **Django Cache Framework**, per-site, per-view, and template fragment caching, **Redis Cache Backends**, and low-level cache API usage.

---

## Visual Architecture: Django Multi-Tier Cache Framework

```mermaid
flowchart TD
    Client[Incoming Request] --> SiteCache{1. Per-Site Cache: CacheMiddleware}
    SiteCache -->|Hit| ReturnFast[Return Cached HTML < 5ms]
    
    SiteCache -->|Miss| ViewCache{2. Per-View Cache: @cache_page}
    ViewCache -->|Hit| ReturnView[Return Cached View Response]
    
    ViewCache -->|Miss| FragmentCache{3. Template Fragment Cache: {% cache %}}
    FragmentCache --> LowLevelCache{4. Low-Level Cache API: cache.get/set}
    LowLevelCache --> QueryDB[(PostgreSQL Database)]
```

---

## Questions & Comprehensive Solutions

### DJ-PERF-001: The 4 Tiers of Caching in Django

1. **Per-Site Caching (Full Page):**
   - Configured via `UpdateCacheMiddleware` (top of middleware list) and `FetchFromCacheMiddleware` (bottom). Caches every single response for all anonymous users.
2. **Per-View Caching (`@cache_page`):**
   - Caches the output of a specific view function or class:
     ```python
     from django.views.decorators.cache import cache_page
     
     @cache_page(60 * 15) # Cache for 15 minutes
     def catalog_view(request): ...
     ```
3. **Template Fragment Caching:**
   - Caches expensive HTML blocks (e.g. site navigation bars or top trending products) directly in templates:
     ```html
     {% load cache %}
     {% cache 600 sidebar request.user.username %}
         .. expensive database queries for sidebar ..
     {% endcache %}
     ```
4. **Low-Level Cache API (`django.core.cache`):**
   - Granular programmatic caching of raw Python objects or QuerySets in Redis:
     ```python
     from django.core.cache import cache
     
     def get_popular_categories():
         categories = cache.get("popular_categories")
         if not categories:
             categories = list(Category.objects.filter(is_active=True))
             cache.set("popular_categories", categories, timeout=3600)
         return categories
     ```

---

### DJ-PERF-002: Configuring Redis as Django's Cache Backend

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": 300, # Default 5 minutes
        "KEY_PREFIX": "my_django_app",
    }
}
```
