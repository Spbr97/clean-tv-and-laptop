# Laptop cleanup: HP OMEN 16

An HP OMEN 16 (Intel i7-14650HX, 16 GB RAM, Windows 11 Home) that felt slow. It was diagnosed
read-only first, and every removal was then approved **item by item**.

**Result:** free space on C: went from **336 GB to 530 GB**, and the background RAM hogs were found.
The slowness was **memory pressure, not the CPU**: with a few dev tools, Docker and a browser open,
16 GB fills up and Windows starts paging.

## What was found and done

### Memory and startup

| Finding | Action |
|---|---|
| A leftover Gradle daemon from an Android build, holding 2.3 GB | Stopped |
| Teams, Codex and Microsoft Lists started with Windows | Turned off (the same switch as Task Manager → Startup apps) |
| Docker Desktop starts **23 containers** (three local Supabase stacks, all `restart: unless-stopped`), about **3.7 GB of RAM**. Free RAM dropped to 0.8 GB. | Kept. Quit Docker when you're not using those stacks. |

### Disk

| Finding | Size | Action |
|---|---|---|
| An EA game download that stopped halfway two months earlier (36,552 `*_DiP_Staged` files, no working game file) | 110 GB | Deleted |
| A Plague Tale: Requiem and Control (Game Pass), plus Assassin's Creed's leftover folders | ~100 GB, counted together with the Store apps below | Removed. Control was removed by mistake; see Lessons. |
| Temp files, crash dumps, Windows Error Reporting, old logs | 3.5 GB | Deleted |
| npm, pnpm and Playwright caches | 2.1 GB | Deleted. Run `npx playwright install` before the next Playwright run. |
| Unity Hub's leftover installer copies (the editor itself stays) | 5.1 GB | Recycle Bin |
| Old downloaded videos | 11 GB | Recycle Bin |
| HP Insights Analytics' telemetry database (`ssm.db`) | 3 GB | Deleted with [`reset-hp-telemetry.ps1`](scripts/reset-hp-telemetry.ps1). It grows back slowly. |

### Programs

| Removed | Notes |
|---|---|
| Store apps: Bing News, Bing Weather, Bing Search, Get Help, Feedback Hub, Clipchamp, Dropbox promo, Power Automate, Microsoft Family | `Remove-AppxPackage` |
| HP Client Management Script Library, HP Documentation, PunkBuster | [`uninstall-hp-extras.ps1`](scripts/uninstall-hp-extras.ps1) |
| .NET Runtime 8.0.29 x64, ASP.NET Core 8.0.29 x86, Desktop Runtime 8.0.29 x86, Desktop Runtime 10.0.10 x64 | Each had a newer patch installed beside it (8.0.32 / 10.0.13). Done with [`uninstall-old-dotnet.ps1`](scripts/uninstall-old-dotnet.ps1). |

**Kept on purpose:**
- **Antivirus and vendor tools:** McAfee, HP One Agent, HP Connection Optimizer, the HP promo apps and Intel's telemetry and Driver & Support Assistant.
- **Apps:** Phone Link, the Microsoft 365 hub, Brave, µTorrent and PostgreSQL.
- **Games and dev tools:** the games still being played, the Unity editor (a game project uses it), and Docker's images and build cache.

## Still worth watching

- **McAfee's debug logs.** `C:\ProgramData\McAfee\wps\log` reached **16 GB in two days** (about 11 GB
  on the worst day) in 134 MB trace files. McAfee's self-protection blocks deleting them, even as
  admin. The only fixes are to uninstall McAfee (Microsoft Defender switches itself back on) or to
  reinstall it fresh.
- **Docker's disk.** `docker_data.vhdx` is 40 GB:
  - The build cache (20 GB, `docker builder prune`) and two superseded images (9.5 GB) can go.
  - Data volumes are separate; never prune them blindly.
  - The `.vhdx` file doesn't shrink by itself after a prune.
- **Chrome's on-device AI model** (4 GB under `OptGuideOnDeviceModel`). Switch it off in
  `chrome://settings/system` → *On-device AI*, and Chrome deletes it.
- **Fine to leave:**
  - `pagefile.sys` and `hiberfil.sys`, which Windows manages.
  - The NVIDIA shader cache: deleting it only causes stutter while it rebuilds.
  - `C:\Program Files\HP\OMEN-Broadcast`, which the OMEN virtual camera still uses.

## Scripts

All of them are in [`scripts/`](scripts). The scan scripts only read, and the others change the
system, so they need an elevated PowerShell.

| Script | What it does |
|---|---|
| `python -I scan-big.py` | Walks C: once: biggest folders (depth 1–4) and every file of 1 GB or more, with ages. Read-only. |
| `python -I scan-leftovers.py` | Size and age of the usual leftover places: temp, crash dumps, update caches, dev caches, browser caches, vendor logs, Downloads. Read-only. |
| `find-file-lock.ps1 <file>` | Shows which process or service has a file open (Restart Manager API). Read-only. |
| `uninstall-old-dotnet.ps1 -Installers <names>` | Removes old .NET runtimes whose cached uninstaller is gone (see below). Admin. |
| `uninstall-hp-extras.ps1` | Silent uninstall of HP CMSL, HP Documentation and PunkBuster. Admin. |
| `reset-hp-telemetry.ps1` | Stops HP's two analytics services, deletes `ssm.db` and starts them again. Admin. |

## Lessons learned

- **Ask about one item at a time.** One checkbox covered two games, and it removed a Game Pass game
  that was still being played.
- **Removing a Game Pass game deletes its local saves.** `Remove-AppxPackage` deletes
  `%LOCALAPPDATA%\Packages\<package>` with the game, and `C:\XboxGames\GameSave` doesn't keep a copy.
  Only Xbox cloud saves survive. Reinstall from the Xbox app and launch while signed in to get them back.
- **Old .NET runtimes with a missing Package Cache can't be removed the usual ways:**
  - "Installed apps" fails, because the uninstall entry points to a deleted `.exe`.
  - `msiexec /x {code}` on the parts reports exit 0 but removes nothing, because the bundle's
    dependency keeps them.
  - What works: download the same version's official installer from `builds.dotnet.microsoft.com`,
    check the Microsoft signature, then run `<installer> /uninstall /quiet`.
- **PunkBuster's uninstaller is in `SysWOW64`**, not in the `System32` path that "Installed apps" shows.
- **McAfee protects its own folders**, even from an elevated process.
- **HP One Agent holds `ssm.db` open** as well as HP Insights Analytics. Stopping both services
  lets the file be deleted; `find-file-lock.ps1` showed which process was holding it.
- **`uv cache clean` fails while any app started by uv is running.** Close it first.
- **`C:\SWSetup`** (HP's driver installers) needs admin rights to delete. Remove it from File Explorer if you need the space.
