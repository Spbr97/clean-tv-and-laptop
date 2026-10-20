#!/usr/bin/env python3
"""Undo everything: re-enable every package in debloat.txt, give Home back to the stock launcher,
and put back the settings we changed (Private DNS, screensaver, animation scales).

Usage: tools/venv/Scripts/python.exe -I tools/restore.py [--uninstall-launcher]
TV_HOST defaults to 192.168.1.7. The packages that were already disabled before we started
(com.heytap.olink, com.oneplus.tv.remote) are left disabled, as they were.
"""
import os
import re
import sys

os.environ.setdefault("TV_HOST", "192.168.1.7")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tv  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_HOME = "com.google.android.tvlauncher/.MainActivity"
# Original values from backup/00-original. None means "was unset": the key is deleted.
SETTINGS = [
    ("global", "private_dns_mode", None),
    ("global", "private_dns_specifier", None),
    ("secure", "screensaver_components", ""),
    ("global", "window_animation_scale", "1.0"),
    ("global", "transition_animation_scale", "1.0"),
    ("global", "animator_duration_scale", "0.6"),
]


def packages():
    with open(os.path.join(ROOT, "debloat.txt"), encoding="utf-8") as f:
        for line in f:
            pkg = re.sub(r"#.*$", "", line).strip()
            if pkg:
                yield pkg


def main():
    dev = tv.connect()

    def sh(cmd):  # one command per shell call: chained pm commands can stop after the first
        out = dev.shell(cmd, read_timeout_s=120.0).strip()
        print(f"$ {cmd}\n  {out}" if out else f"$ {cmd}")
        return out

    for pkg in packages():
        sh(f"pm enable --user 0 {pkg}")
    sh(f"cmd package set-home-activity --user 0 {STOCK_HOME}")
    for ns, key, val in SETTINGS:
        sh(f"settings delete {ns} {key}" if val is None else f"settings put {ns} {key} '{val}'")
    if "--uninstall-launcher" in sys.argv:
        sh("pm uninstall com.gathin.tvhome")
    print("\nStill disabled:")
    print(sh("pm list packages -d"))
    print("Home now:", sh("cmd package resolve-activity --brief -a android.intent.action.MAIN "
                          "-c android.intent.category.HOME").splitlines()[-1])
    dev.close()


if __name__ == "__main__":
    main()
