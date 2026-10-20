<#
Deletes HP Insights Analytics' local telemetry database (C:\ProgramData\HP\Telemetry\data\ssm.db),
which grew to 3 GB in four months here. HP's services start a fresh, empty one; drivers, warranty,
OMEN Gaming Hub and HP updates are not affected. It grows back over time.

Both HP Insights Analytics and HP One Agent hold the file open, so both are stopped for a few seconds
and started again. Run elevated. Writes hp-telemetry-log.txt next to this script.
#>
$log = Join-Path $PSScriptRoot 'hp-telemetry-log.txt'
"Started $(Get-Date)" | Out-File $log -Encoding utf8
function L($m) { $m | Out-File $log -Append -Encoding utf8; Write-Host $m }
$svcs = 'HpTouchpointAnalyticsService', 'hp-one-agent-service'   # One Agent also holds ssm.db open
$dir = 'C:\ProgramData\HP\Telemetry\data'
foreach ($svc in $svcs) { try { Stop-Service $svc -Force -ErrorAction Stop; L "stopped: $svc" } catch { L "stop failed: $svc : $($_.Exception.Message)" } }
Start-Sleep 5
foreach ($n in 'ssm.db', 'ssm.db-wal', 'ssm.db-shm') {
    $p = Join-Path $dir $n
    if (-not (Test-Path -LiteralPath $p)) { L "absent: $n"; continue }
    try { Remove-Item -LiteralPath $p -Force -ErrorAction Stop; L "deleted: $n" } catch { L "FAILED: $n : $($_.Exception.Message)" }
}
foreach ($svc in $svcs) { try { Start-Service $svc -ErrorAction Stop; L "started: $svc -> $((Get-Service $svc).Status)" } catch { L "start failed: $svc : $($_.Exception.Message)" } }
L "Finished $(Get-Date)"
