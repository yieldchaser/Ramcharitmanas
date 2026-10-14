# Ramcharitmanas — Media Collection

Offline media collection organised folder-wise, ready to copy onto a pendrive.

> Audio/video files live in `mp3/` which is gitignored (too large for GitHub). This README documents what each file is and where it came from, so anything deleted can be re-fetched in one command.

## Folder layout (current)

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

The 1–399 pendrive track list (kept in the repo root and in `tools/`) covers the
separate `D:\Music` collection that was copied onto the grandfather's pendrive.

## Re-downloading (if ever needed)

Requires [yt-dlp](https://github.com/yt-dlp/yt-dlp) and ffmpeg. Full pipeline
scripts live in [`tools/`](tools/) — see [`tools/README.md`](tools/README.md).

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
