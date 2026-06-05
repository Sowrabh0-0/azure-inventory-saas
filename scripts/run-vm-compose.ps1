param(
  [string]$ResourceGroup = "azinv-dev-rg",
  [string]$VmName = "azinv-dev-vm",
  [string]$RemoteAppDir = "/opt/azure-inventory"
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $env:TEMP "azure-inventory-run-compose.sh"
Set-Content -LiteralPath $scriptPath -NoNewline -Value @"
set -eu
mkdir -p $RemoteAppDir
base64 -d /tmp/azure-inventory-dev.tar.b64 > /tmp/azure-inventory-dev.tar
tar -xf /tmp/azure-inventory-dev.tar -C $RemoteAppDir
chown -R azureuser:azureuser $RemoteAppDir
cd $RemoteAppDir
docker compose up -d --build
docker compose exec -T backend alembic upgrade head
docker compose ps
"@

az vm run-command invoke `
  --resource-group $ResourceGroup `
  --name $VmName `
  --command-id RunShellScript `
  --scripts "@$scriptPath" `
  --query "value[0].message" `
  -o tsv

