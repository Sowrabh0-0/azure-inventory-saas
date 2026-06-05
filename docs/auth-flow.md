# Authentication Flow

```mermaid
sequenceDiagram
  participant User
  participant Frontend
  participant Backend
  participant Entra
  participant Graph
  participant DB
  participant Celery

  User->>Frontend: Enter optional tenant ID and click Microsoft login
  Frontend->>Backend: GET /auth/login?tenant=<tenant-id>
  Backend-->>Frontend: Authorization URL plus PKCE cookies
  Frontend->>Entra: Redirect to authorize endpoint
  Entra-->>Backend: GET /auth/callback?code&state
  Backend->>Entra: Exchange code with PKCE verifier
  Entra-->>Backend: Access token and refresh token
  Backend->>Backend: Validate JWT issuer, audience, tid, oid
  Backend->>Graph: Read organization metadata
  Backend->>DB: Upsert tenant, user, encrypted refresh token
  Backend->>Celery: Queue sync_tenant
  Backend-->>Frontend: HTTP-only app session cookie
  Frontend->>Backend: Tenant-scoped API requests
```

The backend never trusts frontend-provided tenant claims. It derives `tid`, `oid`, and email from Microsoft-validated token claims.

If `tenant` is omitted, login uses the multi-tenant `/common` authority. If `tenant` is supplied, the authorize and token exchange use that tenant-specific authority, which helps users avoid accidentally selecting a personal Microsoft consumer identity.
