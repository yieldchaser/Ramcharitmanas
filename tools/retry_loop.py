# Patient retry loop for the folders blocked by YouTube's IP rate limit.
# Single-threaded with long sleeps so we stay under the limiter. Uses Firefox cookies
# (readable by yt-dlp) in case a session appears; harmless if absent. Retries in waves
# with growing cooldowns, stopping once every target folder reaches its file target.
import os, subprocess, sys, time, glob

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
WORK = r"C:\Users\Dell\AppData\Local\Temp\ytdl"
LOG = os.path.join(WORK, "logs"); ARCH = os.path.join(WORK, "archives")
os.makedirs(LOG, exist_ok=True); os.makedirs(ARCH, exist_ok=True)
BASE = "D:/MP3"; FOLK = BASE + "/Bhojpuri Folk"

COMMON = [
    "--ffmpeg-location", FFMPEG, "-x", "--audio-format", "mp3",
    "--ignore-errors", "--retries", "10", "--fragment-retries", "10",
    "--js-runtimes", "node", "--cookies-from-browser", "firefox",
    "--sleep-requests", "8", "--sleep-interval", "5", "--max-sleep-interval", "15",
    "--embed-metadata", "--concurrent-fragments", "1",
    "--trim-filenames", "120", "--no-progress", "--no-warnings",
]

# (name, dest, quality, query, match_filter, cap, min_target)
TARGETS = [
    ("Kajri", f"{FOLK}/Kajri", "192K", "kajri bhojpuri song new",
     "duration <= 1500 & duration >= 60", 12, 10),
    ("Rajan Ji Maharaj", f"{BASE}/Rajan Ji Maharaj", "128K", "Rajan Ji Maharaj pravachan ram katha",
     "duration <= 14400 & duration >= 600", 8, 8),
    ("Rambhadracharya", f"{BASE}/Rambhadracharya", "128K", "Jagadguru Rambadracharya ramayan katha",
     "duration <= 14400 & duration >= 600", 8, 8),
    ("Ramnandacharya", f"{BASE}/Ramnandacharya", "128K", "Swami Ramnandacharya pravachan katha",
     "duration <= 14400 & duration >= 600", 8, 8),
    ("Swami Raghvacharya", f"{BASE}/Swami Raghvacharya", "128K", "Swami Raghavacharya ram katha pravachan",
     "duration <= 14400 & duration >= 600", 8, 8),
]

def count(dest):
    return len(glob.glob(os.path.join(dest, "*.mp3")))

def attempt(name, dest, quality, query, mf, cap, n):
    log = os.path.join(LOG, f"retry-{name}-{n}.log")
    cmd = [sys.executable, "-m", "yt_dlp", *COMMON, "--audio-quality", quality,
           "--download-archive", os.path.join(ARCH, f"retry-{name}.archive"),
           "--match-filter", mf, "--max-downloads", str(cap),
           "-o", os.path.join(dest, "%(title)s [%(id)s].%(ext)s"), f"ytsearch14:{query}"]
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    bot = "bot" in open(log, encoding="utf-8", errors="replace").read().lower()
    return rc, bot

if __name__ == "__main__":
    cooldowns = [90, 240, 420, 600, 900, 900]
    for wave, cd in enumerate(cooldowns, 1):
        remaining = [(t) for t in TARGETS if count(t[1]) < t[6]]
        if not remaining:
            print("ALL TARGETS MET. done.", flush=True); break
        print(f"--- wave {wave}: cooldown {cd}s, need: {[t[0] for t in remaining]} ---", flush=True)
        time.sleep(cd)
        for (name, dest, quality, query, mf, cap, min_t) in remaining:
            have = count(dest)
            if have >= min_t: continue
            rc, bot = attempt(name, dest, quality, query, mf, cap, wave)
            print(f"  {name}: have {have}/{min_t} rc={rc} bot={'Y' if bot else 'N'}", flush=True)
            time.sleep(20)  # breathe between jobs
    summary = ", ".join(f"{t[0]}={count(t[1])}" for t in TARGETS)
    print(f"RETRY LOOP DONE. counts: {summary}", flush=True)
