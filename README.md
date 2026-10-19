# Ramcharitmanas — Media Collection

Offline media collection organised folder-wise, ready to copy onto a pendrive.

> Audio/video files live in `mp3/` which is gitignored (too large for GitHub). This README documents what each file is and where it came from, so anything deleted can be re-fetched in one command.

## Repository map

```
tools/            scripts, grouped by job
├── pendrive/     the 001–399 rebuild + verification kit  (see tools/README.md)
├── download/     YouTube → MP3 pipeline
└── legacy/       superseded scripts, kept for reference
archive/          old tracklists that must not be used (see archive/README.md)
mp3/              media files — gitignored, too large for GitHub
Music-Tracklist-001-399.txt / .html    the current pendrive number list
```

## Media layout (current, in the gitignored `mp3/`)

```
mp3/
└── 06_Girl_With_The_Dragon_Tattoo_2011/   Trent Reznor & Atticus Ross score (27 tracks, 2h01m)
                                           + 1 ambient video (33m)
```

## 06 — The Girl with the Dragon Tattoo (2011, David Fincher)

Score album by **Trent Reznor & Atticus Ross** (Null Corporation / Mute, 2011),
split into one MP3 per track from the two chapter-marked CD uploads, plus the
end-credits theme and one ambient video.

| # | Track | Source |
|---|---|---|
| 01–13 | CD1: Immigrant Song … Please Take Your Hand Away | https://www.youtube.com/watch?v=m3QEaHmkSN0 (13 chapters) |
| 14–26 | CD2: Cut Into Pieces … Parallel Timeline With Alternate Outcome | https://www.youtube.com/watch?v=tPOORaiA1Qo (13 chapters) |
| 27 | Is Your Love Strong Enough? (end-credits theme, How To Destroy Angels) | https://www.youtube.com/watch?v=gVEsA6BSsWc |
| — | The Same as the Others — Ambient version (1600% Slow) — **kept as MP4 video**, 360p | https://music.youtube.com/watch?v=mzRB-M2DYhE |

- MP3 tracks: 192 kbps with embedded metadata + thumbnail artwork; zero-padded
  `NN - Title.mp3` so they sort correctly on any MP3 player.
- Track splits verified against the source chapter markers (all durations exact).
- Total size: ~235 MB (27 MP3s + 1 MP4).

## Deleted folders (01–05) — re-download sources

The original katha collection (2.4 GB) was removed to free disk space. Sources:

| Folder | Source | Link |
|---|---|---|
| 01_Rambhadracharya_Kanpur_2019 | Shri Ramcharitmanas Katha — Kanpur 2019 (Jagadguru Rambhadracharya ji) | https://www.youtube.com/playlist?list=PLOZ4QPdIQPK014Q22A-MawqVI9pAuM70U |
| 02_Rambhadracharya_Bageshwar_Dham | Shri Ram Katha Day-1 (Bageshwar Dham) | https://www.youtube.com/watch?v=B6v_sBT3eTs |
| 03_Raghvacharya_Ramcharitmanas_Path_Ayodhya | Ramcharitmanas Paath (Swami Raghvacharya) | https://www.youtube.com/watch?v=xtZv9eDA6TE |
| 04_Rajan_Ji_Ramcharitmanas_Vyakhya | Shri Ramcharitmanas ki Sundar Vyakhya (Pujya Rajan Ji) | https://www.youtube.com/watch?v=7RUK-P9pRd0 |
| 05_GovindDevGiri_Mahabharat_Katha_Pandharpur | Shri Mahabharat Katha — Pandharpur, Days 1–7 (Swami Govind Dev Giri ji) | https://www.youtube.com/watch?v=6HpIAOHPxm4 (Day 1) — full series via watch_videos: `6HpIAOHPxm4,ex_52kbePEI,_zgNaywsvuk,UpUicoXBky0,o2WwKyul3_M,GpAXRTgDHCg,M4_KJTIUxyw` |

## Pendrive library — numbers 001 to 399 (`D:\Music`)

A separate collection for the **C-28 Music Speaker** (generic USB/SD MP3 decoder
module, 7-segment display, `CH+/CH-` and `0-9` keys on the IR remote).

**Track list:** [Music-Tracklist-001-399.txt](Music-Tracklist-001-399.txt) ·
[Music-Tracklist-001-399.html](Music-Tracklist-001-399.html) (searchable, printable —
open it in a browser and press Ctrl+P).

### Drive layout — one folder, nothing else

