# tools/ — scripts, grouped by job

Every script here uses **absolute Windows paths** (`C:\Users\Dell\...`, `D:\Music`) at the
top of the file and expects the WinGet ffmpeg build. If you move the project or run it on
another machine, edit those constants first.

## [pendrive/](pendrive/) — the numbering kit (now 001–410)

The pipeline that rebuilt the C-28 pendrive. Run in this order:

| # | Script | What it does |
|---|---|---|
| 1 | [`plan_rebuild.py`](pendrive/plan_rebuild.py) | Reads `probe_tags.json`, decides the numbering 001 upward, titles and the codec each file needs → `plan.json` |
| 2 | [`rebuild_music.py`](pendrive/rebuild_music.py) | Writes every track as a **real MP3** (stream-copy if already MP3, LAME 192 kbps if AAC/Opus), 3-digit name, ID3v2.3 + ID3v1, no cover art, `D:\Music_new` |
| 3 | [`verify_new.py`](pendrive/verify_new.py) | Checks count, numbering, duration, tags, ID3v1 trailer and that FAT order = numeric order |
| 4 | [`swap.py`](pendrive/swap.py) | Deletes the duplicate `D:\MP3`, swaps `Music_new` in as `Music`, re-asserts order, removes the old library |
| 5 | [`make_tracklist.py`](pendrive/make_tracklist.py) | Writes `Music-Tracklist-001-<max>.txt` + `.html` **into the repo only** (never onto the drive) |
| 6 | [`check_final.py`](pendrive/check_final.py) | Cross-checks the generated list against `plan.json`: row count, durations, titles |
| 7 | [`audit_drive.py`](pendrive/audit_drive.py) | On-device audit: real MPEG frames, tags, ID3v1, no cover art, FAT order, no strays |
| — | [`extend_tracklist.py`](pendrive/extend_tracklist.py) | **Appending only.** Rebuilds both list formats from the drive itself (no `plan.json`), keeps the existing rows byte-for-byte and adds the new numbers under a new group. `python tools/pendrive/extend_tracklist.py "Vivah Gari Geet"` |

`plan.json`, `probe_tags.json` and the logs are intermediates in
`C:\Users\Dell\AppData\Local\Temp\ytdl\` — not committed, regenerable. Windows
clears Temp on its own, so `plan.json` can be gone; that is why
`extend_tracklist.py` never needs it.

## [download/](download/) — YouTube → MP3

| Script | What it does |
|---|---|
| [`dl.py`](download/dl.py) | Batch search+download: 4 parallel jobs, per-destination archive so re-runs top up instead of re-downloading. Edit the `JOBS` list. |
| [`topup.py`](download/topup.py) | Gentler 2-wide retry pass using Chrome cookies to get past the bot check. |
| [`retry_loop.py`](download/retry_loop.py) | Long-sleep single-threaded retry (Firefox cookies) for files YouTube refused. |
| [`madhushala.py`](download/madhushala.py) | Example: explicit video-ID list → one folder, with `--download-archive`. |
| [`mahabharat_watchdog.py`](download/mahabharat_watchdog.py) | Watches the Mahabharat download queue and retries failures (writes `watchdog.log`). |
| [`add_tracks.py`](download/add_tracks.py) | Appends explicit video IDs to the drive as the next numbers: 192 kbps CBR / 48 kHz / stereo re-encode, ID3v2.3 + ID3v1, no artwork, `NNN - Title.mp3`. `--dry-run` shows the numbers first. |

## [legacy/](legacy/) — superseded, kept for reference

These built the **old** library that played the wrong song (unpadded names, renamed
non-MP3 files). Don't reuse them for the pendrive; they are here because they document
the download/merge history.

| Script | Was used for |
|---|---|
| [`merge_music.py`](legacy/merge_music.py) | Copied a folder tree into `D:\Music` as `NNN - Title - Group.mp3`, appended album tags, wrote `_TRACKLIST.txt` |
| [`tracklist.py`](legacy/tracklist.py) | Regenerated `_TRACKLIST.txt` as `NUMBER \| DURATION \| FILE` |
| [`rebuild_list.py`](legacy/rebuild_list.py) | Rebuilt the old 1–399 list from logs while the drive was unplugged |
| [`make_formats.py`](legacy/make_formats.py) | Built the old `.xlsx` / `.docx` track lists |
| [`validate.py`](legacy/validate.py), [`validate_fast.py`](legacy/validate_fast.py) | ffprobe every file in a folder, report corrupt/non-MP3 files |
| [`bare_durations.json`](legacy/bare_durations.json) | Recorded lengths of the 156 untitled old songs |

## Prerequisites

- Python 3.12+ with `mutagen` (`pip install mutagen`) for anything that reads tags
- `yt-dlp` (`pip install yt-dlp`) for the download scripts
- ffmpeg via winget (`winget install Gyan.FFmpeg`); scripts expect the WinGet path

## Gotchas learned the hard way

- YouTube rate-limits datacentre IPs with "sign in to confirm you're not a bot";
  browser cookies (`--cookies-from-browser`) help, plain reruns don't.
- `--download-archive` (not `--archive`) is the correct yt-dlp flag.
- Quote-safe filename templating matters: `\$title` in a bash one-liner writes a literal
  `Madhushala$title.mp3`. Use a Python script, not shell loops, for anything with spaces
  or Devanagari.
- Windows console is cp1252: print Devanagari with
  `sys.stdout.reconfigure(encoding="utf-8")` or set `PYTHONIOENCODING=utf-8`.
- Add the Album tag **after** size checks, or resume logic re-copies everything (tag
  growth changes file size).
- Never put a renamed AAC/Opus/WebM file into a numbered folder: the decoder skips it and
  every later number shifts by one.

## Sources

Playlists, video IDs and re-download commands are listed in the root
[README.md](../README.md).
