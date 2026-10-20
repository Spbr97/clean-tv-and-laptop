# Run one shell command on the TV over ADB (pure Python client, no adb.exe needed).
# Usage: tools\tv.ps1 "pm enable --user 0 com.spotify.tv.android"   [-TvHost 192.168.1.7]
param(
    [Parameter(Mandatory = $true, Position = 0)][string]$Command,
    [string]$TvHost = $(if ($env:TV_HOST) { $env:TV_HOST } else { '192.168.1.7' })
)
$env:TV_HOST = $TvHost
$env:MSYS_NO_PATHCONV = '1'
$repo = Split-Path -Parent $PSScriptRoot
& (Join-Path $repo 'tools\venv\Scripts\python.exe') -I (Join-Path $repo 'tools\tv.py') $Command
