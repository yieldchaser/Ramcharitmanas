# -*- coding: utf-8 -*-
"""Rebuild the 1..399 Music-folder tracklist from the merge log + saved durations."""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LOG = r"C:\Users\Dell\AppData\Local\Temp\ytdl\merge_music.log"
DUR = r"C:\Users\Dell\AppData\Local\Temp\ytdl\bare_durations.json"
OUT = r"C:\Users\Dell\Github\Ramcharitmanas\Music-Tracklist-1-399.txt"

copied, renamed, collisions = {}, {}, []
for line in open(LOG, encoding="utf-8", errors="replace"):
    line = line.rstrip("\n")
    m = re.match(r"^copied (\d+): (.+?)  \(\d+ KB\)$", line)
    if m:
        copied[int(m.group(1))] = m.group(2)          # later lines overwrite earlier
        continue
    m = re.match(r"^renamed (\d+)\.mp3 -> (.+)$", line)
    if m:
        renamed[int(m.group(1))] = m.group(2)
        continue
    if line.startswith("RENAME COLLISION"):
        collisions.append(line)

durations = json.load(open(DUR, encoding="utf-8"))    # {"01.mp3": 678, ...}

def hms(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

missing = [n for n in range(278, 400) if n not in copied]
renamed_cnt = len(renamed)
print("copies parsed:", len(copied), "missing:", missing)
print("renames parsed:", renamed_cnt, "collisions:", collisions or "NONE")

rows, bare = [], 0
for n in range(1, 400):
    if n >= 278:
        name = copied[n]
        dur = ""
    elif n in renamed:
        name = renamed[n]
        dur = ""
    else:
        raw = f"{n:02d}.mp3"
        name = raw
        d = durations.get(raw, durations.get(f"{n}.mp3"))
        bare += 1
        dur = f" | untitled, {hms(d)}" if d else " | untitled, duration unknown"
    rows.append(f"{n:>3} | {name}{dur}")

header = [
    "MUSIC FOLDER - COMPLETE TRACK LIST (numbers 1 to 399)",
    "====================================================",
    "",
    "Number | File name",
    "",
    "1-277   = old collection. The number in the file name is the one to say out loud.",
    "          '(untitled, m:ss)' = the file carries NO song info inside it, only its",
    "          length; identify it by ear and rename it when you know what it is.",
    "278-399 = new downloads; the last part of each name is its group",
    "          (Chaiti, Kajri, Jhumar, Hori, Phag, Rajan Ji Maharaj, Rambhadracharya,",
    "          Ramnandacharya, Swami Raghvacharya, Madhushala).",
    "",
    "399 entries: 277 old + 122 new.",
    "",
]

text = "\r\n".join(header + rows) + "\r\n"
with open(OUT, "w", encoding="utf-8-sig", newline="") as fh:   # BOM so Word shows Hindi correctly
    fh.write(text)
print("untitled(old) entries:", bare, "| total rows:", len(rows))
print("written:", OUT, os.path.getsize(OUT), "bytes")
print("---- preview ----")
print("\n".join(rows[:4] + ["  ..."] + rows[275:279] + ["  ..."] + rows[-3:]))
