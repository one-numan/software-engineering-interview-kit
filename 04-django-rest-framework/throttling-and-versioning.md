# DRF Throttling & API Versioning Guide

## Module Overview
This module covers **DRF Throttling** (AnonRateThrottle, UserRateThrottle, ScopedRateThrottle) and **API Versioning Strategies** (URLPath, Namespace, AcceptHeader).

---

## Questions & Comprehensive Solutions

### DRF-THR-001: Configuring Tiered Throttling in DRF

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',        # Unauthenticated users
        'user': '1000/hour',      # Authenticated standard users
        'premium': '10000/hour',  # Custom scope
    }
}
```

---

### DRF-VER-002: API Versioning Schemes Comparison

| Versioning Scheme | URL / Header Example | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **URLPathVersioning** | `/api/v1/orders/` | Explicit, easy to test in browser, CDN friendly | URL clutter |
| **AcceptHeaderVersioning** | `Accept: application/json; version=1.0` | Clean URLs, follows strict REST purity | Harder to test in browser |
| **QueryParameterVersioning** | `/api/orders/?version=1.0` | Easy fallback | Can conflict with query filters |

**Industry Standard:** `URLPathVersioning` (`/api/v1/`, `/api/v2/`) is overwhelmingly preferred by Stripe, Twilio, and GitHub because of its transparency and simple caching rules.
