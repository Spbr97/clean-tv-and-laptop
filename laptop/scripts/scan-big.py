"""Read-only: walk C:\\ once and report the biggest folders (depth 1-4) and every file of 1 GB or more.

    python -I scan-big.py > big.txt

Skips junctions/symlinks and OneDrive cloud-only files (no local bytes). Ages are days since last write.
"""
import os, stat, sys, time

sys.stdout.reconfigure(encoding="utf-8")   # file names with emoji/odd scripts would crash cp1252

ROOT = "C:\\"
NOW = time.time()
MAXDEPTH = 4
sizes = {}          # folder (depth <= MAXDEPTH) -> total bytes
newest = {}
big_files = []

def walk(path, depth, chain):
    try:
        it = os.scandir(path)
    except OSError:
        return
    with it:
        for e in it:
            try:
                st = e.stat(follow_symlinks=False)
            except OSError:
                continue
            attrs = getattr(st, "st_file_attributes", 0)
            if attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                continue        # junctions/symlinks/OneDrive placeholders: skip
            if stat.S_ISDIR(st.st_mode):
                sub = chain + [e.path] if depth < MAXDEPTH else chain
                if depth < MAXDEPTH:
                    sizes.setdefault(e.path, 0)
                walk(e.path, depth + 1, sub)
            else:
                # skip OneDrive cloud-only files (no local bytes)
                if attrs & 0x400000 or attrs & 0x1000:   # RECALL_ON_DATA_ACCESS / OFFLINE
                    continue
                n = st.st_size
                for c in chain:
                    sizes[c] += n
                    if st.st_mtime > newest.get(c, 0):
                        newest[c] = st.st_mtime
                if n >= 1 << 30:
                    big_files.append((n, int((NOW - st.st_mtime) / 86400), e.path))

walk(ROOT, 1, [])

def h(n):
    return f"{n / (1 << 30):6.1f} GB"

print("== Biggest folders (>= 1 GB), depth 1-4")
for p, n in sorted(sizes.items(), key=lambda x: -x[1]):
    if n >= 1 << 30:
        age = int((NOW - newest.get(p, NOW)) / 86400)
        print(f"{h(n)}  newest {age:>4}d  {p}")

print("\n== Files >= 1 GB")
for n, age, p in sorted(big_files, reverse=True):
    print(f"{h(n)}  {age:>4}d old  {p}")
