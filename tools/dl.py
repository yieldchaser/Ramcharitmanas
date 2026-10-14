# Batch YouTube -> MP3 downloader for the pendrive (D:/MP3)
# Jobs run 4-wide; each has its own log + shared per-destination download archive
# so re-running the script tops up instead of re-downloading.
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
WORK = r"C:\Users\Dell\AppData\Local\Temp\ytdl"
LOG = os.path.join(WORK, "logs")
ARCH = os.path.join(WORK, "archives")
os.makedirs(LOG, exist_ok=True); os.makedirs(ARCH, exist_ok=True)

BASE = "D:/MP3"
FOLK = BASE + "/Bhojpuri Folk"

COMMON = [
    "--ffmpeg-location", FFMPEG,
    "-x", "--audio-format", "mp3",
    "--ignore-errors", "--retries", "10", "--fragment-retries", "10",
    "--js-runtimes", "node",
    "--sleep-requests", "1", "--sleep-interval", "1",
    "--embed-metadata",
    "--concurrent-fragments", "4",
    "--trim-filenames", "120",
    "--no-progress",
    "--no-warnings",
]

def job(name, dest, quality, urls, match_filter=None, max_downloads=None):
    return dict(name=name, dest=dest, quality=quality, urls=urls,
                match_filter=match_filter, max_downloads=max_downloads)

def build_jobs():
    jobs = []
    # ---- Bhojpuri folk genres ----
    # (genre, example video URLs from the user's reference table, search query)
    folk = [
        ("Chaiti", ["https://www.youtube.com/watch?v=NrJ0VNfs7xE",
                    "https://www.youtube.com/watch?v=byyYJBKlks0"],
         "chaiti bhojpuri song new"),
        ("Kajri",  ["https://www.youtube.com/watch?v=0QFMz-d3SWY",
                    "https://www.youtube.com/watch?v=eylv8riakPo",
                    "https://www.youtube.com/watch?v=XNQhoglnCgg"],
         "kajri bhojpuri song new"),
        ("Jhumar", ["https://www.youtube.com/watch?v=WXdvYFTT7V8",
                    "https://www.youtube.com/watch?v=Se3ERbzfHcc"],
         "jhoomar bhojpuri song new"),
        ("Hori",   ["https://www.youtube.com/watch?v=tQRCHSR9qlM",
                    "https://www.youtube.com/watch?v=zuQuDU-Kv2E"],
         "bhojpuri hori song new holi"),
        ("Phag",   ["https://www.youtube.com/watch?v=RKXSG9Phq7Q",
                    "https://www.youtube.com/watch?v=4mqKnu9Sk1w"],
         "phagua bhojpuri song jogira new"),
    ]
    song_filter = "duration <= 1500 & duration >= 60"
    for genre, links, query in folk:
        dest = f"{FOLK}/{genre}"
        # pass 1: the user's example links, no duration filter (jukeboxes allowed)
        jobs.append(job(f"{genre}-examples", dest, "192K", links))
        # pass 2: top up with search results (songs only, skip shorts & jukeboxes)
        jobs.append(job(f"{genre}-search", dest, "192K",
                        [f"ytsearch16:{query}"], song_filter, 12))

    # ---- Pravachan speakers (fill the four empty folders) ----
    speakers = [
        ("Rajan Ji Maharaj",   ["Rajan Ji Maharaj pravachan", "Rajan Ji Maharaj Ramayan katha"]),
        ("Rambhadracharya",    ["Jagadguru Rambadracharya pravachan", "रामभद्राचार्य प्रवचन कथा"]),
        ("Ramnandacharya",     ["Ramnandacharya pravachan", "Ramnand Acharya katha"]),
        ("Swami Raghvacharya", ["Swami Raghavacharya pravachan", "Raghavacharya katha ramayan"]),
    ]
    talk_filter = "duration <= 14400 & duration >= 600"   # 10 min .. 4 h
    for name, queries in speakers:
        dest = f"{BASE}/{name}"
        for i, q in enumerate(queries):
            jobs.append(job(f"{name}-q{i+1}", dest, "128K",
                            [f"ytsearch14:{q}"], talk_filter, 8))
    return jobs

def run(j):
    out = os.path.join(LOG, j["name"] + ".log")
    cmd = [sys.executable, "-m", "yt_dlp", *COMMON,
           "--audio-quality", j["quality"],
           "--download-archive", os.path.join(ARCH, j["name"] + ".archive"),
           "-o", os.path.join(j["dest"], "%(title)s [%(id)s].%(ext)s")]
    if j["match_filter"]:
        cmd += ["--match-filter", j["match_filter"]]
    if j["max_downloads"]:
        cmd += ["--max-downloads", str(j["max_downloads"])]
    cmd += j["urls"]
    t0 = time.time()
    with open(out, "w", encoding="utf-8", errors="replace") as f:
        p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    # 104 = max-downloads reached, that is a normal stop
    ok = p.returncode in (0, 104)
    print(f"{'OK ' if ok else 'FAIL'} {j['name']:32} rc={p.returncode:3} {dt:6.0f}s  -> {j['dest']}",
          flush=True)
    return j["name"], p.returncode, dt

if __name__ == "__main__":
    jobs = build_jobs()
    print(f"launching {len(jobs)} jobs (4-wide)", flush=True)
    fails = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for f in as_completed(futs):
            name, rc, dt = f.result()
            if rc not in (0, 104):
                fails.append((name, rc))
    print("ALL JOBS DONE. failures:", fails if fails else "none", flush=True)
