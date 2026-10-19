import subprocess, sys, os, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
target = "mp3/05_GovindDevGiri_Mahabharat_Katha_Pandharpur/Mahabharat Katha Pandharpur - Day 03.mp3"
cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings",
 "--extractor-args", "youtube:player_client=android",
 "--sleep-requests", "2", "-f", "ba/b", "-x", "--audio-format", "mp3",
 "--audio-quality", "128K", "--embed-metadata", "--embed-thumbnail",
 "--no-overwrites", "--retries", "10", "--socket-timeout", "30",
 "--concurrent-fragments", "4", "--playlist-items", "1",
 "-o", "mp3/05_GovindDevGiri_Mahabharat_Katha_Pandharpur/Mahabharat Katha Pandharpur - Day 03.%(ext)s",
 "https://www.youtube.com/watch_videos?video_ids=_zgNaywsvuk"]
print("day03 watchdog armed; probing every 30 min for 24h", flush=True)
for i in range(48):
    if os.path.exists(target) and os.path.getsize(target) > 100_000_000:
        print("ALREADY_DONE", flush=True); sys.exit(0)
    r = subprocess.call(cmd)
    print(time.strftime("%d %H:%M"), "attempt", i + 1, "exit", r, flush=True)
    if os.path.exists(target) and os.path.getsize(target) > 100_000_000:
        print("DAY03_DONE", flush=True); sys.exit(0)
    time.sleep(1800)
print("GAVE_UP after 24h", flush=True)
