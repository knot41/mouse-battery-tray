param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$Interpreter = (Get-Command $Python -ErrorAction Stop).Source
$Root = Split-Path $PSScriptRoot -Parent
Push-Location $Root
try {
    # Respect the interpreter selected by actions/setup-python or the caller.
    & $Interpreter -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python virtual environment' }
    & .venv\Scripts\python.exe -m pip install -c requirements-build.txt -e '.[build]'
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
    & .venv\Scripts\python.exe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    & .venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name MouseBatteryTray --icon docs/app.ico --paths src --copy-metadata pystray --copy-metadata Pillow --copy-metadata hidapi --copy-metadata six scripts/launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    Write-Host 'Built dist\MouseBatteryTray.exe'
} finally {
    Pop-Location
}
