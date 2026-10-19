# -*- coding: utf-8 -*-
"""Verify D:\\Music_new against plan.json: count, order, MP3, duration, tags."""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

OUT = r"D:\Music_new"
PLAN = r"C:\Users\Dell\AppData\Local\Temp\ytdl\plan.json"
plan = json.load(open(PLAN, encoding="utf-8"))
by_n = {p["n"]: p for p in plan}

files = [f for f in os.listdir(OUT) if f.lower().endswith(".mp3")]
files_sorted = sorted(files)
raw_order = files[:]  # directory enumeration order
print("files:", len(files))
assert len(files) == 399, "expected 399 files"

def num(f):
    m = re.match(r"^(\d{3}) - ", f)
    return int(m.group(1)) if m else None

nums = [num(f) for f in files_sorted]
print("numbers complete 1..399:", nums == list(range(1, 400)))
print("unique numbers:", len(set(nums)))
print("lexicographic order == numeric order:", [num(f) for f in files_sorted] == list(range(1, 400)))
print("directory order == numeric order:", [num(f) for f in raw_order] == list(range(1, 400)))
if [num(f) for f in raw_order] != list(range(1, 400)):
    print("  raw first 15:", [(i + 1, num(f)) for i, f in enumerate(raw_order[:15])])

problems = []
durs = {}
for f in files_sorted:
    n = num(f)
    p = by_n[n]
    path = os.path.join(OUT, f)
    try:
        m = MP3(path, ID3=ID3)
        dur = m.info.length
        durs[n] = dur
        tags = m.tags or {}
        title = str(tags.get("TIT2", ""))
        track = str(tags.get("TRCK", ""))
        album = str(tags.get("TALB", ""))
        apic = [k for k in tags.keys() if k.startswith("APIC")]
        if not title.startswith(f"{n:03d}"):
            problems.append((n, "title", title[:60]))
        if not track.startswith(str(n)):
            problems.append((n, "track", track))
        if album != "Bhakti Collection":
            problems.append((n, "album", album))
        if apic:
            problems.append((n, "coverart", apic))
        if abs(dur - p["dur"]) > 3:
            problems.append((n, "duration", f"{dur:.0f} vs {p['dur']}"))
        # ID3v1 trailer
        with open(path, "rb") as fh:
            fh.seek(-128, os.SEEK_END)
            if fh.read(3) != b"TAG":
                problems.append((n, "id3v1", "missing"))
    except Exception as e:
        problems.append((n, "parse", str(e)[:80]))

print("problems:", len(problems))
for x in problems[:40]:
    print("  ", x)

print("total minutes:", round(sum(durs.values()) / 60, 1))
print("size GB:", round(sum(os.path.getsize(os.path.join(OUT, f)) for f in files) / (1024 ** 3), 2))
