<#
Silently uninstalls the small extras removed from this HP OMEN 16: HP Client Management Script Library
(PowerShell modules for IT admins), the offline HP Documentation, and PunkBuster (anti-cheat for old
games; it runs a service all the time). Each one is skipped if it isn't there.

Run elevated. Writes uninstall-log.txt next to this script. Edit the list to suit your machine.
#>
$log = Join-Path $PSScriptRoot 'uninstall-log.txt'
"Started $(Get-Date)" | Out-File $log -Encoding utf8

function Run([string]$name, [string]$exe, [string]$arguments) {
    if (-not (Test-Path -LiteralPath $exe)) { "SKIP  $name : uninstaller not found ($exe)" | Out-File $log -Append -Encoding utf8; return }
    try {
        $p = Start-Process -FilePath $exe -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
        "DONE  $name : exit code $($p.ExitCode)" | Out-File $log -Append -Encoding utf8
    } catch { "FAIL  $name : $($_.Exception.Message)" | Out-File $log -Append -Encoding utf8 }
}

Run 'HP Client Management Script Library' 'C:\Program Files\WindowsPowerShell\HP.CMSL.UninstallerData\unins000.exe' '/VERYSILENT /NORESTART'
Run 'HP Documentation'                    "$env:WINDIR\System32\cmd.exe" '/c "C:\Program Files\HP\Documentation\Doc_Uninstall.cmd"'
# PunkBuster is 32-bit: its uninstaller lives in SysWOW64 even though "Installed apps" says System32.
Run 'PunkBuster Services'                 "$env:WINDIR\SysWOW64\pbsvc.exe" '-u'

"Finished $(Get-Date)" | Out-File $log -Append -Encoding utf8
Get-Content $log
