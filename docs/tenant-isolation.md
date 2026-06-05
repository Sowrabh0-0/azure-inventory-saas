# Tenant Isolation

Tenant isolation is enforced at three layers.

## Identity Layer

The backend validates Microsoft tokens and extracts:

- `tid`
- `oid`
- `preferred_username` or `email`

The frontend cannot choose a tenant. Session claims are signed by the backend and checked against the database on every request.

## Data Layer

Core tables include `tenant_id`:

- `users`
- `oauth_connections`
- `subscriptions`
- `azure_resources`
- `sync_jobs`

Unique constraints combine external Azure identifiers with `tenant_id`, preventing collisions across tenants.

## Repository Layer

All read methods accept tenant context and filter by `tenant_id`. Avoid direct session queries in API routes; use repositories so the tenant filter remains obvious and testable.

Bad:

```python
select(AzureResource)
```

Good:

```python
select(AzureResource).where(AzureResource.tenant_id == tenant_id)
```

