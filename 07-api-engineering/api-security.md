# API Security, OAuth2 & JWT Protection Guide

## Module Overview
This guide covers **OAuth2 Grants**, **JWT Anatomy and Security Pitfalls**, and API gateway authorization.

---

## Visual Flow: OAuth2 Authorization Code Grant with PKCE

```mermaid
sequenceDiagram
    participant User as User / Browser
    participant App as Client Web App
    participant Auth as Authorization Server (Auth0 / Google)
    participant API as Resource Server (Backend API)

    User->>App: 1. Click 'Login with Google'
    App->>Auth: 2. Redirect with code_challenge (PKCE)
    User->>Auth: 3. User authenticates & approves scopes
    Auth->>App: 4. Redirects to callback with Authorization Code
    App->>Auth: 5. Exchanges Code + code_verifier for Access & ID Tokens
    Auth->>App: 6. Issues signed JWT Access Token
    App->>API: 7. GET /api/v1/profile with Bearer <JWT>
    API->>API: 8. Cryptographically verifies JWT signature with public key
    API->>App: 9. Returns protected resource data (200 OK)
```

---

## JWT Security Pitfalls & Protections

1. **The `alg: "none"` Attack:** Always enforce strict cryptographic verification on the backend; reject tokens specifying `none` or mismatched HMAC/RSA algorithms.
2. **Token Revocation (Blacklisting):** Because JWTs are stateless, they cannot be natively revoked before expiration. Use Redis to maintain a **token revocation blacklist** indexed by `jti` (JWT ID claim) checked on sensitive operations.
