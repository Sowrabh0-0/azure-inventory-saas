# Azure VM Dev Infrastructure

This Terraform deploys a normal public Ubuntu VM for dev testing. It intentionally does not create AKS, Azure Container Apps, or Key Vault.

The VM includes:

- Public IP
- Network security group allowing SSH, HTTP, and HTTPS
- Docker Engine and Docker Compose plugin installed by cloud-init
- `/opt/azure-inventory` prepared as the deployment directory
- Password-based SSH login for dev testing

Deploy the app by copying the repository and `.env` file to the VM, then running:

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
```
