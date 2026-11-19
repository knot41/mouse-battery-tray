param([switch]$Startup, [switch]$ShowOnTaskbar)
$ErrorActionPreference = 'Stop'
$Source = Join-Path (Split-Path $PSScriptRoot -Parent) 'dist\MouseBatteryTray.exe'
if (!(Test-Path $Source)) {
    $Source = Join-Path (Split-Path $PSScriptRoot -Parent) 'MouseBatteryTray.exe'
}
if (!(Test-Path $Source)) { throw 'Build first, or extract the complete portable ZIP' }
$Destination = Join-Path $env:LOCALAPPDATA 'MouseBatteryTray'
New-Item -ItemType Directory -Force $Destination | Out-Null
Copy-Item $Source (Join-Path $Destination 'MouseBatteryTray.exe') -Force
$Exe = Join-Path $Destination 'MouseBatteryTray.exe'
if ($ShowOnTaskbar) {
    $SettingsPath = Join-Path $Destination 'settings.json'
    $Settings = @{}
    if (Test-Path $SettingsPath) {
        $Previous = Get-Content $SettingsPath -Raw | ConvertFrom-Json
        $Previous.PSObject.Properties | ForEach-Object { $Settings[$_.Name] = $_.Value }
    }
    $Settings['show_on_taskbar'] = $true
    $Settings | ConvertTo-Json | Set-Content $SettingsPath -Encoding UTF8
}
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Programs')) 'Mouse Battery Tray.lnk'))
$Shortcut.TargetPath = $Exe
$Shortcut.WorkingDirectory = $Destination
$Shortcut.Save()
if ($Startup) {
    $Run = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    New-Item -Path $Run -Force | Out-Null
    New-ItemProperty -Path $Run -Name 'MouseBatteryTray' -Value ('"' + $Exe + '"') -PropertyType String -Force | Out-Null
}
Start-Process $Exe
Write-Host "Installed to $Exe"
