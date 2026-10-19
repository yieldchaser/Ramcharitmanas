# -*- coding: utf-8 -*-
"""Rebuild the pendrive music library as real MP3, 001-399, copied in numeric order."""
import os, re, sys, json, subprocess, time, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r"D:\Music"
OUT  = r"D:\Music_new"
FF   = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
LOGP = r"C:\Users\Dell\AppData\Local\Temp\ytdl\rebuild.log"

plan  = json.load(open(r"C:\Users\Dell\AppData\Local\Temp\ytdl\plan.json", encoding="utf-8"))
probe = json.load(open(r"C:\Users\Dell\AppData\Local\Temp\ytdl\probe_tags.json", encoding="utf-8"))
by_num = {int(re.match(r"^\d+", f).group()): f for f in probe}

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

logf = open(LOGP, "w", encoding="utf-8")
def log(msg):
    print(msg, flush=True)
    logf.write(msg + "\n"); logf.flush()

start = time.time()
fail = []
for i, p in enumerate(plan):
    n = p["n"]; src = os.path.join(ROOT, by_num[n]); dst = os.path.join(OUT, p["file"])
    cmd = [FF, "-nostdin", "-y", "-v", "error", "-i", src, "-map", "0:a:0", "-vn"]
    if p["codec"] == "mp3":
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2"]
    cmd += ["-id3v2_version", "3", "-write_id3v1", "1",
            "-metadata", f"title={n:03d} - {p['title']}",
            "-metadata", f"artist={p['artist']}",
            "-metadata", "album=Bhakti Collection",
            "-metadata", f"track={n}/399",
            "-metadata", "genre=Devotional",
            "-metadata", f"comment=Track {n:03d} of 399",
            dst]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 1024:
        fail.append((n, r.returncode, (r.stderr or "")[-400:]))
        log(f"FAIL {n:03d}: rc={r.returncode} {r.stderr[-200:] if r.stderr else ''}")
    if (i + 1) % 10 == 0 or i == 0 or i == len(plan) - 1:
        el = time.time() - start
        log(f"[{i+1:3d}/{len(plan)}] n={n:03d} {p['codec']:>4} -> {os.path.getsize(dst)//(1024*1024) if os.path.exists(dst) else 0} MB | {el/60:.1f} min elapsed")

log(f"DONE files={len(os.listdir(OUT))} failures={len(fail)} elapsed={(time.time()-start)/60:.1f} min")
for x in fail: log("FAILED " + repr(x))
logf.close()
