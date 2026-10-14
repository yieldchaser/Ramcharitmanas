# -*- coding: utf-8 -*-
"""Merge D:\MP3 into D:\Music.
Phase 1: copy every MP3-folder file into Music as "NNN - Title - Group.mp3" (278+).
Phase 2: rename originals "NN.mp3" -> "NN - Title - Artist.mp3" when tags allow.
Phase 3: write _TRACKLIST.txt (utf-8-sig) listing every number.
D:\MP3 is only ever READ.
"""
import os, re, shutil, sys, time

MUSIC = r"D:\Music"
MP3ROOT = r"D:\MP3"
LOG = r"C:\Users\Dell\AppData\Local\Temp\ytdl\merge_music.log"

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TALB
from mutagen.mp4 import MP4

_lines = []
def log(msg):
    _lines.append(msg)
    with open(LOG, "a", encoding="utf-8", errors="replace") as fh:
        fh.write(msg + "\n")

def sanitize(s, cap):
    if not s:
        return ""
    s = str(s)
    s = s.replace("\x00", "")
    s = re.sub(r"[|｜]", " - ", s)                 # ascii + fullwidth pipe -> separator
    s = re.sub(r'[<>:"/\\?*]', " ", s)             # FAT/Win32 illegal chars
    s = re.sub(r"[\x00-\x1f]", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.replace("(Raag.Fm)", "").replace("(raag.fm)", "").replace("Raag.Fm", "")
    s = re.sub(r"\s+", " ", s).strip(" .-")
    if len(s) > cap:
        s = s[:cap].rstrip(" .-")
    return s

def get_tags(path):
    """Return (title, artist) or ("", "")."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(12)
        if b"ftyp" in head:
            m = MP4(path)
            t = m.tags or {}
            title = (t.get("\xa9nam") or [""])[0]
            artist = (t.get("\xa9ART") or [""])[0]
            return str(title), str(artist)
        if head[:4] == b"\x1aE\xdf\xa3":
            return "", ""   # webm, no tags readable
        m = MP3(path, ID3=ID3)
        t = m.tags
        if not t:
            return "", ""
        title = str(t.get("TIT2")) if t.get("TIT2") else ""
        artist = str(t.get("TPE1")) if t.get("TPE1") else ""
        return title, artist
    except Exception as e:
        log(f"  tagread fail {os.path.basename(path)}: {e}")
        return "", ""

# ---------------- Phase 1: copy with new numbers ----------------
GROUPS = [
    (r"Bhojpuri Folk\Chaiti", "Chaiti"),
    (r"Bhojpuri Folk\Kajri", "Kajri"),
    (r"Bhojpuri Folk\Jhumar", "Jhumar"),
    (r"Bhojpuri Folk\Hori", "Hori"),
    (r"Bhojpuri Folk\Phag", "Phag"),
    (r"Rajan Ji Maharaj", "Rajan Ji Maharaj"),
    (r"Rambhadracharya", "Rambhadracharya"),
    (r"Ramnandacharya", "Ramnandacharya"),
    (r"Swami Raghvacharya", "Swami Raghvacharya"),
    (r"Madhushala", "Madhushala"),
]

log(f"=== merge start {time.ctime()} ===")
num = 278
copied = 0
existing = set(os.listdir(MUSIC))
for rel, label in GROUPS:
    d = os.path.join(MP3ROOT, rel)
    if not os.path.isdir(d):
        log(f"MISSING DIR: {d}")
        continue
    files = sorted([f for f in os.listdir(d) if f.lower().endswith(".mp3")], key=str.lower)
    for f in files:
        src = os.path.join(d, f)
        title, _ = get_tags(src)
        title = sanitize(title or os.path.splitext(f)[0], 90)
        if not title:
            title = sanitize(os.path.splitext(f)[0], 90)
        g = sanitize(label, 30)
        stem = f"{num} - {title} - {g}"
        dst = os.path.join(MUSIC, stem + ".mp3")
        if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
            log(f"skip-exists {stem}.mp3")
        else:
            shutil.copy2(src, dst)
            copied += 1
            log(f"copied {num}: {stem}.mp3  ({os.path.getsize(dst)//1024} KB)")
        # album tag on the COPY only, so players can browse by group
        try:
            mp = MP3(dst, ID3=ID3)
            if mp.tags is None:
                mp.add_tags()
            mp.tags.add(TALB(encoding=3, text=[g]))
            mp.save()
        except Exception as e:
            log(f"  album-tag fail {stem}: {e}")
        num += 1
new_max = num - 1
log(f"phase1 done: copied={copied}, numbers 278..{new_max}")

# ---------------- Phase 2: rename taggable originals ----------------
renamed = {}
skipped_untagged = 0
snapshot = sorted(os.listdir(MUSIC))
for f in snapshot:
    if not f.lower().endswith(".mp3"):
        continue
    stem, ext = os.path.splitext(f)
    if not stem.isdigit():          # only bare originals; renamed/new have " - "
        continue
    path = os.path.join(MUSIC, f)
    title, artist = get_tags(path)
    t = sanitize(title, 90)
    a = sanitize(artist, 50)
    if not t and not a:
        skipped_untagged += 1
        continue
    if not t:
        t = a; a = ""
    newstem = f"{stem} - {t}"
    if a and a.lower() not in t.lower() and len(newstem) + len(a) + 3 <= 160:
        newstem += f" - {a}"
    newname = newstem + ext
    if newname == f:
        continue
    if newname in existing:
        log(f"RENAME COLLISION, kept original: {f} -> {newname}")
        continue
    os.rename(path, os.path.join(MUSIC, newname))
    existing.add(newname)
    renamed[f] = newname
    log(f"renamed {f} -> {newname}")
log(f"phase2 done: renamed={len(renamed)} left-bare(no tags)={skipped_untagged}")

# ---------------- Phase 3: tracklist ----------------
def leading_num(name):
    m = re.match(r"(\d+)", name)
    return int(m.group(1)) if m else 999999

rows = []
for f in sorted(os.listdir(MUSIC), key=lambda x: (leading_num(x), x.lower())):
    if not f.lower().endswith(".mp3"):
        continue
    n = leading_num(f)
    rows.append(f"{n:>3} | {f}")
tl = os.path.join(MUSIC, "_TRACKLIST.txt")
with open(tl, "w", encoding="utf-8-sig") as fh:
    fh.write("TRACK LIST - MP3 folder for music system\r\n")
    fh.write("==========================================\r\n")
    fh.write("Numbers 001-277 = old collection (renamed where song titles were embedded in the file).\r\n")
    fh.write("Numbers 278-399 = new downloads from MP3 folder (Title - Group).\r\n")
    fh.write("Files that show only a number have no song info inside them; ask the owner what they are.\r\n")
    fh.write("\r\n")
    fh.write("\r\n".join(rows) + "\r\n")
log(f"phase3 done: tracklist rows={len(rows)}")

# ---------------- summary ----------------
n_music = len([x for x in os.listdir(MUSIC) if x.lower().endswith('.mp3')])
log(f"TOTAL music mp3s = {n_music} (expected 399)")
log(f"=== merge end {time.ctime()} ===")
print(f"copied={copied} renamed={len(renamed)} untagged_left={skipped_untagged} total={n_music} new_max={new_max}", flush=True)
