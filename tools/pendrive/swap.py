# -*- coding: utf-8 -*-
"""Put D:\\Music_new live as D:\\Music, after verifying, and remove duplicates."""
import os, re, sys, shutil, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = r"D:\Music_new"
OLD = r"D:\Music"
BAK = r"D:\Music_OLD"
DUP = r"D:\MP3"

def count(d):
    return len([f for f in os.listdir(d) if f.lower().endswith(".mp3")])

def order_ok(d):
    fs = os.listdir(d)
    nums = []
    for f in fs:
        m = re.match(r"^(\d{3}) - ", f)
        if m:
            nums.append(int(m.group(1)))
    return len(fs) == 399 and nums == list(range(1, 400)), nums[:5], nums[-5:]

print("new files:", count(OUT), "old files:", count(OLD), "dup mp3:", count(DUP))
ok, first, last = order_ok(OUT)
assert ok, "Music_new is not 399 in numeric directory order"
print("new verified: 399 numeric order, first", first, "last", last)

# 1. remove duplicate source folder (all 122 already copied as 278-399)
if os.path.isdir(DUP):
    n = sum(len(fs) for _, _, fs in os.walk(DUP))
    print("deleting D:\\MP3 (%d entries)..." % n)
    shutil.rmtree(DUP)
    print("D:\\MP3 removed:", not os.path.exists(DUP))

# 2. swap
if os.path.exists(BAK):
    raise SystemExit("D:\\Music_OLD already exists - stop and inspect")
os.rename(OLD, BAK)
print("renamed Music -> Music_OLD")
try:
    os.rename(OUT, OLD)
    print("renamed Music_new -> Music")
    ok2, f2, l2 = order_ok(OLD)
    assert ok2 and count(OLD) == 399
    print("live folder verified:", count(OLD), "files, order", f2, "...", l2)
except Exception as e:
    print("SWAP FAILED:", e, "- rolling back")
    if os.path.exists(OLD) and not os.path.exists(OUT) and os.path.exists(BAK):
        os.rename(OLD, OUT)
        os.rename(BAK, OLD)
    raise

# 3. old library no longer needed (fully superseded and verified)
print("deleting Music_OLD (20 GB of superseded files)...")
t = time.time()
shutil.rmtree(BAK)
print("Music_OLD removed in %.1fs" % (time.time() - t))

print("ROOT NOW:", os.listdir("D:\\"))
print("live mp3 count:", count(OLD))
