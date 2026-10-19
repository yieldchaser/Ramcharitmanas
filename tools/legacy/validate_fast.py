# Fast validation: each file must (a) start with ID3 or an MPEG sync frame, and
# (b) let ffmpeg parse its stream metadata (proves it's a real, non-truncated MP3).
import os, glob, subprocess

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"
BASE = "D:\\MP3"
FOLK = os.path.join(BASE, "Bhojpuri Folk")
folders = [os.path.join(FOLK, g) for g in ["Chaiti", "Kajri", "Jhumar", "Hori", "Phag"]] + \
          [os.path.join(BASE, s) for s in ["Rajan Ji Maharaj", "Rambhadracharya",
                                           "Ramnandacharya", "Swami Raghvacharya"]]

total = 0; bad = []; stats = {}
for folder in folders:
    files = glob.glob(os.path.join(folder, "*.mp3"))
    ok = 0
    for fp in files:
        total += 1
        try:
            with open(fp, "rb") as f: head = f.read(3)
            size = os.path.getsize(fp)
            has_sync = head[:3] == b"ID3" or (len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0)
            r = subprocess.run([FFMPEG, "-v", "error", "-show_entries",
                                "format=duration,bit_rate:stream=codec_name",
                                "-of", "default=noprint_wrappers=1", fp],
                               capture_output=True, text=True, errors="replace")
            parsed = r.returncode == 0 and "codec_name=mp3" in (r.stdout or "")
            if has_sync and parsed and size > 10000:
                ok += 1
            else:
                bad.append((fp, f"size={size} sync={has_sync} parsed={parsed} {r.stderr.strip()[:80]}"))
        except Exception as e:
            bad.append((fp, f"exc {e}"))
    stats[os.path.basename(folder)] = (ok, len(files))

print("=== per-folder (ok / total) ===")
for k, (ok, n) in stats.items(): print(f"  {k:22} {ok}/{n}")
print(f"\nTOTAL={total}  bad={len(bad)}")
for fp, e in bad: print(f"  BAD {os.path.basename(fp)[:60]} :: {e}")
