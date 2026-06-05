# Architecture

```mermaid
flowchart LR
  U["Browser"] -->|"HTTP 80"| N["Nginx on Azure VM"]
  N --> F["Next.js frontend container"]
  N --> B["FastAPI backend container"]
  B --> P["PostgreSQL container"]
  B --> R["Redis container"]
  W["Celery worker container"] --> P
  W --> R
  S["Celery beat container"] --> R
  B --> G["Microsoft Graph API"]
  B --> A["Azure Resource Manager API"]
  U --> E["Microsoft Entra ID"]
  E -->|"Auth code callback"| N
```

## Runtime Boundaries

- Browser never receives ARM refresh tokens or backend ARM access tokens.
- Backend validates Microsoft claims and issues an HTTP-only app session cookie.
- Background sync uses encrypted refresh tokens stored in PostgreSQL.
- Inventory data is keyed by internal `tenant_id`.
- Nginx exposes one public endpoint and routes `/auth/*`, `/api/*`, and `/healthz` to FastAPI.

