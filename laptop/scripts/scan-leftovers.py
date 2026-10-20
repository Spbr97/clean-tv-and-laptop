"""Read-only: measure size, file count and newest-file age of the usual leftover locations.

    python -I scan-leftovers.py

Only lists locations of 20 MB or more, plus the largest items (50 MB+) in Downloads. Deletes nothing.
"""
import os, sys, time

sys.stdout.reconfigure(encoding="utf-8")

U = os.path.expanduser("~")
LA = os.environ["LOCALAPPDATA"]
RA = os.environ["APPDATA"]
W = os.environ.get("WINDIR", r"C:\Windows")
NOW = time.time()

CANDIDATES = {
    "Temp & crash data": [
        os.environ["TEMP"], rf"{W}\Temp", rf"{LA}\CrashDumps", rf"{W}\Minidump", rf"{W}\MEMORY.DMP",
        rf"{LA}\Microsoft\Windows\WER", r"C:\ProgramData\Microsoft\Windows\WER", rf"{W}\LiveKernelReports",
        rf"{LA}\D3DSCache", rf"{LA}\NVIDIA\DXCache", rf"{LA}\NVIDIA\GLCache", rf"{LA}\Intel\ShaderCache",
    ],
    "Windows update & install leftovers": [
        rf"{W}\SoftwareDistribution\Download", rf"{W}\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache",
        r"C:\Windows.old", r"C:\$WINDOWS.~BT", r"C:\$WinREAgent", r"C:\SWSetup", r"C:\NVIDIA", r"C:\Intel", r"C:\AMD",
        rf"{W}\Installer\$PatchCache$", rf"{W}\Downloaded Program Files", rf"{W}\Logs\CBS",
    ],
    "Developer caches (safe to rebuild)": [
        rf"{LA}\pip\Cache", rf"{LA}\uv\cache", rf"{LA}\npm-cache", rf"{RA}\npm-cache", rf"{LA}\Yarn\Cache",
        rf"{LA}\pnpm-cache", rf"{U}\.cache", rf"{U}\.nuget\packages", rf"{LA}\NuGet\Cache", rf"{U}\.m2\repository",
        rf"{LA}\ms-playwright", rf"{U}\.vscode\extensions", rf"{RA}\Code\Cache", rf"{RA}\Code\CachedData",
        rf"{RA}\Code\CachedExtensionVSIXs", rf"{RA}\Code\logs", rf"{LA}\Docker", rf"{LA}\Programs\DockerDesktop",
        rf"{U}\.gradle", rf"{U}\.android", rf"{RA}\UnityHub\downloads",
    ],
    "Browser & app caches": [
        rf"{LA}\Microsoft\Edge\User Data\Default\Cache", rf"{LA}\Microsoft\Edge\User Data\Default\Code Cache",
        rf"{LA}\Google\Chrome\User Data\Default\Cache", rf"{LA}\Google\Chrome\User Data\Default\Code Cache",
        rf"{LA}\Google\Chrome\User Data\OptGuideOnDeviceModel",
        rf"{RA}\discord\Cache", rf"{LA}\Steam\htmlcache", rf"{LA}\EpicGamesLauncher\Saved\webcache",
        rf"{LA}\EpicGamesLauncher\Saved\Logs", rf"{RA}\uTorrent", rf"{LA}\Packages\MSTeams_8wekyb3d8bbwe\LocalCache",
        rf"{RA}\ChatGPT\Cache", rf"{LA}\Riot Games\Riot Client\Logs",
    ],
    "Vendor logs & telemetry": [
        r"C:\ProgramData\McAfee\wps\log", r"C:\ProgramData\HP\Telemetry\data", r"C:\ProgramData\NVIDIA Corporation",
    ],
    "Downloads & Recycle Bin": [rf"{U}\Downloads", r"C:\$Recycle.Bin"],
}


def measure(path):
    if not os.path.exists(path):
        return None
    if os.path.isfile(path):
        st = os.stat(path)
        return st.st_size, 1, st.st_mtime
    size = files = 0
    newest = 0.0
    stack = [path]
    while stack:
        p = stack.pop()
        try:
            with os.scandir(p) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        else:
                            st = e.stat(follow_symlinks=False)
                            size += st.st_size
                            files += 1
                            newest = max(newest, st.st_mtime)
                    except OSError:
                        pass
        except OSError:
            pass
    return size, files, newest


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


grand = 0
for group, paths in CANDIDATES.items():
    print(f"\n== {group}")
    for p in paths:
        r = measure(p)
        if not r or r[0] < 20 * 1024 * 1024:   # skip missing and anything under 20 MB
            continue
        size, files, newest = r
        grand += size
        age = f"newest file {int((NOW - newest) / 86400)} days old" if newest else ""
        print(f"  {human(size):>9}  {files:>7} files  {age:<24} {p}")
print(f"\nTotal in listed locations (20 MB+): {human(grand)}")

# Downloads: big and old files
d = rf"{U}\Downloads"
if os.path.isdir(d):
    items = []
    for e in os.scandir(d):
        r = measure(e.path)
        if r and r[0] > 50 * 1024 * 1024:
            items.append((r[0], int((NOW - (r[2] or NOW)) / 86400), e.name))
    if items:
        print("\n== Largest items in Downloads (50 MB+)")
        for size, age, name in sorted(items, reverse=True)[:20]:
            print(f"  {human(size):>9}  {age:>4} days  {name}")
