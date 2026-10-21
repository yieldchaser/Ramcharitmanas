# -*- coding: utf-8 -*-
"""Append extra tracks to the pendrive library (D:\\Music).

For each YouTube ID in TRACKS:
  1. download the best audio and let yt-dlp unpack it to a scratch MP3
  2. re-encode with ffmpeg to a real 192 kbps / 48 kHz / stereo MP3 (metadata dropped,
     so no cover art -- the C-28 truncates files that carry artwork)
  3. write the same ID3 set the 001-399 library uses: ID3v2.3 + ID3v1, TIT2, TPE1,
     TALB, TRCK, COMM, TCON, TDRC, TXXX:purl
  4. name it with the next free three-digit number and copy it onto the drive in
     ascending order, because the player walks the FAT directory order

Usage:
    python tools/download/add_tracks.py --dry-run   # show numbers + titles only
    python tools/download/add_tracks.py             # download and append
"""
import os, re, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FFMPEG = (r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages"
          r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
          r"\ffmpeg-9.0-full_build\bin\ffmpeg.exe")
WORK = r"C:\Users\Dell\AppData\Local\Temp\ytdl"
DEST = r"D:\Music"
ALBUM = "Bhakti Collection"      # same album tag the whole library carries
GENRE = "Devotional"             # same genre tag the whole library carries

# id, group shown in the track list, hand-written title used instead of the raw
# YouTube one (the raw titles carry "#Video |" prefixes and hashtag spam).
# Entries already present on the drive are skipped by title, so re-running this
# file never duplicates or renumbers anything -- it is the log of the group.
TRACKS = [
    ("-a8YCshjQXs", "Vivah Gari Geet",
     "दुलहा के बहिन यार राखेली थानेदार राखेली - विवाह गारी गीत"),
    ("BK2BmylPQcs", "Vivah Gari Geet",
     "समधी के बहिनिया पटाके हलवाई - विवाह गारी गीत"),
    ("krtCO751U-Q", "Vivah Gari Geet",
     "कईसन बाराती अइले मांग मांग खाले - विवाह गारी गीत"),
    ("vtmiqqRsp90", "Vivah Gari Geet",
     "समधी के दीदी बड़की खेलाड़ - विवाह गारी गीत"),
    ("l5bKr_5jfAY", "Vivah Gari Geet",
     "तनी सुन ला... साले तब जइहा - विवाह गारी गीत"),
    ("5I3sFVTplJs", "Vivah Gari Geet",
     "बराती गाली गीत - विवाह गारी गीत"),
    # ---- Mithila (Maithili) Ram-Sita vivah gari geet ----
    ("pro5DTrX9vs", "Mithila Gari Geet",
     "छयलवा को दइहौं चुन चुन गारी - मिथिला गारी गीत"),
    ("etilxcWujzA", "Mithila Gari Geet",
     "मिथिला की अद्भुत गारी - मिथिला गारी गीत"),
    ("-UPq7a61koQ", "Mithila Gari Geet",
     "राम जी से पूछे जनकपुर की नारी - मिथिला गारी गीत"),
    ("d6MWk5M5NQY", "Mithila Gari Geet",
     "जनकपुर की अद्भुत गारी - मिथिला गारी गीत"),
    ("W_wy1B54yVg", "Mithila Gari Geet",
     "मिथिला की नारि भगवान राम को गारी कहती हैं - मिथिला गारी गीत"),
]

JUNK = re.compile(r"^(untitled|track\s*\d+|audio|mp3|song|unknown|na|n/?a)$", re.I)


def clean_title(s):
    if not s:
        return ""
    s = str(s).replace("\x00", "")
    s = re.sub(r"[|｜]", " - ", s)
    s = re.sub(r"[<>:\"/\\?*]", " ", s)
    s = re.sub(r"[\x00-\x1f\x7f]", " ", s)
    s = re.sub(r"[\U00010000-\U0010ffff]", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .-")
    return s[:80].strip(" .-")


def next_number():
    nums = [int(m.group(1)) for f in os.listdir(DEST)
            if (m := re.match(r"^(\d+)\s*-", f))]
    return max(nums) + 1 if nums else 1


def titles_on_drive():
    """Clean titles already numbered on the drive, so re-runs skip them."""
    out = set()
    for f in os.listdir(DEST):
        m = re.match(r"^\d+\s*-\s*(.+)\.mp3$", f, re.I)
        if m:
            out.add(m.group(1).strip())
    return out


def download(vid):
    """Download to WORK and return (scratch mp3 path, title, artist, year, url)."""
    os.makedirs(WORK, exist_ok=True)
    out_tpl = os.path.join(WORK, f"{vid}.%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp",
           "--ffmpeg-location", FFMPEG,
           "-x", "--audio-format", "mp3", "--audio-quality", "0",
           "--js-runtimes", "node", "--no-playlist",
           "--retries", "10", "--fragment-retries", "10",
           "--sleep-requests", "1",
           "--embed-metadata",
           "--no-progress", "--no-warnings",
           "-o", out_tpl, f"https://www.youtube.com/watch?v={vid}"]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"yt-dlp failed for {vid}: {p.stderr.strip()[-400:]}")
    scratch = os.path.join(WORK, f"{vid}.mp3")
    if not os.path.exists(scratch):
        raise RuntimeError(f"no mp3 produced for {vid}")

    from mutagen.mp3 import MP3
    tags = MP3(scratch).tags or {}
    title = str(tags.get("TIT2", ""))
    artist = str(tags.get("TPE1", ""))
    year = str(tags.get("TDRC", ""))[:4]
    return scratch, title, artist, year, f"https://www.youtube.com/watch?v={vid}"


