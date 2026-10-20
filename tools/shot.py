#!/usr/bin/env python3
"""Press remote keys on the TV, then take a screenshot and pull it.

Usage: TV_HOST=<ip> tools/venv/Scripts/python.exe -I tools/shot.py <name> [KEY ...]
Keys are KEYCODE_ names without the prefix (HOME, DPAD_DOWN, ...) or 'wait:<seconds>'.
Saves screens/<name>.png. The screenshot is saved on the TV and pulled, since some
MediaTek firmwares print junk before the PNG on exec-out.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tv  # noqa: E402


def main():
    name, keys = sys.argv[1], sys.argv[2:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "screens", name + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    dev = tv.connect()
    for k in keys:
        if k.startswith("wait:"):
            time.sleep(float(k[5:]))
            continue
        dev.shell(f"input keyevent KEYCODE_{k}")
        time.sleep(0.6)
    time.sleep(1.0)
    dev.shell("screencap -p /data/local/tmp/s.png")
    dev.pull("/data/local/tmp/s.png", out)
    dev.shell("rm -f /data/local/tmp/s.png")
    dev.close()
    print(out)


if __name__ == "__main__":
    main()
