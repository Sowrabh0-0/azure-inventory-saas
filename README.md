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

If password SSH makes `scp` inconvenient, deploy through Azure VM Run Command:

```powershell
.\scripts\deploy-via-az-run-command.ps1
```

The script prints the redirect URI you must add to the Entra app registration, for example:

```text
http://PUBLIC_IP/auth/callback
```

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

Set the Entra app redirect URI to:

```text
http://PUBLIC_IP/auth/callback
```

For HTTPS testing, add certificates under `nginx/certs` and extend `nginx/nginx.conf`.

## Required Entra App Configuration

Use a multi-tenant app registration and configure:

- Platform: Web
- Redirect URI: `http://localhost/auth/callback` or `http://PUBLIC_IP/auth/callback`
- Allow public client flows: no
- Client secret: create and place in `.env`
- API permissions: `openid`, `profile`, `email`, `offline_access`, `User.Read`, `https://management.azure.com/user_impersonation`

Admin consent may be required depending on tenant policy.

## Tenant Isolation

Every persisted inventory object has `tenant_id`. API dependencies derive tenant identity from backend-validated session data, not from frontend claims. Repository queries always filter by `tenant_id`, for example:

```sql
SELECT * FROM azure_resources WHERE tenant_id = :tenant_id;
```

Never add an inventory query without tenant scope.

## Notes

This is a dev-ready baseline. Before production use, add TLS automation, managed PostgreSQL/Redis, backups, private networking, stricter rate limiting, observability alerts, image scanning, secret rotation, and a formal RBAC model for app-level roles.
