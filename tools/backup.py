#!/usr/bin/env python3
"""Snapshot the TV's state before changing anything: packages, disabled packages, getprop, all settings.

Usage: TV_HOST=<ip> tools/venv/Scripts/python.exe -I tools/backup.py [out_dir]
Writes into backup/<timestamp>/ by default.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tv  # noqa: E402

FILES = {
    "packages-all.txt": "pm list packages -f -u",
    "packages-enabled.txt": "pm list packages -e",
    "packages-disabled.txt": "pm list packages -d",
    "packages-system.txt": "pm list packages -s",
    "packages-third-party.txt": "pm list packages -3",
    "getprop.txt": "getprop",
    "settings-system.txt": "settings list system",
    "settings-secure.txt": "settings list secure",
    "settings-global.txt": "settings list global",
    "home-activities.txt": "cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME",
    "home-resolved.txt": "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME",
    "ime.txt": "ime list -s; echo; settings get secure default_input_method",
    "tv-inputs.txt": "dumpsys tv_input",
    "meminfo.txt": "cat /proc/meminfo",
    "storage.txt": "df -h /data",
}


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        root, "backup", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out, exist_ok=True)
    dev = tv.connect()
    for name, cmd in FILES.items():
        data = dev.shell(cmd, read_timeout_s=120.0)
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
        print(f"{name:28s} {len(data.splitlines()):6d} lines")
    dev.close()
    print("backup written to", out)


if __name__ == "__main__":
    main()
