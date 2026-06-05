param(
  [string]$ResourceGroup = "azinv-dev-rg",
  [string]$VmName = "azinv-dev-vm",
  [string]$RemoteAppDir = "/opt/azure-inventory"
)

$ErrorActionPreference = "Stop"

$archive = Join-Path $env:TEMP "azure-inventory-dev.tar"
if (Test-Path -LiteralPath $archive) {
  Remove-Item -LiteralPath $archive -Force
}

tar `
  --exclude="./.git" `
  --exclude="./frontend/node_modules" `
  --exclude="./frontend/.next" `
  --exclude="./.terraform" `
  --exclude="./infra/envs/dev/.terraform" `
  --exclude="./infra/envs/dev/tfplan" `
  --exclude="./infra/envs/dev/tfplan-zone3" `
  --exclude="./infra/envs/dev/tfplan-vm-zone3-only" `
  --exclude="./*.tfstate" `
  --exclude="./*.tfstate.*" `
  -cf $archive .

$b64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($archive))
$scriptPath = Join-Path $env:TEMP "azure-inventory-single-deploy.sh"

$script = @"
set -eu
cat > /tmp/azure-inventory-dev.tar.b64 <<'AZINV_ARCHIVE_EOF'
$b64
AZINV_ARCHIVE_EOF
base64 -d /tmp/azure-inventory-dev.tar.b64 > /tmp/azure-inventory-dev.tar
mkdir -p $RemoteAppDir
tar -xf /tmp/azure-inventory-dev.tar -C $RemoteAppDir
chown -R azureuser:azureuser $RemoteAppDir
cd $RemoteAppDir
docker compose up -d --build
docker compose exec -T backend alembic upgrade head
docker compose ps
"@

Set-Content -LiteralPath $scriptPath -Value $script -NoNewline
Write-Host "Deploy script size: $((Get-Item $scriptPath).Length) bytes"

az vm run-command invoke `
  --resource-group $ResourceGroup `
  --name $VmName `
  --command-id RunShellScript `
  --scripts "@$scriptPath" `
  --query "value[0].message" `
  -o tsv