def encode(src, dst, tag, total):
    """Re-encode to 192 kbps CBR and write the library's tag set."""
    cmd = [FFMPEG, "-y", "-i", src, "-map", "0:a:0",
           "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-map_metadata", "-1", "-id3v2_version", "3", "-write_id3v1", "1",
           "-metadata", f"title={tag['title']}",
           "-metadata", f"artist={tag['artist']}",
           "-metadata", f"album={ALBUM}",
           "-metadata", f"track={tag['n']}/{total}",
           "-metadata", f"genre={GENRE}",
           "-metadata", f"date={tag['year']}",
           "-metadata", f"comment=Track {tag['n']} of {total}",
           dst]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr.strip()[-400:]}")

    from mutagen.id3 import ID3, TXXX, COMM, TCON, TDRC, TALB
    t = ID3(dst)
    if "APIC" in t:                     # paranoia: no cover art ever
        del t["APIC"]
    t.setall("TALB", [TALB(encoding=3, text=[ALBUM])])
    t.setall("TCON", [TCON(encoding=3, text=[GENRE])])
    if tag["year"]:
        t.setall("TDRC", [TDRC(encoding=3, text=[tag["year"]])])
    t.setall("COMM", [COMM(encoding=3, lang="eng", desc="", text=[f"Track {tag['n']} of {total}"]),
                      COMM(encoding=3, lang="eng", desc="ID3v1 Comment",
                           text=[tag["url"]])])
    t.add(TXXX(encoding=3, desc="purl", text=[tag["url"]]))
    t.save(v1=2, v2_version=3)
    return dst


def main():
    dry = "--dry-run" in sys.argv
    have = titles_on_drive()
    pending = [t for t in TRACKS if clean_title(t[2]) not in have]
    start = next_number()
    total = start + len(pending) - 1
    print(f"drive holds {start - 1} tracks, {len(pending)} of {len(TRACKS)} entries pending", flush=True)
    if not pending:
        print("nothing to add -- every TRACKS entry is already on the drive")
        return
    print(f"new numbers {start:03d}-{total:03d}", flush=True)
    if dry:
        for i, (vid, group, given) in enumerate(pending):
            print(f"  {start + i:03d}  {vid}  [{group}]  {given}", flush=True)
        return

    written = []
    for i, (vid, group, given) in enumerate(pending):
        n = start + i
        print(f"[{n:03d}] downloading {vid} ...", flush=True)
        scratch, title, artist, year, url = download(vid)
        t = clean_title(given or title)
        if not t or JUNK.match(t):
            raise RuntimeError(f"unusable title for {vid}: {title!r}")
        from mutagen.mp3 import MP3
        dur = MP3(scratch).info.length
        name = f"{n:03d} - {t}.mp3"
        tmp_out = os.path.join(WORK, f"{n:03d}.mp3")
        encode(scratch, tmp_out, dict(n=n, title=f"{n:03d} - {t}", artist=artist or "Various Artists",
                                      year=year, url=url), total)
        final = os.path.join(DEST, name)
        shutil.copy2(tmp_out, final)
        os.remove(tmp_out)
        os.remove(scratch)
        written.append((n, name, group, dur, url, artist))
        print(f"      -> {name}  ({int(dur // 60)}m{int(dur % 60):02d}s, {artist or '?'})", flush=True)
        time.sleep(2)

    print("\nadded:")
    for n, name, group, dur, url, artist in written:
        print(f"  {n:03d} | {int(dur // 60)}m{int(dur % 60):02d}s | {name} | {group} | {url}")
    print(f"total files on drive: {len([f for f in os.listdir(DEST) if f.lower().endswith('.mp3')])}")


if __name__ == "__main__":
    main()
