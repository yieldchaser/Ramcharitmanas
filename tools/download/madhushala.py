# -*- coding: utf-8 -*-
"""Download Madhushala (Harivansh Rai Bachchan) collection into D:/MP3/Madhushala."""
import os, subprocess, sys, time

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
OUT = r"D:\MP3\Madhushala"
ARCHIVE = r"C:\Users\Dell\AppData\Local\Temp\ytdl\archives\madhushala.archive"
LOGDIR = r"C:\Users\Dell\AppData\Local\Temp\ytdl\logs"
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)

# curated picks: (video_id, suggested title)
PICKS = [
    ("01tTexP2Pg0", "Madhushala [Complete] - Sri Harivansh Rai Bachchan (Poet's own recitation)"),
    ("_-jL1gdnIhU", "Madhushala Full with Lyrics - Voice Kumar Rajesh"),
    ("i51q56EAPeQ", "Madhushala Complete Poem - Reading by Anwar Jamal"),
    ("S27uNaAa72M", "Madhushala Poem - Dr Harivansh Rai Bachchan"),
    ("XZGQcLyPHMs", "Madhushala Poem - Harivansh Rai Bachchan"),
    ("5vXaY13KPOU", "Madhushala - Madiralay Jane Ko - Manna Dey (Ghazal)"),
    ("a-TebVXPKzk", "Madhushala Recited by Amitabh Bachchan"),
    ("n4jkYIeC23A", "Madhushala Part 1 - Complete Poetry Collection"),
    ("ZRkF9rawXkA", "Madhushala Part 1 - Sahitya Manch"),
    ("-tZmtZfnM9g", "Maadhushala Ep 01 - Manoj Muntashir"),
]

def already(name):
    return any(f.startswith(name[:60]) and f.endswith(".mp3") for f in os.listdir(OUT))

fails = []
for i, (vid, title) in enumerate(PICKS, 1):
    if already(title):
        print(f"[{i}/{len(PICKS)}] skip (exists): {title}", flush=True)
        continue
    log = os.path.join(LOGDIR, f"madhushala_{i}.log")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        f"https://www.youtube.com/watch?v={vid}",
        "--ffmpeg-location", FFMPEG,
        "-x", "--audio-format", "mp3", "--audio-quality", "192K",
        "--embed-thumbnail", "--embed-metadata",
        "--download-archive", ARCHIVE,
        "-o", os.path.join(OUT, title + ".%(ext)s"),
        "--no-playlist",
        "--retries", "10", "--fragment-retries", "10",
        "--sleep-requests", "1",
        "--newline", "--progress",
    ]
    print(f"[{i}/{len(PICKS)}] downloading: {title} ({vid})", flush=True)
    with open(log, "w", encoding="utf-8", errors="replace") as lf:
        rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
    if rc != 0:
        tail = ""
        try:
            with open(log, encoding="utf-8", errors="replace") as lf:
                tail = "".join(lf.readlines()[-6:])
        except Exception:
            pass
        print(f"  FAILED rc={rc}\n{tail}", flush=True)
        fails.append(vid)
    else:
        print(f"  OK: {title}", flush=True)
    time.sleep(4)

print(f"\nDONE. failed={len(fails)} {fails}", flush=True)
print("final files:", flush=True)
for f in sorted(os.listdir(OUT)):
    print("  ", f, flush=True)
