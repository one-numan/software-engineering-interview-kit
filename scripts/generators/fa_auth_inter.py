"""
fa_auth_inter.py
================
Intermediate FastAPI Authentication & Security Questions: FA-INT-076 to FA-INT-100 (25 questions)
"""

inter_data = [
    # FA-INT-076
    (
        "FA-INT-076",
        "Refresh Token Rotation Architecture and Revocation Lists",
        "Refresh Token Rotation (RTR) issues a new refresh token every time an access token is renewed and invalidates the entire token family if a previously used token is presented.",
        "Stateless JWT access tokens cannot be revoked before their expiration time without querying a database on every request (which defeats the purpose of stateless tokens). The standard architectural solution is Refresh Token Rotation (RTR): 1) Short-lived access tokens (15 mins) are issued alongside long-lived refresh tokens (7 days). 2) When exchanging a refresh token at `/auth/refresh`, the server invalidates the old refresh token and issues a brand-new refresh token. 3) If an attacker attempts to reuse an already-exchanged refresh token, the server detects token theft and immediately revokes all tokens belonging to that user family.",
        "from fastapi import FastAPI, HTTPException, status\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n# Simulated token family storage in Redis / DB\ntoken_families = {\n    'family_alice_01': {'active_token': 'refresh_v2', 'user_id': 'alice'}\n}\n\nclass RefreshRequest(BaseModel):\n    family_id: str\n    refresh_token: str\n\n@app.post('/auth/refresh')\ndef refresh_token(req: RefreshRequest):\n    family = token_families.get(req.family_id)\n    if not family:\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid session')\n    \n    # Theft detection: If client sends an old, previously used refresh token\n    if req.refresh_token != family['active_token']:\n        # Compromise detected: Purge entire family immediately\n        del token_families[req.family_id]\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Token theft detected - all active sessions revoked'\n        )\n    \n    # Rotate token\n    new_refresh = f'refresh_{req.refresh_token}_next'\n    family['active_token'] = new_refresh\n    return {'access_token': 'new_jwt_access_token', 'refresh_token': new_refresh}",
        "Implementing Refresh Token Rotation with automatic theft detection and session family purge.",
        "When an attacker intercepts a refresh token and uses it before the legitimate client, the legitimate client's subsequent refresh attempt will submit the old token. The server detects the replay and revokes all tokens in the family.",
        "Securing single-page web applications and mobile banking apps against persistent session hijacking.",
        ["What is a token family and how does it prevent attacker persistence?", "Why should refresh tokens be stored in secure HttpOnly cookies rather than localStorage?"],
        ["Using long-lived access tokens (e.g. 30 days) without any refresh token rotation.", "Failing to invalidate the entire token family when reuse of an old refresh token is detected."],
        "Security architecture rule: Always implement Refresh Token Rotation with family-wide revocation to protect against token exfiltration.",
        ["[Access Tokens](authentication-and-security.md)", "[Token Storage](authentication-and-security.md)"],
        ["https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation"]
    ),

    # FA-INT-077
    (
        "FA-INT-077",
        "Fine-Grained OAuth2 Scopes and Permission Verification with Security()",
        "`Security(dependency, scopes=['read', 'write'])` passes required permission scopes into the dependency via `SecurityScopes`, allowing declarative role and scope enforcement.",
        "In enterprise multi-tenant systems, permissions cannot be reduced to simple boolean flags (like `is_admin`). Granular operations require specific scopes (e.g. `items:read`, `items:write`, `reports:export`). In FastAPI, using `Security(get_current_user, scopes=['items:write'])` injects the declared scopes into a `SecurityScopes` parameter in your dependency, enabling automated scope checking and updating Swagger UI documentation.",
        "from fastapi import FastAPI, Security, HTTPException, status\nfrom fastapi.security import SecurityScopes, OAuth2PasswordBearer\n\napp = FastAPI()\noauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')\n\ndef check_scopes(security_scopes: SecurityScopes, token: str = Security(oauth2_scheme)):\n    # Simulated decoded scopes from JWT payload\n    user_token_scopes = ['items:read']\n    \n    for required_scope in security_scopes.scopes:\n        if required_scope not in user_token_scopes:\n            raise HTTPException(\n                status_code=status.HTTP_403_FORBIDDEN,\n                detail=f'Insufficient permissions: requires scope {required_scope}',\n                headers={'WWW-Authenticate': f'Bearer scope=\"{security_scopes.scope_str}\"'}\n            )\n    return {'user': 'alice', 'scopes': user_token_scopes}\n\n@app.get('/items', dependencies=[Security(check_scopes, scopes=['items:read'])])\ndef list_items():\n    return [{'item_id': 1, 'name': 'Scanner'}]",
        "Enforcing fine-grained OAuth2 scopes declaratively using Security and SecurityScopes.",
        "FastAPI inspects the `Security()` declaration and injects `SecurityScopes(scopes=...)` into the dependency parameters. It also records required scopes in OpenAPI's `security` object.",
        "Securing third-party developer APIs (like GitHub or Google Workspace APIs) where external apps request specific permission scopes.",
        ["How are OAuth2 scopes displayed in Swagger UI?", "What is the difference between `Security()` and `Depends()` in FastAPI?"],
        ["Using `Depends()` instead of `Security()`, which prevents scopes from being passed and documented in OpenAPI.", "Failing to return the `WWW-Authenticate: Bearer scope=...` header on 403 Forbidden responses."],
        "Design principle: `Security()` documents required scopes in OpenAPI and injects `SecurityScopes` into your dependency callable.",
        ["[Security vs Depends](routing-and-dependencies.md)", "[RBAC Implementation](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/"]
    ),

    # FA-INT-078
    (
        "FA-INT-078",
        "Role-Based Access Control (RBAC) Implementation with Custom Dependencies",
        "Role-Based Access Control (RBAC) groups permissions into roles (Admin, Editor, Viewer), enforced cleanly using parameterized callable class dependencies.",
        "Hardcoding `if user.role != 'admin': raise HTTPException(403)` across dozens of route functions violates DRY principles and creates maintenance bugs. A clean architectural approach in FastAPI uses a callable class dependency: `class RoleChecker: def __init__(self, allowed_roles): ... def __call__(self, user=Depends(get_current_user)): ...`. Routes declare `dependencies=[Depends(RoleChecker(['admin', 'superadmin']))]`, ensuring declarative, reusable authorization.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\ndef get_current_user():\n    return {'username': 'bob', 'role': 'editor'}\n\nclass RoleChecker:\n    def __init__(self, allowed_roles: list[str]):\n        self.allowed_roles = allowed_roles\n\n    def __call__(self, user: dict = Depends(get_current_user)):\n        if user.get('role') not in self.allowed_roles:\n            raise HTTPException(\n                status_code=status.HTTP_403_FORBIDDEN,\n                detail=f'Access forbidden: requires one of {self.allowed_roles}'\n            )\n        return user\n\n# Reusable role guards\nallow_admin = RoleChecker(['admin'])\nallow_editors = RoleChecker(['admin', 'editor'])\n\n@app.post('/articles', dependencies=[Depends(allow_editors)])\ndef create_article():\n    return {'status': 'article created'}",
        "Implementing declarative Role-Based Access Control (RBAC) using callable dependencies.",
        "FastAPI invokes `RoleChecker.__call__`, which first resolves `get_current_user`. If the user's role is not in `allowed_roles`, it raises an HTTP 403 Forbidden error before the route executes.",
        "Managing access permissions across SaaS platforms with hierarchical roles (Owner, Admin, Member, Guest).",
        ["How does RBAC differ from Attribute-Based Access Control (ABAC)?", "Can multiple role checkers be chained on a single endpoint?"],
        ["Hardcoding role checks inside endpoint handler bodies rather than using declarative dependencies.", "Returning 401 Unauthorized for role mismatches (403 Forbidden must be returned for authenticated role failures)."],
        "Architectural pattern: Parameterized callable classes (`RoleChecker(['admin'])`) provide the cleanest, most idiomatic RBAC in FastAPI.",
        ["[Class-Based Dependencies](routing-and-dependencies.md)", "[Auth vs Authz](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/"]
    ),

    # FA-INT-079
    (
        "FA-INT-079",
        "Attribute-Based Access Control (ABAC) and Policy Enforcement",
        "Attribute-Based Access Control (ABAC) evaluates dynamic policies based on attributes of the user, the resource, the action, and environmental context (time, IP, location).",
        "While RBAC assigns static roles, enterprise compliance often requires dynamic context: 'Users can only edit documents they created', or 'Managers can only approve expenses under $10,000 from within the corporate VPN during business hours'. ABAC evaluates policies against four attribute dimensions: Subject (user), Resource (document), Action (write), and Environment (IP, time). In FastAPI, ABAC is implemented via dependencies that extract the target resource and evaluate policy rules.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\ndef get_current_user(): return {'id': 101, 'department': 'engineering'}\n\ndef get_document(doc_id: int): return {'id': doc_id, 'owner_id': 101, 'dept': 'engineering'}\n\ndef verify_document_policy(\n    doc_id: int,\n    user: dict = Depends(get_current_user)\n):\n    doc = get_document(doc_id)\n    # ABAC Policy: User must own the document OR belong to the same department\n    is_owner = (user['id'] == doc['owner_id'])\n    same_dept = (user['department'] == doc['dept'])\n    \n    if not (is_owner or same_dept):\n        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='ABAC Policy Violation')\n    return doc\n\n@app.put('/documents/{doc_id}')\ndef update_document(doc: dict = Depends(verify_document_policy)):\n    return {'status': 'updated', 'doc_id': doc['id']}",
        "Enforcing dynamic Attribute-Based Access Control (ABAC) policy rules in dependencies.",
        "The dependency fetches the resource from the database, compares resource attributes against subject attributes, and enforces fine-grained policy rules before allowing mutation.",
        "Healthcare data access (HIPAA patient-doctor relationship checks), financial approval thresholds, and document collaboration tools.",
        ["What are the performance costs of evaluating ABAC policies on every request?", "How does Open Policy Agent (OPA) externalize ABAC policy evaluation in microservices?"],
        ["Trying to model complex dynamic ownership rules using static RBAC roles.", "Fetching database resources multiple times across route dependencies and handlers."],
        "Rule of thumb: Use RBAC for broad coarse-grained permissions; use ABAC for fine-grained dynamic ownership and contextual rules.",
        ["[RBAC Implementation](authentication-and-security.md)", "[Sub-dependencies](routing-and-dependencies.md)"],
        ["https://en.wikipedia.org/wiki/Attribute-based_access_control"]
    ),

    # FA-INT-080
    (
        "FA-INT-080",
        "Multi-Factor Authentication (MFA/2FA) Flow Integration with TOTP",
        "Multi-Factor Authentication enforces Time-based One-Time Password (TOTP, RFC 6238) verification before issuing fully authenticated session tokens.",
        "Single-factor password authentication is vulnerable to phishing and credential stuffing. In a 2FA workflow: 1) Initial login: User submits password. Server verifies password and returns a temporary, scoped token (`mfa_required`). 2) Second factor: User submits a 6-digit TOTP code generated by an authenticator app (Google Authenticator, Authy). 3) Verification: Server verifies the TOTP code against the user's secret key using `pyotp`. 4) Completion: Server issues the full-access JWT session token.",
        "import pyotp\nfrom fastapi import FastAPI, HTTPException, status\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n# User's shared TOTP base32 secret (stored encrypted in DB)\nUSER_TOTP_SECRET = pyotp.random_base32()\n\nclass MFAVerificationRequest(BaseModel):\n    temp_token: str\n    totp_code: str\n\n@app.post('/auth/verify-2fa')\ndef verify_2fa(req: MFAVerificationRequest):\n    totp = pyotp.TOTP(USER_TOTP_SECRET)\n    # Verify 6-digit TOTP code with 30-second time window\n    if not totp.verify(req.totp_code, valid_window=1):\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired 2FA code')\n    return {'status': 'authenticated', 'access_token': 'full_jwt_session_token'}",
        "Verifying 6-digit Time-based One-Time Passwords (TOTP) using pyotp.",
        "TOTP calculates HMAC-SHA1 over the current Unix time divided by 30 seconds. The output is truncated to 6 digits. `valid_window=1` accommodates slight clock drift between client devices and the server.",
        "Protecting privileged administrative accounts, fintech transactions, and user profile security settings.",
        ["What is the difference between TOTP (time-based) and HOTP (counter-based) authentication?", "Why should backup recovery codes be generated when users enable 2FA?"],
        ["Accepting unverified 2FA codes without checking clock skew.", "Storing TOTP shared secrets in plaintext in database tables."],
        "Security mandate: Always generate hashed single-use backup recovery codes when enabling MFA in case users lose their authenticator device.",
        ["[Password Hashing](authentication-and-security.md)", "[Access Tokens](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc6238"]
    ),

    # FA-INT-081
    (
        "FA-INT-081",
        "CSRF Protection for Cookie-Based Authentication in FastAPI",
        "Cross-Site Request Forgery (CSRF) is prevented by pairing `SameSite=Lax/Strict` cookies with Double Submit Cookie or Synchronizer Token patterns.",
        "When an API uses browser cookies for authentication, the browser automatically attaches the cookie to cross-site requests (e.g. an attacker site submitting a hidden form to `https://bank.com/transfer`). While `SameSite=Lax` cookies provide strong modern protection, complete defense requires the Double Submit Cookie pattern: the server sets an unguessable CSRF token in a readable cookie, and the frontend must read this token and attach it as a custom header (`X-CSRF-Token`) on all state-changing requests (POST/PUT/DELETE).",
        "import secrets\nfrom fastapi import FastAPI, Depends, HTTPException, Header, Cookie, status\n\napp = FastAPI()\n\ndef verify_csrf_token(\n    csrf_cookie: str = Cookie(default='', alias='csrf_token'),\n    csrf_header: str = Header(default='', alias='X-CSRF-Token')\n):\n    # Constant-time comparison between cookie and header\n    if not csrf_cookie or not secrets.compare_digest(csrf_cookie, csrf_header):\n        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF verification failed')\n    return True\n\n@app.post('/transfer-funds', dependencies=[Depends(verify_csrf_token)])\ndef transfer_funds():\n    return {'status': 'transfer successful'}",
        "Enforcing CSRF defense via Double Submit Cookie verification dependency.",
        "Because of the Same-Origin Policy, an attacker's website cannot read the CSRF cookie on your domain to construct the matching `X-CSRF-Token` header. If the header does not match the cookie, the request is rejected with 403.",
        "Protecting web applications that use cookie authentication for state-changing CRUD operations.",
        ["Why doesn't pure Bearer token authentication in the `Authorization` header require CSRF protection?", "What is the difference between `SameSite='Lax'` and `SameSite='Strict'` in cookie defense?"],
        ["Assuming Bearer tokens stored in `localStorage` need CSRF tokens (they are immune to CSRF because browsers do not attach headers automatically).", "Using predictable or sequential CSRF tokens instead of cryptographically secure random strings."],
        "Key insight: CSRF only affects cookie-based authentication. If your API exclusively uses `Authorization: Bearer <token>`, it is inherently immune to CSRF.",
        ["[Token Storage](authentication-and-security.md)", "[Constant-Time Comparison](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"]
    ),

    # FA-INT-082
    (
        "FA-INT-082",
        "Cryptographic Timing Attacks and Constant-Time Comparison",
        "Timing attacks measure microsecond response latency variations to deduce secret keys byte-by-byte; `secrets.compare_digest()` neutralizes this by executing in constant time.",
        "When comparing two strings in Python with `==`, the interpreter checks character by character and stops at the first mismatched byte. An attacker sending thousands of requests across a low-latency network can measure subtle timing differences (in CPU cycles) to determine whether the first byte matched, then the second byte, and so on. `secrets.compare_digest(a, b)` eliminates this by always comparing all bytes regardless of where differences occur.",
        "import secrets\nimport time\n\n# Simulated API key verification\nSTORED_SECRET = 'api_key_secure_secret_9981'\n\ndef secure_verify(incoming_key: str) -> bool:\n    # SECURE: Executes in constant time, leaking zero timing information\n    return secrets.compare_digest(incoming_key, STORED_SECRET)\n\nassert secure_verify('api_key_secure_secret_9981') is True\nassert secure_verify('wrong_key') is False",
        "Using secrets.compare_digest to prevent side-channel timing attacks.",
        "`secrets.compare_digest` calls CPython's C implementation `CRYPTO_memcmp`, which iterates over the entire byte buffer using bitwise OR operations without branching on mismatches.",
        "Validating webhook signatures (Stripe, GitHub), API keys, password reset tokens, and HMAC digests.",
        ["Why is `secrets.compare_digest` preferable to `hmac.compare_digest` (they are aliases in modern Python)?", "What network conditions are required for an attacker to execute a remote timing attack?"],
        ["Comparing cryptographic signatures or secrets using standard Python `==`.", "Writing custom comparison loops with early `break` statements."],
        "Security rule: Every cryptographic token, HMAC signature, and secret comparison in Python MUST use `secrets.compare_digest()`.",
        ["[Plaintext Passwords](authentication-and-security.md)", "[HMAC Request Signing](authentication-and-security.md)"],
        ["https://docs.python.org/3/library/secrets.html#secrets.compare_digest"]
    ),

    # FA-INT-083
    (
        "FA-INT-083",
        "Secure Token Blacklisting and Invalidation using Redis",
        "Stateless JWT revocation is achieved by blacklisting token unique identifiers (`jti`) in Redis with Time-To-Live (TTL) set to the token's remaining lifespan.",
        "Because JWTs are self-contained and verified locally, revoking a token upon user logout or password reset is an architectural challenge. The industry-standard solution is Redis Blacklisting: 1) Every token includes a unique `jti` (JWT ID) claim. 2) When a user logs out, the `jti` is stored in Redis with an expiration time equal to the token's remaining validity: `redis.set(f'blacklist:{jti}', 1, ex=remaining_seconds)`. 3) Authentication dependencies check if `jti` exists in Redis; if present, the token is rejected. 4) Once the token expires naturally, Redis automatically evicts the key.",
        "import time\nfrom fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\n# Simulated in-memory Redis key-value store with TTL\nredis_blacklist = set()\n\ndef verify_token_not_blacklisted(jti: str = 'token_uuid_101'):\n    # Check Redis for blacklisted JTI\n    if jti in redis_blacklist:\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has been revoked')\n    return jti\n\n@app.post('/auth/logout')\ndef logout(jti: str = Depends(verify_token_not_blacklisted)):\n    # Add JTI to Redis with TTL\n    redis_blacklist.add(jti)\n    return {'status': 'logged out successfully'}",
        "Revoking JWT tokens using Redis JTI blacklisting with automatic TTL eviction.",
        "Using Redis allows O(1) in-memory lookups. Because Redis TTL matches the token's remaining lifetime, the blacklist memory footprint remains strictly bounded and does not grow indefinitely.",
        "Implementing immediate user logout, terminating sessions after security alerts, and disabling compromised tokens.",
        ["Why is blacklisting `jti` in Redis better than storing all active sessions in a database?", "What happens to the Redis blacklist size if tokens have short lifetimes (e.g. 15 minutes)?"],
        ["Storing blacklisted tokens indefinitely without TTL expiration, causing Redis memory exhaustion.", "Oozing statefulness: Checking a relational SQL database on every single request instead of an in-memory Redis cluster."],
        "Architectural efficiency: Keeping access token lifespans short (15 mins) ensures Redis blacklists remain minuscule and auto-pruning.",
        ["[Token Expiration](authentication-and-security.md)", "[Redis Integration](../06-redis-and-messaging/redis.md)"],
        ["https://auth0.com/blog/blacklist-json-web-token-api-keys/"]
    ),

    # FA-INT-084
    (
        "FA-INT-084",
        "OAuth2 Authorization Code Flow with PKCE for Single-Page Apps (SPA)",
        "Proof Key for Code Exchange (PKCE, RFC 7636) secures the OAuth2 Authorization Code flow in public clients (SPAs and mobile apps) without requiring a client secret.",
        "Public clients (like React apps or iOS apps) cannot securely store a static `client_secret` because client-side source code can be decompiled. In the legacy flow, an attacker could intercept the authorization code and exchange it for a token. PKCE solves this: 1) The client generates a random `code_verifier` and computes its SHA-256 hash (`code_challenge`). 2) The client sends `code_challenge` to the authorization server. 3) When exchanging the authorization code, the client transmits the original `code_verifier`. 4) The server hashes it and verifies it matches the original challenge, proving the caller is the legitimate creator.",
        "import hashlib\nimport base64\nimport secrets\n\ndef generate_pkce_pair():\n    # 1. Generate high-entropy cryptographic code verifier\n    code_verifier = secrets.token_urlsafe(64)\n    \n    # 2. Compute SHA-256 digest\n    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()\n    \n    # 3. Base64URL encode without padding\n    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')\n    return code_verifier, code_challenge\n\nverifier, challenge = generate_pkce_pair()\nprint('PKCE Verifier length:', len(verifier))\nprint('PKCE Challenge:', challenge)",
        "Generating cryptographic PKCE code_verifier and code_challenge pair.",
        "PKCE neutralizes authorization code interception attacks on mobile operating systems and single-page applications by binding code exchange to the transient secret generated by the client.",
        "Securing Single-Page Web Applications (React, Angular, Vue) and mobile apps authenticating via Auth0, Okta, or Keycloak.",
        ["Why shouldn't Single-Page Applications ever use the OAuth2 Implicit Flow?", "How does the authorization server verify the PKCE exchange?"],
        ["Embedding `client_secret` in frontend React or mobile code repositories.", "Using plain text PKCE (`code_challenge_method=plain`) instead of SHA-256 (`S256`)."],
        "OAuth 2.1 standard mandate: All public and confidential clients must use Authorization Code Flow with PKCE; the Implicit Flow is formally deprecated.",
        ["[OAuth2 Password Flow](authentication-and-security.md)", "[Third-Party Social Logins](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc7636"]
    ),

    # FA-INT-085
    (
        "FA-INT-085",
        "Third-Party Social Logins (Google, GitHub, Auth0) with OAuth2",
        "Integrating social logins involves redirecting users to the identity provider, exchanging the returned authorization code for an ID token, and mapping user claims to internal accounts.",
        "Rather than managing passwords directly, modern applications allow users to 'Log in with Google' or 'Log in with GitHub'. In FastAPI, this is implemented using an asynchronous HTTP client (like `httpx`): 1) User clicks login; FastAPI redirects to Google's authorization URL. 2) Google authenticates user and redirects back to `/auth/google/callback?code=...`. 3) FastAPI exchanges the code for an ID token / access token via Google's token endpoint. 4) FastAPI decodes the user's verified email and issues an internal session JWT.",
        "import httpx\nfrom fastapi import FastAPI, HTTPException, Query\n\napp = FastAPI()\n\nGOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'\nGOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'\n\n@app.get('/auth/google/callback')\nasync def google_callback(code: str = Query(...)):\n    # In production: Exchange authorization code with Google using httpx\n    # async with httpx.AsyncClient() as client:\n    #     token_resp = await client.post(GOOGLE_TOKEN_URL, data={...})\n    #     user_resp = await client.get(GOOGLE_USERINFO_URL, headers={'Authorization': f'Bearer {token}'})\n    #     user_data = user_resp.json()\n    return {'status': 'authenticated', 'provider': 'google', 'user_email': 'user@gmail.com'}",
        "Handling third-party OAuth2 authorization callbacks using async HTTP client.",
        "FastAPI coordinates the back-channel HTTP POST to the provider's token endpoint, keeping the client secret securely on the server and never exposing it to the browser.",
        "Consumer SaaS onboarding, enterprise Google Workspace SSO, and developer developer portals with GitHub login.",
        ["How does OpenID Connect (OIDC) extend OAuth2 for identity verification?", "Why must the `state` parameter be verified during OAuth2 social login redirects to prevent CSRF?"],
        ["Omitting the `state` parameter in the initial redirect, exposing users to login CSRF attacks.", "Trusting user email without checking the `email_verified` claim from the identity provider."],
        "Security critical step: Always verify that `state` received in the callback matches the cryptographically signed cookie set during the redirect.",
        ["[PKCE Flow](authentication-and-security.md)", "[JWT Architecture](authentication-and-security.md)"],
        ["https://developers.google.com/identity/protocols/oauth2/openid-connect"]
    ),

    # FA-INT-086
    (
        "FA-INT-086",
        "JSON Web Encryption (JWE) vs Signed JWTs (JWS)",
        "JWS (JSON Web Signature) provides data integrity and tamper-detection while leaving payload contents readable, whereas JWE (JSON Web Encryption) encrypts the payload for confidentiality.",
        "Standard JWTs used in FastAPI are almost universally JWS (JSON Web Signatures): the payload is publicly readable Base64URL text, and the signature guarantees it has not been modified. However, if claims contain confidential data (such as medical records, personal phone numbers, or proprietary risk scores), standard JWS is unsafe. JSON Web Encryption (JWE, RFC 7516) encrypts the payload using symmetric content encryption keys wrapped with asymmetric public keys, ensuring only the intended recipient can decrypt and read the claims.",
        "from jose import jwe\n\n# JWE encrypts payload bytes using recipient's key\nSECRET_KEY = b'sixteen_byte_key!'  # 128-bit key\nplaintext_payload = b'Sensitive Medical Data: Patient HIV Negative'\n\n# Encrypt payload into compact 5-part JWE string\nencrypted_jwe = jwe.encrypt(plaintext_payload, SECRET_KEY, algorithm='dir', encryption='A128GCM')\nprint('JWE Compact Format (5 parts separated by dots):', encrypted_jwe[:30].decode() + '...')\n\n# Decrypt payload\ndecrypted = jwe.decrypt(encrypted_jwe, SECRET_KEY)\nassert decrypted == plaintext_payload",
        "Encrypting and decrypting sensitive payload claims using JWE.",
        "A JWE has five parts separated by dots: Header, Encrypted Key, Initialization Vector (IV), Ciphertext, and Authentication Tag. The data cannot be decoded or read without the decryption key.",
        "Healthcare API tokens, financial credit scoring payload transfers, and transmitting sensitive PII across untrusted networks.",
        ["What are the 5 parts of a JWE compared to the 3 parts of a JWS?", "What is the performance overhead of JWE encryption/decryption compared to JWS signatures?"],
        ["Assuming standard JWTs (JWS) hide sensitive user data from clients.", "Using JWE everywhere unnecessarily, introducing substantial CPU overhead for public claims like `sub` and `exp`."],
        "Rule of thumb: Use standard signed JWT (JWS) for 99% of authentication tokens; use JWE only when claims contain confidential secrets that clients must not read.",
        ["[JWT Architecture](authentication-and-security.md)", "[Symmetric vs Asymmetric JWT](authentication-and-security.md)"],
        ["https://datatracker.ietf.org/doc/html/rfc7516"]
    ),

    # FA-INT-087
    (
        "FA-INT-087",
        "OpenID Connect (OIDC) Discovery and JWKS Key Rotation",
        "OIDC Discovery (`.well-known/openid-configuration`) and JSON Web Key Sets (JWKS) allow FastAPI microservices to fetch public keys dynamically and verify asymmetric tokens without redeploying when keys rotate.",
        "In enterprise cloud environments, identity providers (Keycloak, Okta, Auth0) sign tokens with asymmetric keys that rotate every 30 to 90 days. Hardcoding the public key in your FastAPI application breaks authentication whenever key rotation occurs. By querying the provider's OIDC discovery endpoint and caching the JSON Web Key Set (`/.well-known/jwks.json`), FastAPI can match the `kid` (Key ID) header in incoming tokens and verify signatures dynamically.",
        "from jose import jwt\n\n# Simulated JWKS public key set fetched from identity provider\nsimulated_jwks = {\n    'keys': [{\n        'kty': 'RSA',\n        'kid': 'key_2026_primary',\n        'use': 'sig',\n        'alg': 'RS256'\n    }]\n}\n\ndef get_signing_key(token: str) -> str:\n    # Extract unverified header to inspect Key ID (kid)\n    unverified_header = jwt.get_unverified_header(token)\n    key_id = unverified_header.get('kid')\n    # In production: Match key_id against cached JWKS keys\n    return f'public_key_for_{key_id}'",
        "Extracting Key ID (kid) from token headers to match against dynamic JWKS keys.",
        "The application queries the identity provider's JWKS endpoint periodically or upon encountering an unknown `kid`. Caching public keys with a 1-hour TTL minimizes network overhead.",
        "Microservices validating tokens issued by central identity providers in multi-cloud Kubernetes clusters.",
        ["What is the purpose of the `kid` (Key ID) header parameter in a JWT?", "How do you handle key rotation gracefully without rejecting valid tokens during the rotation window?"],
        ["Hardcoding RSA public keys in configuration files or docker environment variables.", "Fetching the JWKS endpoint synchronously on every single incoming request (causes massive latency and rate limiting)."],
        "Observability standard: Cache the JWKS public keys in memory and refresh the cache lazily only when an incoming token contains a newer `kid`.",
        ["[Asymmetric JWT](authentication-and-security.md)", "[Social Logins](authentication-and-security.md)"],
        ["https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-sets"]
    ),

    # FA-INT-088
    (
        "FA-INT-088",
        "Securing File Upload Endpoints: MIME-Type Sniffing, Quotas, and Storage",
        "Securing file uploads requires validating real magic bytes (not just file extensions), enforcing file size limits, sanitizing filenames, and storing files outside the web root.",
        "File upload endpoints are among the highest-risk attack vectors in web applications. Attackers upload malicious PHP/Python scripts disguised as images, or upload multi-gigabyte ZIP bombs to exhaust disk storage. Comprehensive hardening requires: 1) Magic Byte Inspection: Use `python-magic` to check the actual file header bytes, ignoring spoofed client `Content-Type` headers. 2) Strict Size Limits: Reject uploads exceeding predefined thresholds. 3) Path Traversal Prevention: Strip filenames using `pathlib` or assign UUIDs. 4) Isolated Cloud Storage: Upload files directly to S3/GCS buckets with no execute permissions.",
        "import uuid\nfrom fastapi import FastAPI, UploadFile, File, HTTPException, status\n\napp = FastAPI()\nALLOWED_MAGIC_PREFIXES = {b'\\xff\\xd8\\xff': 'jpeg', b'\\x89PNG': 'png'}\n\n@app.post('/upload-avatar')\nasync def upload_avatar(file: UploadFile = File(...)):\n    # Read initial bytes to verify true file signature (magic bytes)\n    header_bytes = await file.read(4)\n    await file.seek(0)  # Reset buffer position\n    \n    is_valid = any(header_bytes.startswith(magic) for magic in ALLOWED_MAGIC_PREFIXES)\n    if not is_valid:\n        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid image file format')\n        \n    # Generate safe random filename; never trust client file.filename directly\n    safe_filename = f'{uuid.uuid4()}.img'\n    return {'status': 'uploaded', 'stored_as': safe_filename}",
        "Validating magic bytes and sanitizing filenames on file uploads.",
        "Checking magic bytes reads the binary file signature at offset 0. Spoofed extensions (e.g. `malware.exe` renamed to `avatar.png`) are immediately caught and rejected.",
        "User profile avatar uploads, document attachment ingestion, and customer KYC passport uploads.",
        ["Why is checking `file.content_type` or file extensions completely insufficient for security?", "How can SVG file uploads introduce Cross-Site Scripting (XSS) vulnerabilities?"],
        ["Trusting client-supplied filenames directly, allowing directory traversal attacks (`file.filename = '../../etc/passwd'`).", "Storing uploaded files in directories served directly by web servers with script execution permissions."],
        "Security rule: Never trust `file.filename` or `file.content_type`. Check magic bytes and generate random UUID filenames.",
        ["[File Uploads](routing-and-dependencies.md)", "[API Security](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html"]
    ),

    # FA-INT-089
    (
        "FA-INT-089",
        "Content Security Policy (CSP) and Security Headers Middleware",
        "Injecting standard security headers (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `HSTS`) hardens API clients and browsers against injection and clickjacking.",
        "While REST APIs primarily exchange JSON, modern security compliance standards (like OWASP Secure Headers) require web applications to return protective HTTP headers. By writing a simple ASGI middleware, FastAPI can enforce: 1) `X-Content-Type-Options: nosniff`: Prevents MIME-type confusion attacks. 2) `X-Frame-Options: DENY`: Prevents clickjacking by disabling embedding in iframes. 3) `Content-Security-Policy`: Restricts allowed resource origins. 4) `Strict-Transport-Security`: Mandates HTTPS.",
        "from fastapi import FastAPI, Request, Response\n\napp = FastAPI()\n\n@app.middleware('http')\nasync def add_security_headers(request: Request, call_next):\n    response: Response = await call_next(request)\n    # Inject standard OWASP protective security headers\n    response.headers['X-Content-Type-Options'] = 'nosniff'\n    response.headers['X-Frame-Options'] = 'DENY'\n    response.headers['X-XSS-Protection'] = '1; mode=block'\n    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'\n    response.headers['Content-Security-Policy'] = \"default-src 'self'\"\n    return response",
        "Enforcing OWASP security headers globally using HTTP middleware.",
        "The middleware wraps the request-response pipeline. Before the ASGI response headers are transmitted, the middleware injects these protective headers into the response dictionary.",
        "Meeting SOC2, ISO 27001, and banking security compliance checklists for web and API platforms.",
        ["What attack is prevented by the `X-Frame-Options: DENY` header?", "Why is `X-Content-Type-Options: nosniff` essential for APIs serving user-uploaded content?"],
        ["Failing to test CSP policies before deployment, inadvertently blocking valid CDN fonts or analytics scripts.", "Assuming security headers protect non-browser API clients (they only protect browser-based consumers)."],
        "Compliance takeaway: Adding security headers middleware takes 10 lines of code and immediately passes enterprise security scanners.",
        ["[Hiding Server Headers](authentication-and-security.md)", "[Middleware](middleware-and-exception-handling.md)"],
        ["https://owasp.org/www-project-secure-headers/"]
    ),

    # FA-INT-090
    (
        "FA-INT-090",
        "Rate Limiting Authentication Endpoints against Brute-Force Attacks",
        "Applying aggressive rate limiting specifically to `/token`, `/login`, and `/password-reset` endpoints blocks automated credential stuffing and dictionary attacks.",
        "While general API endpoints might allow 1,000 requests per minute, authentication endpoints must be constrained strictly (e.g. 5 failed login attempts per minute per IP or per username). Implementing rate limiting on authentication routes uses Redis sliding window counters. When the limit is exceeded, an HTTP 429 Too Many Requests response is returned with a `Retry-After: 60` header, frustrating automated brute-force scripts.",
        "from fastapi import FastAPI, Request, HTTPException, status\n\napp = FastAPI()\n\n# Simulated IP-based rate limiting dictionary\nfailed_attempts = {}\n\n@app.post('/auth/login')\ndef login(request: Request):\n    client_ip = request.client.host if request.client else 'anonymous'\n    attempts = failed_attempts.get(client_ip, 0)\n    \n    if attempts >= 5:\n        raise HTTPException(\n            status_code=status.HTTP_429_TOO_MANY_REQUESTS,\n            detail='Too many failed login attempts. Please wait 1 minute.',\n            headers={'Retry-After': '60'}\n        )\n    # Simulated failed attempt\n    failed_attempts[client_ip] = attempts + 1\n    return {'status': 'invalid credentials'}",
        "Enforcing request rate limiting on authentication endpoints to mitigate brute force.",
        "The limiter checks request counts against a sliding time window. In production, Redis Lua scripts record timestamps and reject requests that exceed allowed limits atomically.",
        "Defending login portals, password reset endpoints, and SMS OTP verification routes against automated bot attacks.",
        ["Why should rate limiting track both IP address AND targeted username simultaneously?", "What is Credential Stuffing and how does it differ from a brute-force dictionary attack?"],
        ["Rate limiting solely by IP address, allowing attackers to bypass limits using rotating residential proxy networks.", "Locking accounts permanently on brute-force attempts without an automated unlock mechanism (creates Denial of Service for legitimate users)."],
        "Defense strategy: Rate limit by both client IP (to stop rapid scripts) and targeted username (to stop distributed proxy credential stuffing).",
        ["[Rate Limiting Dependency](routing-and-dependencies.md)", "[Redis Integration](../06-redis-and-messaging/redis.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#protect-against-automated-attacks"]
    ),

    # FA-INT-091
    (
        "FA-INT-091",
        "Mutual TLS (mTLS) Authentication for Inter-Microservice Security",
        "Mutual TLS (mTLS) enforces two-way cryptographic verification where both the client and the server present valid X.509 certificates to establish zero-trust communication.",
        "Standard HTTPS only validates the server's identity to the client. In zero-trust inter-service architectures (service mesh), servers must also cryptographically verify the client's identity at the transport layer. In mTLS: 1) Client initiates TLS handshake. 2) Server presents its certificate. 3) Server requests client certificate. 4) Client presents its certificate signed by the internal Certificate Authority (CA). 5) Socket connection is established only if both certificates are valid.",
        "# Production Uvicorn command launching mTLS with client certificate verification\n# $ uvicorn main:app \\\n#     --ssl-keyfile=/certs/server.key \\\n#     --ssl-certfile=/certs/server.crt \\\n#     --ssl-ca-certs=/certs/internal-ca.crt \\\n#     --ssl-cert-reqs=2  # ssl.CERT_REQUIRED: Mandates valid client certificate\n\nfrom fastapi import FastAPI, Request\n\napp = FastAPI()\n\n@app.get('/internal/rpc')\ndef internal_rpc(request: Request):\n    # Connection is cryptographically guaranteed to originate from trusted microservice\n    return {'status': 'mTLS verified'}",
        "Configuring Uvicorn with client certificate requirements for mutual TLS.",
        "The TLS handshake fails at the socket level if the connecting client cannot present a certificate signed by the trusted CA (`--ssl-ca-certs`), dropping the connection before any Python or HTTP processing occurs.",
        "Securing internal microservice RPC calls, payment processing pipelines, and Kubernetes pod-to-pod communications.",
        ["Why is mTLS superior to static API keys for microservice-to-microservice authentication?", "What role does a Service Mesh (Istio, Linkerd) play in automating mTLS certificates?"],
        ["Using mTLS for public consumer-facing web traffic (regular browsers do not have client certificates installed).", "Failing to automate certificate rotation, causing catastrophic service outages when CA certificates expire."],
        "Zero-trust standard: Use mTLS for backend internal microservices; use OAuth2/JWT for edge user traffic.",
        ["[HTTPS Enforcement](authentication-and-security.md)", "[Zero-Trust Architecture](authentication-and-security.md)"],
        ["https://en.wikipedia.org/wiki/Mutual_authentication"]
    ),

    # FA-INT-092
    (
        "FA-INT-092",
        "Tenant Isolation and Cross-Tenant Data Leakage Prevention",
        "Enforcing tenant boundaries requires deriving `tenant_id` from trusted cryptographically verified JWT claims rather than untrusted client URL parameters or request bodies.",
        "In multi-tenant SaaS platforms, the most catastrophic security vulnerability is Cross-Tenant Data Leakage (Customer A seeing Customer B's confidential data). This occurs when endpoints accept `tenant_id` from client request bodies or URL parameters (`/api/records?tenant_id=123`), allowing malicious users to query other tenants by changing the ID. Secure isolation requires deriving `tenant_id` exclusively from the verified JWT token and scoping all database queries with `where(Tenant.id == token_tenant_id)`.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\ndef get_authenticated_tenant() -> str:\n    # Extracted from cryptographically signed JWT claim, NEVER from request params\n    verified_jwt_claims = {'sub': 'user_1', 'tenant_id': 'tenant_acme_corp'}\n    return verified_jwt_claims['tenant_id']\n\n@app.get('/invoices')\ndef list_invoices(tenant_id: str = Depends(get_authenticated_tenant)):\n    # Database query is strictly scoped to the authenticated tenant\n    query = f'SELECT * FROM invoices WHERE tenant_id = :tenant_id'\n    return {'tenant': tenant_id, 'query_scope': query}",
        "Deriving tenant context securely from verified JWT claims rather than client input.",
        "Because the JWT signature is verified with the server's private key, the client cannot tamper with the `tenant_id` claim. All database queries execute with mandatory tenant filters.",
        "B2B SaaS platforms hosting healthcare, legal, or financial data across corporate customers.",
        ["How does Row-Level Security (RLS) in PostgreSQL enforce tenant isolation at the database engine layer?", "What is the difference between schema-based multi-tenancy and shared-table multi-tenancy?"],
        ["Accepting `tenant_id` from client request bodies or query parameters, creating Broken Object Level Authorization (BOLA).", "Reusing database connections from pools without resetting tenant search paths or session variables."],
        "Security golden rule: Never trust client-supplied tenant identifiers; always extract `tenant_id` from cryptographically verified authentication tokens.",
        ["[Tenant-Scoped DI](routing-and-dependencies.md)", "[Database Integration](database-integration.md)"],
        ["https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"]
    ),

    # FA-INT-093
    (
        "FA-INT-093",
        "HMAC Request Signing for Webhook Verification (Stripe and GitHub style)",
        "Webhook endpoints verify authenticity by computing the HMAC-SHA256 signature over the raw request body bytes and comparing it against the incoming signature header.",
        "When an API receives webhooks from external providers (Stripe, GitHub, Shopify), attackers can forge fake webhook events (e.g. 'payment succeeded') to trick your system. Webhook providers sign payloads using a shared secret. The webhook receiver must compute `HMAC_SHA256(secret, raw_request_body)` and verify that the computed digest matches the signature in the header using `secrets.compare_digest`.",
        "import hmac\nimport hashlib\nimport secrets\nfrom fastapi import FastAPI, Request, HTTPException, Header, status\n\napp = FastAPI()\nWEBHOOK_SECRET = b'whsec_shared_secret_key_12345'\n\n@app.post('/webhooks/stripe')\nasync def stripe_webhook(request: Request, stripe_signature: str = Header(..., alias='Stripe-Signature')):\n    # CRITICAL: Must read raw unparsed byte stream\n    raw_body = await request.body()\n    \n    # Compute HMAC-SHA256 digest over raw bytes\n    computed_signature = hmac.new(WEBHOOK_SECRET, raw_body, hashlib.sha256).hexdigest()\n    \n    # Constant-time comparison against incoming header\n    if not secrets.compare_digest(computed_signature, stripe_signature):\n        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid webhook signature')\n        \n    return {'status': 'verified', 'event': 'payment.succeeded'}",
        "Verifying webhook HMAC-SHA256 signatures over raw request bytes.",
        "HMAC creates a cryptographic digest using a shared secret key. If even a single byte of the payload is modified in transit, or if the attacker does not possess the secret, the signatures will not match.",
        "Ingesting payment notifications from Stripe, Git push webhooks from GitHub, and billing alerts from Shopify.",
        ["Why must you verify the signature using `await request.body()` instead of parsed JSON (`await request.json()`)?", "How do timestamped signatures prevent replay attacks on webhooks?"],
        ["Verifying HMAC against re-serialized JSON (key ordering and whitespace differences will break the signature match).", "Comparing HMAC signatures using standard `==` instead of `secrets.compare_digest()`."],
        "Critical webhook rule: Always compute the HMAC over raw request bytes (`await request.body()`) before any JSON parsing occurs.",
        ["[Constant-Time Comparison](authentication-and-security.md)", "[Raw Request Injection](routing-and-dependencies.md)"],
        ["https://stripe.com/docs/webhooks/signatures"]
    ),

    # FA-INT-094
    (
        "FA-INT-094",
        "Password Reset Architecture: Ephemeral Tokens and Security Pitfalls",
        "Password reset workflows require short-lived, single-use, cryptographically signed tokens containing a hash of the user's current password to guarantee instant invalidation.",
        "Insecure password reset flows are a common cause of account takeovers. A robust architecture requires: 1) Short lifespan: Reset tokens should expire in 15 minutes. 2) Single-use: Once used, the token cannot be reused. 3) Self-invalidating design: Include a hash of the user's *current* password hash in the token payload (`token_secret = HMAC(user.password_hash)`). As soon as the password is changed, the token secret changes, instantly invalidating any other pending reset links.",
        "from datetime import datetime, timedelta, timezone\nfrom jose import jwt\n\nSECRET = 'global_app_secret'\n\ndef generate_password_reset_token(user_id: int, current_pwd_hash: str) -> str:\n    expire = datetime.now(timezone.utc) + timedelta(minutes=15)\n    # Bind token to user's CURRENT password hash\n    payload = {\n        'sub': str(user_id),\n        'pwd_fingerprint': current_pwd_hash[:16],\n        'exp': expire\n    }\n    return jwt.encode(payload, SECRET, algorithm='HS256')\n\n# When password is changed, current_pwd_hash updates, invalidating all old reset tokens",
        "Generating self-invalidating password reset tokens bound to the current password hash.",
        "If a user requests multiple reset emails, or if an attacker gains access to an old reset link, the link is rendered useless the moment the password hash in the database is modified.",
        "User recovery flows across all consumer and enterprise web applications.",
        ["Why should password reset endpoints always return generic success messages ('If your email exists, a link was sent')?", "How can user enumeration be prevented during password reset requests?"],
        ["Returning different responses for existing vs non-existing emails, allowing attackers to enumerate registered users.", "Creating reset tokens that do not expire or remain valid after the password has already been changed."],
        "Anti-enumeration rule: Always return the identical response message regardless of whether the email was found in the database.",
        ["[Password Hashing](authentication-and-security.md)", "[Token Expiration](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html"]
    ),

    # FA-INT-095
    (
        "FA-INT-095",
        "Session Invalidation on Password Change or Compromise",
        "Changing a password or triggering security alerts must immediately revoke all existing active sessions and refresh tokens across all user devices.",
        "When an account password is changed (e.g. after a compromise or forgotten password recovery), any existing session held by an attacker must be immediately terminated. In stateless JWT architectures, this is accomplished by incrementing a `token_version` integer in the user's database record (or updating a `password_changed_at` timestamp). Every incoming token's version claim is verified against the database; if outdated, the token is rejected.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI()\n\n# User DB record contains a token_version counter\nuser_db = {'user_1': {'password_hash': '...', 'token_version': 3}}\n\ndef verify_token_version(user_id: str = 'user_1', token_ver: int = 2):\n    current_user = user_db.get(user_id)\n    # If token_version in JWT is older than DB version, session is revoked\n    if not current_user or token_ver < current_user['token_version']:\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail='Password was changed; please log in again'\n        )\n    return current_user\n\n@app.get('/me')\ndef get_me(user=Depends(verify_token_version)):\n    return {'status': 'active'}",
        "Enforcing session revocation on password change using token_version checks.",
        "Incrementing `user.token_version` immediately invalidates all outstanding access and refresh tokens across all mobile and web devices without requiring a Redis blacklist.",
        "Account security dashboards ('Log out of all devices') and post-password-reset session termination.",
        ["How does the `token_version` pattern compare to Redis token blacklists in scalability?", "What is the trade-off of querying the database for `token_version` on every request?"],
        ["Allowing existing sessions to remain active after a user changes their compromised password.", "Requiring a full database write per request instead of caching `token_version` in Redis."],
        "Design pattern: Use `token_version` in user tables and cache it in Redis for sub-millisecond session validation.",
        ["[Redis Blacklisting](authentication-and-security.md)", "[Password Reset](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html"]
    ),

    # FA-INT-096
    (
        "FA-INT-096",
        "Securing WebSockets: Handshake Authentication vs Frame-Level Authentication",
        "WebSockets authenticate primarily during the initial HTTP handshake using ticket tokens or cookies, rejecting unauthorized connections before protocol upgrade.",
        "WebSocket connections begin as standard HTTP requests that 'upgrade' to the WebSocket protocol. Authentication can occur at two stages: 1) Handshake Authentication (Recommended): The client sends an ephemeral single-use ticket token in the connection query parameters or cookies. FastAPI validates the token before calling `await websocket.accept()`. If invalid, the server closes the connection immediately with status code 1008 (Policy Violation). 2) Frame-Level Authentication: Authenticating individual message frames after the socket is open, useful for long-lived sockets where credentials rotate.",
        "from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status\n\napp = FastAPI()\n\nasync def verify_ws_ticket(ticket: str = Query(...)) -> str:\n    # In production: Verify ephemeral single-use ticket in Redis\n    if ticket != 'valid_ticket_123':\n        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)\n    return 'authenticated_user_alice'\n\n@app.websocket('/ws/feed')\nasync def secure_feed(websocket: WebSocket, user: str = Query('alice')):\n    # Reject unauthorized connections before accepting socket\n    await websocket.accept()\n    await websocket.send_text(f'Secure stream established for {user}')\n    await websocket.close()",
        "Authenticating WebSocket connections during the initial HTTP handshake.",
        "Rejecting the connection before `websocket.accept()` prevents allocating socket memory and worker tasks for unauthorized attackers.",
        "Real-time financial trading tickers, collaborative whiteboard tools, and private customer chat channels.",
        ["Why can't standard browser WebSocket APIs send custom `Authorization: Bearer` headers during handshakes?", "What is the ticket-token pattern for WebSocket authentication?"],
        ["Accepting the WebSocket connection before validating credentials, consuming server memory on unauthorized clients.", "Passing long-lived JWTs in WebSocket query strings where they persist in server access logs."],
        "Browser workaround: Standard browser `new WebSocket(url)` cannot send headers; exchange your JWT for a 30-second single-use ticket token and pass it via query param.",
        ["[WebSocket Routing](routing-and-dependencies.md)", "[Token Storage](authentication-and-security.md)"],
        ["https://fastapi.tiangolo.com/advanced/websockets/"]
    ),

    # FA-INT-097
    (
        "FA-INT-097",
        "Auditing and Security Event Logging (OWASP Logging Guide)",
        "Security event logging records authentication attempts, permission failures, password resets, and privilege changes with structured context while strictly redacting PII and secrets.",
        "Incident response and forensic investigation require comprehensive audit logs. OWASP guidelines mandate logging all security events: successful/failed logins, access denials (403), password changes, and admin actions. Logs must be structured (JSON) and include: timestamp (UTC), event type, actor ID, client IP, user agent, and correlation ID. Logs must strictly redact sensitive data: passwords, credit cards, auth tokens, and personally identifiable information (PII).",
        "import logging\nfrom fastapi import FastAPI, Request, HTTPException, status\n\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger('security.audit')\n\napp = FastAPI()\n\n@app.post('/auth/login')\ndef login(username: str, request: Request):\n    client_ip = request.client.host if request.client else 'unknown'\n    # Simulate failed login attempt\n    login_successful = False\n    \n    if not login_successful:\n        # Structured security audit log entry (PII/secrets redacted)\n        logger.warning('SECURITY_EVENT: LOGIN_FAILURE',\n            extra={\n                'event': 'AUTH_FAILURE',\n                'targeted_user': username,\n                'client_ip': client_ip,\n                'user_agent': request.headers.get('User-Agent')\n            }\n        )\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')",
        "Recording structured security audit logs for failed authentication events.",
        "Structured logs are forwarded to centralized Security Information and Event Management (SIEM) systems (Datadog, Splunk, Elastic) for automated anomaly detection and alerting.",
        "Complying with SOC2, PCI-DSS, and ISO 27001 audit trail requirements across enterprise platforms.",
        ["What sensitive fields must be strictly redacted from application logs according to OWASP?", "How do SIEM tools use audit logs to detect automated brute-force attacks?"],
        ["Logging raw request bodies containing plaintext passwords, API keys, or credit cards.", "Omitting client IP addresses or timestamps from security log messages."],
        "Compliance mandate: Log WHO did WHAT, WHEN, and from WHERE, but NEVER log passwords, credit card numbers, or full tokens.",
        ["[Masking Sensitive Fields](pydantic-and-validation.md)", "[Brute-Force Rate Limiting](authentication-and-security.md)"],
        ["https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"]
    ),

    # FA-INT-098
    (
        "FA-INT-098",
        "Detecting Credential Stuffing and Automated Bot Attacks",
        "Credential stuffing attacks use stolen username/password lists from other breaches; mitigation involves CAPTCHA verification, IP reputation checks, and device fingerprinting.",
        "Attackers use automated botnets to test millions of breached credentials against your `/login` endpoint. Standard IP rate limiting is often defeated by rotating residential proxies. Mitigating credential stuffing requires multi-layered defense: 1) Rate limiting by targeted username. 2) Bot detection: Integrating Cloudflare Turnstile or Google reCAPTCHA v3 on login forms. 3) IP Reputation: Blocking known proxy and Tor exit nodes. 4) Leaked credential checks: Checking passwords against HaveIBeenPwned API during registration.",
        "from fastapi import FastAPI, Header, HTTPException, status\n\napp = FastAPI()\n\ndef verify_bot_challenge(x_turnstile_token: str = Header(default='')):\n    # In production: Verify token against Cloudflare Turnstile / reCAPTCHA API\n    if not x_turnstile_token:\n        raise HTTPException(\n            status_code=status.HTTP_400_BAD_REQUEST,\n            detail='Bot verification challenge required'\n        )\n    return True\n\n@app.post('/auth/login')\ndef bot_protected_login(bot_check: bool = Header(..., alias='X-Bot-Verified')):\n    return {'status': 'human verified'}",
        "Enforcing bot verification challenges on authentication endpoints.",
        "Bot mitigation services score client browser behavior (mouse movements, TLS fingerprints) before issuing a cryptographically signed token that the backend verifies.",
        "Protecting high-value consumer portals (e-commerce, airline loyalty points, streaming platforms) from account takeover.",
        ["How do attackers use rotating residential proxies to bypass IP-based rate limiters?", "What is the difference between interactive CAPTCHAs and invisible risk-based scoring (Cloudflare Turnstile)?"],
        ["Relying exclusively on IP-based rate limiting to stop credential stuffing.", "Using intrusive visual puzzles that frustrate legitimate users instead of modern invisible bot detection."],
        "Anti-bot strategy: Combine invisible challenge tokens (Turnstile) with username-based velocity limits to neutralize credential stuffing.",
        ["[Brute-Force Rate Limiting](authentication-and-security.md)", "[Security Audit](authentication-and-security.md)"],
        ["https://owasp.org/www-community/attacks/Credential_stuffing"]
    ),

    # FA-INT-099
    (
        "FA-INT-099",
        "Handling Deprecated Crypto Algorithms (Migrating SHA1/MD5/DES to Argon2id)",
        "Migrating legacy weak password hashes to Argon2id is achieved transparently upon user login using Passlib's `needs_update()` and automatic re-hashing.",
        "Legacy applications frequently contain outdated, insecure password hashes (such as MD5, SHA-1, or plain SHA-256). Because password hashing is one-way, you cannot convert existing hashes in the database directly. The industry-standard migration pattern re-hashes passwords transparently when users log in: 1) Verify the user's password against the legacy hash algorithm. 2) If valid, check `pwd_context.needs_update(stored_hash)`. 3) If true, hash the password using modern Argon2id and update the database record.",
        "from passlib.context import CryptContext\n\n# Configure modern Argon2 as default, but keep legacy md5 for verification\npwd_context = CryptContext(schemes=['argon2', 'md5_crypt'], deprecated=['md5_crypt'])\n\n# Legacy hash stored in database\nlegacy_md5_hash = '$1$salt$qR3M2auhz02.N7D8N2g..1'\n\ndef authenticate_and_upgrade(password: str, stored_hash: str):\n    is_valid = pwd_context.verify(password, stored_hash)\n    if not is_valid:\n        return False, None\n    \n    # Check if hash needs upgrade to modern Argon2\n    if pwd_context.needs_update(stored_hash):\n        new_hash = pwd_context.hash(password)\n        return True, new_hash  # Save new_hash to database!\n    return True, None",
        "Transparently upgrading legacy password hashes to modern Argon2 during login.",
        "The migration happens lazily without forcing a mass password reset. Users who log in are seamlessly upgraded to state-of-the-art Argon2id encryption.",
        "Modernizing legacy monoliths and migrated database backups without disrupting active users.",
        ["Why can't you migrate legacy password hashes to Argon2 using a batch database script?", "What should happen to inactive user accounts that never log in to be upgraded?"],
        ["Forcing an immediate mass password reset across all users when migrating hash algorithms.", "Continuing to hash new passwords with legacy algorithms for consistency with old records."],
        "Migration rule: Configure `deprecated=['legacy_scheme']` in `CryptContext`; modern algorithms hash all new passwords while upgrading old ones upon login.",
        ["[Password Hashing](authentication-and-security.md)", "[Plaintext Passwords](authentication-and-security.md)"],
        ["https://passlib.readthedocs.io/en/stable/lib/passlib.context.html#upgrading-hashes"]
    ),

    # FA-INT-100
    (
        "FA-INT-100",
        "Pentesting FastAPI: Common Vulnerabilities Found in Security Audits",
        "Common vulnerabilities in FastAPI audits include BOLA (Broken Object Level Authorization), CORS misconfiguration, unhandled exceptions leaking stack traces, and unauthenticated Swagger UI.",
        "Independent penetration tests and security audits consistently uncover recurring vulnerabilities in FastAPI applications: 1) BOLA / IDOR: Endpoints accepting IDs (e.g. `/orders/{id}`) without verifying that the authenticated user owns that order. 2) Information Disclosure: Server returning full Python tracebacks in 500 errors in production. 3) CORS Wildcards: Allowing `*` with credentials. 4) Unprotected OpenAPI Docs: Exposing `/docs` and `/redoc` publicly on internal microservices. 5) Mass Assignment: Updating database models with unvalidated input dictionaries.",
        "from fastapi import FastAPI, Depends, HTTPException, status\n\napp = FastAPI(docs_url=None, redoc_url=None)  # Disables public docs in production\n\ndef get_current_user(): return {'user_id': 101}\n\n# SAFE FROM BOLA: Verifies resource ownership\n@app.get('/orders/{order_id}')\ndef get_order(order_id: int, current_user=Depends(get_current_user)):\n    db_order = {'id': order_id, 'owner_id': 101}\n    if db_order['owner_id'] != current_user['user_id']:\n        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')\n    return db_order",
        "Disabling public docs and mitigating BOLA vulnerabilities via ownership verification.",
        "Security audits evaluate endpoints against the OWASP API Security Top 10, probing for authentication bypasses, broken authorization, and data leakage.",
        "Conducting pre-launch security audits, threat modeling, and SOC2 readiness evaluations.",
        ["What is BOLA (Broken Object Level Authorization) and why is it #1 on the OWASP API Security Top 10?", "Why return 404 Not Found instead of 403 Forbidden when an unauthorized user probes an object ID?"],
        ["Leaving Swagger UI (`/docs`) open to the public on private internal microservices.", "Returning 403 Forbidden on unauthorized object access, confirming to attackers that the secret ID exists."],
        "Pentesting tip: Returning 404 instead of 403 prevents attackers from enumerating valid resource IDs through trial and error.",
        ["[Tenant Isolation](authentication-and-security.md)", "[CORS Basics](authentication-and-security.md)"],
        ["https://owasp.org/API-Security/editions/2023/en/0x11-t10/"]
    ),
]
