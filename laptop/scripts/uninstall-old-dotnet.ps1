<#
Removes old .NET runtime copies whose own uninstaller is missing from C:\ProgramData\Package Cache.

In that state "Installed apps" can't remove them, and `msiexec /x {code}` on the parts reports exit 0
but removes nothing (the bundle still holds a dependency on them). What works: download the official
installer for the exact same version, check Microsoft's signature, and run its /uninstall.

Run elevated. Check what you have first with `dotnet --list-runtimes`, and only remove a version when
a newer patch of the same major.minor stays installed (.NET always runs the newest patch).

  powershell -ExecutionPolicy Bypass -File uninstall-old-dotnet.ps1 `
      -Installers dotnet-runtime-8.0.29-win-x64.exe, windowsdesktop-runtime-10.0.10-win-x64.exe
#>
param([Parameter(Mandatory)][string[]]$Installers)

$ErrorActionPreference = 'Stop'
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrators')) {
    throw 'Run this from an elevated PowerShell.'
}

$base = 'https://builds.dotnet.microsoft.com/dotnet'
$folder = @{ dotnet = 'Runtime'; aspnetcore = 'aspnetcore/Runtime'; windowsdesktop = 'WindowsDesktop' }
$dir = Join-Path $env:TEMP ("dotnet-uninstall-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory $dir | Out-Null
$ProgressPreference = 'SilentlyContinue'

try {
    foreach ($name in $Installers) {
        if ($name -notmatch '^(dotnet|aspnetcore|windowsdesktop)-runtime-(\d+\.\d+\.\d+)-win-(x64|x86|arm64)\.exe$') {
            Write-Warning "Skipping '$name': expected e.g. dotnet-runtime-8.0.29-win-x64.exe"; continue
        }
        $url = "$base/$($folder[$Matches[1]])/$($Matches[2])/$name"
        $file = Join-Path $dir $name
        Write-Host "Downloading $url"
        Invoke-WebRequest $url -OutFile $file -UseBasicParsing

        $sig = Get-AuthenticodeSignature $file
        if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation' -or
            $sig.SignerCertificate.Issuer -notmatch '^CN=Microsoft Code Signing PCA') {
            Write-Warning "Skipping '$name': signature is not a valid Microsoft one ($($sig.Status))"; continue
        }

        $p = Start-Process $file -ArgumentList '/uninstall /quiet /norestart' -Wait -PassThru
        Write-Host ("{0}: exit code {1}" -f $name, $p.ExitCode)
    }
} finally {
    Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`nRuntimes now installed:"
foreach ($exe in "$env:ProgramFiles\dotnet\dotnet.exe", "${env:ProgramFiles(x86)}\dotnet\dotnet.exe") {
    if (Test-Path $exe) { & $exe --list-runtimes }
}
