# Top-up pass: fills folders that hit YouTube bot-detection / 403 in the main batch.
# Uses Chrome's YouTube session cookies, runs 2-wide with long sleeps to stay under the radar.
# Reuses the same per-job archives so nothing already downloaded is repeated.
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
WORK = r"C:\Users\Dell\AppData\Local\Temp\ytdl"
LOG = os.path.join(WORK, "logs")
ARCH = os.path.join(WORK, "archives")
os.makedirs(LOG, exist_ok=True); os.makedirs(ARCH, exist_ok=True)

BASE = "D:/MP3"
FOLK = BASE + "/Bhojpuri Folk"

# gentler pacing + browser cookies to dodge bot checks
COMMON = [
    "--ffmpeg-location", FFMPEG,
    "-x", "--audio-format", "mp3",
    "--ignore-errors", "--retries", "10", "--fragment-retries", "10",
    "--js-runtimes", "node",
    "--cookies-from-browser", "chrome",
    "--sleep-requests", "5", "--sleep-interval", "3", "--max-sleep-interval", "8",
    "--embed-metadata",
    "--concurrent-fragments", "2",
    "--extractor-args", "youtube:player_client=android,vr",
    "--trim-filenames", "120",
    "--no-progress", "--no-warnings",
]

def job(name, dest, quality, urls, match_filter=None, max_downloads=None):
    return dict(name=name, dest=dest, quality=quality, urls=urls,
                match_filter=match_filter, max_downloads=max_downloads)

def build_jobs():
    jobs = []
    # Kajri needs a full search top-up (its search 403'd early)
    jobs.append(job("Kajri-search2", f"{FOLK}/Kajri", "192K",
                    ["ytsearch16:kajri bhojpuri song new"],
                    "duration <= 1500 & duration >= 60", 12))
    # Speaker folders: more pravachan queries to reach ~8-10 each
    speakers = [
        ("Rajan Ji Maharaj",   ["Rajan Ji Maharaj pravachan ram katha",
                                "Rajan ji maharaj ke pravachan"]),
        ("Rambhadracharya",    ["Rambadracharya ramayan pravachan",
                                "Jagadguru Rambadracharya katha"]),
        ("Ramnandacharya",     ["Ramnandacharya pravachan",
                                "Swami Ramnandacharya katha"]),
        ("Swami Raghvacharya", ["Swami Raghavacharya pravachan",
                                "Raghavacharya ram katha pravachan"]),
    ]
    talk_filter = "duration <= 14400 & duration >= 600"
    for name, queries in speakers:
        for i, q in enumerate(queries):
            jobs.append(job(f"{name}-top{i+1}", f"{BASE}/{name}", "128K",
                            [f"ytsearch14:{q}"], talk_filter, 6))
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
    ok = p.returncode in (0, 104, 101)
    print(f"{'OK ' if ok else 'FAIL'} {j['name']:30} rc={p.returncode:3} {dt:6.0f}s", flush=True)
    return j["name"], p.returncode

if __name__ == "__main__":
    jobs = build_jobs()
    print(f"TOP-UP: {len(jobs)} jobs (2-wide, cookies, slow pacing)", flush=True)
    fails = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]):
            name, rc = f.result()
            if rc not in (0, 104, 101):
                fails.append((name, rc))
    print("TOP-UP DONE. failures:", fails if fails else "none", flush=True)
