# VM Docker Compose Deployment

## 1. Provision VM

```bash
cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

PowerShell automation from the repository root:

```powershell
.\scripts\deploy-dev-vm.ps1
```

This runs Terraform, reads `public_ip_address`, updates `.env` with `PUBLIC_BASE_URL=http://PUBLIC_IP`, uploads the app archive to the VM, starts Docker Compose, and runs Alembic migrations.

To only update `.env` from an existing Terraform deployment:

```powershell
.\scripts\update-env-from-terraform.ps1
```

The NSG exposes:

- `22/tcp` from `ssh_source_address_prefix`
- `80/tcp` from the internet
- `443/tcp` from the internet

The dev VM uses password-based SSH. The generated password is stored in ignored `infra/envs/dev/terraform.tfvars`.

## 2. Copy Application

```bash
scp -r ../../../* azureuser@PUBLIC_IP:/opt/azure-inventory
```

## 3. Configure Environment

```bash
ssh azureuser@PUBLIC_IP
cd /opt/azure-inventory
cp .env.example .env
```

Set:

- `PUBLIC_BASE_URL=http://PUBLIC_IP`
- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `JWT_SIGNING_KEY`
- `TOKEN_ENCRYPTION_KEY`

## 4. Start

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose ps
```

## 5. Test

For Microsoft OAuth dev testing, use a localhost tunnel:

```powershell
ssh -L 8080:localhost:80 azureuser@PUBLIC_IP
```

Open:

```text
http://localhost:8080
```

Configure these redirect URIs in the app registration:

```text
http://localhost/auth/callback
http://localhost:8080/auth/callback
```

Public HTTP callbacks are not accepted by Microsoft. Use HTTPS for direct public browser access.

```bash
curl http://PUBLIC_IP/healthz
```
