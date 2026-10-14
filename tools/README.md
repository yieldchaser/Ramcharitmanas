# tools/ — YouTube → MP3 pipeline (preserved for future downloads)

The 2.4 GB of MP3s that used to live in `mp3/` were deleted to save disk space.
Everything needed to **re-download them or add new songs** is kept here.

## Prerequisites

- Python 3.12+ with `yt-dlp` (`pip install yt-dlp`)
- ffmpeg (installed via winget: `winget install Gyan.FFmpeg`) — scripts expect it at the
  WinGet path; edit the `FFMPEG = r"..."` constant at the top of each script if yours differs
- Optional: `mutagen` (`pip install mutagen`) for the tag/merge scripts

## The scripts

| Script | What it does |
|---|---|
| `dl.py` | Batch search+download: 4 parallel jobs, per-destination download archive so re-runs top up instead of re-downloading. Edit the `JOBS` list with query → output folder. |
| `topup.py` | Gentler 2-wide retry pass using Chrome session cookies to get past YouTube's bot check. |
| `retry_loop.py` | Long-sleep single-threaded retry (Firefox cookies) for the files YouTube refused. |
| `madhushala.py` | Example: explicit list of video IDs → one folder, with `--download-archive`. |
| `validate.py` / `validate_fast.py` | ffprobe every file in a folder; reports corrupt/non-MP3 files. |
| `merge_music.py` | Copies a folder tree of MP3s into `D:\Music` as `NNN - Title - Group.mp3`, continuing an existing `001–NNN` numbering, renames originals from embedded tags, writes `_TRACKLIST.txt`. **D:\MP3 side is read-only.** |
| `tracklist.py` | Regenerates `_TRACKLIST.txt` with `NUMBER | DURATION | FILE NAME` rows. |
| `rebuild_list.py` | Rebuilds the full 1–399 list from `merge_music.log` + `bare_durations.json` (works even when the drive is unplugged). |
| `make_formats.py` | Builds the formatted `Music-Tracklist-1-399.xlsx` (filters, group colours) and `.docx` (group index, repeating headers) from those sources. |
| `bare_durations.json` | Recorded lengths of the 156 untitled old songs — needed by `rebuild_list.py`. |

## Gotchas learned the hard way

- YouTube rate-limits datacentre IPs with "sign in to confirm you're not a bot";
  browser cookies (`--cookies-from-browser`) help, plain reruns don't.
- `--download-archive` (not `--archive`) is the correct yt-dlp flag.
- Quote-safe filename templating matters: `\\$title` in a bash one-liner writes a literal
  `Madhushala$title.mp3`. Use a Python script, not shell loops, for anything with spaces/Devanagari.
- Windows console is cp1252: print Devanagari with `sys.stdout.reconfigure(encoding="utf-8")`
  or `PYTHONIOENCODING=utf-8`.
- Add the Album tag **after** size checks, or resume logic will re-copy everything
  (tag growth changes file size).

## The playlist sources

See the root [README.md](../README.md) — it lists every playlist/video link used,
so any deleted file can be fetched again in one command:

```
python -m yt_dlp -x --audio-format mp3 --embed-metadata "<URL>"
```
