param([string]$Target = (Join-Path $HOME ".claude"))
$ErrorActionPreference = "Stop"
$kit = $PSScriptRoot

$checkOutput = & python (Join-Path $kit "tools/check_kit.py") --root $kit
if ($LASTEXITCODE -ne 0) {
    $checkOutput | ForEach-Object { Write-Output $_ }
    throw "check_kit.py thất bại - không cài."
}

$pluginCache = Join-Path $Target "plugins/cache"
$hasSuperpowers = $false
if (Test-Path -LiteralPath $pluginCache) {
    $hasSuperpowers = [bool](Get-ChildItem -LiteralPath $pluginCache -Directory -Recurse -Depth 1 -Filter "superpowers" -ErrorAction SilentlyContinue)
}
if (-not $hasSuperpowers) {
    Write-Warning "Chưa thấy plugin superpowers trong $pluginCache. Agent vẫn chạy nhưng không có skill superpowers; cài plugin superpowers bằng /plugin trong Claude Code."
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $Target "backups/web-studio-kit-$stamp"
$agentsDst = Join-Path $Target "agents"
$skillDst = Join-Path $Target "skills/web-studio"
$replaced = @()

New-Item -ItemType Directory -Force -Path $agentsDst | Out-Null
$agents = Get-ChildItem -Path (Join-Path $kit "agents") -Filter "*.md" | Where-Object { -not $_.Name.StartsWith("_") }
foreach ($agent in $agents) {
    $dst = Join-Path $agentsDst $agent.Name
    if (Test-Path -LiteralPath $dst) {
        New-Item -ItemType Directory -Force -Path (Join-Path $backup "agents") | Out-Null
        Copy-Item -LiteralPath $dst -Destination (Join-Path $backup "agents")
        $replaced += "agents/$($agent.Name)"
    }
    Copy-Item -LiteralPath $agent.FullName -Destination $dst -Force
}

$manifest = Join-Path $agentsDst ".web-studio-kit-agents.txt"
if (Test-Path -LiteralPath $manifest) {
    $current = $agents | ForEach-Object { $_.Name }
    foreach ($stale in (Get-Content -LiteralPath $manifest | Where-Object { $_ -and ($current -notcontains $_) })) {
        $stalePath = Join-Path $agentsDst $stale
        if (Test-Path -LiteralPath $stalePath) {
            New-Item -ItemType Directory -Force -Path (Join-Path $backup "agents") | Out-Null
            Move-Item -LiteralPath $stalePath -Destination (Join-Path $backup "agents")
            $replaced += "agents/$stale (đã gỡ: không còn trong kit)"
        }
    }
}
$agents | ForEach-Object { $_.Name } | Set-Content -LiteralPath $manifest -Encoding UTF8

if (Test-Path -LiteralPath $skillDst) {
    New-Item -ItemType Directory -Force -Path (Join-Path $backup "skills") | Out-Null
    Copy-Item -LiteralPath $skillDst -Destination (Join-Path $backup "skills") -Recurse
    Remove-Item -LiteralPath $skillDst -Recurse -Force -Confirm:$false
    $replaced += "skills/web-studio"
}
New-Item -ItemType Directory -Force -Path (Split-Path $skillDst) | Out-Null
Copy-Item -Path (Join-Path $kit "skills/web-studio") -Destination $skillDst -Recurse

Write-Output "Đã cài $($agents.Count) agent vào $agentsDst"
Write-Output "Đã cài skill web-studio vào $skillDst"
if ($replaced.Count -gt 0) {
    Write-Output "Đã ghi đè (bản cũ sao lưu ở $backup):"
    $replaced | ForEach-Object { Write-Output "  $_" }
}
Write-Output "Mở phiên Claude Code mới (hoặc Reload Window trong VS Code) để nạp agent."