```
D:\
└── Music\        399 files, 001 - Title.mp3 … 399 - Title.mp3   (21.1 GB)
```

No sub-folders, no playlist files, no copies of this list on the drive. The
decoder scans `Music` and indexes the files in FAT order, which the rebuild
forced to equal 001→399. Keep it that way: a new folder would need `CH+`
navigation the listener cannot do, and any file dropped at the root competes
with `Music` for the decoder's scan. Print or open the list from this repo
instead — [`Music-Tracklist-001-399.html`](Music-Tracklist-001-399.html) is
searchable and prints cleanly.

### Why the old pendrive played the wrong song

The `0-9` keys on these decoder modules do not open a file by name. They jump to
the **Nth playable file the decoder indexed** while scanning the folder, and that
index is built in the order the files sit in the FAT directory — anything the
decoder cannot play is silently skipped, which shifts every later track.

Measured on the old library (399 files, 351 decodable):

| Defect | Scope | Effect on numbering |
|---|---|---|
| 48 files were **not MP3** — 45 AAC/M4A, 3 WebM/Opus, all renamed `.mp3` | 12% | Decoder skips them, so every later number is one lower |
| 99 names used 2-digit prefixes (`01.mp3`), 300 used 3-digit | 25% | Any name-sorted player reads 1, 10, 100, 101, 11 … so 010–099 land in the wrong place |
| **No** ID3 track-number tags in any file | all | Nothing to fall back on |
| Files copied in several separate passes | — | FAT directory order ≠ numeric order |

Simulation on the real file list: under filename sorting **0 of 351** decodable
tracks sat on their own number; under directory order with the bad files skipped
also **0 of 351**, with a drift of 48 numbers for 206 songs. "Some songs work"
was simply the drift being invisible near the start of the list.

### Rules the rebuilt library follows

- Every file is a **real MP3** (LAME 192 kbps, 44.1 kHz, stereo). Nothing is a
  renamed AAC/Opus/WebM container.
- Names are **zero-padded to three digits**: `001 - Title.mp3` … `399 - Title.mp3`,
  in one flat `Music` folder.
- Files are written **in numeric order**, so FAT order, name order and ID3 order
  all agree — whichever way the decoder counts, 025 is 025.
- ID3v2.3 + ID3v1 tags, `track` = the file number, album `Bhakti Collection`,
  **no cover art** (embedded APIC art stalls some cheap decoders).
- 156 old recordings carry no title inside them; they are `Untitled recording`
  and are identified in the list by their exact length.
- Numbers 001–277 are the old collection; 278–399 are Chaiti, Kajri, Jhumar,
  Hori, Phag, Rajan Ji, Rambhadracharya, Ramnandacharya, Swami Raghvacharya and
  Madhushala.

If any song is ever added: keep the `NNN - Title.mp3` name, add it in numeric
order, keep the ID3 track equal to the number, and never drop in a renamed
non-MP3 file. The rebuild and verification scripts are in
[`tools/pendrive/`](tools/pendrive/) — run them in the order listed in
[`tools/README.md`](tools/README.md).

## Re-downloading (if ever needed)

Requires [yt-dlp](https://github.com/yt-dlp/yt-dlp) and ffmpeg. The download
scripts live in [`tools/download/`](tools/download/); prerequisites, flags and the
gotchas are in [`tools/README.md`](tools/README.md).

Chapter-split album example (what produced folder 06):

```bash
yt-dlp --no-warnings --ffmpeg-location <ffmpeg> \
  -x --audio-format mp3 --audio-quality 192K --embed-metadata --embed-thumbnail \
  -o "chapter:%(section_number)02d - %(section_title)s.%(ext)s" \
  --split-chapters "https://www.youtube.com/watch?v=m3QEaHmkSN0"
```

The `chapter:` prefix in the output template is required for `--split-chapters`
to name the split files; without it every file is written as `NA - NA.mp3`.

Simple playlist example:

```bash
yt-dlp -f "ba/b" -x --audio-format mp3 --audio-quality 128K \
  --embed-metadata --embed-thumbnail \
  -o "mp3/01_Rambhadracharya_Kanpur_2019/Kanpur 2019 Katha - Day %(playlist_index)02d.%(ext)s" \
  --playlist-items 1-7 "https://www.youtube.com/playlist?list=PLOZ4QPdIQPK014Q22A-MawqVI9pAuM70U"
```

*Downloaded for personal/family listening.*
