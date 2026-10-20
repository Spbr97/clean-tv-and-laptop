# Undo everything: re-enable every package in debloat.txt, give Home back to the stock launcher, and
# put back Private DNS, the screensaver and the animation scales as they were before.
# Usage: powershell -ExecutionPolicy Bypass -File tools\restore.ps1 [-TvHost 192.168.1.7] [-UninstallLauncher]
param(
    [string]$TvHost = $(if ($env:TV_HOST) { $env:TV_HOST } else { '192.168.1.7' }),
    [switch]$UninstallLauncher
)
$env:TV_HOST = $TvHost
$repo = Split-Path -Parent $PSScriptRoot
$py = Join-Path $repo 'tools\venv\Scripts\python.exe'
$extra = @()
if ($UninstallLauncher) { $extra += '--uninstall-launcher' }
& $py -I (Join-Path $repo 'tools\restore.py') @extra
