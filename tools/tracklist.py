# -*- coding: utf-8 -*-
"""Regenerate _TRACKLIST.txt with durations and container notes."""
import os, re, sys, json, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MUSIC = r"D:\Music"
FFPROBE = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"

def lead(f):
    m = re.match(r"(\d+)", os.path.splitext(f)[0])
    return int(m.group(1)) if m else None

def kind(f):
    with open(os.path.join(MUSIC, f), "rb") as fh:
        head = fh.read(12)
    if b"ftyp" in head:
        return "m4a"
    if head[:4] == b"\x1aE\xdf\xa3":
        return "webm"
    return "mp3"

def hms(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

files = sorted([f for f in os.listdir(MUSIC) if f.lower().endswith(".mp3")], key=lambda x: (lead(x) or 0, x))
bare_dur = json.load(open(r"C:\Users\Dell\AppData\Local\Temp\ytdl\bare_durations.json", encoding="utf-8"))

rows = []
need_dur = []
for f in files:
    n = lead(f)
    dur = bare_dur.get(f)
    if dur is None:
        need_dur.append(f)
    rows.append([n, f, dur])

# probe durations only where we don't have them (title already identifies the track,
# but a duration still helps the listener pick)
for i in range(0, len(need_dur), 40):
    chunk = need_dur[i:i + 40]
    for f in chunk:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", os.path.join(MUSIC, f)],
                           capture_output=True, text=True, timeout=300)
        try:
            d = round(float((r.stdout or "0").strip()))
        except ValueError:
            d = 0
        for row in rows:
            if row[1] == f:
                row[2] = d
    print(f"probed {min(i + 40, len(need_dur))}/{len(need_dur)}", flush=True)

lines = [
    "TRACK LIST - Music folder (pen drive) - for the music system",
    "===========================================================",
    "",
    "Format:  NUMBER | DURATION | FILE NAME",
    "",
    "Numbers 001-277 = old collection.",
    "  Names were added where the file itself carried a song title.",
    "  A nameless entry (just the number + duration) has NO song info inside the file;",
    "  identify it by ear once, then tell someone the number to rename it.",
    "Numbers 278-399 = new downloads (title + group, e.g. Chaiti, Kajri, Ramnandacharya).",
    "",
    "(m4a) / (webm) marks files that carry a .mp3 name but a different audio format",
    "inside - most players still read them; if one refuses to play, that is why.",
    "",
    "TOTAL: 399 songs",
    "",
]
for n, f, dur in rows:
    k = kind(f)
    tag = "" if k == "mp3" else f" ({k})"
    d = hms(dur) if dur else "?:??"
    lines.append(f"{n:>3} | {d:>7} | {f}{tag}")

out = "\r\n".join(lines) + "\r\n"
with open(os.path.join(MUSIC, "_TRACKLIST.txt"), "w", encoding="utf-8-sig", newline="") as fh:
    fh.write(out)
rows_written = sum(1 for l in lines if re.match(r"^\s*\d+ \|", l))
print("rows written:", rows_written)
