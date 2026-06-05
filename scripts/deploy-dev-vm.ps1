param(
  [string]$TerraformDir = "infra/envs/dev",
  [string]$RemoteAppDir = "/opt/azure-inventory",
  [string]$MicrosoftClientId = "11a7c76b-7570-4c27-a6e2-c590614131f0",
  [switch]$SkipTerraformApply,
  [switch]$SkipUpload,
  [switch]$SkipCompose,
  [switch]$SkipAppRegistrationUpdate
)

$ErrorActionPreference = "Stop"

function Set-EnvValue {
  param(
    [string]$Path,
    [string]$Key,
    [string]$Value
  )

  if (!(Test-Path -LiteralPath $Path)) {
    Copy-Item -LiteralPath ".env.example" -Destination $Path
  }

  $lines = Get-Content -LiteralPath $Path
  $updated = $false
  $next = foreach ($line in $lines) {
    if ($line -match "^\s*$([regex]::Escape($Key))=") {
      "$Key=$Value"
      $updated = $true
    } else {
      $line
    }
  }

  if (!$updated) {
    $next += "$Key=$Value"
  }

  Set-Content -LiteralPath $Path -Value $next
}

if (!(Test-Path -LiteralPath $TerraformDir)) {
  throw "Terraform directory not found: $TerraformDir"
}

if (!$SkipTerraformApply) {
  terraform "-chdir=$TerraformDir" init
  terraform "-chdir=$TerraformDir" apply
}

$publicIp = terraform "-chdir=$TerraformDir" output -raw public_ip_address
$sshCommand = terraform "-chdir=$TerraformDir" output -raw ssh_command
$adminUser = ($sshCommand -replace "^ssh\s+", "" -split "@")[0]

if ([string]::IsNullOrWhiteSpace($publicIp)) {
  throw "Terraform did not return public_ip_address."
}

$publicBaseUrl = "http://$publicIp"
Set-EnvValue -Path ".env" -Key "PUBLIC_BASE_URL" -Value $publicBaseUrl
Set-EnvValue -Path ".env" -Key "COOKIE_SECURE" -Value "false"

Write-Host "Updated .env:"
Write-Host "  PUBLIC_BASE_URL=$publicBaseUrl"
Write-Host ""
Write-Host "Add this redirect URI to the Entra app registration:"
Write-Host "  $publicBaseUrl/auth/callback"
Write-Host ""

if (!$SkipAppRegistrationUpdate) {
  $existingUris = az ad app show --id $MicrosoftClientId --query "web.redirectUris" -o tsv
  $uriSet = New-Object System.Collections.Generic.HashSet[string]
  foreach ($uri in $existingUris) {
    if (![string]::IsNullOrWhiteSpace($uri)) {
      [void]$uriSet.Add($uri.Trim())
    }
  }
  [void]$uriSet.Add("http://localhost/auth/callback")
  [void]$uriSet.Add("$publicBaseUrl/auth/callback")
  az ad app update --id $MicrosoftClientId --web-redirect-uris @($uriSet)
  Write-Host "Updated Entra redirect URIs."
  Write-Host ""
}

if (!$SkipUpload) {
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
    --exclude="./*.tfstate" `
    --exclude="./*.tfstate.*" `
    -cf $archive .

  scp $archive "${adminUser}@${publicIp}:/tmp/azure-inventory-dev.tar"
  ssh "${adminUser}@${publicIp}" "sudo mkdir -p $RemoteAppDir && sudo chown -R ${adminUser}:${adminUser} $RemoteAppDir && tar -xf /tmp/azure-inventory-dev.tar -C $RemoteAppDir"
}

if (!$SkipCompose) {
  ssh "${adminUser}@${publicIp}" "cd $RemoteAppDir && docker compose up -d --build && docker compose exec -T backend alembic upgrade head"
}

Write-Host ""
Write-Host "VM app URL:"
Write-Host "  $publicBaseUrl"
