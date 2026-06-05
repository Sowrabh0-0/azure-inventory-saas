param(
  [string]$TerraformDir = "infra/envs/dev"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath ".env")) {
  Copy-Item -LiteralPath ".env.example" -Destination ".env"
}

$publicIp = terraform "-chdir=$TerraformDir" output -raw public_ip_address
if ([string]::IsNullOrWhiteSpace($publicIp)) {
  throw "Terraform did not return public_ip_address."
}

$publicBaseUrl = "http://$publicIp"
$lines = Get-Content -LiteralPath ".env"
$updated = $false
$next = foreach ($line in $lines) {
  if ($line -match "^\s*PUBLIC_BASE_URL=") {
    "PUBLIC_BASE_URL=$publicBaseUrl"
    $updated = $true
  } else {
    $line
  }
}

if (!$updated) {
  $next += "PUBLIC_BASE_URL=$publicBaseUrl"
}

Set-Content -LiteralPath ".env" -Value $next

Write-Host "PUBLIC_BASE_URL=$publicBaseUrl"
Write-Host "Entra redirect URI: $publicBaseUrl/auth/callback"
