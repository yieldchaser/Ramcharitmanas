# Validate every newly-downloaded MP3: full ffmpeg decode to null, capturing real errors.
import os, glob, subprocess, sys

FFMPEG = r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
BASE = "D:\\MP3"
FOLK = os.path.join(BASE, "Bhojpuri Folk")

folders = [os.path.join(FOLK, g) for g in ["Chaiti", "Kajri", "Jhumar", "Hori", "Phag"]] + \
          [os.path.join(BASE, s) for s in ["Rajan Ji Maharaj", "Rambhadracharya",
                                           "Ramnandacharya", "Swami Raghvacharya"]]

total = 0; corrupt = []; stats = {}
for folder in folders:
    files = glob.glob(os.path.join(folder, "*.mp3"))
    ok = 0
    for fp in files:
        total += 1
        r = subprocess.run([FFMPEG, "-v", "error", "-i", fp, "-f", "null", "-"],
                           capture_output=True, text=True, errors="replace")
        err = (r.stderr or "").strip()
        if r.returncode != 0 or err:
            corrupt.append((fp, err[:120]))
        else:
            ok += 1
    stats[os.path.basename(folder)] = (ok, len(files))

print("=== per-folder (ok / total) ===")
for k, (ok, n) in stats.items():
    print(f"  {k:22} {ok}/{n}")
print(f"\nTOTAL files={total}  corrupt={len(corrupt)}")
if corrupt:
    print("\n=== corrupt files ===")
    for fp, e in corrupt:
        print(f"  {os.path.basename(fp)[:70]}\n     {e}")
