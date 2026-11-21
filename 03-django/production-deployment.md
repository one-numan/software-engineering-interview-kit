# Django Production Deployment & Hardening Guide

## Module Overview
This module covers **Django Production Hardening**, `settings.py` security flags, static file collection via **WhiteNoise / S3**, and zero-downtime database migrations.

---

## Production Security Checklist (`settings.py`)

```python
# 1. ALWAYS False in Production (Never leak tracebacks to users)
DEBUG = False

# 2. Strict Host Whitelisting
ALLOWED_HOSTS = ["api.mycompany.com", "mycompany.com"]

# 3. HTTPS & HSTS Enforcements
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000 # 1 Year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 4. Anti-Sniffing and Clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

---

## Zero-Downtime Database Migration Rules

When rolling out migrations to a live high-traffic Django application:
1. **Never rename columns in a single step:** Renaming `full_name` to `name` instantly breaks all running v1 worker instances that are still querying `full_name`.
2. **The 3-Step Safe Migration Pattern:**
   - **Step 1:** Add the new column `name` as nullable.
   - **Step 2:** Deploy application code that writes to *both* columns and reads from `name` (backfill existing records via background task).
   - **Step 3:** Deploy code that drops reads/writes to `full_name`, and run a migration to drop the old column.
