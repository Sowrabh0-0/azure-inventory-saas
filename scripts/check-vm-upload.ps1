param(
  [string]$ResourceGroup = "azinv-dev-rg",
  [string]$VmName = "azinv-dev-vm"
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $env:TEMP "azure-inventory-check-upload.sh"
Set-Content -LiteralPath $scriptPath -NoNewline -Value @'
set -eu
if [ ! -f /tmp/azure-inventory-dev.tar.b64 ]; then
  echo "archive_base64=missing"
  exit 0
fi
echo "archive_base64_chars=$(cat /tmp/azure-inventory-dev.tar.b64 | tr -d '\n' | wc -c)"
if base64 -d /tmp/azure-inventory-dev.tar.b64 > /tmp/azure-inventory-dev.tar 2>/tmp/base64.err; then
  echo "decoded=yes"
else
  echo "decoded=no"
  cat /tmp/base64.err
fi
ls -lh /tmp/azure-inventory-dev.tar /tmp/azure-inventory-dev.tar.b64 2>/dev/null || true
ls -la /opt/azure-inventory 2>/dev/null | head || true
'@

az vm run-command invoke `
  --resource-group $ResourceGroup `
  --name $VmName `
  --command-id RunShellScript `
  --scripts "@$scriptPath" `
  --query "value[0].message" `
  -o tsv

