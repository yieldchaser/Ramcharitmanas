# -*- coding: utf-8 -*-
"""Final on-device audit of D:\\Music: structure, FAT order, MP3 validity, tags."""
import os, re, sys, json, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

ROOT = r"D:\Music"
FFPROBE_PLAN = r"C:\Users\Dell\AppData\Local\Temp\ytdl\plan.json"
plan = json.load(open(FFPROBE_PLAN, encoding="utf-8"))
by = {p["n"]: p for p in plan}

entries = os.listdir(ROOT)
files = sorted([f for f in entries if f.lower().endswith(".mp3")])
print("root of Music: entries=%d mp3=%d other=%s" % (
    len(entries), len(files), [e for e in entries if not e.lower().endswith('.mp3')][:5]))

nums = []
for f in files:
    m = re.match(r"^(\d{3}) - .+\.mp3$", f)
    nums.append(int(m.group(1)) if m else -1)
print("names 001..399 complete:", nums == list(range(1, 400)))

# FAT/enumeration order as the player sees it
raw = [os.path.join(ROOT, f) for f in entries if f.lower().endswith(".mp3")]
raw_nums = [int(re.match(r"^(\d{3})", os.path.basename(p)).group(1)) for p in raw]
print("FAT order == 001..399:", raw_nums == list(range(1, 400)))
if raw_nums != list(range(1, 400)):
    for i, (a, b) in enumerate(zip(range(1, 400), raw_nums)):
        if a != b:
            print("  first mismatch at position", i + 1, "->", b)
            break

bad = []
for f in files:
    n = int(f[:3])
    p = os.path.join(ROOT, f)
    try:
        size = os.path.getsize(p)
        with open(p, "rb") as fh:
            head = fh.read(10)
            fh.seek(-128, os.SEEK_END)
            has_v1 = fh.read(3) == b"TAG"
        # real MPEG audio: ID3v2 tag or MPEG frame sync
        if head[:3] == b"ID3":
            tagsize = ((head[6] & 0x7F) << 21) | ((head[7] & 0x7F) << 14) | \
                      ((head[8] & 0x7F) << 7) | (head[9] & 0x7F)
            off = 10 + tagsize + (10 if (head[5] & 0x10) else 0)
            with open(p, "rb") as fh:
                fh.seek(off)
                frame = fh.read(2)
        else:
            frame = head[:2]
        if len(frame) < 2 or frame[0] != 0xFF or (frame[1] & 0xE0) != 0xE0:
            bad.append((n, "not mpeg audio", frame.hex()))
        if not has_v1:
            bad.append((n, "no id3v1", ""))
        m = MP3(p, ID3=ID3)
        t = m.tags or {}
        title = str(t.get("TIT2", ""))
        track = str(t.get("TRCK", ""))
        album = str(t.get("TALB", ""))
        if not title.startswith("%03d" % n):
            bad.append((n, "title", title[:40]))
        if not track.startswith(str(n)):
            bad.append((n, "track", track))
        if album != "Bhakti Collection":
            bad.append((n, "album", album))
        if [k for k in t.keys() if k.startswith("APIC")]:
            bad.append((n, "coverart", ""))
        if abs(m.info.length - by[n]["dur"]) > 3:
            bad.append((n, "duration", "%.0f vs %s" % (m.info.length, by[n]["dur"])))
        if size < 100 * 1024:
            bad.append((n, "tiny", size))
    except Exception as e:
        bad.append((n, "parse", str(e)[:70]))

print("problems:", len(bad))
for x in bad[:20]:
    print("  ", x)
print("total GB:", round(sum(os.path.getsize(os.path.join(ROOT, f)) for f in files) / (1024 ** 3), 2))
