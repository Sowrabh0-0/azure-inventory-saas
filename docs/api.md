# API

## Auth

- `GET /auth/login`: creates PKCE verifier/state cookies and returns Microsoft authorization URL
- `GET /auth/login?tenant=<tenant-id>`: starts login against a specific Entra tenant authority
- `GET /auth/callback`: exchanges Microsoft auth code, validates claims, stores encrypted refresh token, queues tenant sync, sets HTTP-only session cookie
- `POST /auth/logout`: clears session cookie
- `GET /auth/me`: returns backend-derived user and tenant context

## Inventory

All routes require an HTTP-only session cookie and are scoped by `tenant_id`.

- `GET /api/v1/overview`
- `GET /api/v1/subscriptions`
- `GET /api/v1/resources`
- `GET /api/v1/resources?resource_type=Microsoft.Storage/storageAccounts`
- `GET /api/v1/resource-groups`
- `GET /api/v1/aks`
- `GET /api/v1/storage`
- `GET /api/v1/keyvaults`

## Background Sync

Celery task names:

- `app.tasks.sync.sync_tenant`
- `app.tasks.sync.sync_all_tenants`

Sync is automatically queued after successful login. Run manually when troubleshooting:

```bash
docker compose exec -T celery-worker celery -A app.core.celery_app.celery_app call app.tasks.sync.sync_all_tenants
```
