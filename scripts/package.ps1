param([string]$Python)
$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
if (!$Python) { $Python = Join-Path $Root '.venv\Scripts\python.exe' }
Push-Location $Root
try {
    $Version = (& $Python -c 'from mouse_battery_tray import __version__; print(__version__)').Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Could not read version; build first' }
    & $Python -m build --outdir dist
    if ($LASTEXITCODE -ne 0) { throw 'Python distribution build failed' }
    $Stage = Join-Path 'build' ('portable-' + $Version + '-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force (Join-Path $Stage 'scripts') | Out-Null
    Copy-Item dist\MouseBatteryTray.exe $Stage
    Copy-Item LICENSE,THIRD_PARTY.md,README.md,README.en.md,CHANGELOG.md $Stage
    Copy-Item docs (Join-Path $Stage 'docs') -Recurse
    Copy-Item scripts\install.ps1 (Join-Path $Stage 'scripts')
    $Zip = Join-Path 'dist' ("MouseBatteryTray-$Version-windows-x64.zip")
    & $Python (Join-Path $PSScriptRoot 'make_zip.py') $Stage $Zip
    if ($LASTEXITCODE -ne 0) { throw 'Portable ZIP creation failed' }
    Get-ChildItem dist -File | Where-Object { $_.Name -ne 'SHA256SUMS.txt' } | Sort-Object Name | ForEach-Object {
        $Hash = Get-FileHash $_.FullName -Algorithm SHA256
        '{0}  {1}' -f $Hash.Hash.ToLowerInvariant(), $_.Name
    } | Set-Content dist\SHA256SUMS.txt -Encoding ASCII
    Write-Host 'Release assets prepared in dist/'
} finally {
    Pop-Location
}
