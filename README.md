# Azure Inventory SaaS

Production-shaped dev scaffold for a multi-tenant Azure resource inventory platform. Users sign in with Microsoft Entra ID, the backend validates tenant/user claims, stores encrypted refresh tokens, and syncs Azure Resource Manager inventory into tenant-scoped PostgreSQL tables.

This version is tuned for dev testing on a normal Azure VM:

- No AKS
- No Azure Container Apps
- No Key Vault
- Public VM IP enabled
- Nginx reverse proxy on the VM
- Everything runs as Docker containers through Docker Compose

## Services

- `frontend`: Next.js 15 App Router, TypeScript, TailwindCSS, shadcn-style primitives, MSAL config
- `backend`: FastAPI, async SQLAlchemy, Alembic, Pydantic v2, Microsoft OAuth, ARM/Graph clients
- `postgres`: local PostgreSQL 16 container for dev
- `redis`: local Redis container for Celery
- `celery-worker`: background inventory sync
- `celery-beat`: periodic sync scheduler
- `nginx`: public reverse proxy for frontend and backend routes

## Local Dev

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

Open `http://localhost`.

On login, leave Tenant ID blank for normal multi-tenant discovery, or enter a specific Entra tenant ID to force a work/school or guest-directory sign-in. This is useful when the same email address also has a personal Microsoft account.

## Azure VM Dev Deploy

```bash
cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

On Windows/PowerShell you can automate the Terraform apply, `.env` public IP update, upload, Compose start, and migration:

```powershell
.\scripts\deploy-dev-vm.ps1
```

If you already ran Terraform and only want to copy the VM IP into `.env`:

```powershell
.\scripts\update-env-from-terraform.ps1
```

For dev OAuth testing through the VM, use an SSH tunnel and browse through localhost:

```powershell
ssh -L 8080:localhost:80 azureuser@PUBLIC_IP
```

Then open:

```text
http://localhost:8080
```

Microsoft allows plain HTTP redirect URIs only for localhost. A public VM IP callback such as `http://PUBLIC_IP/auth/callback` is rejected by Microsoft. For direct public access, configure HTTPS and use an HTTPS redirect URI.

The dev VM uses password-based SSH. The password is in ignored `infra/envs/dev/terraform.tfvars` as `admin_password`.

Manual deploy path:

```bash
scp -r ../../../* azureuser@PUBLIC_IP:/opt/azure-inventory
ssh azureuser@PUBLIC_IP
cd /opt/azure-inventory
cp .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

For tunnel-based dev testing, set Entra redirect URIs to:

```text
http://localhost/auth/callback
http://localhost:8080/auth/callback
```

For HTTPS testing, add certificates under `nginx/certs` and extend `nginx/nginx.conf`.

## Required Entra App Configuration

Use a multi-tenant app registration and configure:

- Platform: Web
- Redirect URI: `http://localhost/auth/callback`, `http://localhost:8080/auth/callback`, or an HTTPS public URI
- Allow public client flows: no
- Client secret: create and place in `.env`
- API permissions: `openid`, `profile`, `email`, `offline_access`, `User.Read`, Azure Resource Manager `user_impersonation`

Admin consent may be required depending on tenant policy.

## Inventory Sync

After successful login, the backend automatically queues a Celery sync for the signed-in tenant. The dashboard may show zeroes for a few seconds while the worker discovers subscriptions and resources.

Manual sync is still available for troubleshooting:

```bash
docker compose exec -T celery-worker celery -A app.core.celery_app.celery_app call app.tasks.sync.sync_all_tenants
```

## Tenant Isolation

Every persisted inventory object has `tenant_id`. API dependencies derive tenant identity from backend-validated session data, not from frontend claims. Repository queries always filter by `tenant_id`, for example:

```sql
SELECT * FROM azure_resources WHERE tenant_id = :tenant_id;
```

Never add an inventory query without tenant scope.

## Notes

This is a dev-ready baseline. Before production use, add TLS automation, managed PostgreSQL/Redis, backups, private networking, stricter rate limiting, observability alerts, image scanning, secret rotation, and a formal RBAC model for app-level roles.
