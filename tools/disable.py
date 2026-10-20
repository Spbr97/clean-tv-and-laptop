#!/usr/bin/env python3
"""Disable the packages in debloat.txt (pm disable-user --user 0, never uninstall).

Usage: tools/venv/Scripts/python.exe -I tools/disable.py [batch number ...]
With no batch numbers, applies batches 1-6 (batch 7, the stock launcher, is handled by
launcher/build-and-install.ps1 once the new launcher owns Home). TV_HOST defaults to 192.168.1.7.
"""
import os
import re
import sys

os.environ.setdefault("TV_HOST", "192.168.1.7")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tv  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def batches():
    out, cur = {}, None
    with open(os.path.join(ROOT, "debloat.txt"), encoding="utf-8") as f:
        for line in f:
            m = re.match(r"##\s*Batch\s+(\d+)", line)
            if m:
                cur = int(m.group(1))
                continue
            pkg = re.sub(r"#.*$", "", line).strip()
            if pkg and cur is not None:
                out.setdefault(cur, []).append(pkg)
    return out


def main():
    wanted = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
    all_batches = batches()
    dev = tv.connect()
    for b in wanted:
        for pkg in all_batches.get(b, []):
            # one pm command per shell call: chained pm commands can silently stop after the first
            out = dev.shell(f"pm disable-user --user 0 {pkg}", read_timeout_s=120.0).strip()
            print(f"[batch {b}] {pkg}: {out}")
    dev.close()


if __name__ == "__main__":
    main()
