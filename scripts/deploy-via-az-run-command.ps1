param(
  [string]$ResourceGroup = "azinv-dev-rg",
  [string]$VmName = "azinv-dev-vm",
  [string]$RemoteAppDir = "/opt/azure-inventory",
  [int]$ChunkSize = 6000,
  [switch]$ResumeUpload,
  [switch]$SkipCompose
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

$bytes = [System.IO.File]::ReadAllBytes($archive)
$b64 = [Convert]::ToBase64String($bytes)

$startIndex = 0
if ($ResumeUpload) {
  $remoteLengthText = az vm run-command invoke `
    --resource-group $ResourceGroup `
    --name $VmName `
    --command-id RunShellScript `
    --scripts "test -f /tmp/azure-inventory-dev.tar.b64 && tr -d '\n' < /tmp/azure-inventory-dev.tar.b64 | wc -c || echo 0" `
    --query "value[0].message" `
    -o tsv
  if ($remoteLengthText -match "\[stdout\]\s*(\d+)") {
    $startIndex = [int]$Matches[1]
  }
  Write-Host "Resuming upload from base64 character $startIndex / $($b64.Length)"
} else {
  az vm run-command invoke `
    --resource-group $ResourceGroup `
    --name $VmName `
    --command-id RunShellScript `
    --scripts "rm -f /tmp/azure-inventory-dev.tar.b64 /tmp/azure-inventory-dev.tar" `
    --query "value[0].message" `
    -o tsv
}

$chunkScriptPath = Join-Path $env:TEMP "azure-inventory-upload-chunk.sh"
for ($i = $startIndex; $i -lt $b64.Length; $i += $ChunkSize) {
  $length = [Math]::Min($ChunkSize, $b64.Length - $i)
  $chunk = $b64.Substring($i, $length)
  $script = "cat >> /tmp/azure-inventory-dev.tar.b64 <<'EOF'`n$chunk`nEOF"
  Set-Content -LiteralPath $chunkScriptPath -Value $script -NoNewline
  Write-Host "Uploading chunk $([Math]::Floor($i / $ChunkSize) + 1) / $([Math]::Ceiling($b64.Length / $ChunkSize))"
  az vm run-command invoke `
    --resource-group $ResourceGroup `
    --name $VmName `
    --command-id RunShellScript `
    --scripts "@$chunkScriptPath" `
    --query "value[0].message" `
    -o tsv | Out-Null
}

$deployScript = @"
set -eu
mkdir -p $RemoteAppDir
base64 -d /tmp/azure-inventory-dev.tar.b64 > /tmp/azure-inventory-dev.tar
tar -xf /tmp/azure-inventory-dev.tar -C $RemoteAppDir
chown -R azureuser:azureuser $RemoteAppDir
cd $RemoteAppDir
"@

if (!$SkipCompose) {
  $deployScript += @"

docker compose up -d --build
docker compose exec -T backend alembic upgrade head
"@
}

$deployScriptPath = Join-Path $env:TEMP "azure-inventory-deploy.sh"
Set-Content -LiteralPath $deployScriptPath -Value $deployScript -NoNewline

az vm run-command invoke `
  --resource-group $ResourceGroup `
  --name $VmName `
  --command-id RunShellScript `
  --scripts "@$deployScriptPath" `
  --query "value[0].message" `
  -o tsv

Write-Host "Deployment completed through Azure Run Command."
