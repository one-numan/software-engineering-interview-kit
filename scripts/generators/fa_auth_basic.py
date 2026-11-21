"""
fa_auth_basic.py
================
Basic FastAPI Authentication & Security Questions: FA-BAS-076 to FA-BAS-100 (25 questions)
"""

basic_data = [
    # FA-BAS-076
    (
        "FA-BAS-076",
        "fastapi.security Module Overview and Security Schemes",
        "`fastapi.security` provides reusable security scheme classes that integrate directly with OpenAPI/Swagger UI, allowing automatic extraction and documentation of credentials.",
        "Building secure APIs requires handling authentication schemes like HTTP Basic, API Keys, and OAuth2. Rather than parsing raw headers manually, FastAPI provides `fastapi.security`. Classes like `HTTPBasic`, `APIKeyHeader`, `OAuth2PasswordBearer`, and `SecurityScopes` inherit from Starlette or OpenAPI security models. When used with `Depends()`, they automatically extract credentials from requests, validate formats, trigger HTTP 401 challenges, and generate the interactive 'Authorize' lock icon in Swagger UI.",
        "from fastapi import FastAPI, Depends\nfrom fastapi.security import HTTPBasic, HTTPBasicCredentials\n\napp = FastAPI()\nsecurity = HTTPBasic()\n\n@app.get('/users/me')\ndef read_current_user(credentials: HTTPBasicCredentials = Depends(security)):\n    # Automatically decoded from Base64 Authorization header\n    return {'username': credentials.username}",
        "Extracting HTTP Basic authentication credentials using fastapi.security.HTTPBasic.",
        "`HTTPBasic` inspects the ASGI `scope['headers']` for the `Authorization: Basic <base64>` header. If missing, it raises an `HTTPException(status_code=401, headers={'WWW-Authenticate': 'Basic'})`. In OpenAPI, it registers an `http` security scheme.",
        "Securing administrative dashboards, internal health-check metrics, and microservice endpoints.",
        ["What happens in the browser when an endpoint returns `WWW-Authenticate: Basic`?", "How does `fastapi.security` link authentication to Swagger UI documentation?"],
        ["Parsing `request.headers.get('Authorization')` manually instead of using `fastapi.security` utilities.", "Forgetting that `fastapi.security` schemes extract credentials but do not verify passwords against a database."],
        "Emphasize: `fastapi.security` handles credential extraction and OpenAPI documentation; password verification remains your application logic.",
        ["[HTTP Basic Auth](authentication-and-security.md)", "[OAuth2 Password Bearer](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/"]
    ),

    # FA-BAS-077
    (
        "FA-BAS-077",
        "HTTP Basic Authentication with HTTPBasic and HTTPBasicCredentials",
        "`HTTPBasic` extracts username and password credentials transmitted in the standard HTTP `Authorization: Basic <base64>` header.",
        "HTTP Basic Authentication is a standard IETF protocol (RFC 7617) where client credentials are formatted as `username:password`, encoded in Base64, and sent in the `Authorization` header. In FastAPI, declaring `Depends(HTTPBasic())` automatically parses this header, decodes the Base64 payload, and populates an `HTTPBasicCredentials` object with `.username` and `.password` attributes. If credentials are missing or malformed, it triggers an HTTP 401 response with `WWW-Authenticate: Basic`.",
        "import secrets\nfrom fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import HTTPBasic, HTTPBasicCredentials\n\napp = FastAPI()\nsecurity = HTTPBasic()\n\ndef authenticate_admin(credentials: HTTPBasicCredentials = Depends(security)):\n    correct_username = secrets.compare_digest(credentials.username, 'admin')\n    correct_password = secrets.compare_digest(credentials.password, 'super_secret')\n    if not (correct_username and correct_password):\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Incorrect username or password',\n            headers={'WWW-Authenticate': 'Basic'},\n        )\n    return credentials.username\n\n@app.get('/admin')\ndef admin_panel(user: str = Depends(authenticate_admin)):\n    return {'message': f'Welcome to admin panel, {user}'}",
        "Securing an endpoint with HTTP Basic authentication and constant-time string comparison.",
        "When the browser receives a 401 response with `WWW-Authenticate: Basic`, it automatically opens a native credential login prompt, re-sending subsequent requests with the Base64 header.",
        "Protecting internal developer documentation, staging environments, and monitoring endpoints like Prometheus metrics.",
        ["Why is constant-time string comparison (`secrets.compare_digest`) essential when checking passwords?", "Can HTTP Basic authentication be considered secure over unencrypted HTTP?"],
        ["Comparing passwords using standard `==`, exposing the application to timing attacks.", "Using HTTP Basic over plain HTTP without TLS (Base64 is NOT encryption; credentials can be sniffed trivially)."],
        "Security rule: HTTP Basic Auth MUST only be run over HTTPS/TLS; Base64 encoding provides zero encryption.",
        ["[Security Schemes](authentication-and-security.md)", "[Constant-Time Comparison](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/advanced/security/http-basic-auth/"]
    ),

    # FA-BAS-078
    (
        "FA-BAS-078",
        "API Key Authentication via Header with APIKeyHeader",
        "`APIKeyHeader` extracts client API keys from a designated HTTP request header (such as `X-API-Key`) and documents the key in OpenAPI security specifications.",
        "In B2B APIs, server-to-server microservices, and public developer developer platforms, clients authenticate using static or rolling API keys transmitted in headers. FastAPI provides `APIKeyHeader(name='X-API-Key')`. When used with `Depends()`, it extracts the header value from incoming requests. If the header is missing, it returns a 403 Forbidden (or 401 if configured).",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import APIKeyHeader\n\napp = FastAPI()\napi_key_header = APIKeyHeader(name='X-API-Key', auto_error=True)\n\nVALID_API_KEYS = {'prod_key_alpha9981', 'test_key_beta0012'}\n\ndef verify_api_key(api_key: str = Depends(api_key_header)):\n    if api_key not in VALID_API_KEYS:\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Invalid or inactive API Key'\n        )\n    return api_key\n\n@app.get('/data')\ndef get_secure_data(key: str = Depends(verify_api_key)):\n    return {'status': 'authenticated', 'key_prefix': key[:8]}",
        "Validating incoming API keys using APIKeyHeader dependency injection.",
        "FastAPI reads the header name from `request.headers`. In Swagger UI, it renders an API key input field under the Authorize modal, automatically attaching `X-API-Key` to interactive requests.",
        "Developer APIs (like Stripe, OpenAI, Twilio) where automated backend clients authenticate via long-lived API tokens.",
        ["What does `auto_error=False` do in `APIKeyHeader`?", "How should API keys be stored in production databases (hashing vs plain text)?"],
        ["Storing client API keys in plain text in database tables instead of cryptographic SHA-256 hashes.", "Passing API keys in URL query strings where they get logged in web server access logs."],
        "Best practice: Always transmit API keys in custom headers (`X-API-Key`) rather than query parameters to prevent log leakage.",
        ["[API Key via Query](authentication-and-security.md)", "[API Key via Cookie](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/"]
    ),

    # FA-BAS-079
    (
        "FA-BAS-079",
        "API Key Authentication via Query Parameter with APIKeyQuery",
        "`APIKeyQuery` extracts API keys from URL query parameters (e.g. `?api_key=secret`), enabling authentication in scenarios where custom headers cannot be sent.",
        "Certain client integrations (such as webhooks, file download links clicked in browser emails, or embedded image tags) cannot attach custom HTTP headers. FastAPI accommodates this via `APIKeyQuery(name='api_key')`. It extracts the parameter from the URL query string and registers an `apiKey` in query security scheme in OpenAPI documentation.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import APIKeyQuery\n\napp = FastAPI()\napi_key_query = APIKeyQuery(name='api_key', auto_error=True)\n\nVALID_KEYS = {'secret-download-key-123'}\n\ndef verify_query_key(key: str = Depends(api_key_query)):\n    if key not in VALID_KEYS:\n        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')\n    return key\n\n@app.get('/download/report.pdf')\ndef download_report(key: str = Depends(verify_query_key)):\n    return {'message': 'Authorized download access granted'}",
        "Authenticating via URL query parameters using APIKeyQuery.",
        "FastAPI reads `request.query_params[name]`. If missing and `auto_error=True`, it raises an HTTP 403 Forbidden response.",
        "Serving direct file download links, media streaming endpoints, and email verification callbacks.",
        ["Why is transmitting API keys in query parameters considered a security risk?", "How can you mitigate API key exposure in web server access logs?"],
        ["Using query parameter API keys for sensitive write operations (POST/PUT/DELETE).", "Forgetting that query parameters are stored in browser history, proxy logs, and `Referer` headers."],
        "Security caveat: Query parameter keys are logged in plaintext across Nginx/CloudFront logs; use short-lived signed URLs for downloads.",
        ["[API Key via Header](authentication-and-security.md)", "[API Key via Cookie](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/"]
    ),

    # FA-BAS-080
    (
        "FA-BAS-080",
        "API Key Authentication via Cookie with APIKeyCookie",
        "`APIKeyCookie` extracts authentication keys or session tokens directly from browser HTTP cookies.",
        "Web applications serving browser clients conventionally manage authentication sessions via HTTP cookies rather than requiring frontend JavaScript to manually manage headers. FastAPI provides `APIKeyCookie(name='session_id')`. It reads the cookie from incoming browser requests, validates its presence, and documents cookie authentication in OpenAPI.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import APIKeyCookie\n\napp = FastAPI()\nsession_cookie = APIKeyCookie(name='session_token', auto_error=True)\n\nACTIVE_SESSIONS = {'sess_abc123': 'user_alice'}\n\ndef get_session_user(token: str = Depends(session_cookie)):\n    if token not in ACTIVE_SESSIONS:\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired')\n    return ACTIVE_SESSIONS[token]\n\n@app.get('/dashboard')\ndef dashboard(user: str = Depends(get_session_user)):\n    return {'user': user, 'content': 'Secure Dashboard'}",
        "Validating session tokens from HTTP cookies using APIKeyCookie.",
        "FastAPI extracts the token from Starlette's `request.cookies[name]`. In Swagger UI, it registers a cookie security requirement.",
        "Browser-based web applications, Single-Sign-On (SSO) portals, and stateful dashboard backends.",
        ["Why must cookies used for authentication be marked with `HttpOnly` and `SameSite`?", "How does cookie authentication introduce vulnerability to Cross-Site Request Forgery (CSRF)?"],
        ["Allowing JavaScript to read authentication cookies by omitting the `HttpOnly` flag (exposing tokens to XSS).", "Using cookie authentication without CSRF protection tokens."],
        "Cookie security trifecta: Always configure authentication cookies with `HttpOnly=True`, `Secure=True`, and `SameSite='Lax'` or `'Strict'`.",
        ["[Cookie Extraction](routing-and-dependencies.md)", "[CSRF Protection](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/"]
    ),

    # FA-BAS-081
    (
        "FA-BAS-081",
        "Introduction to OAuth2 and OAuth2PasswordBearer",
        "`OAuth2PasswordBearer` defines an OAuth2 bearer token security scheme, specifying the URL where clients can exchange credentials for an access token.",
        "OAuth2 is the industry-standard authorization framework (RFC 6749). In FastAPI, `OAuth2PasswordBearer(tokenUrl='token')` serves two key purposes: 1) Runtime: It extracts the Bearer token from the HTTP `Authorization: Bearer <token>` header. 2) OpenAPI / Swagger UI: It documents the OAuth2 password flow and enables the Swagger UI 'Authorize' modal, configuring Swagger to send username/password to `tokenUrl` and automatically attach the returned token to future requests.",
        "from fastapi import FastAPI, Depends\nfrom fastapi.security import OAuth2PasswordBearer\n\napp = FastAPI()\n# Defines OAuth2 scheme pointing to login URL\noauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')\n\n@app.get('/items')\ndef read_items(token: str = Depends(oauth2_scheme)):\n    # token is the raw JWT string extracted from Authorization header\n    return {'token_received': token}",
        "Declaring OAuth2PasswordBearer and extracting raw Bearer tokens.",
        "`OAuth2PasswordBearer` checks `request.headers['Authorization']`. If the header is missing or does not start with `Bearer `, it immediately returns an HTTP 401 Unauthorized response.",
        "Standard REST API authentication across mobile apps, single-page web apps, and distributed microservices.",
        ["What does the `tokenUrl` parameter represent in `OAuth2PasswordBearer`?", "Does `OAuth2PasswordBearer` validate JWT signatures automatically?"],
        ["Thinking `OAuth2PasswordBearer` decodes or validates JWT tokens (it only extracts the token string from the header).", "Specifying an incorrect `tokenUrl` path, causing Swagger UI authentication to fail with 404."],
        "Crucial interview point: `OAuth2PasswordBearer` extracts the token string and tells Swagger UI where to log in; token decoding and signature validation is your responsibility.",
        ["[Security Schemes](authentication-and-security.md)", "[JWT Architecture](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"]
    ),

    # FA-BAS-082
    (
        "FA-BAS-082",
        "Generating OpenAPI Security Definitions and the Swagger UI Authorize Button",
        "FastAPI automatically injects security schemes into OpenAPI's `components.securitySchemes`, rendering an interactive 'Authorize' button in Swagger UI.",
        "One of FastAPI's most acclaimed developer experience features is its out-of-the-box interactive documentation. When any security scheme from `fastapi.security` (such as `OAuth2PasswordBearer` or `HTTPBasic`) is used in a dependency on any route, FastAPI automatically injects the security definition into the OpenAPI 3.1 JSON document. Swagger UI detects this and renders a green 'Authorize' padlock icon at the top of the page.",
        "from fastapi import FastAPI, Depends\nfrom fastapi.security import OAuth2PasswordBearer\n\napp = FastAPI(title='Secured API Platform')\noauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')\n\n@app.get('/protected-resource')\ndef get_protected(token: str = Depends(oauth2_scheme)):\n    return {'data': 'confidential_payload'}",
        "Configuring security dependency that activates Swagger UI's interactive Authorize modal.",
        "FastAPI updates OpenAPI's `components/securitySchemes` object with the OAuth2 password flow definition, and adds a `security: [{'OAuth2PasswordBearer': []}]` requirement to the route's path item.",
        "Accelerating frontend and QA integration by allowing developers to authenticate and test secured endpoints directly in the browser.",
        ["How do you apply a security scheme globally across all endpoints in Swagger UI?", "Can multiple security schemes (e.g. API Key OR OAuth2) be documented on the same endpoint?"],
        ["Expecting the 'Authorize' button to appear without using any `fastapi.security` dependencies in your application.", "Hardcoding absolute URLs in `tokenUrl` that break when deployed behind reverse proxies or custom domains."],
        "DX tip: Always use relative paths for `tokenUrl` (e.g. `tokenUrl='token'` or `tokenUrl='/api/v1/auth/token'`) so Swagger UI works across localhost and production.",
        ["[OAuth2 Password Bearer](authentication-and-security.md)", "[FastAPI Overview](fundamentals.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/first-steps/"]
    ),

    # FA-BAS-083
    (
        "FA-BAS-083",
        "Password Hashing with Passlib, Argon2, and Bcrypt",
        "Passwords must be transformed using one-way cryptographic key-derivation functions (like Argon2id or Bcrypt) with per-password salt before database persistence.",
        "Storing plaintext passwords in databases is a catastrophic engineering failure. Modern security standards mandate hashing passwords with slow, salted, computationally expensive key derivation algorithms: 1) Argon2id: The PHC (Password Hashing Competition) winner; highly resistant to GPU/ASIC cracking. 2) Bcrypt: Industry-proven standard using Blowfish cipher. In Python, libraries like `pwdlib`, `passlib`, or `argon2-cffi` provide simple APIs to hash passwords during registration and verify them during login.",
        "from passlib.context import CryptContext\n\n# Configure password hashing context using modern Argon2 with bcrypt fallback\npwd_context = CryptContext(schemes=['argon2', 'bcrypt'], deprecated='auto')\n\n# 1. Hashing password during user registration\nraw_password = 'MySuperSecurePassword!2026'\nhashed_password = pwd_context.hash(raw_password)\nprint('Hashed representation:', hashed_password[:35] + '...')\n\n# 2. Verifying password during login\nis_valid = pwd_context.verify('MySuperSecurePassword!2026', hashed_password)\nassert is_valid is True\nassert pwd_context.verify('WrongPassword', hashed_password) is False",
        "Hashing and verifying passwords securely using CryptContext with Argon2.",
        "Password hashing functions generate a random cryptographic salt for every password and perform thousands of computation rounds (work factor), producing a formatted string containing algorithm identifier, cost parameters, salt, and hash.",
        "User registration and authentication services across all production web applications.",
        ["What is salt in password hashing and what attack does it neutralize (Rainbow Table attacks)?", "Why are fast hash algorithms like MD5 or SHA256 completely unsuitable for password storage?"],
        ["Using fast cryptographic hashes like SHA-256 for passwords (can be cracked at billions of hashes per second using GPUs).", "Generating fixed or shared salts instead of letting the hashing library generate unique salts per password."],
        "Cryptographic standard: Recommend Argon2id (or Bcrypt if Argon2 is unavailable); never use SHA-256 or MD5 for passwords.",
        ["[Plaintext Passwords](authentication-and-security.md)", "[OAuth2 Password Flow](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords"]
    ),

    # FA-BAS-084
    (
        "FA-BAS-084",
        "Why Plaintext Passwords Must Never Be Stored or Compared with ==",
        "Storing plaintext passwords exposes credentials during database breaches, and comparing password hashes with `==` introduces timing side-channel vulnerabilities.",
        "Two foundational security mandates govern password engineering: 1) Never store plaintext: If database backups, SQL dumps, or read replicas are leaked, all user accounts across the web are compromised. 2) Never compare with standard `==`: Python's `==` operator terminates immediately upon finding the first mismatched byte (short-circuit evaluation). Attackers can measure response time variations (in microseconds) to determine password length and characters byte-by-byte. Always use constant-time comparison functions like `secrets.compare_digest` or library `verify()` methods.",
        "import secrets\n\nstored_hash = '$argon2id$v=19$m=65536,t=3,p=4$...'  # Real hash from DB\n\n# DANGEROUS: Short-circuit timing attack vulnerable\n# if user_input == stored_secret: ...\n\n# SECURE: Constant-time comparison (executes in identical time regardless of match)\nis_match = secrets.compare_digest('expected_token_abc', 'client_token_abc')\nassert is_match is True",
        "Contrasting insecure standard string equality with constant-time secrets.compare_digest.",
        "`secrets.compare_digest` compares all bytes of both strings without early termination, ensuring execution time is invariant regardless of where character differences occur.",
        "Preventing timing attacks on API keys, HMAC signatures, CSRF tokens, and authentication credentials.",
        ["What is a timing attack and how can attackers exploit it over network connections?", "What is a Rainbow Table and how does cryptographic salting prevent it?"],
        ["Comparing API keys or tokens with `==` instead of `secrets.compare_digest`.", "Logging password strings in error logs or exception tracebacks during failed login attempts."],
        "Rule of law: Never use `==` for authentication tokens or password hashes—always use constant-time `secrets.compare_digest()`.",
        ["[Password Hashing](authentication-and-security.md)", "[Constant-Time Comparison](authentication-and-security.md)"],
        ["https://docs.python.org/3/library/secrets.html#secrets.compare_digest"]
    ),

    # FA-BAS-085
    (
        "FA-BAS-085",
        "JSON Web Tokens (JWT) Architecture: Header, Payload, and Signature",
        "A JSON Web Token (JWT, RFC 7519) is a compact, URL-safe means of representing claims between two parties, composed of three Base64URL-encoded segments separated by dots: Header, Payload, and Signature.",
        "JWTs are the dominant mechanism for stateless authentication in modern distributed architectures. A JWT has three distinct parts: `header.payload.signature`: 1) Header: Contains token metadata and signing algorithm (e.g. `{\"alg\": \"HS256\", \"typ\": \"JWT\"}`). 2) Payload: Contains claims about the subject (e.g. `sub: user_id`, `exp: expiration_time`, `role: admin`). 3) Signature: Cryptographic hash computed by hashing the Base64URL header and payload using a secret key. The server verifies the signature to ensure the payload was not tampered with.",
        "import base64\nimport json\n\n# Conceptual breakdown of a JWT structure\nheader = {'alg': 'HS256', 'typ': 'JWT'}\npayload = {'sub': 'user_101', 'role': 'engineer', 'exp': 1770000000}\n\ndef b64_url_encode(data: dict) -> str:\n    json_bytes = json.dumps(data).encode('utf-8')\n    return base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')\n\nencoded_header = b64_url_encode(header)\nencoded_payload = b64_url_encode(payload)\nsimulated_jwt = f'{encoded_header}.{encoded_payload}.<cryptographic_signature_here>'\nprint('JWT Format:', simulated_jwt)",
        "Demonstrating the three-part Base64URL structure of a JSON Web Token.",
        "Because the payload is merely Base64URL-encoded (not encrypted), anyone who possesses the token can decode and read the claims. However, any modification of the payload invalidates the signature, which can only be computed with the server's private secret key.",
        "Stateless authentication in microservices where services verify tokens without querying a central database session store.",
        ["Are claims inside a standard JWT encrypted or publicly readable?", "What standard registered claims are defined in RFC 7519 (`sub`, `exp`, `iat`, `iss`, `aud`)?"],
        ["Storing confidential secrets (like passwords or credit card numbers) in JWT payloads (JWT payloads are readable by anyone).", "Treating JWTs as an encrypted format rather than a signed integrity format."],
        "Critical distinction: Standard JWTs provide tamper-proof integrity, NOT confidentiality. Never put passwords or private data in a JWT payload.",
        ["[Symmetric vs Asymmetric JWT](authentication-and-security.md)", "[Access Tokens](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc7519"]
    ),

    # FA-BAS-086
    (
        "FA-BAS-086",
        "Symmetric vs Asymmetric JWT Signing (HS256 vs RS256)",
        "Symmetric signing (HS256) uses a single shared secret for both signing and verification, whereas asymmetric signing (RS256/ES256) uses a private key to sign and a public key to verify.",
        "Choosing between signing algorithms is a key architectural decision: 1) HS256 (HMAC-SHA256): Fast symmetric algorithm. A single secret key signs and verifies tokens. Every microservice that verifies tokens must possess the secret key; if one service is compromised, attackers can forge tokens for the entire system. 2) RS256 (RSA Signature with SHA-256): Asymmetric. An identity provider (Auth0, Keycloak, or your Auth service) holds the private key and signs tokens. All other microservices hold only the public key to verify tokens. Even if a consumer service is compromised, it cannot forge tokens.",
        "from jose import jwt\n\nSECRET_KEY = 'super_secret_symmetric_key_shared_by_monolith'\nALGORITHM = 'HS256'\n\n# HS256: Symmetric token generation\npayload = {'sub': 'user_42', 'scope': 'read:items'}\ntoken = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)\n\n# Verification uses the exact SAME secret key\ndecoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\nassert decoded['sub'] == 'user_42'",
        "Generating and verifying symmetric HS256 JWT tokens using python-jose.",
        "In HS256, HMAC computes `HMAC_SHA256(header + '.' + payload, secret)`. In RS256, the private key generates an RSA digital signature, and the public key verifies mathematical validity via modular exponentiation.",
        "HS256 is ideal for monolithic applications and small setups. RS256/ES256 is mandatory for distributed microservice architectures and public OAuth providers.",
        ["Why is RS256 preferred over HS256 in multi-service microservice architectures?", "What is the 'alg: none' vulnerability in flawed JWT implementations?"],
        ["Sharing a single symmetric HS256 secret key across 20 independent microservices, creating a massive blast radius.", "Using weak, short symmetric keys for HS256 (keys must be at least 256 bits of cryptographic entropy)."],
        "Architectural recommendation: Use HS256 for simple monoliths; use RS256/ES256 whenever multiple services need to verify tokens independently.",
        ["[JWT Architecture](authentication-and-security.md)", "[Access Tokens](authentication-and-security.md)"],
        ["https://auth0.com/blog/rs256-vs-hs256-whats-the-difference/"]
    ),

    # FA-BAS-087
    (
        "FA-BAS-087",
        "Creating Access Tokens with python-jose or PyJWT",
        "`jwt.encode()` serializes a dictionary of claims, an expiration timestamp, and a secret key into a signed JWT access token string.",
        "When a user successfully validates their credentials at a `/token` or `/login` endpoint, the server generates an access token. In FastAPI, `python-jose` or `pyjwt` is used to construct the token: developers assemble standard claims (`sub` for subject user ID, `exp` for expiration timestamp, `iat` for issued-at time), pass the secret key and algorithm, and return the resulting encoded string to the client.",
        "from datetime import datetime, timedelta, timezone\nfrom jose import jwt\n\nSECRET_KEY = 'enterprise_production_secret_key_change_me'\nALGORITHM = 'HS256'\n\ndef create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:\n    now = datetime.now(timezone.utc)\n    expire = now + (expires_delta or timedelta(minutes=15))\n    to_encode = {\n        'sub': subject,\n        'iat': now,\n        'exp': expire\n    }\n    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)\n\n# Generate access token expiring in 30 minutes\ntoken = create_access_token(subject='user_99', expires_delta=timedelta(minutes=30))\nprint('Generated Token:', token[:30] + '...')",
        "Constructing a signed access token with subject and UTC expiration claims.",
        "`jwt.encode()` converts timestamps to integer Unix epochs, serializes the payload to JSON, encodes to Base64URL, and computes the HMAC signature using the configured algorithm.",
        "Issuing bearer access tokens during user login, OAuth2 authorization, and API key exchange.",
        ["What claims are mandatory in a production access token?", "Why should access token lifetimes be kept short (e.g. 15-30 minutes)?"],
        ["Using `datetime.utcnow()` without timezone awareness in modern Python (use `datetime.now(timezone.utc)`).", "Setting excessively long access token lifetimes (e.g. 30 days) with no mechanism for revocation."],
        "Best practice: Keep access tokens short-lived (15-30 minutes) and issue refresh tokens for session renewal.",
        ["[Token Expiration](authentication-and-security.md)", "[Decoding Tokens](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#create-a-jwt-token"]
    ),

    # FA-BAS-088
    (
        "FA-BAS-088",
        "Token Expiration (exp Claim) and Timezone Handling",
        "The `exp` claim specifies the exact Unix timestamp after which a token must be rejected, and must always be generated using UTC timezone timestamps.",
        "Tokens without expiration timestamps are valid forever, meaning stolen tokens can be used indefinitely. RFC 7519 defines the `exp` claim as an integer representing the number of seconds since Unix Epoch (1970-01-01T00:00:00Z). A major Python bug occurs when generating expiration timestamps using local system time instead of UTC: if the server timezone differs from UTC, tokens expire immediately or remain valid hours longer than intended.",
        "from datetime import datetime, timedelta, timezone\nfrom jose import jwt, JWTError\n\nSECRET = 'my_secret'\n\n# ALWAYS use datetime.now(timezone.utc)\nvalid_until = datetime.now(timezone.utc) + timedelta(minutes=15)\npayload = {'sub': 'user_1', 'exp': valid_until}\ntoken = jwt.encode(payload, SECRET, algorithm='HS256')\n\n# Demonstrating automatic expiration rejection\npast_time = datetime.now(timezone.utc) - timedelta(minutes=1)\nexpired_token = jwt.encode({'sub': 'user_1', 'exp': past_time}, SECRET, algorithm='HS256')\n\ntry:\n    jwt.decode(expired_token, SECRET, algorithms=['HS256'])\nexcept JWTError as exc:\n    print('Expired token successfully caught by validator:', exc)",
        "Demonstrating UTC token expiration generation and automatic JWTError rejection.",
        "When `jwt.decode()` executes, it extracts `exp` and compares it to `time.time()`. If current time exceeds `exp`, it raises an `ExpiredSignatureError` (subclass of `JWTError`).",
        "Enforcing session timeouts across financial dashboards, e-commerce checkouts, and mobile banking apps.",
        ["How does clock skew between servers affect JWT expiration verification?", "Can a leeway parameter (e.g. `leeway=10`) be configured during JWT decoding?"],
        ["Using naive `datetime.now()` without UTC timezone, causing timezone-offset expiration bugs.", "Failing to check for `JWTError` during token decoding, causing unhandled 500 crashes."],
        "Timezone rule: Always use `datetime.now(timezone.utc)` for JWT timestamps; naive datetimes will cause intermittent validation bugs.",
        ["[Access Tokens](authentication-and-security.md)", "[Decoding Tokens](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4"]
    ),

    # FA-BAS-089
    (
        "FA-BAS-089",
        "Extracting and Decoding Bearer Tokens in Dependencies",
        "A FastAPI dependency combining `OAuth2PasswordBearer` and `jwt.decode()` extracts, decodes, and validates bearer tokens, injecting the authenticated user into route handlers.",
        "In production FastAPI architectures, endpoints do not parse tokens manually. Instead, an authentication dependency (e.g. `get_current_user`) declares `token: str = Depends(oauth2_scheme)`. The dependency calls `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`, validates the signature, extracts the user ID from `payload.get('sub')`, verifies the user exists in the database, and injects the user model directly into the route handler.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import OAuth2PasswordBearer\nfrom jose import jwt, JWTError\n\napp = FastAPI()\noauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')\nSECRET_KEY = 'production_secret_key'\nALGORITHM = 'HS256'\n\ndef get_current_user(token: str = Depends(oauth2_scheme)) -> dict:\n    credentials_exception = HTTPException(\n        status_code=status.HTTP_401_UNAUTHORIZED,\n        detail='Could not validate credentials',\n        headers={'WWW-Authenticate': 'Bearer'},\n    )\n    try:\n        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\n        username: str = payload.get('sub')\n        if username is None:\n            raise credentials_exception\n    except JWTError:\n        raise credentials_exception\n    return {'username': username, 'role': 'admin'}\n\n@app.get('/profile')\ndef user_profile(current_user: dict = Depends(get_current_user)):\n    return {'user': current_user['username']}",
        "Decoding JWT tokens and injecting current user via FastAPI dependency.",
        "FastAPI executes `oauth2_scheme` to extract the bearer string, then invokes `get_current_user`. If token decoding fails, it raises an HTTP 401 response and halts route execution.",
        "Universal pattern for securing private endpoints across all RESTful FastAPI services.",
        ["What is the significance of the `WWW-Authenticate: Bearer` response header?", "What happens if an attacker modifies the `sub` claim in transit?"],
        ["Omitting the `algorithms` list in `jwt.decode()`, exposing the app to algorithm confusion vulnerabilities.", "Catching generic `Exception` instead of `JWTError`, hiding unexpected internal bugs."],
        "Security mandate: Always explicitly pass `algorithms=[ALGORITHM]` to `jwt.decode()` to prevent algorithm switching attacks.",
        ["[OAuth2 Password Bearer](authentication-and-security.md)", "[Invalid Tokens](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#get-the-current-user"]
    ),

    # FA-BAS-090
    (
        "FA-BAS-090",
        "Handling Invalid or Expired Tokens with HTTPException(401) and WWW-Authenticate",
        "RFC 6750 mandates returning HTTP 401 Unauthorized with a `WWW-Authenticate: Bearer` header when token validation fails due to invalid signatures or expiration.",
        "When an incoming bearer token fails validation (e.g. signature mismatch, expired timestamp, or corrupted Base64 bytes), the server must communicate the failure adhering to RFC 6750. In FastAPI, this is done by raising `HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='...', headers={'WWW-Authenticate': 'Bearer'})`. The `WWW-Authenticate` header instructs client applications (like mobile apps or API gateways) that bearer authentication is required and has failed.",
        "from fastapi import FastAPI, HTTPException, status\n\napp = FastAPI()\n\ndef raise_auth_challenge(error_detail: str):\n    # RFC 6750 compliant 401 Unauthorized challenge\n    raise HTTPException(\n        status_code=status.HTTP_401_UNAUTHORIZED,\n        detail=error_detail,\n        headers={'WWW-Authenticate': 'Bearer error=\"invalid_token\"'}\n    )\n\n@app.get('/test-auth-fail')\ndef test_endpoint():\n    raise_auth_challenge('Token has expired or signature is invalid')",
        "Raising standard RFC 6750 compliant HTTP 401 challenges with WWW-Authenticate header.",
        "The ASGI server sets status code 401 and transmits the `WWW-Authenticate` header in the HTTP response line, signaling the client to refresh tokens or redirect to login.",
        "Standardizing API authentication responses for mobile clients, SDKs, and frontend error interceptors (e.g. Axios response interceptors).",
        ["What is the difference between HTTP 401 Unauthorized and HTTP 403 Forbidden?", "How do frontend interceptors use the 401 status to trigger automatic refresh token flows?"],
        ["Returning HTTP 403 Forbidden when a token is invalid (401 means unauthenticated; 403 means authenticated but lacking permission).", "Omitting the `WWW-Authenticate` header from 401 error responses (violates RFC 6750)."],
        "Clear rule: 401 = Missing or invalid credentials (try logging in); 403 = Authenticated, but your account lacks permission.",
        ["[Decoding Tokens](authentication-and-security.md)", "[Auth vs Authz](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc6750#section-3"]
    ),

    # FA-BAS-091
    (
        "FA-BAS-091",
        "Authentication vs Authorization in Software Architecture",
        "Authentication verifies WHO the user is (identity verification), whereas Authorization verifies WHAT the authenticated user is allowed to do (permission check).",
        "Confusing authentication (AuthN) with authorization (AuthZ) is a widespread conceptual error in software engineering. 1) Authentication (AuthN): Confirms identity through credentials (passwords, biometrics, API keys, JWTs). The output is an authenticated identity (e.g. `User(id=42, role='editor')`). 2) Authorization (AuthZ): Evaluates policies to determine whether that authenticated identity has permission to perform an action on a resource (e.g. Can User 42 delete Post 101?). AuthN always precedes AuthZ.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\n# 1. AUTHENTICATION: Who are you?\ndef authenticate_user(token: str = 'user_token') -> dict:\n    # Verifies identity; returns user principal\n    return {'user_id': 101, 'role': 'viewer'}\n\n# 2. AUTHORIZATION: What are you allowed to do?\ndef require_admin_role(user: dict = Depends(authenticate_user)):\n    if user['role'] != 'admin':\n        # 403 Forbidden: We know who you are, but you are not allowed to do this\n        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin role required')\n    return user\n\n@app.delete('/system/purge')\ndef purge_system(admin=Depends(require_admin_role)):\n    return {'status': 'purged'}",
        "Separating authentication (AuthN) from authorization (AuthZ) into distinct dependencies.",
        "FastAPI resolves `authenticate_user` first. If identity is invalid, it returns 401. If identity is valid, `require_admin_role` checks permissions; if unauthorized, it returns 403.",
        "Structuring enterprise security layers where authentication is handled at the gateway while authorization is enforced at microservice boundaries.",
        ["Why does an unauthenticated request return 401, but an unauthorized request return 403?", "How do RBAC and ABAC relate to authorization?"],
        ["Returning 401 when an authenticated user attempts an unauthorized action (should return 403 Forbidden).", "Coupling password checking and permission checking into a single tangled function."],
        "Mnemonic: AuthN = Identity (Who are you? -> 401 if failed); AuthZ = Permissions (Can you do this? -> 403 if failed).",
        ["[Invalid Tokens](authentication-and-security.md)", "[RBAC Implementation](authentication-and-security.md)"],
        ["https://en.wikipedia.org/wiki/Authentication"]
    ),

    # FA-BAS-092
    (
        "FA-BAS-092",
        "OAuth2 Password Flow and the /token Endpoint",
        "The OAuth2 Resource Owner Password Credentials flow exchanges a `username` and `password` submitted via form data for a JSON access token response.",
        "In the OAuth2 specification, the Password Flow allows trusted first-party clients (like your own mobile app or website) to exchange user credentials for a token. In FastAPI, the login endpoint accepts form data containing `username` and `password`, verifies credentials against the database, and returns a JSON payload conforming to OAuth2 specs: `{\"access_token\": \"...\", \"token_type\": \"bearer\"}`.",
        "from fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import OAuth2PasswordRequestForm\n\napp = FastAPI()\n\n@app.post('/token')\ndef login(form_data: OAuth2PasswordRequestForm = Depends()):\n    # form_data provides .username and .password parsed from application/x-www-form-urlencoded\n    if form_data.username != 'alice' or form_data.password != 'secret123':\n        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect credentials')\n    \n    # Standard OAuth2 response structure\n    return {\n        'access_token': 'jwt_access_token_sample_string',\n        'token_type': 'bearer',\n        'expires_in': 1800\n    }",
        "Implementing standard OAuth2 /token endpoint using OAuth2PasswordRequestForm.",
        "FastAPI parses the form data. Returning `{'access_token': '...', 'token_type': 'bearer'}` satisfies the OAuth2 RFC specification, allowing Swagger UI to store the token automatically.",
        "First-party web and mobile application authentication gateways.",
        ["Why does OAuth2 specify `application/x-www-form-urlencoded` instead of JSON for the `/token` endpoint?", "What is the security limitation of the Password Flow compared to Authorization Code with PKCE?"],
        ["Sending JSON to the `/token` endpoint from frontend clients instead of form data, resulting in 422 errors.", "Returning a non-standard response key (like `token` instead of `access_token`), breaking Swagger UI authentication."],
        "OAuth2 standard rule: The login response dictionary MUST contain `access_token` and `token_type` (lowercase `'bearer'`).",
        ["[OAuth2 Request Form](authentication-and-security.md)", "[Access Tokens](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/"]
    ),

    # FA-BAS-093
    (
        "FA-BAS-093",
        "Using OAuth2PasswordRequestForm for Standard OAuth2 Login",
        "`OAuth2PasswordRequestForm` is a dependency class provided by FastAPI that extracts standard OAuth2 form fields (`username`, `password`, `grant_type`, `scope`, `client_id`).",
        "RFC 6749 mandates that OAuth2 token requests submit credentials as form parameters (`application/x-www-form-urlencoded`). Rather than declaring individual `Form()` parameters manually, FastAPI provides `OAuth2PasswordRequestForm`. Using `form_data: OAuth2PasswordRequestForm = Depends()` automatically extracts `username`, `password`, `scope` (as a list of space-separated strings), and optional client credentials, while integrating seamlessly with Swagger UI's login dialog.",
        "from fastapi import FastAPI, Depends\nfrom fastapi.security import OAuth2PasswordRequestForm\n\napp = FastAPI()\n\n@app.post('/auth/login')\ndef login(form: OAuth2PasswordRequestForm = Depends()):\n    # form.username, form.password, form.scopes are available\n    return {\n        'received_username': form.username,\n        'requested_scopes': form.scopes,\n        'grant_type': form.grant_type\n    }",
        "Extracting OAuth2 login form parameters with OAuth2PasswordRequestForm.",
        "`OAuth2PasswordRequestForm` parses the incoming form body. In Swagger UI, it drives the modal that collects credentials and sends an encoded form POST to the configured `tokenUrl`.",
        "Powering login endpoints that serve both first-party frontend clients and interactive API documentation.",
        ["What library must be installed to use `OAuth2PasswordRequestForm` (`python-multipart`)?", "Can `OAuth2PasswordRequestForm` accept an email address in the `username` field?"],
        ["Forgetting to install `python-multipart`, leading to runtime server errors on form parsing.", "Attempting to send JSON to an endpoint using `OAuth2PasswordRequestForm`."],
        "Convenience tip: Even if your users log in with email, pass the email string into the `username` field of `OAuth2PasswordRequestForm`.",
        ["[OAuth2 Password Flow](authentication-and-security.md)", "[Form Data Parsing](routing-and-dependencies.md)"],
        ["https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#use-oauth2passwordrequestform"]
    ),

    # FA-BAS-094
    (
        "FA-BAS-094",
        "Storing Tokens: LocalStorage vs Secure HttpOnly Cookies",
        "Storing tokens in browser `localStorage` exposes them to theft via Cross-Site Scripting (XSS), whereas `HttpOnly`, `Secure`, `SameSite` cookies protect tokens from JavaScript access.",
        "Where web applications store access and refresh tokens in browser clients is a primary security design decision: 1) `localStorage` / `sessionStorage`: Convenient for single-page apps (easy to attach to `Authorization` headers), but COMPLETELY accessible to JavaScript. Any XSS vulnerability (e.g. a compromised third-party npm package) can read and exfiltrate the token. 2) `HttpOnly` Cookies: Inaccessible to JavaScript (`document.cookie` cannot read them), completely eliminating XSS token theft. However, cookie-based authentication requires CSRF protection (`SameSite` cookies or CSRF tokens).",
        "from fastapi import FastAPI, Response\n\napp = FastAPI()\n\n@app.post('/secure-login')\ndef secure_login(response: Response):\n    # Issue token inside a secure, HttpOnly, SameSite cookie\n    response.set_cookie(\n        key='access_token',\n        value='jwt_token_secret_123',\n        httponly=True,  # Inaccessible to JavaScript (XSS immune)\n        secure=True,    # Only transmitted over HTTPS\n        samesite='lax'  # CSRF defense\n    )\n    return {'status': 'authenticated'}",
        "Issuing an authentication cookie with HttpOnly, Secure, and SameSite flags.",
        "The browser stores the cookie in an encrypted internal jar. For subsequent requests to the same origin, the browser automatically attaches the `Cookie` header at the network level without exposing bytes to JavaScript execution contexts.",
        "Architecting banking portals, healthcare platforms, and enterprise dashboards with strict zero-trust security policies.",
        ["How does `SameSite='Lax'` vs `SameSite='Strict'` defend against CSRF attacks?", "What is the token-handling pattern recommended for high-security single-page applications (in-memory access token + HttpOnly refresh token)?"],
        ["Storing refresh tokens in `localStorage` where they can be exfiltrated by rogue browser extensions or XSS payloads.", "Setting cookies without `HttpOnly=True` or `Secure=True`."],
        "Security architecture consensus: Store long-lived refresh tokens in `HttpOnly, Secure, SameSite` cookies; keep short-lived access tokens in JavaScript memory.",
        ["[Cookie Extraction](routing-and-dependencies.md)", "[CSRF Protection](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#local-storage"]
    ),

    # FA-BAS-095
    (
        "FA-BAS-095",
        "Cross-Origin Resource Sharing (CORS) Basics and Security Implications",
        "CORS is a browser security mechanism that restricts web applications running at one origin from making HTTP requests to a different origin unless the server explicitly grants permission.",
        "Browsers enforce the Same-Origin Policy (SOP): an application running on `https://frontend.com` cannot read responses from `https://api.backend.com` unless the API server sends specific CORS response headers (`Access-Control-Allow-Origin`). When making cross-origin requests that modify data or send credentials, the browser first sends an HTTP `OPTIONS` preflight request. If the server does not respond with valid CORS headers, the browser blocks the frontend code from reading the response.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI()\n\n# Configure allowed frontend origins explicitly\norigins = [\n    'https://frontend.production.com',\n    'http://localhost:3000'\n]\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=origins,\n    allow_credentials=True,\n    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],\n    allow_headers=['Authorization', 'Content-Type']\n)",
        "Configuring CORSMiddleware to allow specific origins, methods, and credentials.",
        "For cross-origin calls, the browser sends `Origin: https://frontend.com`. FastAPI's `CORSMiddleware` checks the origin against `allow_origins`. If matched, it echoes back `Access-Control-Allow-Origin: https://frontend.com`.",
        "Enabling Single-Page Applications (React, Vue, Next.js) hosted on different domains to communicate with FastAPI backend APIs.",
        ["What is an HTTP OPTIONS preflight request and when does a browser trigger it?", "Why is setting `allow_origins=['*']` dangerous when `allow_credentials=True`?"],
        ["Setting `allow_origins=['*']` in production alongside `allow_credentials=True` (browsers explicitly reject this combination for security).", "Thinking CORS is a server-side firewall (CORS is purely enforced by browser clients; curl and Python scripts bypass CORS entirely)."],
        "Crucial insight: CORS is a browser security constraint, NOT a server-side firewall. Backend-to-backend API calls do not use CORS.",
        ["[CORSMiddleware](authentication-and-security.md)", "[Middleware](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/cors/"]
    ),

    # FA-BAS-096
    (
        "FA-BAS-096",
        "Configuring CORSMiddleware in FastAPI",
        "`CORSMiddleware` in FastAPI intercepts incoming HTTP and OPTIONS preflight requests, validating origins and injecting appropriate `Access-Control-*` response headers.",
        "FastAPI provides Starlette's `CORSMiddleware` for turn-key CORS configuration. Key configuration parameters include: 1) `allow_origins`: List of allowed origins (must include scheme and port, e.g. `['http://localhost:3000']`). 2) `allow_credentials`: Boolean indicating whether cookies and Authorization headers are allowed. 3) `allow_methods`: HTTP methods permitted (`['*']` or specific verbs). 4) `allow_headers`: HTTP headers accepted from the client. 5) `max_age`: Time in seconds that browsers can cache preflight responses.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI()\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=['https://mycompany.com'],\n    allow_credentials=True,\n    allow_methods=['*'],\n    allow_headers=['*'],\n    max_age=600  # Cache preflight response for 10 minutes\n)\n\n@app.get('/ping')\ndef ping(): return {'status': 'pong'}",
        "Adding CORSMiddleware with preflight cache max_age tuning.",
        "When an HTTP `OPTIONS` request arrives, `CORSMiddleware` intercepts it before route matching, verifies headers, and returns an immediate 200 OK with `Access-Control-Allow-Methods` and `Access-Control-Max-Age`.",
        "Connecting decentralized micro-frontends and mobile web apps to centralized backend microservices.",
        ["Why shouldn't `max_age` be omitted in high-traffic APIs (prevents redundant OPTIONS requests)?", "What happens if an origin has a trailing slash in `allow_origins`?"],
        ["Including trailing slashes in origins like `https://mycompany.com/` (origins must NOT have trailing slashes).", "Placing `CORSMiddleware` after other custom middleware that might short-circuit OPTIONS requests."],
        "Configuration tip: Origins must match `protocol://domain[:port]` exactly without paths or trailing slashes (e.g. `http://localhost:5173`).",
        ["[CORS Basics](authentication-and-security.md)", "[Middleware](middleware-and-exception-handling.md)"],
        ["https://fastapi.tiangolo.com/tutorial/cors/"]
    ),

    # FA-BAS-097
    (
        "FA-BAS-097",
        "HTTPS Enforcement and SSL/TLS Termination in Production",
        "Production APIs must mandate HTTPS via TLS termination at the reverse proxy (Nginx/ALB) and enforce it in FastAPI using `HTTPSRedirectMiddleware` and HSTS headers.",
        "Transmitting API traffic over plain HTTP exposes passwords, session tokens, and sensitive data to network eavesdropping and man-in-the-middle (MITM) attacks. In production architectures: 1) TLS Termination: An edge proxy (Nginx, Cloudflare, or AWS ALB) terminates SSL certificates and forwards traffic to Uvicorn. 2) HTTPS Redirection: FastAPI's `HTTPSRedirectMiddleware` automatically redirects any unencrypted HTTP request to HTTPS. 3) HSTS: Sending `Strict-Transport-Security` headers instructs browsers to never connect over plain HTTP.",
        "from fastapi import FastAPI\nfrom fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware\n\napp = FastAPI()\n\n# Automatically redirect all incoming HTTP traffic to HTTPS (307 Temporary Redirect)\napp.add_middleware(HTTPSRedirectMiddleware)\n\n@app.get('/secure')\ndef secure_data():\n    return {'status': 'Encrypted transit guaranteed'}",
        "Enforcing automatic HTTPS redirection using HTTPSRedirectMiddleware.",
        "`HTTPSRedirectMiddleware` inspects the ASGI `scope['scheme']` (or `X-Forwarded-Proto` header from reverse proxies). If `http`, it issues an immediate redirect to `https://`.",
        "Securing production applications against packet sniffing on public Wi-Fi networks and complying with SOC2/PCI-DSS standards.",
        ["Why is TLS usually terminated at the reverse proxy (Nginx) rather than inside Python/Uvicorn?", "What does the `Strict-Transport-Security` (HSTS) header instruct browsers to do?"],
        ["Terminating SSL inside Uvicorn worker processes in high-traffic production (offloading TLS to Nginx or hardware load balancers is much faster).", "Forgetting to configure `trusted_hosts` or proxy headers, leading to infinite redirect loops."],
        "Production pattern: Terminate TLS at Nginx / AWS ALB, pass `X-Forwarded-Proto: https` to Uvicorn, and enforce HSTS headers.",
        ["[Security Headers](authentication-and-security.md)", "[Production Deployment](../11-devops/nginx.md)"],
        ["https://www.starlette.io/middleware/#httpsredirectmiddleware"]
    ),

    # FA-BAS-098
    (
        "FA-BAS-098",
        "Hiding Sensitive Server Fingerprinting Headers (Server, X-Powered-By)",
        "Stripping revealing server fingerprint headers prevents attackers from identifying exact software versions to target known CVE vulnerabilities.",
        "By default, web servers and frameworks frequently broadcast software names and versions in response headers (e.g. `Server: uvicorn`, `X-Powered-By: FastAPI`). This metadata aids reconnaissance: if an unpatched vulnerability is announced for a specific Uvicorn or Python version, automated scanner bots query these headers to target vulnerable servers. Stripping or obfuscating these headers prevents trivial banner grabbing.",
        "from fastapi import FastAPI, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def strip_server_fingerprint(request, call_next):\n    response: Response = await call_next(request)\n    # Strip or genericize server fingerprint headers\n    if 'server' in response.headers:\n        del response.headers['server']\n    response.headers['X-Content-Type-Options'] = 'nosniff'\n    return response",
        "Stripping the Server header and adding protective nosniff headers via middleware.",
        "The custom middleware intercepts outgoing response messages before transmission to the socket, deleting the `Server` header set by the ASGI server.",
        "Hardening production deployments against automated security scanners and reconnaissance tools (Shodan, Nessus).",
        ["Why does security-by-obscurity (hiding headers) serve as defense-in-depth rather than absolute security?", "How can Nginx be configured to hide server tokens globally (`server_tokens off;`)?"],
        ["Relying solely on hiding headers without actually patching software vulnerabilities.", "Failing to configure reverse proxies (Nginx/Cloudflare) which often inject their own `Server` headers."],
        "Defense-in-depth tip: Set `server_tokens off;` in Nginx and configure Uvicorn with `--no-server-header` in production containers.",
        ["[Middleware](middleware-and-exception-handling.md)", "[Security Headers](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html"]
    ),

    # FA-BAS-099
    (
        "FA-BAS-099",
        "Preventing Cross-Site Scripting (XSS) in API Responses",
        "APIs prevent XSS by returning structured JSON with strict `application/json` Content-Type headers and avoiding reflective HTML rendering of unescaped user inputs.",
        "Cross-Site Scripting (XSS) occurs when malicious JavaScript is injected into web pages and executed in victim browsers. While classic server-side rendered apps (like Django templates) prevent XSS through HTML auto-escaping, REST APIs prevent XSS by: 1) Strictly returning `Content-Type: application/json` (browsers do not execute script tags inside JSON responses). 2) Adding `X-Content-Type-Options: nosniff` to prevent MIME-type sniffing. 3) Never echoing user inputs into HTML responses without escaping.",
        "from fastapi import FastAPI, Response\nfrom fastapi.responses import HTMLResponse\nimport html\n\napp = FastAPI()\n\n# SAFE: Returns JSON (Browser treats payload as data, never executes script)\n@app.get('/safe-json')\ndef get_safe_json(user_input: str):\n    return {'user_text': user_input}\n\n# SAFE HTML: Explicitly escapes user input before rendering\n@app.get('/safe-html', response_class=HTMLResponse)\ndef get_safe_html(user_input: str):\n    escaped = html.escape(user_input)\n    return f'<h1>Hello, {escaped}</h1>'",
        "Contrasting safe JSON responses with HTML escaping to prevent XSS injection.",
        "FastAPI default `JSONResponse` serializes payloads into JSON strings and sets `Content-Type: application/json`. Modern browsers will not execute `<script>` tags delivered in JSON media types.",
        "Protecting user comments, profile bios, and dynamic text rendering across Single-Page Web Applications.",
        ["Can an XSS payload execute if an API returns `Content-Type: text/html` with unescaped input?", "What does the `X-Content-Type-Options: nosniff` header do?"],
        ["Returning unescaped user input inside an `HTMLResponse`, allowing stored or reflected XSS.", "Assuming returning JSON is 100% immune if frontend frameworks use `dangerouslySetInnerHTML`."],
        "Core takeaway: REST APIs are inherently protected from XSS by returning `application/json`; danger only arises when rendering raw HTML or using `dangerouslySetInnerHTML` in React.",
        ["[Security Headers](authentication-and-security.md)", "[API Security](authentication-and-security.md)"],
        ["https://owasp.org/www-community/attacks/xss/"]
    ),

    # FA-BAS-100
    (
        "FA-BAS-100",
        "Preventing SQL Injection using Parameterized Queries in FastAPI",
        "SQL Injection is prevented by using parameterized queries and modern ORMs (SQLAlchemy, Tortoise), never interpolating raw user strings into SQL query templates.",
        "SQL Injection (SQLi) is one of the most devastating web vulnerabilities, allowing attackers to bypass authentication, dump database tables, or execute remote commands. In FastAPI, SQL injection occurs when developers concatenate user input into SQL strings (e.g. `f'SELECT * FROM users WHERE name = \"{name}\"'`). Parameterized queries separate SQL logic from untrusted user data: query parameters are sent to the database engine as separate protocol values, ensuring input can never be interpreted as executable SQL syntax.",
        "from fastapi import FastAPI\nfrom sqlalchemy import select, text\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n# INSECURE ANTI-PATTERN (DO NOT USE):\n# query = f\"SELECT * FROM users WHERE username = '{untrusted_input}'\"\n\n# SECURE PATTERN 1: SQLAlchemy 2.0 ORM / Core select\n# stmt = select(User).where(User.username == untrusted_input)\n\n# SECURE PATTERN 2: Parameterized raw SQL with bind parameters\nsecure_stmt = text('SELECT id, username FROM users WHERE username = :uname')\n# In database execution: session.execute(secure_stmt, {'uname': untrusted_input})",
        "Demonstrating parameterized SQL statements using bind variables with SQLAlchemy.",
        "In parameterized execution, the database engine compiles the SQL query plan before binding user parameter values. Even if the input contains `' OR 1=1 --`, it is treated strictly as a literal string value.",
        "Securing search bars, filter endpoints, and database queries across all backend applications.",
        ["Why doesn't sanitizing input with regex provide complete protection against SQL injection?", "How does SQLAlchemy 2.0 prevent SQL injection by default?"],
        ["Using Python f-strings or `.format()` to construct raw SQL queries inside route handlers.", "Believing NoSQL databases (MongoDB) are completely immune to injection attacks (NoSQL injection exists)."],
        "Absolute security rule: Never concatenate user inputs into SQL strings—always use SQLAlchemy ORM expressions or `:bind_params`.",
        ["[Database Integration](database-integration.md)", "[Pydantic Validation](pydantic-and-validation.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"]
    ),
]
