<#
Read-only: shows which process (and service) has a file open, using Windows' Restart Manager API.
Handy when a delete fails with "being used by another process".

  powershell -ExecutionPolicy Bypass -File find-file-lock.ps1 C:\ProgramData\HP\Telemetry\data\ssm.db
#>
param([Parameter(Mandatory)][string]$Path)

Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices; using System.Collections.Generic;
public static class RmLock {
  [StructLayout(LayoutKind.Sequential)] struct UNIQUE_PROCESS { public int pid; public System.Runtime.InteropServices.ComTypes.FILETIME t; }
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct INFO { public UNIQUE_PROCESS p; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=256)] public string app; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=64)] public string svc; public int type; public int status; public int sess; [MarshalAs(UnmanagedType.Bool)] public bool restartable; }
  [DllImport("rstrtmgr.dll", CharSet=CharSet.Unicode)] static extern int RmStartSession(out uint h, int f, string k);
  [DllImport("rstrtmgr.dll")] static extern int RmEndSession(uint h);
  [DllImport("rstrtmgr.dll", CharSet=CharSet.Unicode)] static extern int RmRegisterResources(uint h, uint n, string[] f, uint a, UNIQUE_PROCESS[] b, uint c, string[] d);
  [DllImport("rstrtmgr.dll")] static extern int RmGetList(uint h, out uint need, ref uint n, [In, Out] INFO[] i, ref uint r);
  public static List<string> Who(string path) {
    var res = new List<string>(); uint h; RmStartSession(out h, 0, Guid.NewGuid().ToString());
    try { RmRegisterResources(h, 1, new[]{path}, 0, null, 0, null); uint need=0, n=0, r=0;
      int rc = RmGetList(h, out need, ref n, null, ref r);
      if (rc == 234) { var a = new INFO[need]; n = need; RmGetList(h, out need, ref n, a, ref r); foreach (var x in a) res.Add(x.p.pid + "|" + x.app + "|" + x.svc); }
      else if (rc != 0) res.Add("error|Restart Manager returned " + rc + "|"); } finally { RmEndSession(h); } return res; } }
'@

$found = [RmLock]::Who((Resolve-Path -LiteralPath $Path).Path)
if (-not $found) { "Nothing has '$Path' open."; return }
foreach ($line in $found) {
    $pid_, $app, $svc = $line.Split('|')
    "{0,6}  {1}{2}" -f $pid_, $app, $(if ($svc) { "  [service: $svc]" } else { '' })
}
